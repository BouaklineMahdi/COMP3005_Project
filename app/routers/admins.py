from fastapi import APIRouter, HTTPException
from app.db_raw import get_cursor

router = APIRouter(prefix="/admins", tags=["admins"])

@router.get("/db-health")
def db_health():
    try:
        with get_cursor() as cur:
            cur.execute("SELECT 1 AS ok;")
            row = cur.fetchone()
        return {"db": "ok", "value": row["ok"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
