<div align="center">
  <a href="https://brightdata.com/">
    <img src="https://mintlify.s3.us-west-1.amazonaws.com/brightdata/logo/light.svg" width="300" alt="Bright Data Logo">
  </a>

# AI BDR/SDR Agent System

Real-time prospecting with multi-agent intelligence and trigger-based personalization.

<img src="https://img.shields.io/badge/python-3.11+-blue" />
<img src="https://img.shields.io/badge/OpenAI-API-blueviolet" />
<img src="https://img.shields.io/badge/License-MIT-blue" />
</div>

<div align="center">
<img src="https://media.brightdata.com/2025/09/AI-SDR-Agent-demo.gif" alt="AI SDR/BDR Agent Demo">
</div>

---

## Overview

This system uses **5 specialized AI agents**:
  1. Company Discovery Agent — Find companies matching your ICP
  2. Trigger Detection Agent — Identify buying signals and optimal timing
  3. Contact Research Agent — Extract decision-maker information
  4. Message Generation Agent — Create personalized outreach
  5. Pipeline Manager — Score leads and integrate with CRM

[**Visit the step-by-step guide on our blog**](https://brightdata.com/blog/ai/ai-sdr-agent-with-web-mcp)

---

## Prerequisites

- Python 3.11+
- Node.js and npm (for MCP server)
- API Keys:
    - [OpenAI API key](https://platform.openai.com/api-keys)
    - [Bright Data](https://brightdata.com/) account with Web MCP access
    - HubSpot CRM credentials (optional)

---

## Quick Start

1. **Clone and setup:**

        git clone <repository>
        cd AI_BDR_SDR
        python setup.py

2. **Configure API keys:**  
   Edit `.env` file with your credentials:

        OPENAI_API_KEY=your_key_here
        BRIGHT_DATA_API_TOKEN=your_token_here
        HUBSPOT_API_KEY=your_hubspot_key_here

3. **Test the system:**

        python test_workflow.py

4. **Run the application:**

        streamlit run ai_bdr_system.py

---

## Features

- Multi-Agent Workflow: Parallel processing, real-time data, scoring, CRM integration
- Trigger Intelligence: Hiring spikes, funding, leadership changes, expansion
- Personalization Engine: Context-aware, trigger-based, multi-channel, A/B testing
- Export & Integration: CSV, HubSpot sync, field mapping, bulk contacts

---

## System Architecture

    ┌─────────────────────────────────────────────────────────────┐
    │                    Streamlit Frontend                      │
    ├─────────────────────────────────────────────────────────────┤
    │                    CrewAI Orchestration                    │
    ├─────────────────────────────────────────────────────────────┤
    │  Discovery │ Triggers │ Contacts │ Messages │ Pipeline      │
    │   Agent    │  Agent   │  Agent   │  Agent   │ Manager       │
    ├─────────────────────────────────────────────────────────────┤
    │    Bright Data MCP │ OpenAI │ HubSpot API                  │
    └─────────────────────────────────────────────────────────────┘

---

## Configuration

### ICP Targeting
  - Industry selection (SaaS, FinTech, E-commerce, etc.)
  - Company size ranges
  - Geographic targeting
  - Custom criteria

### Message Types
  - Cold email campaigns
  - LinkedIn connection requests
  - Follow-up sequences
  - Custom templates

### Lead Scoring
  - ICP match score (30%)
  - Trigger event score (30%)
  - Contact quality score (20%)
  - Timing optimization (20%)

---

## API Integrations

### Bright Data MCP
  - Real-time web scraping
  - LinkedIn company data
  - News and press releases
  - Contact information

### OpenAI GPT-4
  - Message personalization
  - Content generation
  - Trigger analysis
  - Lead qualification

### HubSpot CRM
  - Contact creation/updates
  - Lead scoring sync
  - Custom properties
  - Pipeline management

---

## Troubleshooting

1. MCP Connection Errors

        npm install -g @brightdata/mcp

2. Missing Dependencies

        pip install -r requirements.txt

3. API Key Errors

    - Verify keys in `.env` file
    - Check API quotas and permissions

### Validation

        python test_workflow.py

---

## Performance Metrics

- Companies discovered: 15-25
- Trigger events: 8-15
- Quality contacts: 40-60
- Response rate: 15-25%
- Meeting bookings: 3-8%

---

## Security & Privacy

- API keys stored in environment variables
- No data persistence beyond session
- GDPR-compliant contact handling
- Rate limiting for API protection

---

## License

MIT License - see LICENSE file for details.
