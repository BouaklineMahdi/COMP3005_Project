# app/routers/ui.py

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(
    prefix="/ui",
    tags=["ui"],
)


@router.get("/", response_class=HTMLResponse)
def ui_home(request: Request):
    """
    Landing page: choose role and log in.
    """
    return templates.TemplateResponse(
        "home.html",
        {"request": request},
    )


@router.get("/login/{role}", response_class=HTMLResponse)
def login_page(role: str, request: Request):
    """
    Generic login page, parameterized by role: member/trainer/admin.
    """
    role = role.lower()
    if role not in {"member", "trainer", "admin"}:
        raise HTTPException(status_code=404, detail="Unknown role")

    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "role": role,
        },
    )


@router.get("/dashboard/member", response_class=HTMLResponse)
def member_dashboard_page(request: Request):
    """
    Member dashboard shell – actual data is fetched via JS using token.
    """
    return templates.TemplateResponse(
        "member_dashboard.html",
        {"request": request},
    )


@router.get("/dashboard/trainer", response_class=HTMLResponse)
def trainer_dashboard_page(request: Request):
    """
    Trainer dashboard shell.
    """
    return templates.TemplateResponse(
        "trainer_dashboard.html",
        {"request": request},
    )


@router.get("/dashboard/admin", response_class=HTMLResponse)
def admin_dashboard_page(request: Request):
    """
    Admin dashboard shell.
    """
    return templates.TemplateResponse(
        "admin_dashboard.html",
        {"request": request},
    )


@router.get("/logout")
def ui_logout():
    """
    Front-end logout: just redirect; JS will clear localStorage.
    """
    # The JS clears localStorage; here we only send them home.
    return RedirectResponse(url="/ui/", status_code=302)
