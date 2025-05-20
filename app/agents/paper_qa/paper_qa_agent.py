import logging
from typing import Dict, Any, List, Optional
import re
import json

from app.agents.base.base_agent import BaseAgent
from app.utils.llm import LLMTool
from app.utils.arxiv_tool import ArxivTool


class PaperQAAgent(BaseAgent):
    """
    论文问答Agent，用于回答与论文相关的问题
    """

    def __init__(self):
        """
        初始化论文问答Agent
        """
        super().__init__(
            name="paper_qa",
            description="论文问答专家，可以回答学术论文相关问题，搜索最新论文，并提供论文解读"
        )
        self.llm_tool = LLMTool()
        self.arxiv_tool = ArxivTool()

    def can_handle(self, query: str, context: Optional[Dict[str, Any]] = None) -> float:
        """
        判断是否适合处理该查询
        
        Args:
            query: 用户查询
            context: 上下文信息
            
        Returns:
            适合度分数
        """
        # 定义与学术和论文相关的关键词
        keywords = [
            "论文", "研究", "学术", "paper", "research", "study", "arxiv",
            "发表", "文献", "引用", "引文", "journal", "conference", "学者",
            "实验", "方法", "结果", "结论", "摘要", "abstract", "introduction",
            "方法学", "methodology", "数据集", "dataset", "模型", "算法",
            "课题", "学科", "文章", "publication"
        ]

        # 匹配论文ID
        arxiv_id_pattern = r"(\d{4}\.\d{4,5}(v\d+)?)"
        if re.search(arxiv_id_pattern, query):
            return 0.9

        # 计算关键词匹配度
        query_lower = query.lower()
        match_count = sum(1 for keyword in keywords if keyword.lower() in query_lower)

        if match_count > 2:
            return 0.8
        elif match_count > 0:
            return 0.6

        return 0.3

    async def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        处理查询
        
        Args:
            query: 用户查询
            context: 上下文信息
            
        Returns:
            处理结果
        """
        # 定义LLM可用的工具
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_arxiv_papers",
                    "description": "搜索ArXiv上的学术论文",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "搜索关键词，用英文表示，如'large language model'"
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "最大返回结果数",
                                "default": 3
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_paper_by_id",
                    "description": "通过ArXiv ID获取特定论文",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "paper_id": {
                                "type": "string",
                                "description": "ArXiv论文ID，如'2201.08239'或'2201.08239v1'"
                            }
                        },
                        "required": ["paper_id"]
                    }
                }
            }
        ]
        
        # 设置系统提示词
        system_prompt = """你是一个专业的学术问答助手，擅长回答关于学术论文和研究的问题。你可以：
1. 搜索并推荐相关论文
2. 解读特定论文的内容
3. 总结研究领域的最新进展
4. 解释学术概念

你有权限使用两个工具：
- search_arxiv_papers：用于搜索学术论文
- get_paper_by_id：用于获取特定论文详情

当回答问题时，请遵循以下原则：
- 如果用户提到特定论文ID（如：2201.08239），使用get_paper_by_id工具查询
- 如果用户问的是某领域的研究或论文，使用search_arxiv_papers工具搜索
- 保持专业、准确和有帮助
- 主动使用工具获取信息，不要假装知道没有查询过的论文内容
- 针对中文问题，在工具查询时使用英文关键词，但回答用中文
- 不确定的内容要诚实说明

