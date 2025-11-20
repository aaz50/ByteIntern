# Deployment Guide

## Option 1: GitHub Actions (Recommended)

GitHub Actions lets you run the job tracker automatically in the cloud for free.

### Setup Steps:

1. **Create a GitHub repository and push your code**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/linkedin-job-tracker.git
   git push -u origin main
   ```

2. **Add Secrets to GitHub**
   - Go to your repository on GitHub
   - Click Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Add each of these secrets:
     - `EMAIL_SENDER`: Your Gmail address
     - `EMAIL_PASSWORD`: Your Gmail app password
     - `EMAIL_RECIPIENT`: Email to receive notifications
     - `ADZUNA_APP_ID`: Your Adzuna App ID
     - `ADZUNA_API_KEY`: Your Adzuna API Key

3. **Create GitHub Actions Workflow**
   
   Create `.github/workflows/job-tracker.yml`:
   ```yaml
   name: Job Tracker
   
   on:
     schedule:
       # Run every 6 hours
       - cron: '0 */6 * * *'
     
     # Allow manual trigger
     workflow_dispatch:
   
   jobs:
     check-jobs:
       runs-on: ubuntu-latest
       
       steps:
         - name: Checkout code
           uses: actions/checkout@v3
         
         - name: Set up Python
           uses: actions/setup-python@v4
           with:
             python-version: '3.11'
         
         - name: Install dependencies
           run: |
             python -m pip install --upgrade pip
             pip install -r requirements.txt
         
         - name: Run job tracker
           env:
             EMAIL_SENDER: ${{ secrets.EMAIL_SENDER }}
             EMAIL_PASSWORD: ${{ secrets.EMAIL_PASSWORD }}
             EMAIL_RECIPIENT: ${{ secrets.EMAIL_RECIPIENT }}
             ADZUNA_APP_ID: ${{ secrets.ADZUNA_APP_ID }}
             ADZUNA_API_KEY: ${{ secrets.ADZUNA_API_KEY }}
           run: python main.py
         
         - name: Upload database artifact
           uses: actions/upload-artifact@v3
           with:
             name: jobs-database
             path: jobs.db
             retention-days: 30
   ```

4. **Adjust Schedule** (Optional)
   
   Modify the cron expression in the workflow file:
   - `0 */6 * * *` - Every 6 hours
   - `0 */4 * * *` - Every 4 hours
   - `0 9,17 * * *` - 9am and 5pm daily
   - `0 9 * * 1-5` - 9am on weekdays only
   
   Use [crontab.guru](https://crontab.guru/) to create custom schedules.

5. **Test the Workflow**
   - Go to Actions tab in GitHub
   - Select "Job Tracker" workflow
   - Click "Run workflow" to test manually

### Important Notes:
- GitHub Actions has a 2000 minutes/month limit on free accounts (plenty for this)
- The database resets between runs (but that's fine since we track by job ID)
- To keep persistent database, you'll need to commit it or use Actions artifacts

---

## Option 2: Local Cron Job

Run on your own computer using cron (Mac/Linux) or Task Scheduler (Windows).

### Mac/Linux Setup:

1. **Make script executable**
   ```bash
   chmod +x main.py
   ```

2. **Edit crontab**
   ```bash
   crontab -e
   ```

3. **Add cron job** (runs every 6 hours)
   ```
   0 */6 * * * cd /full/path/to/linkedin-job-tracker && /usr/bin/python3 main.py >> tracker.log 2>&1
   ```

### Windows Setup:

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily (or your preference)
4. Action: Start a program
   - Program: `python`
   - Arguments: `C:\path\to\linkedin-job-tracker\main.py`
   - Start in: `C:\path\to\linkedin-job-tracker`

---

## Option 3: Cloud Server (Heroku, Railway, etc.)

For more advanced users who want 24/7 uptime.

### Railway Setup:

1. Push code to GitHub
2. Go to [Railway.app](https://railway.app)
3. Create new project from GitHub repo
4. Add environment variables in Railway dashboard
5. Add a start command: `while true; do python main.py; sleep 21600; done`

### Heroku Setup (using scheduler add-on):

1. Create Heroku app
2. Add Heroku Scheduler add-on
3. Configure job to run `python main.py` every hour/day
4. Set environment variables in Heroku dashboard

---

## Monitoring

### Check if it's working:
- Look for emails with new job postings
- Check GitHub Actions logs for errors
- Run `python main.py --stats` to see database stats

### Troubleshooting:
- No emails? Check spam folder
- API errors? Verify Adzuna credentials
- Email errors? Regenerate Gmail app password
- No new jobs? Try increasing `MAX_DAYS_OLD` in config.py
