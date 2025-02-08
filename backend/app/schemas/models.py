from pydantic import BaseModel, Field
from typing import List, Optional, TypedDict, Literal, Tuple, Dict, Any

from pyparsing import Opt

class JobData(BaseModel):
    title: str = Field(default="")
    job_type: str = Field(default="")
    description: str = Field(default="")
    posted_date: str = Field(default="")
    company: str = Field(default="")
    location: str = Field(default="")
    url: Optional[str] = None
    source: str = Field(default="careerjet")

    def to_dict(self) -> Dict[str, Any]:
        """Convert JobData to dictionary format"""
        return {
            "title": self.title,
            "job_type": self.job_type,
            "description": self.description,
            "posted_date": self.posted_date,
            "company": self.company,
            "location": self.location,
            "url": self.url,
            "source": self.source
        }

class AgentState(TypedDict):
    session_id: str
    # user_id: Optional[str]
    query: str
    data: Optional[List[JobData]]
    validated: bool
    current_tool: Optional[Literal["api_fetcher", "web_search"]]
    retries: int
    response: Optional[dict]
    pagesize: int
    api_exhausted: bool
    web_search_results: Optional[List[str]]
    is_job_query: bool
    chat_history: List[dict]

class SearchResponse(BaseModel):
    status: str
    message: str
    data: Optional[Any]
    source: str

class RefinedQuery(BaseModel):
    original_query: str
    refined_query: str
    is_job_related: bool
    job_title: Optional[str] = None
    location: Optional[str] = None
    experience_level: Optional[str] = None

class QueryComponents(BaseModel):
    job_title: Optional[str] = None
    skills: List[str] = []
    location: Optional[str] = None
    experience_level: Optional[str] = None

class ChatRequest(BaseModel):
    query: str
    pagesize: int = Field(default=6)
    session_id: Optional[str] = None
    chat_history: Optional[List[Dict[str, Any]]] = []

class ChatResponse(BaseModel):
    response: dict
    chat_history: List[dict]
