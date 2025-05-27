from agno import Tool
from agno.tools.slack import SlackClient, send_message, create_channel
from typing import Dict, Any, List, Optional
from datetime import datetime


class SlackIntegration(SlackClient):
    """Slack integration for team communication, extending agno's SlackClient."""
    
    def __init__(self, config: Dict[str, Any]):
        # Extract Slack-specific config and pass to parent SlackClient
        bot_token = config.get("bot_token")
        default_channel = config.get("default_channel", "#security")
        
        # Initialize parent SlackClient class
        super().__init__(
            token=bot_token,
            default_channel=default_channel
        )
        
        # Store additional engage-specific config
        self.config = config
        self.security_channel = config.get("security_channel", "#security")
        self.incident_channel_prefix = config.get("incident_channel_prefix", "incident-")
        self.escalation_users = config.get("escalation_users", [])
    
    def notify_security_team(
        self,
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
            Message send confirmation from agno Slack client
        """
        # Format message with mentions
        formatted_message = message
        if mention_users:
            mentions = " ".join([f"<@{user}>" for user in mention_users])
            formatted_message = f"{mentions}\n{message}"
        
        # Add urgency indicators
        if urgency in ["high", "critical"]:
            formatted_message = f"🚨 **{urgency.upper()}** 🚨\n{formatted_message}"
        elif urgency == "low":
            formatted_message = f"ℹ️ **{urgency.upper()}** ℹ️\n{formatted_message}"
        
        # Use parent class send_message method
        result = self.send_message(
            message=formatted_message,
            channel=channel or self.security_channel
        )
        
        # Enhance result with engage-specific metadata
        result.update({
            "urgency": urgency,
            "mentioned_users": mention_users or [],
            "engage_timestamp": datetime.now().isoformat(),
            "message_type": "security_notification"
        })
        
        return result
    
    def create_incident_channel(
        self,
        incident_id: str,
        initial_message: str,
        team_members: Optional[List[str]] = None,
        is_private: bool = False
    ) -> Dict[str, Any]:
        """
        Create a dedicated Slack channel for incident response.
        
        Args:
            incident_id: Unique incident identifier
            initial_message: Initial message for the channel
            team_members: Team members to invite
            is_private: Whether to create a private channel
        
        Returns:
            Channel creation confirmation from agno Slack client
        """
        channel_name = f"{self.incident_channel_prefix}{incident_id.lower()}"
        
        # Use parent class create_channel method
        result = self.create_channel(
            name=channel_name,
            purpose=f"Incident response for {incident_id}",
            is_private=is_private
        )
        
        # Send initial message to the new channel
        if result.get("ok") and result.get("channel"):
            channel_id = result["channel"].get("id")
            if channel_id:
                self.send_message(
                    message=initial_message,
                    channel=channel_id
                )
                
                # Invite team members if specified and if we have invite capability
                if team_members:
                    try:
                        for member in team_members:
                            self.invite_user_to_channel(channel_id, member)
                    except Exception as e:
                        result["invite_warnings"] = f"Could not invite some users: {str(e)}"
        
        # Enhance result with engage-specific metadata
        result.update({
            "incident_id": incident_id,
            "initial_message": initial_message,
            "team_members": team_members or [],
            "engage_created": datetime.now().isoformat(),
            "channel_type": "incident_response"
        })
        
        return result
    
    def request_human_input(
        self,
        question: str,
        context: str,
        urgency: str = "normal",
        timeout_hours: int = 4,
        channel: Optional[str] = None,
        escalate_to: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Request human input/decision via Slack.
        
        Args:
            question: Question to ask
            context: Context information
            urgency: Urgency level
            timeout_hours: Hours to wait for response
            channel: Channel to send request to
            escalate_to: Users to escalate to if no response
        
        Returns:
            Request confirmation (actual response would come via callback)
        """
        request_id = f"req_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Auto-escalate to configured users for high urgency
        if urgency in ["high", "critical"] and not escalate_to:
            escalate_to = self.escalation_users
        
        message = f"""
🤖 **Human Input Required** (ID: {request_id})

**Question:** {question}

**Context:** {context}

**Urgency:** {urgency}
**Response needed within:** {timeout_hours} hours

Please respond with your decision/input and reference ID: {request_id}
        """
        
        # Add escalation mentions for urgent requests
        if escalate_to:
            mentions = " ".join([f"<@{user}>" for user in escalate_to])
            message = f"{mentions}\n{message}"
        
        # Use parent class send_message method
        result = self.send_message(
            message=message,
            channel=channel or self.security_channel
        )
        
        # Enhance result with engage-specific metadata
        result.update({
            "request_id": request_id,
            "question": question,
            "context": context,
            "urgency": urgency,
            "timeout_hours": timeout_hours,
            "escalated_to": escalate_to or [],
            "engage_requested": datetime.now().isoformat(),
            "message_type": "human_input_request"
        })
        
        return result
    
    def send_security_alert(
        self,
        alert_title: str,
        alert_details: str,
        severity: str = "medium",
        source_system: Optional[str] = None,
        channel: Optional[str] = None,
        alert_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send formatted security alert via Slack.
        
        Args:
            alert_title: Title of the security alert
            alert_details: Detailed information about the alert
            severity: Alert severity (low, medium, high, critical)
            source_system: System that generated the alert
            channel: Channel to send alert to
            alert_id: Unique alert identifier
        
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
{f"**Alert ID:** {alert_id}" if alert_id else ""}
{f"**Source:** {source_system}" if source_system else ""}

**Details:**
{alert_details}

**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
        """
        
        # Auto-mention escalation users for high/critical alerts
        if severity in ["high", "critical"] and self.escalation_users:
            mentions = " ".join([f"<@{user}>" for user in self.escalation_users])
            message = f"{mentions}\n{message}"
        
        # Use parent class send_message method
        result = self.send_message(
            message=message,
            channel=channel or self.security_channel
        )
        
        # Enhance result with engage-specific metadata
        result.update({
            "alert_title": alert_title,
            "alert_id": alert_id,
            "severity": severity,
            "source_system": source_system,
            "engage_alert_sent": datetime.now().isoformat(),
            "message_type": "security_alert",
            "escalated": severity in ["high", "critical"] and bool(self.escalation_users)
        })
        
        return result
    
    def send_investigation_update(
        self,
        incident_id: str,
        update_message: str,
        findings: Optional[str] = None,
        next_steps: Optional[str] = None,
        channel: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send investigation update to incident channel or security team.
        
        Args:
            incident_id: Incident identifier
            update_message: Update message
            findings: Investigation findings
            next_steps: Planned next steps
            channel: Channel to send to (defaults to incident channel)
        
        Returns:
            Message send confirmation
        """
        # Try to determine incident channel if not specified
        if not channel:
            channel = f"#{self.incident_channel_prefix}{incident_id.lower()}"
        
        message = f"""
📋 **Investigation Update - {incident_id}**

{update_message}

{f"**Findings:**\n{findings}\n" if findings else ""}
{f"**Next Steps:**\n{next_steps}\n" if next_steps else ""}

**Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
        """
        
        # Use parent class send_message method
        result = self.send_message(
            message=message,
            channel=channel
        )
        
        # Enhance result with engage-specific metadata
        result.update({
            "incident_id": incident_id,
            "update_type": "investigation_update",
            "has_findings": bool(findings),
            "has_next_steps": bool(next_steps),
            "engage_updated": datetime.now().isoformat()
        })
        
        return result


# Tool functions that use the SlackIntegration class
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
    # This would typically get config from a global config manager
    config = {
        "bot_token": "xoxb-your-token",
        "default_channel": "#security",
        "escalation_users": ["security-lead", "soc-manager"]
    }
    
    slack = SlackIntegration(config)
    return slack.notify_security_team(
        message=message,
        channel=channel,
        urgency=urgency,
        mention_users=mention_users
    )


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
    config = {
        "bot_token": "xoxb-your-token",
        "default_channel": "#security",
        "incident_channel_prefix": "incident-"
    }
    
    slack = SlackIntegration(config)
    return slack.create_incident_channel(
        incident_id=incident_id,
        initial_message=initial_message,
        team_members=team_members
    )


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
    config = {
        "bot_token": "xoxb-your-token",
        "default_channel": "#security",
        "escalation_users": ["security-lead", "soc-manager"]
    }
    
    slack = SlackIntegration(config)
    return slack.request_human_input(
        question=question,
        context=context,
        urgency=urgency,
        timeout_hours=timeout_hours,
        channel=channel
    )


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
    config = {
        "bot_token": "xoxb-your-token",
        "default_channel": "#security",
        "escalation_users": ["security-lead", "soc-manager"]
    }
    
    slack = SlackIntegration(config)
    return slack.send_security_alert(
        alert_title=alert_title,
        alert_details=alert_details,
        severity=severity,
        source_system=source_system,
        channel=channel
    )