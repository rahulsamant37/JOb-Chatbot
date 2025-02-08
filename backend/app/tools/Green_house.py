import requests
import logging
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class GreenhouseJobClient:
    """
    Client for searching jobs on Greenhouse job boards.
    """
    BASE_URL = "https://boards-api.greenhouse.io/v1/boards/{company}/jobs"

    def __init__(self, timeout: int = 6):
        """
        Initialize Greenhouse Job Client.
        
        Args:
            timeout (int): Request timeout in seconds
        """
        self.timeout = timeout

    def search_jobs(
        self, 
        company: str, 
        keyword: Optional[str] = None, 
        department: Optional[str] = None
    ) -> List[Dict]:
        """
        Search for jobs on a specific Greenhouse job board.
        
        Args:
            company: Company identifier in Greenhouse job board URL
            keyword: Optional keyword to filter job titles
            department: Optional department to filter jobs
        
        Returns:
            List of matching jobs
        """
        url = self.BASE_URL.format(company=company)
        
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            jobs = data.get('jobs', [])
            
            # Apply filters
            filtered_jobs = self._filter_jobs(jobs, keyword, department)
            
            logger.info(f"Found {len(filtered_jobs)} jobs for {company}")
            return filtered_jobs
        
        except requests.RequestException as e:
            logger.error(f"Error fetching jobs for {company}: {e}")
            return []

    def _filter_jobs(
        self, 
        jobs: List[Dict], 
        keyword: Optional[str] = None, 
        department: Optional[str] = None
    ) -> List[Dict]:
        """
        Filter jobs based on keyword and department.
        
        Args:
            jobs: List of job dictionaries
            keyword: Optional keyword to filter job titles
            department: Optional department to filter jobs
        
        Returns:
            Filtered list of jobs
        """
        filtered_jobs = jobs

        if keyword:
            filtered_jobs = [
                job for job in filtered_jobs 
                if keyword.lower() in job.get('title', '').lower()
            ]
        
        if department:
            filtered_jobs = [
                job for job in filtered_jobs 
                if department.lower() in job.get('departments', [{}])[0].get('name', '').lower()
            ]
        
        return filtered_jobs