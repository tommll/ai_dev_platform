import json
import csv
from io import StringIO
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.database import get_db
from app.models.user import User
from app.models.project import Project
from app.models.dataset import Dataset, DatasetItem
from app.schemas.dataset import (
    DatasetCreate, DatasetUpdate, DatasetResponse,
    DatasetItemCreate, DatasetItemResponse, DatasetItemBulkCreate
)
from app.services.auth import get_current_user

router = APIRouter(tags=["Dataset Management"])


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


async def verify_dataset_access(
    dataset_id: int,
    current_user: User,
    db: AsyncSession
) -> Dataset:
    """Verify user has access to the dataset"""
    result = await db.execute(
        select(Dataset).join(Project).where(
            and_(
                Dataset.id == dataset_id,
                Project.organization_id == current_user.organization_id
            )
        )
    )
    dataset = result.scalar_one_or_none()
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    return dataset


@router.get("/projects/{project_id}/datasets", response_model=List[DatasetResponse])
async def get_project_datasets(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all datasets for a project"""
    await verify_project_access(project_id, current_user, db)
    
    result = await db.execute(
        select(Dataset).where(Dataset.project_id == project_id)
    )
    datasets = result.scalars().all()
    
    return datasets


@router.post("/projects/{project_id}/datasets", response_model=DatasetResponse)
async def create_dataset(
    project_id: int,
    dataset_data: DatasetCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new dataset for a project"""
    await verify_project_access(project_id, current_user, db)
    
    # Verify project_id matches
    if dataset_data.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project ID mismatch"
        )
    
    dataset = Dataset(**dataset_data.dict())
    db.add(dataset)
    await db.commit()
    await db.refresh(dataset)
    
    return dataset


@router.post("/datasets/{dataset_id}/upload")
async def upload_dataset_file(
    dataset_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload a file to create dataset items"""
    dataset = await verify_dataset_access(dataset_id, current_user, db)
    
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    # Read file content
    content = await file.read()
    
    try:
        if file.filename.endswith('.json'):
            # Parse JSON file
            data = json.loads(content.decode('utf-8'))
            items = []
            
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict) and 'items' in data:
                items = data['items']
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid JSON format. Expected array or object with 'items' key"
                )
            
            # Create dataset items
            created_items = []
            for item_data in items:
                if not isinstance(item_data, dict) or 'input_data' not in item_data:
                    continue
                
                item = DatasetItem(
                    dataset_id=dataset_id,
                    input_data=item_data['input_data'],
                    expected_output=item_data.get('expected_output')
                )
                db.add(item)
                created_items.append(item)
            
            await db.commit()
            
            return {
                "message": f"Successfully uploaded {len(created_items)} items",
                "dataset_id": dataset_id,
                "items_created": len(created_items)
            }
            
        elif file.filename.endswith('.csv'):
            # Parse CSV file
            csv_content = content.decode('utf-8')
            csv_reader = csv.DictReader(StringIO(csv_content))
            
            created_items = []
            for row in csv_reader:
                # Assume first column is input_data and second is expected_output
                input_data = {"text": row.get(list(row.keys())[0], "")}
                expected_output = row.get(list(row.keys())[1]) if len(row.keys()) > 1 else None
                
                item = DatasetItem(
                    dataset_id=dataset_id,
                    input_data=input_data,
                    expected_output=expected_output
                )
                db.add(item)
                created_items.append(item)
            
            await db.commit()
            
            return {
                "message": f"Successfully uploaded {len(created_items)} items",
                "dataset_id": dataset_id,
                "items_created": len(created_items)
            }
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file format. Please upload JSON or CSV files"
            )
            
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )


@router.get("/datasets/{dataset_id}/items", response_model=List[DatasetItemResponse])
async def get_dataset_items(
    dataset_id: int,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get dataset items with pagination"""
    await verify_dataset_access(dataset_id, current_user, db)
    
    result = await db.execute(
        select(DatasetItem)
        .where(DatasetItem.dataset_id == dataset_id)
        .offset(offset)
        .limit(limit)
    )
    items = result.scalars().all()
    
    return items


@router.post("/datasets/{dataset_id}/items/bulk")
async def create_dataset_items_bulk(
    dataset_id: int,
    bulk_data: DatasetItemBulkCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create multiple dataset items in bulk"""
    await verify_dataset_access(dataset_id, current_user, db)
    
    created_items = []
    for item_data in bulk_data.items:
        if not isinstance(item_data, dict) or 'input_data' not in item_data:
            continue
        
        item = DatasetItem(
            dataset_id=dataset_id,
            input_data=item_data['input_data'],
            expected_output=item_data.get('expected_output')
        )
        db.add(item)
        created_items.append(item)
    
    await db.commit()
    
    return {
        "message": f"Successfully created {len(created_items)} items",
        "dataset_id": dataset_id,
        "items_created": len(created_items)
    } 