from fastmcp import FastMCP
from fastmcp.exceptions import ToolError, ValidationError
from http_client import jira_request
from schemas import SearchIssuesSchema


def register(mcp: FastMCP) -> None:

    @mcp.tool(
        annotations={"readOnlyHint": True}
    )
    def search_issues(
        jql: str,
        max_results: int = 20,
    ) -> dict:
        """
        Search Jira issues using JQL.

        Args:
            jql:         JQL query string.
                         Examples:
                           'project=JAIA ORDER BY created DESC'
                           'project=JAIA AND status=Open'
                           'project=JAIA AND issuetype=Bug'
            max_results: Number of issues to return. Between 1 and 50. Default: 20.

        Returns:
            Total count and list of matching issues.
        """
        try:
            data = SearchIssuesSchema(jql=jql, max_results=max_results)
        except (ValueError, ValidationError) as e:
            raise ToolError(str(e)) from e

        result = jira_request(
            "POST",
            "/rest/api/3/search/jql",
            json={
                "jql":        data.jql,
                "maxResults": data.max_results,
                "fields":     ["summary", "status", "assignee", "priority", "issuetype"],
            },
        )

        issues = result.get("issues", [])
        total  = result.get("total", 0)

        items = []
        for issue in issues:
            fields = issue.get("fields", {})
            items.append({
                "key":      issue.get("key", "—"),
                "summary":  fields.get("summary", "—"),
                "status":   fields.get("status", {}).get("name", "—"),
                "assignee": (fields.get("assignee") or {}).get("displayName", "Unassigned"),
                "priority": (fields.get("priority") or {}).get("name", "—"),
                "type":     fields.get("issuetype", {}).get("name", "—"),
            })

        return {
            "total":  total,
            "count":  len(items),
            "issues": items,
        }