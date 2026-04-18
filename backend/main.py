from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from config import settings
from database import init_db
from routes import router

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs("/opt/craque-do-jogo/uploads", exist_ok=True)
    init_db()
    print("Store API ready on port 5051")
    yield
    print("Shutting down Store API")


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory="/opt/craque-do-jogo/uploads"), name="uploads")

app.include_router(router)

STATIC_DIR = "/opt/craque-do-jogo/backend/static"


@app.get("/")
def serve_root():
    return FileResponse(f"{STATIC_DIR}/index.html")


@app.get("/assets/{path:path}")
def serve_assets(path: str):
    full_path = f"{STATIC_DIR}/assets/{path}"
    if os.path.exists(full_path):
        return FileResponse(full_path)
    raise HTTPException(status_code=404)


@app.get("/{path:path}", include_in_schema=False)
async def serve_spa_fallback(path: str):
    if path.startswith("api/") or path.startswith("assets/") or path.startswith("uploads/"):
        raise HTTPException(status_code=404)
    index = f"{STATIC_DIR}/index.html"
    if os.path.exists(index):
        return FileResponse(index)
    raise HTTPException(status_code=404)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5051)
