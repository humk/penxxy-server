from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete

from app.api.deps import get_current_active_user, get_current_superuser
from app.core.security import get_password_hash
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import User as UserSchema, UserCreate, UserUpdate

router = APIRouter()


@router.get("/me", response_model=UserSchema)
async def read_user_me(current_user: User = Depends(get_current_active_user)) -> Any:
    """
    获取当前用户信息
    """
    return current_user


@router.put("/me", response_model=UserSchema)
async def update_user_me(
    *,
    db: AsyncSession = Depends(get_db),
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    更新当前用户信息
    """
    # 构建更新数据
    update_data = user_in.dict(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = get_password_hash(update_data["password"])
        del update_data["password"]
    
    # 更新用户
    await db.execute(
        update(User).where(User.id == current_user.id).values(**update_data)
    )
    await db.commit()
    
    # 返回更新后的用户
    return await User.get_by_id(db, id=current_user.id)


@router.get("", response_model=List[UserSchema])
async def read_users(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    获取所有用户列表
    """
    result = await db.execute(select(User).offset(skip).limit(limit))
    users = result.scalars().all()
    return users


@router.post("", response_model=UserSchema)
async def create_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_in: UserCreate,
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    创建新用户
    """
    # 检查用户名是否已存在
    user = await User.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在",
        )
    
    # 检查邮箱是否已存在
    if user_in.email:
        user = await User.get_by_email(db, email=user_in.email)
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已存在",
            )
    
    # 创建用户
    user = User(
        username=user_in.username,
        email=user_in.email,
        mobile=user_in.mobile,
        hashed_password=get_password_hash(user_in.password),
        is_active=user_in.is_active,
        is_superuser=user_in.is_superuser,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return user


@router.get("/{user_id}", response_model=UserSchema)
async def read_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取指定用户信息
    """
    # 非管理员只能获取自己的信息
    if not current_user.is_superuser and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足",
        )
    
    user = await User.get_by_id(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )
    
    return user


@router.put("/{user_id}", response_model=UserSchema)
async def update_user(
    *,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    user_in: UserUpdate,
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    更新指定用户信息
    """
    user = await User.get_by_id(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )
    
    # 构建更新数据
    update_data = user_in.dict(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = get_password_hash(update_data["password"])
        del update_data["password"]
    
    # 更新用户
    await db.execute(
        update(User).where(User.id == user_id).values(**update_data)
    )
    await db.commit()
    
    # 返回更新后的用户
    return await User.get_by_id(db, id=user_id)


@router.delete("/{user_id}", response_model=UserSchema)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    删除指定用户
    """
    user = await User.get_by_id(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )
    
    # 删除用户
    await db.execute(delete(User).where(User.id == user_id))
    await db.commit()
    
    return user 