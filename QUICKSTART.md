# Quick Start Guide

Get your IT Helpdesk Copilot MVP running in 10 minutes!

## Prerequisites

- Python 3.11+
- Node.js 18+
- MongoDB Atlas account (free tier) - https://www.mongodb.com/cloud/atlas
- OpenAI API key - https://platform.openai.com/api-keys

## Step 1: Setup Environment (2 min)

```bash
# Clone/navigate to project
cd /path/to/Chatbot.ai

# Copy environment file
cp infra/env.example infra/.env

# Edit infra/.env and add:
# - MONGODB_URI (from MongoDB Atlas Connection String)
#   Location: infra/.env
#   Format: mongodb+srv://username:password@cluster.mongodb.net/?appName=AIChatbot
# - OPENAI_API_KEY (from OpenAI dashboard: https://platform.openai.com/api-keys)
#   Location: infra/.env
#   Key name: OPENAI_API_KEY
```

**Note:** The `.env` file location is `infra/.env` - this is checked first by the API configuration.

## Step 2: Install Dependencies (3 min)

```bash
# Python dependencies
cd apps/api
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ../..

# Node dependencies
cd apps/web
npm install
cd ../..
```

## Step 3: Initialize MongoDB (1 min)

The database will auto-initialize on first run. Or manually:

```bash
cd apps/api
source venv/bin/activate
python -c "from db import init_database; import asyncio; asyncio.run(init_database())"
```

## Step 4: Ingest Knowledge Base (2 min)

```bash
cd apps/api
source venv/bin/activate
python -m packages.rag.ingestion ../seeds/kb
```

This loads 6 sample KB articles (MFA, VPN, Password Reset, Email, Teams, Laptop Setup).

## Step 5: Create Vector Search Index (2 min)

1. Go to MongoDB Atlas: https://cloud.mongodb.com
2. Navigate to your cluster > Collections > `kb_chunks`
3. Click "Create Search Index" > "JSON Editor"
4. Paste this JSON:

```json
{
  "fields": [
    {
      "type": "vector",
      "path": "embedding",
      "numDimensions": 1536,
      "similarity": "cosine"
    }
  ]
}
```

5. Name it: `kb_chunks_vec`
6. Click "Next" > "Create Search Index"
7. Wait ~1 minute for index to build

**Note:** If Vector Search isn't available on your tier, the system will fall back to client-side similarity.

## Step 6: Start Services (1 min)

```bash
# Terminal 1: API
cd apps/api
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Web
cd apps/web
npm run dev

# Terminal 3: n8n (optional)
docker-compose -f infra/docker-compose.yml up n8n
```

## Step 7: Test It! (1 min)

1. Open browser: http://localhost:3000
2. Enter any email (e.g., `demo@acme.com`)
3. Click "Sign In"
4. Try these queries:
   - "How do I set up MFA?"
   - "Open a ticket for VPN issue"
   - "Reset my password"

## Troubleshooting

### "MongoDB connection failed"
- Verify connection string in `infra/.env`
- Check MongoDB Atlas IP whitelist (allow 0.0.0.0/0 for demo)
- Ensure network access is enabled

### "OpenAI API error"
- Verify API key is correct
- Check API quota/limits
- Ensure billing is set up

### "Vector search failed"
- Verify index `kb_chunks_vec` exists and is built
- Check embedding dimensions (1536 for text-embedding-3-large)
- System will fall back to client-side similarity

### "Import errors"
- Ensure you're in the correct directory
- Activate virtual environment
- Check Python path includes `apps/api`

## Next Steps

1. **Add more KB articles**: Add markdown files to `seeds/kb/` and re-run ingestion
2. **Configure real integrations**: Set `USE_MOCK_INTEGRATIONS=false` in `.env` and add credentials
3. **Set up n8n workflows**: Create webhooks in n8n for ticket notifications
4. **Customize prompts**: Edit `packages/orchestrator/prompts.py`

## Demo Script

### Flow A: Knowledge Base Query
**User:** "How do I set up MFA on a new laptop?"
**Bot:** Returns step-by-step instructions from KB

### Flow B: Create Ticket
**User:** "Open a P2 ticket for VPN failing on Mac"
**Bot:** Creates ticket (mock or real) and returns ID

### Flow C: Check Ticket Status
**User:** "What's the status of INC0012345?"
**Bot:** Returns current ticket status

### Flow D: Password Reset
**User:** "Reset my password"
**Bot:** Sends password reset link

## Architecture Overview

```
┌─────────────┐
│  Next.js    │  Port 3000
│  Frontend   │
└──────┬──────┘
       │ HTTP
       ▼
┌─────────────┐
│  FastAPI    │  Port 8000
│  Backend    │
└──────┬──────┘
       │
       ├──► MongoDB Atlas (Knowledge Base + Tickets)
       ├──► OpenAI (LLM + Embeddings)
       ├──► ServiceNow/Jira (Ticket Systems)
       ├──► M365 Graph (Password Reset)
       └──► n8n (Automations)
```

## Support

- **Documentation**: See `README.md`
- **API Docs**: http://localhost:8000/docs
- **Issues**: Check import paths and environment variables

## What's Next?

- Production deployment
- Azure AD OAuth integration
- Custom LLM models
- Enhanced RAG with multiple data sources
- Advanced n8n workflows
- Monitoring and observability

Happy building! 🚀

