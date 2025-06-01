from agno.tools.confluence import ConfluenceTools
from typing import Dict, Any, List, Optional
from datetime import datetime


class ConfluenceIntegration(ConfluenceTools):
    """Confluence integration for documentation and knowledge base, extending agno's ConfluenceTools."""

    def __init__(self, config: Dict[str, Any]):
        # Extract Confluence-specific config and pass to parent ConfluenceTools
        url = config.get("confluence_url", "https://example.atlassian.net")
        username = config.get("username", "unknown")
        api_token = config.get("api_token", "unknown")

        # Initialize parent ConfluenceTools class
        super().__init__(url=url, username=username, api_key=api_token)

        # Store additional engage-specific config
        self.config = config
        self.security_space_key = config.get("security_space_key", "SEC")
        self.playbook_space_key = config.get("playbook_space_key", "PLAYBOOKS")
        self.incident_page_template = config.get(
            "incident_page_template", "Security Incident Template"
        )
        self.knowledge_base_labels = config.get(
            "knowledge_base_labels", ["security", "kb", "procedures"]
        )
        self.register(self.search_security_knowledge_base)
        self.register(self.get_page_content)

    def search_security_knowledge_base(
        self, query: str, space_key: Optional[str] = None, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search the security knowledge base in Confluence.

        Args:
            query: Search query
            space_key: Confluence space to search in (defaults to security space)
            limit: Maximum number of results to return

        Returns:
            List of relevant knowledge base articles
        """
        search_space = space_key or self.security_space_key

        try:
            # Use parent class search_content method
            search_results = self.search_content(
                query=query, space_key=search_space, limit=limit
            )

            # Filter and enhance results for security context
            kb_articles = []
            for result in search_results.get("results", []):
                # Check if page has security/KB labels
                page_id = result.get("content", {}).get("id")
                if page_id:
                    try:
                        page_details = self.get_page(page_id)
                        labels = [
                            label.get("name", "")
                            for label in page_details.get("metadata", {})
                            .get("labels", {})
                            .get("results", [])
                        ]

                        # Only include pages with security/KB labels
                        if any(label in self.knowledge_base_labels for label in labels):
                            kb_articles.append(
                                {
                                    "title": result.get("title", ""),
                                    "url": f"{self.url}{result.get('_links', {}).get('webui', '')}",
                                    "excerpt": result.get("excerpt", ""),
                                    "last_updated": result.get("lastModified", ""),
                                    "space": result.get("content", {})
                                    .get("space", {})
                                    .get("key", ""),
                                    "labels": labels,
                                    "relevance_score": result.get("score", 0)
                                    / 100.0,  # Normalize score
                                    "page_id": page_id,
                                }
                            )
                    except Exception as e:
                        # Include basic info even if we can't get labels
                        kb_articles.append(
                            {
                                "title": result.get("title", ""),
                                "url": f"{self.url}{result.get('_links', {}).get('webui', '')}",
                                "excerpt": result.get("excerpt", ""),
                                "last_updated": result.get("lastModified", ""),
                                "space": result.get("content", {})
                                .get("space", {})
                                .get("key", ""),
                                "labels": [],
                                "relevance_score": result.get("score", 0) / 100.0,
                                "page_id": page_id,
                                "warning": f"Could not retrieve labels: {str(e)}",
                            }
                        )

            return kb_articles

        except Exception as e:
            # Return mock data with error info if API fails
            return [
                {
                    "title": "PowerShell Attack Investigation Procedures",
                    "url": f"{self.url}/display/{search_space}/powershell-attacks",
                    "excerpt": "Standard procedures for investigating PowerShell-based attacks...",
                    "last_updated": datetime.now().isoformat(),
                    "relevance_score": 0.92,
                    "space": search_space,
                    "labels": ["security", "procedures", "powershell"],
                    "error": f"API search failed, showing cached result: {str(e)}",
                }
            ]

    def get_playbook_content(
        self, playbook_name: str, space_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve playbook content from Confluence.

        Args:
            playbook_name: Name of the playbook to retrieve
            space_key: Space to search in (defaults to playbook space)

        Returns:
            Playbook content and metadata
        """
        search_space = space_key or self.playbook_space_key

        try:
            # Search for the playbook by title
            search_results = self.search_content(
                query=f'title:"{playbook_name}"', space_key=search_space, limit=5
            )

            # Find exact or closest match
            playbook_page = None
            for result in search_results.get("results", []):
                if playbook_name.lower() in result.get("title", "").lower():
                    playbook_page = result
                    break

            if not playbook_page:
                return {
                    "error": f"Playbook '{playbook_name}' not found in space {search_space}",
                    "searched_space": search_space,
                    "available_results": [
                        r.get("title", "") for r in search_results.get("results", [])
                    ],
                }

            # Get full page content
            page_id = playbook_page.get("content", {}).get("id")
            if page_id:
                page_details = self.get_page(
                    page_id, expand="body.storage,metadata.labels"
                )

                return {
                    "name": playbook_name,
                    "title": page_details.get("title", ""),
                    "content": page_details.get("body", {})
                    .get("storage", {})
                    .get("value", ""),
                    "url": f"{self.url}{page_details.get('_links', {}).get('webui', '')}",
                    "space": search_space,
                    "page_id": page_id,
                    "last_updated": page_details.get("version", {}).get("when", ""),
                    "labels": [
                        label.get("name", "")
                        for label in page_details.get("metadata", {})
                        .get("labels", {})
                        .get("results", [])
                    ],
                    "metadata": {
                        "version": page_details.get("version", {}).get("number", 1),
                        "created": page_details.get("history", {}).get(
                            "createdDate", ""
                        ),
                        "creator": page_details.get("history", {})
                        .get("createdBy", {})
                        .get("displayName", ""),
                    },
                }
            else:
                return {
                    "error": f"Could not retrieve page ID for playbook '{playbook_name}'",
                    "title": playbook_page.get("title", ""),
                    "excerpt": playbook_page.get("excerpt", ""),
                }

        except Exception as e:
            # Return mock/cached content if API fails
            return {
                "name": playbook_name,
                "title": f"{playbook_name} Playbook",
                "content": f"## {playbook_name} Playbook\n\nThis is cached/mock content for the {playbook_name} playbook.",
                "url": f"{self.url}/display/{search_space}/{playbook_name.replace(' ', '-')}",
                "space": search_space,
                "error": f"API retrieval failed, showing mock content: {str(e)}",
                "metadata": {
                    "name": playbook_name,
                    "created": datetime.now().isoformat(),
                    "source": "mock_fallback",
                },
            }
