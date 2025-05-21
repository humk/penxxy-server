from typing import List, Union, Optional
from pydantic import AnyHttpUrl, field_validator, Field, BaseModel
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """应用程序配置"""
    
    # 应用配置
    APP_ENV: str = os.getenv("APP_ENV", "development")
    PROJECT_NAME: str = "微信小程序和公众号后台服务"
    PROJECT_DESCRIPTION: str = "为微信小程序和公众号提供后台服务，包括用户管理、内容管理等"
    PROJECT_VERSION: str = "0.1.0"
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ('true', '1', 't')
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_secret_key_here")
    ADMIN_TOKEN: str = os.getenv("ADMIN_TOKEN", "admin_default_token")
    
    # 跨域设置
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            import json
            try:
                return json.loads(v)
            except:
                return []
        return []
    
    # 数据库配置
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    
    # JWT设置
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your_jwt_secret")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # 微信小程序配置
    WECHAT_MINI_APPID: str = os.getenv("WECHAT_MINI_APPID", "")
    WECHAT_MINI_SECRET: str = os.getenv("WECHAT_MINI_SECRET", "")
    
    # 微信公众号配置
    WECHAT_MP_APPID: str = os.getenv("WECHAT_MP_APPID", "")
    WECHAT_MP_SECRET: str = os.getenv("WECHAT_MP_SECRET", "")
    WECHAT_MP_TOKEN: str = os.getenv("WECHAT_MP_TOKEN", "")
    WECHAT_MP_AES_KEY: str = os.getenv("WECHAT_MP_AES_KEY", "")
    
    # 微信支付配置
    WECHAT_PAY_MCHID: str = os.getenv("WECHAT_PAY_MCHID", "")
    WECHAT_PAY_KEY: str = os.getenv("WECHAT_PAY_KEY", "")
    WECHAT_PAY_CERT_PATH: str = os.getenv("WECHAT_PAY_CERT_PATH", "")
    WECHAT_PAY_KEY_PATH: str = os.getenv("WECHAT_PAY_KEY_PATH", "")
    
    # LLM配置
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    OPENAI_API_BASE: Optional[str] = os.getenv("OPENAI_API_BASE")
    OPENAI_HTTP_PROXY: Optional[str] = os.getenv("OPENAI_HTTP_PROXY")
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        # 允许额外的属性
        extra = "ignore"


settings = Settings() 