from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from crud import create_relay_module
from schemas import RelayModuleCreate

router = APIRouter()

@router.post("/relay_module/")
def add_relay_module(module: RelayModuleCreate, db: Session = Depends(get_db)):
    return create_relay_module(db, module.ip_address, module.port, module.name, module.relays_count)
