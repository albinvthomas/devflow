from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import models
import schemas
import auth
from database import get_db
import github_service

router = APIRouter(
    prefix="/github",
    tags=["GitHub Integration"]
)

@router.get("/login")
async def github_login():
    """Redirect user to GitHub for OAuth authorization."""
    if not github_service.GITHUB_CLIENT_ID:
        raise HTTPException(status_code=500, detail="GitHub Client ID not configured.")
    url = f"https://github.com/login/oauth/authorize?client_id={github_service.GITHUB_CLIENT_ID}&scope=repo"
    return RedirectResponse(url=url)

@router.post("/callback")
async def github_callback(data: schemas.GitHubCode, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """Exchange the OAuth code for an access token and save it to the user profile."""
    try:
        access_token = await github_service.exchange_code_for_token(data.code)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error exchanging token: {str(e)}")
        
    if not access_token:
        raise HTTPException(status_code=400, detail="Failed to retrieve access token from GitHub")
        
    # Save token to user
    current_user.github_token = access_token
    db.add(current_user)
    await db.commit()
    
    return {"message": "GitHub account linked successfully!"}

@router.get("/repos", response_model=List[schemas.RepoResponse])
async def list_github_repos(current_user: models.User = Depends(auth.get_current_user)):
    """List all GitHub repositories for the authenticated user."""
    if not current_user.github_token:
        raise HTTPException(status_code=400, detail="GitHub account not linked. Please login to GitHub first.")
        
    try:
        repos_data = await github_service.get_user_repos(current_user.github_token)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching repositories: {str(e)}")
        
    # Filter out only the fields we need based on RepoResponse schema
    filtered_repos = []
    for repo in repos_data:
        # Note: Some users might have over 100 repos, pagination might be needed for production.
        filtered_repos.append({
            "name": repo.get("name"),
            "full_name": repo.get("full_name"),
            "language": repo.get("language"),
            "description": repo.get("description"),
            "html_url": repo.get("html_url")
        })
        
    return filtered_repos
