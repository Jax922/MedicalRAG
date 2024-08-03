import pytest
from fastapi.testclient import TestClient
from api import app  # 假设你的 FastAPI 应用代码在 api.py 中
from service import (
    ragPipeline, chatPipeline, reset_chat_engine,
    get_chat_history, single_agent, multi_agent,
    emotion_detection, check_rag_usage, keywords_highlight
)

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}

def test_query_endpoint(mocker):
    mock_response = ("response_text", [["reference1", "file1"], ["reference2", "file2"]])
    mocker.patch("service.ragPipeline", return_value=mock_response)
    
    response = client.post("/query", json={"user_query": "test query"})
    assert response.status_code == 200
    json_response = response.json()
    assert "response" in json_response
    assert "references" in json_response
    assert len(json_response["references"]) > 0

def test_chat_endpoint(mocker):
    mock_response = ("chat_response", [["chat_reference1", "file1"], ["chat_reference2", "file2"]])
    mocker.patch("service.chatPipeline", return_value=mock_response)
    
    response = client.post("/chat", json={"user_query": "chat query"})
    assert response.status_code == 200
    json_response = response.json()
    assert "response" in json_response
    assert "references" in json_response
    assert len(json_response["references"]) > 0

def test_reset_endpoint(mocker):
    mocker.patch("service.reset_chat_engine", return_value={"message": "Chat engine has been reset"})
    
    response = client.post("/reset")
    assert response.status_code == 200
    json_response = response.json()
    assert "message" in json_response

def test_emotion_endpoint(mocker):
    mock_response = {"情绪": "中性", "置信度": 0.7}
    mocker.patch("service.emotion_detection", return_value=mock_response)
    
    response = client.post("/emotion", json={"text": "I am happy"})
    assert response.status_code == 200
    json_response = response.json()
    assert "情绪" in json_response
    assert "置信度" in json_response

def test_check_rag_endpoint(mocker):
    mock_response = "False"
    mocker.patch("service.check_rag_usage", return_value=mock_response)
    
    response = client.post("/check_rag", json={"user_query": "check query", "history": ["query1", "query2"]})
    assert response.status_code == 200
    json_response = response.json()
    assert "usage" in json_response

def test_keywords_highlight_endpoint(mocker):
    mock_response = ["keyword1", "keyword2"]
    mocker.patch("service.keywords_highlight", return_value=mock_response)
    
    response = client.post("/keywords_highlight", json={"user_query": "highlight query", "bald_text": "some text"})
    assert response.status_code == 200
    json_response = response.json()
    assert "keywords" in json_response
    assert len(json_response["keywords"]) > 0

def test_get_chat_history_endpoint(mocker):
    mock_response = ["history1", "history2"]
    mocker.patch("service.get_chat_history", return_value=mock_response)
    
    response = client.get("/get_chat_history")
    assert response.status_code == 200
    json_response = response.json()
    assert "chat_history" in json_response
    assert len(json_response["chat_history"]) >= 0

def test_single_agent_endpoint(mocker):
    mock_response = {"final_response": "single agent response", "history": []}
    mocker.patch("service.single_agent", return_value=mock_response)
    
    response = client.post("/single_agent", json={"user_query": "single agent query", "history": []})
    assert response.status_code == 200
    json_response = response.json()
    assert "final_response" in json_response
    assert "history" in json_response

def test_multi_agent_endpoint(mocker):
    mock_response = {"final_response": "multi agent response", "health_history": [], "therapy_history": []}
    mocker.patch("service.multi_agent", return_value=mock_response)
    
    response = client.post("/multi_agent", json={"user_query": "multi agent query", "health_history": [], "therapy_history": []})
    assert response.status_code == 200
    json_response = response.json()
    assert "final_response" in json_response
    assert "health_history" in json_response
    assert "therapy_history" in json_response

if __name__ == "__main__":
    pytest.main()
