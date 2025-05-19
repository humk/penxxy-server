from typing import List, Optional, Union, Dict, Any
from pydantic import AnyHttpUrl, EmailStr, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    应用程序设置
    """
    # 应用程序基本信息
    APP_ENV: str = "development"
    API_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "微信小程序与公众号后台服务"
    PROJECT_DESCRIPTION: str = "为微信小程序与公众号提供后台服务接口"
    PROJECT_VERSION: str = "0.1.0"
    
    # 调试模式
    DEBUG: bool = True
    
    # 安全设置 - 为开发环境提供默认值
    SECRET_KEY: str = "dev_secret_key_please_change_in_production"
    
    # CORS设置
    BACKEND_CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        if isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # 数据库设置 - 开发环境使用SQLite
    DATABASE_URL: str = "sqlite:///./dev.db"
    
    # JWT设置 - 为开发环境提供默认值
    JWT_SECRET_KEY: str = "dev_jwt_secret_key_please_change_in_production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 微信小程序设置 - 开发环境使用测试值
    WECHAT_MINI_APPID: Optional[str] = "wx_mini_appid"
    WECHAT_MINI_SECRET: Optional[str] = "wx_mini_secret"
    
    # 微信公众号设置 - 开发环境使用测试值
    WECHAT_MP_APPID: Optional[str] = "wx_mp_appid"
    WECHAT_MP_SECRET: Optional[str] = "wx_mp_secret"
    WECHAT_MP_TOKEN: Optional[str] = "wx_mp_token"
    WECHAT_MP_AES_KEY: Optional[str] = None
    
    # 微信支付设置 - 开发环境使用测试值
    WECHAT_PAY_MCHID: Optional[str] = "wx_pay_mchid"
    WECHAT_PAY_KEY: Optional[str] = "wx_pay_key"
    WECHAT_PAY_CERT_PATH: Optional[str] = None
    WECHAT_PAY_KEY_PATH: Optional[str] = None
    
    model_config = {
        "case_sensitive": True,
        "env_file": ".env",
        "extra": "ignore",  # 允许额外的字段
    }


settings = Settings() 