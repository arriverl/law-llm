#!/usr/bin/env python3
"""
MongoDB数据库初始化脚本
创建数据库、集合和初始数据
"""
import os
import sys
import asyncio
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.database_mongodb import init_mongodb, close_mongodb
from backend.app.models.mongodb_models import (
    User, KnowledgeBase, EcosystemPartner, 
    LegalConsultation, SmartContract
)
from backend.app.core.security import get_password_hash

async def create_admin_user():
    """创建管理员用户"""
    try:
        # 检查是否已存在管理员用户
        admin_user = User.objects(username="admin").first()
        if admin_user:
            print("管理员用户已存在")
            return
        
        # 创建管理员用户
        admin_user = User(
            username="admin",
            email="admin@law-ai.com",
            hashed_password=get_password_hash("admin123"),
            full_name="系统管理员",
            role="admin",
            is_active=True
        )
        admin_user.save()
        
        print("✅ 管理员用户创建成功")
        print("用户名: admin")
        print("密码: admin123")
        
    except Exception as e:
        print(f"❌ 创建管理员用户失败: {e}")

async def create_demo_users():
    """创建演示用户"""
    try:
        demo_users = [
            {
                "username": "lawyer1",
                "email": "lawyer1@law-ai.com",
                "password": "lawyer123",
                "full_name": "张律师",
                "role": "lawyer"
            },
            {
                "username": "enterprise1",
                "email": "enterprise1@law-ai.com",
                "password": "enterprise123",
                "full_name": "某科技公司",
                "role": "enterprise"
            },
            {
                "username": "user1",
                "email": "user1@law-ai.com",
                "password": "user123",
                "full_name": "普通用户",
                "role": "user"
            }
        ]
        
        for user_data in demo_users:
            # 检查用户是否已存在
            existing_user = User.objects(username=user_data["username"]).first()
            if existing_user:
                print(f"用户 {user_data['username']} 已存在")
                continue
            
            # 创建用户
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                hashed_password=get_password_hash(user_data["password"]),
                full_name=user_data["full_name"],
                role=user_data["role"],
                is_active=True
            )
            user.save()
            print(f"✅ 用户 {user_data['username']} 创建成功")
        
        print("✅ 演示用户创建完成")
        
    except Exception as e:
        print(f"❌ 创建演示用户失败: {e}")

async def create_demo_knowledge():
    """创建演示知识库数据"""
    try:
        demo_knowledge = [
            {
                "title": "民法典合同编要点解析",
                "content": """
                民法典合同编是民事法律的重要组成部分，主要规定了合同的订立、履行、变更、解除等内容。
                
                主要特点：
                1. 保护合同当事人的合法权益
                2. 维护社会经济秩序
                3. 促进社会主义市场经济的发展
                
                重要条文：
                - 第四百六十九条：合同的内容由当事人约定
                - 第五百零九条：当事人应当按照约定全面履行自己的义务
                - 第五百六十三条：当事人一方迟延履行主要债务，经催告后在合理期限内仍未履行
                """,
                "category": "civil_law",
                "tags": ["民法典", "合同", "民事法律"],
                "source": "法律专家",
                "version": "1.0",
                "word_count": 150,
                "reading_time": 3,
                "difficulty_level": "intermediate"
            },
            {
                "title": "劳动争议处理实务指南",
                "content": """
                劳动争议处理是劳动法律实务中的重要内容，需要按照法定程序进行。
                
                处理程序：
                1. 协商解决：双方协商解决争议
                2. 调解程序：申请劳动争议调解
                3. 仲裁程序：申请劳动争议仲裁
                4. 诉讼程序：不服仲裁裁决可起诉
                
                注意事项：
                - 注意时效期间
                - 准备相关证据
                - 选择合适的解决方式
                """,
                "category": "labor_law",
                "tags": ["劳动争议", "处理程序", "劳动法"],
                "source": "劳动法律师",
                "version": "1.0",
                "word_count": 120,
                "reading_time": 2,
                "difficulty_level": "beginner"
            },
            {
                "title": "知识产权保护要点",
                "content": """
                知识产权保护是法律实务中的重要内容，涉及专利、商标、著作权等方面。
                
                保护范围：
                1. 专利权：发明、实用新型、外观设计
                2. 商标权：商品商标、服务商标
                3. 著作权：文学、艺术、科学作品
                
                保护措施：
                - 及时申请注册
                - 建立保护机制
                - 维护合法权益
                """,
                "category": "intellectual_property",
                "tags": ["知识产权", "专利", "商标", "著作权"],
                "source": "知识产权律师",
                "version": "1.0",
                "word_count": 100,
                "reading_time": 2,
                "difficulty_level": "intermediate"
            }
        ]
        
        for knowledge_data in demo_knowledge:
            # 检查知识条目是否已存在
            existing = KnowledgeBase.objects(title=knowledge_data["title"]).first()
            if existing:
                print(f"知识条目 {knowledge_data['title']} 已存在")
                continue
            
            # 创建知识条目
            knowledge_item = KnowledgeBase(**knowledge_data)
            knowledge_item.save()
            print(f"✅ 知识条目 {knowledge_data['title']} 创建成功")
        
        print("✅ 演示知识库数据创建完成")
        
    except Exception as e:
        print(f"❌ 创建演示知识库数据失败: {e}")

