from fastmcp import FastMCP
from fastmcp.exceptions import ToolError, ValidationError
from http_client import jira_request
from schemas import CreateIssueSchema
from adf import to_adf
from config import PROJECT_KEY

def register(mcp: FastMCP) -> None:

    @mcp.tool
    def create_issue(
        summary: str,
        description: str = "",
        issue_type: str = "Task",
    ) -> dict:
        """
        Create a new Jira issue.

        Args:
            summary:     Short title. Max 255 chars.
            description: Plain text. Use double newlines for paragraphs.
            issue_type:  Bug | Task | Epic. Default is Task.
        Returns:
            Created issue key, summary and url.
        """
        try:
            data = CreateIssueSchema(
                summary=summary,
                description=description,
                issue_type=issue_type,
            )
        except (ValueError, ValidationError) as e:
            raise ToolError(str(e)) from e

        payload = {
            "fields": {
                "project":     {"key": PROJECT_KEY},
                "summary":     data.summary,
                "description": to_adf(data.description),
                "issuetype":   {"name": data.issue_type},
            }
        }

        result = jira_request("POST", "/rest/api/3/issue", json=payload)
        key = result.get("key", "Unknown")

        return {
            "key":     key,
            "summary": data.summary,
            "type":    data.issue_type,
        }