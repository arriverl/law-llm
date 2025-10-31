#!/usr/bin/env python3
"""
数据库初始化脚本
创建数据库表结构和初始数据
"""
import os
import sys
import asyncio
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.database import init_db, SessionLocal, User, KnowledgeBase, EcosystemPartner
from backend.app.core.security import get_password_hash
from backend.app.services.knowledge_builder import knowledge_builder

def create_admin_user():
    """创建管理员用户"""
    db = SessionLocal()
    try:
        # 检查是否已存在管理员用户
        admin_user = db.query(User).filter(User.username == "admin").first()
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
        
        db.add(admin_user)
        db.commit()
        
        print("管理员用户创建成功")
        print("用户名: admin")
        print("密码: admin123")
        
    except Exception as e:
        print(f"创建管理员用户失败: {e}")
        db.rollback()
    finally:
        db.close()

def create_demo_users():
    """创建演示用户"""
    db = SessionLocal()
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
            existing_user = db.query(User).filter(User.username == user_data["username"]).first()
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
            
            db.add(user)
            print(f"用户 {user_data['username']} 创建成功")
        
        db.commit()
        print("演示用户创建完成")
        
    except Exception as e:
        print(f"创建演示用户失败: {e}")
        db.rollback()
    finally:
        db.close()

def create_demo_knowledge():
    """创建演示知识库数据"""
    db = SessionLocal()
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
                "version": "1.0"
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
                "version": "1.0"
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
                "version": "1.0"
            }
        ]
        
        for knowledge_data in demo_knowledge:
            # 检查知识条目是否已存在
            existing = db.query(KnowledgeBase).filter(
                KnowledgeBase.title == knowledge_data["title"]
            ).first()
            if existing:
                print(f"知识条目 {knowledge_data['title']} 已存在")
                continue
            
            # 创建知识条目
            knowledge_item = KnowledgeBase(
                title=knowledge_data["title"],
                content=knowledge_data["content"],
                category=knowledge_data["category"],
                tags=knowledge_data["tags"],
                source=knowledge_data["source"],
                version=knowledge_data["version"]
            )
            
            db.add(knowledge_item)
            print(f"知识条目 {knowledge_data['title']} 创建成功")
        
        db.commit()
        print("演示知识库数据创建完成")
        
    except Exception as e:
        print(f"创建演示知识库数据失败: {e}")
        db.rollback()
    finally:
        db.close()

def create_demo_partners():
    """创建演示生态合作伙伴"""
    db = SessionLocal()
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
                "status": "active"
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
                "status": "active"
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
                "status": "active"
            }
        ]
        
        for partner_data in demo_partners:
            # 检查合作伙伴是否已存在
            existing = db.query(EcosystemPartner).filter(
                EcosystemPartner.name == partner_data["name"]
            ).first()
            if existing:
                print(f"合作伙伴 {partner_data['name']} 已存在")
                continue
            
            # 创建合作伙伴
            partner = EcosystemPartner(
                name=partner_data["name"],
                type=partner_data["type"],
                region=partner_data["region"],
                contact_info=partner_data["contact_info"],
                services=partner_data["services"],
                status=partner_data["status"]
            )
            
            db.add(partner)
            print(f"合作伙伴 {partner_data['name']} 创建成功")
        
        db.commit()
        print("演示生态合作伙伴创建完成")
        
    except Exception as e:
        print(f"创建演示生态合作伙伴失败: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """主函数"""
    print("开始初始化数据库...")
    
    try:
        # 1. 创建管理员用户
        print("\n1. 创建管理员用户...")
        create_admin_user()
        
        # 2. 创建演示用户
        print("\n2. 创建演示用户...")
        create_demo_users()
        
        # 3. 创建演示知识库数据
        print("\n3. 创建演示知识库数据...")
        create_demo_knowledge()
        
        # 4. 创建演示生态合作伙伴
        print("\n4. 创建演示生态合作伙伴...")
        create_demo_partners()
        
        print("\n数据库初始化完成!")
        print("\n系统访问信息:")
        print("后端API: http://localhost:8000")
        print("前端界面: http://localhost:3000")
        print("API文档: http://localhost:8000/docs")
        
        print("\n默认用户账号:")
        print("管理员: admin / admin123")
        print("律师: lawyer1 / lawyer123")
        print("企业: enterprise1 / enterprise123")
        print("用户: user1 / user123")
        
    except Exception as e:
        print(f"数据库初始化失败: {e}")

if __name__ == "__main__":
    main()






