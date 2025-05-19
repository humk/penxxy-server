from typing import Any, Dict
import hashlib

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.services.wechat_mp import WechatMPService

router = APIRouter()


@router.get("/callback", response_class=PlainTextResponse)
async def verify_mp_callback(
    signature: str,
    timestamp: str,
    nonce: str,
    echostr: str,
) -> Any:
    """
    验证微信公众号服务器配置
    """
    token = settings.WECHAT_MP_TOKEN
    temp_list = sorted([token, timestamp, nonce])
    temp_str = "".join(temp_list)
    hash_str = hashlib.sha1(temp_str.encode("utf-8")).hexdigest()
    
    if hash_str == signature:
        return echostr
    
    return "验证失败"


@router.post("/send_custom_message", response_model=Dict[str, Any])
async def send_custom_message(
    *,
    db: AsyncSession = Depends(get_db),
    openid: str,
    message_type: str = "text",
    content: str,
) -> Any:
    """
    发送客服消息
    """
    wechat_service = WechatMPService(
        appid=settings.WECHAT_MP_APPID,
        secret=settings.WECHAT_MP_SECRET,
        token=settings.WECHAT_MP_TOKEN,
        aes_key=settings.WECHAT_MP_AES_KEY,
    )
    
    try:
        result = await wechat_service.send_custom_message(openid, message_type, content)
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"发送客服消息失败: {str(e)}",
        ) 