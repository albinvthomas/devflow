from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
from routers import auth, health, github, projects, deployments

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the database tables on startup
    async with engine.begin() as conn:
        # In a real app, you might want to use Alembic for migrations instead
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Clean up resources on shutdown
    await engine.dispose()

app = FastAPI(
    title="DevFlow API",
    description="Backend for DevFlow CI/CD automation platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://localhost:8000",
        "https://*.onrender.com",
        "https://*.vercel.app"
    ],  # Allows local dev, Render frontend, and Vercel frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
from fastapi.responses import JSONResponse
import traceback

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Don't catch HTTPException globally to allow normal FastAPI behavior for 404, 401 etc.
    if isinstance(exc, HTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    
    # Log the full traceback for debugging
    traceback.print_exc()
    
    return JSONResponse(
        status_code=500,
        content={"error": str(exc) or "An unexpected error occurred."}
    )

app.include_router(auth.router)
app.include_router(github.router)
app.include_router(projects.router)
app.include_router(deployments.router)
