from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from contextlib import asynccontextmanager
import os

from config import settings
from database import init_db
from routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs("/opt/craque-do-jogo/uploads", exist_ok=True)
    init_db()
    print("Store API ready on port 5051")
    yield
    print("Shutting down Store API")


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("/opt/craque-do-jogo/uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="/opt/craque-do-jogo/uploads"), name="uploads")

app.include_router(router)

STATIC_DIR = "/opt/craque-do-jogo/backend/static"

# Serve root → index.html
@app.get("/")
def serve_root():
    return FileResponse(f"{STATIC_DIR}/index.html")

# Serve assets with flexible hashing
@app.get("/assets/{path:path}")
def serve_assets(path: str):
    full_path = f"{STATIC_DIR}/assets/{path}"
    if os.path.exists(full_path):
        return FileResponse(full_path)
    raise HTTPException(status_code=404)

# Catch-all SPA — only non-API, non-asset routes
@app.get("/{path:path}", include_in_schema=False)
async def serve_spa_fallback(path: str):
    # Skip API routes and asset files
    if path.startswith("api/") or path.startswith("assets/") or path.startswith("uploads/"):
        raise HTTPException(status_code=404)
    index = f"{STATIC_DIR}/index.html"
    if os.path.exists(index):
        return FileResponse(index)
    raise HTTPException(status_code=404)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5051)