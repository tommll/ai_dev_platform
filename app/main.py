import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import init_db, close_db
from app.api.routes import evaluation, auth, prompts, datasets, experiments, observability
from app.services.evaluation_worker import EvaluationWorker
from app.database import AsyncSessionLocal


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting LLM Development Platform...")
    await init_db()
    
    # Start evaluation worker
    worker_task = asyncio.create_task(start_worker())
    
    yield
    
    # Shutdown
    print("Shutting down...")
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass
    await close_db()


async def start_worker():
    """Start the evaluation worker"""
    async with AsyncSessionLocal() as db:
        worker = EvaluationWorker(db)
        await worker.start()


app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(prompts.router, prefix=settings.api_v1_prefix)
app.include_router(datasets.router, prefix=settings.api_v1_prefix)
app.include_router(experiments.router, prefix=settings.api_v1_prefix)
app.include_router(observability.router, prefix=settings.api_v1_prefix)
app.include_router(evaluation.router, prefix=settings.api_v1_prefix)


@app.get("/")
async def root():
    return {
        "message": "LLM Development Platform API",
        "version": settings.version,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    ) 