# src/chatbot/utils/error_handler.py
"""
统一的错误处理装饰器和工具
"""
import functools
from writelog import HandleLog
from typing import Callable, Any, Type, Union, Optional
import asyncio
from contextlib import contextmanager

logger = HandleLog()

class ChatError(Exception):
    def __init__(self, message: str, details: Any = None):
        super().__init__(message, "VALIDATION_ERROR", details)

class ChatbotException(Exception):
    """基础异常类"""
    def __init__(self, message: str, code: str = "INTERNAL_ERROR", details: Any = None):
        self.message = message
        self.code = code
        self.details = details
        super().__init__(self.message)

class ValidationError(ChatbotException):
    """输入验证错误"""
    def __init__(self, message: str, details: Any = None):
        super().__init__(message, "VALIDATION_ERROR", details)

class APIError(ChatbotException):
    """请求调用错误"""
    def __init__(self, message: str, details: Any = None):
        super().__init__(message, "REQUEST_ERROR", details)

class HandlerError(ChatbotException):
    """处理器错误"""
    def __init__(self, message: str, details: Any = None):
        super().__init__(message, "HANDLER_ERROR", details)

class ResourceNotFound(ChatbotException):
    """资源未找到"""
    def __init__(self, message: str, details: Any = None):
        super().__init__(message, "RESOURCE_NOT_FOUND", details)




def handle_errors(fallback_response: Any = None,log_level: str = "ERROR",capture_traceback: bool = True,retry_on: Optional[tuple] = (APIError,),max_retries: int = 0):
    """
    通用错误处理装饰器
    
    Args:
        fallback_response: 出错时返回的默认值
        log_level: 日志级别
        capture_traceback: 是否捕获堆栈信息
        retry_on: 需要重试的异常类型
        max_retries: 最大重试次数
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            retries = 0
            while True:
                try:
                    
                    return await func(*args, **kwargs)
                except tuple(retry_on) if retry_on else () as e:
                    if retries < max_retries:
                        retries += 1
                        logger.warning(f"正在重试{retries}/{max_retries}: 在{func.__name__}发生错误: {e}")
                        continue
                    raise
                except Exception as e:
                    await _log_and_handle_error(
                        e, func.__name__, log_level, 
                        capture_traceback, args, kwargs
                    )
                    return fallback_response
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            retries = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except tuple(retry_on) if retry_on else () as e:
                    if retries < max_retries:
                        retries += 1
                        logger.warning(f"正在重试{retries}/{max_retries}: 在{func.__name__}发生错误: {e}")
                        continue
                    raise
                except Exception as e:
                    _log_and_handle_error_sync(
                        e, func.__name__, log_level,
                        capture_traceback, args, kwargs
                    )
                    return fallback_response
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

async def _log_and_handle_error(
    error: Exception,
    func_name: str,
    log_level: str,
    capture_traceback: bool,
    args: tuple,
    kwargs: dict
):
    """处理异步函数错误"""
    
    logger.error(f"发生错误{func_name}: {error}")
    
    # 如果是我们定义的异常，记录详细信息
    if isinstance(error, ChatbotException):
        logger.debug(f"错误代码: {error.code}, 详细内容: {error.details}")

def _log_and_handle_error_sync(
    error: Exception,
    func_name: str,
    log_level: str,
    capture_traceback: bool,
    args: tuple,
    kwargs: dict
):
    """处理同步函数错误"""
    logger.error(f"发生错误{func_name}: {error}")
    
    if isinstance(error, ChatbotException):
        logger.debug(f"错误代码: {error.code}, 详细内容: {error.details}")