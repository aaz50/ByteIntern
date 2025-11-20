import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Email configuration
EMAIL_SENDER = os.getenv('EMAIL_SENDER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_RECIPIENT = os.getenv('EMAIL_RECIPIENT')

# Adzuna API configuration
ADZUNA_APP_ID = os.getenv('ADZUNA_APP_ID')
ADZUNA_API_KEY = os.getenv('ADZUNA_API_KEY')

# Job search configuration
SEARCH_KEYWORDS = "software engineer intern"
SEARCH_LOCATIONS = ["United States"]  # Can add multiple locations
MAX_DAYS_OLD = 7  # Only fetch jobs posted in last N days

# Database configuration
DATABASE_PATH = "jobs.db"

# Validation
def validate_config():
    """Check if all required environment variables are set"""
    required = {
        'EMAIL_SENDER': EMAIL_SENDER,
        'EMAIL_PASSWORD': EMAIL_PASSWORD,
        'EMAIL_RECIPIENT': EMAIL_RECIPIENT,
        'ADZUNA_APP_ID': ADZUNA_APP_ID,
        'ADZUNA_API_KEY': ADZUNA_API_KEY
    }
    
    missing = [key for key, value in required.items() if not value]
    
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
    
    return True
