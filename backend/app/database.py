"""
数据库连接和模型定义
"""
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import redis
from contextlib import asynccontextmanager

from .core.config import settings

# 创建数据库引擎 - 仅在使用SQLAlchemy时创建
engine = None
SessionLocal = None

# 只有在使用SQLAlchemy时才创建引擎
if hasattr(settings, 'DATABASE_URL') and settings.DATABASE_URL:
    if "sqlite" in settings.DATABASE_URL:
        # SQLite配置
        engine = create_engine(
            settings.DATABASE_URL,
            poolclass=StaticPool,
            connect_args={"check_same_thread": False}
        )
    elif "postgresql" in settings.DATABASE_URL:
        # PostgreSQL配置
        engine = create_engine(
            settings.DATABASE_URL,
            poolclass=StaticPool
        )
    
    if engine:
        # 创建会话工厂
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()

# Redis连接
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

async def init_db():
    """初始化数据库"""
    # 只有在有SQLAlchemy引擎时才创建表
    if engine is not None:
        Base.metadata.create_all(bind=engine)
    
    # 初始化Redis连接
    try:
        redis_client.ping()
        print("Redis连接成功")
    except Exception as e:
        print(f"Redis连接失败: {e}")

def get_db():
    """获取数据库会话"""
    if SessionLocal is None:
        # 如果没有SQLAlchemy会话，返回None
        yield None
        return
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_redis():
    """获取Redis连接"""
    return redis_client

# 数据库模型
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(String(20), default="user")  # user, admin, lawyer, enterprise
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    consultations = relationship("LegalConsultation", back_populates="user")
    cases = relationship("LegalCase", back_populates="user")

class LegalConsultation(Base):
    """法律咨询记录"""
    __tablename__ = "legal_consultations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    question = Column(Text, nullable=False)
    answer = Column(Text)
    category = Column(String(50))  # 法律领域分类
    confidence_score = Column(String(10))  # AI回答置信度
    status = Column(String(20), default="pending")  # pending, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="consultations")

class LegalCase(Base):
    """法律案例"""
    __tablename__ = "legal_cases"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    case_title = Column(String(200), nullable=False)
    case_description = Column(Text)
    case_type = Column(String(50))
    jurisdiction = Column(String(50))  # 司法管辖区
    case_data = Column(JSON)  # 案例详细数据
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="cases")

class KnowledgeBase(Base):
    """法律知识库"""
    __tablename__ = "knowledge_base"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(50))
    tags = Column(JSON)  # 标签列表
    source = Column(String(100))  # 来源
    version = Column(String(20), default="1.0")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class EcosystemPartner(Base):
    """生态合作伙伴"""
    __tablename__ = "ecosystem_partners"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50))  # government, enterprise, law_firm
    region = Column(String(50))  # 地区
    contact_info = Column(JSON)
    services = Column(JSON)  # 提供的服务
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
