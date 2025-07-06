from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class EvaluationResultResponse(BaseModel):
    id: int
    input_data: Dict[str, Any]
    expected_output: Optional[str] = None
    actual_output: Optional[str] = None
    accuracy_score: Optional[float] = None
    latency_ms: Optional[float] = None
    cost_usd: Optional[float] = None
    custom_metrics: Optional[Dict[str, Any]] = None
    is_success: bool
    error_message: Optional[str] = None
    experiment_run_id: int
    dataset_item_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True 