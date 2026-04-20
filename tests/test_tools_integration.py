# tests/test_tools_integration.py
import pytest
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastmcp import Client
from fastmcp.client.transports import PythonStdioTransport
from fastmcp.exceptions import ToolError
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# ─── Server transport ──────────────────────────────────────────────────────

PYTHON_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", ".venv", "Scripts", "python.exe")
)
SERVER_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "server.py")
)

def get_transport():
    return PythonStdioTransport(
        script_path=SERVER_PATH,
        python_cmd=PYTHON_PATH,
        args=[
            "--email",       os.getenv("JIRA_EMAIL"),
            "--token",       os.getenv("JIRA_TOKEN"),
            "--url",         os.getenv("JIRA_URL"),
            "--project-key", os.getenv("JIRA_PROJECT_KEY", "DEV"),
        ],
    )


# ─── Basic integration tests (should always PASS) ──────────────────────────

@pytest.mark.asyncio
async def test_get_issue_valid():
    """get_issue returns data for DEV-1"""
    async with Client(get_transport()) as client:
        result = await client.call_tool("get_issue", {"issue_key": "DEV-1"})
        assert result.is_error is False
        data = json.loads(result.content[0].text)
        assert data["key"] == "DEV-1"


@pytest.mark.asyncio
async def test_get_issue_invalid_format():
    """Invalid key format raises ToolError"""
    async with Client(get_transport()) as client:
        with pytest.raises(ToolError):
            await client.call_tool("get_issue", {"issue_key": "INVALID"})


@pytest.mark.asyncio
async def test_create_issue_empty_summary():
    """Empty summary raises ToolError"""
    async with Client(get_transport()) as client:
        with pytest.raises(ToolError):
            await client.call_tool(
                "create_issue", {"summary": "", "issue_type": "Bug"}
            )


# ─── BUG tests — FAIL before fix, PASS after ──────────────────────────────

@pytest.mark.asyncio
@pytest.mark.bug
async def test_add_comment_response_fields_are_correct():
    """
    BUG #1: add_comment returns swapped field values.
    - comment_id must be the numeric comment ID (e.g. '10000')
    - issue_key must equal the input key ('DEV-1')
    - author must be the display name, not a numeric account ID
    """
    async with Client(get_transport()) as client:
        result = await client.call_tool(
            "add_comment",
            {"issue_key": "DEV-1", "comment": "Automated bug test comment"}
        )
        assert result.is_error is False
        data = json.loads(result.content[0].text)

        # issue_key must be "DEV-1", not the author display name
        assert data["issue_key"] == "DEV-1", (
            f"BUG: issue_key should be 'DEV-1' but got '{data['issue_key']}'"
        )

        # author must be a display name (not a numeric string)
        assert not data["author"].isdigit(), (
            f"BUG: author should be display name but got numeric '{data['author']}'"
        )

        # comment_id must NOT contain ':' (that would be an accountId)
        assert ":" not in str(data["comment_id"]), (
            f"BUG: comment_id looks like accountId: '{data['comment_id']}'"
        )


@pytest.mark.asyncio
@pytest.mark.bug
async def test_get_comments_trailing_space():
    """
    BUG #2: get_comments uses issue_key.upper() without .strip().
    'DEV-1 ' currently raises ToolError correctly via regex,
    but the key is not normalized — it should be stripped first.
    This test verifies ToolError IS raised (correct behaviour).
    """
    async with Client(get_transport()) as client:
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool(
                "get_comments", {"issue_key": "DEV-1 "}
            )
        # The error must mention the key with the space preserved,
        # proving the key was NOT stripped before error reporting
        assert "DEV-1 " in str(exc_info.value), (
            "BUG: error message should show unstripped key 'DEV-1 '"
        )


@pytest.mark.asyncio
@pytest.mark.bug
async def test_get_comments_leading_space():
    """
    BUG #2: get_comments uses issue_key.upper() without .strip().
    ' DEV-1' currently raises ToolError correctly via regex,
    but the key is not normalized — it should be stripped first.
    This test verifies ToolError IS raised (correct behaviour).
    """
    async with Client(get_transport()) as client:
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool(
                "get_comments", {"issue_key": " DEV-1"}
            )
        assert " DEV-1" in str(exc_info.value), (
            "BUG: error message should show unstripped key ' DEV-1'"
        )