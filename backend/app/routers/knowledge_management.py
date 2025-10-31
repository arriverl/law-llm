"""
知识库管理路由
提供知识库构建、导入、搜索等高级功能
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import os
from datetime import datetime

from ..database import get_db
from .auth import get_current_user
from ..services.knowledge_builder import knowledge_builder

router = APIRouter()

# 请求模型
class KnowledgeImportRequest(BaseModel):
    file_path: str
    category: str
    auto_extract_tags: bool = True

class KnowledgeSearchRequest(BaseModel):
    query: str
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    limit: int = 20

class KnowledgeBuildRequest(BaseModel):
    rebuild: bool = False
    include_cases: bool = True
    include_practical: bool = True

# 响应模型
class KnowledgeImportResponse(BaseModel):
    success: bool
    message: str
    knowledge_id: Optional[int] = None

class KnowledgeSearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    total: int
    query: str

@router.post("/build", response_model=Dict[str, Any])
async def build_knowledge_base(
    request: KnowledgeBuildRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """构建法律知识库"""
    try:
        # 异步构建知识库
        background_tasks.add_task(
            knowledge_builder.build_knowledge_base,
            db
        )
        
        return {
            "success": True,
            "message": "知识库构建已启动，请稍后查看结果",
            "task_id": f"build_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"知识库构建失败: {str(e)}")

@router.post("/import", response_model=KnowledgeImportResponse)
async def import_knowledge(
    file: UploadFile = File(...),
    category: str = "general",
    background_tasks: BackgroundTasks = None,
    current_user: dict = Depends(get_current_user)
):
    """导入知识文件"""
    try:
        # 检查文件格式
        if not file.filename.endswith(('.txt', '.pdf', '.docx')):
            raise HTTPException(status_code=400, detail="不支持的文件格式")
        
        # 保存上传文件
        upload_dir = "uploads/knowledge"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # 异步处理文件导入
        background_tasks.add_task(
            knowledge_builder.import_from_file,
            file_path,
            category
        )
        
        return KnowledgeImportResponse(
            success=True,
            message="文件上传成功，正在处理中",
            knowledge_id=None
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件导入失败: {str(e)}")

@router.post("/search", response_model=KnowledgeSearchResponse)
async def search_knowledge(
    request: KnowledgeSearchRequest,
    db: Session = Depends(get_db)
):
    """搜索知识库"""
    try:
        results = await knowledge_builder.search_knowledge(
            query=request.query,
            category=request.category,
            db=db
        )
        
        # 转换为响应格式
        search_results = []
        for item in results[:request.limit]:
            search_results.append({
                "id": item.id,
                "title": item.title,
                "content": item.content[:200] + "..." if len(item.content) > 200 else item.content,
                "category": item.category,
                "tags": item.tags,
                "source": item.source,
                "version": item.version,
                "created_at": item.created_at.isoformat()
            })
        
        return KnowledgeSearchResponse(
            results=search_results,
            total=len(results),
            query=request.query
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")

@router.get("/stats")
async def get_knowledge_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取知识库统计信息"""
    try:
        stats = await knowledge_builder.get_knowledge_stats(db)
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")

@router.post("/batch-import")
async def batch_import_knowledge(
    files: List[UploadFile] = File(...),
    category: str = "general",
    background_tasks: BackgroundTasks = None,
    current_user: dict = Depends(get_current_user)
):
    """批量导入知识文件"""
    try:
        results = []
        
        for file in files:
            # 检查文件格式
            if not file.filename.endswith(('.txt', '.pdf', '.docx')):
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "message": "不支持的文件格式"
                })
                continue
            
            # 保存文件
            upload_dir = "uploads/knowledge"
            os.makedirs(upload_dir, exist_ok=True)
            
            file_path = os.path.join(upload_dir, file.filename)
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # 异步处理
            background_tasks.add_task(
                knowledge_builder.import_from_file,
                file_path,
                category
            )
            
            results.append({
                "filename": file.filename,
                "success": True,
                "message": "文件上传成功，正在处理中"
            })
        
        return {
            "success": True,
            "message": f"批量导入完成，共处理 {len(files)} 个文件",
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量导入失败: {str(e)}")

@router.get("/categories")
async def get_knowledge_categories():
    """获取知识库分类"""
    categories = [
        {
            "id": "civil_law",
            "name": "民法",
            "description": "民事法律条文和案例",
            "color": "#1890ff"
        },
        {
            "id": "criminal_law", 
            "name": "刑法",
            "description": "刑事法律条文和案例",
            "color": "#ff4d4f"
        },
        {
            "id": "administrative_law",
            "name": "行政法",
            "description": "行政法律条文和案例", 
            "color": "#52c41a"
        },
        {
            "id": "commercial_law",
            "name": "商法",
            "description": "商事法律条文和案例",
            "color": "#faad14"
        },
        {
            "id": "labor_law",
            "name": "劳动法",
            "description": "劳动法律条文和案例",
            "color": "#722ed1"
        },
        {
            "id": "intellectual_property",
            "name": "知识产权法",
            "description": "知识产权法律条文和案例",
            "color": "#13c2c2"
        },
        {
            "id": "international_law",
            "name": "国际法",
            "description": "国际法律条文和案例",
            "color": "#eb2f96"
        },
        {
            "id": "environmental_law",
            "name": "环境法",
            "description": "环境法律条文和案例",
            "color": "#52c41a"
        }
    ]
    
    return {"categories": categories}

@router.get("/export")
async def export_knowledge(
    category: Optional[str] = None,
    format: str = "json",
    current_user: dict = Depends(get_current_user)
):
    """导出知识库数据"""
    try:
        # 这里实现知识库数据导出逻辑
        export_data = {
            "export_id": f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "format": format,
            "category": category,
            "status": "processing",
            "download_url": f"/api/knowledge-management/download/{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "estimated_completion": "5-10分钟"
        }
        
        return export_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")
