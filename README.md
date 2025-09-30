# AI BDR/SDR Agent System

Real-time prospecting with multi-agent intelligence and trigger-based personalization.

## Overview

This system uses 5 specialized AI agents to automate the entire sales prospecting workflow:

1. **Company Discovery Agent** - Find companies matching your ICP
2. **Trigger Detection Agent** - Identify buying signals and optimal timing  
3. **Contact Research Agent** - Extract decision-maker information
4. **Message Generation Agent** - Create personalized outreach
5. **Pipeline Manager** - Score leads and integrate with CRM

## Prerequisites

- Python 3.11+
- Node.js and npm (for MCP server)
- API Keys:
  - OpenAI API key
  - Bright Data account with MCP access
  - HubSpot CRM credentials (optional)

## Quick Start

1. **Clone and setup:**
   ```bash
   git clone <repository>
   cd AI_BDR_SDR
   python setup.py
   ```

2. **Configure API keys:**
   Edit `.env` file with your credentials:
   ```bash
   OPENAI_API_KEY=your_key_here
   BRIGHT_DATA_API_TOKEN=your_token_here
   HUBSPOT_API_KEY=your_hubspot_key_here
   ```

3. **Test the system:**
   ```bash
   python test_workflow.py
   ```

4. **Run the application:**
   ```bash
   streamlit run ai_bdr_system.py
   ```

## Features

### Multi-Agent Workflow
- **Parallel processing** with CrewAI orchestration
- **Real-time data** from LinkedIn, company websites, news sources
- **Intelligent scoring** based on multiple factors
- **CRM integration** with HubSpot

### Trigger Intelligence
- Hiring spikes and job postings
- Funding rounds and investments
- Leadership changes
- Business expansion signals

### Personalization Engine
- Context-aware message generation
- Trigger-based outreach timing
- Multi-channel support (email, LinkedIn)
- A/B testing capabilities

### Export & Integration
- CSV reports with full prospect data
- HubSpot CRM sync with lead scoring
- Custom field mapping
- Bulk contact management

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                       │
├─────────────────────────────────────────────────────────────┤
│                    CrewAI Orchestration                     │
├─────────────────────────────────────────────────────────────┤
│  Discovery │ Triggers │ Contacts │ Messages │ Pipeline      │
│   Agent    │  Agent   │  Agent   │  Agent   │ Manager       │
├─────────────────────────────────────────────────────────────┤
│            Bright Data MCP │ OpenAI │ HubSpot API            │
└─────────────────────────────────────────────────────────────┘
```

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

## Troubleshooting

### Common Issues

1. **MCP Connection Errors**
   ```bash
   npm install -g @brightdata/mcp
   ```

2. **Missing Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **API Key Errors**
   - Verify keys in `.env` file
   - Check API quotas and permissions

### Validation
Run the test suite to identify issues:
```bash
python test_workflow.py
```

## Performance Metrics

Typical results per workflow run:
- **Companies discovered:** 15-25
- **Trigger events:** 8-15
- **Quality contacts:** 40-60
- **Response rate:** 15-25%
- **Meeting bookings:** 3-8%

## Security & Privacy

- API keys stored in environment variables
- No data persistence beyond session
- GDPR-compliant contact handling
- Rate limiting for API protection

## Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Submit pull request

## License

MIT License - see LICENSE file for details.