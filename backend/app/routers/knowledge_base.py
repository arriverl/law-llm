"""
法律知识库管理路由
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import json

from ..database import get_db, KnowledgeBase
from .auth import get_current_user

router = APIRouter()

# 请求模型
class KnowledgeCreate(BaseModel):
    title: str
    content: str
    category: str
    tags: List[str] = []
    source: str

class KnowledgeUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    source: Optional[str] = None

class KnowledgeSearch(BaseModel):
    query: str
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    limit: int = 10

# 响应模型
class KnowledgeResponse(BaseModel):
    id: int
    title: str
    content: str
    category: str
    tags: List[str]
    source: str
    version: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

class SearchResult(BaseModel):
    id: int
    title: str
    content: str
    category: str
    tags: List[str]
    relevance_score: float

@router.post("/knowledge", response_model=KnowledgeResponse)
async def create_knowledge(
    knowledge_data: KnowledgeCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """创建知识条目"""
    try:
        new_knowledge = KnowledgeBase(
            title=knowledge_data.title,
            content=knowledge_data.content,
            category=knowledge_data.category,
            tags=knowledge_data.tags,
            source=knowledge_data.source,
            version="1.0"
        )
        
        db.add(new_knowledge)
        db.commit()
        db.refresh(new_knowledge)
        
        return KnowledgeResponse(
            id=new_knowledge.id,
            title=new_knowledge.title,
            content=new_knowledge.content,
            category=new_knowledge.category,
            tags=new_knowledge.tags,
            source=new_knowledge.source,
            version=new_knowledge.version,
            is_active=new_knowledge.is_active,
            created_at=new_knowledge.created_at,
            updated_at=new_knowledge.updated_at
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建知识条目失败: {str(e)}")

@router.get("/knowledge", response_model=List[KnowledgeResponse])
async def get_knowledge_list(
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """获取知识库列表"""
    query = db.query(KnowledgeBase).filter(KnowledgeBase.is_active == True)
    
    if category:
        query = query.filter(KnowledgeBase.category == category)
    
    knowledge_items = query.offset(skip).limit(limit).all()
    
    return [
        KnowledgeResponse(
            id=k.id,
            title=k.title,
            content=k.content,
            category=k.category,
            tags=k.tags,
            source=k.source,
            version=k.version,
            is_active=k.is_active,
            created_at=k.created_at,
            updated_at=k.updated_at
        )
        for k in knowledge_items
    ]

@router.get("/knowledge/{knowledge_id}", response_model=KnowledgeResponse)
async def get_knowledge(
    knowledge_id: int,
    db: Session = Depends(get_db)
):
    """获取特定知识条目"""
    knowledge = db.query(KnowledgeBase).filter(KnowledgeBase.id == knowledge_id).first()
    
    if not knowledge:
        raise HTTPException(status_code=404, detail="知识条目不存在")
    
    return KnowledgeResponse(
        id=knowledge.id,
        title=knowledge.title,
        content=knowledge.content,
        category=knowledge.category,
        tags=knowledge.tags,
        source=knowledge.source,
        version=knowledge.version,
        is_active=knowledge.is_active,
        created_at=knowledge.created_at,
        updated_at=knowledge.updated_at
    )

@router.put("/knowledge/{knowledge_id}", response_model=KnowledgeResponse)
async def update_knowledge(
    knowledge_id: int,
    knowledge_data: KnowledgeUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """更新知识条目"""
    knowledge = db.query(KnowledgeBase).filter(KnowledgeBase.id == knowledge_id).first()
    
    if not knowledge:
        raise HTTPException(status_code=404, detail="知识条目不存在")
    
    # 更新字段
    if knowledge_data.title is not None:
        knowledge.title = knowledge_data.title
    if knowledge_data.content is not None:
        knowledge.content = knowledge_data.content
    if knowledge_data.category is not None:
        knowledge.category = knowledge_data.category
    if knowledge_data.tags is not None:
        knowledge.tags = knowledge_data.tags
    if knowledge_data.source is not None:
        knowledge.source = knowledge_data.source
    
    knowledge.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(knowledge)
    
    return KnowledgeResponse(
        id=knowledge.id,
        title=knowledge.title,
        content=knowledge.content,
        category=knowledge.category,
        tags=knowledge.tags,
        source=knowledge.source,
        version=knowledge.version,
        is_active=knowledge.is_active,
        created_at=knowledge.created_at,
        updated_at=knowledge.updated_at
    )

@router.delete("/knowledge/{knowledge_id}")
async def delete_knowledge(
    knowledge_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """删除知识条目"""
    knowledge = db.query(KnowledgeBase).filter(KnowledgeBase.id == knowledge_id).first()
    
    if not knowledge:
        raise HTTPException(status_code=404, detail="知识条目不存在")
    
    knowledge.is_active = False
    db.commit()
    
    return {"message": "知识条目已删除"}

@router.post("/search", response_model=List[SearchResult])
async def search_knowledge(
    search_data: KnowledgeSearch,
    db: Session = Depends(get_db)
):
    """搜索知识库"""
    try:
        # 简化的搜索实现
        query = db.query(KnowledgeBase).filter(KnowledgeBase.is_active == True)
        
        if search_data.category:
            query = query.filter(KnowledgeBase.category == search_data.category)
        
        if search_data.tags:
            # 这里应该实现更复杂的标签搜索逻辑
            pass
        
        # 简单的文本搜索
        search_results = query.filter(
            KnowledgeBase.title.contains(search_data.query) |
            KnowledgeBase.content.contains(search_data.query)
        ).limit(search_data.limit).all()
        
        results = []
        for item in search_results:
            # 计算相关性分数（简化实现）
            relevance_score = 0.8 if search_data.query.lower() in item.title.lower() else 0.6
            
            results.append(SearchResult(
                id=item.id,
                title=item.title,
                content=item.content[:200] + "..." if len(item.content) > 200 else item.content,
                category=item.category,
                tags=item.tags,
                relevance_score=relevance_score
            ))
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")

@router.post("/upload")
async def upload_knowledge_file(
    file: UploadFile = File(...),
    category: str = "general",
    background_tasks: BackgroundTasks = None,
    current_user: dict = Depends(get_current_user)
):
    """上传知识文件"""
    try:
        if not file.filename.endswith(('.txt', '.pdf', '.docx')):
            raise HTTPException(status_code=400, detail="不支持的文件格式")
        
        # 读取文件内容
        content = await file.read()
        
        # 异步处理文件解析
        background_tasks.add_task(
            process_uploaded_file,
            file.filename,
            content,
            category,
            current_user
        )
        
        return {
            "filename": file.filename,
            "status": "processing",
            "message": "文件上传成功，正在处理中"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")

@router.get("/categories")
async def get_knowledge_categories():
    """获取知识库分类"""
    categories = [
        {"id": "civil_law", "name": "民法", "description": "民事法律条文和案例"},
        {"id": "criminal_law", "name": "刑法", "description": "刑事法律条文和案例"},
        {"id": "administrative_law", "name": "行政法", "description": "行政法律条文和案例"},
        {"id": "commercial_law", "name": "商法", "description": "商事法律条文和案例"},
        {"id": "labor_law", "name": "劳动法", "description": "劳动法律条文和案例"},
        {"id": "intellectual_property", "name": "知识产权法", "description": "知识产权法律条文和案例"},
        {"id": "international_law", "name": "国际法", "description": "国际法律条文和案例"},
        {"id": "environmental_law", "name": "环境法", "description": "环境法律条文和案例"}
    ]
    
    return {"categories": categories}

@router.get("/stats")
async def get_knowledge_stats(db: Session = Depends(get_db)):
    """获取知识库统计信息"""
    try:
        total_knowledge = db.query(KnowledgeBase).filter(KnowledgeBase.is_active == True).count()
        
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
            "total_knowledge": total_knowledge,
            "category_stats": category_stats,
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")

async def process_uploaded_file(filename: str, content: bytes, category: str, current_user: dict):
    """异步处理上传的文件"""
    # 这里实现文件解析和知识提取逻辑
    pass
