import time
from typing import Any, Dict, List, Optional

import uvicorn
from chatbot_demo_test import single_agent, single_agent_v1_2
from dotenv import find_dotenv, load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from utils import gpt4o_history_call

_ = load_dotenv(find_dotenv("../env/.env"), override=True)


app = FastAPI()


# Allow CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryModel(BaseModel):
    user_query: str


class EmotionModel(BaseModel):
    text: str


class HistoryModel(BaseModel):
    user_query: str
    history: list

    language: Optional[str] = 'yueyu'
    mode: Optional[dict] = None


class MultiAgentModel(BaseModel):
    user_query: str
    health_history: list
    therapy_history: list


class HighlightModel(BaseModel):
    user_query: str
    bald_text: str


@app.post("/single_agent")
def single_agent_endpoint(query: HistoryModel):

    response = single_agent(query.user_query, query.history,
                            query.mode, query.language, False)
    return {"response": response}


@app.post("/single_agent_v1_2")
def single_agent_v1_2_endpoint(query: HistoryModel):

    response = single_agent_v1_2(
        query.user_query, query.history, query.mode, query.language, False)
    return {"response": response}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
