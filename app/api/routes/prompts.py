from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.database import get_db
from app.models.user import User
from app.models.project import Project
from app.models.prompt import Prompt, PromptVersion
from app.schemas.prompt import (
    PromptCreate, PromptUpdate, PromptResponse,
    PromptVersionCreate, PromptVersionResponse
)
from app.services.auth import get_current_user

router = APIRouter(tags=["Prompt Management"])


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


@router.get("/projects/{project_id}/prompts", response_model=List[PromptResponse])
async def get_project_prompts(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all prompts for a project"""
    await verify_project_access(project_id, current_user, db)
    
    result = await db.execute(
        select(Prompt).where(Prompt.project_id == project_id)
    )
    prompts = result.scalars().all()
    
    return prompts


@router.post("/projects/{project_id}/prompts", response_model=PromptResponse)
async def create_prompt(
    project_id: int,
    prompt_data: PromptCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new prompt for a project"""
    await verify_project_access(project_id, current_user, db)
    
    # Verify project_id matches
    if prompt_data.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project ID mismatch"
        )
    
    prompt = Prompt(**prompt_data.dict())
    db.add(prompt)
    await db.commit()
    await db.refresh(prompt)
    
    return prompt


@router.get("/prompts/{prompt_id}/versions", response_model=List[PromptVersionResponse])
async def get_prompt_versions(
    prompt_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all versions of a prompt"""
    # Get prompt and verify access
    result = await db.execute(
        select(Prompt).join(Project).where(
            and_(
                Prompt.id == prompt_id,
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
    
    # Get versions
    result = await db.execute(
        select(PromptVersion).where(PromptVersion.prompt_id == prompt_id)
    )
    versions = result.scalars().all()
    
    return versions


@router.post("/prompts/{prompt_id}/versions", response_model=PromptVersionResponse)
async def create_prompt_version(
    prompt_id: int,
    version_data: PromptVersionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new version of a prompt"""
    # Get prompt and verify access
    result = await db.execute(
        select(Prompt).join(Project).where(
            and_(
                Prompt.id == prompt_id,
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
    
    # Verify prompt_id matches
    if version_data.prompt_id != prompt_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Prompt ID mismatch"
        )
    
    # Check if version already exists
    result = await db.execute(
        select(PromptVersion).where(
            and_(
                PromptVersion.prompt_id == prompt_id,
                PromptVersion.version == version_data.version
            )
        )
    )
    existing_version = result.scalar_one_or_none()
    
    if existing_version:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Version already exists"
        )
    
    version = PromptVersion(**version_data.dict())
    db.add(version)
    await db.commit()
    await db.refresh(version)
    
    return version


@router.put("/prompts/{prompt_id}/versions/{version}/deploy")
async def deploy_prompt_version(
    prompt_id: int,
    version: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Deploy a specific version of a prompt"""
    # Get prompt and verify access
    result = await db.execute(
        select(Prompt).join(Project).where(
            and_(
                Prompt.id == prompt_id,
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
    
    # Get the specific version
    result = await db.execute(
        select(PromptVersion).where(
            and_(
                PromptVersion.prompt_id == prompt_id,
                PromptVersion.version == version
            )
        )
    )
    prompt_version = result.scalar_one_or_none()
    
    if not prompt_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt version not found"
        )
    
    # Undeploy all other versions of this prompt
    await db.execute(
        select(PromptVersion).where(PromptVersion.prompt_id == prompt_id)
    )
    all_versions = result.scalars().all()
    
    for v in all_versions:
        v.is_deployed = False
    
    # Deploy the specified version
    prompt_version.is_deployed = True
    prompt.is_deployed = True
    
    await db.commit()
    
    return {
        "message": f"Version {version} deployed successfully",
        "prompt_id": prompt_id,
        "version": version
    } 