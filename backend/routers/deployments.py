from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import json

import models
import schemas
import auth
from database import get_db

router = APIRouter(
    prefix="/deployments",
    tags=["Deployments"]
)

@router.get("/{deployment_id}", response_model=schemas.DeploymentResponse)
async def get_deployment(deployment_id: UUID, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """Get status and details of a specific deployment."""
    # First get the deployment
    result = await db.execute(select(models.Deployment).where(models.Deployment.id == deployment_id))
    deployment = result.scalars().first()
    
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
        
    # Security check: Make sure the project belongs to the user
    project_result = await db.execute(select(models.Project).where(models.Project.id == deployment.project_id, models.Project.user_id == current_user.id))
    if not project_result.scalars().first():
        raise HTTPException(status_code=403, detail="Not authorized to view this deployment")
        
    return deployment

@router.get("/{deployment_id}/logs", response_model=schemas.DeploymentLogResponse)
async def get_deployment_logs(deployment_id: UUID, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """Get just the logs for a specific deployment."""
    result = await db.execute(select(models.Deployment).where(models.Deployment.id == deployment_id))
    deployment = result.scalars().first()
    
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
        
    # Security check
    project_result = await db.execute(select(models.Project).where(models.Project.id == deployment.project_id, models.Project.user_id == current_user.id))
    if not project_result.scalars().first():
        raise HTTPException(status_code=403, detail="Not authorized to view this deployment")
        
    return {"logs": deployment.logs}

import asyncio
from fastapi.responses import StreamingResponse

@router.get("/{deployment_id}/stream")
async def stream_deployment_logs(deployment_id: UUID, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(auth.get_current_user_ws)):
    """Stream deployment logs in real-time using Server-Sent Events (SSE)."""
    # Verify access
    result = await db.execute(select(models.Deployment).where(models.Deployment.id == deployment_id))
    deployment = result.scalars().first()
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
        
    project_result = await db.execute(select(models.Project).where(models.Project.id == deployment.project_id, models.Project.user_id == current_user.id))
    if not project_result.scalars().first():
        raise HTTPException(status_code=403, detail="Not authorized to view this deployment")
        
    async def log_generator():
        last_log_length = 0
        while True:
            # Re-fetch deployment
            await db.refresh(deployment)
            current_logs = deployment.logs or ""
            
            # Yield any new logs
            if len(current_logs) > last_log_length:
                yield f"data: {json.dumps({'logs': current_logs, 'status': deployment.status})}\n\n"
                last_log_length = len(current_logs)
            
            if deployment.status in ["success", "failed"]:
                # One last check just in case, though the above if statement caught it
                break
                
            await asyncio.sleep(1)
            
    return StreamingResponse(log_generator(), media_type="text/event-stream")
