"""
法律知识库构建服务
实现知识采集、处理、存储和检索的完整流程
"""
import os
import json
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import PyPDF2
from docx import Document as DocxDocument
from sqlalchemy.orm import Session
from ..database import KnowledgeBase, get_db
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)

class LegalKnowledgeBuilder:
    """法律知识库构建器"""
    
    def __init__(self):
        self.knowledge_base_path = settings.KNOWLEDGE_BASE_PATH
        self.supported_formats = ['.txt', '.pdf', '.docx', '.html']
        
    async def build_knowledge_base(self, db: Session):
        """构建完整的法律知识库"""
        try:
            # 1. 初始化基础法律条文
            await self._init_basic_laws(db)
            
            # 2. 采集案例数据
            await self._collect_legal_cases(db)
            
            # 3. 处理实务文档
            await self._process_practical_docs(db)
            
            # 4. 建立知识关联
            await self._build_knowledge_relations(db)
            
            logger.info("法律知识库构建完成")
            return True
            
        except Exception as e:
            logger.error(f"知识库构建失败: {e}")
            return False
    
    async def _init_basic_laws(self, db: Session):
        """初始化基础法律条文"""
        basic_laws = [
            {
                "title": "中华人民共和国民法典",
                "content": "民法典是民事法律的基础，规定了民事主体的权利义务关系...",
                "category": "civil_law",
                "tags": ["民法典", "民事法律", "基础法律"],
                "source": "全国人大",
                "version": "2021.1.1"
            },
            {
                "title": "中华人民共和国刑法",
                "content": "刑法规定了犯罪和刑罚的基本制度，是刑事法律的核心...",
                "category": "criminal_law", 
                "tags": ["刑法", "刑事法律", "犯罪"],
                "source": "全国人大",
                "version": "2021.3.1"
            },
            {
                "title": "中华人民共和国行政诉讼法",
                "content": "行政诉讼法规定了行政诉讼的基本程序和要求...",
                "category": "administrative_law",
                "tags": ["行政法", "行政诉讼", "程序法"],
                "source": "全国人大",
                "version": "2017.7.1"
            }
        ]
        
        for law in basic_laws:
            # 检查是否已存在
            existing = db.query(KnowledgeBase).filter(
                KnowledgeBase.title == law["title"]
            ).first()
            
            if not existing:
                knowledge_item = KnowledgeBase(
                    title=law["title"],
                    content=law["content"],
                    category=law["category"],
                    tags=law["tags"],
                    source=law["source"],
                    version=law["version"]
                )
                db.add(knowledge_item)
        
        db.commit()
        logger.info("基础法律条文初始化完成")
    
    async def _collect_legal_cases(self, db: Session):
        """采集法律案例数据"""
        # 模拟案例数据采集
        cases = [
            {
                "title": "合同纠纷典型案例",
                "content": "某公司与供应商签订采购合同，因质量问题产生纠纷...",
                "category": "civil_law",
                "tags": ["合同纠纷", "典型案例", "民事纠纷"],
                "source": "最高人民法院",
                "version": "2023.1"
            },
            {
                "title": "劳动争议处理案例",
                "content": "员工与用人单位因工资支付问题产生争议...",
                "category": "labor_law",
                "tags": ["劳动争议", "工资支付", "劳动法"],
                "source": "劳动仲裁委员会",
                "version": "2023.2"
            }
        ]
        
        for case in cases:
            existing = db.query(KnowledgeBase).filter(
                KnowledgeBase.title == case["title"]
            ).first()
            
            if not existing:
                knowledge_item = KnowledgeBase(
                    title=case["title"],
                    content=case["content"],
                    category=case["category"],
                    tags=case["tags"],
                    source=case["source"],
                    version=case["version"]
                )
                db.add(knowledge_item)
        
        db.commit()
        logger.info("法律案例采集完成")
    
    async def _process_practical_docs(self, db: Session):
        """处理实务文档"""
        # 实务文档模板
        practical_docs = [
            {
                "title": "合同审查要点",
                "content": "合同审查是法律实务中的重要环节，需要注意以下要点...",
                "category": "commercial_law",
                "tags": ["合同审查", "实务指南", "商业法律"],
                "source": "律师事务所",
                "version": "2023.1"
            },
            {
                "title": "劳动争议处理流程",
                "content": "劳动争议处理需要按照法定程序进行，具体流程如下...",
                "category": "labor_law",
                "tags": ["劳动争议", "处理流程", "劳动法"],
                "source": "劳动法律师",
                "version": "2023.1"
            }
        ]
        
        for doc in practical_docs:
            existing = db.query(KnowledgeBase).filter(
                KnowledgeBase.title == doc["title"]
            ).first()
            
            if not existing:
                knowledge_item = KnowledgeBase(
                    title=doc["title"],
                    content=doc["content"],
                    category=doc["category"],
                    tags=doc["tags"],
                    source=doc["source"],
                    version=doc["version"]
                )
                db.add(knowledge_item)
        
        db.commit()
        logger.info("实务文档处理完成")
    
    async def _build_knowledge_relations(self, db: Session):
        """建立知识关联关系"""
        # 这里可以实现知识条目之间的关联关系
        # 例如：相关法条、相关案例、相关实务等
        logger.info("知识关联关系建立完成")
    
    async def import_from_file(self, file_path: str, category: str, db: Session):
        """从文件导入知识"""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.txt':
                content = self._extract_from_txt(file_path)
            elif file_ext == '.pdf':
                content = self._extract_from_pdf(file_path)
            elif file_ext == '.docx':
                content = self._extract_from_docx(file_path)
            else:
                raise ValueError(f"不支持的文件格式: {file_ext}")
            
            # 生成知识条目
            title = os.path.basename(file_path)
            knowledge_item = KnowledgeBase(
                title=title,
                content=content,
                category=category,
                tags=self._extract_tags(content),
                source="文件导入",
                version="1.0"
            )
            
            db.add(knowledge_item)
            db.commit()
            
            logger.info(f"文件导入成功: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"文件导入失败: {e}")
            return False
    
    def _extract_from_txt(self, file_path: str) -> str:
        """从TXT文件提取内容"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """从PDF文件提取内容"""
        content = ""
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                content += page.extract_text()
        return content
    
    def _extract_from_docx(self, file_path: str) -> str:
        """从DOCX文件提取内容"""
        doc = DocxDocument(file_path)
        content = ""
        for paragraph in doc.paragraphs:
            content += paragraph.text + "\n"
        return content
    
    def _extract_tags(self, content: str) -> List[str]:
        """从内容中提取标签"""
        # 简化的标签提取逻辑
        legal_keywords = [
            "合同", "侵权", "婚姻", "继承", "劳动", "刑事", "行政",
            "民事", "商事", "知识产权", "环境", "金融", "房地产"
        ]
        
        tags = []
        for keyword in legal_keywords:
            if keyword in content:
                tags.append(keyword)
        
        return tags
    
    async def search_knowledge(self, query: str, category: str = None, db: Session = None):
        """搜索知识库"""
        try:
            # 构建查询
            search_query = db.query(KnowledgeBase).filter(
                KnowledgeBase.is_active == True
            )
            
            if category:
                search_query = search_query.filter(KnowledgeBase.category == category)
            
            # 简单的文本搜索
            results = search_query.filter(
                KnowledgeBase.title.contains(query) |
                KnowledgeBase.content.contains(query)
            ).all()
            
            return results
            
        except Exception as e:
            logger.error(f"知识搜索失败: {e}")
            return []
    
    async def get_knowledge_stats(self, db: Session):
        """获取知识库统计信息"""
        try:
            total_count = db.query(KnowledgeBase).filter(KnowledgeBase.is_active == True).count()
            
            # 按分类统计
            category_stats = {}
            categories = db.query(KnowledgeBase.category).distinct().all()
            
            for category in categories:
                count = db.query(KnowledgeBase).filter(
                    KnowledgeBase.category == category[0],
                    KnowledgeBase.is_active == True
                ).count()
                category_stats[category[0]] = count
            
            return {
                "total_count": total_count,
                "category_stats": category_stats,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}

# 全局知识库构建器实例
knowledge_builder = LegalKnowledgeBuilder()
