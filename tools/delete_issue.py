from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from pydantic import ValidationError
from http_client import jira_request
from schemas import IssueKeySchema


def register(mcp: FastMCP) -> None:

    @mcp.tool(
        annotations={"destructiveHint": True}
    )
    def delete_issue(issue_key: str) -> dict:
        """
        Delete a Jira issue permanently.
        This action cannot be undone.

        Args:
            issue_key: Issue key, e.g. 'AT-42'.

        Returns:
            Deleted issue key and confirmation.
        """
        try:
            data = IssueKeySchema(issue_key=issue_key)
        except (ValueError, ValidationError) as e:
            raise ToolError(str(e)) from e

        jira_request(
            "DELETE",
            f"/rest/api/3/issue/{data.issue_key}",
        )

        return {
            "key":    data.issue_key,
            "deleted": True,
        }