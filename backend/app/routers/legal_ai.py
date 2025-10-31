"""
法律AI服务路由
提供智能法律咨询和分析功能
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import asyncio

from ..database import get_db, LegalConsultation, User
from ..models.ai_models import legal_ai_model
from ..services.lawllm_service_windows import get_lawllm_service
from .auth import get_current_user

router = APIRouter()

# 请求模型
class LegalQuestionRequest(BaseModel):
    question: str
    context: Optional[str] = None
    category: Optional[str] = None
    user_id: Optional[int] = None

class LegalAnalysisRequest(BaseModel):
    document_text: str
    analysis_type: str  # contract, case, regulation
    jurisdiction: Optional[str] = None

class BatchConsultationRequest(BaseModel):
    questions: List[str]
    batch_id: Optional[str] = None

# 响应模型
class LegalResponse(BaseModel):
    answer: str
    confidence: float
    category: str
    intent: str
    sources: List[str]
    model_version: str
    consultation_id: Optional[int] = None

class LegalAnalysisResponse(BaseModel):
    analysis_result: str
    risk_level: str
    recommendations: List[str]
    legal_issues: List[str]
    confidence: float

@router.post("/consult", response_model=LegalResponse)
async def legal_consultation(
    request: LegalQuestionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """法律咨询接口 - 使用 LawLLM-7B 模型"""
    try:
        # 获取 LawLLM 服务
        lawllm_service = get_lawllm_service()
        
        # 使用 LawLLM-7B 生成回复
        lawllm_response = lawllm_service.legal_consultation(
            question=request.question,
            context=request.context
        )
        
        # 保存咨询记录
        consultation = LegalConsultation(
            user_id=current_user.get("user_id"),
            question=request.question,
            answer=lawllm_response["answer"],
            category=request.category or "法律咨询",
            confidence_score=str(lawllm_response["confidence"]),
            status="completed",
            ai_model_version="LawLLM-7B"
        )
        
        db.add(consultation)
        db.commit()
        db.refresh(consultation)
        
        # 异步更新用户偏好
        background_tasks.add_task(
            update_user_preferences,
            current_user.get("user_id"),
            request.category or "法律咨询"
        )
        
        return LegalResponse(
            answer=lawllm_response["answer"],
            confidence=lawllm_response["confidence"],
            category=request.category or "法律咨询",
            intent="法律咨询",
            sources=["LawLLM-7B"],
            model_version="LawLLM-7B",
            consultation_id=consultation.id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"法律咨询处理失败: {str(e)}")

@router.post("/analyze", response_model=LegalAnalysisResponse)
async def legal_analysis(
    request: LegalAnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
    """法律文档分析 - 使用 LawLLM-7B 模型"""
    try:
        # 获取 LawLLM 服务
        lawllm_service = get_lawllm_service()
        
        # 使用 LawLLM-7B 进行法律分析
        lawllm_response = lawllm_service.legal_analysis(
            case_text=request.document_text
        )
        
        # 解析分析结果
        analysis_text = lawllm_response["analysis"]
        
        # 简单的风险等级评估
        risk_level = "低"
        if "高风险" in analysis_text or "严重" in analysis_text:
            risk_level = "高"
        elif "风险" in analysis_text or "问题" in analysis_text:
            risk_level = "中"
        
        # 提取建议和问题
        recommendations = []
        legal_issues = []
        
        if "建议" in analysis_text:
            recommendations.append("请参考分析结果中的建议")
        if "问题" in analysis_text or "风险" in analysis_text:
            legal_issues.append("请关注分析结果中提到的问题")
        
        return LegalAnalysisResponse(
            analysis_result=analysis_text,
            risk_level=risk_level,
            recommendations=recommendations,
            legal_issues=legal_issues,
            confidence=lawllm_response["confidence"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"法律分析失败: {str(e)}")

@router.post("/batch-consult")
async def batch_consultation(
    request: BatchConsultationRequest,
    current_user: dict = Depends(get_current_user)
):
    """批量法律咨询 - 使用 LawLLM-7B 模型"""
    try:
        # 获取 LawLLM 服务
        lawllm_service = get_lawllm_service()
        
        # 使用 LawLLM-7B 进行批量咨询
        lawllm_responses = lawllm_service.batch_consultation(request.questions)
        
        results = []
        for i, response in enumerate(lawllm_responses):
            results.append({
                "question": response["question"],
                "answer": response["answer"],
                "confidence": response["confidence"],
                "category": "法律咨询",
                "index": i
            })
        
        return {
            "batch_id": request.batch_id,
            "total_questions": len(request.questions),
            "results": results,
            "status": "completed",
            "model": "LawLLM-7B"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量咨询失败: {str(e)}")

@router.get("/consultations")
async def get_user_consultations(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取用户咨询历史"""
    consultations = db.query(LegalConsultation)\
        .filter(LegalConsultation.user_id == current_user.get("user_id"))\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return {
        "consultations": [
            {
                "id": c.id,
                "question": c.question,
                "answer": c.answer,
                "category": c.category,
                "confidence": c.confidence_score,
                "status": c.status,
                "created_at": c.created_at
            }
            for c in consultations
        ],
        "total": len(consultations)
    }

@router.get("/categories")
async def get_legal_categories():
    """获取法律领域分类"""
    categories = [
        {"id": "civil", "name": "民事法律", "description": "民事纠纷、合同、侵权等"},
        {"id": "criminal", "name": "刑事法律", "description": "刑事案件、刑法适用等"},
        {"id": "administrative", "name": "行政法律", "description": "行政行为、行政复议等"},
        {"id": "commercial", "name": "商事法律", "description": "公司法、证券法、金融法等"},
        {"id": "labor", "name": "劳动法律", "description": "劳动合同、劳动争议等"},
        {"id": "intellectual", "name": "知识产权", "description": "专利、商标、著作权等"},
        {"id": "international", "name": "国际法律", "description": "国际法、跨境贸易等"},
        {"id": "environmental", "name": "环境法律", "description": "环境保护、污染治理等"}
    ]
    
    return {"categories": categories}

@router.get("/model-status")
async def get_model_status():
    """获取AI模型状态 - LawLLM-7B"""
    try:
        # 获取 LawLLM 服务
        lawllm_service = get_lawllm_service()
        
        # 检查模型信息
        model_info = lawllm_service.get_model_info()
        
        return {
            "status": "active",
            "models": {
                "lawllm_7b": "available",
                "vllm_engine": "available",
                "legal_classifier": "available"
            },
            "model_info": model_info,
            "version": "2.0.0",
            "last_updated": "2024-01-01T00:00:00Z"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "models": {
                "lawllm_7b": "unavailable",
                "vllm_engine": "unavailable", 
                "legal_classifier": "unavailable"
            }
        }

async def update_user_preferences(user_id: int, category: str):
    """异步更新用户偏好"""
    # 这里可以实现用户偏好学习逻辑
    pass
