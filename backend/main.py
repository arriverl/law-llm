"""
AI法律服务生态链系统 - 主服务入口
集成DeepSeek R1模型和BERT机制，实现法律智能服务
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import uvicorn
import os
from dotenv import load_dotenv

from app.database import init_db
from app.database_mongodb import init_mongodb, close_mongodb
from app.routers import auth, legal_ai, knowledge_base, ecosystem, analytics
from app.core.config import settings
from app.core.security import verify_token

load_dotenv()

# 安全令牌
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    await init_db()
    await init_mongodb()
    yield
    # 关闭时清理资源
    await close_mongodb()

# 创建FastAPI应用
app = FastAPI(
    title="AI法律服务生态链系统",
    description="基于DeepSeek R1和BERT的法律智能服务平台",
    version="1.0.0",
    lifespan=lifespan
)

# CORS中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 依赖注入：获取当前用户
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取当前认证用户"""
    token = credentials.credentials
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(legal_ai.router, prefix="/api/legal-ai", tags=["法律AI"])
app.include_router(knowledge_base.router, prefix="/api/knowledge", tags=["知识库"])
app.include_router(ecosystem.router, prefix="/api/ecosystem", tags=["生态管理"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["数据分析"])

@app.get("/")
async def root():
    """根路径健康检查"""
    return {
        "message": "AI法律服务生态链系统",
        "version": "1.0.0",
        "status": "运行中",
        "features": [
            "DeepSeek R1模型集成",
            "BERT掩码机制优化",
            "法律知识库管理",
            "生态协同网络",
            "智能合约部署"
        ]
    }

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "service": "AI法律服务生态链"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
