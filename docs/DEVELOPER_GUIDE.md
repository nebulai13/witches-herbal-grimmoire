# Grimmoire Developer Guide

## Architecture Overview

```
grimmoire/
├── main.py              # CLI entry point
├── db/                  # Database layer
│   ├── schema.py        # SQLite schema + initialization
│   └── manager.py       # CRUD operations, FTS search
├── search/              # Search functionality
│   ├── engine.py        # Main search orchestration
│   ├── spellcheck.py    # Fuzzy matching (RapidFuzz)
│   └── pubmed.py        # PubMed E-utilities client
├── scraper/             # Data ingestion
│   ├── base.py          # Abstract base scraper
│   ├── sources.py       # Source registry pattern
│   └── crawlers/        # Concrete implementations
│       └── naeb.py      # NAEB + PubChem scrapers
├── jobs/                # Background processing
│   ├── runner.py        # Job execution with signals
│   └── journal.py       # Event journaling for recovery
└── repl/                # User interface
    ├── interface.py     # Main REPL loop
    └── commands.py      # Command handlers
```

## Key Design Patterns

### 1. Registry Pattern (Scrapers)

Scrapers self-register using a decorator:

```python
from grimmoire.scraper.sources import register_scraper, SourceRegistry

@register_scraper("My Source")
class MyScraper(BaseScraper):
    def scrape(self, resume_from=None):
        # yield items
        pass
    
    def process_item(self, item):
        # return normalized dict
        pass

# Usage
scraper = SourceRegistry.get_scraper("My Source", db)
```

### 2. Generator-Based Scraping

Scrapers yield items for memory efficiency:

```python
def scrape(self, resume_from=None):
    for page in range(start_page, total_pages):
        if self.should_stop():
            break
        
        for item in self.fetch_page(page):
            yield item
        
        self.progress.current_page = page
```

### 3. Journaling for Recovery

All job events are logged for crash recovery:

```python
# In runner.py
self.db.journal_event('start', {'timestamp': ...}, job_id)
self.db.journal_event('progress', progress_dict, job_id)
self.db.journal_event('interrupt_requested', {...}, job_id)

# In journal.py
def get_recovery_point(self, job_id):
    # Find last valid progress state
```

---

## Adding a New Scraper

### 1. Create the Scraper Class

```python
# grimmoire/scraper/crawlers/mysource.py
from typing import Generator, Optional, Dict
from ..base import BaseScraper, ScraperProgress
from ..sources import register_scraper

@register_scraper("My Source")
class MySourceScraper(BaseScraper):
    """Scraper for My Source API."""
    
    BASE_URL = "https://api.mysource.com"
    PAGE_SIZE = 100
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rate_limit = 5  # requests per second
    
    def scrape(self, resume_from: ScraperProgress = None) -> Generator[Dict, None, None]:
        if resume_from:
            self.progress = resume_from
        
        # Get total count
        total = self._get_total_count()
        self.progress.total_items = total
        
        # Resume from last page
        start_page = self.progress.current_page
        
        for page in range(start_page, (total // self.PAGE_SIZE) + 1):
            if self.should_stop():
                break
            
            items = self._fetch_page(page)
            for item in items:
                yield item
            
            self.progress.current_page = page
            self.progress.processed_items += len(items)
    
    def process_item(self, item: Dict) -> Optional[Dict]:
        """Transform raw item to normalized format."""
        return {
            '_type': 'plant',  # or 'ingredient', 'ailment', 'recipe'
            'name': item.get('name', ''),
            'scientific_name': item.get('latin_name'),
            'description': item.get('description'),
            # ... other fields
        }
    
    def _get_total_count(self) -> int:
        response = self._make_request(f"{self.BASE_URL}/count")
        return response.json().get('total', 0)
    
    def _fetch_page(self, page: int) -> list:
        response = self._make_request(
            f"{self.BASE_URL}/items",
            params={'page': page, 'size': self.PAGE_SIZE}
        )
        return response.json().get('items', [])
```

### 2. Register the Scraper

Add import to `grimmoire/scraper/crawlers/__init__.py`:

```python
from . import naeb
from . import mysource  # Add this
```

### 3. Add Source to Database

In `grimmoire/db/schema.py`, add to `DEFAULT_SOURCES`:

```python
DEFAULT_SOURCES = [
    # ... existing sources
    ("My Source", "https://mysource.com", "api", 50, 1, '{"rate_limit": 5}'),
]
```

---

## Database Schema

### Core Tables

```sql
-- Plants with taxonomy
CREATE TABLE plants (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    scientific_name TEXT,
    family TEXT,
    common_names TEXT,  -- JSON array
    description TEXT,
    taxonomy_id TEXT    -- NCBI taxonomy ID
);

-- Chemical compounds
CREATE TABLE ingredients (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    synonyms TEXT,           -- JSON array
    cas_number TEXT,
    pubchem_cid TEXT,
    inchi_key TEXT,
    smiles TEXT,
    molecular_formula TEXT,
    molecular_weight REAL
);

-- Diseases and conditions
CREATE TABLE ailments (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    synonyms TEXT,       -- JSON array
    icd10_code TEXT,
    mesh_id TEXT,
    category TEXT
);

-- Traditional formulations
CREATE TABLE recipes (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    tradition TEXT,      -- TCM, Ayurveda, etc.
    description TEXT,
    preparation TEXT,
    dosage TEXT,
    source_id INTEGER REFERENCES sources(id)
);
```

