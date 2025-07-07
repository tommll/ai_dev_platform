import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, text
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User
from app.models.project import Project
from app.models.trace import Trace
from app.models.metrics import EvalMetrics, TraceMetrics, UsageMetrics
from app.services.auth import get_current_user

router = APIRouter(tags=["Observability"])


class TraceCreate(BaseModel):
    prompt_id: int
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    latency_ms: Optional[float] = None
    tokens_used: Optional[int] = None
    cost_usd: Optional[float] = None
    model_name: Optional[str] = None
    model_provider: Optional[str] = None
    is_success: bool = True
    error_message: Optional[str] = None


class AlertRuleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    metric_name: str
    threshold: float
    operator: str  # "gt", "lt", "eq", "gte", "lte"
    time_window_minutes: int = 60
    is_active: bool = True


class AlertRuleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    metric_name: str
    threshold: float
    operator: str
    time_window_minutes: int
    is_active: bool
    project_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


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


@router.post("/traces")
async def submit_trace(
    trace_data: TraceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Submit a production trace"""
    # Verify prompt exists and user has access to the project
    from app.models.prompt import Prompt
    
    result = await db.execute(
        select(Prompt).join(Project).where(
            and_(
                Prompt.id == trace_data.prompt_id,
                Project.organization_id == current_user.organization_id
            )
        )
    )
    prompt = result.scalar_one_or_none()
    
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found"
        )
    
    # Create trace
    trace = Trace(
        trace_id=f"trace_{uuid.uuid4().hex[:8]}",
        prompt_id=trace_data.prompt_id,
        input_data=trace_data.input_data,
        output_data=trace_data.output_data,
        latency_ms=trace_data.latency_ms,
        tokens_used=trace_data.tokens_used,
        cost_usd=trace_data.cost_usd,
        model_name=trace_data.model_name,
        model_provider=trace_data.model_provider,
        is_success=trace_data.is_success,
        error_message=trace_data.error_message,
        project_id=prompt.project_id
    )
    
    db.add(trace)
    await db.commit()
    await db.refresh(trace)
    
    # Store trace metrics for observability
    if trace_data.latency_ms and trace_data.cost_usd and trace_data.model_name:
        trace_metric = TraceMetrics(
            project_id=prompt.project_id,
            model=trace_data.model_name,
            latency_ms=trace_data.latency_ms,
            cost_usd=trace_data.cost_usd
        )
        db.add(trace_metric)
        await db.commit()
    
    return {
        "trace_id": trace.trace_id,
        "message": "Trace submitted successfully"
    }


@router.get("/projects/{project_id}/metrics")
async def query_metrics(
    project_id: int,
    metric_type: str = Query(..., description="Type of metric: eval, trace, usage"),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    interval: str = Query("1 hour", description="Time interval for aggregation"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Query metrics for a project"""
    await verify_project_access(project_id, current_user, db)
    
    # Set default time range if not provided
    if not end_time:
        end_time = datetime.utcnow()
    if not start_time:
        start_time = end_time - timedelta(hours=24)
    
    try:
        if metric_type == "eval":
            # Query evaluation metrics
            query = text("""
                SELECT 
                    time_bucket(:interval, time) as bucket,
                    metric_name,
                    AVG(value) as avg_value,
                    MAX(value) as max_value,
                    MIN(value) as min_value,
                    COUNT(*) as count
                FROM eval_metrics 
                WHERE project_id = :project_id 
                AND time >= :start_time 
                AND time <= :end_time
                GROUP BY bucket, metric_name
                ORDER BY bucket DESC
            """)
            
            result = await db.execute(
                query,
                {
                    "interval": interval,
                    "project_id": project_id,
                    "start_time": start_time,
                    "end_time": end_time
                }
            )
            
            metrics = []
            for row in result:
                metrics.append({
                    "bucket": row.bucket,
                    "metric_name": row.metric_name,
                    "avg_value": float(row.avg_value),
                    "max_value": float(row.max_value),
                    "min_value": float(row.min_value),
                    "count": row.count
                })
            
            return {"metrics": metrics}
            
        elif metric_type == "trace":
            # Query trace metrics
            query = text("""
                SELECT 
                    time_bucket(:interval, time) as bucket,
                    model,
                    AVG(latency_ms) as avg_latency,
                    MAX(latency_ms) as max_latency,
                    MIN(latency_ms) as min_latency,
                    SUM(cost_usd) as total_cost,
                    COUNT(*) as request_count
                FROM trace_metrics 
                WHERE project_id = :project_id 
                AND time >= :start_time 
                AND time <= :end_time
                GROUP BY bucket, model
                ORDER BY bucket DESC
            """)
            
            result = await db.execute(
                query,
                {
                    "interval": interval,
                    "project_id": project_id,
                    "start_time": start_time,
                    "end_time": end_time
                }
            )
            
            metrics = []
            for row in result:
                metrics.append({
                    "bucket": row.bucket,
                    "model": row.model,
                    "avg_latency": float(row.avg_latency),
                    "max_latency": float(row.max_latency),
                    "min_latency": float(row.min_latency),
                    "total_cost": float(row.total_cost),
                    "request_count": row.request_count
                })
            
            return {"metrics": metrics}
            
        elif metric_type == "usage":
            # Query usage metrics
            query = text("""
                SELECT 
                    time_bucket(:interval, time) as bucket,
                    SUM(api_calls) as total_api_calls,
                    SUM(tokens_used) as total_tokens
                FROM usage_metrics 
                WHERE organization_id = :organization_id 
                AND time >= :start_time 
                AND time <= :end_time
                GROUP BY bucket
                ORDER BY bucket DESC
            """)
            
            result = await db.execute(
                query,
                {
                    "interval": interval,
                    "organization_id": current_user.organization_id,
                    "start_time": start_time,
                    "end_time": end_time
                }
            )
            
            metrics = []
            for row in result:
                metrics.append({
                    "bucket": row.bucket,
                    "total_api_calls": row.total_api_calls,
                    "total_tokens": row.total_tokens
                })
            
            return {"metrics": metrics}
            
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid metric type. Must be 'eval', 'trace', or 'usage'"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error querying metrics: {str(e)}"
        )


