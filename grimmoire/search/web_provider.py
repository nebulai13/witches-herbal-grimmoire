"""Web search providers for querying online traditional medicine databases."""
import time
import requests
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class SourceType(str, Enum):
    """Types of data sources."""
    COMPOUND = "compound"
    PLANT = "plant"
    AILMENT = "ailment"
    CLINICAL = "clinical"
    ETHNOBOTANY = "ethnobotany"


@dataclass
class WebSearchResult:
    """A result from a web search provider."""
    source: str
    result_type: str
    name: str
    data: Dict[str, Any]
    url: Optional[str] = None
    score: float = 1.0
    
    def to_dict(self) -> Dict:
        return {
            "source": self.source,
            "type": self.result_type,
            "name": self.name,
            "data": self.data,
            "url": self.url,
            "score": self.score
        }


class BaseWebProvider(ABC):
    """Base class for web search providers."""
    
    name: str = "Unknown"
    source_types: List[SourceType] = []
    rate_limit: float = 1.0  # requests per second
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.last_request = 0
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Grimmoire/0.1 (Traditional Medicine Research Tool)'
        })
    
    def _rate_limit_wait(self):
        """Enforce rate limiting."""
        now = time.time()
        min_interval = 1.0 / self.rate_limit
        elapsed = now - self.last_request
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self.last_request = time.time()
    
    def _get(self, url: str, params: Dict = None, headers: Dict = None, timeout: int = 30) -> requests.Response:
        """Make a rate-limited GET request."""
        self._rate_limit_wait()
        if headers:
            self.session.headers.update(headers)
        response = self.session.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        return response
    
    def _post(self, url: str, data: Any = None, json: Dict = None, headers: Dict = None, timeout: int = 30) -> requests.Response:
        """Make a rate-limited POST request."""
        self._rate_limit_wait()
        if headers:
            self.session.headers.update(headers)
        response = self.session.post(url, data=data, json=json, timeout=timeout)
        response.raise_for_status()
        return response
    
    @abstractmethod
    def search(self, query: str, max_results: int = 20) -> List[WebSearchResult]:
        """Search the provider for the given query."""
        pass
    
    def supports(self, source_type: SourceType) -> bool:
        """Check if this provider supports the given source type."""
        return source_type in self.source_types


class COCONUTProvider(BaseWebProvider):
    """COCONUT 2.0 - Collection of Open Natural Products (695K compounds)."""
    
    name = "COCONUT"
    source_types = [SourceType.COMPOUND, SourceType.PLANT]
    rate_limit = 2.0
    BASE_URL = "https://coconut.naturalproducts.net/api"
    
    def search(self, query: str, max_results: int = 20) -> List[WebSearchResult]:
        results = []
        try:
            # Search by text (name, synonyms)
            response = self._get(
                f"{self.BASE_URL}/search/simple",
                params={"query": query, "limit": max_results}
            )
            data = response.json()
            
            for item in data.get("naturalProducts", [])[:max_results]:
                results.append(WebSearchResult(
                    source=self.name,
                    result_type="compound",
                    name=item.get("name") or item.get("iupacName") or f"COCONUT-{item.get('id')}",
                    data={
                        "coconut_id": item.get("id"),
                        "smiles": item.get("smiles"),
                        "inchi_key": item.get("inchiKey"),
                        "molecular_formula": item.get("molecularFormula"),
                        "molecular_weight": item.get("molecularWeight"),
                        "organisms": item.get("organisms", []),
                        "np_likeness": item.get("npLikeness"),
                    },
                    url=f"https://coconut.naturalproducts.net/compound/{item.get('id')}"
                ))
        except Exception as e:
            # Silently handle errors, return empty results
            pass
        return results


