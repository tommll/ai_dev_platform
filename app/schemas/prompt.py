from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class PromptBase(BaseModel):
    name: str
    description: Optional[str] = None


class PromptCreate(PromptBase):
    project_id: int


class PromptUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    is_deployed: Optional[bool] = None


class PromptResponse(PromptBase):
    id: int
    is_active: bool
    is_deployed: bool
    project_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PromptVersionBase(BaseModel):
    version: str
    template: str
    variables: Optional[Dict[str, Any]] = None


class PromptVersionCreate(PromptVersionBase):
    prompt_id: int


class PromptVersionResponse(PromptVersionBase):
    id: int
    is_deployed: bool
    prompt_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True 