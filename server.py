import os
import traceback
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

# Настройка БД
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    raise RuntimeError("❌ DATABASE_URL не задан")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Таблица пользователей
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    nickname = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=True)
    is_guest = Column(Integer, default=0)

Base.metadata.create_all(bind=engine)

# Pydantic модели
class RegisterRequest(BaseModel):
    nickname: str
    password: str

class LoginRequest(BaseModel):
    nickname: str
    password: str

class GuestRequest(BaseModel):
    nickname: str

# FastAPI приложение
app = FastAPI()

# Глобальный обработчик ошибок
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print("❌ ERROR:", exc)
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "error": str(exc)},
    )

@app.post("/register")
def register(data: RegisterRequest):
    db = SessionLocal()
    if db.query(User).filter_by(nickname=data.nickname).first():
        raise HTTPException(status_code=400, detail="Ник уже занят")
    user = User(nickname=data.nickname, password=data.password, is_guest=0)
    db.add(user)
    db.commit()
    return {"message": f"✅ Пользователь {data.nickname} зарегистрирован"}

@app.post("/login")
def login(data: LoginRequest):
    db = SessionLocal()
    user = db.query(User).filter_by(nickname=data.nickname, password=data.password).first()
    if not user:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    return {"message": f"🔑 Успешный вход: {data.nickname}"}

@app.post("/guest")
def guest(data: GuestRequest):
    db = SessionLocal()
    nickname = f"Гость ({data.nickname})"
    if db.query(User).filter_by(nickname=nickname).first():
        raise HTTPException(status_code=400, detail="Такой гость уже есть")
    user = User(nickname=nickname, is_guest=1)
    db.add(user)
    db.commit()
    return {"message": f"👤 Вошёл как гость: {nickname}"}
