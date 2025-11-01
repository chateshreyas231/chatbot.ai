# Security Guidelines

## Environment Variables

**All sensitive credentials must be stored in `.env` files and NEVER committed to git.**

### Required Environment Variables

Create a `.env` file in `infra/` with the following variables:

```bash
# MongoDB Atlas
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?appName=AIChatbot
MONGODB_DB_NAME=it_helpdesk

# OpenAI
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-large

# Feature Flags
USE_MOCK_INTEGRATIONS=true
ENABLE_AUDIT_LOGS=true

# Optional: Real Integrations (only when USE_MOCK_INTEGRATIONS=false)
# SERVICENOW_INSTANCE_URL=https://yourinstance.service-now.com
# SERVICENOW_USERNAME=your_username
# SERVICENOW_PASSWORD=your_password

# JIRA_SERVER_URL=https://yourcompany.atlassian.net
# JIRA_EMAIL=your_email
# JIRA_API_TOKEN=your_api_token

# M365_TENANT_ID=your_tenant_id
# M365_CLIENT_ID=your_client_id
# M365_CLIENT_SECRET=your_client_secret
```

## Files Excluded from Git

The following files are automatically excluded via `.gitignore`:

- `.env` files (all variants)
- `MongoDB-user.txt` - Contains MongoDB credentials
- `connect.js` - Contains hardcoded MongoDB connection string (use environment variable instead)
- `*.key`, `*.pem` - Private keys
- `secrets/` - Secret files directory
- `*credentials*`, `*password*` - Any files with credentials/passwords in name

## Best Practices

1. **Never commit `.env` files** - Use `.env.example` as a template
2. **Rotate credentials regularly** - Change passwords and API keys periodically
3. **Use environment variables** - Never hardcode credentials in source code
4. **Review commits before pushing** - Verify no sensitive data is included
5. **Use secret management** - For production, consider AWS Secrets Manager or Azure Key Vault

## If You Accidentally Commit Credentials

If you accidentally commit credentials:

1. **Rotate the credentials immediately** - Change all exposed passwords/keys
2. **Remove from git history**:
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch path/to/file" \
     --prune-empty --tag-name-filter cat -- --all
   ```
3. **Force push** (coordinate with team first):
   ```bash
   git push origin --force --all
   ```

## MongoDB Connection

The MongoDB connection string should be loaded from environment variables, not hardcoded. 

Example (correct):
```python
from config import settings
uri = settings.mongodb_uri  # Loaded from .env
```

Example (incorrect):
```python
uri = "mongodb+srv://user:pass@cluster..."  # Never do this!
```

## API Keys

- Store all API keys in `.env` files
- Use different keys for development and production
- Rotate keys regularly
- Never share keys in chat, emails, or documentation

## Production Security

For production deployments:

1. Use managed secret services (AWS Secrets Manager, Azure Key Vault, etc.)
2. Enable encryption at rest
3. Use HTTPS/TLS for all connections
4. Implement rate limiting
5. Enable audit logging
6. Use least-privilege access controls
7. Regularly review access logs

