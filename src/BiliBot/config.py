
# config.py
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

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
    
    # 模型配置
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="", 
        case_sensitive=False,
        extra="ignore"
    )

CONFIG = Settings()
