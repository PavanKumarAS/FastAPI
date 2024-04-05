from fastapi import FastAPI
import models
from database import engine, SessionLocal
from routers import auth, todos, admin, users
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "https://github.com/login",
    "http://127.0.0.1:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind = engine)

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)


 