class LOTUSProvider(BaseWebProvider):
    """LOTUS - Natural Products via Wikidata SPARQL (750K structure-organism pairs)."""
    
    name = "LOTUS"
    source_types = [SourceType.COMPOUND, SourceType.PLANT]
    rate_limit = 1.0
    SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
    
    def search(self, query: str, max_results: int = 20) -> List[WebSearchResult]:
        results = []
        sparql_query = f"""
        SELECT ?compound ?compoundLabel ?inchiKey ?smiles ?taxon ?taxonLabel WHERE {{
          ?compound wdt:P31 wd:Q11173 .  # instance of chemical compound
          ?compound rdfs:label ?label .
          FILTER(CONTAINS(LCASE(?label), LCASE("{query}")))
          OPTIONAL {{ ?compound wdt:P235 ?inchiKey . }}
          OPTIONAL {{ ?compound wdt:P233 ?smiles . }}
          OPTIONAL {{ 
            ?compound p:P703 ?statement .
            ?statement ps:P703 ?taxon .
          }}
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" . }}
        }}
        LIMIT {max_results}
        """
        
        try:
            response = self._get(
                self.SPARQL_ENDPOINT,
                params={"query": sparql_query, "format": "json"},
                headers={"Accept": "application/sparql-results+json"}
            )
            data = response.json()
            
            for binding in data.get("results", {}).get("bindings", []):
                compound_uri = binding.get("compound", {}).get("value", "")
                wikidata_id = compound_uri.split("/")[-1] if compound_uri else None
                
                results.append(WebSearchResult(
                    source=self.name,
                    result_type="compound",
                    name=binding.get("compoundLabel", {}).get("value", "Unknown"),
                    data={
                        "wikidata_id": wikidata_id,
                        "inchi_key": binding.get("inchiKey", {}).get("value"),
                        "smiles": binding.get("smiles", {}).get("value"),
                        "organism": binding.get("taxonLabel", {}).get("value"),
                        "organism_id": binding.get("taxon", {}).get("value", "").split("/")[-1],
                    },
                    url=compound_uri
                ))
        except Exception:
            pass
        return results


class ChEMBLProvider(BaseWebProvider):
    """ChEMBL - Chemical database with bioactivity data (2.4M compounds)."""
    
    name = "ChEMBL"
    source_types = [SourceType.COMPOUND]
    rate_limit = 3.0
    BASE_URL = "https://www.ebi.ac.uk/chembl/api/data"
    
    def search(self, query: str, max_results: int = 20) -> List[WebSearchResult]:
        results = []
        try:
            response = self._get(
                f"{self.BASE_URL}/molecule/search",
                params={"q": query, "limit": max_results, "format": "json"}
            )
            data = response.json()
            
            for mol in data.get("molecules", [])[:max_results]:
                props = mol.get("molecule_properties") or {}
                results.append(WebSearchResult(
                    source=self.name,
                    result_type="compound",
                    name=mol.get("pref_name") or mol.get("molecule_chembl_id"),
                    data={
                        "chembl_id": mol.get("molecule_chembl_id"),
                        "smiles": mol.get("molecule_structures", {}).get("canonical_smiles"),
                        "inchi_key": mol.get("molecule_structures", {}).get("standard_inchi_key"),
                        "molecular_formula": props.get("full_molformula"),
                        "molecular_weight": props.get("full_mwt"),
                        "alogp": props.get("alogp"),
                        "natural_product": mol.get("natural_product"),
                    },
                    url=f"https://www.ebi.ac.uk/chembl/compound_report_card/{mol.get('molecule_chembl_id')}"
                ))
        except Exception:
            pass
        return results


class ClinicalTrialsProvider(BaseWebProvider):
    """ClinicalTrials.gov - Clinical trial data for herbal/natural medicine."""
    
    name = "ClinicalTrials.gov"
    source_types = [SourceType.CLINICAL]
    rate_limit = 3.0
    BASE_URL = "https://clinicaltrials.gov/api/v2/studies"
    
    def search(self, query: str, max_results: int = 20) -> List[WebSearchResult]:
        results = []
        # Enhance query for herbal/natural medicine context
        enhanced_query = f"{query} AND (herbal OR botanical OR plant OR natural OR traditional medicine)"
        
        try:
            response = self._get(
                self.BASE_URL,
                params={
                    "query.term": enhanced_query,
                    "pageSize": max_results,
                    "format": "json"
                }
            )
            data = response.json()
            
            for study in data.get("studies", [])[:max_results]:
                protocol = study.get("protocolSection", {})
                id_module = protocol.get("identificationModule", {})
                status_module = protocol.get("statusModule", {})
                desc_module = protocol.get("descriptionModule", {})
                
                nct_id = id_module.get("nctId")
                results.append(WebSearchResult(
                    source=self.name,
                    result_type="clinical_trial",
                    name=id_module.get("briefTitle", "Unknown Trial"),
                    data={
                        "nct_id": nct_id,
                        "official_title": id_module.get("officialTitle"),
                        "status": status_module.get("overallStatus"),
                        "phase": status_module.get("studyType"),
                        "brief_summary": desc_module.get("briefSummary"),
                        "conditions": protocol.get("conditionsModule", {}).get("conditions", []),
                        "interventions": [
                            i.get("name") for i in 
                            protocol.get("armsInterventionsModule", {}).get("interventions", [])
                        ],
                    },
                    url=f"https://clinicaltrials.gov/study/{nct_id}" if nct_id else None
                ))
        except Exception:
            pass
        return results


