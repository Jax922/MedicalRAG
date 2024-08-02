import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from service import (chatPipeline, check_rag_usage, emotion_detection,
                     keywords_highlight, ragPipeline, reset_chat_engine, get_chat_history)

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


class HighlightModel(BaseModel):
    user_query: str
    bald_text: str


@app.post("/query")
def query_endpoint(query: QueryModel):
    response, ref = ragPipeline(query.user_query)
    return {
        "response": response,
        "references": ref
    }


@app.post("/chat")
def chat_endpoint(query: QueryModel):
    response, ref = chatPipeline(query.user_query)
    return {
        "response": response,
        "references": ref
    }


@app.post("/reset")
def reset_endpoint():
    return reset_chat_engine()


@app.post("/emotion")
def emotion_endpoint(emotion: EmotionModel):
    result = emotion_detection(emotion.text)
    return result


@app.post("/check_rag")
def check_rag_endpoint(history: HistoryModel):
    result = check_rag_usage(history.user_query, history.history)
    return {"usage": result}


@app.post("/keywords_highlight")
def keywords_highlight_endpoint(highlight: HighlightModel):
    result = keywords_highlight(highlight.user_query, highlight.bald_text)
    return {"keywords": result}


@app.get("/get_chat_history")
def get_chat_history_endpoint():
    return {"chat_history": get_chat_history()}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
