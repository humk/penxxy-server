from typing import Any, Dict
import time
import uuid

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.services.wechat_pay import WechatPayService

router = APIRouter()


@router.post("/create-order", response_model=Dict[str, Any])
async def create_order(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    amount: int,
    description: str,
) -> Any:
    """
    创建微信支付订单
    """
    # 验证金额
    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="金额必须大于0",
        )
    
    # 创建微信支付服务
    wechat_pay_service = WechatPayService(
        appid=settings.WECHAT_MINI_APPID,
        mchid=settings.WECHAT_PAY_MCHID,
        key=settings.WECHAT_PAY_KEY,
        cert_path=settings.WECHAT_PAY_CERT_PATH,
        key_path=settings.WECHAT_PAY_KEY_PATH,
    )
    
    try:
        # 生成订单号
        out_trade_no = f"ORDER_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        # 创建支付订单
        result = await wechat_pay_service.create_jsapi_order(
            openid=current_user.openid,
            out_trade_no=out_trade_no,
            amount=amount,
            description=description,
        )
        
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"创建订单失败: {str(e)}",
        )


@router.post("/notify", response_model=Dict[str, str])
async def wechat_pay_notify(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    处理微信支付结果通知
    """
    wechat_pay_service = WechatPayService(
        appid=settings.WECHAT_MINI_APPID,
        mchid=settings.WECHAT_PAY_MCHID,
        key=settings.WECHAT_PAY_KEY,
        cert_path=settings.WECHAT_PAY_CERT_PATH,
        key_path=settings.WECHAT_PAY_KEY_PATH,
    )
    
    try:
        # 获取请求体
        body = await request.body()
        
        # 处理回调
        result = await wechat_pay_service.process_callback(body)
        
        # 处理订单逻辑
        if result["return_code"] == "SUCCESS":
            # TODO: 更新订单状态
            pass
        
        # 返回成功响应
        return {"return_code": "SUCCESS", "return_msg": "OK"}
    
    except Exception as e:
        # 记录错误但仍返回成功，避免微信反复推送
        return {"return_code": "SUCCESS", "return_msg": "OK"} 