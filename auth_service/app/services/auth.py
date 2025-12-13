from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.schemas.token import TokenPair
from app.services.security import SecurityService


class AuthService:
    """Сервис авторизации и управления пользователями"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Получить пользователя по email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Получить пользователя по username"""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Получить пользователя по ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def create_user(self, user_data: UserCreate) -> User:
        """Регистрация нового пользователя"""
        if self.get_user_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        if self.get_user_by_username(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        hashed_password = SecurityService.hash_password(user_data.password)
        user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Аутентификация пользователя"""
        user = self.get_user_by_email(email)
        if not user:
            return None
        if not SecurityService.verify_password(password, user.hashed_password):
            return None
        return user
    
    def create_tokens(self, user: User) -> TokenPair:
        """Создание пары токенов (access + refresh)"""
        token_data = {"sub": str(user.id), "email": user.email}
        
        access_token = SecurityService.create_access_token(token_data)
        refresh_token = SecurityService.create_refresh_token(token_data)
        
        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token
        )
    
    def refresh_tokens(self, refresh_token: str) -> TokenPair:
        """Обновление токенов по refresh токену"""
        if not SecurityService.verify_token_type(refresh_token, "refresh"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        token_data = SecurityService.decode_token(refresh_token)
        if not token_data or not token_data.user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user = self.get_user_by_id(token_data.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is deactivated"
            )
        
        return self.create_tokens(user)
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """Обновление данных пользователя"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if user_data.email and user_data.email != user.email:
            if self.get_user_by_email(user_data.email):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            user.email = user_data.email
        
        if user_data.username and user_data.username != user.username:
            if self.get_user_by_username(user_data.username):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
            user.username = user_data.username
        
        if user_data.password:
            user.hashed_password = SecurityService.hash_password(user_data.password)
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def delete_user(self, user_id: int) -> bool:
        """Удаление пользователя"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        self.db.delete(user)
        self.db.commit()
        return True
    
    def deactivate_user(self, user_id: int) -> User:
        """Деактивация пользователя"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.is_active = False
        self.db.commit()
        self.db.refresh(user)
        
        return user

