from crewai import Agent, Task
from crewai.tools import BaseTool
from datetime import datetime
from typing import List
from pydantic import BaseModel, Field
import requests
import os
from .utils import validate_companies_input

class LeadScoringInput(BaseModel):
    companies: List[dict] = Field(description="List of companies to score")

class LeadScoringTool(BaseTool):
    name: str = "score_leads"
    description: str = "Score leads based on multiple intelligence factors"
    args_schema: type[BaseModel] = LeadScoringInput
    
    def _run(self, companies) -> list:
        companies = validate_companies_input(companies)
        if not companies:
            return []
        
        for company in companies:
                
            score_breakdown = self._calculate_lead_score(company)
            company['lead_score'] = score_breakdown['total_score']
            company['score_breakdown'] = score_breakdown
            company['lead_grade'] = self._assign_grade(score_breakdown['total_score'])
        
        return sorted(companies, key=lambda x: x.get('lead_score', 0), reverse=True)
    
    def _calculate_lead_score(self, company):
        breakdown = {
            'icp_score': min(company.get('icp_score', 0) * 0.3, 25),
            'trigger_score': min(company.get('trigger_score', 0) * 2, 30),
            'contact_score': min(company.get('contact_score', 0) * 0.2, 20),
            'timing_score': self._assess_timing(company),
            'company_health': self._assess_health(company)
        }
        breakdown['total_score'] = sum(breakdown.values())
        return breakdown
    
    def _assess_timing(self, company):
        triggers = company.get('trigger_events', [])
        if not triggers:
            return 0
        
        recent_triggers = sum(1 for t in triggers if 'high' in t.get('severity', ''))
        return min(recent_triggers * 8, 15)
    
    def _assess_health(self, company):
        score = 0
        if company.get('trigger_events'):
            score += 5
        if company.get('employee_count', 0) > 50:
            score += 5
        return score
    
    def _assign_grade(self, score):
        if score >= 80: return 'A'
        elif score >= 65: return 'B' 
        elif score >= 50: return 'C'
        else: return 'D'

class CRMIntegrationInput(BaseModel):
    companies: List[dict] = Field(description="List of companies to export to CRM")
    min_grade: str = Field(default="B", description="Minimum lead grade to export (A, B, C, D)")

class CRMIntegrationTool(BaseTool):
    name: str = "crm_integration"
    description: str = "Export qualified leads to HubSpot CRM"
    args_schema: type[BaseModel] = CRMIntegrationInput
    
    def _run(self, companies, min_grade='B') -> dict:
        companies = validate_companies_input(companies)
        if not companies:
            return {"message": "No companies provided for CRM export", "success": 0, "errors": 0}
        
        qualified = [c for c in companies if isinstance(c, dict) and c.get('lead_grade', 'D') in ['A', 'B']]
        
        if not os.getenv("HUBSPOT_API_KEY"):
            return {"error": "HubSpot API key not configured", "success": 0, "errors": 0}
        
        results = {"success": 0, "errors": 0, "details": []}
        
        for company in qualified:
            for contact in company.get('contacts', []):
                if not isinstance(contact, dict):
                    continue
                    
                result = self._create_hubspot_contact(contact, company)
                if result.get('success'):
                    results['success'] += 1
                else:
                    results['errors'] += 1
                results['details'].append(result)
        
        return results
    
    def _create_hubspot_contact(self, contact, company):
        api_key = os.getenv("HUBSPOT_API_KEY")
        if not api_key:
            return {"success": False, "error": "HubSpot API key not configured"}
            
        url = "https://api.hubapi.com/crm/v3/objects/contacts"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        trigger_summary = "; ".join([
            f"{t.get('type', '')}: {t.get('description', '')}" 
            for t in company.get('trigger_events', [])
        ])
        
        email = contact.get('email', '').strip()
        if not email:
            return {"success": False, "error": "Contact email is required", "contact": contact.get('first_name', 'Unknown')}
        
        properties = {
            "email": email,
            "firstname": contact.get('first_name', ''),
            "lastname": contact.get('last_name', ''),
            "jobtitle": contact.get('title', ''),
            "company": company.get('name', ''),
            "website": f"https://{company.get('domain', '')}" if company.get('domain') else "",
            "hs_lead_status": "NEW",
            "lifecyclestage": "lead"
        }
        
        if company.get('lead_score'):
            properties["lead_score"] = str(company.get('lead_score', 0))
        if company.get('lead_grade'):
            properties["lead_grade"] = company.get('lead_grade', 'D')
        if trigger_summary:
            properties["trigger_events"] = trigger_summary[:1000]
        if contact.get('confidence_score'):
            properties["contact_confidence"] = str(contact.get('confidence_score', 0))
        
        properties["ai_discovery_date"] = datetime.now().isoformat()
        
        try:
            response = requests.post(url, json={"properties": properties}, headers=headers, timeout=30)
            
            if response.status_code == 201:
                return {
                    "success": True,
                    "contact": contact.get('first_name', ''),
                    "company": company.get('name', ''),
                    "hubspot_id": response.json().get('id')
                }
            elif response.status_code == 409:
                existing_contact = response.json()
                return {
                    "success": True,
                    "contact": contact.get('first_name', ''),
                    "company": company.get('name', ''),
                    "hubspot_id": existing_contact.get('id'),
                    "note": "Contact already exists"
                }
            else:
                error_detail = response.text if response.text else f"HTTP {response.status_code}"
                return {
                    "success": False,
                    "contact": contact.get('first_name', ''),
                    "company": company.get('name', ''),
                    "error": f"API Error: {error_detail}"
                }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "contact": contact.get('first_name', ''),
                "company": company.get('name', ''),
                "error": f"Network error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "contact": contact.get('first_name', ''),
                "company": company.get('name', ''),
                "error": f"Unexpected error: {str(e)}"
            }

def create_pipeline_manager_agent():
    return Agent(
        role='Pipeline Manager',
        goal='Score leads and manage CRM integration for qualified prospects',
        backstory='Expert at evaluating prospect quality and managing sales pipeline.',
        tools=[LeadScoringTool(), CRMIntegrationTool()],
        verbose=True
    )