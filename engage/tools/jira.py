from agno import Tool
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from agno.tools.jira import JiraTools


class JiraIntegration(JiraTools):
    """JIRA integration for ticket management, extending agno's JiraTools."""
    
    def __init__(self, config: Dict[str, Any]):
        # Extract JIRA-specific config and pass to parent JiraTools
        server = config.get("jira_url")
        username = config.get("jira_username")
        api_token = config.get("jira_api_token")
        
        # Initialize parent JiraTools class
        super().__init__(
            server=server,
            username=username,
            token=api_token
        )
        
        # Store additional engage-specific config
        self.config = config
        self.project_key = config.get("jira_project_key", "SEC")
        self.default_issue_type = config.get("jira_default_issue_type", "Task")
    
    def create_security_ticket(
        self,
        summary: str,
        description: str,
        priority: str = "Medium",
        alert_id: str = None,
        assignee: str = None,
        issue_type: str = None
    ) -> Dict[str, Any]:
        """
        Create a security incident ticket in JIRA.
        
        Args:
            summary: Brief summary of the incident
            description: Detailed description with findings
            priority: Priority level (Low, Medium, High, Critical)
            alert_id: Associated alert ID for tracking
            assignee: Optional assignee for the ticket
            issue_type: JIRA issue type (uses default if not provided)
        
        Returns:
            Created ticket information from JIRA API
        """
        # Enhance description with alert context if provided
        enhanced_description = description
        if alert_id:
            enhanced_description = f"Alert ID: {alert_id}\n\n{description}"
        
        # Prepare issue fields
        issue_fields = {
            "project": {"key": self.project_key},
            "summary": summary,
            "description": enhanced_description,
            "issuetype": {"name": issue_type or self.default_issue_type},
            "priority": {"name": priority}
        }
        
        # Add assignee if provided
        if assignee:
            issue_fields["assignee"] = {"name": assignee}
        
        # Add custom labels for security incidents
        labels = ["security", "incident"]
        if alert_id:
            labels.append(f"alert-{alert_id}")
        issue_fields["labels"] = labels
        
        # Use parent class create_issue method
        result = self.create_issue(fields=issue_fields)
        
        # Enhance result with engage-specific metadata
        if result.get("key"):
            result.update({
                "alert_id": alert_id,
                "engage_created": datetime.now().isoformat(),
                "url": f"{self.server}/browse/{result['key']}"
            })
        
        return result
    
    def update_ticket_with_findings(
        self,
        ticket_id: str,
        findings: str,
        status: Optional[str] = None,
        add_labels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Update a JIRA ticket with investigation findings.
        
        Args:
            ticket_id: JIRA ticket ID/key
            findings: Investigation findings to add
            status: New status for the ticket
            add_labels: Labels to add to the ticket
        
        Returns:
            Update confirmation from JIRA API
        """
        results = {}
        
        # Add comment with findings using parent class method
        comment_result = self.add_comment(
            issue_key=ticket_id,
            comment=f"**Investigation Findings ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})**\n\n{findings}"
        )
        results["comment_added"] = comment_result
        
        # Update status if provided
        if status:
            try:
                transition_result = self.transition_issue(
                    issue_key=ticket_id,
                    transition=status
                )
                results["status_updated"] = transition_result
                results["new_status"] = status
            except Exception as e:
                results["status_update_error"] = str(e)
        
        # Add labels if provided
        if add_labels:
            try:
                # Get current issue to append labels
                issue = self.get_issue(ticket_id)
                current_labels = issue.get("fields", {}).get("labels", [])
                updated_labels = list(set(current_labels + add_labels))
                
                update_result = self.update_issue(
                    issue_key=ticket_id,
                    fields={"labels": updated_labels}
                )
                results["labels_added"] = add_labels
                results["labels_update"] = update_result
            except Exception as e:
                results["labels_update_error"] = str(e)
        
        results.update({
            "ticket_id": ticket_id,
            "findings_added": bool(comment_result),
            "updated": datetime.now().isoformat()
        })
        
        return results
    
    def get_stale_tickets(
        self,
        hours_old: int = 24,
        status_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get security tickets that haven't been updated recently.
        
        Args:
            hours_old: Consider tickets stale after this many hours
            status_filter: Filter by specific status
        
        Returns:
            List of stale tickets from JIRA API
        """
        # Calculate cutoff time
        cutoff_time = datetime.now() - timedelta(hours=hours_old)
        cutoff_str = cutoff_time.strftime('%Y-%m-%d %H:%M')
        
        # Build JQL query
        jql_parts = [
            f"project = {self.project_key}",
            "labels in (security, incident)",
            f"updated < '{cutoff_str}'"
        ]
        
        if status_filter:
            jql_parts.append(f"status = '{status_filter}'")
        else:
            # Exclude resolved/closed tickets by default
            jql_parts.append("status not in (Resolved, Closed, Done)")
        
        jql = " AND ".join(jql_parts)
        
        try:
            # Search for stale tickets using parent class method
            search_result = self.search_issues(
                jql=jql,
                fields=["summary", "status", "assignee", "updated", "priority", "labels"]
            )
            
            stale_tickets = []
            for issue in search_result.get("issues", []):
                fields = issue.get("fields", {})
                updated_str = fields.get("updated", "")
                
                # Calculate age in hours
                try:
                    updated_time = datetime.fromisoformat(updated_str.replace('Z', '+00:00'))
                    age_hours = (datetime.now() - updated_time.replace(tzinfo=None)).total_seconds() / 3600
                except:
                    age_hours = hours_old + 1  # Assume it's stale if we can't parse
                
                stale_tickets.append({
                    "ticket_id": issue["key"],
                    "summary": fields.get("summary", ""),
                    "status": fields.get("status", {}).get("name", ""),
                    "assignee": fields.get("assignee", {}).get("displayName", "Unassigned") if fields.get("assignee") else "Unassigned",
                    "last_updated": updated_str,
                    "priority": fields.get("priority", {}).get("name", ""),
                    "age_hours": round(age_hours, 1),
                    "labels": fields.get("labels", [])
                })
            
            return stale_tickets
            
        except Exception as e:
            # Return empty list with error info if API fails
            return [{
                "error": f"Failed to retrieve stale tickets: {str(e)}",
                "query_attempted": jql,
                "timestamp": datetime.now().isoformat()
            }]
    
    def get_security_ticket_details(self, ticket_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific security ticket.
        
        Args:
            ticket_id: JIRA ticket ID/key
        
        Returns:
            Detailed ticket information with security-specific enhancements
        """
        try:
            # Use parent class get_issue method
            issue = self.get_issue(ticket_id)
            fields = issue.get("fields", {})
            
            # Extract security-specific information
            labels = fields.get("labels", [])
            alert_id = None
            for label in labels:
                if label.startswith("alert-"):
                    alert_id = label.replace("alert-", "")
                    break
            
            return {
                "ticket_id": issue["key"],
                "summary": fields.get("summary", ""),
                "description": fields.get("description", ""),
                "status": fields.get("status", {}).get("name", ""),
                "priority": fields.get("priority", {}).get("name", ""),
                "assignee": fields.get("assignee", {}).get("displayName", "Unassigned") if fields.get("assignee") else "Unassigned",
                "reporter": fields.get("reporter", {}).get("displayName", "") if fields.get("reporter") else "",
                "created": fields.get("created", ""),
                "updated": fields.get("updated", ""),
                "labels": labels,
                "alert_id": alert_id,
                "is_security_ticket": "security" in labels,
                "is_incident": "incident" in labels,
                "components": [c.get("name", "") for c in fields.get("components", [])],
                "project": fields.get("project", {}).get("key", ""),
                "issue_type": fields.get("issuetype", {}).get("name", ""),
                "url": f"{self.server}/browse/{issue['key']}"
            }
            
        except Exception as e:
            return {
                "ticket_id": ticket_id,
                "error": f"Failed to retrieve ticket: {str(e)}",
                "retrieved": datetime.now().isoformat()
            }


# Tool functions that use the JiraIntegration class
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
    # This would typically get config from a global config manager
    # For now, using placeholder config
    config = {
        "url": "https://your-jira.com",
        "username": "api-user",
        "api_token": "your-token",
        "project_key": "SEC"
    }
    
    jira = JiraIntegration(config)
    return jira.create_security_ticket(
        summary=summary,
        description=description,
        priority=priority,
        alert_id=alert_id,
        assignee=assignee
    )


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
    config = {
        "url": "https://your-jira.com",
        "username": "api-user", 
        "api_token": "your-token",
        "project_key": "SEC"
    }
    
    jira = JiraIntegration(config)
    return jira.update_ticket_with_findings(
        ticket_id=ticket_id,
        findings=findings,
        status=status,
        add_labels=add_labels
    )


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
    config = {
        "url": "https://your-jira.com",
        "username": "api-user",
        "api_token": "your-token", 
        "project_key": "SEC"
    }
    
    jira = JiraIntegration(config)
    return jira.get_stale_tickets(
        hours_old=hours_old,
        status_filter=status_filter
    )