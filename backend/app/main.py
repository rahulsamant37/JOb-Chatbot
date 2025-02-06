import logging
from fastapi import FastAPI, Depends
# 
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2, OAuth2AuthorizationCodeBearer, OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from authlib.integrations.starlette_client import OAuth

import uuid

from streamlit import form
from app.utils.auth import authenticate_user, create_access_token, get_current_user
from app.utils.session_memory import memory, load_session_state

# 
from app.schemas.models import ChatRequest, ChatResponse
from app.agents.job_search_agent import create_job_search_agent
from app.utils.common import create_query_processor
# import spacy
# spacy.load('en_core_web_sm')
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials =True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware For OAuth
# app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET", "your_secret_key"))

# OAuth Config:
# OAUTH_CLIENT_ID = os.getenv("OAUTH_CLIENT_ID", "your_client_id")
# OAUTH_CLIENT_SECRET = os.getenv("OAUTH_CLIENT_SECRET", "your_client_secret")
# OAUTH_REDIRECT_URI = "http://localhost:8000/auth/callback"


logging.basicConfig(level=logging.INFO)

@app.get("/")
async def root():
    return {"message": "Welcome to the Job Search Chatbot API"}



# Auth, routes:
@app.post("/auth/signup")
async def signup(email:str, password:str):
    # if email in database (condition already a user check) raise "User Exists Exception"
    # else
    # collect hashed password & email and store to database 
    # return "User Registered successfully"
    pass

@app.post("auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # user = authenticate_user(form_data.username, form_data.password)
    # if not user:
    #     raise "Invalid Credentials"
    # token = create_access_token({"sub" : user["email"]})
    # return {"access_token": token, "token_type": "bearer"}
    pass

# Protected route [token verify by get_current_user]
@app.post("/search", response_model=ChatResponse)
async def job_search(request: ChatRequest, user: dict= Depends(get_current_user)):
    logging.info(f"Received request: {request}")
    try:
        
        # ghelani...
        session_id = request.chat_history[0].get("session_id") if request.chat_history else str(uuid.uuid4())
        # user_id = request.chat_history[0].get("user_id") if request.chat_history else None

        past_state = load_session_state(session_id)
        if past_state:
            initial_state = past_state
        # else: ->
        processor = create_query_processor()
        refined_query = processor.process_query(request.query)
        initial_state = {
            "session_id": session_id,
            # "user_id": user_id,
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
        
        workflow = create_job_search_agent()  # Create the workflow
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