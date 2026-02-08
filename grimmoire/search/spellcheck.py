"""Spell checking and fuzzy matching for search queries."""
from rapidfuzz import fuzz, process
from typing import Optional, List, Tuple, Set


class SpellChecker:
    """Provides spell correction and fuzzy matching for search queries."""
    
    def __init__(self, dictionary: Set[str] = None):
        self.dictionary = dictionary or set()
        self.min_score = 70
    
    def update_dictionary(self, words: Set[str]):
        self.dictionary.update(w.lower() for w in words if w)
    
    def check(self, query: str) -> Tuple[str, List[str]]:
        """Check query and return (corrected_query, suggestions)."""
        if not self.dictionary:
            return query, []
        
        words = query.lower().split()
        corrected_words = []
        all_suggestions = []
        
        for word in words:
            if word in self.dictionary:
                corrected_words.append(word)
            else:
                matches = process.extract(word, self.dictionary, scorer=fuzz.ratio, limit=5)
                good_matches = [(m[0], m[1]) for m in matches if m[1] >= self.min_score]
                
                if good_matches:
                    corrected_words.append(good_matches[0][0])
                    for match, score in good_matches[1:]:
                        all_suggestions.append(match)
                else:
                    corrected_words.append(word)
        
        return ' '.join(corrected_words), all_suggestions
    
    def suggest(self, partial: str, limit: int = 10) -> List[str]:
        """Get suggestions for partial input (autocomplete)."""
        if not self.dictionary or not partial:
            return []
        
        partial_lower = partial.lower()
        prefix_matches = [w for w in self.dictionary if w.startswith(partial_lower)]
        fuzzy_matches = process.extract(partial_lower, self.dictionary, scorer=fuzz.partial_ratio, limit=limit * 2)
        
        results = list(prefix_matches[:limit])
        for match, score, _ in fuzzy_matches:
            if match not in results and score >= 60:
                results.append(match)
            if len(results) >= limit:
                break
        return results[:limit]
    
    def did_you_mean(self, query: str, results_count: int) -> Optional[str]:
        if results_count > 0:
            return None
        corrected, _ = self.check(query)
        if corrected.lower() != query.lower():
            return corrected
        return None
