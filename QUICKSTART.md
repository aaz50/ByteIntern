# Quick Start Guide

Get your job tracker running in 10 minutes!

## Step 1: Clone/Download the Project

```bash
cd linkedin-job-tracker
```

## Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note:** If you don't have pip, install it first:
- Mac: `python3 -m ensurepip`
- Windows: `python -m ensurepip`

## Step 3: Get API Keys

### Adzuna API (Free, 5 minutes)

1. Go to https://developer.adzuna.com/
2. Click "Sign Up" → Create account
3. Once logged in, click "Create a new application"
4. Name it "Job Tracker" (or anything)
5. Copy your **Application ID** and **API Key**

**Free tier:** 1000 API calls/month (plenty for hourly checks)

### Gmail App Password (3 minutes)

1. **Enable 2-Factor Authentication** on your Google account first
2. Go to https://myaccount.google.com/apppasswords
3. Select "Mail" → Generate
4. Copy the 16-character password (looks like: `abcd efgh ijkl mnop`)

**Important:** Use the app password, NOT your regular Gmail password!

## Step 4: Configure Environment

Create a `.env` file from the template:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```bash
# On Mac/Linux
nano .env

# On Windows
notepad .env
```

Fill in your values:
```
EMAIL_SENDER=youremail@gmail.com
EMAIL_PASSWORD=abcdefghijklmnop
EMAIL_RECIPIENT=youremail@gmail.com
ADZUNA_APP_ID=12345abc
ADZUNA_API_KEY=1234567890abcdef1234567890abcdef
```

**Save the file!**

## Step 5: Test Everything

### Test API fetching
```bash
python -m src.core.fetcher
```
✓ Should show list of jobs

### Test email
```bash
python -m src.core.notifier
```
✓ Should receive test email

### Test full system
```bash
python -m src.runners.local --check
```
✓ Should fetch jobs and add to database (no email sent)

## Step 6: Run For Real

```bash
python -m src.runners.local
```

This will:
1. Fetch jobs from Adzuna
2. Check which are new
3. Send you an email if new jobs found
4. Store jobs in SQLite database

## Step 7: Deploy to GitHub Actions

### 7.1 Create GitHub Repository

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/linkedin-job-tracker.git
git push -u origin main
```

### 7.2 Add Secrets to GitHub

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**
4. Add each of these secrets:

| Secret Name | Value |
|------------|-------|
| `EMAIL_SENDER` | your-email@gmail.com |
| `EMAIL_PASSWORD` | your-app-password (16 chars) |
| `EMAIL_RECIPIENT` | your-email@gmail.com |
| `ADZUNA_APP_ID` | your-app-id |
| `ADZUNA_API_KEY` | your-api-key |

### 7.3 Test the Workflow

1. Go to **Actions** tab in GitHub
2. Select "Job Tracker" workflow
3. Click **"Run workflow"** → **"Run workflow"**
4. Wait ~1 minute
5. Check your email for results!

### 7.4 Customize Schedule

The workflow runs every 6 hours by default. To change:

Edit `.github/workflows/job-tracker.yml`:

```yaml
schedule:
  - cron: '0 */4 * * *'  # Every 4 hours
  # or
  - cron: '0 9,17 * * *'  # 9am and 5pm daily
  # or
  - cron: '0 9 * * 1-5'   # 9am on weekdays only
```

Use [crontab.guru](https://crontab.guru/) to create custom schedules.

## Useful Commands

```bash
# Check stats
python -m src.runners.local --stats

# Test email only
python -m src.runners.local --test-email

# Check without emailing
python -m src.runners.local --check

# Normal run (searches + emails)
python -m src.runners.local
```

## Customize Search

Edit `src/core/config.py` or add to `.env`:

```bash
# .env
SEARCH_KEYWORDS=python developer intern
SEARCH_LOCATIONS=San Francisco,New York,Remote
MAX_DAYS_OLD=3
```

## Troubleshooting

### "Missing required environment variables"
- Make sure `.env` file exists in project root
- Check all values are filled in (no empty strings)
- No spaces around `=` signs

### "Error fetching jobs"
- Verify Adzuna credentials are correct
- Check you haven't exceeded 1000 calls/month
- Try running fetcher test: `python -m src.core.fetcher`

### "Failed to send email"
- Use app password, not regular Gmail password
- Make sure 2FA is enabled
- Try regenerating app password
- Check sender email is correct

### "No new jobs to report"
- Normal if you've seen all available jobs
- Wait a few hours for new postings
- Try increasing MAX_DAYS_OLD
- Try different keywords/locations

### GitHub Actions not running
- Check if workflow file is in `.github/workflows/`
- Verify secrets are added correctly
- Go to Actions tab → check for error messages

## Next Steps

✅ Phase 1 Complete: Working tracker with GitHub Actions!

**Future enhancements:**
- Phase 2: Migrate to AWS Lambda for faster checks
- Phase 3: Build web UI with React/TypeScript
- Add filtering by company, salary, remote status
- Track application status
- Add company research integration

---

## Pro Tips

1. **Check frequently for early applications**: Edit cron to `*/30 * * * *` (every 30 min) for competitive advantage
2. **Customize notifications**: Fork the code to send Discord/Slack messages instead
3. **Filter results**: Add logic in `src/core/storage.py` to skip certain companies
4. **Track applications**: Add a status column to mark "applied", "interview", etc.

Happy job hunting! 🚀
