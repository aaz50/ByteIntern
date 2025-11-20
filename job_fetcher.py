import requests
from typing import List, Dict
from datetime import datetime, timedelta
import config

class JobFetcher:
    def __init__(self):
        self.app_id = config.ADZUNA_APP_ID
        self.api_key = config.ADZUNA_API_KEY
        self.base_url = "https://api.adzuna.com/v1/api/jobs"
    
    def fetch_jobs(self, keywords: str, country: str = "us", 
                   location: str = None, max_days_old: int = 7) -> List[Dict]:
        """
        Fetch jobs from Adzuna API
        
        Args:
            keywords: Search keywords (e.g., "software engineer intern")
            country: Country code (default: "us")
            location: Specific location filter
            max_days_old: Only return jobs posted in last N days
        
        Returns:
            List of job dictionaries
        """
        url = f"{self.base_url}/{country}/search/1"
        
        params = {
            'app_id': self.app_id,
            'app_key': self.api_key,
            'what': keywords,
            'results_per_page': 50,
            'content-type': 'application/json'
        }
        
        if location:
            params['where'] = location
        
        # Filter by date - only jobs posted in last N days
        max_age_days = max_days_old
        params['max_days_old'] = max_age_days
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            jobs = data.get('results', [])
            
            print(f"Fetched {len(jobs)} jobs from Adzuna")
            
            # Transform to our format
            transformed_jobs = []
            for job in jobs:
                transformed_job = {
                    'id': str(job['id']),
                    'title': job['title'],
                    'company': job['company']['display_name'],
                    'location': job['location']['display_name'],
                    'url': job['redirect_url'],
                    'description': job.get('description', ''),
                    'posted_date': job['created'],
                    'salary_min': job.get('salary_min'),
                    'salary_max': job.get('salary_max')
                }
                transformed_jobs.append(transformed_job)
            
            return transformed_jobs
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching jobs: {e}")
            return []
    
    def fetch_all_locations(self, keywords: str, locations: List[str], 
                           max_days_old: int = 7) -> List[Dict]:
        """
        Fetch jobs from multiple locations
        
        Args:
            keywords: Search keywords
            locations: List of location strings
            max_days_old: Only return jobs posted in last N days
        
        Returns:
            Combined list of jobs from all locations
        """
        all_jobs = []
        seen_ids = set()
        
        for location in locations:
            print(f"Searching in: {location}")
            jobs = self.fetch_jobs(keywords, location=location, max_days_old=max_days_old)
            
            # Deduplicate by job ID
            for job in jobs:
                if job['id'] not in seen_ids:
                    all_jobs.append(job)
                    seen_ids.add(job['id'])
        
        print(f"Total unique jobs found: {len(all_jobs)}")
        return all_jobs

# Test function
if __name__ == "__main__":
    config.validate_config()
    
    fetcher = JobFetcher()
    jobs = fetcher.fetch_jobs("software engineer intern", max_days_old=7)
    
    print(f"\nSample jobs:")
    for job in jobs[:3]:
        print(f"- {job['title']} at {job['company']}")
        print(f"  Location: {job['location']}")
        print(f"  URL: {job['url']}\n")
