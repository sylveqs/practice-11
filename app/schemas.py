from pydantic import BaseModel, EmailStr, ConfigDict, Field
from datetime import datetime
from typing import Optional, List

# User
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Auth Schemas 
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[int] = None


# Task Schemas
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(todo|in_progress|done)$")
    assignee_id: Optional[int] = None

class TaskCreate(TaskBase):
    title: str
    status: Optional[str] = "todo"

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(todo|in_progress|done)$")
    assignee_id: Optional[int] = None

class TaskResponse(TaskBase):
    id: int
    status: str
    project_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    assignee_username: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


# Project
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    task_count: int = 0
    
    model_config = ConfigDict(from_attributes=True)

class ProjectDetailResponse(ProjectBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    tasks: List[TaskResponse] = []
    
    model_config = ConfigDict(from_attributes=True)


#  Error 
class ErrorResponse(BaseModel):
    detail: str