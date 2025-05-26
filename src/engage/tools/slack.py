from agno import Tool
from agno.tools.slack import SlackClient, send_message, create_channel
from typing import Dict, Any, List, Optional
from datetime import datetime
from .base import BaseIntegration

class SlackIntegration(BaseIntegration):
    """Slack integration for team communication using agno Slack tools."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.bot_token = config.get("bot_token")
        self.default_channel = config.get("default_channel", "#security")
        
        # Initialize agno SlackClient
        self.slack_client = SlackClient(
            token=self.bot_token,
            default_channel=self.default_channel
        )
    
    def test_connection(self) -> bool:
        """Test Slack API connection using agno client."""
        try:
            return self.slack_client.test_connection()
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
    Send notification to security team via Slack using agno.
    
    Args:
        message: Message content
        channel: Slack channel (defaults to security channel)
        urgency: Urgency level (low, normal, high, critical)
        mention_users: List of users to mention
    
    Returns:
        Message send confirmation from agno Slack tool
    """
    # Format message with mentions
    if mention_users:
        mentions = " ".join([f"<@{user}>" for user in mention_users])
        message = f"{mentions}\n{message}"
    
    # Add urgency indicators
    if urgency in ["high", "critical"]:
        message = f"🚨 **{urgency.upper()}** 🚨\n{message}"
    
    # Use agno's send_message tool
    result = send_message(
        message=message,
        channel=channel or "#security"
    )
    
    # Enhance result with engage-specific metadata
    result.update({
        "urgency": urgency,
        "mentioned_users": mention_users or [],
        "engage_timestamp": datetime.now().isoformat()
    })
    
    return result

@Tool
def create_incident_channel(
    incident_id: str,
    initial_message: str,
    team_members: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Create a dedicated Slack channel for incident response using agno.
    
    Args:
        incident_id: Unique incident identifier
        initial_message: Initial message for the channel
        team_members: Team members to invite
    
    Returns:
        Channel creation confirmation from agno Slack tool
    """
    channel_name = f"incident-{incident_id.lower()}"
    
    # Use agno's create_channel tool
    result = create_channel(
        name=channel_name,
        purpose=f"Incident response for {incident_id}",
        is_private=False
    )
    
    # Send initial message to the new channel
    if result.get("ok"):
        send_message(
            message=initial_message,
            channel=result.get("channel", {}).get("id")
        )
        
        # Invite team members if specified
        if team_members:
            # Note: You might need to use agno's invite_users tool if available
            pass
    
    # Enhance result with engage-specific metadata
    result.update({
        "incident_id": incident_id,
        "initial_message": initial_message,
        "team_members": team_members or [],
        "engage_created": datetime.now().isoformat()
    })
    
    return result

@Tool
def request_human_input(
    question: str,
    context: str,
    urgency: str = "normal",
    timeout_hours: int = 4,
    channel: Optional[str] = None
) -> Dict[str, Any]:
    """
    Request human input/decision via Slack using agno.
    
    Args:
        question: Question to ask
        context: Context information
        urgency: Urgency level
        timeout_hours: Hours to wait for response
        channel: Channel to send request to
    
    Returns:
        Request confirmation (actual response would come via callback)
    """
    request_id = f"req_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    message = f"""
🤖 **Human Input Required** (ID: {request_id})

**Question:** {question}

**Context:** {context}

**Urgency:** {urgency}
**Response needed within:** {timeout_hours} hours

Please respond with your decision/input and reference ID: {request_id}
    """
    
    # Use agno's send_message tool
    result = send_message(
        message=message,
        channel=channel or "#security"
    )
    
    # Enhance result with engage-specific metadata
    result.update({
        "request_id": request_id,
        "question": question,
        "context": context,
        "urgency": urgency,
        "timeout_hours": timeout_hours,
        "engage_requested": datetime.now().isoformat()
    })
    
    return result

@Tool
def send_security_alert(
    alert_title: str,
    alert_details: str,
    severity: str = "medium",
    source_system: Optional[str] = None,
    channel: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send formatted security alert via Slack using agno.
    
    Args:
        alert_title: Title of the security alert
        alert_details: Detailed information about the alert
        severity: Alert severity (low, medium, high, critical)
        source_system: System that generated the alert
        channel: Channel to send alert to
    
    Returns:
        Alert send confirmation
    """
    # Format security alert message
    severity_emoji = {
        "low": "🟡",
        "medium": "🟠", 
        "high": "🔴",
        "critical": "🚨"
    }.get(severity, "⚪")
    
    message = f"""
{severity_emoji} **SECURITY ALERT** {severity_emoji}

**Title:** {alert_title}
**Severity:** {severity.upper()}
{f"**Source:** {source_system}" if source_system else ""}

**Details:**
{alert_details}

**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
    """
    
    # Use agno's send_message tool
    result = send_message(
        message=message,
        channel=channel or "#security"
    )
    
    # Enhance result with engage-specific metadata
    result.update({
        "alert_title": alert_title,
        "severity": severity,
        "source_system": source_system,
        "engage_alert_sent": datetime.now().isoformat()
    })
    
    return result