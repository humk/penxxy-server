from typing import List, Optional, Union, Dict, Any
import os
from pydantic import AnyHttpUrl, EmailStr, field_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# 获取项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 优先尝试加载.env文件
env_path = os.path.join(BASE_DIR, ".env")
if os.path.exists(env_path):
    print(f"加载环境变量文件: {env_path}")
    load_dotenv(env_path)
else:
    print(f"环境变量文件不存在: {env_path}")


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
        "env_file": env_path,  # 使用绝对路径
        "env_file_encoding": "utf-8",
        "extra": "ignore",  # 允许额外的字段
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 打印调试信息，帮助排查环境变量问题
        if self.APP_ENV == "development":
            print(f"应用配置: APP_ENV={self.APP_ENV}, DEBUG={self.DEBUG}")
            print(f"数据库: {self.DATABASE_URL}")
            print(f"微信小程序: APPID={self.WECHAT_MINI_APPID}")
            print(f"环境变量文件: {env_path}")


# 创建设置实例
settings = Settings()

# 打印当前环境变量，帮助调试
if os.environ.get("APP_ENV") == "development" or settings.DEBUG:
    print("系统环境变量:")
    for key in ["APP_ENV", "DEBUG", "SECRET_KEY", "DATABASE_URL", "WECHAT_MINI_APPID"]:
        print(f"{key}={os.environ.get(key, '未设置')}") 