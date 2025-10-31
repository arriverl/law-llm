"""
MongoDB数据模型
使用MongoEngine定义法律知识库的数据结构
"""
from mongoengine import Document, EmbeddedDocument
from mongoengine.fields import StringField, EmailField, BooleanField, DateTimeField, IntField, FloatField, ListField, DictField, ObjectIdField, EmbeddedDocumentField, ReferenceField
from datetime import datetime
from typing import List, Dict, Any

class ContactInfo(EmbeddedDocument):
    """联系信息"""
    phone = StringField()
    email = StringField()
    address = StringField()
    website = StringField()

class User(Document):
    """用户模型"""
    username = StringField(required=True, unique=True, max_length=50)
    email = EmailField(required=True, unique=True)
    hashed_password = StringField(required=True, max_length=255)
    full_name = StringField(max_length=100)
    role = StringField(choices=['user', 'admin', 'lawyer', 'enterprise'], default='user')
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'users',
        'indexes': ['username', 'email', 'role']
    }

class LegalConsultation(Document):
    """法律咨询记录"""
    user_id = ObjectIdField(required=True)
    question = StringField(required=True)
    answer = StringField()
    category = StringField(max_length=50)
    confidence_score = FloatField()
    status = StringField(choices=['pending', 'completed', 'failed'], default='pending')
    ai_model_version = StringField(max_length=50)
    processing_time = FloatField()  # 处理时间（秒）
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'legal_consultations',
        'indexes': ['user_id', 'category', 'status', 'created_at']
    }

class LegalCase(Document):
    """法律案例"""
    user_id = ObjectIdField(required=True)
    case_title = StringField(required=True, max_length=200)
    case_description = StringField()
    case_type = StringField(max_length=50)
    jurisdiction = StringField(max_length=50)  # 司法管辖区
    case_data = DictField()  # 案例详细数据
    tags = ListField(StringField())
    source = StringField(max_length=100)
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'legal_cases',
        'indexes': ['user_id', 'case_type', 'jurisdiction', 'tags']
    }

class KnowledgeBase(Document):
    """法律知识库"""
    title = StringField(required=True, max_length=200)
    content = StringField(required=True)
    category = StringField(required=True, max_length=50)
    tags = ListField(StringField())
    source = StringField(max_length=100)
    version = StringField(max_length=20, default="1.0")
    is_active = BooleanField(default=True)
    
    # 结构化信息
    law_articles = ListField(DictField())  # 法律条文
    keywords = ListField(DictField())  # 关键词
    entities = ListField(DictField())  # 实体
    references = ListField(StringField())  # 引用
    
    # 元数据
    word_count = IntField()
    reading_time = IntField()  # 预计阅读时间（分钟）
    difficulty_level = StringField(choices=['beginner', 'intermediate', 'advanced'])
    
    # 统计信息
    view_count = IntField(default=0)
    like_count = IntField(default=0)
    share_count = IntField(default=0)
    
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'knowledge_base',
        'indexes': [
            'category',
            'tags',
            'is_active',
            'created_at',
            [('title', 'text'), ('content', 'text')]  # 文本搜索索引
        ]
    }

class EcosystemPartner(Document):
    """生态合作伙伴"""
    name = StringField(required=True, max_length=100)
    type = StringField(choices=['government', 'enterprise', 'law_firm', 'other'], required=True)
    region = StringField(max_length=50)
    contact_info = EmbeddedDocumentField(ContactInfo)
    services = ListField(StringField())
    status = StringField(choices=['active', 'inactive', 'pending'], default='active')
    
    # 合作信息
    cooperation_start_date = DateTimeField()
    cooperation_end_date = DateTimeField()
    cooperation_type = StringField(choices=['data_sharing', 'service_integration', 'joint_development'])
    
    # 统计信息
    data_sharing_volume = IntField(default=0)  # 数据共享量
    service_usage_count = IntField(default=0)  # 服务使用次数
    
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'ecosystem_partners',
        'indexes': ['type', 'region', 'status', 'created_at']
    }

class SmartContract(Document):
    """智能合约"""
    contract_id = StringField(required=True, unique=True)
    contract_type = StringField(required=True)
    parties = ListField(StringField())
    terms = DictField()
    jurisdiction = StringField(required=True)
    
    # 部署信息
    blockchain_network = StringField()
    contract_address = StringField()
    deployment_date = DateTimeField()
    deployment_status = StringField(choices=['pending', 'deployed', 'failed'])
    
    # 执行信息
    execution_count = IntField(default=0)
    last_execution = DateTimeField()
    
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'smart_contracts',
        'indexes': ['contract_type', 'jurisdiction', 'deployment_status']
    }

class DataSharing(Document):
    """数据共享记录"""
    sharing_id = StringField(required=True, unique=True)
    partner_id = ObjectIdField(required=True)
    data_type = StringField(required=True)
    sharing_level = StringField(choices=['public', 'restricted', 'confidential'], required=True)
    purpose = StringField(required=True)
    
    # 共享内容
    shared_data = DictField()
    data_size = IntField()  # 数据大小（字节）
    
    # 权限控制
    access_permissions = ListField(StringField())
    expiration_date = DateTimeField()
    
    # 使用统计
    access_count = IntField(default=0)
    last_accessed = DateTimeField()
    
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'data_sharing',
        'indexes': ['partner_id', 'data_type', 'sharing_level', 'created_at']
    }

class Analytics(Document):
    """分析数据"""
    date = DateTimeField(required=True)
    metric_type = StringField(required=True)  # 指标类型
    metric_name = StringField(required=True)  # 指标名称
    metric_value = FloatField(required=True)  # 指标值
    dimensions = DictField()  # 维度信息
    
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'analytics',
        'indexes': ['date', 'metric_type', 'metric_name']
    }

class SystemLog(Document):
    """系统日志"""
    level = StringField(choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], required=True)
    message = StringField(required=True)
    module = StringField()
    function = StringField()
    user_id = ObjectIdField()
    request_id = StringField()
    extra_data = DictField()
    
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'system_logs',
        'indexes': ['level', 'created_at', 'user_id']
    }
