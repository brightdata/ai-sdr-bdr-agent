import os
import json
import streamlit as st
from dotenv import load_dotenv
from mcp import StdioServerParameters

from mcpadapt.core import MCPAdapt
from mcpadapt.crewai_adapter import CrewAIAdapter

load_dotenv()

class BrightDataMCP:
    def __init__(self):
        """Initialize BrightData client with MCP integration."""
        self.server_params = StdioServerParameters(
            command="npx",
            args=["@brightdata/mcp"],
            env={
                "API_TOKEN": os.getenv("BRIGHT_DATA_API_TOKEN"),
                "WEB_UNLOCKER_ZONE": os.getenv("WEB_UNLOCKER_ZONE", "mcp_unlocker"),
                "BROWSER_ZONE": os.getenv("BROWSER_ZONE", "scraping_browser1"),
            },
        )
        print("✅ BrightData MCP client initialized")
    
    def scrape_company_linkedin(self, company_name):
        """Scrape LinkedIn for hiring activity and posts using Bright Data MCP."""
        try:
            query = f"{company_name} LinkedIn hiring jobs careers"
            search_result = self._mcp_search(query)
            
            if search_result and search_result.get('results'):
                linkedin_url = f"https://linkedin.com/company/{company_name.lower().replace(' ', '-').replace('systems', '').replace('solutions', '').replace('corp', '').strip('-')}"
                return self._parse_linkedin_search_results(search_result['results'], linkedin_url)
            else:
                return {"error": "No LinkedIn data found", "source": "brightdata_mcp"}
                
        except Exception as e:
            print(f"Error scraping LinkedIn for {company_name}: {str(e)}")
            return {"error": str(e), "source": "brightdata_mcp"}
    
    def scrape_company_website(self, domain):
        """Extract company info from website using Bright Data MCP."""
        if not domain:
            return {"error": "No domain provided"}
            
        try:
            query = f"site:{domain} about company technology"
            search_result = self._mcp_search(query)
            
            if search_result and search_result.get('results'):
                url = f"https://{domain}"
                return self._parse_website_results(search_result['results'], url)
            else:
                return {"error": "No website data found", "source": "brightdata_mcp"}
                
        except Exception as e:
            print(f"Error scraping website {domain}: {str(e)}")
            return {"error": str(e), "source": "brightdata_mcp"}
    
    def search_funding_news(self, company_name):
        """Search for funding announcements using MCP search."""
        try:
            query = f'{company_name} funding investment raised Series seed'
            search_result = self._mcp_search(query)
            
            if search_result and search_result.get('results'):
                funding_results = self._filter_funding_results(search_result['results'])
                return {
                    "query": query,
                    "results": funding_results,
                    "source": "brightdata_mcp"
                }
            else:
                return {"query": query, "results": [], "source": "brightdata_mcp"}
                
        except Exception as e:
            print(f"Error searching funding news for {company_name}: {str(e)}")
            return {"error": str(e), "source": "brightdata_mcp"}
    
    def search_company_news(self, company_name):
        """Search for recent company news using MCP search."""
        try:
            query = f'{company_name} news press release announcement CEO hiring expansion'
            search_result = self._mcp_search(query)
            
            if search_result and search_result.get('results'):
                return {
                    "query": query,
                    "results": search_result['results'][:5],
                    "source": "brightdata_mcp"
                }
            else:
                return {"query": query, "results": [], "source": "brightdata_mcp"}
                
        except Exception as e:
            print(f"Error searching company news for {company_name}: {str(e)}")
            return {"error": str(e), "source": "brightdata_mcp"}
    
    def _mcp_search(self, query, num_results=10):
        """Execute search using MCP tools - based on your example."""
        with MCPAdapt(self.server_params, CrewAIAdapter()) as mcp_tools:
            try:
                if not mcp_tools:
                    print("⚠️ No MCP tools available")
                    return {'results': []}
                
                for tool in mcp_tools:
                    try:
                        tool_name = getattr(tool, 'name', str(tool))
                        print(f"🔍 Trying MCP tool: {tool_name}")
                        
                        if 'search_engine' in tool_name and 'batch' not in tool_name:
                            try:
                                if hasattr(tool, '_run'):
                                    result = tool._run(query=query, engine="google")
                                elif hasattr(tool, 'run'):
                                    result = tool.run(query=query, engine="google")
                                elif hasattr(tool, '__call__'):
                                    result = tool(query=query, engine="google")
                                else:
                                    result = tool.search_engine(query=query, engine="google")
                                
                                if result:
                                    return self._parse_mcp_results(result)
                            except Exception as method_error:
                                print(f"⚠️ Method failed for {tool_name}: {str(method_error)}")
                                continue
                        
                        elif any(keyword in tool_name.lower() for keyword in ['scrape', 'web', 'browser']):
                            try:
                                if hasattr(tool, '_run'):
                                    result = tool._run(url=f"https://www.google.com/search?q={query}")
                                elif hasattr(tool, 'run'):
                                    result = tool.run(url=f"https://www.google.com/search?q={query}")
                                
                                if result:
                                    return self._parse_mcp_results(result)
                            except Exception as method_error:
                                print(f"⚠️ Scrape method failed for {tool_name}: {str(method_error)}")
                                continue
                        
                    except Exception as tool_error:
                        print(f"⚠️ Tool {tool_name} failed: {str(tool_error)}")
                        continue
                
                print(f"⚠️ No MCP tool could process: {query}")
                return {'results': []}
                
            except Exception as e:
                print(f"❌ MCP scraping failed: {str(e)}")
                return {'results': []}
    
    def _parse_mcp_results(self, mcp_result):
        """Parse MCP tool results into expected format."""
        try:
            if isinstance(mcp_result, dict) and 'results' in mcp_result:
                print(f"🔍 MCP returned {len(mcp_result['results'])} results")
                return mcp_result
            elif isinstance(mcp_result, list):
                print(f"🔍 MCP returned {len(mcp_result)} results as list")
                return {'results': mcp_result}
            elif isinstance(mcp_result, str):
                if mcp_result.strip().startswith('<') or 'html' in mcp_result.lower():
                    return self._parse_html_search_results(mcp_result)
                else:
                    try:
                        parsed = json.loads(mcp_result)
                        return parsed if isinstance(parsed, dict) else {'results': [parsed]}
                    except:
                        print(f"🔍 MCP returned string: {mcp_result[:100]}...")
                        return {'results': []}
            else:
                try:
                    parsed = json.loads(str(mcp_result))
                    return parsed if isinstance(parsed, dict) else {'results': [parsed]}
                except:
                    print(f"🔍 MCP returned unknown type: {type(mcp_result)}")
                    return {'results': []}
        except Exception as e:
            print(f"⚠️ Error parsing MCP results: {str(e)}")
            return {'results': []}
    
    def _parse_html_search_results(self, html_content):
        """Parse HTML search results page to extract search results."""
        from bs4 import BeautifulSoup
        import re
        
        results = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            all_links = soup.find_all('a', href=True)
            
            for link in all_links:
                try:
                    url = link.get('href', '')
                    
                    if not url.startswith('http'):
                        continue
                        
                    if any(skip in url for skip in [
                        'google.com', 'accounts.google', 'support.google',
                        '/search?', 'javascript:', '#', 'mailto:', 'webcache',
                        'youtube.com/redirect', 'translate.google'
                    ]):
                        continue
                    
                    title_elem = link.find(['h3', 'h2', 'h1', 'span'])
                    if title_elem:
                        title = title_elem.get_text().strip()
                    else:
                        title = link.get_text().strip()
                    
                    if not title or len(title) < 5 or len(title) > 200:
                        continue
                    
                    snippet = ""
                    parent = link.parent
                    if parent:
                        for elem in parent.find_all(['div', 'span', 'p']):
                            text = elem.get_text().strip()
                            if len(text) > 30 and text != title and 'javascript' not in text.lower():
                                snippet = text[:200]
                                break
                    
                    results.append({
                        'url': url,
                        'title': title,
                        'snippet': snippet,
                        'position': len(results) + 1
                    })
                    
                    if len(results) >= 10:
                        break
                            
                except Exception as e:
                    continue
            
            if not results:
                return self._parse_html_with_regex(html_content)
            
            print(f"🔍 Extracted {len(results)} search results from HTML")
            return {'results': results}
            
        except Exception as e:
            print(f"⚠️ Error parsing HTML search results: {str(e)}")
            return self._parse_html_with_regex(html_content)
    
    def _parse_html_with_regex(self, html_content):
        """Fallback regex parsing for HTML search results."""
        import re
        
        results = []
        
        url_pattern = r'https?://[^\s<>"]+\.(?:com|org|net|edu|gov|io|co|ai|tech|biz|info)[^\s<>"]*'
        urls = re.findall(url_pattern, html_content, re.IGNORECASE)
        
        for full_match in re.finditer(url_pattern, html_content, re.IGNORECASE):
            url = full_match.group(0)
            
            if any(skip in url for skip in [
                'google.com', 'youtube.com', 'accounts.google',
                'support.google', 'translate.google'
            ]):
                continue
            
            start_pos = max(0, full_match.start() - 500)
            end_pos = min(len(html_content), full_match.end() + 500)
            surrounding_text = html_content[start_pos:end_pos]
            
            title_patterns = [
                r'<h[1-6][^>]*>([^<]+)</h[1-6]>',
                r'<title[^>]*>([^<]+)</title>',
                r'>([^<]{10,80})</[^>]*>(?=.*' + re.escape(url[:30]) + ')',
                r'([A-Z][^|<>{}\[\]]{10,80})(?=.*' + re.escape(url[:20]) + ')'
            ]
            
            title = ""
            for title_pattern in title_patterns:
                title_matches = re.findall(title_pattern, surrounding_text, re.IGNORECASE)
                if title_matches:
                    title = title_matches[0].strip()
                    break
            
            if not title:
                domain = url.split('://')[1].split('/')[0]
                title = domain.replace('www.', '').title()
            
            if len(title) > 5:
                results.append({
                    'url': url,
                    'title': title[:100],
                    'snippet': '',
                    'position': len(results) + 1
                })
                
                if len(results) >= 10:
                    break
        
        print(f"🔍 Regex extracted {len(results)} search results")
        return {'results': results}
    
    def _parse_linkedin_search_results(self, results, linkedin_url):
        """Parse search results for LinkedIn data."""
        hiring_posts = []
        recent_activity = []
        employee_count = None
        
        for result in results:
            title = result.get('title', '').lower()
            snippet = result.get('snippet', '').lower()
            
            if any(keyword in title or keyword in snippet for keyword in ['hiring', 'jobs', 'careers', 'join']):
                hiring_posts.append({
                    "title": result.get('title', '')[:100],
                    "source": "linkedin_mcp"
                })
            
            if any(keyword in title or keyword in snippet for keyword in ['announces', 'launches', 'proud', 'excited']):
                recent_activity.append({
                    "type": "company_update",
                    "content": result.get('snippet', '')[:200]
                })
        
        return {
            "url": linkedin_url,
            "hiring_posts": hiring_posts,
            "employee_count": employee_count,
            "recent_activity": recent_activity,
            "source": "brightdata_mcp"
        }
    
    def _parse_website_results(self, results, url):
        """Parse website search results."""
        technologies = []
        title = ""
        description = ""
        
        for result in results:
            if not title:
                title = result.get('title', '')[:200]
            if not description:
                description = result.get('snippet', '')[:500]
            
            content = (result.get('title', '') + ' ' + result.get('snippet', '')).lower()
            tech_keywords = {
                'react': 'React',
                'angular': 'Angular', 
                'vue': 'Vue.js',
                'node.js': 'Node.js',
                'python': 'Python',
                'shopify': 'Shopify',
                'salesforce': 'Salesforce'
            }
            
            for keyword, tech in tech_keywords.items():
                if keyword in content and tech not in technologies:
                    technologies.append(tech)
        
        return {
            "url": url,
            "title": title,
            "description": description,
            "technologies": technologies,
            "source": "brightdata_mcp"
        }
    
    def _filter_funding_results(self, results):
        """Filter results for funding-related content."""
        funding_results = []
        funding_keywords = ['funding', 'investment', 'series a', 'series b', 'seed', 'raises', 'raised']
        
        for result in results:
            title = result.get('title', '').lower()
            snippet = result.get('snippet', '').lower()
            
            if any(keyword in title or keyword in snippet for keyword in funding_keywords):
                funding_results.append({
                    "title": result.get('title', '')[:150],
                    "source": result.get('url', '').split('/')[2] if result.get('url') else "Unknown",
                    "date": "2024-01-15"
                })
        
        return funding_results