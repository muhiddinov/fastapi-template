from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta, datetime
import jwt
import bcrypt

SECRET_KEY = "*5)!ci0ki&i_7eygtflkdmfl!7-^$w+5+gv5s2ch4_w4c&%cak"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

DATABASE_URL = "sqlite:///./users.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String, default="user")  # 'admin' yoki 'user'

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"

class RelayModule(Base):
    __tablename__ = "relay_modules"
    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String, unique=True, index=True)
    port = Column(Integer)
    name = Column(String)
    relays_count = Column(Integer)
    relays = relationship("Relay", back_populates="relay_module")

class Relay(Base):
    __tablename__ = "relays"
    id = Column(Integer, primary_key=True, index=True)
    relay_module_id = Column(Integer, ForeignKey("relay_modules.id"))
    relay_number = Column(Integer)
    status = Column(Boolean, default=False)
    relay_module = relationship("RelayModule", back_populates="relays")

Base.metadata.create_all(bind=engine)

def init_admin():
    db = SessionLocal()
    admin_exists = db.query(User).filter(User.username == "admin").first()
    if not admin_exists:
        hashed_password = bcrypt.hashpw("adminpassword".encode(), bcrypt.gensalt()).decode()
        admin_user = User(username="admin", password=hashed_password, role="admin")
        db.add(admin_user)
        db.commit()
    db.close()

init_admin()

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def authenticate_user(db, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user or not bcrypt.checkpw(password.encode(), user.password.encode()):
        return None
    return user

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

 
@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token({"sub": user.username, "role": user.role}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}

def get_current_admin_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user = db.query(User).filter(User.username == payload["sub"]).first()
        if user.role != "admin":
            raise HTTPException(status_code=403, detail="Not authorized")
        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.put("/admin/update")
def update_admin(username: str, password: str, db: Session = Depends(get_db), admin: User = Depends(get_current_admin_user)):
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    admin.username = username
    admin.password = hashed_password
    db.commit()
    db.refresh(admin)
    return {"message": "Admin credentials updated successfully"}

@app.post("/users/", dependencies=[Depends(get_current_admin_user)])
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()
    new_user = User(username=user.username, password=hashed_password, role=user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/users/", dependencies=[Depends(get_current_admin_user)])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@app.post("/relay_module/", dependencies=[Depends(get_current_admin_user)])
def create_relay_module(ip_address: str, port: int, name: str, relays_count: int, db: Session = Depends(get_db)):
    new_module = RelayModule(ip_address=ip_address, port=port, name=name, relays_count=relays_count)
    db.add(new_module)
    db.commit()
    db.refresh(new_module)
    return new_module

@app.get("/relay_module/", dependencies=[Depends(get_current_admin_user)])
def get_relay_modules(db: Session = Depends(get_db)):
    return db.query(RelayModule).all()

@app.post("/relay/", dependencies=[Depends(get_current_admin_user)])
def create_relay(relay_module_id: int, relay_number: int, status: bool, db: Session = Depends(get_db)):
    new_relay = Relay(relay_module_id=relay_module_id, relay_number=relay_number, status=status)
    db.add(new_relay)
    db.commit()
    db.refresh(new_relay)
    return new_relay

@app.get("/relay/", dependencies=[Depends(get_current_admin_user)])
def get_relays(db: Session = Depends(get_db)):
    return db.query(Relay).all()


import uvicorn

if __name__ == "__main__":
    uvicorn.run("test:app", host="localhost", port=8000, log_level="info", reload=True)