# tests/test_mcp_deepeval.py
import os
import sys
import json
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")

import mcp.types as mcp_types
from fastmcp import Client
from fastmcp.client.transports import PythonStdioTransport
from deepeval.test_case import LLMTestCase, MCPServer, MCPToolCall
from deepeval.metrics import MCPUseMetric

# ─── Server config ─────────────────────────────────────────────────────────

PYTHON_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", ".venv", "Scripts", "python.exe")
)
SERVER_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "server.py")
)
SERVER_ARGS = [
    "--email",       os.getenv("JIRA_EMAIL"),
    "--token",       os.getenv("JIRA_TOKEN"),
    "--url",         os.getenv("JIRA_URL"),
    "--project-key", os.getenv("JIRA_PROJECT_KEY", "DEV"),
]

def get_transport():
    return PythonStdioTransport(
        script_path=SERVER_PATH,
        python_cmd=PYTHON_PATH,
        args=SERVER_ARGS,
    )


# ─── Helper: build raw CallToolResult ──────────────────────────────────────

def make_call_tool_result(text: str) -> mcp_types.CallToolResult:
    """Wrap a text string into mcp.types.CallToolResult."""
    return mcp_types.CallToolResult(
        content=[mcp_types.TextContent(type="text", text=text)],
        isError=False,
    )


# ─── Test 1: get_issue single turn ─────────────────────────────────────────

def test_deepeval_get_issue_single_turn():
    """
    MCPUseMetric: verifies that get_issue is called correctly
    for DEV-1 and returns valid data. Threshold >= 0.5
    """
    async def run():
        async with Client(get_transport()) as client:
            tools = await client.list_tools()
            result = await client.call_tool(
                "get_issue", {"issue_key": "DEV-1"}
            )
            raw_text = result.content[0].text
            return tools, raw_text

    tools, raw_text = asyncio.run(run())

    # Build MCPToolCall with mcp.types.CallToolResult as result
    tool_call = MCPToolCall(
        name="get_issue",
        args={"issue_key": "DEV-1"},
        result=make_call_tool_result(raw_text),
    )

    test_case = LLMTestCase(
        input="Get the details of Jira issue DEV-1",
        actual_output=raw_text,
        mcp_servers=[MCPServer(
            server_name="JiraMCP",
            transport="stdio",
            available_tools=tools,
        )],
        mcp_tools_called=[tool_call],
    )

    metric = MCPUseMetric(threshold=0.5, include_reason=True, model="gpt-4o-mini")
    metric.measure(test_case)

    print(f"\nScore: {metric.score}")
    print(f"Reason: {metric.reason}")

    assert metric.score >= 0.5, (
        f"MCPUseMetric score {metric.score} is below threshold 0.5. "
        f"Reason: {metric.reason}"
    )


# ─── Test 2: create and delete issue ───────────────────────────────────────

def test_deepeval_create_and_delete_issue():
    """
    MCPUseMetric: verifies that create_issue and delete_issue
    are called correctly in sequence. Threshold >= 0.5
    """
    async def run():
        async with Client(get_transport()) as client:
            tools = await client.list_tools()

            # Create issue
            create_result = await client.call_tool(
                "create_issue",
                {"summary": "DeepEval test issue", "issue_type": "Bug"}
            )
            create_text = create_result.content[0].text
            issue_key = json.loads(create_text)["key"]

            # Delete the created issue
            delete_result = await client.call_tool(
                "delete_issue",
                {"issue_key": issue_key}
            )
            delete_text = delete_result.content[0].text

            return tools, create_text, issue_key, delete_text

    tools, create_text, issue_key, delete_text = asyncio.run(run())

    tool_calls = [
        MCPToolCall(
            name="create_issue",
            args={"summary": "DeepEval test issue", "issue_type": "Bug"},
            result=make_call_tool_result(create_text),
        ),
        MCPToolCall(
            name="delete_issue",
            args={"issue_key": issue_key},
            result=make_call_tool_result(delete_text),
        ),
    ]

    test_case = LLMTestCase(
        input="Create a Bug issue with summary 'DeepEval test issue' then delete it",
        actual_output=f"Created {issue_key} and deleted it successfully",
        mcp_servers=[MCPServer(
            server_name="JiraMCP",
            transport="stdio",
            available_tools=tools,
        )],
        mcp_tools_called=tool_calls,
    )

    metric = MCPUseMetric(threshold=0.5, include_reason=True, model="gpt-4o-mini")
    metric.measure(test_case)

    print(f"\nScore: {metric.score}")
    print(f"Reason: {metric.reason}")

    assert metric.score >= 0.5, (
        f"MCPUseMetric score {metric.score} is below threshold 0.5. "
        f"Reason: {metric.reason}"
    )