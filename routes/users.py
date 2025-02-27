from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from auth import authenticate_user, create_access_token
from crud import create_user, get_users
from schemas import UserCreate

router = APIRouter()

@router.post("/users/")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user.username, user.password, user.role)

@router.get("/users/")
def list_users(db: Session = Depends(get_db)):
    return get_users(db)
