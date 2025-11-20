"""
Core business logic for LinkedIn Job Tracker.

This module contains all the reusable business logic that's independent
of the deployment platform (local, GitHub Actions, AWS Lambda, etc.).
"""

from src.core.config import validate_config, get_db_config
from src.core.fetcher import JobFetcher
from src.core.storage import get_storage
from src.core.notifier import EmailNotifier

__all__ = [
    'validate_config',
    'get_db_config',
    'JobFetcher',
    'get_storage',
    'EmailNotifier'
]
