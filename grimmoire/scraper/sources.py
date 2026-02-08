"""Source registry for managing data source scrapers."""
from typing import Type, Dict, Optional, List
from .base import BaseScraper
from ..db.manager import DatabaseManager


class SourceRegistry:
    """Registry of available data source scrapers."""
    
    _scrapers: Dict[str, Type[BaseScraper]] = {}
    
    @classmethod
    def register(cls, name: str, scraper_class: Type[BaseScraper]):
        cls._scrapers[name] = scraper_class
    
    @classmethod
    def get_scraper(cls, name: str, db: DatabaseManager, config: dict = None) -> Optional[BaseScraper]:
        scraper_class = cls._scrapers.get(name)
        if scraper_class:
            return scraper_class(db, name, config)
        return None
    
    @classmethod
    def list_sources(cls) -> List[str]:
        return list(cls._scrapers.keys())
    
    @classmethod
    def has_scraper(cls, name: str) -> bool:
        return name in cls._scrapers


def register_scraper(name: str):
    """Decorator to register a scraper class."""
    def decorator(cls: Type[BaseScraper]):
        SourceRegistry.register(name, cls)
        return cls
    return decorator
