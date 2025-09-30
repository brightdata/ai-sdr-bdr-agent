from crewai import Agent, Task
from crewai.tools import BaseTool
from typing import Any
from pydantic import BaseModel, Field
from .utils import validate_companies_input, safe_mcp_call, deduplicate_by_key, extract_domain_from_url

class CompanyDiscoveryInput(BaseModel):
    industry: str = Field(description="Target industry for company discovery")
    size_range: str = Field(description="Company size range (startup, small, medium, enterprise)")
    location: str = Field(default="", description="Geographic location or region")

class CompanyDiscoveryTool(BaseTool):
    name: str = "discover_companies"
    description: str = "Find companies matching ICP criteria using web scraping"
    args_schema: type[BaseModel] = CompanyDiscoveryInput
    mcp: Any = None
    
    def __init__(self, mcp_client):
        super().__init__()
        self.mcp = mcp_client
    
    def _run(self, industry: str, size_range: str, location: str = "") -> list:
        companies = []
        
        search_terms = [
            f"{industry} companies {size_range}",
            f"{industry} startups {location}",
            f"{industry} technology companies"
        ]
        
        for term in search_terms:
            results = self._search_companies(term)
            for company in results:
                enriched = self._enrich_company_data(company)
                if self._matches_icp(enriched, industry, size_range):
                    companies.append(enriched)
        
        return deduplicate_by_key(companies, lambda c: c.get('domain') or c['name'].lower())
    
    def _search_companies(self, term):
        """Search for companies using real web search through Bright Data."""
        try:
            companies = []
            
            search_queries = [
                f"{term} directory",
                f"{term} list",
                f"{term} news"
            ]
            
            for query in search_queries:
                try:
                    results = self._perform_company_search(query)
                    companies.extend(results)
                    
                    if len(companies) >= 10:
                        break
                        
                except Exception as e:
                    print(f"Error in search query '{query}': {str(e)}")
                    continue
            
            return self._filter_unique_companies(companies)
            
        except Exception as e:
            print(f"Error searching companies for '{term}': {str(e)}")
            return []
    
    def _enrich_company_data(self, company):
        linkedin_data = safe_mcp_call(self.mcp, 'scrape_company_linkedin', company['name'])
        website_data = safe_mcp_call(self.mcp, 'scrape_company_website', company.get('domain', ''))
        
        employee_count = linkedin_data.get('employee_count') or 150
        
        return {
            **company,
            'linkedin_intelligence': linkedin_data,
            'website_intelligence': website_data,
            'employee_count': employee_count,
            'icp_score': 0
        }
    
    def _matches_icp(self, company, industry, size_range):
        score = 0
        if industry.lower() in company.get('industry', '').lower():
            score += 30
        if self._check_size_range(company.get('employee_count', 0), size_range):
            score += 25
        
        if company.get('name') and company.get('domain'):
            score += 20
        
        company['icp_score'] = score
        
        return score >= 20
    
    def _check_size_range(self, count, size_range):
        ranges = {'startup': (1, 50), 'small': (51, 200), 'medium': (201, 1000)}
        min_size, max_size = ranges.get(size_range, (0, 999999))
        return min_size <= count <= max_size
    
    
    def _perform_company_search(self, query):
        """Perform company search using Bright Data MCP."""
        search_result = safe_mcp_call(self.mcp, 'search_company_news', query)
        
        if search_result and search_result.get('results'):
            return self._extract_companies_from_mcp_results(search_result['results'], query)
        else:
            print(f"No MCP results for: {query}")
            return []
    
    
    def _filter_unique_companies(self, companies):
        """Filter out duplicate companies."""
        seen_names = set()
        unique_companies = []
        
        for company in companies:
            name_key = company.get('name', '').lower()
            if name_key and name_key not in seen_names:
                seen_names.add(name_key)
                unique_companies.append(company)
        
        return unique_companies
    
    def _extract_companies_from_mcp_results(self, mcp_results, original_query):
        """Extract company information from MCP search results."""
        companies = []
        
        for result in mcp_results[:10]:
            try:
                title = result.get('title', '')
                url = result.get('url', '')
                snippet = result.get('snippet', '')
                
                company_name = self._extract_company_name_from_result(title, url)
                
                if company_name and len(company_name) > 2:
                    domain = self._extract_domain_from_url(url)
                    
                    industry = self._extract_industry_from_query(original_query)
                    
                    companies.append({
                        'name': company_name,
                        'domain': domain,
                        'industry': industry
                    })
                    
            except Exception as e:
                print(f"Error extracting company from MCP result: {str(e)}")
                continue
        
        return companies
    
    def _extract_company_name_from_result(self, title, url):
        """Extract company name from search result title or URL."""
        import re
        
        if title:
            title_clean = re.sub(r'[\|\-\—\–].*$', '', title).strip()
            
            title_clean = re.sub(r'\s+(Inc|Corp|LLC|Ltd|Solutions|Systems|Technologies|Software|Platform|Company)$', '', title_clean, flags=re.IGNORECASE)
            
            if len(title_clean) > 2 and len(title_clean) < 50:
                return title_clean
        
        if url:
            domain_parts = url.split('/')[2].split('.')
            if len(domain_parts) > 1:
                return domain_parts[0].title()
        
        return None
    
    def _extract_domain_from_url(self, url):
        """Extract domain from URL."""
        return extract_domain_from_url(url)
    
    def _extract_industry_from_query(self, query):
        """Extract industry from search query."""
        query_lower = query.lower()
        
        industry_mappings = {
            'saas': 'SaaS',
            'fintech': 'FinTech', 
            'ecommerce': 'E-commerce',
            'healthcare': 'Healthcare',
            'ai': 'AI/ML',
            'machine learning': 'AI/ML',
            'artificial intelligence': 'AI/ML'
        }
        
        for keyword, industry in industry_mappings.items():
            if keyword in query_lower:
                return industry
        
        return 'Technology'

def create_company_discovery_agent(mcp_client):
    return Agent(
        role='Company Discovery Specialist',
        goal='Find high-quality prospects matching ICP criteria',
        backstory='Expert at identifying potential customers using real-time web intelligence.',
        tools=[CompanyDiscoveryTool(mcp_client)],
        verbose=True
    )