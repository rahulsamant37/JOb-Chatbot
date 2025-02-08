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
from app.config.settings import JobSearchConfig

from app.schemas.models import JobData, AgentState
from app.tools.CareerJetAPI import CareerjetClient
from app.tools.Green_house import GreenhouseJobClient
from app.tools.Jooble import JoobleClient
from app.utils.common import QueryProcessor

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
        self.query_processor = QueryProcessor()
        # Optional QA pipeline initialization
        self.qa_pipeline = pipeline(
            "question-answering",
            model="deepset/roberta-base-squad2",
            device="cuda:0" if torch.cuda.is_available() else "cpu"
        )

    def general_search(self, state: AgentState) -> AgentState:
        """Handle non-job related queries using DuckDuckGo"""
        try:
            results = self.duckduckgo.run(state['query'])
            if results:
                state['response'] = {
                    "status": "success",
                    "message": "General search results",
                    "data": results.split('\n'),
                    "source": "duckduckgo"
                }
            else:
                state['response'] = {
                    "status": "error",
                    "message": "No results found",
                    "data": None,
                    "source": "duckduckgo"
                }
        except Exception as e:
            logger.error(f"General search error: {str(e)}")
            state['response'] = {
                "status": "error",
                "message": f"Search error: {str(e)}",
                "data": None,
                "source": "duckduckgo"
            }
        return state
    
    def validate_job_data(self, jobs_data: Optional[List[JobData]]) -> bool:
        """Validate job data"""
        if not jobs_data:
            return False
        
        required_fields = ['title', 'company']
        valid_jobs = [
            job for job in jobs_data
            if all(getattr(job, field) for field in required_fields)
        ]
        return len(valid_jobs) > 0

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
            (self._search_jooble, "jooble")
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
        """Search jobs using Careerjet API"""
        try:
            results = self.careerjet_client.search_jobs(keywords=query, location=location)
            jobs = []
            if results and isinstance(results, dict):
                for job in results.get('jobs', []):
                    job_data = JobData(
                        title=job.get("title", "Unknown Title"),
                        company=job.get("company", "Unknown Company"),
                        location=job.get("location", "Not Specified"),
                        url=job.get("url", ""),
                        posted_date=job.get("date", datetime.now().strftime("%Y-%m-%d")),
                        source="careerjet",
                        job_type=job_type or "",
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
        """Search jobs using DuckDuckGo"""
        try:
            # Fix missing tool_input parameter
            search_query = f"{query} jobs {location if location else ''}"
            result = self.duckduckgo.run(tool_input=search_query)
            jobs = []
            if result and isinstance(result, str):  # DuckDuckGo returns string
                job_data = JobData(
                    title=query,
                    company="Search Result",
                    location=location or "Not Specified",
                    url="",
                    posted_date=datetime.now().strftime("%Y-%m-%d"),
                    source="duckduckgo",
                    job_type="",
                    description=result
                )
                jobs.append(job_data)
            return jobs
        except Exception as e:
            self.logger.error(f"DuckDuckGo search error: {e}")
            return []

    def api_fetcher(self, state: AgentState) -> AgentState:
        """Fetch job data from multiple sources"""
        # Check if query is job-related using QueryProcessor
        is_job_related = self.query_processor.is_job_related_query(state.get('query', ''))
        state['is_job_query'] = is_job_related


        state.setdefault('api_exhausted', False)
        state.setdefault('data', [])

        if not is_job_related:
            state['api_exhausted'] = True
            return state

        try:
            # Extract location if present in query
            location = None
            if " in " in state['query']:
                query_parts = state['query'].split(" in ")
                query = query_parts[0]
                location = query_parts[1]
            else:
                query = state['query']
    
            # Call search_jobs with extracted parameters
            search_results = self.search_jobs(
                query=query,
                location=location,
                job_type=None,  # Could be extracted from query if needed
                max_sources=3  # Use all available sources
            )
    
            if search_results and isinstance(search_results, dict):
                state['data'] = search_results.get('jobs', [])
                state['api_exhausted'] = len(state['data']) == 0
                state['sources_used'] = search_results.get('sources_used', [])
                
                # Log success for debugging
                self.logger.info(f"Found {len(state['data'])} jobs from {len(state['sources_used'])} sources")
            else:
                state['api_exhausted'] = True
                state['data'] = []
                self.logger.warning("No results returned from search_jobs")
    
        except Exception as e:
            self.logger.error(f"API fetcher error: {str(e)}")
            state['api_exhausted'] = True
            state['errors'] = [str(e)]
    
        return state

    def web_search(self, state: AgentState) -> AgentState:
        """Search for jobs using DuckDuckGo with enhanced error handling"""
        try:
            query = f"job posting {state['query']}"
            logger.info(f"Performing web search with query: {query}")
            
            results = self.duckduckgo.run(query)
            if results:
                state['web_search_results'] = results.split('\n')
                web_jobs = self.parse_web_search_results(state['web_search_results'])
                
                logger.info(f"Found {len(web_jobs)} jobs from web search")
                
                if state['data']:
                    state['data'].extend(web_jobs)
                else:
                    state['data'] = web_jobs
            else:
                logger.warning("No results from web search")

        except Exception as e:
            logger.error(f"Web search error: {str(e)}")
        return state

    def parse_web_search_results(self, results: List[str]) -> List[JobData]:
        """Extract job information from web search results"""
        jobs = []
        for result in results:
            title_match = re.search(r"(?i)(.+?(?=\s*at\s|$))", result)
            company_match = re.search(r"(?i)at\s+([^|.]+)", result)
            location_match = re.search(r"(?i)in\s+([^|.]+)", result)

            if title_match:
                job = JobData(
                    title=title_match.group(1).strip(),
                    company=company_match.group(1).strip() if company_match else "",
                    location=location_match.group(1).strip() if location_match else "",
                    description=result[:500],
                    source="web",
                    posted_date=datetime.now().strftime("%Y-%m-%d")
                )
                jobs.append(job)
        return jobs

    def general_search(self, state: AgentState) -> AgentState:
        """Handle non-job related queries using DuckDuckGo"""
        try:
            results = self.duckduckgo.run(state['query'])
            if results:
                # Format response for general queries
                state['response'] = {
                    "status": "success",
                    "message": results,  # Use result directly without splitting
                    "data": [results],  # Wrap in list for frontend compatibility
                    "source": "duckduckgo",
                    "is_job_query": False
                }
            else:
                state['response'] = {
                    "status": "error",
                    "message": "Sorry, I couldn't find any relevant information.",
                    "data": None,
                    "source": "duckduckgo",
                    "is_job_query": False
                }
        except Exception as e:
            logger.error(f"General search error: {str(e)}")
            state['response'] = {
                "status": "error", 
                "message": "I encountered an error while searching. Please try again.",
                "data": None,
                "source": "duckduckgo",
                "is_job_query": False
            }
        return state


def create_job_search_agent():
    """Create and configure the job search workflow"""
    agent = JobSearchAgent()
    workflow = StateGraph(AgentState)

    workflow.add_node("api_fetcher", agent.api_fetcher)
    workflow.add_node("web_search", agent.web_search)
    workflow.add_node("general_search", agent.general_search)

    def validator_node(state: AgentState) -> AgentState:
        """Validate results and prepare response"""
        if not state['is_job_query']:
            if not state.get('response'):
                state['response'] = {
                    "status": "success",
                    "message": "Let me search for that information.",
                    "data": None,
                    "is_job_query": False
                }
            return state
            
        state['validated'] = agent.validate_job_data(state['data'])
        if state['validated']:
            state['response'] = {
                "status": "success",
                "data": state['data'],
                "message": "Here are some job recommendations:",
                "is_job_query": True,
                "metadata": {
                    "total_jobs": len(state['data']) if state['data'] else 0,
                    "sources": list(set(job.source for job in state['data']))
                }
            }
        elif state['api_exhausted'] and state.get('web_search_results'):
            state['response'] = {
                "status": "error",
                "message": "No valid job listings found",
                "data": None,
                "is_job_query": True
            }
        return state
    workflow.add_node("validator", validator_node)
    # Define edges
    workflow.add_edge(START, "api_fetcher")
    workflow.add_edge("api_fetcher", "validator")
    workflow.add_edge("web_search", "validator")
    workflow.add_edge("general_search", END)

    def next_step(state: AgentState) -> str:
        """Determine next step in the workflow"""
        if not state['is_job_query']:
            return "general_search"
            
        if state.get('response') and state['response']['status'] != 'error':
            return END
        
        if state['api_exhausted'] and not state.get('web_search_results'):
            return "web_search"
            
        return END

    # Add conditional edges with proper mapping
    workflow.add_conditional_edges(
        "validator",
        next_step
    )

    return agent, workflow.compile()
