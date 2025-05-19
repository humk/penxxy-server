from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    """
    访问令牌模型
    """
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """
    令牌载荷模型
    """
    sub: Optional[str] = None
    exp: Optional[int] = None 