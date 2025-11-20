# Job Tracker

Automated internship tracker with email notifications for software engineering positions. Built with Python, SQLite, and the Adzuna API.

## Features

- 🔍 Automated job search via Adzuna API
- 📧 Email notifications for new postings
- 💾 SQLite database to track seen jobs
- ⚙️ Customizable search keywords and locations
- 🚀 Deploy to GitHub Actions (free cloud automation)
- 🔧 Extensible architecture for future enhancements

## Tech Stack

**Backend:** Python 3.8+  
**Database:** SQLite (local), DynamoDB-ready (AWS)  
**API:** Adzuna Job Search API  
**Email:** Gmail SMTP  
**Deployment:** GitHub Actions, AWS Lambda (future)

**Key Libraries:**
- `requests` - HTTP client
- `python-dotenv` - Environment management
- `sqlite3` - Database interface

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file with your credentials:

```env
EMAIL_SENDER=your-email@gmail.com
EMAIL_PASSWORD=your-gmail-app-password
EMAIL_RECIPIENT=your-email@gmail.com
ADZUNA_APP_ID=your-app-id
ADZUNA_API_KEY=your-api-key
```

**Get API Keys:**
- **Adzuna API:** [developer.adzuna.com](https://developer.adzuna.com/) (free tier: 1000 calls/month)
- **Gmail App Password:** [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) (requires 2FA)

### 3. Run

```bash
# Search for jobs and send email
python -m src.runners.local

# Test mode (no email sent)
python -m src.runners.local --check

# View database statistics
python -m src.runners.local --stats

# Send test email
python -m src.runners.local --test-email

# Email all jobs in database
python -m src.runners.local --send-all

# View database contents
python view_database.py
```

## Configuration

Customize search parameters in `.env`:

```env
SEARCH_KEYWORDS=software engineer intern
SEARCH_LOCATIONS=San Francisco,New York,Remote
MAX_DAYS_OLD=7
```

## Deployment

### GitHub Actions (Recommended)

1. Push to GitHub
2. Add secrets in **Settings → Secrets → Actions**
3. Workflow runs automatically every 6 hours

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

### Future: AWS Lambda

The project supports AWS Lambda deployment via `src/runners/lambda.py` with DynamoDB backend.

## Project Structure

```
ByteIntern/
├── src/
│   ├── core/              # Business logic
│   │   ├── config.py      # Configuration management
│   │   ├── fetcher.py     # API client
│   │   ├── notifier.py    # Email handler
│   │   └── storage.py     # Database abstraction
│   └── runners/           # Deployment entry points
│       ├── local.py       # Local/GitHub Actions
│       └── lambda.py      # AWS Lambda
├── view_database.py       # Database viewer utility
├── requirements.txt       # Dependencies
└── .env                   # Configuration (not committed)
```

## Architecture Principles

1. **Separation of Concerns:** Core logic independent of deployment
2. **Storage Abstraction:** Easy SQLite → DynamoDB migration
3. **Testability:** Each module can be tested independently
4. **Configurability:** Environment-based settings

## License

MIT

## Contributing

Contributions welcome! Feel free to open issues or submit pull requests.