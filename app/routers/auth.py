from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas, models, auth
from app.database import get_db
from app.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register", 
    response_model=schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": schemas.ErrorResponse, "description": "Email or username already registered"}
    }
)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    - **email**: must be unique
    - **username**: must be unique
    - **password**: will be hashed before storing
    """
    # Check if email or username already exists
    existing_user = db.query(models.User).filter(
        (models.User.email == user_data.email) | 
        (models.User.username == user_data.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )
    
    # Create new user
    hashed_password = auth.get_password_hash(user_data.password)
    db_user = models.User(
        email=user_data.email,
        username=user_data.username,
        password_hash=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.post(
    "/login",
    response_model=schemas.Token,
    responses={
        401: {"model": schemas.ErrorResponse, "description": "Incorrect email or password"}
    }
)
def login(user_data: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    Login with email and password.
    
    Returns a JWT token that should be used in Authorization header for protected endpoints.
    """
    # Find user by email
    user = db.query(models.User).filter(models.User.email == user_data.email).first()
    
    if not user or not auth.verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = auth.create_access_token(data={"sub": str(user.id)})
    
    return schemas.Token(access_token=access_token)


@router.post("/logout", responses={200: {"description": "Successfully logged out"}})
def logout(current_user: models.User = Depends(get_current_user)):
    """
    Logout current user.
    
    JWT is stateless, so client should delete the token.
    """
    return {"detail": "Successfully logged out"}