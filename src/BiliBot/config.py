
# config.py
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, Any
import json
import os
from functools import lru_cache

class Settings(BaseSettings):
    """使用 Field 设置默认值"""
    
    version: str = "1.0.1"
    enable_ai: bool = True
    deepseek_api: str = ""
    deepseek_system: str = "You are a helpful chat bot."
    cookie: str = ""
    check_time: int = 3
    csrf: str = ""
    bot_name: str = "BiliBot"
    uid: str = ""
    connect_out: int = 5
    receive_out: int = 5
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
    enable_debug: bool = False
    enable_like: bool = False # 允许用户点赞后立即回复表达感激，不要开启，除非你清楚地意识到自己在做什么
    tools: dict[str, Any] = {}
    
    # 模型配置
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="", 
        case_sensitive=False,
        extra="ignore"
    )
    @field_validator('tools', mode='before')
    @classmethod
    def load_tools(cls, v):
        """从 tools.json 文件加载工具配置"""
        with open("tools.json", "r", encoding="UTF-8") as f:
            return json.load(f)

@lru_cache()
def get_config() -> Settings:
    """获取配置实例（带缓存）"""
    return Settings()

CONFIG = get_config()
