from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import SessionLocal, init_db
from models import User, Message
from datetime import datetime
import hashlib

app = FastAPI()

# --- инициализация базы ---
init_db()

# --- запросы ---
class RegisterRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class GuestRequest(BaseModel):
    username: str

class MessageRequest(BaseModel):
    username: str
    message: str


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


@app.post("/register")
def register_user(req: RegisterRequest):
    db = SessionLocal()
    existing = db.query(User).filter(User.username == req.username).first()
    if existing:
        db.close()
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(username=req.username, password=hash_password(req.password), is_guest=False)
    db.add(new_user)
    db.commit()
    db.close()
    return {"status": "ok"}


@app.post("/register_guest")
def register_guest(req: GuestRequest):
    db = SessionLocal()
    guest_name = f"Гость({req.username})"

    # проверим, чтобы ник не был занят
    existing = db.query(User).filter(User.username == guest_name).first()
    if existing:
        db.close()
        raise HTTPException(status_code=400, detail="Guest name taken")

    new_guest = User(username=guest_name, password="", is_guest=True)
    db.add(new_guest)
    db.commit()
    db.close()
    return {"status": "ok", "username": guest_name}


@app.post("/login")
def login(req: LoginRequest):
    db = SessionLocal()
    user = db.query(User).filter(User.username == req.username).first()
    if not user or user.password != hash_password(req.password):
        db.close()
        raise HTTPException(status_code=400, detail="Invalid credentials")
    db.close()
    return {"status": "ok", "username": user.username}


@app.post("/send_message")
def send_message(req: MessageRequest):
    db = SessionLocal()
    msg = Message(username=req.username, message=req.message, timestamp=datetime.utcnow())
    db.add(msg)
    db.commit()
    db.close()
    return {"status": "ok"}


@app.get("/messages")
def get_messages():
    db = SessionLocal()
    msgs = db.query(Message).order_by(Message.timestamp.desc()).limit(30).all()
    db.close()
    return [
        {"username": m.username, "message": m.message, "timestamp": m.timestamp.isoformat()}
        for m in reversed(msgs)
    ]
