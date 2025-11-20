# LinkedIn Job Tracker

Automated job posting tracker for software engineering internships with email notifications - will possibly scale to discord/telegram bots

## Design Principles

1. **Separation of Concerns**: Core logic is independent of deployment platform
2. **Database Abstraction**: Easy to swap SQLite → More complex DB
3. **Configuration Management**: Environment-based settings
4. **Testability**: Each module can be tested independently

## Setup Instructions - refer to QUICKSTART.md for detailed guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required variables:
- `EMAIL_SENDER`: Your Gmail address
- `EMAIL_PASSWORD`: Gmail app password (https://myaccount.google.com/apppasswords)
- `EMAIL_RECIPIENT`: Where to send notifications
- `ADZUNA_APP_ID`: From https://developer.adzuna.com/
- `ADZUNA_API_KEY`: From https://developer.adzuna.com/

### 3. Test Components

**Test API fetching:**
```bash
python -m src.core.fetcher
```

**Test email:**
```bash
python -m src.core.notifier
```

**Test full flow:**
```bash
python -m src.runners.local --check
```

### 4. Run It

```bash
# Normal run (sends email if new jobs found)
python -m src.runners.local

# Check mode (no email)
python -m src.runners.local --check

# Show stats
python -m src.runners.local --stats

# Test email
python -m src.runners.local --test-email
```

## Deployment

### GitHub Actions (Phase 1)
1. Push code to GitHub
2. Add secrets to repository (Settings → Secrets)
3. GitHub will run automatically

### AWS Lambda (Phase 2 - Future)
The `src/runners/lambda.py` file will be the Lambda handler.

## Configuration

Edit `src/core/config.py` to customize:
- Search keywords
- Locations
- How many days back to search
- Database type