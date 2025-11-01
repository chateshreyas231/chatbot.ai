"""Client adapters for external systems."""
from .ticket_system import TicketSystem, TicketSystemAdapter
from .servicenow import ServiceNowClient
from .mock import MockTicketClient, MockM365Client

# Optional imports - only if installed
try:
    from .m365 import M365Client
except ImportError:
    # M365 not installed (missing msal), skip it
    M365Client = None

try:
    from .jira import JiraClient
except ImportError:
    # Jira not installed, skip it
    JiraClient = None

# Build __all__ based on what's available
__all__ = [
    "TicketSystem",
    "TicketSystemAdapter",
    "ServiceNowClient",
    "MockTicketClient",
    "MockM365Client"
]

if JiraClient is not None:
    __all__.append("JiraClient")

if M365Client is not None:
    __all__.append("M365Client")

