#!/usr/bin/env python3
"""
LinkedIn Job Tracker - Main Script

Fetches new software engineering internship postings and sends email notifications.
"""

import sys
import argparse
from datetime import datetime
import config
from database import JobDatabase
from job_fetcher import JobFetcher
from email_notifier import EmailNotifier

def main():
    """Main function to orchestrate job tracking"""
    
    parser = argparse.ArgumentParser(description='Track LinkedIn job postings')
    parser.add_argument('--test-email', action='store_true', 
                       help='Send a test email and exit')
    parser.add_argument('--check', action='store_true',
                       help='Check for new jobs without sending email')
    parser.add_argument('--stats', action='store_true',
                       help='Show database statistics')
    args = parser.parse_args()
    
    # Validate configuration
    try:
        config.validate_config()
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("\nPlease create a .env file with required variables.")
        print("See README.md for setup instructions.")
        sys.exit(1)
    
    # Initialize components
    db = JobDatabase()
    fetcher = JobFetcher()
    notifier = EmailNotifier()
    
    # Handle test email
    if args.test_email:
        print("Sending test email...")
        success = notifier.send_test_email()
        sys.exit(0 if success else 1)
    
    # Handle stats
    if args.stats:
        total_jobs = db.get_job_count()
        print(f"\n📊 Database Statistics")
        print(f"=" * 50)
        print(f"Total jobs tracked: {total_jobs}")
        
        if total_jobs > 0:
            print(f"\nRecent jobs:")
            recent_jobs = db.get_all_jobs()[:5]
            for job in recent_jobs:
                print(f"  - {job['title']} at {job['company']}")
                print(f"    Added: {job['first_seen']}")
        sys.exit(0)
    
    # Main job tracking logic
    print(f"\n🔍 LinkedIn Job Tracker")
    print(f"=" * 50)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Searching for: {config.SEARCH_KEYWORDS}")
    print(f"Locations: {', '.join(config.SEARCH_LOCATIONS)}")
    print()
    
    # Fetch jobs
    print("Fetching jobs from Adzuna API...")
    jobs = fetcher.fetch_all_locations(
        keywords=config.SEARCH_KEYWORDS,
        locations=config.SEARCH_LOCATIONS,
        max_days_old=config.MAX_DAYS_OLD
    )
    
    if not jobs:
        print("No jobs found. Check your API credentials or search parameters.")
        sys.exit(0)
    
    # Filter for new jobs
    print(f"\nChecking for new jobs...")
    new_jobs = []
    
    for job in jobs:
        if db.is_new_job(job['id']):
            new_jobs.append(job)
            db.add_job(job)
    
    print(f"Found {len(new_jobs)} new job(s)")
    
    # Send notifications
    if new_jobs:
        if args.check:
            print("\n📝 New jobs found (--check mode, not sending email):")
            for job in new_jobs:
                print(f"  - {job['title']} at {job['company']}")
                print(f"    {job['url']}")
        else:
            print("\n📧 Sending email notification...")
            success = notifier.send_notification(new_jobs)
            
            if success:
                # Mark jobs as notified
                for job in new_jobs:
                    db.mark_as_notified(job['id'])
    else:
        print("No new jobs to report.")
    
    # Summary
    print(f"\n✓ Job check complete")
    print(f"  Total jobs in database: {db.get_job_count()}")
    print(f"  New jobs this run: {len(new_jobs)}")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
