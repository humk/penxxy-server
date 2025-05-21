import os
import logging
from logging.handlers import RotatingFileHandler
import sys
from pathlib import Path

# 创建日志目录
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# 日志格式
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 日志级别映射
LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL
}

def setup_logger(name, log_file=None, level="info"):
    """
    设置一个命名日志记录器
    :param name: 日志记录器名称
    :param log_file: 日志文件名（可选）
    :param level: 日志级别（debug, info, warning, error, critical）
    :return: 日志记录器实例
    """
    # 获取日志级别
    log_level = LOG_LEVELS.get(level.lower(), logging.INFO)
    
    # 创建logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    logger.propagate = False  # 避免日志重复
    
    # 如果已有处理器，则不再添加
    if logger.handlers:
        return logger
    
    # 创建格式器
    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器（如果指定）
    if log_file:
        file_path = log_dir / log_file
        file_handler = RotatingFileHandler(
            file_path, 
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

# 预配置的日志记录器
app_logger = setup_logger("app", "app.log")
api_logger = setup_logger("api", "api.log")
db_logger = setup_logger("db", "db.log")
llm_logger = setup_logger("llm", "llm.log")

# 获取或创建日志记录器的便捷函数
def get_logger(name=None):
    """
    获取一个命名日志记录器，如果不存在则创建一个新的
    :param name: 日志记录器名称，如果为None，则返回app_logger
    :return: 日志记录器实例
    """
    if name is None:
        return app_logger
    
    # 检查是否已存在预配置的日志记录器
    if name == "app":
        return app_logger
    elif name == "api":
        return api_logger
    elif name == "db":
        return db_logger
    elif name == "llm":
        return llm_logger
    
    # 为其他模块创建新的日志记录器
    return setup_logger(name, f"{name}.log") 