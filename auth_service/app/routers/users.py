from typing import List
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.user import UserResponse, UserUpdate, BalanceOperation, BalanceResponse
from app.services.auth import AuthService
from app.services.security import get_current_user, get_current_active_superuser
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=List[UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """
    Получение списка всех пользователей (только для суперпользователей)
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получение пользователя по ID
    
    Обычные пользователи могут видеть только свой профиль,
    суперпользователи - любой
    """
    if current_user.id != user_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    auth_service = AuthService(db)
    user = auth_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Обновление данных пользователя
    
    Пользователи могут обновлять только свои данные,
    суперпользователи - любые
    """
    if current_user.id != user_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    auth_service = AuthService(db)
    return auth_service.update_user(user_id, user_data)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """
    Удаление пользователя (только для суперпользователей)
    """
    auth_service = AuthService(db)
    auth_service.delete_user(user_id)
    return None


@router.post("/balance/deposit", response_model=BalanceResponse)
async def deposit_balance(
    operation: BalanceOperation,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Пополнение баланса пользователя
    """
    new_balance = Decimal(str(current_user.balance)) + operation.amount
    current_user.balance = new_balance
    db.commit()
    db.refresh(current_user)
    
    return BalanceResponse(
        balance=current_user.balance,
        message=f"Баланс успешно пополнен на {operation.amount} монет"
    )


@router.post("/balance/withdraw", response_model=BalanceResponse)
async def withdraw_balance(
    operation: BalanceOperation,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Вывод средств с баланса пользователя
    """
    current_balance = Decimal(str(current_user.balance))
    
    if current_balance < operation.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Недостаточно средств. Текущий баланс: {current_balance}"
        )
    
    new_balance = current_balance - operation.amount
    current_user.balance = new_balance
    db.commit()
    db.refresh(current_user)
    
    return BalanceResponse(
        balance=current_user.balance,
        message=f"Успешно выведено {operation.amount} монет"
    )


@router.get("/balance", response_model=BalanceResponse)
async def get_balance(
    current_user: User = Depends(get_current_user)
):
    """
    Получение текущего баланса пользователя
    """
    return BalanceResponse(
        balance=current_user.balance,
        message="Текущий баланс"
    )
#
