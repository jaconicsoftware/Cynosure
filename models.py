from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(100), nullable=True)  # None для гостей
    is_guest = Column(Integer, default=0)  # 0 - обычный, 1 - гость
