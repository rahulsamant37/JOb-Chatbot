from logging import config
import torch
from transformers import pipeline
from langgraph.graph import StateGraph, END, START
from typing import List, Optional, TypedDict, Literal
from pydantic import BaseModel, Field
from careerjet_api_client import CareerjetAPIClient
from langchain_community.tools import DuckDuckGoSearchRun
import re
from datetime import datetime
from app.config.settings import settings
from app.schemas.models import JobData, AgentState
from app.tools.CareerJetAPI import CareerjetClient
from app.utils.common import QueryProcessor
from app.utils.session_memory import memory, save_session_state
import logging

logger = logging.getLogger(__name__)

class JobSearchAgent:
    def __init__(self):
        self.careerjet_client = CareerjetClient()
        self.duckduckgo = DuckDuckGoSearchRun()
        self.query_processor = QueryProcessor()
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

    def api_fetcher(self, state: AgentState) -> AgentState:
        """Fetch job data from Careerjet API"""
        if not state['is_job_query']:
            state['api_exhausted'] = True
            return state
            
        try:
            query = state['query']
            keywords = query
            location = None
            if " in " in query:
                keywords, location = query.split(" in ", 1)
                
            results = self.careerjet_client.search_jobs(keywords, location, state['pagesize'])
            
            if results and results.get('hits', 0) > 0 and results.get('jobs'):
                state['data'] = [
                    JobData(
                        title=job.get('title', ''),
                        job_type=job.get('type', ''),
                        description=job.get('description', ''),
                        posted_date=job.get('date', ''),
                        company=job.get('company', ''),
                        location=job.get('locations', ''),
                        url=job.get('url', ''),
                        source='careerjet'
                    ) for job in results['jobs']
                ]
            else:
                state['api_exhausted'] = True
        except Exception as e:
            logger.error(f"API fetcher error: {str(e)}")
            state['api_exhausted'] = True
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

def create_job_search_agent():
    agent = JobSearchAgent()
    
    workflow = StateGraph(AgentState)
    
    workflow.add_node("api_fetcher", agent.api_fetcher)
    # RAG   
    workflow.add_node("web_search", agent.web_search)
    workflow.add_node("general_search", agent.general_search)
    
    def validator_node(state: AgentState) -> AgentState:
        """Validate results and prepare response"""
        if not state['is_job_query']:
            return state
            
        state['validated'] = agent.validate_job_data(state['data'])

        if state['validated']:
            state['response'] = {
                "status": "success",
                "data": state['data'],
                "metadata": {
                    "total_jobs": len(state['data']) if state['data'] else 0,
                    "sources": list(set(job.source for job in state['data']))
                }
            }
        elif state['api_exhausted'] and state.get('web_search_results'):
            state['response'] = {
                "status": "error",
                "message": "No valid job listings found",
                "data": None
            }
            
        # DB save;
        save_session_state(state["session_id"], state)
            
        return state

    workflow.add_node("validator", validator_node)
    workflow.add_edge(START, "api_fetcher")
    workflow.add_edge("api_fetcher", "validator")
    workflow.add_edge("web_search", "validator")
    workflow.add_edge("general_search", END)

    def next_step(state: AgentState) -> str:
        """Determine next step in the workflow"""
        if not state['is_job_query']:
            return "general_search"
            
        if state.get('response'):
            return END
        
        if state['api_exhausted'] and not state.get('web_search_results'):
            return "web_search"
            
        return END

    workflow.add_conditional_edges(
        "validator",
        next_step
    )

    return workflow.compile(checkpointer=memory)