from agno import Tool
from typing import Dict, Any, List, Optional
from datetime import datetime
from .base import BaseIntegration

class JiraIntegration(BaseIntegration):
    """JIRA integration for ticket management."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.url = config.get("url")
        self.username = config.get("username")
        self.api_token = config.get("api_token")
    
    def test_connection(self) -> bool:
        """Test JIRA API connection."""
        try:
            # Mock test - replace with actual API call
            return True
        except Exception as e:
            self.logger.error(f"JIRA connection test failed: {e}")
            return False

@Tool
def create_security_ticket(
    summary: str,
    description: str,
    priority: str = "Medium",
    alert_id: str = None,
    assignee: str = None
) -> Dict[str, Any]:
    """
    Create a security incident ticket in JIRA.
    
    Args:
        summary: Brief summary of the incident
        description: Detailed description with findings
        priority: Priority level (Low, Medium, High, Critical)
        alert_id: Associated alert ID for tracking
        assignee: Optional assignee for the ticket
    
    Returns:
        Created ticket information
    """
    ticket_id = f"SEC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    return {
        "ticket_id": ticket_id,
        "summary": summary,
        "description": description,
        "priority": priority,
        "status": "Open",
        "assignee": assignee,
        "alert_id": alert_id,
        "url": f"https://your-jira.com/browse/{ticket_id}",
        "created": datetime.now().isoformat()
    }

@Tool
def update_ticket_with_findings(
    ticket_id: str,
    findings: str,
    status: Optional[str] = None,
    add_labels: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Update a JIRA ticket with investigation findings.
    
    Args:
        ticket_id: JIRA ticket ID
        findings: Investigation findings to add
        status: New status for the ticket
        add_labels: Labels to add to the ticket
    
    Returns:
        Update confirmation
    """
    return {
        "ticket_id": ticket_id,
        "findings_added": True,
        "status_updated": status is not None,
        "new_status": status,
        "labels_added": add_labels or [],
        "updated": datetime.now().isoformat()
    }

@Tool
def get_stale_tickets(
    hours_old: int = 24,
    status_filter: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get security tickets that haven't been updated recently.
    
    Args:
        hours_old: Consider tickets stale after this many hours
        status_filter: Filter by specific status
    
    Returns:
        List of stale tickets
    """
    # Mock implementation
    return [
        {
            "ticket_id": "SEC-20241201120000",
            "summary": "Suspicious Network Activity",
            "status": "In Progress",
            "assignee": "john.doe",
            "last_updated": (datetime.now() - timedelta(hours=25)).isoformat(),
            "priority": "High",
            "age_hours": 25
        }
    ]