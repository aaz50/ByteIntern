"""
Job fetching module - handles API calls to job aggregation services.

Currently supports Adzuna API, but can be extended to support other sources.
"""

import requests
from typing import List, Dict, Optional
from src.core import config


class JobFetcher:
    """Fetches job postings from external APIs."""
    
    def __init__(self):
        self.app_id = config.ADZUNA_APP_ID
        self.api_key = config.ADZUNA_API_KEY
        self.base_url = "https://api.adzuna.com/v1/api/jobs"
    
    def fetch_jobs(
        self, 
        keywords: str, 
        country: str = "us", 
        location: Optional[str] = None, 
        max_days_old: int = 7
    ) -> List[Dict]:
        """
        Fetch jobs from Adzuna API.
        
        Args:
            keywords: Search keywords (e.g., "software engineer intern")
            country: Country code (default: "us")
            location: Specific location filter (optional)
            max_days_old: Only return jobs posted in last N days
        
        Returns:
            List of job dictionaries with standardized fields
        """
        url = f"{self.base_url}/{country}/search/1"
        
        params = {
            'app_id': self.app_id,
            'app_key': self.api_key,
            'what': keywords,
            'results_per_page': 50,
            'content-type': 'application/json',
            'max_days_old': max_days_old
        }
        
        if location:
            params['where'] = location
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            jobs = data.get('results', [])
            
            print(f"✓ Fetched {len(jobs)} jobs from Adzuna")
            
            # Transform to standardized format
            return [self._transform_job(job) for job in jobs]
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error fetching jobs: {e}")
            return []
    
    def fetch_all_locations(
        self, 
        keywords: str, 
        locations: List[str], 
        max_days_old: int = 7
    ) -> List[Dict]:
        """
        Fetch jobs from multiple locations and deduplicate.
        
        Args:
            keywords: Search keywords
            locations: List of location strings
            max_days_old: Only return jobs posted in last N days
        
        Returns:
            Combined list of unique jobs from all locations
        """
        all_jobs = []
        seen_ids = set()
        
        for location in locations:
            print(f"  Searching in: {location}")
            jobs = self.fetch_jobs(
                keywords, 
                location=location, 
                max_days_old=max_days_old
            )
            
            # Deduplicate by job ID
            for job in jobs:
                if job['id'] not in seen_ids:
                    all_jobs.append(job)
                    seen_ids.add(job['id'])
        
        print(f"✓ Total unique jobs found: {len(all_jobs)}")
        return all_jobs
    
    def _transform_job(self, raw_job: Dict) -> Dict:
        """
        Transform raw API response to standardized format.
        
        This allows us to swap APIs later without changing downstream code.
        """
        return {
            'id': str(raw_job['id']),
            'title': raw_job['title'],
            'company': raw_job['company']['display_name'],
            'location': raw_job['location']['display_name'],
            'url': raw_job['redirect_url'],
            'description': raw_job.get('description', ''),
            'posted_date': raw_job['created'],
            'salary_min': raw_job.get('salary_min'),
            'salary_max': raw_job.get('salary_max')
        }


# Test function for standalone execution
if __name__ == "__main__":
    config.validate_config()
    
    fetcher = JobFetcher()
    jobs = fetcher.fetch_jobs("software engineer intern", max_days_old=7)
    
    print(f"\n📋 Sample jobs:")
    for job in jobs[:3]:
        print(f"  • {job['title']} at {job['company']}")
        print(f"    Location: {job['location']}")
        print(f"    URL: {job['url']}\n")
