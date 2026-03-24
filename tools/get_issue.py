from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from pydantic import ValidationError
from http_client import jira_request
from schemas import IssueKeySchema


def register(mcp: FastMCP) -> None:

    @mcp.tool(
        annotations={"readOnlyHint": True}
    )
    def get_issue(issue_key: str) -> dict:
        """
        Get Jira issue details by key.

        Args:
            issue_key: Issue key, e.g. 'DEV-1'.

        Returns:
            Issue key, summary, status, assignee, priority and description.
        """
        try:
            data = IssueKeySchema(issue_key=issue_key)
        except (ValueError, ValidationError) as e:
            raise ToolError(str(e)) from e

        result = jira_request(
            "GET",
            f"/rest/api/3/issue/{data.issue_key}",
            params={"fields": "summary,status,assignee,priority,description"}
        )

        fields      = result.get("fields", {})
        summary     = fields.get("summary", "—")
        status      = fields.get("status", {}).get("name", "—")
        assignee    = (fields.get("assignee") or {}).get("displayName", "Unassigned")
        priority    = (fields.get("priority") or {}).get("name", "—")

        description = "No description"
        adf = fields.get("description")
        if adf and isinstance(adf, dict):
            texts = []
            for block in adf.get("content", []):
                for inline in block.get("content", []):
                    if inline.get("type") == "text":
                        texts.append(inline.get("text", ""))
            description = " ".join(texts).strip() or "No description"

        return {
            "key":         data.issue_key,
            "summary":     summary,
            "status":      status,
            "assignee":    assignee,
            "priority":    priority,
            "description": description,
        }