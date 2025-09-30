import streamlit as st
import os
from dotenv import load_dotenv
from crewai import Crew, Process, Task
import pandas as pd
from datetime import datetime
import json
from mcp_client import BrightDataMCP
from agents.company_discovery import create_company_discovery_agent
from agents.trigger_detection import create_trigger_detection_agent
from agents.contact_research import create_contact_research_agent
from agents.message_generation import create_message_generation_agent
from agents.pipeline_manager import create_pipeline_manager_agent

load_dotenv()

st.set_page_config(
    page_title="AI BDR/SDR System",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI BDR/SDR Agent System")
st.markdown("**Real-time prospecting with multi-agent intelligence and trigger-based personalization**")

if 'workflow_results' not in st.session_state:
    st.session_state.workflow_results = None

with st.sidebar:
    try:
        st.image("bright-data-logo.png", width=200)
        st.markdown("---")
    except:
        st.markdown("**🌐 Powered by Bright Data**")
        st.markdown("---")
    
    st.header("⚙️ Configuration")
    
    st.subheader("Ideal Customer Profile")
    industry = st.selectbox("Industry", ["SaaS", "FinTech", "E-commerce", "Healthcare", "AI/ML"])
    size_range = st.selectbox("Company Size", ["startup", "small", "medium", "enterprise"])
    location = st.text_input("Location (optional)", placeholder="San Francisco, NY, etc.")
    max_companies = st.slider("Max Companies", 5, 50, 20)
    
    st.subheader("Target Decision Makers")
    all_roles = ["CEO", "CTO", "VP Engineering", "Head of Product", "VP Sales", "CMO", "CFO"]
    target_roles = st.multiselect("Roles", all_roles, default=["CEO", "CTO", "VP Engineering"])
    
    st.subheader("Outreach Configuration")
    message_types = st.multiselect(
        "Message Types",
        ["cold_email", "linkedin_message", "follow_up"],
        default=["cold_email"]
    )
    
    with st.expander("Advanced Intelligence"):
        enable_competitive = st.checkbox("Competitive Intelligence", value=True)
        enable_validation = st.checkbox("Multi-source Validation", value=True)
        min_lead_grade = st.selectbox("Min CRM Export Grade", ["A", "B", "C"], index=1)
    
    st.divider()
    
    st.subheader("🔗 API Status")
    
    apis = [
        ("Bright Data", "BRIGHT_DATA_API_TOKEN", "🌐"),
        ("OpenAI", "OPENAI_API_KEY", "🧠"),
        ("HubSpot CRM", "HUBSPOT_API_KEY", "📊")
    ]
    
    for name, env_var, icon in apis:
        if os.getenv(env_var):
            st.success(f"{icon} {name} Connected")
        else:
            if name == "HubSpot CRM":
                st.warning(f"⚠️ {name} Required for CRM export")
            elif name == "Bright Data":
                st.error(f"❌ {name} Missing")
                if st.button("🔧 Configuration Help", key="bright_data_help"):
                    st.info("""
                    **Bright Data Setup Required:**
                    
                    1. Get credentials from Bright Data dashboard
                    2. Update .env file with:
                       ```
                       BRIGHT_DATA_API_TOKEN=your_password
                       WEB_UNLOCKER_ZONE=lum-customer-username-zone-zonename
                       ```
                    3. See BRIGHT_DATA_SETUP.md for detailed guide
                    
                    **Current Error**: 407 Invalid Auth = Wrong credentials
                    """)
            else:
                st.error(f"❌ {name} Missing")

col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("🚀 AI Prospecting Workflow")
    
    if st.button("Start Multi-Agent Prospecting", type="primary", use_container_width=True):
        required_keys = ["BRIGHT_DATA_API_TOKEN", "OPENAI_API_KEY"]
        missing_keys = [key for key in required_keys if not os.getenv(key)]
        
        if missing_keys:
            st.error(f"Missing required API keys: {', '.join(missing_keys)}")
            st.stop()
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            mcp_client = BrightDataMCP()
            
            discovery_agent = create_company_discovery_agent(mcp_client)
            trigger_agent = create_trigger_detection_agent(mcp_client)
            contact_agent = create_contact_research_agent(mcp_client)
            message_agent = create_message_generation_agent()
            pipeline_agent = create_pipeline_manager_agent()
            
            status_text.text("🔍 Discovering companies matching ICP...")
            progress_bar.progress(15)
            
            discovery_task = Task(
                description=f"Find {max_companies} companies in {industry} ({size_range} size) in {location}",
                expected_output="List of companies with ICP scores and intelligence",
                agent=discovery_agent
            )
            
            discovery_crew = Crew(
                agents=[discovery_agent],
                tasks=[discovery_task],
                process=Process.sequential
            )
            
            companies = discovery_agent.tools[0]._run(industry, size_range, location)
            
            st.success(f"✅ Discovered {len(companies)} companies")
            
            status_text.text("🎯 Analyzing trigger events and buying signals...")
            progress_bar.progress(30)
            
            trigger_task = Task(
                description="Detect hiring spikes, funding rounds, leadership changes, and expansion signals",
                expected_output="Companies with trigger events and scores",
                agent=trigger_agent
            )
            
            trigger_crew = Crew(
                agents=[trigger_agent],
                tasks=[trigger_task],
                process=Process.sequential
            )
            
            companies_with_triggers = trigger_agent.tools[0]._run(companies)
            
            total_triggers = sum(len(c.get('trigger_events', [])) for c in companies_with_triggers)
            
            st.success(f"✅ Detected {total_triggers} trigger events")
            progress_bar.progress(45)
            
            status_text.text("👥 Finding decision-maker contacts...")
            
            contact_task = Task(
                description=f"Find verified contacts for roles: {', '.join(target_roles)}",
                expected_output="Companies with decision-maker contact information",
                agent=contact_agent
            )
            
            contact_crew = Crew(
                agents=[contact_agent],
                tasks=[contact_task],
                process=Process.sequential
            )
            
            companies_with_contacts = contact_agent.tools[0]._run(companies_with_triggers, target_roles)
            
            total_contacts = sum(len(c.get('contacts', [])) for c in companies_with_contacts)
            
            st.success(f"✅ Found {total_contacts} verified contacts")
            progress_bar.progress(60)
            
            status_text.text("✍️ Generating personalized outreach messages...")
            
            message_task = Task(
                description=f"Generate {', '.join(message_types)} for each contact using trigger intelligence",
                expected_output="Companies with personalized messages",
                agent=message_agent
            )
            
            message_crew = Crew(
                agents=[message_agent],
                tasks=[message_task],
                process=Process.sequential
            )
            
            companies_with_messages = message_agent.tools[0]._run(companies_with_contacts, message_types[0])
            
            total_messages = sum(len(c.get('contacts', [])) for c in companies_with_messages)
            
            st.success(f"✅ Generated {total_messages} personalized messages")
            progress_bar.progress(75)
            
            status_text.text("📊 Scoring leads and updating CRM...")
            
            pipeline_task = Task(
                description=f"Score leads and export Grade {min_lead_grade}+ to HubSpot CRM",
                expected_output="Scored leads with CRM integration results",
                agent=pipeline_agent
            )
            
            pipeline_crew = Crew(
                agents=[pipeline_agent],
                tasks=[pipeline_task],
                process=Process.sequential
            )
            
            final_companies = pipeline_agent.tools[0]._run(companies_with_messages)
            qualified_leads = [c for c in final_companies if c.get('lead_grade', 'D') in ['A', 'B']]
            
            crm_results = {"success": 0, "errors": 0}
            if os.getenv("HUBSPOT_API_KEY"):
                crm_results = pipeline_agent.tools[1]._run(final_companies, min_lead_grade)
            
            progress_bar.progress(100)
            status_text.text("✅ Workflow completed successfully!")
            
            st.session_state.workflow_results = {
                'companies': final_companies,
                'total_companies': len(final_companies),
                'total_triggers': total_triggers,
                'total_contacts': total_contacts,
                'qualified_leads': len(qualified_leads),
                'crm_results': crm_results,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            st.error(f"❌ Workflow failed: {str(e)}")
            st.write("Please check your API configurations and try again.")

if st.session_state.workflow_results:
    results = st.session_state.workflow_results
    
    st.markdown("---")
    st.subheader("📊 Workflow Results")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Companies Analyzed", results['total_companies'])
    with col2:
        st.metric("Trigger Events", results['total_triggers'])
    with col3:
        st.metric("Contacts Found", results['total_contacts'])
    with col4:
        st.metric("Qualified Leads", results['qualified_leads'])
    
    if results['crm_results']['success'] > 0 or results['crm_results']['errors'] > 0:
        st.subheader("🔄 HubSpot CRM Integration")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Exported to CRM", results['crm_results']['success'], delta="contacts")
        with col2:
            if results['crm_results']['errors'] > 0:
                st.metric("Export Errors", results['crm_results']['errors'], delta_color="inverse")
    
    st.subheader("🏢 Company Intelligence")
    
    for company in results['companies'][:10]:
        with st.expander(f"📋 {company.get('name', 'Unknown')} - Grade {company.get('lead_grade', 'D')} (Score: {company.get('lead_score', 0):.0f})"):
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Industry:** {company.get('industry', 'Unknown')}")
                st.write(f"**Domain:** {company.get('domain', 'Unknown')}")
                st.write(f"**ICP Score:** {company.get('icp_score', 0)}")
                
                triggers = company.get('trigger_events', [])
                if triggers:
                    st.write("**🎯 Trigger Events:**")
                    for trigger in triggers:
                        severity_emoji = {"high": "🔥", "medium": "⚡", "low": "💡"}.get(trigger.get('severity', 'low'), '💡')
                        st.write(f"{severity_emoji} {trigger.get('description', 'Unknown trigger')}")
            
            with col2:
                contacts = company.get('contacts', [])
                if contacts:
                    st.write("**👥 Decision Makers:**")
                    for contact in contacts:
                        confidence = contact.get('confidence_score', 0)
                        confidence_color = "🟢" if confidence >= 75 else "🟡" if confidence >= 50 else "🔴"
                        
                        st.write(f"{confidence_color} **{contact.get('first_name', '')} {contact.get('last_name', '')}**")
                        st.write(f"   {contact.get('title', 'Unknown title')}")
                        st.write(f"   📧 {contact.get('email', 'No email')}")
                        st.write(f"   Confidence: {confidence}%")
                        
                        message = contact.get('generated_message', {})
                        if message.get('subject'):
                            st.write(f"   **Subject:** {message['subject']}")
                        if message.get('body'):
                            preview = message['body'][:100] + "..." if len(message['body']) > 100 else message['body']
                            st.write(f"   **Preview:** {preview}")
                        st.write("---")
    
    st.subheader("📥 Export & Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        export_data = []
        for company in results['companies']:
            for contact in company.get('contacts', []):
                export_data.append({
                    'Company': company.get('name', ''),
                    'Industry': company.get('industry', ''),
                    'Lead Grade': company.get('lead_grade', ''),
                    'Lead Score': company.get('lead_score', 0),
                    'Trigger Count': len(company.get('trigger_events', [])),
                    'Contact Name': f"{contact.get('first_name', '')} {contact.get('last_name', '')}",
                    'Title': contact.get('title', ''),
                    'Email': contact.get('email', ''),
                    'Confidence': contact.get('confidence_score', 0),
                    'Subject Line': contact.get('generated_message', {}).get('subject', ''),
                    'Message': contact.get('generated_message', {}).get('body', '')
                })
        
        if export_data:
            df = pd.DataFrame(export_data)
            csv = df.to_csv(index=False)
            
            st.download_button(
                label="📄 Download Full Report (CSV)",
                data=csv,
                file_name=f"ai_bdr_prospects_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    with col2:
        if st.button("🔄 Sync to HubSpot CRM", use_container_width=True):
            if not os.getenv("HUBSPOT_API_KEY"):
                st.warning("HubSpot API key required for CRM export")
            else:
                with st.spinner("Syncing to HubSpot..."):
                    pipeline_agent = create_pipeline_manager_agent()
                    new_crm_results = pipeline_agent.tools[1]._run(results['companies'], min_lead_grade)
                    st.session_state.workflow_results['crm_results'] = new_crm_results
                st.rerun()
    
    with col3:
        if st.button("🗑️ Clear Results", use_container_width=True):
            st.session_state.workflow_results = None
            st.rerun()

if __name__ == "__main__":
    pass