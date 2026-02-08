"""Search engine for Grimmoire."""
from typing import Any, Optional, List, Tuple
from enum import Enum

from ..db.manager import DatabaseManager
from .spellcheck import SpellChecker


class SearchType(str, Enum):
    PLANT = "plant"
    INGREDIENT = "ingredient"
    AILMENT = "ailment"
    RECIPE = "recipe"
    ALL = "all"


class SearchResult:
    """A search result with metadata."""
    
    def __init__(self, result_type: str, data: dict, source: str = "local", score: float = 1.0):
        self.type = result_type
        self.data = data
        self.source = source
        self.score = score
    
    def to_dict(self) -> dict:
        return {"type": self.type, "data": self.data, "source": self.source, "score": self.score}
    
    def __repr__(self):
        return f"<SearchResult {self.type}: {self.data.get('name', 'Unknown')}>"


class SearchEngine:
    """Main search engine coordinating local DB and external APIs."""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.spellchecker = SpellChecker()
        self._load_dictionary()
    
    def _load_dictionary(self):
        names = self.db.get_all_names()
        self.spellchecker.update_dictionary(names)
    
    def refresh_dictionary(self):
        self._load_dictionary()
    
    def search(self, query: str, search_type: SearchType = SearchType.ALL,
               limit: int = 20, correct_spelling: bool = True) -> Tuple[List[SearchResult], Optional[str]]:
        """Search the local database. Returns (results, correction_suggestion)."""
        original_query = query
        suggestion = None
        
        if correct_spelling:
            corrected, alternatives = self.spellchecker.check(query)
            if corrected.lower() != query.lower():
                suggestion = corrected
                query = corrected
        
        results = []
        
        if search_type in (SearchType.ALL, SearchType.PLANT):
            try:
                plants = self.db.search_plants(query, limit)
                results.extend([SearchResult("plant", p, "local") for p in plants])
            except Exception:
                pass
        
        if search_type in (SearchType.ALL, SearchType.INGREDIENT):
            try:
                ingredients = self.db.search_ingredients(query, limit)
                results.extend([SearchResult("ingredient", i, "local") for i in ingredients])
            except Exception:
                pass
        
        if search_type in (SearchType.ALL, SearchType.AILMENT):
            try:
                ailments = self.db.search_ailments(query, limit)
                results.extend([SearchResult("ailment", a, "local") for a in ailments])
            except Exception:
                pass
        
        if search_type in (SearchType.ALL, SearchType.RECIPE):
            try:
                recipes = self.db.search_recipes(query, limit)
                results.extend([SearchResult("recipe", r, "local") for r in recipes])
            except Exception:
                pass
        
        self.db.log_search(original_query, suggestion, search_type.value, len(results))
        
        if not results and not suggestion:
            suggestion = self.spellchecker.did_you_mean(original_query, 0)
        
        return results[:limit], suggestion
    
    def search_by_relationship(self, entity_type: str, entity_id: int, target_type: str) -> List[SearchResult]:
        """Search for related entities."""
        results = []
        
        if entity_type == "plant" and target_type == "ailment":
            rows = self.db.conn.execute("""
                SELECT a.* FROM ailments a JOIN plant_ailments pa ON a.id = pa.ailment_id
                WHERE pa.plant_id = ?
            """, (entity_id,)).fetchall()
            results = [SearchResult("ailment", dict(r), "local") for r in rows]
        
        elif entity_type == "plant" and target_type == "ingredient":
            rows = self.db.conn.execute("""
                SELECT i.* FROM ingredients i JOIN plant_ingredients pi ON i.id = pi.ingredient_id
                WHERE pi.plant_id = ?
            """, (entity_id,)).fetchall()
            results = [SearchResult("ingredient", dict(r), "local") for r in rows]
        
        elif entity_type == "ailment" and target_type == "plant":
            rows = self.db.conn.execute("""
                SELECT p.* FROM plants p JOIN plant_ailments pa ON p.id = pa.plant_id
                WHERE pa.ailment_id = ?
            """, (entity_id,)).fetchall()
            results = [SearchResult("plant", dict(r), "local") for r in rows]
        
        return results
    
    def autocomplete(self, partial: str, limit: int = 10) -> List[str]:
        return self.spellchecker.suggest(partial, limit)