class DrDukeProvider(BaseWebProvider):
    """Dr. Duke's Phytochemical and Ethnobotanical Databases (USDA)."""
    
    name = "Dr. Duke's"
    source_types = [SourceType.PLANT, SourceType.COMPOUND, SourceType.ETHNOBOTANY]
    rate_limit = 1.0
    BASE_URL = "https://phytochem.nal.usda.gov/phytochem/search"
    
    def search(self, query: str, max_results: int = 20) -> List[WebSearchResult]:
        results = []
        try:
            # Search plants
            response = self._get(
                f"{self.BASE_URL}/plants",
                params={"q": query, "max": max_results}
            )
            # Parse response (may be HTML or JSON depending on endpoint)
            # This is a simplified version - actual implementation may need HTML parsing
            data = response.json() if 'application/json' in response.headers.get('content-type', '') else {}
            
            for item in data.get("plants", [])[:max_results]:
                results.append(WebSearchResult(
                    source=self.name,
                    result_type="plant",
                    name=item.get("commonName") or item.get("scientificName"),
                    data={
                        "scientific_name": item.get("scientificName"),
                        "common_name": item.get("commonName"),
                        "family": item.get("family"),
                        "chemicals": item.get("chemicals", []),
                        "activities": item.get("activities", []),
                    },
                    url=f"https://phytochem.nal.usda.gov/phytochem/plants/show/{item.get('id')}"
                ))
        except Exception:
            pass
        return results


class HERB2Provider(BaseWebProvider):
    """HERB 2.0 - High-throughput Experiment & Reference-guided Database for TCM."""
    
    name = "HERB 2.0"
    source_types = [SourceType.PLANT, SourceType.COMPOUND]
    rate_limit = 1.0
    BASE_URL = "http://herb.ac.cn/api"
    
    def search(self, query: str, max_results: int = 20) -> List[WebSearchResult]:
        results = []
        try:
            # Search herbs
            response = self._get(
                f"{self.BASE_URL}/search",
                params={"keyword": query, "type": "herb", "limit": max_results}
            )
            data = response.json()
            
            for herb in data.get("data", {}).get("herbs", [])[:max_results]:
                results.append(WebSearchResult(
                    source=self.name,
                    result_type="plant",
                    name=herb.get("herb_cn_name") or herb.get("herb_en_name"),
                    data={
                        "herb_id": herb.get("herb_id"),
                        "chinese_name": herb.get("herb_cn_name"),
                        "english_name": herb.get("herb_en_name"),
                        "latin_name": herb.get("herb_latin_name"),
                        "ingredients_count": herb.get("ingredient_count"),
                        "targets_count": herb.get("target_count"),
                    },
                    url=f"http://herb.ac.cn/Detail/?v={herb.get('herb_id')}&type=herb"
                ))
            
            # Also search ingredients
            response = self._get(
                f"{self.BASE_URL}/search",
                params={"keyword": query, "type": "ingredient", "limit": max_results}
            )
            data = response.json()
            
            for ing in data.get("data", {}).get("ingredients", [])[:max_results]:
                results.append(WebSearchResult(
                    source=self.name,
                    result_type="compound",
                    name=ing.get("ingredient_name"),
                    data={
                        "ingredient_id": ing.get("ingredient_id"),
                        "cas": ing.get("cas"),
                        "pubchem_cid": ing.get("pubchem_cid"),
                        "smiles": ing.get("smiles"),
                    },
                    url=f"http://herb.ac.cn/Detail/?v={ing.get('ingredient_id')}&type=ingredient"
                ))
        except Exception:
            pass
        return results[:max_results]


class TCMSPProvider(BaseWebProvider):
    """TCMSP - Traditional Chinese Medicine Systems Pharmacology Database."""
    
    name = "TCMSP"
    source_types = [SourceType.PLANT, SourceType.COMPOUND]
    rate_limit = 1.0
    BASE_URL = "https://tcmsp-e.com/api"
    
    def search(self, query: str, max_results: int = 20) -> List[WebSearchResult]:
        results = []
        try:
            # Search herbs
            response = self._get(
                f"{self.BASE_URL}/herbs",
                params={"keyword": query, "limit": max_results}
            )
            data = response.json()
            
            for herb in data.get("herbs", [])[:max_results]:
                results.append(WebSearchResult(
                    source=self.name,
                    result_type="plant",
                    name=herb.get("Herb_en_name") or herb.get("Herb_cn_name"),
                    data={
                        "tcmsp_id": herb.get("TCMSP_id"),
                        "chinese_name": herb.get("Herb_cn_name"),
                        "english_name": herb.get("Herb_en_name"),
                        "pinyin": herb.get("Herb_pinyin_name"),
                    },
                    url=f"https://tcmsp-e.com/tcmspsearch.php?qr={herb.get('Herb_en_name')}"
                ))
        except Exception:
            pass
        return results


