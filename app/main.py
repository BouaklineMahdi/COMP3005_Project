# app/main.py
from fastapi import FastAPI
from app.routers import admins, members, trainers, auth
from fastapi.staticfiles import StaticFiles
from app.routers import ui
from fastapi.responses import RedirectResponse

app = FastAPI(title="Health & Fitness Club Management")

app.include_router(admins.router)
app.include_router(members.router)
app.include_router(trainers.router)
app.include_router(auth.router)
app.include_router(ui.router)


app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)



@app.get("/")
def root_redirect():
    return RedirectResponse(url="/ui/", status_code=302)



#uvicorn app.main:app --reload 
#http://127.0.0.1:8000/     this should say something like status: "ok"
#http://127.0.0.1:8000/docs#/   this should show you the default/ root or smth