async def create_demo_partners():
    """创建演示生态合作伙伴"""
    try:
        demo_partners = [
            {
                "name": "某律师事务所",
                "type": "law_firm",
                "region": "GBA",
                "contact_info": {
                    "phone": "020-12345678",
                    "email": "contact@lawfirm.com",
                    "address": "广州市天河区"
                },
                "services": ["法律咨询", "合同审查", "诉讼代理"],
                "status": "active",
                "cooperation_type": "service_integration"
            },
            {
                "name": "某科技公司",
                "type": "enterprise",
                "region": "GBA",
                "contact_info": {
                    "phone": "0755-87654321",
                    "email": "contact@tech.com",
                    "address": "深圳市南山区"
                },
                "services": ["技术合作", "数据共享", "平台对接"],
                "status": "active",
                "cooperation_type": "data_sharing"
            },
            {
                "name": "某区政府",
                "type": "government",
                "region": "GBA",
                "contact_info": {
                    "phone": "020-11111111",
                    "email": "contact@gov.com",
                    "address": "广州市越秀区"
                },
                "services": ["政策支持", "监管协调", "公共服务"],
                "status": "active",
                "cooperation_type": "joint_development"
            }
        ]
        
        for partner_data in demo_partners:
            # 检查合作伙伴是否已存在
            existing = EcosystemPartner.objects(name=partner_data["name"]).first()
            if existing:
                print(f"合作伙伴 {partner_data['name']} 已存在")
                continue
            
            # 创建合作伙伴
            partner = EcosystemPartner(**partner_data)
            partner.save()
            print(f"✅ 合作伙伴 {partner_data['name']} 创建成功")
        
        print("✅ 演示生态合作伙伴创建完成")
        
    except Exception as e:
        print(f"❌ 创建演示生态合作伙伴失败: {e}")

async def create_demo_smart_contracts():
    """创建演示智能合约"""
    try:
        demo_contracts = [
            {
                "contract_id": "CONTRACT_001",
                "contract_type": "legal_service",
                "parties": ["system", "partners"],
                "terms": {
                    "version": "1.0",
                    "jurisdiction": "GBA",
                    "governance": "decentralized"
                },
                "jurisdiction": "GBA",
                "blockchain_network": "Ethereum",
                "deployment_status": "deployed"
            },
            {
                "contract_id": "CONTRACT_002",
                "contract_type": "data_sharing",
                "parties": ["partners", "government"],
                "terms": {
                    "version": "1.0",
                    "data_types": ["legal_knowledge", "case_data"],
                    "sharing_level": "restricted"
                },
                "jurisdiction": "GBA",
                "blockchain_network": "Ethereum",
                "deployment_status": "pending"
            }
        ]
        
        for contract_data in demo_contracts:
            # 检查智能合约是否已存在
            existing = SmartContract.objects(contract_id=contract_data["contract_id"]).first()
            if existing:
                print(f"智能合约 {contract_data['contract_id']} 已存在")
                continue
            
            # 创建智能合约
            contract = SmartContract(**contract_data)
            contract.save()
            print(f"✅ 智能合约 {contract_data['contract_id']} 创建成功")
        
        print("✅ 演示智能合约创建完成")
        
    except Exception as e:
        print(f"❌ 创建演示智能合约失败: {e}")

async def create_indexes():
    """创建数据库索引"""
    try:
        print("创建数据库索引...")
        
        # 为知识库创建文本搜索索引
        KnowledgeBase.objects()._collection.create_index([
            ("title", "text"),
            ("content", "text"),
            ("tags", "text")
        ])
        
        # 为用户创建索引
        User.objects()._collection.create_index("username")
        User.objects()._collection.create_index("email")
        
        # 为咨询记录创建索引
        LegalConsultation.objects()._collection.create_index([
            ("user_id", 1),
            ("created_at", -1)
        ])
        
        # 为生态合作伙伴创建索引
        EcosystemPartner.objects()._collection.create_index([
            ("type", 1),
            ("region", 1),
            ("status", 1)
        ])
        
        print("✅ 数据库索引创建完成")
        
    except Exception as e:
        print(f"❌ 创建数据库索引失败: {e}")

async def main():
    """主函数"""
    print("MongoDB数据库初始化")
    print("=" * 50)
    
    try:
        # 1. 初始化MongoDB连接
        print("1. 初始化MongoDB连接...")
        await init_mongodb()
        
        # 2. 创建管理员用户
        print("\n2. 创建管理员用户...")
        await create_admin_user()
        
        # 3. 创建演示用户
        print("\n3. 创建演示用户...")
        await create_demo_users()
        
        # 4. 创建演示知识库数据
        print("\n4. 创建演示知识库数据...")
        await create_demo_knowledge()
        
        # 5. 创建演示生态合作伙伴
        print("\n5. 创建演示生态合作伙伴...")
        await create_demo_partners()
        
        # 6. 创建演示智能合约
        print("\n6. 创建演示智能合约...")
        await create_demo_smart_contracts()
        
        # 7. 创建索引
        print("\n7. 创建数据库索引...")
        await create_indexes()
        
        print("\nMongoDB数据库初始化完成!")
        print("\n📋 系统访问信息:")
        print("  后端API: http://localhost:8000")
        print("  前端界面: http://localhost:3000")
        print("  API文档: http://localhost:8000/docs")
        
        print("\n👤 默认用户账号:")
        print("  管理员: admin / admin123")
        print("  律师: lawyer1 / lawyer123")
        print("  企业: enterprise1 / enterprise123")
        print("  用户: user1 / user123")
        
        print("\n🗄️ 数据库信息:")
        print("  数据库类型: MongoDB")
        print("  连接URL: mongodb://localhost:27017")
        print("  数据库名: law_ai_db")
        
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
    finally:
        await close_mongodb()

if __name__ == "__main__":
    asyncio.run(main())
