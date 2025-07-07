import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.project import Project
from app.models.experiment import Experiment, ExperimentRun, RunStatus
from app.models.prompt import Prompt
from app.models.dataset import Dataset
from app.schemas.experiment import (
    ExperimentCreate, ExperimentUpdate, ExperimentResponse,
    ExperimentRunCreate, ExperimentRunResponse
)
from app.services.auth import get_current_user
from app.services.evaluation_worker import EvaluationWorker

router = APIRouter(tags=["Experiment Execution"])


async def verify_project_access(
    project_id: int,
    current_user: User,
    db: AsyncSession
) -> Project:
    """Verify user has access to the project"""
    result = await db.execute(
        select(Project).where(
            and_(
                Project.id == project_id,
                Project.organization_id == current_user.organization_id
            )
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return project


async def verify_experiment_access(
    experiment_id: int,
    current_user: User,
    db: AsyncSession
) -> Experiment:
    """Verify user has access to the experiment"""
    result = await db.execute(
        select(Experiment).join(Project).where(
            and_(
                Experiment.id == experiment_id,
                Project.organization_id == current_user.organization_id
            )
        )
    )
    experiment = result.scalar_one_or_none()
    
    if not experiment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experiment not found"
        )
    
    return experiment


async def verify_run_access(
    experiment_id: int,
    run_id: str,
    current_user: User,
    db: AsyncSession
) -> ExperimentRun:
    """Verify user has access to the experiment run"""
    result = await db.execute(
        select(ExperimentRun).join(Experiment).join(Project).where(
            and_(
                ExperimentRun.experiment_id == experiment_id,
                ExperimentRun.id == run_id,
                Project.organization_id == current_user.organization_id
            )
        )
    )
    run = result.scalar_one_or_none()
    
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experiment run not found"
        )
    
    return run


@router.post("/experiments", response_model=ExperimentResponse)
async def create_experiment(
    experiment_data: ExperimentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new experiment"""
    # Verify project access
    await verify_project_access(experiment_data.project_id, current_user, db)
    
    # Verify prompt exists and belongs to the project
    result = await db.execute(
        select(Prompt).where(
            and_(
                Prompt.id == experiment_data.prompt_id,
                Prompt.project_id == experiment_data.project_id
            )
        )
    )
    prompt = result.scalar_one_or_none()
    
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found in project"
        )
    
    # Verify dataset exists and belongs to the project
    result = await db.execute(
        select(Dataset).where(
            and_(
                Dataset.id == experiment_data.dataset_id,
                Dataset.project_id == experiment_data.project_id
            )
        )
    )
    dataset = result.scalar_one_or_none()
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found in project"
        )
    
    experiment = Experiment(**experiment_data.dict())
    db.add(experiment)
    await db.commit()
    await db.refresh(experiment)
    
    return experiment


@router.post("/experiments/{experiment_id}/runs", response_model=ExperimentRunResponse)
async def create_experiment_run(
    experiment_id: int,
    run_data: ExperimentRunCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create and start a new experiment run"""
    experiment = await verify_experiment_access(experiment_id, current_user, db)
    
    # Verify experiment_id matches
    if run_data.experiment_id != experiment_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Experiment ID mismatch"
        )
    
    # Generate unique run ID
    run_id = f"run_{uuid.uuid4().hex[:8]}"
    
    # Create experiment run
    run = ExperimentRun(
        id=run_id,
        experiment_id=experiment_id,
        status=RunStatus.PENDING
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)
    
    # Start evaluation in background
    background_tasks.add_task(start_evaluation, run_id, experiment_id, db)
    
    return {
        "id": run.id,
        "run_id": run.id,
        "status": run.status,
        "total_items": run.total_items,
        "completed_items": run.completed_items,
        "failed_items": run.failed_items,
        "metrics": run.metrics,
        "experiment_id": run.experiment_id,
        "created_at": run.created_at,
        "started_at": run.started_at,
        "completed_at": run.completed_at
    }


async def start_evaluation(run_id: str, experiment_id: int, db: AsyncSession):
    """Start the evaluation process for an experiment run"""
    try:
        # Update run status to running
        result = await db.execute(
            select(ExperimentRun).where(ExperimentRun.id == run_id)
        )
        run = result.scalar_one_or_none()
        
        if run:
            run.status = RunStatus.RUNNING
            run.started_at = datetime.utcnow()
            await db.commit()
        
        # Initialize evaluation worker
        worker = EvaluationWorker(db)
        await worker.evaluate_experiment_run(run_id, experiment_id)
        
    except Exception as e:
        # Update run status to failed
        result = await db.execute(
            select(ExperimentRun).where(ExperimentRun.id == run_id)
        )
        run = result.scalar_one_or_none()
        
        if run:
            run.status = RunStatus.FAILED
            await db.commit()
        
        print(f"Evaluation failed for run {run_id}: {str(e)}")


@router.get("/experiments/{experiment_id}/runs/{run_id}/status")
async def get_run_status(
    experiment_id: int,
    run_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get the status of an experiment run"""
    run = await verify_run_access(experiment_id, run_id, current_user, db)
    
    return {
        "run_id": run.id,
        "status": run.status,
        "total_items": run.total_items,
        "completed_items": run.completed_items,
        "failed_items": run.failed_items,
        "progress_percentage": (run.completed_items / run.total_items * 100) if run.total_items > 0 else 0,
        "created_at": run.created_at,
        "started_at": run.started_at,
        "completed_at": run.completed_at
    }


@router.get("/experiments/{experiment_id}/runs/{run_id}/results")
async def get_run_results(
    experiment_id: int,
    run_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get the results of an experiment run"""
    run = await verify_run_access(experiment_id, run_id, current_user, db)
    
    if run.status != RunStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Experiment run is not completed yet"
        )
    
    # Get evaluation results
    from app.models.evaluation import EvaluationResult
    
    result = await db.execute(
        select(EvaluationResult).where(EvaluationResult.experiment_run_id == run_id)
    )
    evaluation_results = result.scalars().all()
    
    return {
        "run_id": run.id,
        "status": run.status,
        "metrics": run.metrics,
        "total_items": run.total_items,
        "completed_items": run.completed_items,
        "failed_items": run.failed_items,
        "evaluation_results": [
            {
                "id": er.id,
                "dataset_item_id": er.dataset_item_id,
                "input_data": er.input_data,
                "output_data": er.output_data,
                "metrics": er.metrics,
                "is_success": er.is_success,
                "error_message": er.error_message,
                "created_at": er.created_at
            }
            for er in evaluation_results
        ],
        "created_at": run.created_at,
        "started_at": run.started_at,
        "completed_at": run.completed_at
    }


@router.post("/experiments/{experiment_id}/runs/{run_id}/cancel")
async def cancel_experiment_run(
    experiment_id: int,
    run_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel an experiment run"""
    run = await verify_run_access(experiment_id, run_id, current_user, db)
    
    if run.status in [RunStatus.COMPLETED, RunStatus.FAILED, RunStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel a completed, failed, or already cancelled run"
        )
    
    run.status = RunStatus.CANCELLED
    run.completed_at = datetime.utcnow()
    await db.commit()
    
    return {
        "message": "Experiment run cancelled successfully",
        "run_id": run.id,
        "status": run.status
    } 