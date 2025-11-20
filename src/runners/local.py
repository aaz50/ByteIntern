#!/usr/bin/env python3
"""
Local runner for LinkedIn Job Tracker.

This script is used for:
- Local development and testing
- GitHub Actions execution
- Manual cron jobs

The business logic is in src/core, this is just the entry point.
"""

import sys
import argparse
from datetime import datetime
from src.core import (
    validate_config, 
    JobFetcher, 
    get_storage, 
    EmailNotifier,
    config
)


def main():
    """Main orchestration function."""
    
    parser = argparse.ArgumentParser(
        description='LinkedIn Job Tracker - Find SWE internships'
    )
    parser.add_argument(
        '--test-email', 
        action='store_true', 
        help='Send a test email and exit'
    )
    parser.add_argument(
        '--check', 
        action='store_true',
        help='Check for new jobs without sending email'
    )
    parser.add_argument(
        '--stats', 
        action='store_true',
        help='Show database statistics'
    )
    args = parser.parse_args()
    
    # Validate configuration
    try:
        validate_config()
    except ValueError as e:
        print(f"\n❌ Configuration error: {e}")
        print("\nPlease create a .env file with required variables.")
        print("See .env.example for template.\n")
        sys.exit(1)
    
    # Initialize components
    storage = get_storage()
    fetcher = JobFetcher()
    notifier = EmailNotifier()
    
    # Handle test email
    if args.test_email:
        print("\n📧 Sending test email...")
        success = notifier.send_test_email()
        sys.exit(0 if success else 1)
    
    # Handle stats
    if args.stats:
        total_jobs = storage.get_job_count()
        print(f"\n📊 Database Statistics")
        print(f"=" * 50)
        print(f"Total jobs tracked: {total_jobs}")
        
        if total_jobs > 0:
            print(f"\nRecent jobs:")
            recent_jobs = storage.get_all_jobs()[:5]
            for job in recent_jobs:
                print(f"  • {job['title']} at {job['company']}")
                print(f"    Added: {job['first_seen']}")
        print()
        sys.exit(0)
    
    # Main job tracking logic
    print(f"\n{'='*60}")
    print(f"🔍 LinkedIn Job Tracker")
    print(f"{'='*60}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Searching for: {config.SEARCH_KEYWORDS}")
    print(f"Locations: {', '.join(config.SEARCH_LOCATIONS)}")
    print(f"Max age: {config.MAX_DAYS_OLD} days")
    print()
    
    # Fetch jobs
    print("🌐 Fetching jobs from Adzuna API...")
    jobs = fetcher.fetch_all_locations(
        keywords=config.SEARCH_KEYWORDS,
        locations=config.SEARCH_LOCATIONS,
        max_days_old=config.MAX_DAYS_OLD
    )
    
    if not jobs:
        print("\n⚠️  No jobs found. Possible issues:")
        print("  - API credentials incorrect")
        print("  - Search parameters too restrictive")
        print("  - No matching jobs in timeframe")
        sys.exit(0)
    
    # Filter for new jobs
    print(f"\n🔎 Checking for new jobs...")
    new_jobs = []
    
    for job in jobs:
        if storage.is_new_job(job['id']):
            new_jobs.append(job)
            storage.add_job(job)
    
    print(f"\n{'='*60}")
    print(f"📈 Results: Found {len(new_jobs)} new job(s)")
    print(f"{'='*60}")
    
    # Send notifications
    if new_jobs:
        if args.check:
            print("\n📝 New jobs found (--check mode, not sending email):")
            for job in new_jobs:
                print(f"  • {job['title']} at {job['company']}")
                print(f"    {job['url']}")
        else:
            print("\n📧 Sending email notification...")
            success = notifier.send_notification(new_jobs)
            
            if success:
                # Mark jobs as notified
                for job in new_jobs:
                    storage.mark_as_notified(job['id'])
    else:
        print("\n✅ No new jobs to report (all jobs already seen)")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"✓ Job check complete")
    print(f"  Total jobs in database: {storage.get_job_count()}")
    print(f"  New jobs this run: {len(new_jobs)}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
