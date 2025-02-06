from pydantic import BaseModel, Field
from careerjet_api_client import CareerjetAPIClient
from dotenv import load_dotenv
import os
from typing import Dict, Any
import json
import logging

logger = logging.getLogger(__name__)

load_dotenv()
# affid=os.getenv("CAREERJET_AFFID")


class CareerjetClient:
    def __init__(self, affid='cd918e610ecfbcd6cc50f9527541794c'):
        self.cj_client = CareerjetAPIClient("en_US")
        self.affid = affid

    def search_jobs(self, keywords, location=None, pagesize=10) -> Dict[str, Any]:
        try:
            search_params = {
                'keywords': keywords,
                'location': location or '',
                'affid': self.affid,
                'user_ip': '11.22.33.44',
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'url': 'https://www.example.com/jobs',
                'pagesize': pagesize
            }
            
            logger.info(f"Searching with parameters: {json.dumps(search_params, indent=2)}")
            
            response = self.cj_client.search(search_params)
            
            if response:
                logger.info(f"API Response received: {len(response.get('jobs', []))} jobs found")
                return response
            else:
                logger.warning("Empty response from Careerjet API")
                return {"hits": 0, "jobs": []}
                
        except Exception as e:
            logger.error(f"Careerjet API error: {str(e)}")
            raise