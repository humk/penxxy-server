from typing import Any
from sqlalchemy.ext.declarative import as_declarative, declared_attr
import re


@as_declarative()
class Base:
    """
    SQLAlchemy声明式基类
    """
    id: Any
    
    # 生成表名
    @declared_attr
    def __tablename__(cls) -> str:
        # 将驼峰式类名转换为下划线分隔的表名
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    # 通用的字符串表示
    def __repr__(self) -> str:
        attrs = []
        for c in self.__table__.columns:
            try:
                attrs.append(f"{c.name}={getattr(self, c.name)}")
            except Exception:
                attrs.append(f"{c.name}=None")
        return f"<{self.__class__.__name__} {', '.join(attrs)}>"
    
    # 通用的字典转换
    def to_dict(self) -> dict:
        result = {}
        for c in self.__table__.columns:
            result[c.name] = getattr(self, c.name)
        return result 