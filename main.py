from fastapi import FastAPI, Depends, HTTPException, status
from database import engine, Base, get_db
from routes import users, relay_modules, relays
from utils import init_admin
from fastapi.security import OAuth2PasswordRequestForm
from auth import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta
from sqlalchemy.orm import Session
from fastapi.websockets import WebSocket, WebSocketDisconnect
import uvicorn
import json

# Bazani yaratish
Base.metadata.create_all(bind=engine)

app = FastAPI()
init_admin()

# Routerlarni qo‘shish
app.include_router(users.router)
app.include_router(relay_modules.router)
app.include_router(relays.router)

clients = []
wash_status = {
    "status": "idle",  # 'idle', 'running', 'paused'
    "active_option": None,
    "balance": 0,
    "remaining_time": 0,
    "paused_time": 0
}

@app.websocket("/ws/status")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            message = await websocket.receive_text()
            for client in clients:
                await client.send_text(json.dumps({"host": "server", "data": message}))
    except WebSocketDisconnect:
        clients.remove(websocket)

@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    access_token = create_access_token(
        {"sub": user.username, "role": user.role}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, log_level="info", reload=True)