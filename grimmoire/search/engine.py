"""Search engine for Grimmoire."""
from typing import Any, Optional, List, Tuple, Dict
from enum import Enum

from ..db.manager import DatabaseManager
from .spellcheck import SpellChecker
from .web_provider import (
    WebSearchAggregator, WebSearchResult, SourceType,
    get_provider, list_providers
)


class SearchType(str, Enum):
    PLANT = "plant"
    INGREDIENT = "ingredient"
    AILMENT = "ailment"
    RECIPE = "recipe"
    ALL = "all"


# Map SearchType to web SourceType
_TYPE_MAP = {
    SearchType.PLANT: SourceType.PLANT,
    SearchType.INGREDIENT: SourceType.COMPOUND,
    SearchType.AILMENT: SourceType.CLINICAL,
    SearchType.RECIPE: SourceType.ETHNOBOTANY,
}


class SearchResult:
    """A search result with metadata."""
    
    def __init__(self, result_type: str, data: dict, source: str = "local", score: float = 1.0, url: str = None):
        self.type = result_type
        self.data = data
        self.source = source
        self.score = score
        self.url = url
    
    def to_dict(self) -> dict:
        return {"type": self.type, "data": self.data, "source": self.source, "score": self.score, "url": self.url}
    
    def __repr__(self):
        return f"<SearchResult {self.type}: {self.data.get('name', 'Unknown')}>"
    
    @classmethod
    def from_web_result(cls, web_result: WebSearchResult) -> 'SearchResult':
        """Convert a WebSearchResult to SearchResult."""
        # Map web result types to local types
        type_map = {
            "compound": "ingredient",
            "clinical_trial": "ailment",
            "ethnobotany": "recipe",
        }
        result_type = type_map.get(web_result.result_type, web_result.result_type)
        
        data = {"name": web_result.name, **web_result.data}
        return cls(result_type, data, source=web_result.source, score=web_result.score, url=web_result.url)


class SearchEngine:
    """Main search engine coordinating local DB and external APIs."""
    
    def __init__(self, db: DatabaseManager, web_fallback: bool = True, web_config: Dict = None):
        self.db = db
        self.spellchecker = SpellChecker()
        self.web_fallback = web_fallback
        self.web_aggregator = WebSearchAggregator(web_config) if web_fallback else None
        self._load_dictionary()
    
    def _load_dictionary(self):
        names = self.db.get_all_names()
        self.spellchecker.update_dictionary(names)
    
    def refresh_dictionary(self):
        self._load_dictionary()
    
    def search(self, query: str, search_type: SearchType = SearchType.ALL,
               limit: int = 20, correct_spelling: bool = True,
               include_web: bool = None) -> Tuple[List[SearchResult], Optional[str]]:
        """Search local database, with optional web fallback.
        
        Args:
            query: Search query
            search_type: Type of entity to search for
            limit: Maximum results to return
            correct_spelling: Whether to suggest spelling corrections
            include_web: Force web search (True), force local only (False), or auto (None = fallback if no local)
        
        Returns:
            Tuple of (results list, spelling suggestion or None)
        """
        original_query = query
        suggestion = None
        
        if correct_spelling:
            corrected, alternatives = self.spellchecker.check(query)
            if corrected.lower() != query.lower():
                suggestion = corrected
                query = corrected
        
        results = []
        
        # Local search
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
        
        # Web fallback: search web if no local results (auto mode) or if forced
        should_search_web = (
            include_web is True or  # Forced web search
            (include_web is None and not results and self.web_fallback)  # Auto fallback
        )
        
        if should_search_web and self.web_aggregator:
            web_results = self._search_web(original_query, search_type, limit - len(results))
            results.extend(web_results)
        
        self.db.log_search(original_query, suggestion, search_type.value, len(results))
        
        if not results and not suggestion:
            suggestion = self.spellchecker.did_you_mean(original_query, 0)
        
        return results[:limit], suggestion
    
    def _search_web(self, query: str, search_type: SearchType, limit: int) -> List[SearchResult]:
        """Search web providers."""
        if not self.web_aggregator:
            return []
        
        # Map search type to web source types
        source_types = None
        if search_type != SearchType.ALL:
            source_type = _TYPE_MAP.get(search_type)
            source_types = [source_type] if source_type else None
        
        try:
            web_results = self.web_aggregator.search(query, source_types, limit)
            return [SearchResult.from_web_result(r) for r in web_results]
        except Exception:
            return []
    
    def search_web_only(self, query: str, search_type: SearchType = SearchType.ALL,
                        limit: int = 20, providers: List[str] = None) -> List[SearchResult]:
        """Search only web providers (bypass local database)."""
        if not self.web_aggregator:
            self.web_aggregator = WebSearchAggregator({"providers": providers} if providers else None)
        
        if providers:
            # Temporarily override providers
            old_providers = self.web_aggregator.enabled_providers
            self.web_aggregator.enabled_providers = providers
            results = self._search_web(query, search_type, limit)
            self.web_aggregator.enabled_providers = old_providers
            return results
        
        return self._search_web(query, search_type, limit)
    
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
