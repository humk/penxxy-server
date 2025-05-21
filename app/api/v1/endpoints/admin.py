from typing import Dict, List, Any, Optional
import os
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile, Body
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger("admin")

# 简单的管理员认证
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def check_admin_token(token: str = Depends(oauth2_scheme)):
    """检查管理员令牌"""
    if token != settings.ADMIN_TOKEN:
        logger.warning(f"管理员认证失败，使用了无效令牌: {token[:5]}...")
        raise HTTPException(status_code=401, detail="无效的管理员令牌")
    return token


@router.get("/logs", response_model=Dict[str, Any])
async def get_logs(
    log_type: str = Query("app", description="日志类型: app, api, db, llm, arxiv, paper_qa, wechat_mp"),
    lines: int = Query(100, ge=1, le=1000, description="返回的日志行数"),
    token: str = Depends(check_admin_token)
):
    """
    获取指定类型的日志
    """
    log_dir = Path("logs")
    log_file = log_dir / f"{log_type}.log"
    
    if not log_file.exists():
        log_files = [f.name for f in log_dir.glob("*.log")]
        logger.warning(f"请求的日志文件 {log_type}.log 不存在")
        return {
            "error": True,
            "message": f"找不到指定的日志文件: {log_type}.log",
            "available_logs": log_files
        }
    
    try:
        # 读取最后N行日志
        with open(log_file, "r", encoding="utf-8") as f:
            all_lines = f.readlines()
            log_content = all_lines[-lines:] if len(all_lines) > lines else all_lines
        
        logger.info(f"成功读取日志文件: {log_type}.log，返回 {len(log_content)} 行")
        return {
            "error": False,
            "log_type": log_type,
            "lines": len(log_content),
            "content": log_content
        }
    except Exception as e:
        logger.error(f"读取日志文件时出错: {str(e)}")
        return {
            "error": True,
            "message": f"读取日志文件时出错: {str(e)}"
        }


@router.get("/logs/types", response_model=List[str])
async def get_log_types(token: str = Depends(check_admin_token)):
    """
    获取可用的日志类型
    """
    log_dir = Path("logs")
    
    if not log_dir.exists():
        logger.warning("日志目录不存在")
        return []
    
    try:
        log_files = [f.stem for f in log_dir.glob("*.log")]
        logger.info(f"找到 {len(log_files)} 个日志文件")
        return log_files
    except Exception as e:
        logger.error(f"获取日志类型时出错: {str(e)}")
        return [] 