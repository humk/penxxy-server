from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class BaseAgent(ABC):
    """
    所有Agent的基类，定义了Agent需要实现的接口
    """
    
    def __init__(self, name: str, description: str):
        """
        初始化Agent
        
        Args:
            name: Agent名称
            description: Agent描述
        """
        self.name = name
        self.description = description
    
    @abstractmethod
    async def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        处理用户查询
        
        Args:
            query: 用户查询字符串
            context: 额外的上下文信息
            
        Returns:
            包含处理结果的字典
        """
        pass
    
    def can_handle(self, query: str, context: Optional[Dict[str, Any]] = None) -> float:
        """
        判断该Agent是否适合处理该查询，返回一个0-1之间的分数
        默认实现返回0.5，子类应该覆盖这个方法提供更精确的判断
        
        Args:
            query: 用户查询字符串
            context: 额外的上下文信息
            
        Returns:
            该Agent处理该查询的适合度分数(0-1)
        """
        return 0.5
    
    def get_info(self) -> Dict[str, Any]:
        """
        获取Agent的基本信息
        
        Returns:
            包含Agent信息的字典
        """
        return {
            "name": self.name,
            "description": self.description
        } 