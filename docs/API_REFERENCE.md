# API Reference

## Database Module

### grimmoire.db.schema

#### `get_db_path() -> Path`
Returns the default database path (`~/.grimmoire/grimmoire.db`).

#### `init_db(db_path: Path = None) -> sqlite3.Connection`
Initialize the database with schema and default sources.

---

### grimmoire.db.manager.DatabaseManager

```python
class DatabaseManager:
    def __init__(self, db_path: Path = None)
```

#### Plant Operations

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `add_plant` | name, scientific_name=None, family=None, common_names=None, description=None, taxonomy_id=None | int | Add a plant, returns ID |
| `get_plant` | plant_id: int | dict \| None | Get plant by ID |
| `search_plants` | query: str, limit: int = 20 | list[dict] | FTS search |

#### Ingredient Operations

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `add_ingredient` | name, synonyms=None, cas_number=None, pubchem_cid=None, inchi_key=None, smiles=None, molecular_formula=None, molecular_weight=None, description=None | int | Add ingredient |
| `get_ingredient` | ingredient_id: int | dict \| None | Get by ID |
| `search_ingredients` | query: str, limit: int = 20 | list[dict] | FTS search |

#### Ailment Operations

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `add_ailment` | name, synonyms=None, icd10_code=None, mesh_id=None, category=None, description=None | int | Add ailment |
| `get_ailment` | ailment_id: int | dict \| None | Get by ID |
| `search_ailments` | query: str, limit: int = 20 | list[dict] | FTS search |

#### Recipe Operations

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `add_recipe` | name, tradition=None, description=None, preparation=None, dosage=None, source_id=None | int | Add recipe |
| `get_recipe` | recipe_id: int | dict \| None | Get by ID |
| `search_recipes` | query: str, limit: int = 20 | list[dict] | FTS search |

#### Source Operations

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `get_sources` | enabled_only: bool = False | list[dict] | List all sources |
| `add_source` | name, url, source_type="manual", priority=50, config=None | int | Add source |
| `enable_source` | source_id: int | None | Enable source |
| `disable_source` | source_id: int | None | Disable source |
| `update_source_scraped` | source_id: int | None | Update last_scraped |

#### Job Operations

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `create_job` | job_type: str, query: dict = None | int | Create job |
| `get_job` | job_id: int | dict \| None | Get job |
| `get_jobs` | status: str = None | list[dict] | List jobs |
| `update_job_status` | job_id, status, error=None | None | Update status |
| `update_job_progress` | job_id, progress: dict, results_count=None | None | Update progress |

#### Journal Operations

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `journal_event` | event_type, event_data=None, job_id=None | None | Log event |
| `get_journal` | job_id=None, limit=100 | list[dict] | Get entries |

#### Utility Operations

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `get_stats` | | dict | Entity counts |
| `get_all_names` | | set[str] | All names for spellcheck |
| `bulk_insert_plants` | plants: list[dict] | int | Bulk insert |
| `log_search` | query, corrected_query=None, search_type=None, results_count=0 | None | Log search |

---

## Search Module

### grimmoire.search.engine.SearchType

```python
class SearchType(str, Enum):
    PLANT = "plant"
    INGREDIENT = "ingredient"
    AILMENT = "ailment"
    RECIPE = "recipe"
    ALL = "all"
```

### grimmoire.search.engine.SearchResult

```python
@dataclass
class SearchResult:
    type: str          # "plant", "ingredient", etc.
    data: dict         # Entity data
    source: str        # "local" or source name
    score: float       # Relevance score
```

### grimmoire.search.engine.SearchEngine

```python
class SearchEngine:
    def __init__(self, db: DatabaseManager)
```

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `search` | query, search_type=ALL, limit=20, correct_spelling=True | (list[SearchResult], str \| None) | Search with correction |
| `search_by_relationship` | entity_type, entity_id, target_type | list[SearchResult] | Find related entities |
| `autocomplete` | partial: str, limit=10 | list[str] | Get suggestions |
| `refresh_dictionary` | | None | Reload spellcheck dict |

### grimmoire.search.spellcheck.SpellChecker

```python
class SpellChecker:
    def __init__(self, dictionary: set[str] = None)
```

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `update_dictionary` | words: set[str] | None | Add words |
| `check` | query: str | (str, list[str]) | (corrected, suggestions) |
| `suggest` | partial: str, limit=10 | list[str] | Autocomplete |
| `did_you_mean` | query, results_count | str \| None | Suggestion if no results |

