"""Database manager for Grimmoire."""
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, List, Dict, Set

from .schema import init_db, get_db_path


class DatabaseManager:
    """Manages all database operations."""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or get_db_path()
        self.conn = init_db(self.db_path)
    
    def close(self):
        self.conn.close()
    
    def add_plant(self, name: str, scientific_name: Optional[str] = None, family: Optional[str] = None,
                  common_names: Optional[List] = None, description: Optional[str] = None, 
                  taxonomy_id: Optional[str] = None) -> int:
        cursor = self.conn.execute("""
            INSERT INTO plants (name, scientific_name, family, common_names, description, taxonomy_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, scientific_name, family, json.dumps(common_names or []), description, taxonomy_id))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_plant(self, plant_id: int) -> Optional[Dict]:
        row = self.conn.execute("SELECT * FROM plants WHERE id = ?", (plant_id,)).fetchone()
        return dict(row) if row else None
    
    def search_plants(self, query: str, limit: int = 20) -> List[Dict]:
        rows = self.conn.execute("""
            SELECT p.* FROM plants p JOIN fts_plants fts ON p.id = fts.rowid
            WHERE fts_plants MATCH ? ORDER BY rank LIMIT ?
        """, (query, limit)).fetchall()
        return [dict(row) for row in rows]
    
    def add_ingredient(self, name: str, synonyms: Optional[List] = None, cas_number: Optional[str] = None,
                       pubchem_cid: Optional[str] = None, inchi_key: Optional[str] = None, 
                       smiles: Optional[str] = None, molecular_formula: Optional[str] = None, 
                       molecular_weight: Optional[float] = None, description: Optional[str] = None) -> int:
        cursor = self.conn.execute("""
            INSERT INTO ingredients (name, synonyms, cas_number, pubchem_cid, inchi_key,
                                     smiles, molecular_formula, molecular_weight, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, json.dumps(synonyms or []), cas_number, pubchem_cid, inchi_key,
              smiles, molecular_formula, molecular_weight, description))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_ingredient(self, ingredient_id: int) -> Optional[Dict]:
        row = self.conn.execute("SELECT * FROM ingredients WHERE id = ?", (ingredient_id,)).fetchone()
        return dict(row) if row else None
    
    def search_ingredients(self, query: str, limit: int = 20) -> List[Dict]:
        rows = self.conn.execute("""
            SELECT i.* FROM ingredients i JOIN fts_ingredients fts ON i.id = fts.rowid
            WHERE fts_ingredients MATCH ? ORDER BY rank LIMIT ?
        """, (query, limit)).fetchall()
        return [dict(row) for row in rows]
    
    def add_ailment(self, name: str, synonyms: Optional[List] = None, icd10_code: Optional[str] = None,
                    mesh_id: Optional[str] = None, category: Optional[str] = None, 
                    description: Optional[str] = None) -> int:
        cursor = self.conn.execute("""
            INSERT INTO ailments (name, synonyms, icd10_code, mesh_id, category, description)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, json.dumps(synonyms or []), icd10_code, mesh_id, category, description))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_ailment(self, ailment_id: int) -> Optional[Dict]:
        row = self.conn.execute("SELECT * FROM ailments WHERE id = ?", (ailment_id,)).fetchone()
        return dict(row) if row else None
    
    def search_ailments(self, query: str, limit: int = 20) -> List[Dict]:
        rows = self.conn.execute("""
            SELECT a.* FROM ailments a JOIN fts_ailments fts ON a.id = fts.rowid
            WHERE fts_ailments MATCH ? ORDER BY rank LIMIT ?
        """, (query, limit)).fetchall()
        return [dict(row) for row in rows]
    
    def add_recipe(self, name: str, tradition: Optional[str] = None, description: Optional[str] = None,
                   preparation: Optional[str] = None, dosage: Optional[str] = None, 
                   source_id: Optional[int] = None) -> int:
        cursor = self.conn.execute("""
            INSERT INTO recipes (name, tradition, description, preparation, dosage, source_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, tradition, description, preparation, dosage, source_id))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_recipe(self, recipe_id: int) -> Optional[Dict]:
        row = self.conn.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,)).fetchone()
        return dict(row) if row else None
    
    def search_recipes(self, query: str, limit: int = 20) -> List[Dict]:
        rows = self.conn.execute("""
            SELECT r.* FROM recipes r JOIN fts_recipes fts ON r.id = fts.rowid
            WHERE fts_recipes MATCH ? ORDER BY rank LIMIT ?
        """, (query, limit)).fetchall()
        return [dict(row) for row in rows]
    
    def get_sources(self, enabled_only: bool = False) -> List[Dict]:
        query = "SELECT * FROM sources"
        if enabled_only:
            query += " WHERE enabled = 1"
        query += " ORDER BY priority DESC"
        rows = self.conn.execute(query).fetchall()
        return [dict(row) for row in rows]
    
    def add_source(self, name: str, url: str, source_type: str = "manual",
                   priority: int = 50, config: Optional[Dict] = None) -> int:
        cursor = self.conn.execute("""
            INSERT INTO sources (name, url, source_type, priority, enabled, config)
            VALUES (?, ?, ?, ?, 1, ?)
        """, (name, url, source_type, priority, json.dumps(config or {})))
        self.conn.commit()
        return cursor.lastrowid
    
    def enable_source(self, source_id: int):
        self.conn.execute("UPDATE sources SET enabled = 1 WHERE id = ?", (source_id,))
        self.conn.commit()
    
    def disable_source(self, source_id: int):
        self.conn.execute("UPDATE sources SET enabled = 0 WHERE id = ?", (source_id,))
        self.conn.commit()
    
    def update_source_scraped(self, source_id: int):
        self.conn.execute("UPDATE sources SET last_scraped = ? WHERE id = ?",
                         (datetime.now().isoformat(), source_id))
        self.conn.commit()
    
    def create_job(self, job_type: str, query: Optional[Dict] = None) -> int:
        cursor = self.conn.execute("""
            INSERT INTO jobs (job_type, query, status) VALUES (?, ?, 'pending')
        """, (job_type, json.dumps(query or {})))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_job(self, job_id: int) -> Optional[Dict]:
        row = self.conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        return dict(row) if row else None
    
    def get_jobs(self, status: Optional[str] = None) -> List[Dict]:
        if status:
            rows = self.conn.execute("SELECT * FROM jobs WHERE status = ? ORDER BY created_at DESC", (status,)).fetchall()
        else:
            rows = self.conn.execute("SELECT * FROM jobs ORDER BY created_at DESC").fetchall()
        return [dict(row) for row in rows]
    
    def update_job_status(self, job_id: int, status: str, error: Optional[str] = None):
        if status == 'running':
            self.conn.execute("UPDATE jobs SET status = ?, started_at = ? WHERE id = ?",
                            (status, datetime.now().isoformat(), job_id))
        elif status in ('completed', 'failed'):
            self.conn.execute("UPDATE jobs SET status = ?, completed_at = ?, error = ? WHERE id = ?",
                            (status, datetime.now().isoformat(), error, job_id))
        else:
            self.conn.execute("UPDATE jobs SET status = ? WHERE id = ?", (status, job_id))
        self.conn.commit()
    
    def update_job_progress(self, job_id: int, progress: Dict, results_count: Optional[int] = None):
        if results_count is not None:
            self.conn.execute("UPDATE jobs SET progress = ?, results_count = ? WHERE id = ?",
                            (json.dumps(progress), results_count, job_id))
        else:
            self.conn.execute("UPDATE jobs SET progress = ? WHERE id = ?", (json.dumps(progress), job_id))
        self.conn.commit()
    
    def add_job_result(self, job_id: int, result_type: str, result_data: Dict) -> int:
        cursor = self.conn.execute("""
            INSERT INTO job_results (job_id, result_type, result_data) VALUES (?, ?, ?)
        """, (job_id, result_type, json.dumps(result_data)))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_job_results(self, job_id: int, limit: int = 100) -> List[Dict]:
        rows = self.conn.execute("SELECT * FROM job_results WHERE job_id = ? ORDER BY created_at LIMIT ?",
                                (job_id, limit)).fetchall()
        return [dict(row) for row in rows]
    
    def journal_event(self, event_type: str, event_data: Optional[Dict] = None, job_id: Optional[int] = None):
        self.conn.execute("INSERT INTO journal (job_id, event_type, event_data) VALUES (?, ?, ?)",
                         (job_id, event_type, json.dumps(event_data or {})))
        self.conn.commit()
    
    def get_journal(self, job_id: Optional[int] = None, limit: int = 100) -> List[Dict]:
        if job_id:
            rows = self.conn.execute("SELECT * FROM journal WHERE job_id = ? ORDER BY created_at DESC LIMIT ?",
                                    (job_id, limit)).fetchall()
        else:
            rows = self.conn.execute("SELECT * FROM journal ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        return [dict(row) for row in rows]
    
    def log_search(self, query: str, corrected_query: Optional[str] = None, 
                   search_type: Optional[str] = None, results_count: int = 0):
        self.conn.execute("""
            INSERT INTO search_history (query, corrected_query, search_type, results_count)
            VALUES (?, ?, ?, ?)
        """, (query, corrected_query, search_type, results_count))
        self.conn.commit()
    
    def get_stats(self) -> Dict:
        stats = {}
        for table in ['plants', 'ingredients', 'ailments', 'recipes', 'sources', 'jobs']:
            row = self.conn.execute(f"SELECT COUNT(*) as count FROM {table}").fetchone()
            stats[table] = row['count']
        return stats
    
    def get_all_names(self) -> Set[str]:
        names = set()
        for table, col in [('plants', 'name'), ('plants', 'scientific_name'),
                           ('ingredients', 'name'), ('ailments', 'name'), ('recipes', 'name')]:
            rows = self.conn.execute(f"SELECT {col} FROM {table} WHERE {col} IS NOT NULL").fetchall()
            names.update(row[0].lower() for row in rows)
        return names