### Relationship Tables

```sql
-- Plant-ingredient relationships
CREATE TABLE plant_ingredients (
    plant_id INTEGER REFERENCES plants(id),
    ingredient_id INTEGER REFERENCES ingredients(id),
    part_used TEXT,      -- leaf, root, bark
    concentration TEXT
);

-- Plant-ailment relationships
CREATE TABLE plant_ailments (
    plant_id INTEGER REFERENCES plants(id),
    ailment_id INTEGER REFERENCES ailments(id),
    use_type TEXT,       -- primary, secondary
    evidence_level TEXT  -- traditional, clinical, research
);
```

### Full-Text Search

FTS5 virtual tables mirror main tables:

```sql
CREATE VIRTUAL TABLE fts_plants USING fts5(
    name, scientific_name, common_names, description,
    content='plants', content_rowid='id'
);
```

Triggers keep FTS in sync automatically.

---

## API Reference

### DatabaseManager

```python
from grimmoire.db.manager import DatabaseManager

db = DatabaseManager()

# CRUD operations
plant_id = db.add_plant(name="Sage", scientific_name="Salvia officinalis")
plant = db.get_plant(plant_id)
plants = db.search_plants("sage", limit=20)

# Source management
sources = db.get_sources(enabled_only=True)
db.disable_source(source_id)

# Job management
job_id = db.create_job('scrape', {'source': 'NAEB'})
db.update_job_status(job_id, 'running')
db.update_job_progress(job_id, {'page': 5}, results_count=500)

# Journaling
db.journal_event('progress', {'page': 5}, job_id)
entries = db.get_journal(job_id)
```

### SearchEngine

```python
from grimmoire.search.engine import SearchEngine, SearchType

engine = SearchEngine(db)

# Search with spell correction
results, suggestion = engine.search("chamomil", SearchType.PLANT)
if suggestion:
    print(f"Did you mean: {suggestion}")

# Autocomplete
suggestions = engine.autocomplete("cham", limit=5)
```

### PubMedClient

```python
from grimmoire.search.pubmed import PubMedClient

pubmed = PubMedClient(api_key="optional")

# Search herbs
articles = pubmed.search_herbs("chamomile", max_results=10)

# Search ailment treatments
articles = pubmed.search_ailment_treatment("insomnia", "valerian")

# Search compounds
articles = pubmed.search_compound("curcumin")
```

### JobRunner

```python
from grimmoire.jobs.runner import JobRunner, JobContext

runner = JobRunner(db)

def my_job(ctx: JobContext):
    for i in range(100):
        if ctx.should_stop():
            break
        # Do work
        ctx.progress_callback({'step': i}, i)

# Run synchronously
runner.run_job(job_id, my_job)

# Run in background
runner.run_job(job_id, my_job, async_mode=True)

# Handle interrupts
runner.request_stop()

# Resume paused job
runner.resume_job(job_id, my_resume_func)
```

---

## Testing

### Unit Tests

```python
# tests/test_search.py
import pytest
from grimmoire.db.manager import DatabaseManager
from grimmoire.search.engine import SearchEngine, SearchType

@pytest.fixture
def db():
    db = DatabaseManager(":memory:")
    db.add_plant(name="Chamomile", scientific_name="Matricaria chamomilla")
    yield db
    db.close()

def test_search_plant(db):
    engine = SearchEngine(db)
    results, _ = engine.search("chamomile", SearchType.PLANT)
    assert len(results) == 1
    assert results[0].data['name'] == "Chamomile"

def test_spell_correction(db):
    engine = SearchEngine(db)
    results, suggestion = engine.search("chamomil", SearchType.PLANT)
    assert suggestion == "chamomile"
```

### Integration Tests

```python
# tests/test_scraper.py
def test_naeb_scraper(db):
    scraper = SourceRegistry.get_scraper("NAEB Datasette", db)
    
    # Scrape first 10 items
    items = []
    for item in scraper.scrape():
        items.append(item)
        if len(items) >= 10:
            scraper.request_stop()
            break
    
    assert len(items) == 10
```

---

## Extending the REPL

### Adding a Command

1. Add handler in `commands.py`:

```python
def cmd_mycommand(self, args: List[str]) -> CommandResult:
    """
    My new command.
    Usage: mycommand <arg>
    """
    if not args:
        return CommandResult(False, "Usage: mycommand <arg>")
    
    # Do something
    result = self.do_something(args[0])
    
    return CommandResult(True, f"Result: {result}")
```

2. Add to `_handle_command` in `interface.py`:

```python
elif command == 'mycommand':
    return self.handler.cmd_mycommand(args)
```

3. Add to help text and autocomplete.

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GRIMMOIRE_DB` | Database path | `~/.grimmoire/grimmoire.db` |
| `NCBI_API_KEY` | PubMed API key | None |

### Config File (Future)

```yaml
# ~/.grimmoire/config.yaml
database:
  path: ~/.grimmoire/grimmoire.db

pubmed:
  api_key: your_key_here
  rate_limit: 10

scraping:
  default_timeout: 30
  retry_count: 3
```
