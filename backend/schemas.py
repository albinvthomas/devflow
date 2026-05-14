from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: UUID
    github_token: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class ProjectBase(BaseModel):
    repo_url: str
    repo_name: str
    tech_stack: Optional[Dict[str, Any]] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: UUID
    user_id: UUID
    status: str
    latest_deployment_status: Optional[str] = None
    generated_configs: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class DeploymentBase(BaseModel):
    project_id: UUID
    logs: Optional[str] = None
    status: str

class DeploymentResponse(DeploymentBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class RepoResponse(BaseModel):
    name: str
    full_name: str
    language: Optional[str] = None
    description: Optional[str] = None
    html_url: str

class ProjectCreateRequest(BaseModel):
    repo_full_name: str

class DevOpsConfigsResponse(BaseModel):
    dockerfile: str
    docker_compose: str
    github_actions: str
    explanation: str

class DeploymentLogResponse(BaseModel):
    logs: Optional[str] = None

class GitHubCode(BaseModel):
    code: str
