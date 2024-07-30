from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
from uuid import uuid4

app = FastAPI()

# Allow CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    user: str
    text: str

class Session(BaseModel):
    session_id: str
    messages: List[Message]

# In-memory storage for sessions
sessions: Dict[str, List[Message]] = {}

@app.post("/start_session", response_model=Session)
def start_session():
    session_id = str(uuid4())
    sessions[session_id] = []
    return Session(session_id=session_id, messages=[])

@app.post("/send_message", response_model=Session)
def send_message(session_id: str, message: Message):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    sessions[session_id].append(message)
    # Here you could add your bot's response logic
    bot_response = Message(user="bot", text=f"Echo: {message.text}")
    sessions[session_id].append(bot_response)

    return Session(session_id=session_id, messages=sessions[session_id])

@app.get("/get_session/{session_id}", response_model=Session)
def get_session(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return Session(session_id=session_id, messages=sessions[session_id])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
