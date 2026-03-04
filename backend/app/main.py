from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings
from app.routers import auth, cages, events, lots, kpi

app = FastAPI(
    title="いけすログ API",
    description="養殖生産管理システム Ikesu Log",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static uploads
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

app.include_router(auth.router)
app.include_router(cages.router)
app.include_router(events.router)
app.include_router(lots.router)
app.include_router(kpi.router)


@app.get("/health")
async def health():
    return {"status": "ok", "app": "いけすログ"}