回答应该清晰、专业，如果引用论文，提供标题、作者和发表日期等信息。
"""

        # 创建用户消息
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]
        
        # 设置最大迭代次数
        max_iterations = 3
        current_iteration = 0
        
        # 处理可能的错误
        try:
            # 开始多轮工具调用循环
            while current_iteration < max_iterations:
                current_iteration += 1
                
                # 是否继续提供工具
                provide_tools = current_iteration < max_iterations
                
                # 调用模型
                response = await self.llm_tool.chat_completion(
                    messages=messages,
                    temperature=0.2,
                    tools=tools if provide_tools else None,
                )
                
                if isinstance(response, dict) and "error" in response and response["error"]:
                    logging.error(response.get('message', '未知错误'))
                    return {"answer": f"抱歉，在处理您的请求时遇到了一些问题。"}
                
                message = response.choices[0].message
                
                # 添加模型回复到消息历史
                if provide_tools and hasattr(message, 'tool_calls') and message.tool_calls:
                    # 处理有工具调用的情况
                    assistant_message = {
                        "role": "assistant", 
                        "content": message.content,
                    }
                    
                    # 如果有tool_calls字段，添加它
                    if hasattr(message, 'tool_calls') and message.tool_calls:
                        # 直接添加工具调用信息，不用包装成字典
                        assistant_message["tool_calls"] = message.tool_calls
                    
                    messages.append(assistant_message)
                else:
                    # 没有工具调用的情况
                    messages.append({"role": "assistant", "content": message.content})
                
                # 检查是否有工具调用
                if not provide_tools or not hasattr(message, 'tool_calls') or not message.tool_calls:
                    # 如果没有工具调用或已达到最大迭代次数，使用最后一次响应
                    break
                
                # 处理工具调用
                has_tool_calls = False
                
                for tool_call in message.tool_calls:
                    try:
                        # 提取工具调用信息
                        function_name = tool_call.function.name
                        arguments = json.loads(tool_call.function.arguments)
                        
                        result = None
                        # 根据函数名调用相应的工具
                        if function_name == "search_arxiv_papers":
                            papers = await self.arxiv_tool.search(
                                query=arguments.get("query"),
                                max_results=arguments.get("max_results", 3)
                            )
                            result = {"papers": papers}
                            has_tool_calls = True
                        
                        elif function_name == "get_paper_by_id":
                            paper = await self.arxiv_tool.get_paper_by_id(arguments.get("paper_id"))
                            result = {"paper": paper}
                            has_tool_calls = True
                        
                        # 添加工具响应
                        if result:
                            messages.append({
                                "tool_call_id": tool_call.id,
                                "role": "tool",
                                "name": function_name,
                                "content": json.dumps(result, ensure_ascii=False)
                            })
                    except Exception as e:
                        print(f"处理工具调用时出错: {str(e)}")
                        # 添加错误响应
                        messages.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name if hasattr(tool_call, 'function') and hasattr(tool_call.function, 'name') else "unknown",
                            "content": json.dumps({"error": str(e)}, ensure_ascii=False)
                        })
                
                # 如果没有实际的工具调用，退出循环
                if not has_tool_calls:
                    break
            
            # 获取最终回答
            final_answer = messages[-1]["content"] if messages[-1]["role"] == "assistant" else None
            
            # 如果最后一条消息不是助手回复（可能是工具响应），再次调用模型获取最终回答
            if final_answer is None:
                final_response = await self.llm_tool.chat_completion(
                    messages=messages,
                    temperature=0.3,
                    # 最后一次不再提供工具
                    tools=None
                )
                
                if isinstance(final_response, dict) and "error" in final_response and final_response["error"]:
                    logging.error(final_response.get('message', '未知错误'))
                    return {"answer": "抱歉，在处理您的请求时遇到了一些问题"}
                
                final_answer = final_response.choices[0].message.content
            
            return {
                "answer": final_answer,
                "iterations": current_iteration,
                "raw_messages": messages
            }
            
        except Exception as e:
            print(f"处理工具调用过程中出错: {str(e)}")
            # 出错时返回一个友好的错误消息
            return {
                "answer": f"抱歉，在处理您的问题时遇到了技术问题。请尝试重新表述您的问题或稍后再试。",
                "error": str(e)
            }


# 添加测试用的主函数
if __name__ == "__main__":
    import asyncio
    import os
    import json
    import traceback
    from dotenv import load_dotenv
    
    # 加载环境变量
    load_dotenv()
    
    # 确保OpenAI API密钥已设置
    if not os.environ.get("OPENAI_API_KEY"):
        print("错误: 未找到OPENAI_API_KEY环境变量。请在.env文件中设置该变量。")
        exit(1)
    
    async def test_paper_qa_agent():
        # 初始化PaperQAAgent
        agent = PaperQAAgent()
        
        # 测试用的查询示例
        test_queries = [
            "你能介绍一下大语言模型最近的进展吗？",
            "请解释一下论文2303.08774的主要贡献",
            "多模态大模型在医疗领域有哪些应用？",
            "GPT-4论文的主要内容是什么？"
        ]
        
        # 选择查询
        print("\n可用测试查询:")
        for i, q in enumerate(test_queries):
            print(f"{i+1}. {q}")
        
        choice = input("\n请选择测试查询编号 (1-4)，或输入自定义查询: ")
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(test_queries):
                query = test_queries[idx]
            else:
                query = choice
        except ValueError:
            query = choice
            
        print(f"\n{'=' * 50}")
        print(f"测试查询: {query}")
        print(f"{'=' * 50}")
        
        # 处理查询
        try:
            print("正在处理查询...")
            result = await agent.process(query)
            
            # 打印回答
            print(f"\n回答: {result['answer']}")
            print(f"迭代次数: {result.get('iterations', 'N/A')}")
            
            # 询问是否显示详细消息历史
            show_details = input("\n是否显示详细消息历史? (y/n): ").lower() == 'y'
            if show_details and 'raw_messages' in result:
                print("\n消息历史:")
                for i, msg in enumerate(result['raw_messages']):
                    role = msg.get('role', '未知')
                    content = msg.get('content', '')
                    
                    if content and len(content) > 200:
                        content = content[:200] + "..."
                        
                    print(f"\n[{i+1}] {role}: {content}")
                    
                    # 如果是工具调用，显示工具名称
                    if msg.get('name'):
                        print(f"   工具: {msg.get('name')}")
            
        except Exception as e:
            print(f"错误: {str(e)}")
            print("详细错误信息:")
            traceback.print_exc()
    
    # 运行测试
    asyncio.run(test_paper_qa_agent())