### grimmoire.search.pubmed.PubMedClient

```python
class PubMedClient:
    def __init__(self, api_key: str = None, email: str = None)
```

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `search` | query, max_results=20, retstart=0 | dict | Search PubMed |
| `fetch_summaries` | pmids: list[str] | list[dict] | Get article summaries |
| `fetch_abstracts` | pmids: list[str] | dict[str, str] | Get abstracts |
| `search_herbs` | herb_name, max_results=20 | list[dict] | Search herb research |
| `search_ailment_treatment` | ailment, treatment=None, max_results=20 | list[dict] | Search treatments |
| `search_compound` | compound_name, max_results=20 | list[dict] | Search compound research |

---

## Scraper Module

### grimmoire.scraper.base.ScraperProgress

```python
@dataclass
class ScraperProgress:
    total_items: int = 0
    processed_items: int = 0
    current_page: int = 0
    last_id: str = None
    errors: list = field(default_factory=list)
```

### grimmoire.scraper.base.BaseScraper

Abstract base class for scrapers.

```python
class BaseScraper(ABC):
    def __init__(self, db: DatabaseManager, source_name: str, config: dict = None)
```

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `scrape` | resume_from: ScraperProgress = None | Generator[dict] | **Abstract** - yield items |
| `process_item` | item: dict | dict \| None | **Abstract** - normalize |
| `run` | resume_from=None, callback=None | ScraperProgress | Run full scrape |
| `request_stop` | | None | Request graceful stop |
| `should_stop` | | bool | Check stop requested |
| `save_item` | item: dict, entity_type: str | int | Save to DB |

### grimmoire.scraper.sources.SourceRegistry

```python
class SourceRegistry:
    @classmethod
    def register(cls, name: str, scraper_class: Type[BaseScraper])
    
    @classmethod
    def get_scraper(cls, name: str, db: DatabaseManager, config: dict = None) -> BaseScraper
    
    @classmethod
    def list_sources(cls) -> list[str]
    
    @classmethod
    def has_scraper(cls, name: str) -> bool
```

### @register_scraper decorator

```python
from grimmoire.scraper.sources import register_scraper

@register_scraper("Source Name")
class MyScraper(BaseScraper):
    ...
```

---

## Jobs Module

### grimmoire.jobs.runner.JobStatus

```python
class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
```

### grimmoire.jobs.runner.JobContext

```python
@dataclass
class JobContext:
    job_id: int
    db: DatabaseManager
    progress_callback: Callable
    should_stop: Callable[[], bool]
```

### grimmoire.jobs.runner.JobRunner

```python
class JobRunner:
    def __init__(self, db: DatabaseManager)
```

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `run_job` | job_id, job_func, async_mode=False | Any | Run job |
| `resume_job` | job_id, job_func, async_mode=False | Any | Resume paused job |
| `request_stop` | | None | Request stop |
| `should_stop` | | bool | Check stop |
| `wait_for_completion` | timeout=None | bool | Wait for async job |
| `get_resumable_jobs` | | list[dict] | Get paused jobs |

### grimmoire.jobs.journal.Journal

```python
class Journal:
    def __init__(self, db: DatabaseManager)
```

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `log` | event_type, data=None, job_id=None | None | Log event |
| `get_last_checkpoint` | job_id: int | dict \| None | Last progress |
| `get_recovery_point` | job_id: int | dict \| None | Resume state |
| `get_job_timeline` | job_id: int | list[dict] | Full timeline |
| `summarize_job` | job_id: int | dict | Job summary |
| `clear_old_entries` | days: int = 30 | None | Cleanup |

---

## REPL Module

### grimmoire.repl.commands.CommandResult

```python
@dataclass
class CommandResult:
    success: bool
    message: str = ""
    data: any = None
```

### grimmoire.repl.commands.CommandHandler

```python
class CommandHandler:
    def __init__(self, db: DatabaseManager, console: Console)
```

Command methods:
- `cmd_search(args)` - Search database
- `cmd_find(args)` - Quick search
- `cmd_pubmed(args)` - PubMed search
- `cmd_sources(args)` - Source management
- `cmd_scrape(args, timeout=30)` - Run scraper
- `cmd_jobs(args)` - Job management
- `cmd_db(args)` - Database utilities

### grimmoire.repl.interface.GrimmoireREPL

```python
class GrimmoireREPL:
    def __init__(self, db_path: Path = None)
    
    def run(self) -> None  # Main loop
```
