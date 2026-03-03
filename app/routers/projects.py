from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import schemas, models
from app.database import get_db
from app.dependencies import get_current_user, get_project_or_404

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("/", response_model=List[schemas.ProjectResponse])
def get_projects(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get all projects owned by current user.
    
    Returns list of projects with task_count.
    Sorted by created_at (newest first).
    """
    projects = db.query(models.Project).filter(
        models.Project.owner_id == current_user.id
    ).order_by(models.Project.created_at.desc()).all()
    
    # Add task_count to response
    result = []
    for project in projects:
        project_data = schemas.ProjectResponse.model_validate(project)
        project_data.task_count = project.task_count
        result.append(project_data)
    
    return result


@router.post(
    "/",
    response_model=schemas.ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": schemas.ErrorResponse}}
)
def create_project(
    project_data: schemas.ProjectCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Create a new project.
    
    - **name**: required
    - **description**: optional
    """
    if not project_data.name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project name is required"
        )
    
    db_project = models.Project(
        name=project_data.name,
        description=project_data.description,
        owner_id=current_user.id
    )
    
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    return db_project


@router.get(
    "/{project_id}",
    response_model=schemas.ProjectDetailResponse,
    responses={
        403: {"model": schemas.ErrorResponse, "description": "Not enough permissions"},
        404: {"model": schemas.ErrorResponse, "description": "Project not found"}
    }
)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get detailed information about a project.
    
    Returns project details with all tasks inside.
    User must be the owner of the project.
    """
    project = get_project_or_404(project_id, db, current_user)
    
    # Prepare tasks with assignee usernames
    tasks = []
    for task in project.tasks:
        task_response = schemas.TaskResponse.model_validate(task)
        task_response.assignee_username = task.assignee.username if task.assignee else None
        tasks.append(task_response)
    
    # Create response with tasks
    response = schemas.ProjectDetailResponse.model_validate(project)
    response.tasks = tasks
    
    return response