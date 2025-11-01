# Environment Variables Setup Guide

## Primary Location: `infra/.env`

The main `.env` file is located at **`infra/.env`**. This is the first location checked by the API configuration.

### File Loading Priority

The API (`apps/api/config.py`) loads environment variables in this order:

1. **`infra/.env`** (Primary - recommended)
2. `apps/api/.env` (Fallback)
3. `.env` (Root directory fallback)
4. System environment variables (last resort)

## Creating Your `.env` File

```bash
# From project root
cp infra/env.example infra/.env

# Then edit infra/.env with your actual credentials
nano infra/.env  # or use your preferred editor
```

## Required Environment Variables

### MongoDB Atlas (`MONGODB_URI`)

**Location in `.env`:** `infra/.env`
**Variable name:** `MONGODB_URI`
**Format:** `mongodb+srv://username:password@cluster.mongodb.net/?appName=AIChatbot`

**How to get:**
1. Go to MongoDB Atlas: https://cloud.mongodb.com
2. Click "Connect" on your cluster
3. Choose "Connect your application"
4. Copy the connection string
5. Replace `<password>` with your database user password

**Example:**
```bash
MONGODB_URI=mongodb+srv://chatbot-admin:YOUR_PASSWORD@aichatbot.g9gdaei.mongodb.net/?appName=AIChatbot
```

### OpenAI API Key (`OPENAI_API_KEY`)

**Location in `.env`:** `infra/.env`
**Variable name:** `OPENAI_API_KEY`

**How to get:**
1. Go to OpenAI Platform: https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key (you'll only see it once!)
4. Paste into `infra/.env`

**Example:**
```bash
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## Optional Variables

### Feature Flags

```bash
# Use mock integrations (ServiceNow, Jira, M365) for demo
USE_MOCK_INTEGRATIONS=true

# Enable audit logging
ENABLE_AUDIT_LOGS=true
```

### n8n Webhooks

```bash
N8N_WEBHOOK_TICKET_CREATED=http://localhost:5678/webhook/ticket-created
N8N_WEBHOOK_ESCALATE=http://localhost:5678/webhook/escalate
```

### Real Integrations (when `USE_MOCK_INTEGRATIONS=false`)

#### ServiceNow
```bash
SERVICENOW_INSTANCE_URL=https://yourinstance.service-now.com
SERVICENOW_USERNAME=your_username
SERVICENOW_PASSWORD=your_password
```

#### Jira
```bash
JIRA_SERVER_URL=https://yourcompany.atlassian.net
JIRA_EMAIL=your_email
JIRA_API_TOKEN=your_api_token
```

#### M365 Graph API
```bash
M365_TENANT_ID=your_tenant_id
M365_CLIENT_ID=your_client_id
M365_CLIENT_SECRET=your_client_secret
```

## Verification

### Check if `.env` is loaded:

```python
# In Python (apps/api/)
from config import settings
print(f"MongoDB URI configured: {settings.mongodb_uri is not None}")
print(f"OpenAI key configured: {settings.openai_api_key is not None}")
```

### Check in Node.js:

```javascript
// In Node.js
require('dotenv').config({ path: './infra/.env' });
console.log('MongoDB URI:', process.env.MONGODB_URI ? 'Set' : 'Missing');
console.log('OpenAI Key:', process.env.OPENAI_API_KEY ? 'Set' : 'Missing');
```

## Troubleshooting

### "MongoDB connection failed"
- Check `infra/.env` exists and has `MONGODB_URI` set
- Verify MongoDB Atlas IP whitelist allows your IP (or 0.0.0.0/0 for demo)
- Ensure credentials are correct

### "OpenAI API error"
- Verify `OPENAI_API_KEY` in `infra/.env`
- Check API key hasn't expired
- Ensure billing is set up on OpenAI account

### "Environment variable not found"
- Ensure `.env` file is in `infra/` directory
- Check variable name matches exactly (case-insensitive but must match)
- Verify file is not corrupted (check for syntax errors)

## Security Best Practices

1. **Never commit `.env` to git** - It's in `.gitignore`
2. **Use different keys for dev/prod** - Rotate credentials regularly
3. **Restrict MongoDB IP access** - Use IP whitelist in Atlas
4. **Rotate credentials** - Especially after exposure (see `ROTATE_CREDENTIALS.md`)

## Files Reference

- **API Configuration:** `apps/api/config.py` - Loads `infra/.env`
- **Example Template:** `infra/env.example` - Template with placeholders
- **Connect Script:** `connect.js` - Uses `infra/.env` for MongoDB URI
- **Next.js Config:** `apps/web/next.config.js` - Uses `NEXT_PUBLIC_API_URL` or `API_URL`

## Quick Reference

| Variable | Location | Required | Example Location |
|----------|----------|----------|------------------|
| `MONGODB_URI` | `infra/.env` | ✅ Yes | MongoDB Atlas |
| `OPENAI_API_KEY` | `infra/.env` | ✅ Yes | OpenAI Platform |
| `USE_MOCK_INTEGRATIONS` | `infra/.env` | ❌ No (default: true) | - |
| `SERVICENOW_*` | `infra/.env` | ❌ No | ServiceNow instance |
| `JIRA_*` | `infra/.env` | ❌ No | Jira instance |
| `M365_*` | `infra/.env` | ❌ No | Azure Portal |

---

**Remember:** Always use `infra/.env` as your primary environment file location!

