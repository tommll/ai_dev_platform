from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.services.redis_queue import RedisQueue
from app.models.experiment import ExperimentRun
from app.schemas.experiment import (
    EvaluationJobRequest, 
    EvaluationJobResponse, 
    JobStatusResponse,
    ProgressResponse
)
from app.schemas.evaluation import EvaluationResultResponse
from app.models.evaluation import EvaluationResult

router = APIRouter(prefix="/evaluation", tags=["evaluation"])


@router.post("/jobs", response_model=EvaluationJobResponse)
async def submit_evaluation_job(
    job_request: EvaluationJobRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Submit an evaluation job to the queue"""
    
    # Verify experiment run exists
    stmt = select(ExperimentRun).where(ExperimentRun.run_id == job_request.experiment_run_id)
    result = await db.execute(stmt)
    run = result.scalar_one_or_none()
    
    if not run:
        raise HTTPException(status_code=404, detail="Experiment run not found")
    
    # Convert Pydantic model to dict for Redis
    job_data = {
        "experiment_run_id": job_request.experiment_run_id,
        "dataset_items": [item.dict() for item in job_request.dataset_items],
        "prompt_config": job_request.prompt_config.dict(),
        "evaluators": [evaluator.dict() for evaluator in job_request.evaluators],
        "execution_config": job_request.execution_config.dict()
    }
    
    # Enqueue job
    redis_queue = RedisQueue()
    job_id = await redis_queue.enqueue_job(job_data)
    await redis_queue.close()
    
    return EvaluationJobResponse(
        job_id=job_id,
        status="queued",
        experiment_run_id=job_request.experiment_run_id,
        created_at=job_data.get("created_at", "")
    )


@router.get("/jobs/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """Get the status of an evaluation job"""
    redis_queue = RedisQueue()
    job_data = await redis_queue.get_job_status(job_id)
    await redis_queue.close()
    
    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JobStatusResponse(
        job_id=job_id,
        status=job_data.get("status", "unknown"),
        progress=job_data.get("progress"),
        created_at=job_data.get("created_at", "")
    )


@router.get("/runs/{run_id}/progress", response_model=ProgressResponse)
async def get_run_progress(run_id: str):
    """Get the progress of an experiment run"""
    redis_queue = RedisQueue()
    progress_data = await redis_queue.get_progress(run_id)
    await redis_queue.close()
    
    if not progress_data:
        raise HTTPException(status_code=404, detail="Run progress not found")
    
    return ProgressResponse(**progress_data)


@router.get("/runs/{run_id}/results", response_model=List[EvaluationResultResponse])
async def get_run_results(
    run_id: str,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """Get evaluation results for an experiment run"""
    
    # Get experiment run
    stmt = select(ExperimentRun).where(ExperimentRun.run_id == run_id)
    result = await db.execute(stmt)
    run = result.scalar_one_or_none()
    
    if not run:
        raise HTTPException(status_code=404, detail="Experiment run not found")
    
    # Get evaluation results
    stmt = select(EvaluationResult).where(
        EvaluationResult.experiment_run_id == run.id
    ).offset(offset).limit(limit)
    
    result = await db.execute(stmt)
    evaluation_results = result.scalars().all()
    
    return [EvaluationResultResponse.from_orm(r) for r in evaluation_results]


@router.post("/runs/{run_id}/cancel")
async def cancel_run(run_id: str, db: AsyncSession = Depends(get_db)):
    """Cancel an experiment run"""
    
    # Get experiment run
    stmt = select(ExperimentRun).where(ExperimentRun.run_id == run_id)
    result = await db.execute(stmt)
    run = result.scalar_one_or_none()
    
    if not run:
        raise HTTPException(status_code=404, detail="Experiment run not found")
    
    # Update status to cancelled
    from app.models.experiment import RunStatus
    run.status = RunStatus.CANCELLED
    await db.commit()
    
    return {"message": "Run cancelled successfully"} 