# IT Helpdesk Copilot MVP

AI-powered IT support assistant with RAG, ticket creation, and agentic workflows.

## Features

- **RAG (Retrieval Augmented Generation)**: Answer questions from knowledge base using MongoDB Atlas Vector Search
- **Ticket Creation**: Create tickets in ServiceNow or Jira (with mock fallback)
- **Password Reset**: Trigger M365 self-service password reset flows
- **Ticket Status**: Check status of existing tickets
- **Agentic Workflows**: LangGraph-based orchestrator with intent classification
- **n8n Integration**: Automated notifications and workflows

## Architecture

```
Web (Next.js) ──> API (FastAPI) ──> Orchestrator (LangGraph)
                                      │
                                      ├──> RAG: MongoDB Atlas Vector Search
                                      ├──> Tools: ServiceNow/Jira/M365
                                      └──> n8n: Notifications
```

## Tech Stack

- **Frontend**: Next.js 14, React, Tailwind CSS
- **Backend**: FastAPI (Python)
- **LLM**: OpenAI (GPT-4o-mini)
- **RAG**: MongoDB Atlas Vector Search + OpenAI Embeddings
- **Orchestration**: LangGraph + LangChain
- **Database**: MongoDB Atlas (M0 free tier)
- **Automation**: n8n (Docker)

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- MongoDB Atlas account (free tier)
- OpenAI API key
- Docker (for n8n)

### Setup

1. **Clone and install dependencies**

```bash
# Install Python dependencies
cd apps/api
pip install -r requirements.txt

# Install Node dependencies
cd ../../apps/web
npm install
```

2. **Configure environment**

```bash
# Copy example env file
cp infra/env.example infra/.env

# Edit infra/.env and add:
# - MongoDB Atlas connection string
# - OpenAI API key
# - Other optional credentials
```

3. **Initialize MongoDB**

The database will be initialized automatically on first run. You can also run:

```python
# From apps/api directory
python -c "from db import init_database; import asyncio; asyncio.run(init_database())"
```

4. **Ingest Knowledge Base**

```bash
# From apps/api directory
python -m packages.rag.ingestion ../seeds/kb
```

This will:
- Load all markdown files from `seeds/kb`
- Chunk and embed them
- Store in MongoDB with vector embeddings

5. **Create MongoDB Vector Search Index**

In MongoDB Atlas UI:
1. Go to your cluster > Collections
2. Select `kb_chunks` collection
3. Click "Create Search Index"
4. Use JSON Editor and paste:

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

Name it `kb_chunks_vec`.

6. **Start services**

```bash
# Terminal 1: Start API
cd apps/api
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start Web
cd apps/web
npm run dev

# Terminal 3: Start n8n (optional)
docker-compose -f infra/docker-compose.yml up n8n
```

7. **Access application**

- Web UI: http://localhost:3000
- API Docs: http://localhost:8000/docs
- n8n: http://localhost:5678 (admin/admin)

### Using Docker (Full Stack)

```bash
# Start all services
docker-compose -f infra/docker-compose.yml up -d

# View logs
docker-compose -f infra/docker-compose.yml logs -f
```

## Usage

### Authentication

1. Open web UI: http://localhost:3000
2. Enter any email (demo mode)
3. Click "Sign In"
4. Token will be returned (for demo only)

### Chat Examples

- **Knowledge**: "How do I set up MFA on a new laptop?"
- **Create Ticket**: "Open a P2 ticket for VPN failing on Mac"
- **Ticket Status**: "What's the status of INC0012345?"
- **Password Reset**: "Reset my password"

### API Endpoints

- `POST /chat` - Send chat message
- `GET /sessions/{id}/messages` - Get conversation history
- `GET /tickets/{id}` - Get ticket status
- `POST /auth/magic-link` - Create magic link (demo)
- `POST /admin/ingest` - Ingest KB documents (admin only)

See full API docs at http://localhost:8000/docs

