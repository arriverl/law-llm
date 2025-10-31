"""
MongoDB知识库服务
使用MongoDB存储和管理法律知识库
"""
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from ..models.mongodb_models import KnowledgeBase, User, LegalConsultation
from ..database_mongodb import get_mongodb

logger = logging.getLogger(__name__)

class MongoDBKnowledgeService:
    """MongoDB知识库服务"""
    
    def __init__(self):
        self.db = get_mongodb()
    
    async def create_knowledge(self, knowledge_data: Dict[str, Any]) -> str:
        """创建知识条目"""
        try:
            knowledge = KnowledgeBase(**knowledge_data)
            knowledge.save()
            logger.info(f"知识条目创建成功: {knowledge.title}")
            return str(knowledge.id)
        except Exception as e:
            logger.error(f"创建知识条目失败: {e}")
            raise
    
    async def get_knowledge_by_id(self, knowledge_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取知识条目"""
        try:
            knowledge = KnowledgeBase.objects(id=knowledge_id).first()
            if knowledge:
                return self._serialize_knowledge(knowledge)
            return None
        except Exception as e:
            logger.error(f"获取知识条目失败: {e}")
            return None
    
    async def search_knowledge(self, query: str, category: str = None, 
                             tags: List[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """搜索知识库"""
        try:
            # 构建查询条件
            search_filter = {"is_active": True}
            
            if category:
                search_filter["category"] = category
            
            if tags:
                search_filter["tags__in"] = tags
            
            # 执行搜索
            if query:
                # 使用MongoDB的文本搜索
                knowledge_items = KnowledgeBase.objects(
                    __raw__={
                        "$and": [
                            search_filter,
                            {"$text": {"$search": query}}
                        ]
                    }
                ).limit(limit)
            else:
                knowledge_items = KnowledgeBase.objects(**search_filter).limit(limit)
            
            results = []
            for item in knowledge_items:
                results.append(self._serialize_knowledge(item))
            
            return results
            
        except Exception as e:
            logger.error(f"搜索知识库失败: {e}")
            return []
    
    async def get_knowledge_by_category(self, category: str, skip: int = 0, limit: int = 20) -> List[Dict[str, Any]]:
        """根据分类获取知识条目"""
        try:
            knowledge_items = KnowledgeBase.objects(
                category=category,
                is_active=True
            ).skip(skip).limit(limit)
            
            results = []
            for item in knowledge_items:
                results.append(self._serialize_knowledge(item))
            
            return results
            
        except Exception as e:
            logger.error(f"获取分类知识失败: {e}")
            return []
    
    async def update_knowledge(self, knowledge_id: str, update_data: Dict[str, Any]) -> bool:
        """更新知识条目"""
        try:
            knowledge = KnowledgeBase.objects(id=knowledge_id).first()
            if not knowledge:
                return False
            
            # 更新字段
            for key, value in update_data.items():
                if hasattr(knowledge, key):
                    setattr(knowledge, key, value)
            
            knowledge.updated_at = datetime.utcnow()
            knowledge.save()
            
            logger.info(f"知识条目更新成功: {knowledge.title}")
            return True
            
        except Exception as e:
            logger.error(f"更新知识条目失败: {e}")
            return False
    
    async def delete_knowledge(self, knowledge_id: str) -> bool:
        """删除知识条目（软删除）"""
        try:
            knowledge = KnowledgeBase.objects(id=knowledge_id).first()
            if not knowledge:
                return False
            
            knowledge.is_active = False
            knowledge.save()
            
            logger.info(f"知识条目删除成功: {knowledge.title}")
            return True
            
        except Exception as e:
            logger.error(f"删除知识条目失败: {e}")
            return False
    
    async def get_knowledge_stats(self) -> Dict[str, Any]:
        """获取知识库统计信息"""
        try:
            # 总数量
            total_count = KnowledgeBase.objects(is_active=True).count()
            
            # 按分类统计
            pipeline = [
                {"$match": {"is_active": True}},
                {"$group": {"_id": "$category", "count": {"$sum": 1}}}
            ]
            
            category_stats = {}
            for item in self.db.knowledge_base.aggregate(pipeline):
                category_stats[item["_id"]] = item["count"]
            
            # 按标签统计
            tag_pipeline = [
                {"$match": {"is_active": True}},
                {"$unwind": "$tags"},
                {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 10}
            ]
            
            top_tags = []
            for item in self.db.knowledge_base.aggregate(tag_pipeline):
                top_tags.append({"tag": item["_id"], "count": item["count"]})
            
            return {
                "total_count": total_count,
                "category_stats": category_stats,
                "top_tags": top_tags,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}
    
    async def get_popular_knowledge(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取热门知识条目"""
        try:
            knowledge_items = KnowledgeBase.objects(
                is_active=True
            ).order_by('-view_count').limit(limit)
            
            results = []
            for item in knowledge_items:
                results.append(self._serialize_knowledge(item))
            
            return results
            
        except Exception as e:
            logger.error(f"获取热门知识失败: {e}")
            return []
    
    async def increment_view_count(self, knowledge_id: str) -> bool:
        """增加浏览次数"""
        try:
            knowledge = KnowledgeBase.objects(id=knowledge_id).first()
            if knowledge:
                knowledge.view_count += 1
                knowledge.save()
                return True
            return False
        except Exception as e:
            logger.error(f"增加浏览次数失败: {e}")
            return False
    
    async def get_related_knowledge(self, knowledge_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """获取相关知识条目"""
        try:
            knowledge = KnowledgeBase.objects(id=knowledge_id).first()
            if not knowledge:
                return []
            
            # 基于标签和分类查找相关条目
            related_items = KnowledgeBase.objects(
                is_active=True,
                id__ne=knowledge_id,
                __raw__={
                    "$or": [
                        {"category": knowledge.category},
                        {"tags": {"$in": knowledge.tags}}
                    ]
                }
            ).limit(limit)
            
            results = []
            for item in related_items:
                results.append(self._serialize_knowledge(item))
            
            return results
            
        except Exception as e:
            logger.error(f"获取相关知识失败: {e}")
            return []
    
    def _serialize_knowledge(self, knowledge: KnowledgeBase) -> Dict[str, Any]:
        """序列化知识条目"""
        return {
            "id": str(knowledge.id),
            "title": knowledge.title,
            "content": knowledge.content,
            "category": knowledge.category,
            "tags": knowledge.tags,
            "source": knowledge.source,
            "version": knowledge.version,
            "is_active": knowledge.is_active,
            "word_count": knowledge.word_count,
            "reading_time": knowledge.reading_time,
            "difficulty_level": knowledge.difficulty_level,
            "view_count": knowledge.view_count,
            "like_count": knowledge.like_count,
            "share_count": knowledge.share_count,
            "created_at": knowledge.created_at.isoformat() if knowledge.created_at else None,
            "updated_at": knowledge.updated_at.isoformat() if knowledge.updated_at else None
        }

# 全局MongoDB知识库服务实例
mongodb_knowledge_service = MongoDBKnowledgeService()






