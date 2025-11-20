"""
Configuration management for job tracker.

Supports both local (.env file) and cloud (environment variables) configuration.
"""

import os
from typing import List
from dotenv import load_dotenv

# Load .env file if it exists (for local development)
load_dotenv()

# Email configuration
EMAIL_SENDER = os.getenv('EMAIL_SENDER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_RECIPIENT = os.getenv('EMAIL_RECIPIENT')

# Adzuna API configuration
ADZUNA_APP_ID = os.getenv('ADZUNA_APP_ID')
ADZUNA_API_KEY = os.getenv('ADZUNA_API_KEY')

# Job search configuration
SEARCH_KEYWORDS = os.getenv('SEARCH_KEYWORDS', 'software engineer intern')
SEARCH_LOCATIONS = os.getenv('SEARCH_LOCATIONS', 'United States').split(',')
MAX_DAYS_OLD = int(os.getenv('MAX_DAYS_OLD', '7'))

# Database configuration
# Options: 'sqlite' or 'dynamodb'
DB_TYPE = os.getenv('DB_TYPE', 'sqlite')
DB_PATH = os.getenv('DB_PATH', 'jobs.db')

# AWS configuration (for future Lambda deployment)
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
DYNAMODB_TABLE = os.getenv('DYNAMODB_TABLE', 'job-tracker')
S3_BUCKET = os.getenv('S3_BUCKET', '')  # For SQLite persistence in Lambda


def validate_config() -> bool:
    """
    Validate that all required configuration is present.
    
    Returns:
        True if configuration is valid
        
    Raises:
        ValueError if required configuration is missing
    """
    required = {
        'EMAIL_SENDER': EMAIL_SENDER,
        'EMAIL_PASSWORD': EMAIL_PASSWORD,
        'EMAIL_RECIPIENT': EMAIL_RECIPIENT,
        'ADZUNA_APP_ID': ADZUNA_APP_ID,
        'ADZUNA_API_KEY': ADZUNA_API_KEY
    }
    
    missing = [key for key, value in required.items() if not value]
    
    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}\n"
            f"Please create a .env file or set environment variables."
        )
    
    return True


def get_db_config() -> dict:
    """Get database configuration based on DB_TYPE."""
    if DB_TYPE == 'sqlite':
        return {
            'type': 'sqlite',
            'path': DB_PATH
        }
    elif DB_TYPE == 'dynamodb':
        return {
            'type': 'dynamodb',
            'table_name': DYNAMODB_TABLE,
            'region': AWS_REGION
        }
    else:
        raise ValueError(f"Unknown DB_TYPE: {DB_TYPE}")
