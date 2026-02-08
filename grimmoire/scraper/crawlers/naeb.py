"""NAEB (Native American Ethnobotany Database) and PubChem scrapers."""
from typing import Generator, Optional, List, Dict

from ..base import BaseScraper, ScraperProgress
from ..sources import register_scraper


@register_scraper("NAEB Datasette")
class NAEBScraper(BaseScraper):
    """Scraper for Native American Ethnobotany Database via Datasette API."""
    
    BASE_URL = "https://naeb.louispotok.com"
    PAGE_SIZE = 100
    
    def get_table_count(self, table: str) -> int:
        url = f"{self.BASE_URL}/naeb/{table}.json"
        params = {'_size': 0}
        response = self._make_request(url, params)
        data = response.json()
        return data.get('filtered_table_rows_count', 0) or len(data.get('rows', []))
    
    def fetch_page(self, table: str, offset: int = 0) -> List[Dict]:
        url = f"{self.BASE_URL}/naeb/{table}.json"
        params = {'_size': self.PAGE_SIZE, '_offset': offset}
        response = self._make_request(url, params)
        data = response.json()
        return data.get('rows', [])
    
    def fetch_species(self) -> Generator[Dict, None, None]:
        total = self.get_table_count('species')
        self.progress.total_items = total
        offset = self.progress.current_page * self.PAGE_SIZE
        
        while offset < total:
            if self.should_stop():
                break
            rows = self.fetch_page('species', offset)
            if not rows:
                break
            for row in rows:
                yield {'table': 'species', 'data': row}
            offset += self.PAGE_SIZE
            self.progress.current_page = offset // self.PAGE_SIZE
    
    def fetch_uses(self) -> Generator[Dict, None, None]:
        total = self.get_table_count('uses')
        offset = 0
        while offset < total:
            if self.should_stop():
                break
            rows = self.fetch_page('uses', offset)
            if not rows:
                break
            for row in rows:
                yield {'table': 'uses', 'data': row}
            offset += self.PAGE_SIZE
    
    def scrape(self, resume_from: ScraperProgress = None) -> Generator[Dict, None, None]:
        if resume_from:
            self.progress = resume_from
        yield from self.fetch_species()
        yield from self.fetch_uses()
    
    def process_item(self, item: Dict) -> Optional[Dict]:
        table = item.get('table')
        data = item.get('data', {})
        
        if table == 'species':
            return {
                '_type': 'plant',
                'name': data.get('common_name') or data.get('latin_name', ''),
                'scientific_name': data.get('latin_name'),
                'family': data.get('family'),
                'common_names': [data.get('common_name')] if data.get('common_name') else [],
                'description': f"Native American medicinal plant. Family: {data.get('family', 'Unknown')}"
            }
        elif table == 'uses':
            use_description = data.get('use', '')
            if use_description:
                return {
                    '_type': 'ailment',
                    'name': use_description[:100],
                    'category': data.get('category'),
                    'description': f"Traditional use by {data.get('tribe', 'Native American')} peoples: {use_description}"
                }
        return None


@register_scraper("PubChem")
class PubChemScraper(BaseScraper):
    """Scraper for PubChem compound data."""
    
    BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rate_limit = 5
    
    def search_compounds(self, query: str, max_results: int = 100) -> List[int]:
        url = f"{self.BASE_URL}/compound/name/{query}/cids/JSON"
        try:
            response = self._make_request(url)
            data = response.json()
            return data.get('IdentifierList', {}).get('CID', [])[:max_results]
        except Exception:
            return []
    
    def get_compound_properties(self, cids: List[int]) -> List[Dict]:
        if not cids:
            return []
        cid_str = ','.join(map(str, cids[:100]))
        url = f"{self.BASE_URL}/compound/cid/{cid_str}/property/MolecularFormula,MolecularWeight,IsomericSMILES,InChIKey,IUPACName/JSON"
        try:
            response = self._make_request(url)
            data = response.json()
            return data.get('PropertyTable', {}).get('Properties', [])
        except Exception:
            return []
    
    def get_compound_synonyms(self, cid: int) -> List[str]:
        url = f"{self.BASE_URL}/compound/cid/{cid}/synonyms/JSON"
        try:
            response = self._make_request(url)
            data = response.json()
            info = data.get('InformationList', {}).get('Information', [])
            if info:
                return info[0].get('Synonym', [])[:10]
        except Exception:
            pass
        return []
    
    def scrape(self, resume_from: ScraperProgress = None) -> Generator[Dict, None, None]:
        if resume_from:
            self.progress = resume_from
        
        compounds_to_search = [
            "curcumin", "quercetin", "resveratrol", "berberine", "ginsenoside",
            "catechin", "kaempferol", "luteolin", "apigenin", "naringenin",
            "hesperidin", "rutin", "chlorogenic acid", "caffeic acid", "ferulic acid",
            "rosmarinic acid", "ursolic acid", "oleanolic acid", "betulinic acid",
            "asiaticoside", "withanolide", "artemisinin", "thymoquinone", "allicin", "capsaicin"
        ]
        
        self.progress.total_items = len(compounds_to_search)
        
        for i, compound_name in enumerate(compounds_to_search):
            if self.should_stop():
                break
            cids = self.search_compounds(compound_name, max_results=5)
            for cid in cids:
                props_list = self.get_compound_properties([cid])
                if props_list:
                    props = props_list[0]
                    synonyms = self.get_compound_synonyms(cid)
                    yield {'cid': cid, 'name': compound_name, 'properties': props, 'synonyms': synonyms}
            self.progress.processed_items = i + 1
    
    def process_item(self, item: Dict) -> Optional[Dict]:
        props = item.get('properties', {})
        return {
            '_type': 'ingredient',
            'name': props.get('IUPACName') or item.get('name', ''),
            'synonyms': item.get('synonyms', []),
            'pubchem_cid': str(item.get('cid', '')),
            'inchi_key': props.get('InChIKey'),
            'smiles': props.get('IsomericSMILES'),
            'molecular_formula': props.get('MolecularFormula'),
            'molecular_weight': props.get('MolecularWeight'),
            'description': f"Natural compound. PubChem CID: {item.get('cid')}"
        }
