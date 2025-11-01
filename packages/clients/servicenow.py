"""ServiceNow client."""
import httpx
from typing import Dict, Optional
import sys
from pathlib import Path
import base64

# Add apps/api to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "apps" / "api"))

from config import settings


class ServiceNowClient:
    """ServiceNow REST API client."""
    
    def __init__(
        self,
        instance_url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None
    ):
        self.instance_url = instance_url or settings.servicenow_instance_url
        self.username = username or settings.servicenow_username
        self.password = password or settings.servicenow_password
        
        if not self.instance_url:
            raise ValueError("ServiceNow instance URL required")
        
        # Basic auth
        credentials = f"{self.username}:{self.password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        self.headers = {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    async def create_ticket(
        self,
        short_desc: str,
        description: str,
        priority: str = "3",
        user: str = None,
        category: Optional[str] = None
    ) -> str:
        """Create a ServiceNow incident."""
        url = f"{self.instance_url}/api/now/table/incident"
        
        payload = {
            "short_description": short_desc,
            "description": description,
            "priority": priority,
            "caller_id": user or self.username,
            "category": category or "inquiry"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            # Return sys_id (ServiceNow internal ID) or number
            return data["result"].get("number") or data["result"].get("sys_id")
    
    async def get_ticket(self, external_id: str) -> Dict:
        """Get ticket by number or sys_id."""
        # Try as number first
        url = f"{self.instance_url}/api/now/table/incident"
        params = {"number": external_id}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                if data["result"]:
                    result = data["result"][0]
                    return {
                        "externalId": result.get("number"),
                        "sysId": result.get("sys_id"),
                        "shortDesc": result.get("short_description"),
                        "description": result.get("description"),
                        "status": result.get("state"),
                        "priority": result.get("priority"),
                        "openedBy": result.get("caller_id", {}).get("value"),
                        "assignedTo": result.get("assigned_to", {}).get("value") if result.get("assigned_to") else None,
                        "createdAt": result.get("opened_at"),
                        "updatedAt": result.get("sys_updated_on")
                    }
            
            # Try as sys_id
            url = f"{self.instance_url}/api/now/table/incident/{external_id}"
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            result = response.json()["result"]
            
            return {
                "externalId": result.get("number"),
                "sysId": result.get("sys_id"),
                "shortDesc": result.get("short_description"),
                "description": result.get("description"),
                "status": result.get("state"),
                "priority": result.get("priority"),
                "openedBy": result.get("caller_id", {}).get("value"),
                "assignedTo": result.get("assigned_to", {}).get("value") if result.get("assigned_to") else None,
                "createdAt": result.get("opened_at"),
                "updatedAt": result.get("sys_updated_on")
            }
    
    async def update_ticket(self, external_id: str, updates: Dict) -> bool:
        """Update ticket."""
        # First get sys_id if needed
        ticket = await self.get_ticket(external_id)
        sys_id = ticket.get("sysId") or external_id
        
        url = f"{self.instance_url}/api/now/table/incident/{sys_id}"
        
        async with httpx.AsyncClient() as client:
            response = await client.patch(url, json=updates, headers=self.headers)
            response.raise_for_status()
            return True

