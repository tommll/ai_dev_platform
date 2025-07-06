from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class DatasetBase(BaseModel):
    name: str
    description: Optional[str] = None


class DatasetCreate(DatasetBase):
    project_id: int


class DatasetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class DatasetResponse(DatasetBase):
    id: int
    is_active: bool
    project_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class DatasetItemBase(BaseModel):
    input_data: Dict[str, Any]
    expected_output: Optional[str] = None
    # metadata: Optional[Dict[str, Any]] = None


class DatasetItemCreate(DatasetItemBase):
    dataset_id: int


class DatasetItemResponse(DatasetItemBase):
    id: int
    dataset_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class DatasetItemBulkCreate(BaseModel):
    items: List[Dict[str, Any]] 