from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.models.experiment import ExperimentStatus, RunStatus


class ExperimentBase(BaseModel):
    name: str
    description: Optional[str] = None


class ExperimentCreate(ExperimentBase):
    prompt_id: int
    dataset_id: int
    model_configuration: Dict[str, Any]
    evaluation_config: Dict[str, Any]
    project_id: int


class ExperimentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ExperimentStatus] = None
    model_configuration: Optional[Dict[str, Any]] = None
    evaluation_config: Optional[Dict[str, Any]] = None


class ExperimentResponse(ExperimentBase):
    id: int
    status: ExperimentStatus
    prompt_id: int
    dataset_id: int
    model_configuration: Dict[str, Any]
    evaluation_config: Dict[str, Any]
    project_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ExperimentRunBase(BaseModel):
    pass


class ExperimentRunCreate(ExperimentRunBase):
    experiment_id: int


class ExperimentRunResponse(ExperimentRunBase):
    id: int
    run_id: str
    status: RunStatus
    total_items: int
    completed_items: int
    failed_items: int
    metrics: Optional[Dict[str, Any]] = None
    experiment_id: int
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Evaluation job schemas
class EvaluatorConfig(BaseModel):
    name: str
    config: Optional[Dict[str, Any]] = None


class PromptConfig(BaseModel):
    template: str
    model: str
    provider: str = "openai"
    temperature: float = 0.7
    max_tokens: int = 1000


class ExecutionConfig(BaseModel):
    timeout_seconds: int = 30
    max_retries: int = 3
    parallel_workers: int = 5


class DatasetItem(BaseModel):
    input: Dict[str, Any]
    expected: str
    # metadata: Optional[Dict[str, Any]] = None


class EvaluationJobRequest(BaseModel):
    experiment_run_id: str
    dataset_items: List[DatasetItem]
    prompt_config: PromptConfig
    evaluators: List[EvaluatorConfig]
    execution_config: ExecutionConfig = ExecutionConfig()


class EvaluationJobResponse(BaseModel):
    job_id: str
    status: str
    experiment_run_id: str
    created_at: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: Optional[int] = None
    created_at: str


class ProgressResponse(BaseModel):
    completed: int
    total: int
    percentage: float 