class OSADHIProvider(BaseWebProvider):
    """OSADHI - Online Structural & Analytics Database for Herbs of India."""
    
    name = "OSADHI"
    source_types = [SourceType.COMPOUND, SourceType.PLANT]
    rate_limit = 1.0
    BASE_URL = "https://neist.res.in/osadhi/api"
    
    def search(self, query: str, max_results: int = 20) -> List[WebSearchResult]:
        results = []
        try:
            response = self._get(
                f"{self.BASE_URL}/search",
                params={"q": query, "limit": max_results}
            )
            data = response.json()
            
            for compound in data.get("compounds", [])[:max_results]:
                results.append(WebSearchResult(
                    source=self.name,
                    result_type="compound",
                    name=compound.get("name"),
                    data={
                        "osadhi_id": compound.get("id"),
                        "smiles": compound.get("smiles"),
                        "inchi_key": compound.get("inchi_key"),
                        "plant_source": compound.get("plant_source"),
                        "therapeutic_use": compound.get("therapeutic_use"),
                        "admet": compound.get("admet_properties"),
                    },
                    url=f"https://neist.res.in/osadhi/compound/{compound.get('id')}"
                ))
        except Exception:
            pass
        return results


class IMPPATProvider(BaseWebProvider):
    """IMPPAT 2.0 - Indian Medicinal Plants, Phytochemistry & Therapeutics."""
    
    name = "IMPPAT"
    source_types = [SourceType.PLANT, SourceType.COMPOUND]
    rate_limit = 1.0
    BASE_URL = "https://cb.imsc.res.in/imppat/api"
    
    def search(self, query: str, max_results: int = 20) -> List[WebSearchResult]:
        results = []
        try:
            # Search plants
            response = self._get(
                f"{self.BASE_URL}/plants/search",
                params={"q": query, "limit": max_results}
            )
            data = response.json()
            
            for plant in data.get("plants", [])[:max_results]:
                results.append(WebSearchResult(
                    source=self.name,
                    result_type="plant",
                    name=plant.get("common_name") or plant.get("botanical_name"),
                    data={
                        "imppat_id": plant.get("id"),
                        "botanical_name": plant.get("botanical_name"),
                        "common_name": plant.get("common_name"),
                        "family": plant.get("family"),
                        "therapeutic_uses": plant.get("therapeutic_uses", []),
                        "phytochemicals_count": plant.get("phytochemicals_count"),
                    },
                    url=f"https://cb.imsc.res.in/imppat/plant/{plant.get('id')}"
                ))
        except Exception:
            pass
        return results


class MSKHerbsProvider(BaseWebProvider):
    """Memorial Sloan Kettering - About Herbs Database."""
    
    name = "MSK About Herbs"
    source_types = [SourceType.PLANT, SourceType.COMPOUND]
    rate_limit = 0.5  # Be gentle with scraping
    BASE_URL = "https://www.mskcc.org/cancer-care/diagnosis-treatment/symptom-management/integrative-medicine/herbs"
    SEARCH_URL = "https://www.mskcc.org/api/herbs/search"
    
    def search(self, query: str, max_results: int = 20) -> List[WebSearchResult]:
        results = []
        try:
            # Try API first
            response = self._get(
                self.SEARCH_URL,
                params={"q": query}
            )
            data = response.json()
            
            for herb in data.get("results", [])[:max_results]:
                results.append(WebSearchResult(
                    source=self.name,
                    result_type="plant",
                    name=herb.get("title"),
                    data={
                        "scientific_name": herb.get("scientific_name"),
                        "common_names": herb.get("common_names", []),
                        "clinical_summary": herb.get("clinical_summary"),
                        "mechanism": herb.get("mechanism_of_action"),
                        "adverse_effects": herb.get("adverse_effects"),
                        "interactions": herb.get("interactions"),
                    },
                    url=herb.get("url")
                ))
        except Exception:
            pass
        return results


