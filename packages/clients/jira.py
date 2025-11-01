"""Jira client."""
try:
    from jira import JIRA
    JIRA_AVAILABLE = True
except ImportError:
    JIRA_AVAILABLE = False
    JIRA = None

from typing import Dict, Optional
import sys
from pathlib import Path

# Add apps/api to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "apps" / "api"))

from config import settings


class JiraClient:
    """Jira REST API client."""
    
    def __init__(
        self,
        server_url: Optional[str] = None,
        email: Optional[str] = None,
        api_token: Optional[str] = None
    ):
        if not JIRA_AVAILABLE:
            raise ImportError("Jira package not installed. Install with: pip install jira")
        
        self.server_url = server_url or settings.jira_server_url
        self.email = email or settings.jira_email
        self.api_token = api_token or settings.jira_api_token
        
        if not all([self.server_url, self.email, self.api_token]):
            raise ValueError("Jira server URL, email, and API token required")
        
        self.client = JIRA(
            server=self.server_url,
            basic_auth=(self.email, self.api_token)
        )
    
    async def create_ticket(
        self,
        short_desc: str,
        description: str,
        priority: str = "3",
        user: str = None,
        category: Optional[str] = None
    ) -> str:
        """Create a Jira issue."""
        # Map priority
        priority_map = {"1": "Highest", "2": "High", "3": "Medium", "4": "Low", "5": "Lowest"}
        jira_priority = priority_map.get(priority, "Medium")
        
        issue_dict = {
            "project": {"key": "IT"},  # Default project, should be configurable
            "summary": short_desc,
            "description": description,
            "issuetype": {"name": "Task"},
            "priority": {"name": jira_priority}
        }
        
        new_issue = self.client.create_issue(fields=issue_dict)
        return new_issue.key  # Returns like "IT-123"
    
    async def get_ticket(self, external_id: str) -> Dict:
        """Get ticket by key (e.g., IT-123)."""
        issue = self.client.issue(external_id)
        
        return {
            "externalId": issue.key,
            "shortDesc": issue.fields.summary,
            "description": issue.fields.description or "",
            "status": issue.fields.status.name,
            "priority": issue.fields.priority.name if issue.fields.priority else "Medium",
            "openedBy": issue.fields.reporter.emailAddress if issue.fields.reporter else None,
            "assignedTo": issue.fields.assignee.emailAddress if issue.fields.assignee else None,
            "createdAt": issue.fields.created,
            "updatedAt": issue.fields.updated
        }
    
    async def update_ticket(self, external_id: str, updates: Dict) -> bool:
        """Update ticket."""
        issue = self.client.issue(external_id)
        
        # Map updates to Jira fields
        fields = {}
        if "shortDesc" in updates:
            fields["summary"] = updates["shortDesc"]
        if "description" in updates:
            fields["description"] = updates["description"]
        if "priority" in updates:
            fields["priority"] = {"name": updates["priority"]}
        
        issue.update(fields=fields)
        return True

