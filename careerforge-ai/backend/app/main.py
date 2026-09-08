from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from contextlib import asynccontextmanager
from app.config import settings
from app.api.routes import auth_router, resumes_router, jobs_router, analysis_router, interviews_router
from app.database import engine, Base
from app.models import models

@asynccontextmanager
async def lifespan(app: FastAPI):
    models.Base.metadata.create_all(bind=engine)
    yield

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="CareerForge AI API",
    description="API for the CareerForge AI platform",
    version="1.0.0",
    lifespan=lifespan
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS configuration
import os
origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
origins = [origin.strip() for origin in origins_str.split(",")]

# In case wildcards are needed or Vercel preview links are dynamic
if "*" in origins:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(resumes_router, prefix="/resumes", tags=["Resumes"])
app.include_router(jobs_router, prefix="/jobs", tags=["Jobs"])
app.include_router(analysis_router, prefix="/analysis", tags=["Analysis"])
app.include_router(interviews_router, prefix="/interviews", tags=["Interviews"])
