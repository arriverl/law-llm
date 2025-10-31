"""
法律数据收集服务
从各种来源收集法律文本数据用于BERT训练
"""
import os
import json
import requests
from bs4 import BeautifulSoup
import time
import jieba
from typing import List, Dict, Any
import pandas as pd

class LegalDataCollector:
    """法律数据收集器"""
    
    def __init__(self):
        self.data_dir = "./data/training"
        self.collected_data = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
    def collect_from_websites(self):
        """从粤港澳大湾区法律网站收集数据"""
        print("🌐 开始从粤港澳大湾区法律网站收集数据...")
        
        # 粤港澳大湾区法律网站列表
        legal_sites = [
            {
                "name": "广东省高级人民法院",
                "url": "http://www.gdcourts.gov.cn/",
                "selectors": {
                    "title": "h1, h2, h3, .title",
                    "content": "p, .content, .article-content"
                },
                "region": "广东"
            },
            {
                "name": "深圳市中级人民法院",
                "url": "http://www.szcourt.gov.cn/",
                "selectors": {
                    "title": "h1, h2, h3, .title",
                    "content": "p, .content, .article-content"
                },
                "region": "深圳"
            },
            {
                "name": "广州市中级人民法院",
                "url": "http://www.gzcourt.gov.cn/",
                "selectors": {
                    "title": "h1, h2, h3, .title",
                    "content": "p, .content, .article-content"
                },
                "region": "广州"
            },
            {
                "name": "珠海市中级人民法院",
                "url": "http://www.zhcourt.gov.cn/",
                "selectors": {
                    "title": "h1, h2, h3, .title",
                    "content": "p, .content, .article-content"
                },
                "region": "珠海"
            },
            {
                "name": "佛山市中级人民法院",
                "url": "http://www.fscourt.gov.cn/",
                "selectors": {
                    "title": "h1, h2, h3, .title",
                    "content": "p, .content, .article-content"
                },
                "region": "佛山"
            },
            {
                "name": "东莞市中级人民法院",
                "url": "http://www.dgcourt.gov.cn/",
                "selectors": {
                    "title": "h1, h2, h3, .title",
                    "content": "p, .content, .article-content"
                },
                "region": "东莞"
            },
            {
                "name": "中山市中级人民法院",
                "url": "http://www.zscourt.gov.cn/",
                "selectors": {
                    "title": "h1, h2, h3, .title",
                    "content": "p, .content, .article-content"
                },
                "region": "中山"
            },
            {
                "name": "惠州市中级人民法院",
                "url": "http://www.hzcourt.gov.cn/",
                "selectors": {
                    "title": "h1, h2, h3, .title",
                    "content": "p, .content, .article-content"
                },
                "region": "惠州"
            },
            {
                "name": "江门市中级人民法院",
                "url": "http://www.jmcourt.gov.cn/",
                "selectors": {
                    "title": "h1, h2, h3, .title",
                    "content": "p, .content, .article-content"
                },
                "region": "江门"
            },
            {
                "name": "肇庆市中级人民法院",
                "url": "http://www.zqcourt.gov.cn/",
                "selectors": {
                    "title": "h1, h2, h3, .title",
                    "content": "p, .content, .article-content"
                },
                "region": "肇庆"
            }
        ]
        
        for site in legal_sites:
            try:
                print(f"📡 正在收集: {site['name']}")
                self._scrape_website(site)
                time.sleep(2)  # 避免请求过快
            except Exception as e:
                print(f"❌ 收集失败 {site['name']}: {e}")
    
    def _scrape_website(self, site_config):
        """爬取单个网站"""
        try:
            response = requests.get(site_config['url'], timeout=10, headers=self.headers)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取标题和内容
            titles = soup.select(site_config['selectors']['title'])
            contents = soup.select(site_config['selectors']['content'])
            
            for title, content in zip(titles, contents):
                if title.text.strip() and content.text.strip():
                    self.collected_data.append({
                        "text": f"{title.text.strip()} {content.text.strip()}",
                        "source": site_config['name'],
                        "region": site_config.get('region', '未知'),
                        "category": self._classify_text(title.text.strip()),
                        "timestamp": datetime.now().isoformat()
                    })
                    
        except Exception as e:
            print(f"❌ 爬取失败: {e}")
    
    def _classify_text(self, text: str) -> int:
        """简单的文本分类"""
        # 基于关键词的简单分类
        keywords = {
            0: ["合同", "协议", "履行", "违约"],  # 合同法
            1: ["劳动", "员工", "工资", "社保"],  # 劳动法
            2: ["专利", "商标", "版权", "知识产权"],  # 知识产权
            3: ["事故", "侵权", "赔偿", "责任"],  # 侵权法
            4: ["婚姻", "离婚", "财产", "抚养"],  # 婚姻法
            5: ["公司", "股东", "董事", "企业"],  # 公司法
            6: ["犯罪", "刑罚", "刑事", "起诉"],  # 刑法
            7: ["行政", "政府", "处罚", "复议"],  # 行政法
            8: ["国际", "仲裁", "贸易", "投资"],  # 国际法
            9: ["环境", "污染", "保护", "生态"]   # 环境法
        }
        
        for category, words in keywords.items():
            if any(word in text for word in words):
                return category
        
        return 0  # 默认分类
    
    def create_synthetic_data(self):
        """创建合成法律数据"""
        print("📝 创建合成法律数据...")
        
        # 法律文本模板
        templates = {
            0: [  # 合同法
                "根据《合同法》第{article}条规定，{subject}应当{action}",
                "合同双方应当按照约定{action}，否则承担{consequence}",
                "在{scenario}情况下，合同{result}"
            ],
            1: [  # 劳动法
                "用人单位应当为劳动者{action}，违反者承担{consequence}",
                "根据《劳动法》规定，{subject}享有{rights}",
                "在{scenario}情况下，劳动者可以{action}"
            ],
            2: [  # 知识产权法
                "侵犯他人{ip_type}权的，应当承担{consequence}",
                "根据《{law_name}》规定，{subject}享有{rights}",
                "在{scenario}情况下，{ip_type}权受到保护"
            ]
        }
        
        # 填充词汇
        fillers = {
            "article": ["四百六十九条", "五百零九条", "五百六十三条"],
            "subject": ["当事人", "合同双方", "用人单位", "劳动者"],
            "action": ["履行义务", "支付费用", "提供保障", "遵守约定"],
            "consequence": ["违约责任", "法律责任", "赔偿责任"],
            "scenario": ["合同履行", "劳动关系", "知识产权保护"],
            "result": ["有效", "无效", "可撤销"],
            "rights": ["合法权益", "基本权利", "法定权利"],
            "ip_type": ["专利", "商标", "著作权"],
            "law_name": ["专利法", "商标法", "著作权法"]
        }
        
        synthetic_data = []
        for category, template_list in templates.items():
            for template in template_list:
                # 生成多个变体
                for i in range(5):
                    text = template
                    for key, values in fillers.items():
                        if f"{{{key}}}" in text:
                            import random
                            text = text.replace(f"{{{key}}}", random.choice(values))
                    
                    synthetic_data.append({
                        "text": f"{text} - 变体{i+1}",
                        "category": category,
                        "source": "synthetic"
                    })
        
        self.collected_data.extend(synthetic_data)
        print(f"✅ 创建了 {len(synthetic_data)} 条合成数据")
    
    def process_data(self):
        """处理收集的数据"""
        print("🔧 处理收集的数据...")
        
        processed_data = []
        for item in self.collected_data:
            # 文本清洗
            text = self._clean_text(item['text'])
            if len(text) < 10:  # 过滤太短的文本
                continue
            
            # 分词处理
            words = jieba.lcut(text)
            
            processed_data.append({
                "text": text,
                "label": item.get('category', 0),
                "source": item.get('source', 'unknown'),
                "word_count": len(words)
            })
        
        self.collected_data = processed_data
        print(f"✅ 处理完成，共 {len(processed_data)} 条数据")
    
    def _clean_text(self, text: str) -> str:
        """清洗文本"""
        import re
        
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        
        # 移除特殊字符
        text = re.sub(r'[^\w\s\u4e00-\u9fff]', '', text)
        
        # 移除多余空格
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def save_data(self, filename: str = "legal_training_data.json"):
        """保存数据到文件"""
        os.makedirs(self.data_dir, exist_ok=True)
        filepath = os.path.join(self.data_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.collected_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 数据已保存到: {filepath}")
        
        # 生成统计报告
        self._generate_report()
    
    def _generate_report(self):
        """生成数据统计报告"""
        if not self.collected_data:
            return
        
        df = pd.DataFrame(self.collected_data)
        
        print("\n📊 数据统计报告:")
        print(f"总数据量: {len(df)}")
        print(f"平均文本长度: {df['word_count'].mean():.1f} 词")
        print("\n按类别分布:")
        print(df['label'].value_counts().sort_index())
        print("\n按来源分布:")
        print(df['source'].value_counts())

def main():
    """主函数"""
    print("🚀 开始收集法律训练数据...")
    
    collector = LegalDataCollector()
    
    # 1. 创建合成数据
    collector.create_synthetic_data()
    
    # 2. 从网站收集数据（可选）
    # collector.collect_from_websites()
    
    # 3. 处理数据
    collector.process_data()
    
    # 4. 保存数据
    collector.save_data()
    
    print("✅ 数据收集完成！")

if __name__ == "__main__":
    main()