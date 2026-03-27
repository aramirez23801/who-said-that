import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.database import AsyncSessionLocal, engine, Base
from backend.routers import auth as auth_router, game as game_router, leaderboard as leaderboard_router
from backend.services.seed_service import seed_database
import backend.models  # noqa: F401 — triggers model registration with Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs("static/images", exist_ok=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as db:
        await seed_database(db)
    yield


app = FastAPI(title="Who Said That?!", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("static/images", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth_router.router)
app.include_router(game_router.router)
app.include_router(leaderboard_router.router)


@app.get("/health")
async def health():
    return {"status": "ok", "message": "Who Said That?! is alive"}
