import logging
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uuid
from app.schemas.models import ChatRequest, ChatResponse, JobData
from app.agents.job_search_agent import create_job_search_agent
from app.utils.common import create_query_processor
from app.utils.memory import ChatMemory

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Job Search Chatbot API")

# CORS configuration
origins = [
    "http://localhost:5173",
    # Add other allowed origins as needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize chat memory as a global instance
chat_memory = ChatMemory()

@app.get("/")
async def root():
    """Root endpoint returning welcome message"""
    return {"message": "Welcome to the Job Search Chatbot API"}

# backend/app/main.py

@app.post("/search", response_model=ChatResponse)
async def job_search(request: ChatRequest):
    logger.info(f"Processing job search request - Session ID: {request.session_id}")
    
    try:
        # Generate or use existing session ID
        session_id = request.session_id or str(uuid.uuid4())
        
        # Store user message
        chat_memory.add_user_message(session_id, request.query)
        
        # Process query
        processor = create_query_processor()
        refined_query = processor.process_query(request.query)
        
        # Create workflow
        agent, workflow = create_job_search_agent()
        if not workflow:
            raise ValueError("Failed to create workflow")
            
        # Prepare initial state
        initial_state = chat_memory.update_agent_state(session_id)
        initial_state.update({
            "query": refined_query.refined_query if refined_query.is_job_related else request.query,
            "is_job_query": refined_query.is_job_related,
            "pagesize": request.pagesize or 6
        })
        
        # Execute workflow
        result = workflow.invoke(initial_state)
        
        # Process response
        if result['response']['status'] == 'success':
            if result['response'].get('is_job_query', False):
                job_data = [
                    job.to_dict() if isinstance(job, JobData) else job 
                    for job in result['response'].get('data', [])
                ]
                chat_memory.add_ai_message(
                    session_id,
                    "Here are some job recommendations:",
                    job_data
                )
            else:
                # Handle general search response
                chat_memory.add_ai_message(
                    session_id,
                    str(result['response']['message'])  # Convert to string
                )
        else:
            chat_memory.add_ai_message(
                session_id, 
                result['response'].get('message', 'No results found')
            )
            
        return ChatResponse(
            response=result['response'],
            chat_history=chat_memory.get_chat_history(session_id)
        )
        
    except Exception as e:
        logger.error(f"Error in job search: {str(e)}", exc_info=True)
        error_msg = "An unexpected error occurred while processing your request"
        chat_memory.add_ai_message(session_id, error_msg)
        raise HTTPException(status_code=500, detail=error_msg)