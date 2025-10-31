"""
MongoDB数据库连接和配置
"""
from mongoengine import connect, disconnect
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import logging

from .core.config import settings

logger = logging.getLogger(__name__)

class MongoDBManager:
    """MongoDB连接管理器"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database = None
    
    async def connect(self):
        """连接MongoDB"""
        try:
            # 同步连接（用于MongoEngine）
            connect(
                db=settings.MONGODB_DATABASE,
                host=settings.MONGODB_URL,
                alias='default'
            )
            
            # 异步连接（用于Motor）
            self.client = AsyncIOMotorClient(settings.MONGODB_URL)
            self.database = self.client[settings.MONGODB_DATABASE]
            
            # 测试连接
            await self.client.admin.command('ping')
            logger.info("MongoDB连接成功")
            
        except Exception as e:
            logger.error(f"MongoDB连接失败: {e}")
            raise
    
    async def disconnect(self):
        """断开MongoDB连接"""
        try:
            if self.client:
                self.client.close()
            disconnect()
            logger.info("MongoDB连接已断开")
        except Exception as e:
            logger.error(f"断开MongoDB连接失败: {e}")
    
    def get_database(self):
        """获取数据库实例"""
        return self.database
    
    async def create_indexes(self):
        """创建索引"""
        try:
            # 为知识库创建文本搜索索引
            await self.database.knowledge_base.create_index([
                ("title", "text"),
                ("content", "text"),
                ("tags", "text")
            ])
            
            # 为咨询记录创建复合索引
            await self.database.legal_consultations.create_index([
                ("user_id", 1),
                ("created_at", -1)
            ])
            
            # 为生态合作伙伴创建索引
            await self.database.ecosystem_partners.create_index([
                ("type", 1),
                ("region", 1),
                ("status", 1)
            ])
            
            logger.info("MongoDB索引创建成功")
            
        except Exception as e:
            logger.error(f"创建MongoDB索引失败: {e}")

# 全局MongoDB管理器实例
mongodb_manager = MongoDBManager()

async def init_mongodb():
    """初始化MongoDB"""
    await mongodb_manager.connect()
    await mongodb_manager.create_indexes()

async def close_mongodb():
    """关闭MongoDB连接"""
    await mongodb_manager.disconnect()

def get_mongodb():
    """获取MongoDB数据库实例"""
    return mongodb_manager.get_database()






