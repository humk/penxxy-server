from typing import Dict, Any, List, Optional
import arxiv
import asyncio
from datetime import datetime
import re

from app.utils.logger import get_logger

# 获取ArXiv日志记录器
logger = get_logger("arxiv")

class ArxivTool:
    """
    ArXiv工具类，用于搜索和获取学术论文信息
    """
    
    async def search(
        self, 
        query: str, 
        max_results: int = 5,
        sort_by: arxiv.SortCriterion = arxiv.SortCriterion.Relevance
    ) -> List[Dict[str, Any]]:
        """
        搜索ArXiv论文
        
        Args:
            query: 搜索关键词
            max_results: 最大返回结果数
            sort_by: 排序方式
            
        Returns:
            论文信息列表
        """
        try:
            # 创建异步执行的任务
            loop = asyncio.get_event_loop()
            client = arxiv.Client()
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=sort_by
            )
            
            # 使用run_in_executor执行同步代码
            results = await loop.run_in_executor(
                None, lambda: list(client.results(search))
            )
            
            # 格式化结果
            papers = []
            for paper in results:
                # 格式化时间
                published = paper.published
                if isinstance(published, datetime):
                    published_str = published.strftime("%Y-%m-%d")
                else:
                    published_str = str(published)
                
                # 提取作者
                authors = [author.name for author in paper.authors]
                
                # 构建论文信息
                paper_info = {
                    "title": paper.title,
                    "authors": authors,
                    "summary": paper.summary,
                    "published": published_str,
                    "pdf_url": paper.pdf_url,
                    "arxiv_url": paper.entry_id,
                    "arxiv_id": paper.get_short_id(),
                    "categories": paper.categories
                }
                papers.append(paper_info)
            
            return papers
        
        except Exception as e:
            logger.error(f"ArXiv搜索失败: {str(e)}")
            return []
    
    async def get_paper_by_id(self, paper_id: str) -> Optional[Dict[str, Any]]:
        """
        通过ID获取指定论文
        
        Args:
            paper_id: ArXiv论文ID，可以是完整URL或纯ID
            
        Returns:
            论文信息，如果获取失败则返回None
        """
        try:
            # 提取ID
            if "arxiv.org" in paper_id:
                # 从URL中提取ID
                match = re.search(r'arxiv\.org\/(?:abs|pdf)\/([0-9v\.]+)', paper_id)
                if match:
                    paper_id = match.group(1)
            
            # 创建异步执行的任务
            loop = asyncio.get_event_loop()
            client = arxiv.Client()
            search = arxiv.Search(
                id_list=[paper_id]
            )
            
            # 使用run_in_executor执行同步代码
            results = await loop.run_in_executor(
                None, lambda: list(client.results(search))
            )
            
            if not results:
                return None
            
            paper = results[0]
            
            # 格式化时间
            published = paper.published
            if isinstance(published, datetime):
                published_str = published.strftime("%Y-%m-%d")
            else:
                published_str = str(published)
            
            # 提取作者
            authors = [author.name for author in paper.authors]
            
            # 构建论文信息
            paper_info = {
                "title": paper.title,
                "authors": authors,
                "summary": paper.summary,
                "published": published_str,
                "pdf_url": paper.pdf_url,
                "arxiv_url": paper.entry_id,
                "arxiv_id": paper.get_short_id(),
                "categories": paper.categories
            }
            
            return paper_info
        
        except Exception as e:
            logger.error(f"通过ID获取ArXiv论文失败: {str(e)}")
            return None 