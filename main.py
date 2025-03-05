from fastapi import FastAPI, Depends, HTTPException, status
from database import engine, Base
from routes import users, relay_modules, relays
from utils import init_admin
from fastapi.security import OAuth2PasswordRequestForm
from auth import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta
from sqlalchemy.orm import Session
from database import get_db
import uvicorn

# Bazani yaratish
Base.metadata.create_all(bind=engine)

app = FastAPI()
init_admin()

# Routerlarni qo‘shish
app.include_router(users.router)
app.include_router(relay_modules.router)
app.include_router(relays.router)

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