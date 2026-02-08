"""SQLite database schema for Grimmoire."""
import sqlite3
from pathlib import Path
from typing import Optional

SCHEMA = """
-- Core entities
CREATE TABLE IF NOT EXISTS plants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    scientific_name TEXT,
    family TEXT,
    common_names TEXT,
    description TEXT,
    taxonomy_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_plants_name ON plants(name);
CREATE INDEX IF NOT EXISTS idx_plants_scientific ON plants(scientific_name);

CREATE TABLE IF NOT EXISTS ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    synonyms TEXT,
    cas_number TEXT,
    pubchem_cid TEXT,
    inchi_key TEXT,
    smiles TEXT,
    molecular_formula TEXT,
    molecular_weight REAL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_ingredients_name ON ingredients(name);
CREATE INDEX IF NOT EXISTS idx_ingredients_pubchem ON ingredients(pubchem_cid);

CREATE TABLE IF NOT EXISTS ailments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    synonyms TEXT,
    icd10_code TEXT,
    mesh_id TEXT,
    category TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_ailments_name ON ailments(name);

CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    tradition TEXT,
    description TEXT,
    preparation TEXT,
    dosage TEXT,
    source_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES sources(id)
);
CREATE INDEX IF NOT EXISTS idx_recipes_name ON recipes(name);

-- Relationships
CREATE TABLE IF NOT EXISTS plant_ingredients (
    plant_id INTEGER NOT NULL,
    ingredient_id INTEGER NOT NULL,
    part_used TEXT,
    concentration TEXT,
    PRIMARY KEY (plant_id, ingredient_id),
    FOREIGN KEY (plant_id) REFERENCES plants(id),
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(id)
);

CREATE TABLE IF NOT EXISTS plant_ailments (
    plant_id INTEGER NOT NULL,
    ailment_id INTEGER NOT NULL,
    use_type TEXT,
    evidence_level TEXT,
    notes TEXT,
    PRIMARY KEY (plant_id, ailment_id),
    FOREIGN KEY (plant_id) REFERENCES plants(id),
    FOREIGN KEY (ailment_id) REFERENCES ailments(id)
);

CREATE TABLE IF NOT EXISTS recipe_ingredients (
    recipe_id INTEGER NOT NULL,
    ingredient_id INTEGER,
    plant_id INTEGER,
    amount TEXT,
    preparation TEXT,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id),
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(id),
    FOREIGN KEY (plant_id) REFERENCES plants(id)
);

CREATE TABLE IF NOT EXISTS recipe_ailments (
    recipe_id INTEGER NOT NULL,
    ailment_id INTEGER NOT NULL,
    PRIMARY KEY (recipe_id, ailment_id),
    FOREIGN KEY (recipe_id) REFERENCES recipes(id),
    FOREIGN KEY (ailment_id) REFERENCES ailments(id)
);

-- Sources management
CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    url TEXT,
    source_type TEXT,
    priority INTEGER DEFAULT 50,
    enabled INTEGER DEFAULT 1,
    last_scraped TIMESTAMP,
    config TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Background jobs & journaling
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_type TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    query TEXT,
    progress TEXT,
    results_count INTEGER DEFAULT 0,
    error TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS job_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER NOT NULL,
    result_type TEXT,
    result_data TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs(id)
);

CREATE TABLE IF NOT EXISTS journal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER,
    event_type TEXT NOT NULL,
    event_data TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs(id)
);

-- Full-text search
CREATE VIRTUAL TABLE IF NOT EXISTS fts_plants USING fts5(
    name, scientific_name, common_names, description,
    content='plants', content_rowid='id'
);

CREATE VIRTUAL TABLE IF NOT EXISTS fts_ingredients USING fts5(
    name, synonyms, description,
    content='ingredients', content_rowid='id'
);

CREATE VIRTUAL TABLE IF NOT EXISTS fts_ailments USING fts5(
    name, synonyms, description,
    content='ailments', content_rowid='id'
);

CREATE VIRTUAL TABLE IF NOT EXISTS fts_recipes USING fts5(
    name, description, preparation,
    content='recipes', content_rowid='id'
);

-- Triggers to keep FTS in sync
CREATE TRIGGER IF NOT EXISTS plants_ai AFTER INSERT ON plants BEGIN
    INSERT INTO fts_plants(rowid, name, scientific_name, common_names, description)
    VALUES (new.id, new.name, new.scientific_name, new.common_names, new.description);
END;

CREATE TRIGGER IF NOT EXISTS plants_ad AFTER DELETE ON plants BEGIN
    INSERT INTO fts_plants(fts_plants, rowid, name, scientific_name, common_names, description)
    VALUES ('delete', old.id, old.name, old.scientific_name, old.common_names, old.description);
END;

CREATE TRIGGER IF NOT EXISTS ingredients_ai AFTER INSERT ON ingredients BEGIN
    INSERT INTO fts_ingredients(rowid, name, synonyms, description)
    VALUES (new.id, new.name, new.synonyms, new.description);
END;

CREATE TRIGGER IF NOT EXISTS ingredients_ad AFTER DELETE ON ingredients BEGIN
    INSERT INTO fts_ingredients(fts_ingredients, rowid, name, synonyms, description)
    VALUES ('delete', old.id, old.name, old.synonyms, old.description);
END;

CREATE TRIGGER IF NOT EXISTS ailments_ai AFTER INSERT ON ailments BEGIN
    INSERT INTO fts_ailments(rowid, name, synonyms, description)
    VALUES (new.id, new.name, new.synonyms, new.description);
END;

CREATE TRIGGER IF NOT EXISTS ailments_ad AFTER DELETE ON ailments BEGIN
    INSERT INTO fts_ailments(fts_ailments, rowid, name, synonyms, description)
    VALUES ('delete', old.id, old.name, old.synonyms, old.description);
END;

CREATE TRIGGER IF NOT EXISTS recipes_ai AFTER INSERT ON recipes BEGIN
    INSERT INTO fts_recipes(rowid, name, description, preparation)
    VALUES (new.id, new.name, new.description, new.preparation);
END;

CREATE TRIGGER IF NOT EXISTS recipes_ad AFTER DELETE ON recipes BEGIN
    INSERT INTO fts_recipes(fts_recipes, rowid, name, description, preparation)
    VALUES ('delete', old.id, old.name, old.description, old.preparation);
END;

-- Search history
CREATE TABLE IF NOT EXISTS search_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT NOT NULL,
    corrected_query TEXT,
    search_type TEXT,
    results_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

DEFAULT_SOURCES = [
    ("NAEB Datasette", "https://naeb.louispotok.com", "api", 100, 1, '{"base_url": "https://naeb.louispotok.com"}'),
    ("PubChem", "https://pubchem.ncbi.nlm.nih.gov", "api", 90, 1, '{"rate_limit": 5}'),
    ("PubMed", "https://pubmed.ncbi.nlm.nih.gov", "api", 85, 1, '{"rate_limit": 3}'),
    ("COCONUT", "https://coconut.naturalproducts.net", "api", 80, 1, '{}'),
    ("Dr. Duke's", "https://phytochem.nal.usda.gov", "scrape", 75, 1, '{}'),
    ("HERB 2.0", "http://herb.ac.cn", "scrape", 70, 1, '{}'),
    ("TCMBank", "https://tcmbank.cn", "bulk", 65, 1, '{}'),
    ("OSADHI", "https://neist.res.in/osadhi", "scrape", 60, 1, '{}'),
    ("IMPPAT", "https://cb.imsc.res.in/imppat", "scrape", 55, 1, '{}'),
    ("MSK Herbs", "https://www.mskcc.org/cancer-care/diagnosis-treatment/symptom-management/integrative-medicine/herbs", "scrape", 50, 1, '{}'),
]


def get_db_path() -> Path:
    """Get the database path in user's data directory."""
    data_dir = Path.home() / ".grimmoire"
    data_dir.mkdir(exist_ok=True)
    return data_dir / "grimmoire.db"


def init_db(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Initialize the database with schema."""
    if db_path is None:
        db_path = get_db_path()
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    
    conn.executescript(SCHEMA)
    
    for source in DEFAULT_SOURCES:
        conn.execute("""
            INSERT OR IGNORE INTO sources (name, url, source_type, priority, enabled, config)
            VALUES (?, ?, ?, ?, ?, ?)
        """, source)
    
    conn.commit()
    return conn
