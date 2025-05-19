from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.router import api_router
from app.core.events import startup_event_handler, shutdown_event_handler


def create_application() -> FastAPI:
    """
    创建FastAPI应用实例
    """
    application = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.PROJECT_VERSION,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json" if settings.DEBUG else None,
    )

    # 设置CORS
    if settings.BACKEND_CORS_ORIGINS:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # 添加事件处理
    application.add_event_handler("startup", startup_event_handler(application))
    application.add_event_handler("shutdown", shutdown_event_handler(application))

    # 添加路由
    application.include_router(api_router, prefix=settings.API_PREFIX)

    @application.get("/")
    async def root():
        return {"message": "微信小程序和公众号后台服务"}

    @application.get("/health")
    async def health_check():
        return {"status": "ok"}

    return application


app = create_application() 