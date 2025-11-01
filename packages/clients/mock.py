"""Mock clients for demo/testing."""
import sys
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
import random
import string

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "apps" / "api"))

from db import get_database
from db.models import Ticket


class MockTicketClient:
    """Mock ticket client that stores tickets in MongoDB."""
    
    def __init__(self, system: str = "servicenow"):
        self.system = system
    
    def _generate_id(self) -> str:
        """Generate mock ticket ID."""
        if self.system == "servicenow":
            return f"INC{random.randint(1000000, 9999999)}"
        elif self.system == "jira":
            return f"IT-{random.randint(100, 999)}"
        else:
            return f"TICKET-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"
    
    async def create_ticket(
        self,
        short_desc: str,
        description: str,
        priority: str = "3",
        user: str = None,
        category: Optional[str] = None
    ) -> str:
        """Create a mock ticket."""
        database = await get_database()
        
        external_id = self._generate_id()
        
        ticket = Ticket(
            system=self.system,
            externalId=external_id,
            shortDesc=short_desc,
            description=description,
            status="New",
            priority=priority,
            openedBy=user or "demo@acme.com"
        )
        
        ticket_dict = ticket.model_dump(by_alias=True, exclude={"id"})
        await database.tickets.insert_one(ticket_dict)
        
        return external_id
    
    async def get_ticket(self, external_id: str) -> Dict:
        """Get mock ticket."""
        database = await get_database()
        
        ticket_doc = await database.tickets.find_one({
            "system": self.system,
            "externalId": external_id
        })
        
        if not ticket_doc:
            # Return a mock ticket even if not found
            return {
                "externalId": external_id,
                "shortDesc": "Sample Ticket",
                "description": "This is a mock ticket",
                "status": "In Progress",
                "priority": "3",
                "openedBy": "demo@acme.com",
                "assignedTo": None,
                "createdAt": datetime.utcnow().isoformat(),
                "updatedAt": datetime.utcnow().isoformat()
            }
        
        return {
            "externalId": ticket_doc.get("externalId"),
            "shortDesc": ticket_doc.get("shortDesc"),
            "description": ticket_doc.get("description"),
            "status": ticket_doc.get("status", "New"),
            "priority": ticket_doc.get("priority", "3"),
            "openedBy": ticket_doc.get("openedBy"),
            "assignedTo": ticket_doc.get("assignedTo"),
            "createdAt": ticket_doc.get("createdAt").isoformat() if ticket_doc.get("createdAt") else None,
            "updatedAt": ticket_doc.get("updatedAt").isoformat() if ticket_doc.get("updatedAt") else None
        }
    
    async def update_ticket(self, external_id: str, updates: Dict) -> bool:
        """Update mock ticket."""
        database = await get_database()
        
        result = await database.tickets.update_one(
            {"system": self.system, "externalId": external_id},
            {"$set": updates}
        )
        
        return result.modified_count > 0


class MockM365Client:
    """Mock M365 client for demo."""
    
    async def get_ssr_link(self, user_email: str) -> str:
        """Return mock password reset link."""
        return f"https://account.activedirectory.windowsazure.com/ChangePassword.aspx?email={user_email}&token=MOCK_TOKEN_{user_email.replace('@', '_at_')}"
    
    async def send_password_reset_email(self, user_email: str) -> bool:
        """Mock sending email."""
        print(f"[MOCK] Would send password reset email to {user_email}")
        return True
    
    async def get_user_info(self, user_email: str) -> Optional[Dict]:
        """Return mock user info."""
        return {
            "mail": user_email,
            "displayName": user_email.split("@")[0].title(),
            "userPrincipalName": user_email,
            "id": f"mock-id-{user_email}"
        }

