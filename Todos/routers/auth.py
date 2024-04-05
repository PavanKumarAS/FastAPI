from datetime import datetime, timedelta
from typing import Annotated, List
import bcrypt
from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, EmailStr, Field
from models import Users
from database import SessionLocal
from sqlalchemy.orm import Session
from starlette import status
from fastapi.security import  OAuth2PasswordBearer, OpenIdConnect, OAuth2PasswordRequestForm
from jose import jwt, JWTError

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

Security_key = "17a911e06710ce305a8a50a7ef23277cd0d348818e0cbf70b97f70c5f3d1af9f"

Algorithem = "HS256"
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

open_id_connect = OpenIdConnect(openIdConnectUrl="https://independentadjusterdev.b2clogin.com/independentadjusterdev.onmicrosoft.com/B2C_1_sing_up_in_adjuster/v2.0/.well-known/openid-configuration")


class Token(BaseModel):
    access_token: str
    token_type: str

def get_db():
    db = SessionLocal() 
    try:
        yield db
    finally:
        db.close()

db_dependecy = Annotated[Session, Depends(get_db)]

def hash_password(password):
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password

def verify_password(plain_password, hashed_password):
    password_byte_enc = plain_password.encode('utf-8')
    password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password = password_byte_enc , hashed_password = password)

def authenticate_user(username: str, password: str, db):
    user =  db.query(Users).filter(Users.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.hash_password):
        return None
    return user

def create_access_token(user: Users, expires_delta: timedelta):
    encode = {'username': user.username, 'email': user.email, 'userid': user.id}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp' : expires})
    return jwt.encode(encode, Security_key, algorithm=Algorithem)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)], db: db_dependecy):
    try:
        payload = jwt.decode(token, Security_key, algorithms=Algorithem)
        username: str = payload.get('username')
        userid: int = payload.get('userid')
        email: str = payload.get('email')
        if username is None or userid is None or email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate the User")
        
        user =  db.query(Users).filter(Users.username == username and Users.email == email and Users.id == userid).first()

        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate the User")
        return user
    
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate the User")






class UserRequest(BaseModel):
    email: EmailStr = Field(alias= "Email")
    username: str = Field(alias= "User Name")
    first_name: str = Field(alias= "First Name")
    last_name: str = Field(alias= "Last Name")
    role: str = Field(alias= "User Role")
    password: str = Field(alias= "Login Password")

    class Config:
        json_schema_extra = {
            'example': {
                'Email': 'Pavan@gmail.com',
                'User Name': 'Pavan Kumar',
                'First Name': 'Pavan',
                'Last Name': 'S',
                'User Role': 'Admin',
                'Login Password': '123456'
            }
        }

class UserResponse(BaseModel):
    email: str
    username: str
    first_name: str
    last_name: str
    role: str

@router.get("/user", status_code=status.HTTP_201_CREATED, response_model=List[UserResponse])
async def get_user(db: db_dependecy):
    return db.query(Users).all()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependecy, user_request: UserRequest):
    username =  db.query(Users).filter(Users.username == user_request.username).first()
    useremail =  db.query(Users).filter(Users.email == user_request.email).first()
    if username is not None:
        return "User name is already taken"
    elif useremail is not None:
        return "Email is already taken"

    user_model = Users(
        email = user_request.email,
        username = user_request.username,
        first_name = user_request.first_name,
        last_name = user_request.last_name,
        hash_password = hash_password(user_request.password),
        role = user_request.role,
        is_active = True
    )

    # return user_model

    db.add(user_model)
    db.commit()


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependecy):
    user = authenticate_user(form_data.username, form_data.password, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Could not validate the User")
    
    accesstoken = create_access_token(user, timedelta(minutes=60))

    token = Token(
        access_token=accesstoken,
        token_type="bearer"
    )

    return token

