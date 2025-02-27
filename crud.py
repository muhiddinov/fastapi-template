from sqlalchemy.orm import Session
from models import User, RelayModule, Relay
import bcrypt

def create_user(db: Session, username: str, password: str, role: str = "user"):
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    db_user = User(username=username, password=hashed_password, role=role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: Session):
    return db.query(User).all()

def create_relay_module(db: Session, ip_address: str, port: int, name: str, relays_count: int):
    db_module = RelayModule(ip_address=ip_address, port=port, name=name, relays_count=relays_count)
    db.add(db_module)
    db.commit()
    db.refresh(db_module)
    return db_module

def create_relay(db: Session, relay_module_id: int, relay_number: int, status: bool):
    db_relay = Relay(relay_module_id=relay_module_id, relay_number=relay_number, status=status)
    db.add(db_relay)
    db.commit()
    db.refresh(db_relay)
    return db_relay
