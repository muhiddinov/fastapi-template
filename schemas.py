from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"

class UserDelete(UserCreate):
    pass

class RelayModuleCreate(BaseModel):
    ip_address: str
    port: int
    name: str
    relays_count: int

class RelayCreate(BaseModel):
    relay_module_id: int
    relay_number: int
    status: bool

# 🔹 Relay Module javob schema (DB dan o'qish uchun)
class RelayModuleResponse(RelayModuleCreate):
    id: int

    class Config:
        from_attributes = True

# 🔹 Relay javob schema (DB dan o'qish uchun)
class RelayResponse(RelayCreate):
    id: int

    class Config:
        from_attributes = True