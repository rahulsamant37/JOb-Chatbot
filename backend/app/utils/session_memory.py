from langchain.memory import MemorySaver
from pymongo import MongoClient

import os

# MongoDB Connection:

MONGO_URI = ""
client = MongoClient(MONGO_URI)
db = client["clustername here"]

memory_collection = db["session_memory"]


# memory saver
memory = MemorySaver() # 

def save_session_state(session_id: str, state:dict):
    """Store session state in MongoDB using MemorySaver."""
    memory_collection.update_one(
        {
            "session_id": session_id
        },
        {
            "$set":{
                "session_id": session_id,
                "memory_state": state
            }
        },
        upsert=True
    )
    
def load_session_state(session_id:str):
    """Retrieve session state from MongoDB"""
    session = memory_collection.find_one({"session_id": session_id})
    return session["memory_state"] if session else None