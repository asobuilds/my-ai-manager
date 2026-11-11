from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.calendar import router as calendar_router
from app.api.connections import router as connections_router
from app.api.jobs import router as jobs_router
from app.api.messages import router as messages_router
from app.api.profile import router as profile_router
from app.api.shop import router as shop_router
from app.api.user import router as user_router
from app.api.chat import router as chat_router
from app.api.social import router as social_router
from app.api.preferences import router as preferences_router
from app.api.suppliers import router as suppliers_router
from app.api.health import router as health_router
from app.api.home import router as home_router
from app.core.config import get_settings
from app.core.database import Base, engine

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup (dev convenience — use migrations in prod)
Base.metadata.create_all(bind=engine)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(connections_router, prefix="/api/v1")
app.include_router(messages_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
app.include_router(profile_router, prefix="/api/v1")
app.include_router(jobs_router, prefix="/api/v1")
app.include_router(shop_router, prefix="/api/v1")
app.include_router(calendar_router, prefix="/api/v1")
app.include_router(social_router, prefix="/api/v1")
app.include_router(preferences_router, prefix="/api/v1")
app.include_router(suppliers_router, prefix="/api/v1")
app.include_router(health_router, prefix="/api/v1")
app.include_router(home_router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.APP_NAME}
