from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash
from app.db.session import get_db
from app.models.user import User
from app.schemas.token import Token
from app.services.wechat_mini import WechatMiniService

router = APIRouter()


@router.post("/login", response_model=Token)
async def wechat_mini_login(
    *,
    db: AsyncSession = Depends(get_db),
    code: str,
) -> Any:
    """
    微信小程序登录
    """
    wechat_service = WechatMiniService(
        appid=settings.WECHAT_MINI_APPID,
        secret=settings.WECHAT_MINI_SECRET,
    )
    
    try:
        # 获取微信用户信息
        wx_result = await wechat_service.code2session(code)
        
        # 检查是否有openid
        if "openid" not in wx_result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="微信登录失败，无法获取openid",
            )
        
        openid = wx_result["openid"]
        unionid = wx_result.get("unionid")
        
        # 检查用户是否已存在
        user = await User.get_by_openid(db, openid=openid)
        
        # 如果用户不存在，创建新用户
        if not user:
            # 生成临时用户名
            temp_username = f"wx_{openid[-8:]}"
            temp_password = f"{openid}_{unionid}" if unionid else openid
            
            user = User(
                username=temp_username,
                hashed_password=get_password_hash(temp_password),
                openid=openid,
                unionid=unionid,
                is_active=True,
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        
        # 创建访问令牌
        access_token = create_access_token(subject=str(user.id))
        
        return {"access_token": access_token, "token_type": "bearer"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"微信登录失败: {str(e)}",
        )


@router.post("/phone", response_model=Dict[str, str])
async def wechat_mini_get_phone(
    *,
    db: AsyncSession = Depends(get_db),
    code: str,
) -> Any:
    """
    获取微信小程序用户手机号
    """
    wechat_service = WechatMiniService(
        appid=settings.WECHAT_MINI_APPID,
        secret=settings.WECHAT_MINI_SECRET,
    )
    
    try:
        # 获取微信用户手机号
        result = await wechat_service.get_phone_number(code)
        
        return {"phone": result.get("phone_info", {}).get("phoneNumber", "")}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"获取手机号失败: {str(e)}",
        ) 