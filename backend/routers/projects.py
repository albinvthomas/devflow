from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import models
import schemas
import auth
from database import get_db
import github_service
import ai_engine
import deployment_service

router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)

@router.post("", response_model=schemas.ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(project_in: schemas.ProjectCreateRequest, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """Create a new project from a GitHub repository."""
    if not current_user.github_token:
        raise HTTPException(status_code=400, detail="GitHub account not linked. Please login to GitHub first.")
        
    try:
        # Fetch repo details to verify and get the actual URL/name
        repo_details = await github_service.get_repo_details(current_user.github_token, project_in.repo_full_name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not access repository: {str(e)}")
        
    # Analyze the tech stack
    try:
        tech_stack = await github_service.analyze_tech_stack(current_user.github_token, project_in.repo_full_name)
    except Exception as e:
        # Non-fatal if analysis fails, but we should log it. For now, default to empty dict.
        tech_stack = {}
        
    new_project = models.Project(
        user_id=current_user.id,
        repo_url=repo_details.get("html_url"),
        repo_name=repo_details.get("name"),
        tech_stack=tech_stack,
        status="active"
    )
    
    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)
    
    return new_project

@router.get("", response_model=List[schemas.ProjectResponse])
async def list_projects(db: AsyncSession = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """List all projects for the authenticated user."""
    # We fetch projects and we need to fetch the latest deployment status for each.
    # An easy way is to iterate and query, or use a left outer join.
    # We'll use a simple approach for now.
    result = await db.execute(select(models.Project).where(models.Project.user_id == current_user.id))
    projects = result.scalars().all()
    
    # We need to return them as dicts or modify the objects, but since models are bound to the session
    # and schemas allow from_attributes, we can just temporarily attach the attribute.
    for project in projects:
        dep_result = await db.execute(
            select(models.Deployment)
            .where(models.Deployment.project_id == project.id)
            .order_by(models.Deployment.created_at.desc())
            .limit(1)
        )
        latest_dep = dep_result.scalars().first()
        project.latest_deployment_status = latest_dep.status if latest_dep else None
        
    return projects

@router.get("/{project_id}", response_model=schemas.ProjectResponse)
async def get_project(project_id: UUID, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """Get a specific project's details."""
    result = await db.execute(select(models.Project).where(models.Project.id == project_id, models.Project.user_id == current_user.id))
    project = result.scalars().first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    return project

@router.post("/{project_id}/generate", response_model=schemas.DevOpsConfigsResponse)
async def generate_devops_configs(project_id: UUID, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """Generate DevOps configurations (Dockerfile, Compose, Actions) using AI."""
    # 1. Fetch project
    result = await db.execute(select(models.Project).where(models.Project.id == project_id, models.Project.user_id == current_user.id))
    project = result.scalars().first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    if not current_user.github_token:
        raise HTTPException(status_code=400, detail="GitHub account not linked. Please login to GitHub first.")
        
    # Extract full repo name (owner/repo) from the repo_url
    url_parts = project.repo_url.rstrip('/').split('/')
    if len(url_parts) < 2:
        raise HTTPException(status_code=400, detail="Invalid repository URL in project.")
    repo_full_name = f"{url_parts[-2]}/{url_parts[-1]}"
    
    # 2. Call GitHub API to get file tree
    try:
        file_tree = await github_service.get_repo_file_tree(current_user.github_token, repo_full_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch file tree from GitHub: {str(e)}")
        
    # 3. Call AI engine
    try:
        configs = await ai_engine.generate_devops_configs(project.repo_name, project.tech_stack, file_tree)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    # 4. Save results to DB
    project.generated_configs = configs
    db.add(project)
    await db.commit()
    
    return configs

@router.post("/{project_id}/deploy", response_model=schemas.DeploymentResponse, status_code=status.HTTP_201_CREATED)
async def deploy_project(project_id: UUID, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """Trigger a new deployment for the project using the generated configurations."""
    result = await db.execute(select(models.Project).where(models.Project.id == project_id, models.Project.user_id == current_user.id))
    project = result.scalars().first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    if not project.generated_configs or "dockerfile" not in project.generated_configs:
        raise HTTPException(status_code=400, detail="Project does not have a generated Dockerfile yet. Run generation first.")
        
    # Create deployment record
    new_deployment = models.Deployment(
        project_id=project.id,
        status="queued",
        logs="Deployment queued...\n"
    )
    db.add(new_deployment)
    await db.commit()
    await db.refresh(new_deployment)
    
    # Offload the actual build and run to a background task
    dockerfile_content = project.generated_configs["dockerfile"]
    
    background_tasks.add_task(
        deployment_service.run_deployment_pipeline,
        new_deployment.id,
        project.id,
        dockerfile_content,
        project.repo_url
    )
    
    return new_deployment

@router.get("/{project_id}/deployments", response_model=List[schemas.DeploymentResponse])
async def list_project_deployments(project_id: UUID, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """List all deployments for a specific project."""
    # Verify project
    result = await db.execute(select(models.Project).where(models.Project.id == project_id, models.Project.user_id == current_user.id))
    if not result.scalars().first():
        raise HTTPException(status_code=404, detail="Project not found")
        
    # Fetch deployments
    deployments_result = await db.execute(select(models.Deployment).where(models.Deployment.project_id == project_id).order_by(models.Deployment.created_at.desc()))
    return deployments_result.scalars().all()