## Configuration

### Environment Variables

Key variables in `infra/.env`:

- `MONGODB_URI`: MongoDB Atlas connection string
- `OPENAI_API_KEY`: OpenAI API key
- `USE_MOCK_INTEGRATIONS`: Use mock clients (true/false)
- `N8N_WEBHOOK_*`: n8n webhook URLs

### Switching to Real Integrations

1. Set `USE_MOCK_INTEGRATIONS=false`
2. Add credentials:
   - ServiceNow: `SERVICENOW_INSTANCE_URL`, `SERVICENOW_USERNAME`, `SERVICENOW_PASSWORD`
   - Jira: `JIRA_SERVER_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN`
   - M365: `M365_TENANT_ID`, `M365_CLIENT_ID`, `M365_CLIENT_SECRET`

## n8n Workflows

### Workflow 1: Ticket Created Notification

Trigger: Webhook `/webhook/ticket-created`

Actions:
1. Send Teams message to helpdesk channel
2. Send email to user with ticket details

### Workflow 2: Escalation

Trigger: Webhook `/webhook/escalate`

Actions:
1. Notify L2 support
2. Create ServiceNow comment
3. Send email to user

## Development

### Project Structure

```
it-helpdesk-copilot/
  apps/
    web/          # Next.js frontend
    api/          # FastAPI backend
  packages/
    clients/      # ServiceNow, Jira, M365 clients
    rag/          # RAG utilities (loaders, chunkers, embeddings, retriever)
    orchestrator/ # LangGraph orchestrator
  seeds/
    kb/           # Knowledge base markdown files
  infra/
    docker-compose.yml
    env.example
```

### Adding Knowledge Base Articles

1. Add markdown file to `seeds/kb/`
2. Run ingestion: `python -m packages.rag.ingestion ../seeds/kb`
3. Test retrieval via chat

### Testing

```bash
# Run API tests (when available)
cd apps/api
pytest

# Run web tests
cd apps/web
npm test
```

## Deployment

### Production Checklist

- [ ] Set `USE_MOCK_INTEGRATIONS=false`
- [ ] Configure real integrations (ServiceNow, Jira, M365)
- [ ] Set up Azure AD OAuth (replace magic link)
- [ ] Enable rate limiting
- [ ] Set up monitoring (e.g., Sentry)
- [ ] Configure HTTPS
- [ ] Set secure secrets management
- [ ] Enable audit logs
- [ ] Test all workflows end-to-end

### Deployment Options

- **Render/Fly.io**: Deploy API and web separately
- **AWS/GCP**: Use containers with ECS/Cloud Run
- **On-premise**: Docker Compose on VM

## Demo Script

### Flow A: RAG
1. "How do I set up MFA on a new laptop?"
2. Bot returns step-by-step instructions from KB

### Flow B: Create Ticket
1. "Open a P2 ticket for VPN failing on Mac"
2. Bot creates ticket and returns ID
3. n8n sends Teams notification

### Flow C: Ticket Status
1. "What's the status of INC0012345?"
2. Bot returns current status

### Flow D: Password Reset
1. "Reset my password"
2. Bot sends SSR link via email

## Troubleshooting

### MongoDB Connection Issues
- Verify connection string in `.env`
- Check network access in Atlas
- Ensure IP is whitelisted (or use 0.0.0.0/0 for demo)

### Vector Search Not Working
- Verify index `kb_chunks_vec` exists
- Check embedding dimensions match (1536 for text-embedding-3-large)
- Try fallback retrieval (client-side similarity)

### OpenAI API Errors
- Verify API key is correct
- Check API quota/limits
- Ensure model name is correct

### n8n Not Receiving Webhooks
- Verify n8n is running (http://localhost:5678)
- Check webhook URLs in `.env`
- Test webhook manually in n8n UI

## License

MIT

## Support

For issues or questions:
- Create an issue in the repository
- Contact IT support: ext. 1234

