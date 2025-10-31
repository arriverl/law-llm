#!/usr/bin/env python3
"""
法律数据采集脚本
从各种来源采集法律数据，构建知识库
"""
import os
import sys
import requests
import time
import json
from datetime import datetime
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Any, Optional
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.database import SessionLocal, KnowledgeBase
from backend.app.services.data_collector import data_collector
from backend.app.services.knowledge_processor import knowledge_processor

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LegalDataCollector:
    """法律数据采集器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.db = SessionLocal()
    
    def collect_basic_laws(self):
        """采集基础法律条文"""
        logger.info("开始采集基础法律条文...")
        
        basic_laws = [
            {
                "title": "中华人民共和国民法典",
                "content": """
                第一条 为了保护民事主体的合法权益，调整民事关系，维护社会和经济秩序，适应中国特色社会主义发展要求，弘扬社会主义核心价值观，根据宪法，制定本法。
                
                第二条 民法调整平等主体的自然人、法人和非法人组织之间的人身关系和财产关系。
                
                第三条 民事主体的人身权利、财产权利以及其他合法权益受法律保护，任何组织或者个人不得侵犯。
                """,
                "category": "civil_law",
                "tags": ["民法典", "民事法律", "基础法律"],
                "source": "全国人大",
                "version": "2021.1.1"
            },
            {
                "title": "中华人民共和国刑法",
                "content": """
                第一条 为了惩罚犯罪，保护人民，根据宪法，结合我国同犯罪作斗争的具体经验及实际情况，制定本法。
                
                第二条 中华人民共和国刑法的任务，是用刑罚同一切犯罪行为作斗争，以保卫国家安全，保卫人民民主专政的政权和社会主义制度，保护国有财产和劳动群众集体所有的财产，保护公民私人所有的财产，保护公民的人身权利、民主权利和其他权利，维护社会秩序、经济秩序，保障社会主义建设事业的顺利进行。
                """,
                "category": "criminal_law",
                "tags": ["刑法", "刑事法律", "犯罪"],
                "source": "全国人大",
                "version": "2021.3.1"
            },
            {
                "title": "中华人民共和国行政诉讼法",
                "content": """
                第一条 为保证人民法院公正、及时审理行政案件，解决行政争议，保护公民、法人和其他组织的合法权益，监督行政机关依法行使职权，根据宪法，制定本法。
                
                第二条 公民、法人或者其他组织认为行政机关和行政机关工作人员的行政行为侵犯其合法权益，有权依照本法向人民法院提起诉讼。
                """,
                "category": "administrative_law",
                "tags": ["行政法", "行政诉讼", "程序法"],
                "source": "全国人大",
                "version": "2017.7.1"
            }
        ]
        
        for law in basic_laws:
            self._save_knowledge_item(law)
        
        logger.info(f"基础法律条文采集完成，共 {len(basic_laws)} 条")
    
    def collect_court_cases(self):
        """采集法院案例"""
        logger.info("开始采集法院案例...")
        
        # 模拟案例数据
        cases = [
            {
                "title": "合同纠纷典型案例 - 某公司与供应商采购合同纠纷案",
                "content": """
                案件事实：某公司与供应商签订采购合同，约定供应商提供原材料，公司支付货款。后因供应商提供的原材料存在质量问题，公司要求退货并要求赔偿损失。
                
                争议焦点：1. 供应商是否构成违约；2. 公司是否有权要求退货和赔偿。
                
                法院判决：供应商提供的原材料不符合合同约定的质量标准，构成违约。公司有权要求退货并要求供应商承担违约责任，赔偿因此造成的损失。
                
                法律依据：《民法典》第五百七十七条、第五百八十二条。
                """,
                "category": "civil_law",
                "tags": ["合同纠纷", "典型案例", "民事纠纷"],
                "source": "最高人民法院",
                "version": "2023.1"
            },
            {
                "title": "劳动争议处理案例 - 员工工资支付争议案",
                "content": """
                案件事实：员工与用人单位因工资支付问题产生争议，员工认为用人单位未按约定支付工资，用人单位认为员工工作表现不符合要求。
                
                争议焦点：1. 用人单位是否构成拖欠工资；2. 员工是否有权要求支付工资。
                
                仲裁裁决：用人单位应当按照劳动合同约定支付工资，不得以员工工作表现为由拖欠工资。用人单位应当支付员工工资及相应的经济补偿。
                
                法律依据：《劳动法》第五十条、《劳动合同法》第三十条。
                """,
                "category": "labor_law",
                "tags": ["劳动争议", "工资支付", "劳动法"],
                "source": "劳动仲裁委员会",
                "version": "2023.2"
            }
        ]
        
        for case in cases:
            self._save_knowledge_item(case)
        
        logger.info(f"法院案例采集完成，共 {len(cases)} 条")
    
    def collect_practical_docs(self):
        """采集实务文档"""
        logger.info("开始采集实务文档...")
        
        practical_docs = [
            {
                "title": "合同审查要点指南",
                "content": """
                合同审查是法律实务中的重要环节，需要注意以下要点：
                
                1. 合同主体审查
                   - 确认合同当事人的主体资格
                   - 检查营业执照、资质证书等
                   - 核实授权委托书
                
                2. 合同内容审查
                   - 合同条款是否完整
                   - 权利义务是否对等
                   - 违约责任是否明确
                
                3. 法律风险审查
                   - 是否存在违法条款
                   - 是否符合相关法规
                   - 是否存在法律漏洞
                
                4. 履行保障审查
                   - 履行期限是否合理
                   - 履行方式是否明确
                   - 争议解决机制是否完善
                """,
                "category": "commercial_law",
                "tags": ["合同审查", "实务指南", "商业法律"],
                "source": "律师事务所",
                "version": "2023.1"
            },
            {
                "title": "劳动争议处理流程指南",
                "content": """
                劳动争议处理需要按照法定程序进行，具体流程如下：
                
                1. 协商解决
                   - 双方协商解决争议
                   - 达成和解协议
                   - 避免进入法律程序
                
                2. 调解程序
                   - 申请劳动争议调解
                   - 调解委员会调解
                   - 达成调解协议
                
                3. 仲裁程序
                   - 申请劳动争议仲裁
                   - 仲裁委员会审理
                   - 作出仲裁裁决
                
                4. 诉讼程序
                   - 不服仲裁裁决可起诉
                   - 法院审理判决
                   - 执行判决结果
                """,
                "category": "labor_law",
                "tags": ["劳动争议", "处理流程", "劳动法"],
                "source": "劳动法律师",
                "version": "2023.1"
            }
        ]
        
        for doc in practical_docs:
            self._save_knowledge_item(doc)
        
        logger.info(f"实务文档采集完成，共 {len(practical_docs)} 条")
    
    def collect_from_websites(self):
        """从网站采集数据"""
        logger.info("开始从网站采集数据...")
        
        # 模拟网站数据采集
        websites = [
            {
                "name": "中国法院网",
                "url": "http://www.chinacourt.org",
                "type": "court_news"
            },
            {
                "name": "法制日报",
                "url": "http://www.legaldaily.com.cn",
                "type": "legal_news"
            }
        ]
        
        for website in websites:
            try:
                # 模拟采集网站数据
                collected_data = self._scrape_website(website)
                for item in collected_data:
                    self._save_knowledge_item(item)
                
                logger.info(f"从 {website['name']} 采集完成")
                time.sleep(1)  # 避免请求过于频繁
                
            except Exception as e:
                logger.error(f"从 {website['name']} 采集失败: {e}")
    
    def _scrape_website(self, website: Dict[str, str]) -> List[Dict[str, Any]]:
        """模拟网站数据采集"""
        # 这里实现具体的网站数据采集逻辑
        # 由于涉及版权和访问限制，这里提供模拟数据
        
        if website["type"] == "court_news":
            return [
                {
                    "title": f"来自{website['name']}的法院新闻",
                    "content": "这是从法院网站采集的新闻内容...",
                    "category": "court_news",
                    "tags": ["法院新闻", "法律资讯"],
                    "source": website["name"],
                    "version": "1.0"
                }
            ]
        elif website["type"] == "legal_news":
            return [
                {
                    "title": f"来自{website['name']}的法律新闻",
                    "content": "这是从法律网站采集的新闻内容...",
                    "category": "legal_news",
                    "tags": ["法律新闻", "法制资讯"],
                    "source": website["name"],
                    "version": "1.0"
                }
            ]
        
        return []
    
    def _save_knowledge_item(self, item: Dict[str, Any]):
        """保存知识条目"""
        try:
            # 检查是否已存在
            existing = self.db.query(KnowledgeBase).filter(
                KnowledgeBase.title == item["title"]
            ).first()
            
            if existing:
                logger.info(f"知识条目已存在: {item['title']}")
                return
            
            # 创建新知识条目
            knowledge_item = KnowledgeBase(
                title=item["title"],
                content=item["content"],
                category=item["category"],
                tags=item["tags"],
                source=item["source"],
                version=item["version"]
            )
            
            self.db.add(knowledge_item)
            self.db.commit()
            
            logger.info(f"知识条目保存成功: {item['title']}")
            
        except Exception as e:
            logger.error(f"保存知识条目失败: {e}")
            self.db.rollback()
    
    def process_collected_data(self):
        """处理采集的数据"""
        logger.info("开始处理采集的数据...")
        
        # 获取所有知识条目
        knowledge_items = self.db.query(KnowledgeBase).all()
        
        for item in knowledge_items:
            try:
                # 处理知识条目
                processed_data = knowledge_processor.process_legal_document(
                    item.content, 
                    item.category
                )
                
                # 更新处理结果
                if processed_data:
                    # 这里可以将处理结果保存到数据库
                    logger.info(f"处理完成: {item.title}")
                
            except Exception as e:
                logger.error(f"处理知识条目失败 {item.title}: {e}")
    
    def generate_statistics(self):
        """生成统计信息"""
        logger.info("生成统计信息...")
        
        # 统计各类知识条目数量
        categories = self.db.query(KnowledgeBase.category).distinct().all()
        
        stats = {}
        for category in categories:
            count = self.db.query(KnowledgeBase).filter(
                KnowledgeBase.category == category[0]
            ).count()
            stats[category[0]] = count
        
        total_count = self.db.query(KnowledgeBase).count()
        
        logger.info(f"知识库统计信息:")
        logger.info(f"总条目数: {total_count}")
        for category, count in stats.items():
            logger.info(f"{category}: {count} 条")
    
    def run_collection(self):
        """运行数据采集"""
        logger.info("开始法律数据采集...")
        
        try:
            # 1. 采集基础法律条文
            self.collect_basic_laws()
            
            # 2. 采集法院案例
            self.collect_court_cases()
            
            # 3. 采集实务文档
            self.collect_practical_docs()
            
            # 4. 从网站采集数据
            self.collect_from_websites()
            
            # 5. 处理采集的数据
            self.process_collected_data()
            
            # 6. 生成统计信息
            self.generate_statistics()
            
            logger.info("法律数据采集完成!")
            
        except Exception as e:
            logger.error(f"数据采集失败: {e}")
        finally:
            self.db.close()

def main():
    """主函数"""
    collector = LegalDataCollector()
    collector.run_collection()

if __name__ == "__main__":
    main()






