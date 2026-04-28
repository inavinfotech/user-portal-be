from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.endpoints import users, auth, rbac, applications, external, sessions, dashboard, addresses
from app.db.session import engine, Base
from app.models import user, auth as auth_models, session, application  # Import all models

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Create database tables
    Base.metadata.create_all(bind=engine)
    
    # 2. Seed database (equivalent to seed_db.py logic)
    # from app.db.seeding import seed_db
    # seed_db()
    
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", tags=["health"])
def health_check():
    return {"status": "healthy", "service": settings.PROJECT_NAME}

# API Routes
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(rbac.router, prefix=f"{settings.API_V1_STR}/rbac", tags=["rbac"])
app.include_router(applications.router, prefix=f"{settings.API_V1_STR}/applications", tags=["applications"])
app.include_router(external.router, prefix=f"{settings.API_V1_STR}/external", tags=["external"])
app.include_router(sessions.router, prefix=f"{settings.API_V1_STR}/sessions", tags=["sessions"])
app.include_router(dashboard.router, prefix=f"{settings.API_V1_STR}/dashboard", tags=["dashboard"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(addresses.router, prefix=f"{settings.API_V1_STR}/addresses", tags=["addresses"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
