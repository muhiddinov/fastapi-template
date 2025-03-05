from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from crud import create_user, get_users
from schemas import UserCreate
from dependencies import get_current_admin_user

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(get_current_admin_user)]  # 🔐 Faqat adminlar uchun
)

#dependencies=[Depends(get_current_admin_user)]
@router.post("/users/")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user.username, user.password, user.role)

@router.get("/users/")
def list_users(db: Session = Depends(get_db)):
    return get_users(db)

@router.delete("/users")
def delete_users(db: Session = Depends(get_db)):
    return delete_users(db)