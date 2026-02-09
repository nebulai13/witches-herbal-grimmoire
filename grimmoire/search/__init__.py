"""Search module"""
from .engine import SearchEngine
from .spellcheck import SpellChecker
from .web_provider import (
    WebSearchAggregator, WebSearchResult, BaseWebProvider,
    get_provider, list_providers, get_providers_for_type, SourceType
)