class NAEBWebProvider(BaseWebProvider):
    """NAEB - Native American Ethnobotany Database (Datasette API)."""
    
    name = "NAEB"
    source_types = [SourceType.PLANT, SourceType.ETHNOBOTANY]
    rate_limit = 2.0
    BASE_URL = "https://naeb.louispotok.com/naeb"
    
    def search(self, query: str, max_results: int = 20) -> List[WebSearchResult]:
        results = []
        try:
            # Search species
            response = self._get(
                f"{self.BASE_URL}/species.json",
                params={"_search": query, "_size": max_results}
            )
            data = response.json()
            
            for row in data.get("rows", [])[:max_results]:
                results.append(WebSearchResult(
                    source=self.name,
                    result_type="plant",
                    name=row.get("common_name") or row.get("latin_name"),
                    data={
                        "species_id": row.get("id"),
                        "latin_name": row.get("latin_name"),
                        "common_name": row.get("common_name"),
                        "family": row.get("family"),
                    },
                    url=f"https://naeb.louispotok.com/naeb/species/{row.get('id')}"
                ))
            
            # Also search uses
            response = self._get(
                f"{self.BASE_URL}/uses.json",
                params={"_search": query, "_size": max_results}
            )
            data = response.json()
            
            for row in data.get("rows", [])[:max_results]:
                results.append(WebSearchResult(
                    source=self.name,
                    result_type="ethnobotany",
                    name=row.get("use", "Unknown use")[:80],
                    data={
                        "use_id": row.get("id"),
                        "use": row.get("use"),
                        "category": row.get("use_category"),
                        "tribe": row.get("tribe"),
                        "species_id": row.get("species_id"),
                    },
                    url=f"https://naeb.louispotok.com/naeb/uses/{row.get('id')}"
                ))
        except Exception:
            pass
        return results[:max_results]


# Provider registry
_PROVIDERS: Dict[str, type] = {
    "coconut": COCONUTProvider,
    "lotus": LOTUSProvider,
    "chembl": ChEMBLProvider,
    "clinicaltrials": ClinicalTrialsProvider,
    "dukes": DrDukeProvider,
    "herb2": HERB2Provider,
    "tcmsp": TCMSPProvider,
    "osadhi": OSADHIProvider,
    "imppat": IMPPATProvider,
    "msk": MSKHerbsProvider,
    "naeb": NAEBWebProvider,
}


def get_provider(name: str, config: Dict = None) -> Optional[BaseWebProvider]:
    """Get a provider instance by name."""
    provider_class = _PROVIDERS.get(name.lower())
    if provider_class:
        return provider_class(config)
    return None


def list_providers() -> List[str]:
    """List all available provider names."""
    return list(_PROVIDERS.keys())


def get_providers_for_type(source_type: SourceType, config: Dict = None) -> List[BaseWebProvider]:
    """Get all providers that support a given source type."""
    providers = []
    for name, cls in _PROVIDERS.items():
        provider = cls(config)
        if provider.supports(source_type):
            providers.append(provider)
    return providers


class WebSearchAggregator:
    """Aggregates results from multiple web search providers."""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.enabled_providers = self.config.get("providers", list(_PROVIDERS.keys()))
    
    def search(self, query: str, source_types: List[SourceType] = None, 
               max_results: int = 20, max_per_provider: int = 10) -> List[WebSearchResult]:
        """Search across all enabled providers."""
        all_results = []
        
        for provider_name in self.enabled_providers:
            provider = get_provider(provider_name, self.config)
            if not provider:
                continue
            
            # Filter by source type if specified
            if source_types:
                if not any(provider.supports(st) for st in source_types):
                    continue
            
            try:
                results = provider.search(query, max_per_provider)
                all_results.extend(results)
            except Exception:
                # Provider failed, continue with others
                continue
        
        # Sort by score (if providers set different scores) and limit
        all_results.sort(key=lambda r: r.score, reverse=True)
        return all_results[:max_results]
    
    def search_compounds(self, query: str, max_results: int = 20) -> List[WebSearchResult]:
        """Search for compounds/ingredients only."""
        return self.search(query, [SourceType.COMPOUND], max_results)
    
    def search_plants(self, query: str, max_results: int = 20) -> List[WebSearchResult]:
        """Search for plants only."""
        return self.search(query, [SourceType.PLANT], max_results)
    
    def search_clinical(self, query: str, max_results: int = 20) -> List[WebSearchResult]:
        """Search for clinical trial data only."""
        return self.search(query, [SourceType.CLINICAL], max_results)
