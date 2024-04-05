from typing import Annotated
import bcrypt
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from models import ToDos, Users
from database import SessionLocal
from starlette import status
from pydantic import BaseModel, Field
from .auth import get_current_user


router = APIRouter(
    prefix="/user",
    tags=["user"]
    )

def get_db():
    db = SessionLocal() 
    try:
        yield db
    finally:
        db.close()

db_dependecy = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

def hash_password(password):
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password

def verify_password(plain_password, hashed_password):
    password_byte_enc = plain_password.encode('utf-8')
    return bcrypt.checkpw(password = password_byte_enc , hashed_password = hashed_password)

class ResetUserPassword(BaseModel):
     old_password: str
     new_password: str = Field(min_length=6)

class UserResponse(BaseModel):
    email: str
    username: str
    first_name: str
    last_name: str
    role: str

@router.get("/", response_model=UserResponse)
async def get_user(user: user_dependency, db: db_dependecy):
    if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Failed Authentication")
    
    return db.query(Users).filter(Users.id == user.id).first()


@router.put("/resetpassword", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(user: user_dependency, db: db_dependecy, passwords: ResetUserPassword):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Failed Authentication")

    user_model = db.query(Users).filter(Users.id == user.id).first()

    if not verify_password(passwords.old_password, user_model.hash_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Error on password change")

    user_model.hash_password = hash_password(passwords.new_password)

    db.add(user_model)
    db.commit()

       




