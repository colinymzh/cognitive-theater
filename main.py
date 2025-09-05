# main.py
import uuid
import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, AsyncGenerator

from app.system import CBTTheaterSystem

# --- 1. Application and session storage settings ---

app = FastAPI(
    title="Cognitive Theater",
    description="An AI psychological mutual aid group backend service that supports persistent sessions.",
    version="6.0.0",
)

# CORS
origins = [
    "http://localhost",
    "http://localhost:8001",
    "http://127.0.0.1",
    "http://127.0.0.1:8001",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions_cache: Dict[str, CBTTheaterSystem] = {}
SESSIONS_DIR = "sessions"
os.makedirs(SESSIONS_DIR, exist_ok=True)

def get_session(session_id: str) -> CBTTheaterSystem:

    if session_id not in sessions_cache:
        print(f"[System Activity]: Cache miss, creating instance for session {session_id}...")
        sessions_cache[session_id] = CBTTheaterSystem(session_id)
    return sessions_cache[session_id]


class StartRequest(BaseModel):
    initial_problem: str

class ChatRequest(BaseModel):
    session_id: str
    user_input: str

class SessionSummary(BaseModel):
    session_id: str
    title: str

class ChatHistory(BaseModel):
    history: List[str]
    

@app.get("/")
def read_root():
    return {"message": "Welcome to API v6.0. Please use /docs to view the API documentation."}

@app.get("/sessions", response_model=List[SessionSummary])
def list_sessions():
    summaries = []
    for filename in os.listdir(SESSIONS_DIR):
        if filename.endswith(".json"):
            session_id = filename.replace(".json", "")
            try:
                with open(os.path.join(SESSIONS_DIR, filename), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    title = data.get("initial_problem", "Untitled Dialogue")[:40]
                    if len(data.get("initial_problem", "")) > 40:
                        title += "..."
                summaries.append(SessionSummary(session_id=session_id, title=title))
            except (json.JSONDecodeError, KeyError):
                print(f"Warning: Unable to parse file {filename}")
                continue
    
    summaries.sort(key=lambda s: os.path.getmtime(os.path.join(SESSIONS_DIR, f"{s.session_id}.json")), reverse=True)
    return summaries

@app.get("/sessions/{session_id}", response_model=ChatHistory)
def get_session_history(session_id: str):
    """Load and return a complete conversation history based on session_id."""
    try:
        system_instance = get_session(session_id)
        return ChatHistory(history=system_instance.conversation_history)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Session file not found.")

@app.post("/session/start")
async def start_and_stream_session(request: StartRequest):
    """
    Starts a new session and immediately begins streaming back to the opening conversation.
    """
    session_id = str(uuid.uuid4())
    system_instance = get_session(session_id)
    

    return StreamingResponse(
        system_instance.start_session(request.initial_problem, session_id), 
        media_type="application/x-ndjson"
    )

@app.post("/session/chat")
async def continue_session_stream(request: ChatRequest):
    """Continues an existing conversation session and streams back the AI's responses."""
    try:
        system_instance = get_session(request.session_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found. Please start a new session.")
    
    return StreamingResponse(
        system_instance.continue_session(request.user_input), 
        media_type="application/x-ndjson"
    )

@app.delete("/sessions/{session_id}")
def delete_session(session_id: str):
    """Delete a saved conversation history file based on session_id."""
    print(f"[System Activity]: Received a request to delete session {session_id}...")
    
    if session_id in sessions_cache:
        del sessions_cache[session_id]
        print(f" [Cache]: Removed {session_id} from memory cache.")

    session_file_path = os.path.join(SESSIONS_DIR, f"{session_id}.json")
    if os.path.exists(session_file_path):
        try:
            os.remove(session_file_path)
            print(f"[Hard Drive]: Successfully deleted file {session_file_path}.")
            return {"status": "success", "message": f"Session {session_id} deleted."}
        except OSError as e:
            print(f"[ERROR]: Error deleting file: {e}")
            raise HTTPException(status_code=500, detail=f"Error deleting session file: {e}")
    else:
        print(f"[WARNING]: Trying to delete a non-existent file {session_file_path}.")
        return {"status": "success", "message": f"Session {session_id} did not exist, but request is processed."}