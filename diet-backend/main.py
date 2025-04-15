from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from db import conn, cursor

app = FastAPI()

# 支持跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据模型
class PhoneCheck(BaseModel):
    phone: str

class SupplementData(BaseModel):
    phone: str
    name: str
    gender: str
    birthday: str
    height: str
    weight: str
    bloodPressure: str
    bloodSugar: str
    chronic: str
    medication: str
    avoid: str

@app.post("/api/check-user")
def check_user(data: PhoneCheck):
    cursor.execute("SELECT phone FROM accounts WHERE phone = ?", (data.phone,))
    row = cursor.fetchone()
    return {"isNewUser": row is None}

@app.post("/api/submit-info")
def submit_info(data: SupplementData):
    cursor.execute("INSERT OR IGNORE INTO accounts (phone) VALUES (?)", (data.phone,))
    cursor.execute("REPLACE INTO profile VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   (data.phone, data.name, data.gender, data.birthday, data.height,
                    data.weight, data.bloodPressure, data.bloodSugar))
    cursor.execute("REPLACE INTO health_info VALUES (?, ?, ?, ?)",
                   (data.phone, data.chronic, data.medication, data.avoid))
    cursor.execute("INSERT INTO user_logs (phone, action, detail) VALUES (?, 'submit_info', 'completed')",
                   (data.phone,))
    conn.commit()
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)