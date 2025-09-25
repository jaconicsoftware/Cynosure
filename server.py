from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Сообщения будут храниться прямо в памяти (пока без базы)
messages = []

class Message(BaseModel):
    username: str
    text: str

@app.get("/")
def home():
    return {"status": "ok", "msg": "Добро пожаловать в Cynosure Chat 🚀"}

@app.get("/messages")
def get_messages():
    return messages

@app.post("/send")
def send_message(msg: Message):
    messages.append(msg.dict())
    return {"status": "ok", "msg": "sent"}
