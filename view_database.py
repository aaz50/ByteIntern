#!/usr/bin/env python3
"""
Simple database viewer - shows all jobs in your SQLite database.

Usage:
    python view_database.py              # View all jobs
    python view_database.py --count      # Just show count
    python view_database.py --notified   # Show only notified jobs
    python view_database.py --new        # Show only un-notified jobs
"""

import sqlite3
import argparse
from datetime import datetime, timedelta


def format_timestamp(timestamp_str):
    """Convert ISO 8601 timestamp to readable format."""
    try:
        # Parse ISO 8601 timestamp (UTC)
        dt_utc = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        
        # Convert to EST (UTC-5)
        dt_est = dt_utc - timedelta(hours=5)
        
        # Format: 11/19/2025 - 09:51 AM EST (14:51 UTC)
        date_str = dt_est.strftime('%m/%d/%Y')
        time_12hr = dt_est.strftime('%I:%M %p')
        time_24hr = dt_utc.strftime('%H:%M')
        
        return f"{date_str} - {time_12hr} EST ({time_24hr} UTC)"
    except (ValueError, AttributeError):
        return timestamp_str


def view_all_jobs(db_path='jobs.db', filter_type=None):
    """Display all jobs in the database."""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Build query based on filter
        if filter_type == 'notified':
            query = 'SELECT * FROM jobs WHERE notified = 1 ORDER BY first_seen DESC'
        elif filter_type == 'new':
            query = 'SELECT * FROM jobs WHERE notified = 0 ORDER BY first_seen DESC'
        else:
            query = 'SELECT * FROM jobs ORDER BY first_seen DESC'
        
        cursor.execute(query)
        jobs = cursor.fetchall()
        
        if not jobs:
            print("\n📭 No jobs found in database.")
            print("Run the tracker first: python -m src.runners.local\n")
            return
        
        # Sort jobs by posted_date (newest first)
        jobs_list = [dict(job) for job in jobs]
        jobs_sorted = sorted(
            jobs_list,
            key=lambda x: x.get('posted_date', ''),
            reverse=True
        )
        
        print(f"\n{'='*80}")
        print(f"📊 DATABASE CONTENTS: {len(jobs_sorted)} job(s)")
        print(f"{'='*80}\n")
        
        for i, job in enumerate(jobs_sorted, 1):
            notified_status = "✅ Emailed" if job['notified'] else "📝 Not emailed yet"
            
            print(f"{i}. {job['title']}")
            print(f"   Company: {job['company']}")
            print(f"   Location: {job['location']}")
            
            # Format posted date
            if job['posted_date']:
                formatted_posted = format_timestamp(job['posted_date'])
                print(f"   Posted: {formatted_posted}")
            
            # Show salary if available
            if job['salary_min'] and job['salary_max']:
                print(f"   Salary: ${job['salary_min']:,.0f} - ${job['salary_max']:,.0f}")
            
            print(f"   Status: {notified_status}")
            print(f"   Added to DB: {job['first_seen']}")
            print(f"   URL: {job['url']}")
            print(f"   ID: {job['job_id']}")
            print()
            print("-" * 80)
            print()
        
        # Summary
        cursor.execute('SELECT COUNT(*) FROM jobs WHERE notified = 1')
        notified_count = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM jobs WHERE notified = 0')
        new_count = cursor.fetchone()[0]
        
        print(f"📈 SUMMARY:")
        print(f"   Total jobs: {len(jobs)}")
        print(f"   Emailed: {notified_count}")
        print(f"   Not yet emailed: {new_count}")
        print()
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    except FileNotFoundError:
        print(f"❌ Database file not found: {db_path}")
        print("Run the tracker first: python -m src.runners.local")


def show_count(db_path='jobs.db'):
    """Just show the count of jobs."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM jobs')
        total = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM jobs WHERE notified = 1')
        notified = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM jobs WHERE notified = 0')
        new = cursor.fetchone()[0]
        
        print(f"\n📊 Database Statistics:")
        print(f"   Total jobs: {total}")
        print(f"   Emailed: {notified}")
        print(f"   Not yet emailed: {new}\n")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='View jobs in your SQLite database'
    )
    parser.add_argument(
        '--count', 
        action='store_true',
        help='Show only count statistics'
    )
    parser.add_argument(
        '--notified', 
        action='store_true',
        help='Show only jobs that have been emailed'
    )
    parser.add_argument(
        '--new', 
        action='store_true',
        help='Show only jobs that have NOT been emailed'
    )
    parser.add_argument(
        '--db',
        default='jobs.db',
        help='Path to database file (default: jobs.db)'
    )
    
    args = parser.parse_args()
    
    if args.count:
        show_count(args.db)
    elif args.notified:
        view_all_jobs(args.db, filter_type='notified')
    elif args.new:
        view_all_jobs(args.db, filter_type='new')
    else:
        view_all_jobs(args.db)

