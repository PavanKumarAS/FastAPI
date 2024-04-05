from typing import Annotated, Any, List
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from models import ToDos
from database import SessionLocal
from starlette import status
from pydantic import BaseModel, ConfigDict, Field
from .auth import get_current_user

router = APIRouter()

def get_db():
    db = SessionLocal() 
    try:
        yield db
    finally:
        db.close()

db_dependecy = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[any, Depends(get_current_user)]

class ToDoRequest(BaseModel):
    title: str =Field(min_length=3)
    description: str =Field(min_length=3, max_length=100)
    priority: int = Field(gt=0,lt=6)
    complete: bool

class ToDoResponse(BaseModel):
    title: str
    description: str
    priority: int
    complete: bool

@router.get("/todos", response_model=List[ToDoResponse])
async def get_all(user: user_dependency, db: db_dependecy) -> Any:
    # if user is None:
    #         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Failed Authentication")
    
    return db.query(ToDos).all()

@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK, response_model=ToDoResponse)
async def get_by_id(user: user_dependency,db: db_dependecy, todo_id: int = Path(gt=0)):
    # if user is None:
    #         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Failed Authentication")

    todo_model = db.query(ToDos).filter(ToDos.id == todo_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found")


@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency,db: db_dependecy, todorequest: ToDoRequest):
    if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Failed Authentication")

    todo_model = ToDos(**todorequest.model_dump(), owner= user.id)

    db.add(todo_model)
    db.commit()
    return "ToDo created successfully"

@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependecy, todorequest: ToDoRequest, 
                      todo_id: int = Path(gt=0)):
    if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Failed Authentication")

    todo_model = db.query(ToDos).filter(ToDos.id == todo_id and ToDos.owner == user.id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="ToDo not found")
    
    todo_model.title = todorequest.title
    todo_model.priority = todorequest.priority
    todo_model.description = todorequest.description
    todo_model.complete = todorequest.complete

    db.add(todo_model)
    db.commit()

@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependecy, todo_id: int = Path(gt=0)):
    if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Failed Authentication")

    todo_model = db.query(ToDos).filter(ToDos.id == todo_id and ToDos.owner == user.id).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail="ToDo not found")
    
    db.query(ToDos).filter(ToDos.id == todo_id).delete()
    db.commit()

        




