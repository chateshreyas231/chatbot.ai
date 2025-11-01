"""Microsoft 365 Graph API client."""
import httpx
from typing import Dict, Optional
from msal import ConfidentialClientApplication
import sys
from pathlib import Path
import json

# Add apps/api to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "apps" / "api"))

from config import settings


class M365Client:
    """Microsoft Graph API client for password reset and other M365 operations."""
    
    def __init__(
        self,
        tenant_id: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None
    ):
        self.tenant_id = tenant_id or settings.m365_tenant_id
        self.client_id = client_id or settings.m365_client_id
        self.client_secret = client_secret or settings.m365_client_secret
        
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.scopes = ["https://graph.microsoft.com/.default"]
        
        if all([self.tenant_id, self.client_id, self.client_secret]):
            self.app = ConfidentialClientApplication(
                client_id=self.client_id,
                client_credential=self.client_secret,
                authority=self.authority
            )
        else:
            self.app = None
    
    async def get_access_token(self) -> Optional[str]:
        """Get access token for Graph API."""
        if not self.app:
            return None
        
        result = self.app.acquire_token_for_client(scopes=self.scopes)
        
        if "access_token" in result:
            return result["access_token"]
        else:
            print(f"Token acquisition failed: {result.get('error_description')}")
            return None
    
    async def get_ssr_link(self, user_email: str) -> str:
        """Get self-service password reset link for user."""
        token = await self.get_access_token()
        
        if not token:
            # Return mock link in demo mode
            return f"https://account.activedirectory.windowsazure.com/ChangePassword.aspx?email={user_email}"
        
        # Graph API call to get user
        graph_url = f"https://graph.microsoft.com/v1.0/users/{user_email}"
        headers = {"Authorization": f"Bearer {token}"}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(graph_url, headers=headers)
                if response.status_code == 200:
                    user_data = response.json()
                    # In production, you'd trigger actual password reset
                    # For now, return self-service portal link
                    return f"https://account.activedirectory.windowsazure.com/ChangePassword.aspx?email={user_email}"
                else:
                    # Fallback
                    return f"https://account.activedirectory.windowsazure.com/ChangePassword.aspx?email={user_email}"
            except Exception as e:
                print(f"Error getting SSR link: {e}")
                return f"https://account.activedirectory.windowsazure.com/ChangePassword.aspx?email={user_email}"
    
    async def send_password_reset_email(self, user_email: str) -> bool:
        """Send password reset email via Graph API."""
        token = await self.get_access_token()
        
        if not token:
            return False
        
        # Graph API to send email (requires appropriate permissions)
        graph_url = f"https://graph.microsoft.com/v1.0/users/{user_email}/sendMail"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        message = {
            "message": {
                "subject": "Password Reset Request",
                "body": {
                    "contentType": "HTML",
                    "content": f"""
                    <p>You requested a password reset. Click the link below:</p>
                    <p><a href="{await self.get_ssr_link(user_email)}">Reset Password</a></p>
                    """
                },
                "toRecipients": [{"emailAddress": {"address": user_email}}]
            }
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(graph_url, json=message, headers=headers)
                return response.status_code == 202
            except Exception as e:
                print(f"Error sending email: {e}")
                return False
    
    async def get_user_info(self, user_email: str) -> Optional[Dict]:
        """Get user information from Graph API."""
        token = await self.get_access_token()
        
        if not token:
            return None
        
        graph_url = f"https://graph.microsoft.com/v1.0/users/{user_email}"
        headers = {"Authorization": f"Bearer {token}"}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(graph_url, headers=headers)
                if response.status_code == 200:
                    return response.json()
                return None
            except Exception as e:
                print(f"Error getting user info: {e}")
                return None

