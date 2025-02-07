import os
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import requests
import json
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

api_key = os.getenv("JOOBLE_API_KEY")

class JoobleClient:
    def __init__(self, api_key: Optional[str] = api_key):
        """
        Initialize Jooble API client.
        
        Args:
            api_key (str, optional): Jooble API key. If not provided, 
                                     tries to fetch from environment variable.
        """
        self.api_key = api_key
        if not self.api_key:
            raise ValueError("Jooble API key must be provided")
        
        self.base_url = f"https://jooble.org/api/{self.api_key}"

    def search_jobs(
        self, 
        keywords: str = "Python Developer", 
        location: str = "Chandigarh", 
        radius: Optional[int] = None, 
        page: int = 1, 
        companysearch: bool = False
    ) -> Dict[str, Any]:
        """
        Search for jobs using Jooble API.
        
        Args:
            keywords (str): Job search keywords
            location (str): Job location
            radius (int, optional): Search radius in kilometers
            page (int): Page number of results
            companysearch (bool): Search in company names
        
        Returns:
            Dict containing job search results
        """
        try:
            payload = {
                "keywords": keywords,
                "location": location,
                "page": str(page),
                "companysearch": "true" if companysearch else "false"
            }
            
            if radius:
                payload["radius"] = str(radius)
            
            logger.info(f"Searching jobs with parameters: {json.dumps(payload, indent=2)}")
            
            response = requests.post(self.base_url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            
            logger.info(f"API Response: {len(data.get('jobs', []))} jobs found")
            
            return data
        
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err}")
            raise
        except requests.exceptions.RequestException as req_err:
            logger.error(f"Request error occurred: {req_err}")
            raise
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON response")
            raise