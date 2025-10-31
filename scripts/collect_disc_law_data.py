#!/usr/bin/env python3
"""
基于DISC-LawLLM架构的粤港澳大湾区法律数据收集脚本
参考: https://github.com/FudanDISC/DISC-LawLLM
"""
import os
import sys
import asyncio
import requests
from bs4 import BeautifulSoup
import json
import time
import logging
from datetime import datetime
from typing import List, Dict, Any, Tuple
import pandas as pd
import jieba
from collections import Counter

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DISCLawDataCollector:
    """基于DISC-LawLLM架构的法律数据收集器"""
    
    def __init__(self, output_dir="data/disc_law_data"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 设置请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        self.collected_data = []
        
        # 粤港澳大湾区法律分类体系（参考DISC-LawLLM）
        self.legal_categories = {
            "民事": {
                "keywords": ["合同", "协议", "履行", "违约", "赔偿", "债务", "财产", "婚姻", "继承", "离婚", "抚养"],
                "subcategories": ["合同法", "婚姻法", "继承法", "物权法", "侵权法"]
            },
            "刑事": {
                "keywords": ["犯罪", "刑罚", "刑事", "起诉", "判决", "量刑", "盗窃", "抢劫", "故意伤害", "诈骗"],
                "subcategories": ["刑法总则", "刑法分则", "刑事诉讼法", "刑事执行"]
            },
            "行政": {
                "keywords": ["行政", "政府", "处罚", "复议", "许可", "审批", "执法", "监管", "行政处罚"],
                "subcategories": ["行政法", "行政诉讼法", "行政复议法", "行政许可法"]
            },
            "商事": {
                "keywords": ["公司", "股东", "董事", "企业", "投资", "贸易", "股权", "并购", "破产"],
                "subcategories": ["公司法", "证券法", "保险法", "破产法", "海商法"]
            },
            "劳动": {
                "keywords": ["劳动", "员工", "工资", "社保", "工伤", "解雇", "加班", "休假", "劳动合同"],
                "subcategories": ["劳动法", "劳动合同法", "社会保险法", "劳动争议调解仲裁法"]
            },
            "知识产权": {
                "keywords": ["专利", "商标", "版权", "知识产权", "侵权", "发明", "创作", "著作权"],
                "subcategories": ["专利法", "商标法", "著作权法", "反不正当竞争法"]
            },
            "环境": {
                "keywords": ["环境", "污染", "保护", "生态", "排放", "治理", "可持续发展", "环保"],
                "subcategories": ["环境保护法", "大气污染防治法", "水污染防治法", "固体废物污染环境防治法"]
            },
            "国际": {
                "keywords": ["国际", "仲裁", "贸易", "投资", "合作", "条约", "外交", "国际法"],
                "subcategories": ["国际公法", "国际私法", "国际经济法", "国际商法"]
            },
            "金融": {
                "keywords": ["银行", "证券", "保险", "金融", "投资", "理财", "贷款", "信贷"],
                "subcategories": ["银行法", "证券法", "保险法", "信托法", "基金法"]
            },
            "其他": {
                "keywords": ["其他", "综合", "一般", "特殊"],
                "subcategories": ["其他法律", "综合法律", "特殊法律"]
            }
        }
    
    def collect_gba_court_data(self):
        """收集粤港澳大湾区法院数据"""
        logger.info("🏛️ 开始收集粤港澳大湾区法院数据...")
        
        # 粤港澳大湾区法院网站列表
        gba_courts = [
            {
                "name": "广东省高级人民法院",
                "url": "http://www.gdcourts.gov.cn/",
                "region": "广东",
                "selectors": {
                    "title": "h1, h2, h3, .title, .news-title, .article-title",
                    "content": "p, .content, .article-content, .news-content, .text"
                }
            },
            {
                "name": "深圳市中级人民法院",
                "url": "http://www.szcourt.gov.cn/",
                "region": "深圳",
                "selectors": {
                    "title": "h1, h2, h3, .title, .news-title, .article-title",
                    "content": "p, .content, .article-content, .news-content, .text"
                }
            },
            {
                "name": "广州市中级人民法院",
                "url": "http://www.gzcourt.gov.cn/",
                "region": "广州",
                "selectors": {
                    "title": "h1, h2, h3, .title, .news-title, .article-title",
                    "content": "p, .content, .article-content, .news-content, .text"
                }
            },
            {
                "name": "珠海市中级人民法院",
                "url": "http://www.zhcourt.gov.cn/",
                "region": "珠海",
                "selectors": {
                    "title": "h1, h2, h3, .title, .news-title, .article-title",
                    "content": "p, .content, .article-content, .news-content, .text"
                }
            },
            {
                "name": "佛山市中级人民法院",
                "url": "http://www.fscourt.gov.cn/",
                "region": "佛山",
                "selectors": {
                    "title": "h1, h2, h3, .title, .news-title, .article-title",
                    "content": "p, .content, .article-content, .news-content, .text"
                }
            },
            {
                "name": "东莞市中级人民法院",
                "url": "http://www.dgcourt.gov.cn/",
                "region": "东莞",
                "selectors": {
                    "title": "h1, h2, h3, .title, .news-title, .article-title",
                    "content": "p, .content, .article-content, .news-content, .text"
                }
            },
            {
                "name": "中山市中级人民法院",
                "url": "http://www.zscourt.gov.cn/",
                "region": "中山",
                "selectors": {
                    "title": "h1, h2, h3, .title, .news-title, .article-title",
                    "content": "p, .content, .article-content, .news-content, .text"
                }
            },
            {
                "name": "惠州市中级人民法院",
                "url": "http://www.hzcourt.gov.cn/",
                "region": "惠州",
                "selectors": {
                    "title": "h1, h2, h3, .title, .news-title, .article-title",
                    "content": "p, .content, .article-content, .news-content, .text"
                }
            },
            {
                "name": "江门市中级人民法院",
                "url": "http://www.jmcourt.gov.cn/",
                "region": "江门",
                "selectors": {
                    "title": "h1, h2, h3, .title, .news-title, .article-title",
                    "content": "p, .content, .article-content, .news-content, .text"
                }
            },
            {
                "name": "肇庆市中级人民法院",
                "url": "http://www.zqcourt.gov.cn/",
                "region": "肇庆",
                "selectors": {
                    "title": "h1, h2, h3, .title, .news-title, .article-title",
                    "content": "p, .content, .article-content, .news-content, .text"
                }
            }
        ]
        
        for court in gba_courts:
            try:
                logger.info(f"📡 正在收集: {court['name']} ({court['region']})")
                self._scrape_court_website(court)
                time.sleep(3)  # 避免请求过快
            except Exception as e:
                logger.error(f"收集失败 {court['name']}: {e}")
    
    def _scrape_court_website(self, court_config):
        """爬取单个法院网站"""
        try:
            response = requests.get(court_config['url'], timeout=15, headers=self.headers)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取标题和内容
            titles = soup.select(court_config['selectors']['title'])
            contents = soup.select(court_config['selectors']['content'])
            
            for title, content in zip(titles, contents):
                if title.text.strip() and content.text.strip():
                    # 使用DISC-LawLLM的分类方法
                    category, confidence = self._classify_legal_text(title.text.strip())
                    
                    data = {
                        "text": f"{title.text.strip()} {content.text.strip()}",
                        "title": title.text.strip(),
                        "content": content.text.strip(),
                        "source": court_config['name'],
                        "region": court_config['region'],
                        "category": category,
                        "confidence": confidence,
                        "timestamp": datetime.now().isoformat(),
                        "url": court_config['url'],
                        "word_count": len(title.text.strip() + content.text.strip()),
                        "keywords": self._extract_keywords(title.text.strip() + content.text.strip())
                    }
                    self.collected_data.append(data)
                    logger.info(f"✅ 收集到: {title.text.strip()[:50]}... (类别: {category})")
                    
        except Exception as e:
            logger.error(f"爬取失败 {court_config['name']}: {e}")
    
    def _classify_legal_text(self, text: str) -> Tuple[str, float]:
        """使用DISC-LawLLM方法分类法律文本"""
        text_lower = text.lower()
        category_scores = {}
        
        for category, info in self.legal_categories.items():
            score = 0
            keywords = info['keywords']
            
            # 计算关键词匹配分数
            for keyword in keywords:
                if keyword in text_lower:
                    score += 1
            
            # 计算子类别匹配分数
            for subcategory in info['subcategories']:
                if subcategory in text_lower:
                    score += 2
            
            category_scores[category] = score
        
        # 找到最高分的类别
        best_category = max(category_scores, key=category_scores.get)
        max_score = category_scores[best_category]
        
        # 计算置信度
        total_score = sum(category_scores.values())
        confidence = max_score / total_score if total_score > 0 else 0.0
        
        return best_category, confidence
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 使用jieba分词
        words = jieba.lcut(text)
        
        # 过滤停用词和短词
        stop_words = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'}
        keywords = [word for word in words if len(word) > 1 and word not in stop_words]
        
        # 返回最常见的10个关键词
        return [word for word, count in Counter(keywords).most_common(10)]
    
    def collect_legal_news(self):
        """收集法律新闻数据"""
        logger.info("📰 开始收集法律新闻数据...")
        
        # 法律新闻网站
        news_sites = [
            {
                "name": "中国法院网",
                "url": "http://www.chinacourt.org/",
                "selectors": {
                    "title": "h1, h2, h3, .title, .news-title, .article-title",
                    "content": "p, .content, .article-content, .news-content, .text"
                }
            },
            {
                "name": "法律图书馆",
                "url": "http://www.law-lib.com/",
                "selectors": {
                    "title": "h1, h2, h3, .title, .news-title, .article-title",
                    "content": "p, .content, .article-content, .news-content, .text"
                }
            },
            {
                "name": "中国法律网",
                "url": "http://www.chinalaw.com/",
                "selectors": {
                    "title": "h1, h2, h3, .title, .news-title, .article-title",
                    "content": "p, .content, .article-content, .news-content, .text"
                }
            }
        ]
        
        for site in news_sites:
            try:
                logger.info(f"📡 正在收集: {site['name']}")
                self._scrape_news_website(site)
                time.sleep(2)
            except Exception as e:
                logger.error(f"收集失败 {site['name']}: {e}")
    
    def _scrape_news_website(self, site_config):
        """爬取新闻网站"""
        try:
            response = requests.get(site_config['url'], timeout=15, headers=self.headers)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取标题和内容
            titles = soup.select(site_config['selectors']['title'])
            contents = soup.select(site_config['selectors']['content'])
            
            for title, content in zip(titles, contents):
                if title.text.strip() and content.text.strip():
                    # 使用DISC-LawLLM的分类方法
                    category, confidence = self._classify_legal_text(title.text.strip())
                    
                    data = {
                        "text": f"{title.text.strip()} {content.text.strip()}",
                        "title": title.text.strip(),
                        "content": content.text.strip(),
                        "source": site_config['name'],
                        "region": "粤港澳大湾区",
                        "category": category,
                        "confidence": confidence,
                        "timestamp": datetime.now().isoformat(),
                        "url": site_config['url'],
                        "word_count": len(title.text.strip() + content.text.strip()),
                        "keywords": self._extract_keywords(title.text.strip() + content.text.strip())
                    }
                    self.collected_data.append(data)
                    logger.info(f"✅ 收集到新闻: {title.text.strip()[:50]}... (类别: {category})")
                    
        except Exception as e:
            logger.error(f"爬取失败 {site_config['name']}: {e}")
    
    def create_training_data(self):
        """创建训练数据"""
        logger.info("📚 创建DISC-LawLLM训练数据...")
        
        # 创建训练数据
        training_data = []
        for item in self.collected_data:
            training_data.append({
                "text": item['text'],
                "label": self._get_category_id(item['category']),
                "category": item['category'],
                "confidence": item['confidence'],
                "source": item['source'],
                "region": item['region'],
                "keywords": item['keywords']
            })
        
        # 保存训练数据
        training_file = os.path.join(self.output_dir, "disc_law_training_data.json")
        with open(training_file, 'w', encoding='utf-8') as f:
            json.dump(training_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"训练数据已保存到: {training_file}")
        return training_data
    
    def _get_category_id(self, category: str) -> int:
        """获取类别ID"""
        category_list = list(self.legal_categories.keys())
        return category_list.index(category) if category in category_list else len(category_list) - 1
    
    def save_data(self):
        """保存收集的数据"""
        logger.info("💾 保存收集的数据...")
        
        # 保存为JSON格式
        json_file = os.path.join(self.output_dir, "disc_law_data.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.collected_data, f, ensure_ascii=False, indent=2)
        
        # 保存为CSV格式
        df = pd.DataFrame(self.collected_data)
        csv_file = os.path.join(self.output_dir, "disc_law_data.csv")
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        
        # 保存为TXT格式（用于BERT训练）
        txt_file = os.path.join(self.output_dir, "disc_law_data.txt")
        with open(txt_file, 'w', encoding='utf-8') as f:
            for item in self.collected_data:
                f.write(f"{item['text']}\n")
        
        logger.info(f"✅ 数据已保存到: {self.output_dir}")
        logger.info(f"📊 总共收集了 {len(self.collected_data)} 条数据")
        
        # 按地区统计
        region_stats = {}
        for item in self.collected_data:
            region = item.get('region', '未知')
            region_stats[region] = region_stats.get(region, 0) + 1
        
        logger.info("\n📈 按地区统计:")
        for region, count in region_stats.items():
            logger.info(f"  {region}: {count} 条")
        
        # 按类别统计
        category_stats = {}
        for item in self.collected_data:
            category = item.get('category', '未知')
            category_stats[category] = category_stats.get(category, 0) + 1
        
        logger.info("\n📈 按类别统计:")
        for category, count in category_stats.items():
            logger.info(f"  {category}: {count} 条")
        
        # 创建训练数据
        training_data = self.create_training_data()
        logger.info(f"📚 创建了 {len(training_data)} 条训练数据")

async def main():
    """主函数"""
    logger.info("🌏 基于DISC-LawLLM的粤港澳大湾区法律数据收集器")
    logger.info("=" * 60)
    
    collector = DISCLawDataCollector()
    
    try:
        # 1. 收集法院数据
        logger.info("\n1. 收集粤港澳大湾区法院数据...")
        collector.collect_gba_court_data()
        
        # 2. 收集法律新闻
        logger.info("\n2. 收集法律新闻...")
        collector.collect_legal_news()
        
        # 3. 保存数据
        logger.info("\n3. 保存数据...")
        collector.save_data()
        
        logger.info("\n🎉 数据收集完成!")
        logger.info(f"📁 数据保存在: {collector.output_dir}")
        
    except Exception as e:
        logger.error(f"数据收集失败: {e}")
    finally:
        logger.info("\n📊 收集统计:")
        logger.info(f"总数据量: {len(collector.collected_data)} 条")

if __name__ == "__main__":
    asyncio.run(main())






