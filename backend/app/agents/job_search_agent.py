import logging
import torch
from typing import List, Optional, Dict, Any
from datetime import datetime
import re

from pydantic import BaseModel, Field, ValidationError
from transformers import pipeline
from langgraph.graph import StateGraph, END, START
from langchain_community.tools import DuckDuckGoSearchRun

from app.config.settings import settings
try:
    from app.config.settings import JobSearchConfig
except ImportError:
    class JobSearchConfig:
        DEFAULT_PAGESIZE = 10
        MAX_SOURCES = 3

from app.schemas.models import JobData, AgentState
from app.tools.CareerJetAPI import CareerjetClient
from app.tools.Green_house import GreenhouseJobClient
from app.tools.Jooble import JoobleClient
from app.utils.common import QueryProcessor
from app.utils.session_memory import memory, save_session_state

logger = logging.getLogger(__name__)

class JobSearchAgent:
    def __init__(self, pagesize: int = JobSearchConfig.DEFAULT_PAGESIZE):
        """
        Initialize multi-source job search agent
        """
        self.pagesize = pagesize
        self.logger = logging.getLogger(__name__)
        # Initialize search clients and tools
        self.careerjet_client = CareerjetClient()
        self.greenhouse_client = GreenhouseJobClient()
        self.jooble_client = JoobleClient()
        self.duckduckgo = DuckDuckGoSearchRun()
        # Optional QA pipeline initialization
        self.qa_pipeline = self._init_qa_pipeline()

    def _init_qa_pipeline(self):
        """Initialize Question-Answering pipeline"""
        try:
            return pipeline(
                "question-answering",
                model="deepset/roberta-base-squad2",
                device="cuda:0" if torch.cuda.is_available() else "cpu"
            )
        except Exception as e:
            self.logger.warning(f"QA Pipeline init failed: {e}")
            return None

    def search_jobs(
        self, 
        query: str, 
        location: Optional[str] = None,
        job_type: Optional[str] = None,
        max_sources: int = JobSearchConfig.MAX_SOURCES
    ) -> Dict[str, Any]:
        """
        Comprehensive job search across multiple sources
        """
        results = {
            "total_jobs": 0,
            "jobs": [],
            "sources_used": [],
            "errors": []
        }
        # Source-specific search methods
        search_methods = [
            (self._search_careerjet, "careerjet"),
            (self._search_greenhouse, "greenhouse"),
            (self._search_jooble, "jooble"),
            (self._search_duckduckgo, "duckduckgo")
        ]
        for search_method, source_name in search_methods:
            if len(results['sources_used']) >= max_sources:
                break
            try:
                source_results = search_method(query, location, job_type)
                if source_results:
                    results['jobs'].extend(source_results)
                    results['sources_used'].append(source_name)
                    results['total_jobs'] += len(source_results)
            except Exception as e:
                error_msg = f"{source_name.capitalize()} search error: {str(e)}"
                self.logger.error(error_msg)
                results['errors'].append(error_msg)
        
        # Sort jobs by posted_date (with robust parsing) and limit by pagesize
        results['jobs'] = sorted(
            results['jobs'], 
            key=lambda x: self._parse_date(x.posted_date), 
            reverse=True
        )[:self.pagesize]
        return results

    def _parse_date(self, date_str: Optional[str]) -> datetime:
        """
        Parse the date string using multiple formats.
        If parsing fails, return the current date.
        """
        if not date_str:
            return datetime.now()
        try:
            for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d"]:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            return datetime.now()
        except Exception:
            return datetime.now()

    def _search_careerjet(self, query: str, location: Optional[str], job_type: Optional[str]) -> List[JobData]:
        """
        Search jobs using Careerjet API via CareerjetClient.
        """
        try:
            results = self.careerjet_client.search_jobs(query=query, location=location, job_type=job_type)
            jobs = []
            for job in results:
                job_data = JobData(
                    title=job.get("title", "Unknown Title"),
                    company=job.get("company", "Unknown Company"),
                    location=job.get("location", "Not Specified"),
                    url=job.get("url", ""),
                    posted_date=job.get("posted_date", datetime.now().strftime("%Y-%m-%d")),
                    source="careerjet",
                    job_type=job.get("job_type", ""),
                    description=job.get("description", "")
                )
                jobs.append(job_data)
            return jobs
        except Exception as e:
            self.logger.error(f"Careerjet search error: {e}")
            return []

    def _search_greenhouse(self, query: str, location: Optional[str], job_type: Optional[str]) -> List[JobData]:
        """
        Search jobs using Greenhouse API via GreenhouseJobClient.
        """
        try:
            # Here query is used as a company identifier placeholder.
            results = self.greenhouse_client.search_jobs(company=query, keyword=job_type)
            jobs = []
            for job in results:
                job_data = JobData(
                    title=job.get("title", "Unknown Title"),
                    company=job.get("company", "Unknown Company"),
                    location=job.get("location", "Not Specified"),
                    url=job.get("url", ""),
                    posted_date=job.get("posted_date", datetime.now().strftime("%Y-%m-%d")),
                    source="greenhouse",
                    job_type="",
                    description=""
                )
                jobs.append(job_data)
            return jobs
        except Exception as e:
            self.logger.error(f"Greenhouse search error: {e}")
            return []

    def _search_jooble(self, query: str, location: Optional[str], job_type: Optional[str]) -> List[JobData]:
        """
        Search jobs using Jooble API via JoobleClient.
        """
        try:
            results = self.jooble_client.search_jobs(keywords=query, location=location)
            jobs = []
            for job in results.get("jobs", []):
                job_data = JobData(
                    title=job.get("title", "Unknown Title"),
                    company=job.get("company", "Unknown Company"),
                    location=job.get("location", "Not Specified"),
                    url=job.get("url", ""),
                    posted_date=job.get("posted_date", datetime.now().strftime("%Y-%m-%d")),
                    source="jooble",
                    job_type="",
                    description=""
                )
                jobs.append(job_data)
            return jobs
        except Exception as e:
            self.logger.error(f"Jooble search error: {e}")
            return []

    def _search_duckduckgo(self, query: str, location: Optional[str], job_type: Optional[str] = None) -> List[JobData]:
        """
        Search jobs using DuckDuckGo via DuckDuckGoSearchRun.
        """
        try:
            result = self.duckduckgo.run(query=query)
            jobs = []
            if result and isinstance(result, dict) and "AbstractText" in result:
                job_data = JobData(
                    title=result.get("Heading", "Unknown Title"),
                    company="DuckDuckGo",
                    location=location or "Not Specified",
                    url=result.get("AbstractURL", ""),
                    posted_date=datetime.now().strftime("%Y-%m-%d"),
                    source="duckduckgo",
                    job_type="",
                    description=result.get("AbstractText", "")
                )
                jobs.append(job_data)
            return jobs
        except Exception as e:
            self.logger.error(f"DuckDuckGo search error: {e}")
            return []

    def api_fetcher(self, state: AgentState) -> AgentState:
        """
        Fetch job data from multiple sources
        """
        state.setdefault('is_job_query', True)
        state.setdefault('api_exhausted', False)
        state.setdefault('data', [])
        try:
            search_results = self.search_jobs(
                query=state.get('query', ''),
                location=state.get('location'),
                job_type=state.get('job_type')
            )
            state['data'] = search_results['jobs']
            state['api_exhausted'] = len(search_results['jobs']) == 0
            state['sources_used'] = search_results['sources_used']
        except Exception as e:
            self.logger.error(f"API fetcher error: {e}")
            state['api_exhausted'] = True
            state['errors'] = [str(e)]
        return state

    def web_search(self, state: AgentState) -> AgentState:
        """
        Perform web search as fallback when API sources are exhausted
        """
        if not state.get('api_exhausted', False):
            return state
        try:
            duckduckgo_results = self._search_duckduckgo(
                query=state.get('query', ''),
                location=state.get('location')
            )
            state['web_search_results'] = duckduckgo_results
            state.setdefault('data', [])
            state['data'].extend(duckduckgo_results)
        except Exception as e:
            self.logger.error(f"Web search error: {e}")
        return state

    def validate_job_data(self, jobs: List[JobData]) -> List[JobData]:
        """
        Validate job data, removing entries with missing critical information
        """
        validated_jobs = []
        for job in jobs:
            try:
                validated_job = JobData(
                    title=job.title or 'Unknown Title',
                    company=job.company or 'Unknown Company',
                    location=job.location or 'Not Specified',
                    url=job.url or '',
                    source=job.source or 'unknown',
                    posted_date=job.posted_date or datetime.now().strftime("%Y-%m-%d"),
                    job_type=job.job_type or "",
                    description=job.description or ""
                )
                validated_jobs.append(validated_job)
            except ValidationError as e:
                self.logger.warning(f"Job validation failed: {e}")
        return validated_jobs

    def general_search(self, state: AgentState) -> AgentState:
        """
        Handle non-job search queries
        """
        state['is_job_query'] = False
        state['response'] = {
            "status": "not_applicable",
            "message": "Query does not match job search criteria"
        }
        return state

