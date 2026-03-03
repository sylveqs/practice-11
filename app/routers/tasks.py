from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import schemas, models
from app.database import get_db
from app.dependencies import get_current_user, get_project_or_404, get_task_or_404

router = APIRouter(tags=["Tasks"])


@router.get(
    "/projects/{project_id}/tasks",
    response_model=List[schemas.TaskResponse],
    responses={
        403: {"model": schemas.ErrorResponse, "description": "Not enough permissions"},
        404: {"model": schemas.ErrorResponse, "description": "Project not found"}
    }
)
def get_project_tasks(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get all tasks in a project.
    
    Returns list of tasks with assignee usernames.
    User must be the owner of the project.
    """
    # Check if project exists and user owns it
    project = get_project_or_404(project_id, db, current_user)
    
    tasks = []
    for task in project.tasks:
        task_response = schemas.TaskResponse.model_validate(task)
        task_response.assignee_username = task.assignee.username if task.assignee else None
        tasks.append(task_response)
    
    return tasks


@router.post(
    "/projects/{project_id}/tasks",
    response_model=schemas.TaskResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": schemas.ErrorResponse, "description": "Invalid data or assignee not found"},
        403: {"model": schemas.ErrorResponse, "description": "Not enough permissions"},
        404: {"model": schemas.ErrorResponse, "description": "Project not found"}
    }
)
def create_task(
    project_id: int,
    task_data: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Create a new task in a project.
    
    - **title**: required
    - **description**: optional
    - **assignee_id**: optional (must exist in database)
    - **status**: optional (defaults to "todo")
    
    User must be the owner of the project.
    """
    # Check if project exists and user owns it
    project = get_project_or_404(project_id, db, current_user)
    
    # Validate assignee if provided
    if task_data.assignee_id:
        assignee = db.query(models.User).filter(
            models.User.id == task_data.assignee_id
        ).first()
        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Assignee with id {task_data.assignee_id} not found"
            )
    
    # Create task
    db_task = models.Task(
        title=task_data.title,
        description=task_data.description,
        status=task_data.status or "todo",
        project_id=project_id,
        assignee_id=task_data.assignee_id
    )
    
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    # Prepare response
    response = schemas.TaskResponse.model_validate(db_task)
    response.assignee_username = db_task.assignee.username if db_task.assignee else None
    
    return response


@router.patch(
    "/tasks/{task_id}",
    response_model=schemas.TaskResponse,
    responses={
        403: {"model": schemas.ErrorResponse, "description": "Not enough permissions"},
        404: {"model": schemas.ErrorResponse, "description": "Task not found"}
    }
)
def update_task(
    task_id: int,
    task_update: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Update a task (partial update).
    
    You can update any of these fields:
    - **title**
    - **description**
    - **status** (todo/in_progress/done)
    - **assignee_id**
    
    User must be the owner of the project containing this task.
    """
    # Check if task exists and user owns the project
    task = get_task_or_404(task_id, db, current_user)
    
    # Validate assignee if provided
    if task_update.assignee_id is not None:
        if task_update.assignee_id:
            assignee = db.query(models.User).filter(
                models.User.id == task_update.assignee_id
            ).first()
            if not assignee:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Assignee with id {task_update.assignee_id} not found"
                )
    
    # Update fields
    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    
    db.commit()
    db.refresh(task)
    
    # Prepare response
    response = schemas.TaskResponse.model_validate(task)
    response.assignee_username = task.assignee.username if task.assignee else None
    
    return response


@router.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        403: {"model": schemas.ErrorResponse, "description": "Not enough permissions"},
        404: {"model": schemas.ErrorResponse, "description": "Task not found"}
    }
)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Delete a task.
    
    User must be the owner of the project containing this task.
    """
    # Check if task exists and user owns the project
    task = get_task_or_404(task_id, db, current_user)
    
    db.delete(task)
    db.commit()
    
    return None