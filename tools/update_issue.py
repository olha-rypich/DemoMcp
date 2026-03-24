from fastmcp import FastMCP
from fastmcp.exceptions import ToolError, ValidationError
from http_client import jira_request
from schemas import UpdateIssueSchema
from adf import to_adf


def register(mcp: FastMCP) -> None:

    @mcp.tool
    def update_issue(
        issue_key: str,
        summary: str | None = None,
        description: str | None = None,
    ) -> dict:
        """
        Update an existing Jira issue.
        At least one of summary or description must be provided.

        Args:
            issue_key:   Issue key, e.g. 'AT-42'.
            summary:     New title. Max 255 chars.
            description: New plain text description.

        Returns:
            Updated issue key and changed fields.
        """
        try:
            data = UpdateIssueSchema(
                issue_key=issue_key,
                summary=summary,
                description=description,
            )
        except (ValueError, ValidationError) as e:
            raise ToolError(str(e)) from e

        if data.summary is None and data.description is None:
            raise ToolError(
                "At least one of 'summary' or 'description' must be provided"
            )

        fields: dict = {}
        changed: list[str] = []

        if data.summary is not None:
            fields["summary"] = data.summary
            changed.append("summary")

        if data.description is not None:
            fields["description"] = to_adf(data.description)
            changed.append("description")

        jira_request(
            "PUT",
            f"/rest/api/3/issue/{data.issue_key}",
            json={"fields": fields},
        )

        return {
            "key":     data.issue_key,
            "updated": changed,
        }