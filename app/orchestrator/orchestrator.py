from typing import Dict, Any, List, Optional
import asyncio

from app.agents.base.base_agent import BaseAgent
from app.agents.agent_factory import AgentFactory
from app.utils.llm import LLMTool


class Orchestrator:
    """
    多Agent系统的协调器，负责选择合适的Agent处理查询
    """
    
    def __init__(self):
        """
        初始化协调器
        """
        self.agent_factory = AgentFactory()
        self.llm_tool = LLMTool()
        self.agents = self.agent_factory.create_all_agents()
    
    async def process_query(
        self, 
        query: str, 
        context: Optional[Dict[str, Any]] = None,
        agent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        处理用户查询
        
        Args:
            query: 用户查询
            context: 上下文信息
            agent_id: 指定使用的Agent ID，如果为None则自动选择
            
        Returns:
            处理结果
        """
        if context is None:
            context = {}
        
        # 如果指定了Agent，直接使用
        if agent_id:
            try:
                agent = self.agent_factory.create_agent(agent_id)
                result = await agent.process(query, context)
                return {
                    "agent_id": agent_id,
                    "agent_name": agent.name,
                    "response": result.get("answer", "无法处理您的请求"),
                    "metadata": result
                }
            except ValueError:
                pass  # 如果指定的Agent不存在，回退到自动选择
        
        # 自动选择最合适的Agent
        agent_scores = [(agent, agent.can_handle(query, context)) for agent in self.agents]
        agent_scores.sort(key=lambda x: x[1], reverse=True)
        
        if not agent_scores:
            return {
                "agent_id": None,
                "agent_name": None,
                "response": "我无法处理您的请求，因为没有合适的Agent可用。",
                "metadata": {}
            }
        
        # 选择分数最高的Agent处理
        best_agent, score = agent_scores[0]
        
        # 处理查询
        result = await best_agent.process(query, context)
        
        return {
            "agent_id": best_agent.name,
            "agent_name": best_agent.description,
            "response": result.get("answer", "无法处理您的请求"),
            "metadata": result
        }


# 创建单例实例
orchestrator = Orchestrator() 