# tests/conftest.py
import os
import sys
from dotenv import load_dotenv

# Load .env so config.py gets real credentials via os.getenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# Add root to path for schema/config imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def pytest_configure(config):
    config.addinivalue_line("markers", "bug: marks tests covering known bugs")