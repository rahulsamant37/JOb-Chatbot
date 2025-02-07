import logging
from fastapi import FastAPI
from app.schemas.models import ChatRequest, ChatResponse
from app.agents.job_search_agent import create_job_search_agent
from app.utils.common import create_query_processor




from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:5173",
    # add other allowed origins if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # allow specified origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/search")
async def search():
    return {"message": "Search endpoint response"}

logging.basicConfig(level=logging.INFO)



@app.get("/")
async def root():
    return {"message": "Welcome to the Job Search Chatbot API"}

@app.post("/search", response_model=ChatResponse)
async def job_search(request: ChatRequest):
    logging.info(f"Received request: {request}")
    try:
        processor = create_query_processor()
        refined_query = processor.process_query(request.query)
        workflow = create_job_search_agent()  # Create the workflow
        initial_state = {
            "query": refined_query.refined_query if refined_query.is_job_related else request.query,
            "data": None,
            "validated": False,
            "current_tool": "api_fetcher",
            "retries": 0,
            "response": None,
            "pagesize": request.pagesize,
            "api_exhausted": False,
            "web_search_results": None,
            "is_job_query": refined_query.is_job_related,
            "chat_history": request.chat_history
        }
        
        result = workflow.invoke(initial_state)  # Invoke the workflow
        logging.info(f"Agent result: {result}")
        return ChatResponse(
            response=result['response'],
            chat_history=result['chat_history']
        )
        
    except Exception as e:
        logging.error(f"Error processing request: {e}")
        return ChatResponse(
            response={
                "status": "error",
                "message": str(e)
            },
            chat_history=request.chat_history
        )