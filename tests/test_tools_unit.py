import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from schemas import IssueKeySchema, CreateIssueSchema, SearchIssuesSchema


# ─── IssueKeySchema ────────────────────────────────────────────────────────

def test_valid_key():
    """IssueKeySchema accepts a valid key"""
    schema = IssueKeySchema(issue_key="DEV-1")
    assert schema.issue_key == "DEV-1"


def test_lowercase_converted():
    """Lowercase key is automatically converted to uppercase"""
    schema = IssueKeySchema(issue_key="dev-1")
    assert schema.issue_key == "DEV-1"


def test_empty_key_raises():
    """Empty key raises ValueError — min_length=2 catches it"""
    with pytest.raises(Exception):
        IssueKeySchema(issue_key="")


def test_invalid_format_raises():
    """Malformed key raises ValueError"""
    with pytest.raises(Exception):
        IssueKeySchema(issue_key="INVALID")


# ─── CreateIssueSchema ─────────────────────────────────────────────────────

def test_empty_summary_raises():
    """Empty summary raises ValueError"""
    with pytest.raises(Exception):
        CreateIssueSchema(summary="", issue_type="Bug")


def test_whitespace_summary_raises():
    """Whitespace-only summary raises ValueError"""
    with pytest.raises(Exception):
        CreateIssueSchema(summary="   ", issue_type="Bug")


def test_summary_too_long_raises():
    """Summary longer than 255 chars raises ValueError"""
    with pytest.raises(Exception):
        CreateIssueSchema(summary="A" * 256, issue_type="Bug")


def test_invalid_issue_type_raises():
    """Invalid issue type raises ValueError"""
    with pytest.raises(Exception):
        CreateIssueSchema(summary="Valid summary", issue_type="InvalidType")


# ─── SearchIssuesSchema ────────────────────────────────────────────────────

def test_max_results_out_of_range_raises():
    """max_results = 0 raises ValueError (field has ge=1)"""
    with pytest.raises(Exception):
        SearchIssuesSchema(jql="project=DEV", max_results=0)