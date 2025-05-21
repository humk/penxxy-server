from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, wechat_mini, wechat_mp, wechat_pay, admin

# 创建APIRouter实例
api_router = APIRouter()

# 注册各个模块的路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户"])
api_router.include_router(wechat_mini.router, prefix="/wechat/mini", tags=["微信小程序"])
api_router.include_router(wechat_mp.router, prefix="/wechat/mp", tags=["微信公众号"])
api_router.include_router(wechat_pay.router, prefix="/wechat/pay", tags=["微信支付"])
api_router.include_router(admin.router, prefix="/admin", tags=["管理员"]) 