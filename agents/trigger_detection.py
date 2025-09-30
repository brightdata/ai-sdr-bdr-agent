from crewai import Agent, Task
from crewai.tools import BaseTool
from datetime import datetime, timedelta
from typing import Any, List
from pydantic import BaseModel, Field
from .utils import validate_companies_input, safe_mcp_call

class TriggerDetectionInput(BaseModel):
    companies: List[dict] = Field(description="List of companies to analyze for trigger events")

class TriggerDetectionTool(BaseTool):
    name: str = "detect_triggers"
    description: str = "Find hiring signals, funding news, leadership changes"
    args_schema: type[BaseModel] = TriggerDetectionInput
    mcp: Any = None
    
    def __init__(self, mcp_client):
        super().__init__()
        self.mcp = mcp_client
    
    def _run(self, companies) -> list:
        companies = validate_companies_input(companies)
        if not companies:
            return []
        
        for company in companies:
                
            triggers = []
            
            hiring_signals = self._detect_hiring_triggers(company)
            triggers.extend(hiring_signals)
            
            funding_signals = self._detect_funding_triggers(company)
            triggers.extend(funding_signals)
            
            leadership_signals = self._detect_leadership_triggers(company)
            triggers.extend(leadership_signals)
            
            expansion_signals = self._detect_expansion_triggers(company)
            triggers.extend(expansion_signals)
            
            company['trigger_events'] = triggers
            company['trigger_score'] = self._calculate_trigger_score(triggers)
        
        return sorted(companies, key=lambda x: x.get('trigger_score', 0), reverse=True)
    
    def _detect_hiring_triggers(self, company):
        """Detect hiring triggers using LinkedIn data."""
        linkedin_data = safe_mcp_call(self.mcp, 'scrape_company_linkedin', company['name'])
        triggers = []
        
        if linkedin_data:
            hiring_posts = linkedin_data.get('hiring_posts', [])
            recent_activity = linkedin_data.get('recent_activity', [])
            
            if hiring_posts:
                triggers.append({
                    'type': 'hiring_spike',
                    'severity': 'high',
                    'description': f"Active hiring detected at {company['name']} - {len(hiring_posts)} open positions",
                    'date_detected': datetime.now().isoformat(),
                    'source': 'linkedin_api'
                })
            
            if recent_activity:
                triggers.append({
                    'type': 'company_activity',
                    'severity': 'medium',
                    'description': f"Increased LinkedIn activity at {company['name']}",
                    'date_detected': datetime.now().isoformat(),
                    'source': 'linkedin_api'
                })
        
        return triggers
    
    
    def _detect_funding_triggers(self, company):
        """Detect funding triggers using news search."""
        funding_data = safe_mcp_call(self.mcp, 'search_funding_news', company['name'])
        triggers = []
        
        if funding_data and funding_data.get('results'):
            triggers.append({
                'type': 'funding_round',
                'severity': 'high',
                'description': f"Recent funding activity detected at {company['name']}",
                'date_detected': datetime.now().isoformat(),
                'source': 'news_search'
            })
        
        return triggers
    
    
    def _detect_leadership_triggers(self, company):
        """Detect leadership changes using news search."""
        return self._detect_keyword_triggers(
            company, 'leadership_change', 'medium',
            ['ceo', 'cto', 'vp', 'hired', 'joins', 'appointed'],
            f"Leadership changes detected at {company['name']}"
        )
    
    def _detect_expansion_triggers(self, company):
        """Detect business expansion using news search."""
        return self._detect_keyword_triggers(
            company, 'expansion', 'medium',
            ['expansion', 'new office', 'opening', 'market'],
            f"Business expansion detected at {company['name']}"
        )
    
    def _detect_keyword_triggers(self, company, trigger_type, severity, keywords, description):
        """Generic method to detect triggers based on keywords in news."""
        news_data = safe_mcp_call(self.mcp, 'search_company_news', company['name'])
        triggers = []
        
        if news_data and news_data.get('results'):
            for result in news_data['results']:
                if any(keyword in str(result).lower() for keyword in keywords):
                    triggers.append({
                        'type': trigger_type,
                        'severity': severity,
                        'description': description,
                        'date_detected': datetime.now().isoformat(),
                        'source': 'news_search'
                    })
                    break
        
        return triggers
    
    def _calculate_trigger_score(self, triggers):
        severity_weights = {'high': 15, 'medium': 10, 'low': 5}
        return sum(severity_weights.get(t.get('severity', 'low'), 5) for t in triggers)

def create_trigger_detection_agent(mcp_client):
    return Agent(
        role='Trigger Event Analyst',
        goal='Identify buying signals and optimal timing for outreach',
        backstory='Expert at detecting business events that indicate readiness to buy.',
        tools=[TriggerDetectionTool(mcp_client)],
        verbose=True
    )
    