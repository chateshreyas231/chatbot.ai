"""Client adapters for external systems."""
from .ticket_system import TicketSystem, TicketSystemAdapter
from .servicenow import ServiceNowClient
from .jira import JiraClient
from .m365 import M365Client
from .mock import MockTicketClient, MockM365Client

__all__ = [
    "TicketSystem",
    "TicketSystemAdapter",
    "ServiceNowClient",
    "JiraClient",
    "M365Client",
    "MockTicketClient",
    "MockM365Client"
]

