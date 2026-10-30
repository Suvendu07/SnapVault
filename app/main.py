from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models import user

from app.routers.auth_route import router as auth_routers

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG,)



app.include_router(auth_routers)

@app.get("/")
def root():
    return {
        "message" : "Smart Event photography Playform API",
        "status" : "running",
    }
    

@app.get("/healthy")
def health():
    return {"status" : "healthy"}


@app.get("/health/db")
def database_health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected",
        }

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Database connection failed",
        )
        

