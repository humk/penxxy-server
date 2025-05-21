from typing import Dict, List, Type

from app.agents.base import BaseAgent
from app.agents.paper_qa.paper_qa_agent import PaperQAAgent


class AgentFactory:
    """
    Agent工厂类，管理所有可用的Agent
    """
    
    def __init__(self):
        """
        初始化Agent工厂，注册所有可用的Agent
        """
        self._agent_classes: Dict[str, Type[BaseAgent]] = {}
        self._register_all_agents()
    
    def _register_all_agents(self):
        """
        注册所有可用的Agent
        """
        # 注册论文问答Agent
        self.register_agent("paper_qa", PaperQAAgent)
        
        # 未来可以在这里注册更多Agent
        # self.register_agent("general_qa", GeneralQAAgent)
        # self.register_agent("code_assistant", CodeAssistantAgent)
        # 等等
    
    def register_agent(self, agent_id: str, agent_class: Type[BaseAgent]):
        """
        注册一个Agent
        
        Args:
            agent_id: Agent的唯一标识
            agent_class: Agent类
        """
        self._agent_classes[agent_id] = agent_class
    
    def create_agent(self, agent_id: str) -> BaseAgent:
        """
        创建一个Agent实例
        
        Args:
            agent_id: Agent的唯一标识
            
        Returns:
            创建的Agent实例
            
        Raises:
            ValueError: 当指定的Agent不存在时
        """
        if agent_id not in self._agent_classes:
            raise ValueError(f"Agent {agent_id} not found")
        
        return self._agent_classes[agent_id]()
    
    def create_all_agents(self) -> List[BaseAgent]:
        """
        创建所有已注册的Agent的实例
        
        Returns:
            所有Agent实例的列表
        """
        return [agent_class() for agent_class in self._agent_classes.values()]
    
    def get_available_agents(self) -> List[str]:
        """
        获取所有可用的Agent的ID
        
        Returns:
            所有可用Agent的ID列表
        """
        return list(self._agent_classes.keys()) 