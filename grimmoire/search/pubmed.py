"""PubMed integration via NCBI E-utilities."""
import time
import requests
from typing import Optional, List, Dict
from xml.etree import ElementTree


class PubMedClient:
    """Client for searching PubMed via NCBI E-utilities."""
    
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    def __init__(self, api_key: str = None, email: str = None):
        self.api_key = api_key
        self.email = email
        self.rate_limit = 10 if api_key else 3
        self.last_request = 0
    
    def _rate_limit(self):
        now = time.time()
        min_interval = 1.0 / self.rate_limit
        elapsed = now - self.last_request
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self.last_request = time.time()
    
    def _make_request(self, endpoint: str, params: dict) -> requests.Response:
        self._rate_limit()
        if self.api_key:
            params['api_key'] = self.api_key
        if self.email:
            params['email'] = self.email
        response = requests.get(f"{self.BASE_URL}/{endpoint}", params=params, timeout=30)
        response.raise_for_status()
        return response
    
    def search(self, query: str, max_results: int = 20, retstart: int = 0) -> Dict:
        """Search PubMed and return PMIDs."""
        params = {
            'db': 'pubmed', 'term': query, 'retmax': max_results,
            'retstart': retstart, 'retmode': 'json', 'usehistory': 'y'
        }
        response = self._make_request('esearch.fcgi', params)
        data = response.json()
        result = data.get('esearchresult', {})
        return {
            'count': int(result.get('count', 0)),
            'ids': result.get('idlist', []),
            'web_env': result.get('webenv'),
            'query_key': result.get('querykey')
        }
    
    def fetch_summaries(self, pmids: List[str]) -> List[Dict]:
        """Fetch article summaries for given PMIDs."""
        if not pmids:
            return []
        params = {'db': 'pubmed', 'id': ','.join(pmids), 'retmode': 'json'}
        response = self._make_request('esummary.fcgi', params)
        data = response.json()
        
        results = []
        result_data = data.get('result', {})
        for pmid in pmids:
            if pmid in result_data:
                article = result_data[pmid]
                results.append({
                    'pmid': pmid,
                    'title': article.get('title', ''),
                    'authors': [a.get('name', '') for a in article.get('authors', [])],
                    'source': article.get('source', ''),
                    'pubdate': article.get('pubdate', ''),
                    'doi': self._extract_doi(article),
                    'abstract': ''
                })
        return results
    
    def fetch_abstracts(self, pmids: List[str]) -> Dict[str, str]:
        """Fetch abstracts for given PMIDs."""
        if not pmids:
            return {}
        params = {'db': 'pubmed', 'id': ','.join(pmids), 'rettype': 'abstract', 'retmode': 'xml'}
        response = self._make_request('efetch.fcgi', params)
        
        abstracts = {}
        try:
            root = ElementTree.fromstring(response.content)
            for article in root.findall('.//PubmedArticle'):
                pmid_elem = article.find('.//PMID')
                abstract_elem = article.find('.//AbstractText')
                if pmid_elem is not None and abstract_elem is not None:
                    abstracts[pmid_elem.text] = abstract_elem.text or ''
        except ElementTree.ParseError:
            pass
        return abstracts
    
    def _extract_doi(self, article: Dict) -> Optional[str]:
        for id_item in article.get('articleids', []):
            if id_item.get('idtype') == 'doi':
                return id_item.get('value')
        return None
    
    def search_herbs(self, herb_name: str, max_results: int = 20) -> List[Dict]:
        """Search for research on a specific herb."""
        query = f'"{herb_name}"[Title/Abstract] AND ("Plants, Medicinal"[MeSH] OR "Phytotherapy"[MeSH] OR "Herbal Medicine"[MeSH])'
        search_result = self.search(query, max_results)
        if not search_result['ids']:
            search_result = self.search(f'"{herb_name}" herb OR medicinal', max_results)
        
        summaries = self.fetch_summaries(search_result['ids'])
        if summaries:
            abstracts = self.fetch_abstracts(search_result['ids'])
            for summary in summaries:
                summary['abstract'] = abstracts.get(summary['pmid'], '')
        return summaries
    
    def search_ailment_treatment(self, ailment: str, treatment: str = None, max_results: int = 20) -> List[Dict]:
        """Search for treatments of an ailment."""
        if treatment:
            query = f'"{ailment}"[Title/Abstract] AND "{treatment}"[Title/Abstract] AND ("Phytotherapy"[MeSH] OR "Plant Extracts"[MeSH])'
        else:
            query = f'"{ailment}"[Title/Abstract] AND ("Phytotherapy"[MeSH] OR "Plant Extracts"[MeSH] OR "Herbal Medicine"[MeSH])'
        
        search_result = self.search(query, max_results)
        summaries = self.fetch_summaries(search_result['ids'])
        if summaries:
            abstracts = self.fetch_abstracts(search_result['ids'])
            for summary in summaries:
                summary['abstract'] = abstracts.get(summary['pmid'], '')
        return summaries
    
    def search_compound(self, compound_name: str, max_results: int = 20) -> List[Dict]:
        """Search for research on a specific compound."""
        query = f'"{compound_name}"[Title/Abstract] AND ("Phytochemicals"[MeSH] OR "Plant Extracts"[MeSH] OR "Natural Products")'
        search_result = self.search(query, max_results)
        summaries = self.fetch_summaries(search_result['ids'])
        if summaries:
            abstracts = self.fetch_abstracts(search_result['ids'])
            for summary in summaries:
                summary['abstract'] = abstracts.get(summary['pmid'], '')
        return summaries
