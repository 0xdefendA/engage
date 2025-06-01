# What?
AI powered SOC agent to activate responses for your security operations center.

# Why?
If you have a security operations center, you know how much time it takes handle the influx of events, investigations and alerts. 
s
From the classic Star Trek; `Engage!` is meant to be your AI agent to help you get more done, more quickly with a simple operating model. 

# How?
Engage is an AI agent with tools to help it
- Gather what you'd like it to react to/assist with (usually SOC alerts)
- A set of tools to help it react to those events
- Markdown playbooks to describe how you'd like the agent to engage

# Examples
Let say you have Chronicle for your SIEM. With Engage you can give it tools and a markdown playbook to:
- Pull new detections
- Summarize the investigation in JIRA
- Ping a user in slack for clarity on the detection
- Ping a security team member in slack to help with the investigation and approve next steps
- Automatically use other tools to help with the investigation, respond, quarantine endpoints, etc

# How to use
Here's an example playbook that simply lists the environment and the tools available to the agent.

```shell 
python engage.py --playbook ./engage/playbooks/test_list_tools.md --environment=test
```

### Output: 

The current day of the week is Sunday.

Here's a detailed list of the tools available to me:

**SIEM:** Chronicle

*   **Description:**  A security information and event management (SIEM) system used for collecting, analyzing, and visualizing security logs and events from various sources.  Allows for threat detection, investigation, and response.
*   **Capabilities:** Log aggregation, threat detection, incident response, compliance reporting.  Specific capabilities depend on the configuration and integrations.


**EDR:** CrowdStrike

*   **Description:** An endpoint detection and response (EDR) solution providing real-time protection and visibility into endpoint activity.  Used to detect and respond to malware and other threats on endpoints (computers, servers, etc.).
*   **Capabilities:** Real-time threat detection, malware analysis, endpoint containment, investigation tools, incident response capabilities.


**Directory System:** Google Workspace/Identity

*   **Description:**  Google's suite of cloud-based productivity and collaboration tools, which includes a directory service managing users, groups, and access controls.
*   **Capabilities:** User and group management, access control lists (ACLs), authentication, authorization, single sign-on (SSO) integration.


**Identity/SSO Provider:** Google SSO

*   **Description:**  Google's single sign-on (SSO) solution, allowing users to access multiple applications with a single set of credentials.
*   **Capabilities:** Centralized authentication, authorization, and user management across multiple applications.


**Cloud Provider:** Google GCP (Google Cloud Platform)

*   **Description:**  Google's suite of cloud computing services.
*   **Capabilities:**  Provides infrastructure (compute, storage, networking), platforms (application development, databases, etc.), and services (machine learning, analytics, etc.).  This is the foundation for many other tools.


**Cloud Security Product:** Google Security Command Center

*   **Description:** Google's centralized security management and monitoring service for GCP resources.
*   **Capabilities:**  Provides a unified view of security posture, threat detection, vulnerability management, and compliance monitoring for GCP assets.


**Ticketing System:** Jira

*   **Description:**  A project and issue tracking software commonly used for managing tasks, bugs, and incidents.
*   **Capabilities:** Issue creation, assignment, tracking, workflow management, reporting.


**Playbooks:** Confluence (in Security Space)

*   **Description:**  A collaboration and knowledge management tool, hosting documentation, including security playbooks (step-by-step guides for handling security incidents).
*   **Capabilities:** Document storage, collaboration, knowledge base, and process documentation.


**Important Slack Channels:** #security-alerts, #security-operations, #security-incidents

*   **Description:**  Communication channels within Slack for security-related communication and collaboration.
*   **Capabilities:** Real-time communication, alerts, information sharing, collaboration.

This inventory shows a comprehensive set of tools covering different aspects of security operations, from detection and response to incident management and collaboration.  The integration between these tools is crucial for effective security.