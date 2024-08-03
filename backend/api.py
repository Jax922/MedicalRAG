import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from service import (chat_pipeline, condense_question_pipeline, context_chat_pipeline, react_chat_pipeline,
                     query_pipeline, rag_chat_final_use,
                     reset_chat_engine, get_chat_history,
                     single_agent, multi_agent,
                     check_rag_usage, emotion_detection, keywords_highlight, )

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


class MultiAgentModel(BaseModel):
    user_query: str
    health_history: list
    therapy_history: list


class HighlightModel(BaseModel):
    user_query: str
    bald_text: str


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/query")
def query_endpoint(query: QueryModel):
    response, ref = query_pipeline(query.user_query)
    return {
        "response": response,
        "references": ref
    }


@app.post("/chat")
def chat_endpoint(query: QueryModel):
    # default is openai function call
    response, ref = chat_pipeline(query.user_query)
    return {
        "response": response,
        "references": ref
    }


@app.post("/rag_chat_final_use")
def rag_chat_final_use_endpoint(query: HistoryModel):
    response = rag_chat_final_use(query.user_query, query.history)
    return {"response": response}


@app.post("/context_chat")
def context_chat_endpoint(query: HistoryModel):
    response = context_chat_pipeline(query.user_query, query.history)
    return {"response": response}


@app.post("/react_chat")
def react_chat_endpoint(query: HistoryModel):
    response = react_chat_pipeline(query.user_query, query.history)
    return {"response": response}


@app.post("/condense_question")
def condense_question_endpoint(query: HistoryModel):
    response = condense_question_pipeline(query.user_query, query.history)
    return {"response": response}


@app.post("/reset")
def reset_endpoint():
    return reset_chat_engine()


@app.get("/get_chat_history")
def get_chat_history_endpoint():
    return {"chat_history": get_chat_history()}


@app.post("/single_agent")
def single_agent_endpoint(query: HistoryModel):
    response = single_agent(query.user_query, query.history)
    return {"response": response}


@app.post("/multi_agent")
def multi_agent_endpoint(query: MultiAgentModel):
    response = multi_agent(
        query.user_query, query.health_history, query.therapy_history)
    return {"response": response}


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


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
