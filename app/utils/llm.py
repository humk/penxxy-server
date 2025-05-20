from typing import Dict, Any, List, Optional, Union
import json
import openai
import os
import httpx

from app.core.config import settings


class LLMTool:
    """
    LLM工具类，封装OpenAI API调用
    """
    
    def __init__(self):
        """
        初始化LLM工具
        """
        self.api_key = settings.OPENAI_API_KEY
        self.base_url = settings.OPENAI_API_BASE if settings.OPENAI_API_BASE else None
        self.http_proxy = settings.OPENAI_HTTP_PROXY
    
    async def chat_completion(
        self, 
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        调用OpenAI Chat Completion API
        
        Args:
            messages: 消息列表，格式为[{"role": "user", "content": "Hello"}]
            model: 使用的模型，默认使用配置中的模型
            temperature: 温度参数，控制随机性
            max_tokens: 最大生成令牌数
            tools: 工具定义
            tool_choice: 工具选择
            
        Returns:
            API返回的结果
        """
        try:
            # 创建代理配置
            proxies = None
            if self.http_proxy:
                proxies = self.http_proxy
                print(f"使用OpenAI API代理: {self.http_proxy}")
            
            # 创建httpx客户端与超时设置
            timeout = httpx.Timeout(360.0, connect=360.0)
            http_client = httpx.Client(
                proxy=proxies,
                timeout=timeout
            )
            
            # 创建OpenAI客户端
            client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                http_client=http_client
            )
            
            response = client.chat.completions.create(
                model=model or settings.OPENAI_MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                tools=tools,
                tool_choice=tool_choice,
            )
            return response
        except Exception as e:
            # 记录错误并返回一个简单的错误响应
            print(f"OpenAI API调用失败: {str(e)}")
            return {
                "error": True,
                "message": f"OpenAI API调用失败: {str(e)}"
            }
    
    async def extract_json_from_response(
        self, 
        response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        从LLM响应中提取JSON数据
        
        Args:
            response: LLM响应
            
        Returns:
            提取的JSON数据，如果提取失败则返回空字典
        """
        try:
            if "error" in response and response["error"]:
                return {}
            
            content = response.choices[0].message.content
            
            # 尝试直接解析JSON
            try:
                return json.loads(content)
            except:
                pass
            
            # 如果直接解析失败，尝试提取JSON部分
            if "```json" in content and "```" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
                return json.loads(json_str)
            
            # 尝试找到 { 和 } 包裹的内容
            if "{" in content and "}" in content:
                start = content.find("{")
                end = content.rfind("}") + 1
                json_str = content[start:end]
                return json.loads(json_str)
            
            return {}
        except Exception as e:
            print(f"从响应中提取JSON失败: {str(e)}")
            return {} 