from crewai import Agent, Task
from crewai.tools import BaseTool
from typing import Any, List
from pydantic import BaseModel, Field
import openai
import os

class MessageGenerationInput(BaseModel):
    companies: List[dict] = Field(description="List of companies with contacts to generate messages for")
    message_type: str = Field(default="cold_email", description="Type of message to generate (cold_email, linkedin_message, follow_up)")

class MessageGenerationTool(BaseTool):
    name: str = "generate_messages"
    description: str = "Create personalized outreach based on company intelligence"
    args_schema: type[BaseModel] = MessageGenerationInput
    client: Any = None
    
    def __init__(self):
        super().__init__()
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def _run(self, companies, message_type="cold_email") -> list:
        # Ensure companies is a list
        if not isinstance(companies, list):
            print(f"Warning: Expected list of companies, got {type(companies)}")
            return []
        
        if not companies:
            print("No companies provided for message generation")
            return []
        
        for company in companies:
            if not isinstance(company, dict):
                print(f"Warning: Expected company dict, got {type(company)}")
                continue
                
            for contact in company.get('contacts', []):
                if not isinstance(contact, dict):
                    continue
                    
                message = self._generate_personalized_message(contact, company, message_type)
                contact['generated_message'] = message
                contact['message_quality_score'] = self._calculate_message_quality(message, company)
        return companies
    
    def _generate_personalized_message(self, contact, company, message_type):
        context = self._build_message_context(contact, company)
        
        if message_type == "cold_email":
            return self._generate_cold_email(context)
        elif message_type == "linkedin_message":
            return self._generate_linkedin_message(context)
        else:
            return self._generate_cold_email(context)
    
    def _build_message_context(self, contact, company):
        triggers = company.get('trigger_events', [])
        primary_trigger = triggers[0] if triggers else None
        
        return {
            'contact_name': contact.get('first_name', ''),
            'contact_title': contact.get('title', ''),
            'company_name': company.get('name', ''),
            'industry': company.get('industry', ''),
            'primary_trigger': primary_trigger,
            'trigger_count': len(triggers)
        }
    
    def _generate_cold_email(self, context):
        trigger_text = ""
        if context['primary_trigger']:
            trigger_text = f"I noticed {context['company_name']} {context['primary_trigger']['description'].lower()}."
        
        prompt = f"""Write a personalized cold email:

Contact: {context['contact_name']}, {context['contact_title']} at {context['company_name']}
Industry: {context['industry']}
Context: {trigger_text}

Requirements:
- Subject line that references the trigger event
- Personal greeting with first name
- Opening that demonstrates research
- Brief value proposition
- Clear call-to-action
- Maximum 120 words

Format as:
SUBJECT: [subject line]
BODY: [email body]"""

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=300
        )
        
        return self._parse_email_response(response.choices[0].message.content)
    
    def _generate_linkedin_message(self, context):
        prompt = f"""Write a LinkedIn connection request (max 300 chars):

Contact: {context['contact_name']} at {context['company_name']}
Context: {context.get('primary_trigger', {}).get('description', '')}

Be professional, reference their company activity, no direct sales pitch."""

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=100
        )
        
        return {
            'subject': 'LinkedIn Connection Request',
            'body': response.choices[0].message.content.strip()
        }
    
    def _parse_email_response(self, response):
        lines = response.strip().split('\n')
        subject = ""
        body_lines = []
        
        for line in lines:
            if line.startswith('SUBJECT:'):
                subject = line.replace('SUBJECT:', '').strip()
            elif line.startswith('BODY:'):
                body_lines.append(line.replace('BODY:', '').strip())
            elif body_lines:
                body_lines.append(line)
        
        return {
            'subject': subject,
            'body': '\n'.join(body_lines).strip()
        }
    
    def _calculate_message_quality(self, message, company):
        score = 0
        body = message.get('body', '').lower()
        
        if company.get('name', '').lower() in message.get('subject', '').lower():
            score += 25
        if company.get('trigger_events') and any(t.get('type', '') in body for t in company['trigger_events']):
            score += 30
        if len(body.split()) <= 120:
            score += 20
        if any(word in body for word in ['call', 'meeting', 'discuss', 'connect']):
            score += 25
        
        return score

def create_message_generation_agent():
    return Agent(
        role='Personalization Specialist',
        goal='Create compelling personalized outreach that gets responses',
        backstory='Expert at crafting messages that demonstrate research and provide value.',
        tools=[MessageGenerationTool()],
        verbose=True
    )