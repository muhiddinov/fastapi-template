from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String, default="user")  # 'admin' yoki 'user'

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
