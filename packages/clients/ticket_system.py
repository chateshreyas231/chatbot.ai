"""Ticket system interface and adapter."""
from typing import Protocol, Dict, Optional
from datetime import datetime


class TicketSystem(Protocol):
    """Protocol for ticket systems."""
    
    async def create_ticket(
        self,
        short_desc: str,
        description: str,
        priority: str = "3",
        user: str = None,
        category: Optional[str] = None
    ) -> str:
        """Create a ticket and return external ID."""
        ...
    
    async def get_ticket(self, external_id: str) -> Dict:
        """Get ticket by external ID."""
        ...
    
    async def update_ticket(self, external_id: str, updates: Dict) -> bool:
        """Update ticket."""
        ...


class TicketSystemAdapter:
    """Adapter for ticket systems."""
    
    def __init__(self, client: TicketSystem):
        self.client = client
    
    async def create_ticket(self, **kwargs) -> str:
        """Create ticket via client."""
        return await self.client.create_ticket(**kwargs)
    
    async def get_ticket(self, external_id: str) -> Dict:
        """Get ticket via client."""
        return await self.client.get_ticket(external_id)
    
    async def update_ticket(self, external_id: str, updates: Dict) -> bool:
        """Update ticket via client."""
        return await self.client.update_ticket(external_id, updates)