@router.post("/projects/{project_id}/alerts", response_model=AlertRuleResponse)
async def create_alert_rule(
    project_id: int,
    alert_data: AlertRuleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create an alert rule for a project"""
    await verify_project_access(project_id, current_user, db)
    
    # Validate operator
    valid_operators = ["gt", "lt", "eq", "gte", "lte"]
    if alert_data.operator not in valid_operators:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid operator. Must be one of: {valid_operators}"
        )
    
    # Create alert rule (you would need to create an AlertRule model)
    # For now, we'll return a mock response
    alert_rule = {
        "id": 1,
        "name": alert_data.name,
        "description": alert_data.description,
        "metric_name": alert_data.metric_name,
        "threshold": alert_data.threshold,
        "operator": alert_data.operator,
        "time_window_minutes": alert_data.time_window_minutes,
        "is_active": alert_data.is_active,
        "project_id": project_id,
        "created_at": datetime.utcnow()
    }
    
    return alert_rule


@router.get("/projects/{project_id}/alerts")
async def list_active_alerts(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List active alerts for a project"""
    await verify_project_access(project_id, current_user, db)
    
    # For now, return mock data
    # In a real implementation, you would query the alert rules and check for triggered alerts
    alerts = [
        {
            "id": 1,
            "name": "High Latency Alert",
            "description": "Alert when average latency exceeds 2000ms",
            "metric_name": "latency_ms",
            "threshold": 2000.0,
            "operator": "gt",
            "time_window_minutes": 60,
            "is_active": True,
            "project_id": project_id,
            "created_at": datetime.utcnow() - timedelta(hours=1),
            "last_triggered": datetime.utcnow() - timedelta(minutes=30),
            "trigger_count": 5
        }
    ]
    
    return {"alerts": alerts} 