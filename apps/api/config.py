"""Configuration settings for the IT Helpdesk Copilot API."""
from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path

# Load .env from multiple possible locations
from dotenv import load_dotenv

# Try loading .env from infra/, apps/api/, and root
base_dir = Path(__file__).parent.parent.parent
env_files = [
    base_dir / "infra" / ".env",
    base_dir / "apps" / "api" / ".env",
    base_dir / ".env",
]

for env_file in env_files:
    if env_file.exists():
        load_dotenv(env_file)
        break
else:
    # Fallback to default .env loading
    load_dotenv()


class Settings(BaseSettings):
    """Application settings."""
    
    # MongoDB
    mongodb_uri: str
    mongodb_db_name: str = "it_helpdesk"
    
    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-large"
    
    # Azure AD
    azure_ad_client_id: Optional[str] = None
    azure_ad_client_secret: Optional[str] = None
    azure_ad_tenant_id: Optional[str] = None
    
    # Demo Auth
    magic_link_secret: str = "demo-secret-change-in-production"
    jwt_secret_key: str = "demo-jwt-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60
    
    # n8n
    n8n_webhook_ticket_created: Optional[str] = None
    n8n_webhook_escalate: Optional[str] = None
    
    # ServiceNow
    servicenow_instance_url: Optional[str] = None
    servicenow_username: Optional[str] = None
    servicenow_password: Optional[str] = None
    
    # Jira
    jira_server_url: Optional[str] = None
    jira_email: Optional[str] = None
    jira_api_token: Optional[str] = None
    
    # M365
    m365_tenant_id: Optional[str] = None
    m365_client_id: Optional[str] = None
    m365_client_secret: Optional[str] = None
    
    # Server
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    environment: str = "development"
    
    # Feature Flags
    use_mock_integrations: bool = True
    enable_audit_logs: bool = True
    rate_limit_requests_per_min: int = 20
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