def create_job_search_agent():
    """
    Create and configure the job search workflow
    """
    agent = JobSearchAgent()
    workflow = StateGraph(AgentState)
    # Register nodes for each stage
    workflow.add_node("api_fetcher", agent.api_fetcher)
    workflow.add_node("web_search", agent.web_search)
    workflow.add_node("general_search", agent.general_search)
    
    def validator_node(state: AgentState) -> AgentState:
        """Validate results and prepare response"""
        if not state.get('is_job_query', True):
            return agent.general_search(state)
        # Validate job listings
        state['data'] = agent.validate_job_data(state.get('data', []))
        if state['data']:
            state['response'] = {
                "status": "success",
                "data": state['data'],
                "metadata": {
                    "total_jobs": len(state['data']),
                    "sources": list(set(job.source for job in state['data']))
                }
            }
        else:
            state['response'] = {
                "status": "error",
                "message": "No valid job listings found",
                "data": None
            }
        # Save session state
        save_session_state(state.get("session_id"), state)
        return state

    workflow.add_node("validator", validator_node)
    # Define workflow edges
    workflow.add_edge(START, "api_fetcher")
    workflow.add_edge("api_fetcher", "validator")
    workflow.add_edge("web_search", "validator")
    workflow.add_edge("general_search", END)
    
    def next_step(state: AgentState) -> str:
        """Determine next step in the workflow"""
        if not state.get('is_job_query', True):
            return "general_search"
        if state.get('response'):
            return END
        if state.get('api_exhausted', False) and not state.get('web_search_results'):
            return "web_search"
        return END

    workflow.add_conditional_edges("validator", next_step)
    return workflow.compile(checkpointer=memory)
