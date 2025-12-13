from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.user import UserCreate, UserResponse, UserLogin
from app.schemas.token import Token, TokenPair
from app.services.auth import AuthService
from app.services.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Регистрация нового пользователя
    
    - **email**: уникальный email пользователя
    - **username**: уникальное имя пользователя (3-100 символов)
    - **password**: пароль (минимум 6 символов)
    """
    auth_service = AuthService(db)
    user = auth_service.create_user(user_data)
    return user


@router.post("/login", response_model=TokenPair)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    Авторизация пользователя
    
    Возвращает пару токенов (access + refresh)
    """
    auth_service = AuthService(db)
    user = auth_service.authenticate_user(user_data.email, user_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
    
    return auth_service.create_tokens(user)


@router.post("/login/form", response_model=TokenPair)
async def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Авторизация через форму (для OAuth2 совместимости)
    
    Используется для интеграции с Swagger UI
    """
    auth_service = AuthService(db)
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
    
    return auth_service.create_tokens(user)


@router.post("/refresh", response_model=TokenPair)
async def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """
    Обновление токенов по refresh токену
    
    - **refresh_token**: действующий refresh токен
    """
    auth_service = AuthService(db)
    return auth_service.refresh_tokens(refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Получение информации о текущем авторизованном пользователе
    """
    return current_user


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    Выход из системы
    
    Примечание: для полноценной реализации logout нужен blacklist токенов
    """
    return {"message": "Successfully logged out"}

