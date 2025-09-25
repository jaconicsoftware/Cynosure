from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import uvicorn

from database import SessionLocal, init_db
from models import User

app = FastAPI()

# подключение к БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def startup_event():
    init_db()


# ✅ Регистрация
@app.post("/register")
def register(username: str, password: str, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    user = User(username=username, password=password, is_guest=0)
    db.add(user)
    db.commit()
    return {"message": "User registered successfully"}


# ✅ Вход
@app.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username, User.password == password).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful", "username": user.username}


# ✅ Гостевой вход
@app.post("/guest")
def guest(username: str, db: Session = Depends(get_db)):
    guest_name = f"Guest_{username}"
    user = User(username=guest_name, is_guest=1)
    db.add(user)
    db.commit()
    return {"message": "Guest login successful", "username": guest_name}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
