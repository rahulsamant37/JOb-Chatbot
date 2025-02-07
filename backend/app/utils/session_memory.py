import os
import logging
from typing import Optional, Dict, Any, Union
from datetime import datetime

from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver
from pymongo import MongoClient, errors
from pymongo.collection import Collection
from pymongo.database import Database

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGODB_DB_NAME", "Memory")
COLLECTION_NAME = os.getenv("MONGODB_COLLECTION", "session_memory")
MONGO_TIMEOUT_MS = int(os.getenv("MONGO_TIMEOUT_MS", "5000"))

class SessionMemory:
    def __init__(self) -> None:
        """Initialize session memory with MongoDB and LangGraph fallback"""
        self.memory: MemorySaver = MemorySaver()
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None
        self.collection: Optional[Collection] = None
        self.last_connection_attempt: float = 0
        self.connection_retry_interval: int = 300  # 5 minutes
        self._init_mongodb()

    def _should_retry_connection(self) -> bool:
        """Check if enough time has passed to retry MongoDB connection"""
        now = datetime.now().timestamp()
        return (now - self.last_connection_attempt) > self.connection_retry_interval

    def _init_mongodb(self) -> None:
        """
        Attempt to initialize MongoDB connection; fallback to MemorySaver on failure.
        Implements connection retry logic and better error handling.
        """
        if not MONGO_URI:
            logger.warning("MONGO_URI not provided, using MemorySaver fallback.")
            return

        self.last_connection_attempt = datetime.now().timestamp()

        try:
            self.client = MongoClient(
                MONGO_URI,
                serverSelectionTimeoutMS=MONGO_TIMEOUT_MS,
                connectTimeoutMS=MONGO_TIMEOUT_MS,
                retryWrites=True
            )
            # Force a connection check
            self.client.server_info()
            
            self.db = self.client[DB_NAME]
            self.collection = self.db[COLLECTION_NAME]
            
            # Create indexes for better query performance
            self.collection.create_index("session_id", unique=True)
            self.collection.create_index("last_accessed", expireAfterSeconds=7*24*60*60)  # 7 days TTL
            
            logger.info("MongoDB connection established successfully.")
            
        except errors.ServerSelectionTimeoutError as e:
            logger.warning(f"MongoDB connection timeout: {e}. Using MemorySaver fallback.")
            self._cleanup_connection()
        except errors.ConnectionFailure as e:
            logger.warning(f"MongoDB connection failed: {e}. Using MemorySaver fallback.")
            self._cleanup_connection()
        except Exception as e:
            logger.error(f"Unexpected MongoDB error: {e}. Using MemorySaver fallback.")
            self._cleanup_connection()

    def _cleanup_connection(self) -> None:
        """Clean up MongoDB connection resources"""
        if self.client:
            try:
                self.client.close()
            except Exception as e:
                logger.error(f"Error closing MongoDB connection: {e}")
        self.client = None
        self.db = None
        self.collection = None

    def _try_reconnect(self) -> bool:
        """Attempt to reconnect to MongoDB if connection was lost"""
        if not self.collection and self._should_retry_connection():
            self._init_mongodb()
            return self.collection is not None
        return False

    def save_session_state(self, session_id: str, state: Dict[str, Any]) -> bool:
        """
        Save session state with improved error handling and automatic reconnection.

        Args:
            session_id: Unique session identifier
            state: Session state data to save

        Returns:
            bool: True if save was successful, False otherwise
        """
        if not session_id:
            logger.error("No session_id provided; cannot save session state.")
            return False

        # Try MongoDB first (with potential reconnection)
        if self.collection or self._try_reconnect():
            try:
                self.collection.update_one(
                    {"session_id": session_id},
                    {
                        "$set": {
                            "session_id": session_id,
                            "memory_state": state,
                            "last_accessed": datetime.utcnow(),
                            "last_modified": datetime.utcnow()
                        }
                    },
                    upsert=True
                )
                logger.info(f"Session '{session_id}' saved to MongoDB.")
                return True
            except Exception as e:
                logger.error(f"MongoDB save failed for session '{session_id}': {e}")

        # Fallback to MemorySaver
        try:
            self.memory.save(session_id, state)
            logger.info(f"Session '{session_id}' saved to MemorySaver.")
            return True
        except Exception as e:
            logger.error(f"MemorySaver save failed for session '{session_id}': {e}")
            return False

    def load_session_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Load session state with improved error handling and automatic reconnection.

        Args:
            session_id: Unique session identifier

        Returns:
            Optional[Dict[str, Any]]: Session state if found, None otherwise
        """
        if not session_id:
            logger.error("No session_id provided; cannot load session state.")
            return None

        # Try MongoDB first (with potential reconnection)
        if self.collection or self._try_reconnect():
            try:
                session = self.collection.find_one_and_update(
                    {"session_id": session_id},
                    {"$set": {"last_accessed": datetime.utcnow()}},
                    return_document=True
                )
                if session and "memory_state" in session:
                    logger.info(f"Session '{session_id}' loaded from MongoDB.")
                    return session["memory_state"]
            except Exception as e:
                logger.error(f"MongoDB load failed for session '{session_id}': {e}")

        # Fallback to MemorySaver
        try:
            state = self.memory.load(session_id)
            if state:
                logger.info(f"Session '{session_id}' loaded from MemorySaver.")
                return state
        except Exception as e:
            logger.error(f"MemorySaver load failed for session '{session_id}': {e}")

        logger.info(f"No session found for session_id '{session_id}'.")
        return None

    def clear_session_state(self, session_id: str) -> bool:
        """
        Clear session state from both storage systems.

        Args:
            session_id: Unique session identifier

        Returns:
            bool: True if clearing was successful from at least one storage system
        """
        success = True

        # Try MongoDB first (with potential reconnection)
        if self.collection or self._try_reconnect():
            try:
                result = self.collection.delete_one({"session_id": session_id})
                if result.deleted_count:
                    logger.info(f"Session '{session_id}' cleared from MongoDB.")
                else:
                    logger.info(f"Session '{session_id}' not found in MongoDB.")
            except Exception as e:
                logger.error(f"MongoDB clear failed for session '{session_id}': {e}")
                success = False

        # Always try to clear from MemorySaver too
        try:
            self.memory.clear(session_id)
            logger.info(f"Session '{session_id}' cleared from MemorySaver.")
        except Exception as e:
            logger.error(f"MemorySaver clear failed for session '{session_id}': {e}")
            success = False

        return success

# Initialize global session memory instance
session_memory = SessionMemory()

# Export simplified interface
def save_session_state(session_id: str, state: Dict[str, Any]) -> bool:
    return session_memory.save_session_state(session_id, state)

def load_session_state(session_id: str) -> Optional[Dict[str, Any]]:
    return session_memory.load_session_state(session_id)

def clear_session_state(session_id: str) -> bool:
    return session_memory.clear_session_state(session_id)

# Export memory instance for LangGraph
memory = session_memory.memory