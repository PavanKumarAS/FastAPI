from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, BINARY

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(200), unique=True, nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    hash_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)


class ToDos(Base):
    __tablename__ = 'todos'

    id = Column(Integer, primary_key= True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner = Column(Integer, ForeignKey("users.id"))
