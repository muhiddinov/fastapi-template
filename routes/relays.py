from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Relay, RelayModule
from schemas import RelayCreate, RelayModuleCreate, RelayResponse, RelayModuleResponse
from dependencies import get_current_admin_user

router = APIRouter(
    prefix="/relays",
    tags=["Relays"],
    dependencies=[Depends(get_current_admin_user)]  # 🔐 Faqat adminlar uchun
)

# 🔹 Relay modul yaratish
@router.post("/modules/", response_model=RelayModuleResponse)
def create_relay_module(module: RelayModuleCreate, db: Session = Depends(get_db)):
    new_module = RelayModule(**module.dict())
    db.add(new_module)
    db.commit()
    db.refresh(new_module)
    return new_module

# 🔹 Barcha relay modullarni olish
@router.get("/modules/", response_model=list[RelayModuleResponse])
def get_relay_modules(db: Session = Depends(get_db)):
    return db.query(RelayModule).all()

# 🔹 Bitta relay modulni olish
@router.get("/modules/{module_id}", response_model=RelayModuleResponse)
def get_relay_module(module_id: int, db: Session = Depends(get_db)):
    module = db.query(RelayModule).filter(RelayModule.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Relay module not found")
    return module

# 🔹 Relay qo'shish
@router.post("/", response_model=RelayResponse)
def create_relay(relay: RelayCreate, db: Session = Depends(get_db)):
    relay_module = db.query(RelayModule).filter(RelayModule.id == relay.relay_module_id).first()
    if not relay_module:
        raise HTTPException(status_code=404, detail="Relay module not found")
    
    new_relay = Relay(**relay.dict())
    db.add(new_relay)
    db.commit()
    db.refresh(new_relay)
    return new_relay

# 🔹 Barcha relaylarni olish
@router.get("/", response_model=list[RelayResponse])
def get_relays(db: Session = Depends(get_db)):
    return db.query(Relay).all()

# 🔹 Bitta relayni olish
@router.get("/{relay_id}", response_model=RelayResponse)
def get_relay(relay_id: int, db: Session = Depends(get_db)):
    relay = db.query(Relay).filter(Relay.id == relay_id).first()
    if not relay:
        raise HTTPException(status_code=404, detail="Relay not found")
    return relay

# 🔹 Relay statusini o'zgartirish
@router.put("/{relay_id}/status", response_model=RelayResponse)
def update_relay_status(relay_id: int, status: bool, db: Session = Depends(get_db)):
    relay = db.query(Relay).filter(Relay.id == relay_id).first()
    if not relay:
        raise HTTPException(status_code=404, detail="Relay not found")
    
    relay.status = status
    db.commit()
    db.refresh(relay)
    return relay

# 🔹 Relayni o‘chirish
@router.delete("/{relay_id}")
def delete_relay(relay_id: int, db: Session = Depends(get_db)):
    relay = db.query(Relay).filter(Relay.id == relay_id).first()
    if not relay:
        raise HTTPException(status_code=404, detail="Relay not found")
    
    db.delete(relay)
    db.commit()
    return {"message": "Relay deleted successfully"}
