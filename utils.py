import bcrypt
from passlib.context import CryptContext
from database import SessionLocal
from models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 🔹 Parolni hash qilish
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# 🔹 Parolni tekshirish (hash bilan)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def init_admin():
    db = SessionLocal()
    admin_exists = db.query(User).filter(User.username == "admin").first()
    if not admin_exists:
        hashed_password = bcrypt.hashpw("adminpassword".encode(), bcrypt.gensalt()).decode()
        admin_user = User(username="admin", password=hashed_password, role="admin")
        db.add(admin_user)
        db.commit()
    db.close()