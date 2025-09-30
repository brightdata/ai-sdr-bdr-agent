"""
Shared utility functions for all agent modules.
"""
from typing import List, Dict, Any
import re


def validate_companies_input(companies: Any) -> List[Dict]:
    """Validate and normalize companies input across all agents."""
    if isinstance(companies, dict) and 'companies' in companies:
        companies = companies['companies']
    
    if not isinstance(companies, list):
        print(f"Warning: Expected list of companies, got {type(companies)}")
        return []
    
    if not companies:
        print("No companies provided")
        return []
    
    valid_companies = []
    for company in companies:
        if isinstance(company, dict):
            valid_companies.append(company)
        else:
            print(f"Warning: Expected company dict, got {type(company)}")
    
    return valid_companies


def safe_mcp_call(mcp_client, method_name: str, *args, **kwargs) -> Dict:
    """Safely call MCP methods with consistent error handling."""
    try:
        method = getattr(mcp_client, method_name)
        result = method(*args, **kwargs)
        return result if result and not result.get('error') else {}
    except Exception as e:
        print(f"Error calling MCP {method_name}: {str(e)}")
        return {}


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def deduplicate_by_key(items: List[Dict], key_func) -> List[Dict]:
    """Remove duplicates from list of dicts using a key function."""
    seen = set()
    unique_items = []
    
    for item in items:
        key = key_func(item)
        if key and key not in seen:
            seen.add(key)
            unique_items.append(item)
    
    return unique_items


def extract_domain_from_url(url: str) -> str:
    """Extract domain from URL with fallback parsing."""
    if not url:
        return ""
    
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc
    except:
        if '//' in url:
            return url.split('//')[1].split('/')[0]
        return ""