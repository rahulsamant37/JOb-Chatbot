# memory.py

from typing import List, Dict, Optional, Any
from datetime import datetime
import threading
from pydantic import BaseModel
from app.schemas.models import JobData

class ChatMessage(BaseModel):
    """Matches frontend ChatMessage interface"""
    user: str  # 'ai' | 'user'
    message: str
    jobData: Optional[List[Dict[str, Any]]] = None
    timestamp: datetime = datetime.now()

class ChatMemory:
    def __init__(self):
        self._sessions: Dict[str, List[ChatMessage]] = {}
        self._lock = threading.Lock()

    def add_user_message(self, session_id: str, message: str) -> None:
        """Add a user message to the chat history"""
        chat_message = ChatMessage(
            user="user",
            message=message
        )
        with self._lock:
            if session_id not in self._sessions:
                self._sessions[session_id] = []
            self._sessions[session_id].append(chat_message)

    def add_ai_message(self, 
                      session_id: str, 
                      message: str, 
                      job_data: Optional[List[JobData]] = None) -> None:
        """Add an AI response to the chat history"""

        # Convert JobData objects to dictionaries if present
        job_data_dicts = None
        if job_data:
            job_data_dicts = [
                job.to_dict() if isinstance(job, JobData) else job 
                for job in job_data
            ]

        chat_message = ChatMessage(
            user="ai",
            message=message,
            jobData=job_data_dicts
        )

        with self._lock:
            if session_id not in self._sessions:
                self._sessions[session_id] = []
            self._sessions[session_id].append(chat_message)

    def get_chat_history(self, session_id: str) -> List[Dict]:
        """Get chat history in format matching frontend expectations"""
        with self._lock:
            messages = self._sessions.get(session_id, [])
            return [msg.dict() for msg in messages]

    def get_recent_messages(self, session_id: str, limit: int = 6) -> List[Dict]:
        """Get most recent messages for context"""
        with self._lock:
            messages = self._sessions.get(session_id, [])
            return [msg.dict() for msg in messages[-limit:]]

    def clear_session(self, session_id: str) -> None:
        """Clear chat history for a session"""
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]

    def update_agent_state(self, session_id: str) -> Dict[str, Any]:
        """Convert chat history to agent state format"""
        history = self.get_chat_history(session_id)
        return {
            "session_id": session_id,
            "chat_history": history,
            "data": None,
            "validated": False,
            "current_tool": "api_fetcher",
            "retries": 0,
            "response": None,
            "api_exhausted": False,
            "web_search_results": None,
            "is_job_query": True
        }