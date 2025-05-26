from agno import Tool
from typing import Dict, Any, List, Optional
from datetime import datetime
from .base import BaseIntegration

class SlackIntegration(BaseIntegration):
    """Slack integration for team communication."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.bot_token = config.get("bot_token")
        self.default_channel = config.get("default_channel", "#security")
    
    def test_connection(self) -> bool:
        """Test Slack API connection."""
        try:
            # Mock test - replace with actual API call
            return True
        except Exception as e:
            self.logger.error(f"Slack connection test failed: {e}")
            return False

@Tool
def notify_team(
    message: str,
    channel: Optional[str] = None,
    urgency: str = "normal",
    mention_users: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Send notification to security team via Slack.
    
    Args:
        message: Message content
        channel: Slack channel (defaults to security channel)
        urgency: Urgency level (low, normal, high, critical)
        mention_users: List of users to mention
    
    Returns:
        Message send confirmation
    """
    if mention_users:
        mentions = " ".join([f"<@{user}>" for user in mention_users])
        message = f"{mentions}\n{message}"
    
    if urgency in ["high", "critical"]:
        message = f"🚨 **{urgency.upper()}** 🚨\n{message}"
    
    return {
        "status": "sent",
        "channel": channel or "#security",
        "message": message,
        "urgency": urgency,
        "timestamp": datetime.now().isoformat(),
        "message_id": f"msg_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    }

@Tool
def create_incident_channel(
    incident_id: str,
    initial_message: str,
    team_members: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Create a dedicated Slack channel for incident response.
    
    Args:
        incident_id: Unique incident identifier
        initial_message: Initial message for the channel
        team_members: Team members to invite
    
    Returns:
        Channel creation confirmation
    """
    channel_name = f"incident-{incident_id.lower()}"
    
    return {
        "status": "created",
        "channel_name": channel_name,
        "channel_id": f"C{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "initial_message": initial_message,
        "members_invited": team_members or [],
        "created": datetime.now().isoformat()
    }

@Tool
def request_human_input(
    question: str,
    context: str,
    urgency: str = "normal",
    timeout_hours: int = 4
) -> Dict[str, Any]:
    """
    Request human input/decision via Slack.
    
    Args:
        question: Question to ask
        context: Context information
        urgency: Urgency level
        timeout_hours: Hours to wait for response
    
    Returns:
        Request confirmation (actual response would come via callback)
    """
    message = f"""
🤖 **Human Input Required**

**Question:** {question}

**Context:** {context}

**Urgency:** {urgency}
**Response needed within:** {timeout_hours} hours

Please respond with your decision/input.
    """
    
    return {
        "status": "requested",
        "question": question,
        "urgency": urgency,
        "timeout": timeout_hours,
        "request_id": f"req_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "message": message
    }