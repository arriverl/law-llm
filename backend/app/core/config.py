"""
系统配置管理
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    """应用配置"""
    
    # 基础配置
    APP_NAME: str = "AI法律服务生态链系统"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 数据库配置 - MongoDB版本
    MONGODB_URL: str = "mongodb://localhost:27017"  # MongoDB连接URL
    MONGODB_DATABASE: str = "law_ai_db"  # MongoDB数据库名
    # 保留SQLite作为备用
    DATABASE_URL: str = "sqlite:///./law_ai.db"
    REDIS_URL: str = "redis://localhost:6379"
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AI模型配置
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    BERT_MODEL_PATH: str = "./models/bert-legal"
    MAX_TOKENS: int = 4096
    TEMPERATURE: float = 0.7
    
    # 法律知识库配置
    KNOWLEDGE_BASE_PATH: str = "./data/knowledge_base"
    CASE_DATABASE_URL: str = "postgresql://user:password@localhost/case_db"
    
    # 生态协同配置
    BLOCKCHAIN_RPC_URL: str = "https://mainnet.infura.io/v3/your-project-id"
    SMART_CONTRACT_ADDRESS: str = ""
    
    # CORS配置
    ALLOWED_HOSTS: str = "http://localhost:3000,http://localhost:8080"
    
    # 文件上传配置
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "./uploads"
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    
    # 性能配置
    MAX_CONCURRENT_REQUESTS: int = 100
    REQUEST_TIMEOUT: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# 创建全局配置实例
settings = Settings()
