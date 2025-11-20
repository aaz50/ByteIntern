# Tech Stack

## Overview

ByteIntern is built with Python and designed for flexible deployment, from local execution to cloud-based automation.

## Core Technologies

### Backend
- **Python 3.8+** - Primary programming language
- **SQLite** - Embedded database for local/GitHub Actions deployment
- **DynamoDB** - Future cloud database for AWS Lambda (abstraction layer ready)

### APIs & Services
- **Adzuna API** - Job aggregation service
  - Free tier: 1000 API calls/month
  - Supports multi-location search
  - JSON REST API
- **Gmail SMTP** - Email delivery via Google's SMTP server
  - Requires app-specific password
  - Built-in Python `smtplib` integration

### Key Python Libraries

| Library | Version | Purpose |
|---------|---------|---------|
| `requests` | 2.31.0 | HTTP client for API calls |
| `python-dotenv` | 1.0.0 | Environment variable management |
| `sqlite3` | Built-in | Database interface |
| `smtplib` | Built-in | Email sending |
| `email.mime` | Built-in | Email formatting |

## Architecture

### Design Pattern: Layered Architecture

```
┌─────────────────────────────────────┐
│      Runners (Entry Points)          │
│  ┌──────────┐      ┌──────────┐    │
│  │ local.py │      │lambda.py │    │
│  └────┬─────┘      └────┬─────┘    │
└───────┼──────────────────┼──────────┘
        │                  │
┌───────┴──────────────────┴──────────┐
│         Core Business Logic          │
│  ┌────────┐ ┌────────┐ ┌─────────┐ │
│  │fetcher │ │storage │ │notifier │ │
│  └────────┘ └────────┘ └─────────┘ │
└──────────────────────────────────────┘
        │          │           │
┌───────┴──────────┴───────────┴───────┐
│         External Services             │
│   Adzuna API | SQLite | Gmail SMTP   │
└───────────────────────────────────────┘
```

### Core Modules

#### 1. **`src/core/fetcher.py`** - API Client
- Makes HTTP requests to Adzuna API
- Transforms raw API responses to standardized format
- Handles multi-location searches with deduplication
- Error handling and timeout management

#### 2. **`src/core/storage.py`** - Database Abstraction
- **SQLiteStorage**: File-based database for local use
- **DynamoDBStorage**: Cloud database (future implementation)
- Interface-based design allows easy swapping
- Tracks job IDs, metadata, and notification status

#### 3. **`src/core/notifier.py`** - Email Handler
- Formats job data into readable emails
- Sends via Gmail SMTP (port 465, SSL)
- Supports test emails and bulk notifications
- HTML-ready structure for future enhancements

#### 4. **`src/core/config.py`** - Configuration Management
- Loads environment variables via `python-dotenv`
- Validates required credentials
- Supports both local `.env` files and cloud environment variables
- Default values for optional settings

### Runner Implementations

#### **`src/runners/local.py`**
- Entry point for local and GitHub Actions execution
- Command-line arguments: `--check`, `--stats`, `--test-email`, `--send-all`
- Orchestrates: fetch → filter → store → notify workflow
- Error handling and user-friendly console output

#### **`src/runners/lambda.py`**
- AWS Lambda handler function (future deployment)
- Designed for EventBridge/CloudWatch triggers
- DynamoDB integration for persistent storage
- Optimized for cold-start performance

## Deployment Options

### Phase 1: GitHub Actions (Current)
```yaml
Technology: GitHub Actions
Database: SQLite (uploaded as artifact)
Schedule: Cron-based (e.g., every 6 hours)
Cost: Free (GitHub Actions free tier)
Pros: Zero setup cost, easy to deploy
Cons: Limited to 5-minute runs, slower execution
```

### Phase 2: AWS Lambda (Future)
```yaml
Technology: AWS Lambda + EventBridge
Database: DynamoDB
Schedule: EventBridge rules (e.g., every 15 min)
Cost: AWS Free Tier covers most usage
Pros: Faster execution, frequent checks, scalable
Cons: Requires AWS account and setup
```

