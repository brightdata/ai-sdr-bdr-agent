"""
AI BDR/SDR Agent Package

This package contains specialized AI agents for business development and sales:
- Company Discovery: Find potential customers matching ICP criteria
- Contact Research: Identify decision-makers and their contact information  
- Message Generation: Create personalized outreach messages
- Pipeline Manager: Score leads and manage CRM integration
- Trigger Detection: Identify buying signals and optimal timing
"""

from .company_discovery import create_company_discovery_agent
from .contact_research import create_contact_research_agent
from .message_generation import create_message_generation_agent
from .pipeline_manager import create_pipeline_manager_agent
from .trigger_detection import create_trigger_detection_agent

__all__ = [
    'create_company_discovery_agent',
    'create_contact_research_agent', 
    'create_message_generation_agent',
    'create_pipeline_manager_agent',
    'create_trigger_detection_agent'
]