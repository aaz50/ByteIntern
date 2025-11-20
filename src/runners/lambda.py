"""
AWS Lambda handler for job tracker.

This will be the entry point when deployed to AWS Lambda.
The core logic remains the same - this just adapts it for Lambda's execution model.

FUTURE IMPLEMENTATION - Not needed for Phase 1 (GitHub Actions)
"""

import os
import json
from datetime import datetime
from src.core import (
    validate_config,
    JobFetcher,
    get_storage,
    EmailNotifier,
    config
)


def lambda_handler(event, context):
    """
    AWS Lambda handler function.
    
    This function will be triggered by EventBridge (CloudWatch Events) on a schedule.
    
    Args:
        event: Lambda event data (from EventBridge)
        context: Lambda context object
        
    Returns:
        Response dict with status code and results
    """
    print(f"Job Tracker Lambda triggered at {datetime.now()}")
    
    try:
        # Validate configuration (using environment variables)
        validate_config()
        
        # Initialize components
        # Note: If using SQLite on Lambda, you'll need to:
        # 1. Download from S3 at start
        # 2. Upload to S3 at end
        # Or switch to DynamoDB by setting DB_TYPE=dynamodb
        
        storage = get_storage()
        fetcher = JobFetcher()
        notifier = EmailNotifier()
        
        # Fetch jobs
        print("Fetching jobs...")
        jobs = fetcher.fetch_all_locations(
            keywords=config.SEARCH_KEYWORDS,
            locations=config.SEARCH_LOCATIONS,
            max_days_old=config.MAX_DAYS_OLD
        )
        
        # Filter for new jobs
        print("Checking for new jobs...")
        new_jobs = []
        for job in jobs:
            if storage.is_new_job(job['id']):
                new_jobs.append(job)
                storage.add_job(job)
        
        # Send notifications
        if new_jobs:
            print(f"Sending notification for {len(new_jobs)} new jobs")
            success = notifier.send_notification(new_jobs)
            
            if success:
                for job in new_jobs:
                    storage.mark_as_notified(job['id'])
        
        # Return success response
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Job check complete',
                'jobs_found': len(jobs),
                'new_jobs': len(new_jobs),
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        print(f"Error in Lambda execution: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
        }


# For local testing of Lambda handler
if __name__ == "__main__":
    # Simulate Lambda event/context
    test_event = {}
    
    class MockContext:
        function_name = "job-tracker"
        memory_limit_in_mb = 128
        invoked_function_arn = "arn:aws:lambda:us-east-1:123456789:function:job-tracker"
        aws_request_id = "test-request-id"
    
    result = lambda_handler(test_event, MockContext())
    print(f"\nLambda result: {json.dumps(result, indent=2)}")
