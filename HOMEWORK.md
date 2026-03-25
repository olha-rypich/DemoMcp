# Homework: Testing Jira MCP Server

**Cycle:** find → reproduce → automate 

---

## Task 1 — Manual Testing

Precondition: set up your own Atlassian account and create free jira project

Use **MCP Inspector** or **Postman** to manually test all 7 tools.

### MCP Inspector

```bash
npx @modelcontextprotocol/inspector \
  /path/to/.venv/bin/python \
  /path/to/server.py \
  --email your@email.com \
  --token YOUR_TOKEN \
  --url https://your-domain.atlassian.net \
  --project-key DEV
```

Browser opens at `http://localhost:6274` → click **Connect** → **Load capabilities**.

### Postman

Create a new **MCP Request** → select **STDIO** → paste JSON config:

```json
{
  "command": "/path/to/.venv/bin/python",
  "args": [
    "-u",
    "/path/to/server.py",
    "--email", "your@email.com",
    "--token", "YOUR_TOKEN",
    "--url", "https://your-domain.atlassian.net",
    "--project-key", "DEV"
  ]
}
```

Click **Connect** → **Load capabilities**.

### Deliverables

- Completed test checklist for all 7 tools
- Bug Report for each bug found (tool, input, expected, actual, root cause, fix)

---

## Task 2 — Automated Tests

Write automated tests covering:

**Unit tests** — test Pydantic schemas directly, no network required:
- `IssueKeySchema` — valid key, lowercase conversion, empty raises, invalid format raises
- `CreateIssueSchema` — valid input, empty summary raises, too long raises, invalid type raises
- `SearchIssuesSchema` — valid JQL, empty raises, max_results boundaries

**Integration tests** — test tools via FastMCP Client:
- Each tool returns correct response shape (`isError`, `structuredContent` fields)
- Invalid inputs return `isError: True` with readable message
- Multi-step workflows (create → get → delete)
- Bug tests must **FAIL before fix** and **PASS after fix**

### Deliverables

- `tests/test_tools_unit.py`
- `tests/test_tools_integration.py` — failing tests before fix, passing tests after fix
- Fixed tool code

---

## Task 3 — DeepEval Integration Tests (Optional)

Connect Jira MCP Server to the demo LangChain agent and evaluate it with DeepEval.

**Demo agent:** https://github.com/NahornyiDoc/demo-agent

**DeepEval MCP docs:** https://deepeval.com/docs/getting-started-mcp

**DeepEval Agent docs:** https://deepeval.com/docs/getting-started-agents

### Required metrics

| Layer | Metric |
|-------|--------|
| Reasoning | `PlanQualityMetric` |
| Reasoning | `PlanAdherenceMetric` |
| Action | `ToolCorrectnessMetric` |
| Action | `ArgumentCorrectnessMetric` |
| Execution | `TaskCompletionMetric` |
| Execution | `StepEfficiencyMetric` |
| Custom | `GEval` — Jira issue quality |
| Custom | `GEval` — JQL correctness |

### Deliverables
- Solution integrated Allure reporter 
- Attach screenshot with results
- `tests/test_agent_integration.py` with `@observe` tracing
- Short report — which metrics passed, which failed
- Task 3 (integration tests) link your repo with test automation framework
---

## Grading

| Task | Points |
|------|--------|
| Task 1 — checklist complete + 2 bug reports |
| Task 2 — unit + integration tests, bugs fixed |
| Task 3 — agent + DeepEval/Ragas metrics |
| **Total** | **100** |
