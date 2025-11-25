# app/main.py
from fastapi import FastAPI
from app.routers import admins, members, trainers, auth

app = FastAPI(title="Health & Fitness Club Management")

app.include_router(admins.router)
app.include_router(members.router)
app.include_router(trainers.router)
app.include_router(auth.router)


@app.get("/")
def root():
    return {"status": "ok", "message": "Health & Fitness Club API"}


#uvicorn app.main:app --reload 
#http://127.0.0.1:8000/     this should say something like status: "ok"
#http://127.0.0.1:8000/docs#/   this should show you the default/ root or smth
