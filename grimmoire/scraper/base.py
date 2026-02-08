"""Base scraper class for data sources."""
import time
import requests
from abc import ABC, abstractmethod
from typing import Generator, Any, Optional, List, Dict
from dataclasses import dataclass, field

from ..db.manager import DatabaseManager


@dataclass
class ScraperProgress:
    """Track scraper progress for resumption."""
    total_items: int = 0
    processed_items: int = 0
    current_page: int = 0
    last_id: Optional[str] = None
    errors: List = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            'total_items': self.total_items,
            'processed_items': self.processed_items,
            'current_page': self.current_page,
            'last_id': self.last_id,
            'errors': self.errors[-10:]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ScraperProgress':
        return cls(
            total_items=data.get('total_items', 0),
            processed_items=data.get('processed_items', 0),
            current_page=data.get('current_page', 0),
            last_id=data.get('last_id'),
            errors=data.get('errors', [])
        )


class BaseScraper(ABC):
    """Base class for all data source scrapers."""
    
    def __init__(self, db: DatabaseManager, source_name: str, config: dict = None):
        self.db = db
        self.source_name = source_name
        self.config = config or {}
        self.progress = ScraperProgress()
        self.rate_limit = self.config.get('rate_limit', 1.0)
        self.last_request = 0
        self._stop_requested = False
        self.source_id = self._get_source_id()
    
    def _get_source_id(self) -> Optional[int]:
        sources = self.db.get_sources()
        for source in sources:
            if source['name'] == self.source_name:
                return source['id']
        return None
    
    def _rate_limit(self):
        now = time.time()
        min_interval = 1.0 / self.rate_limit
        elapsed = now - self.last_request
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self.last_request = time.time()
    
    def _make_request(self, url: str, params: dict = None, headers: dict = None) -> requests.Response:
        self._rate_limit()
        default_headers = {'User-Agent': 'Grimmoire/0.1 (Traditional Medicine Research Tool)'}
        if headers:
            default_headers.update(headers)
        response = requests.get(url, params=params, headers=default_headers, timeout=30)
        response.raise_for_status()
        return response
    
    def request_stop(self):
        self._stop_requested = True
    
    def should_stop(self) -> bool:
        return self._stop_requested
    
    @abstractmethod
    def scrape(self, resume_from: ScraperProgress = None) -> Generator[dict, None, None]:
        """Scrape data from the source. Yields dicts of scraped data."""
        pass
    
    @abstractmethod
    def process_item(self, item: dict) -> Optional[dict]:
        """Process a scraped item and return normalized data."""
        pass
    
    def save_item(self, item: dict, entity_type: str) -> int:
        if entity_type == 'plant':
            return self.db.add_plant(**item)
        elif entity_type == 'ingredient':
            return self.db.add_ingredient(**item)
        elif entity_type == 'ailment':
            return self.db.add_ailment(**item)
        elif entity_type == 'recipe':
            item['source_id'] = self.source_id
            return self.db.add_recipe(**item)
        return 0
    
    def run(self, resume_from: ScraperProgress = None, callback: callable = None) -> ScraperProgress:
        """Run the full scraping process."""
        self._stop_requested = False
        self.progress = resume_from or ScraperProgress()
        
        try:
            for item in self.scrape(resume_from):
                if self.should_stop():
                    break
                try:
                    processed = self.process_item(item)
                    if processed:
                        entity_type = processed.pop('_type', 'plant')
                        self.save_item(processed, entity_type)
                        self.progress.processed_items += 1
                except Exception as e:
                    self.progress.errors.append(str(e))
                
                if callback:
                    callback(item, self.progress)
        except Exception as e:
            self.progress.errors.append(f"Fatal error: {str(e)}")
        
        return self.progress
