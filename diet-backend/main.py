from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from db import conn
from datetime import datetime
from openai import OpenAI

app = FastAPI()

# 支持跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置 OpenAI API
# openai.api_key = "sk-D4YRkSe0WYNVycYhuLRsxVK8MjA9Uu6K49bwQQyAqjaejwUN"
# openai.api_base = "https://api.chatanywhere.com.cn/v1"

client = OpenAI(
    api_key="sk-D4YRkSe0WYNVycYhuLRsxVK8MjA9Uu6K49bwQQyAqjaejwUN",
    base_url="https://api.chatanywhere.tech/v1"
)


# --- 数据模型 ---
class PhoneCheck(BaseModel):
    phone: str

class SupplementData(BaseModel):
    phone: str
    gender: str
    age: str
    height: str
    weight: str
    bloodPressure: str
    bloodSugar: str
    chronic: str
    medication: str
    avoid: str

class ChatMessage(BaseModel):
    phone: str
    message: str
    sender: str

class UserLog(BaseModel):
    phone: str
    action: str
    detail: str = ''

class AIRequest(BaseModel):
    phone: str
    message: str
    location: str = "Unknown"

# --- 工具函数 ---
def get_cursor():
    return conn.cursor()

# --- 接口定义 ---
@app.post("/api/check-user")
def check_user(data: PhoneCheck):
    with conn:
        cursor = get_cursor()
        cursor.execute("SELECT phone FROM profile WHERE phone = ?", (data.phone,))
        row = cursor.fetchone()
        return {"isNewUser": row is None}

@app.post("/api/submit-info")
def submit_info(data: SupplementData):
    with conn:
        cursor = get_cursor()
        cursor.execute("INSERT OR IGNORE INTO accounts (phone) VALUES (?)", (data.phone,))
        cursor.execute("REPLACE INTO profile VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (data.phone, data.gender, data.age, data.height,
                        data.weight, data.bloodPressure, data.bloodSugar))
        cursor.execute("INSERT INTO user_logs (phone, action, detail) VALUES (?, 'submit_info', 'completed')",
                       (data.phone,))
    return {"status": "ok"}

@app.post("/api/save-chat")
def save_chat(data: ChatMessage):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with conn:
        cursor = get_cursor()
        cursor.execute(
            "INSERT INTO chat_history (phone, timestamp, message, sender) VALUES (?, ?, ?, ?)",
            (data.phone, now, data.message, data.sender)
        )
    return {"status": "saved"}

@app.post("/api/log-action")
def log_action(data: UserLog):
    with conn:
        cursor = get_cursor()
        cursor.execute(
            "INSERT INTO user_logs (phone, action, detail) VALUES (?, ?, ?)",
            (data.phone, data.action, data.detail)
        )
    return {"status": "logged"}

@app.post("/api/generate-reply")
def generate_reply(data: AIRequest):
    with conn:
        cursor = get_cursor()

        # 获取用户 profile 信息
        cursor.execute("SELECT gender, age, height, weight, blood_pressure, blood_sugar FROM profile WHERE phone = ?", (data.phone,))
        profile = cursor.fetchone()
        profile_text = ""
        if profile:
            gender, age, height, weight, bp, bs = profile
            profile_text = f"用户基本信息：性别{gender}，年龄{age}岁，身高{height}，体重{weight}，血压{bp}，血糖{bs}。"

        # 获取今天的 user 聊天记录
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("""
            SELECT message FROM chat_history 
            WHERE phone = ? AND sender = 'user' AND DATE(timestamp) = ?
        """, (data.phone, today))
        user_msgs = cursor.fetchall()
        daily_summary = "\n".join([row[0] for row in user_msgs][-5:])

    prompt = f"""
你是一个专业的老年人饮食健康助手，请根据以下背景信息，简短而清晰地回复用户今天应该注意的饮食建议：

{profile_text}

地理位置：{data.location}

用户今日饮食和心情描述如下：
{daily_summary}

请根据上述内容，控制回复在两句话以内。
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是一个专业饮食健康顾问"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=150
        )
        reply = response.choices[0].message.content.strip()
        return {"reply": reply}
    except Exception as e:
        return {"error": str(e)}

# --- 启动服务 ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)