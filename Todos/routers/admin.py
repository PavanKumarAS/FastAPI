from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from models import ToDos
from database import SessionLocal
from starlette import status
from pydantic import BaseModel, Field
from .auth import get_current_user

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
    )

def get_db():
    db = SessionLocal() 
    try:
        yield db
    finally:
        db.close()

db_dependecy = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/todos")
async def get_all(user: user_dependency, db: db_dependecy):
    if user is None or user.role != "Admin":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Failed Authentication")

    return db.query(ToDos).all()