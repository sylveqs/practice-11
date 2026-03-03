from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.routers import auth, projects, tasks
from app.database import engine, Base

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Task Manager API",
    description="""
    Task Manager API позволяет пользователям создавать проекты и управлять задачами внутри них.
    
    ## Функциональность
    
    * **Аутентификация** - регистрация, вход, выход
    * **Проекты** - создание, просмотр, детальная информация с задачами
    * **Задачи** - создание, просмотр, обновление, удаление
    
    ## Аутентификация
    
    Для доступа к защищенным эндпоинтам необходимо:
    1. Получить JWT токен через `/auth/login`
    2. Использовать токен в заголовке: `Authorization: Bearer <token>`
    """,
    version="1.0.0",
    contact={
        "name": "Task Manager Support",
        "email": "support@taskmanager.com",
    },
    license_info={
        "name": "MIT",
    }
)

# Include routers
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(tasks.router)


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc.errors())}
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle database errors"""
    logger.error(f"Database error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors"""
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Task Manager API",
        "version": "1.0.0",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        },
        "endpoints": {
            "auth": {
                "register": "POST /auth/register",
                "login": "POST /auth/login",
                "logout": "POST /auth/logout"
            },
            "projects": {
                "list": "GET /projects/",
                "create": "POST /projects/",
                "detail": "GET /projects/{project_id}"
            },
            "tasks": {
                "list": "GET /projects/{project_id}/tasks",
                "create": "POST /projects/{project_id}/tasks",
                "update": "PATCH /tasks/{task_id}",
                "delete": "DELETE /tasks/{task_id}"
            }
        }
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "database": "connected"}