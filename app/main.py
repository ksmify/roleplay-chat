from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.chat.routes import router as chat_router
from app.api.routes.health import router as health_router
from app.api.routes import characters
from app.api.routes import users
from app.api.routes import upload

from app.core.config import settings
from app.db.session import create_tables

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

# Static files
app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static",
)

@app.on_event("startup")
def startup_event():
    create_tables()

app.include_router(health_router)
app.include_router(chat_router)
app.include_router(characters.router)
app.include_router(users.router)
app.include_router(upload.router)

@app.get("/")
async def root() -> dict[str, str]:
    return {
        "message": settings.app_name,
    }