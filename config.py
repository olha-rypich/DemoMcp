import argparse
import base64
import os

def _parse_args():
    parser = argparse.ArgumentParser(description="Jira MCP Server")
    parser.add_argument("--email",       required=False, default=os.getenv("JIRA_EMAIL", ""))
    parser.add_argument("--token",       required=False, default=os.getenv("JIRA_TOKEN", ""))
    parser.add_argument("--url",         required=False, default=os.getenv("JIRA_URL", ""))
    parser.add_argument("--project-key", required=False, default=os.getenv("JIRA_PROJECT_KEY", "DEV"))
    # parse_known_args ignores pytest's own flags (-v, --tb, etc.)
    args, _ = parser.parse_known_args()
    return args

def _build_headers(email: str, token: str) -> dict[str, str]:
    creds = base64.b64encode(f"{email}:{token}".encode()).decode()
    return {
        "Authorization": f"Basic {creds}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

_args = _parse_args()
JIRA_BASE_URL = _args.url.rstrip("/")
PROJECT_KEY   = _args.project_key
HEADERS       = _build_headers(_args.email, _args.token)
VALID_ISSUE_TYPES = ["Bug", "Task", "Epic"]