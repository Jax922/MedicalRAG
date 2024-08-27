import uvicorn
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from service import (chat_pipeline, chat_stream_pipeline,
                     condense_question_pipeline, context_chat_pipeline, react_chat_pipeline,
                     query_pipeline, rag_chat_final_use,
                     reset_chat_engine, get_chat_history,
                     single_agent, multi_agent,
                     check_rag_usage, emotion_detection, keywords_highlight, history_summary,
                     gpt4o_history_call)

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

    language: str

    mode: Optional[dict] = None
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


@app.post("/chat_stream/")
async def chat_endpoint(query: HistoryModel):
    response_generator = chat_stream_pipeline(query.user_query, query.history)
    return StreamingResponse(response_generator, media_type="text/plain")


@app.post("/rag_chat_final_use")
def rag_chat_final_use_endpoint(query: HistoryModel):
    response, ref = rag_chat_final_use(query.user_query, query.history,query.language)
    return {
        "response": response,
        "references": ref
    }


@app.post("/context_chat")
def context_chat_endpoint(query: HistoryModel):
    response, ref = context_chat_pipeline(query.user_query, query.history)
    return {
        "response": response,
        "references": ref
    }


@app.post("/react_chat")
def react_chat_endpoint(query: HistoryModel):
    response, ref = react_chat_pipeline(query.user_query, query.history)
    return {
        "response": response,
        "references": ref
    }


@app.post("/condense_question")
def condense_question_endpoint(query: HistoryModel):
    response, ref = condense_question_pipeline(query.user_query, query.history)
    return {
        "response": response,
        "references": ref
    }


@app.post("/reset")
def reset_endpoint():
    return reset_chat_engine()


@app.get("/get_chat_history")
def get_chat_history_endpoint():
    return {"chat_history": get_chat_history()}


@app.post("/chat_without_prompt")
def chat_without_prompt_endpoint(query: HistoryModel):
    if query.language != 'mandarin':
        query.history.insert(
            0, {'role': 'system', 'content': '请使用粤语回答问题，请使用粤语回答问题'})
    response = gpt4o_history_call('gpt-4o-mini', query.history, False)
    return {
        "response": response
    }


@app.post("/single_agent")
def single_agent_endpoint(query: HistoryModel):

    response = single_agent(query.user_query, query.history, query.mode, False)
    return {"response": response}


@app.post("/manual_input_endpoint")
def manual_input_endpoint(query: HistoryModel):
    # 格式化用户的查询和历史记录
    formatted_history = "\n".join(
        [f"{index + 1}. 【{'用户' if item['role'] == 'user' else '助手'}】: {item['content']}"
         for index, item in enumerate(query.history)]
    )

    # 输出格式化内容
    print(f"【用户】: {query.user_query}\n【历史记录】:\n{formatted_history}")

    # 手动输入管理员的回复
    response = input("请输入管理员的回复: ")

    # 返回管理员输入的响应
    return {"response": response}


@app.post("/single_agent_stream")
def single_agent_stream_endpoint(query: HistoryModel):
    response_generator = single_agent(query.user_query, query.history, True)
    return StreamingResponse(response_generator, media_type="text/plain")


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


@app.post("/history_summary")
def history_summary_endpoint(query: HistoryModel):
    summary = history_summary(query.history)
    return {"response": summary}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
