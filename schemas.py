from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str | None = None

class UserOut(BaseModel):
    id: int
    username: str
    class Config:
        orm_mode = True

class MessageCreate(BaseModel):
    content: str
    owner_id: int

class MessageOut(BaseModel):
    id: int
    content: str
    owner_id: int
    class Config:
        orm_mode = True