### Phase 3: Web Application (Potential)
```yaml
Frontend: React + TypeScript
Backend: FastAPI (Python)
Database: PostgreSQL or DynamoDB
Hosting: Vercel (frontend) + Railway/AWS (backend)
Features: Job dashboard, filters, application tracking
```

## Data Flow

```
1. Trigger (cron/manual)
   ↓
2. Load configuration (.env or environment variables)
   ↓
3. Initialize components (fetcher, storage, notifier)
   ↓
4. Fetch jobs from Adzuna API
   ↓
5. For each job:
   - Check if job_id exists in database
   - If new → Add to database
   - Collect new jobs
   ↓
6. Format new jobs into email
   ↓
7. Send email via Gmail SMTP
   ↓
8. Mark jobs as notified in database
   ↓
9. Log results and exit
```

## Database Schema

### SQLite Table: `jobs`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `job_id` | TEXT | PRIMARY KEY | Unique identifier from Adzuna |
| `title` | TEXT | NOT NULL | Job title |
| `company` | TEXT | NOT NULL | Company name |
| `location` | TEXT | | Job location |
| `url` | TEXT | NOT NULL | Application link |
| `description` | TEXT | | Full job description |
| `posted_date` | TEXT | | ISO 8601 timestamp |
| `salary_min` | REAL | | Minimum salary (if available) |
| `salary_max` | REAL | | Maximum salary (if available) |
| `first_seen` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | When tracker discovered job |
| `notified` | BOOLEAN | DEFAULT 0 | Email sent flag (0=no, 1=yes) |

**Indexes:** Primary key on `job_id` for O(1) duplicate checking

## Security Considerations

### Credential Management
- **Never commit `.env` to git** - included in `.gitignore`
- **Use Gmail app passwords** - not actual Gmail passwords
- **GitHub Secrets** - for CI/CD deployment
- **AWS Secrets Manager** - for Lambda deployment (future)

### API Rate Limiting
- Adzuna: 1000 calls/month (free tier)
- Implementation includes timeout and error handling
- Exponential backoff can be added if needed

### Email Security
- SSL/TLS encryption (port 465)
- App-specific passwords reduce account compromise risk
- No plaintext password storage

## Development Tools

### Testing
```bash
# Test individual components
python -m src.core.fetcher    # API connectivity
python -m src.core.notifier   # Email functionality
python -m src.runners.local --check  # Full flow (no email)
```

### Database Management
```bash
# View database contents
python view_database.py

# SQLite CLI
sqlite3 jobs.db
```

### Linting & Formatting (Recommended)
```bash
pip install black flake8 mypy
black src/
flake8 src/
mypy src/
```

## Performance Characteristics

### Local Execution
- **Startup time:** ~0.5s (module imports)
- **API call:** 1-3s per location
- **Database operations:** <10ms per query
- **Email send:** 1-2s
- **Total runtime:** 5-10s (typical)

### GitHub Actions
- **Cold start:** 30-60s (container setup)
- **Execution:** 5-10s
- **Total:** 35-70s per run

### AWS Lambda (Future)
- **Cold start:** 2-5s
- **Warm start:** 200-500ms
- **Concurrent execution:** Supported

## Scalability

### Current Capacity
- **Job volume:** Handles 50+ jobs per search
- **Locations:** Unlimited (API limit permitting)
- **Email size:** Up to 100 jobs per email (practical limit)

### Future Enhancements
- **Message queue:** SQS for async processing
- **Caching:** Redis for API response caching
- **Webhook support:** Discord/Slack notifications
- **Multi-user:** Database partitioning by user_id

## Dependencies Update Strategy

```bash
# Check for outdated packages
pip list --outdated

# Update requirements.txt
pip freeze > requirements.txt

# Security audits
pip install safety
safety check
```

## License

MIT License - See LICENSE file for details.

