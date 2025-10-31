"""
法律知识处理器
对采集的法律数据进行清洗、标准化和结构化处理
"""
import re
import jieba
import jieba.posseg as pseg
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging
from collections import Counter
import hashlib

logger = logging.getLogger(__name__)

class LegalKnowledgeProcessor:
    """法律知识处理器"""
    
    def __init__(self):
        # 初始化jieba分词
        jieba.initialize()
        
        # 法律专业词汇
        self.legal_terms = [
            "合同", "侵权", "违约", "赔偿", "责任", "义务", "权利",
            "诉讼", "仲裁", "调解", "判决", "裁定", "执行",
            "民事", "刑事", "行政", "商事", "劳动", "婚姻", "继承",
            "知识产权", "专利", "商标", "著作权", "商业秘密"
        ]
        
        # 法律条文模式
        self.law_patterns = [
            r"第[一二三四五六七八九十百千万\d]+条",
            r"第[一二三四五六七八九十百千万\d]+款",
            r"第[一二三四五六七八九十百千万\d]+项",
            r"《[^》]+法》",
            r"《[^》]+条例》",
            r"《[^》]+规定》"
        ]
    
    def process_legal_document(self, content: str, doc_type: str = "general") -> Dict[str, Any]:
        """处理法律文档"""
        try:
            # 1. 文本清洗
            cleaned_content = self._clean_text(content)
            
            # 2. 提取法律条文
            law_articles = self._extract_law_articles(cleaned_content)
            
            # 3. 提取关键词
            keywords = self._extract_keywords(cleaned_content)
            
            # 4. 分类标签
            tags = self._classify_content(cleaned_content)
            
            # 5. 结构化信息
            structured_info = self._extract_structured_info(cleaned_content)
            
            return {
                "cleaned_content": cleaned_content,
                "law_articles": law_articles,
                "keywords": keywords,
                "tags": tags,
                "structured_info": structured_info,
                "processed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"文档处理失败: {e}")
            return {}
    
    def _clean_text(self, content: str) -> str:
        """清洗文本"""
        # 移除多余的空白字符
        content = re.sub(r'\s+', ' ', content)
        
        # 移除特殊字符
        content = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s，。！？；：""''（）【】《》]', '', content)
        
        # 标准化标点符号
        content = re.sub(r'，+', '，', content)
        content = re.sub(r'。+', '。', content)
        
        return content.strip()
    
    def _extract_law_articles(self, content: str) -> List[Dict[str, Any]]:
        """提取法律条文"""
        articles = []
        
        for pattern in self.law_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                article_text = match.group()
                start_pos = match.start()
                end_pos = match.end()
                
                # 提取条文内容
                article_content = self._extract_article_content(content, start_pos, end_pos)
                
                articles.append({
                    "article_text": article_text,
                    "content": article_content,
                    "position": (start_pos, end_pos),
                    "type": self._classify_article_type(article_text)
                })
        
        return articles
    
    def _extract_article_content(self, content: str, start_pos: int, end_pos: int) -> str:
        """提取条文内容"""
        # 从条文开始位置向后查找，直到遇到下一个条文或段落结束
        content_start = end_pos
        content_end = content_start + 200  # 限制长度
        
        # 查找句子结束位置
        sentence_end = content.find('。', content_start, content_end)
        if sentence_end != -1:
            content_end = sentence_end + 1
        
        return content[content_start:content_end].strip()
    
    def _classify_article_type(self, article_text: str) -> str:
        """分类条文类型"""
        if "条" in article_text:
            return "article"
        elif "款" in article_text:
            return "paragraph"
        elif "项" in article_text:
            return "item"
        elif "法" in article_text:
            return "law"
        elif "条例" in article_text:
            return "regulation"
        else:
            return "other"
    
    def _extract_keywords(self, content: str) -> List[Dict[str, Any]]:
        """提取关键词"""
        # 使用jieba分词
        words = jieba.lcut(content)
        
        # 过滤停用词和短词
        filtered_words = [
            word for word in words 
            if len(word) > 1 and word not in self._get_stop_words()
        ]
        
        # 统计词频
        word_freq = Counter(filtered_words)
        
        # 提取关键词
        keywords = []
        for word, freq in word_freq.most_common(20):
            keywords.append({
                "word": word,
                "frequency": freq,
                "is_legal_term": word in self.legal_terms
            })
        
        return keywords
    
    def _get_stop_words(self) -> set:
        """获取停用词列表"""
        return {
            "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一", "一个",
            "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好",
            "自己", "这", "那", "里", "来", "下", "过", "他", "她", "它", "们", "我们",
            "你们", "他们", "这个", "那个", "这些", "那些", "什么", "怎么", "为什么",
            "因为", "所以", "但是", "然后", "如果", "虽然", "而且", "或者", "还是"
        }
    
    def _classify_content(self, content: str) -> List[str]:
        """分类内容标签"""
        tags = []
        
        # 法律领域分类
        legal_domains = {
            "民事法律": ["合同", "侵权", "婚姻", "继承", "物权", "债权"],
            "刑事法律": ["犯罪", "刑罚", "刑法", "刑事", "罪名"],
            "行政法律": ["行政", "处罚", "许可", "复议", "诉讼"],
            "商事法律": ["公司", "证券", "金融", "保险", "破产"],
            "劳动法律": ["劳动", "工资", "社保", "工伤", "解雇"],
            "知识产权": ["专利", "商标", "著作权", "商业秘密", "版权"]
        }
        
        for domain, keywords in legal_domains.items():
            if any(keyword in content for keyword in keywords):
                tags.append(domain)
        
        # 文档类型分类
        doc_types = {
            "法律条文": ["第", "条", "款", "项", "法", "条例"],
            "案例判决": ["判决", "裁定", "案例", "法院", "审理"],
            "实务指南": ["流程", "步骤", "操作", "指南", "手册"],
            "政策文件": ["政策", "规定", "通知", "公告", "意见"]
        }
        
        for doc_type, keywords in doc_types.items():
            if any(keyword in content for keyword in keywords):
                tags.append(doc_type)
        
        return tags
    
    def _extract_structured_info(self, content: str) -> Dict[str, Any]:
        """提取结构化信息"""
        structured_info = {
            "entities": self._extract_entities(content),
            "dates": self._extract_dates(content),
            "numbers": self._extract_numbers(content),
            "references": self._extract_references(content)
        }
        
        return structured_info
    
    def _extract_entities(self, content: str) -> List[Dict[str, Any]]:
        """提取实体"""
        entities = []
        
        # 使用jieba进行词性标注
        words = pseg.cut(content)
        
        for word, flag in words:
            if flag in ['nr', 'ns', 'nt']:  # 人名、地名、机构名
                entities.append({
                    "text": word,
                    "type": self._map_pos_to_entity_type(flag),
                    "position": content.find(word)
                })
        
        return entities
    
    def _map_pos_to_entity_type(self, pos: str) -> str:
        """映射词性到实体类型"""
        mapping = {
            'nr': 'person',
            'ns': 'location', 
            'nt': 'organization'
        }
        return mapping.get(pos, 'other')
    
    def _extract_dates(self, content: str) -> List[str]:
        """提取日期"""
        date_patterns = [
            r'\d{4}年\d{1,2}月\d{1,2}日',
            r'\d{4}-\d{1,2}-\d{1,2}',
            r'\d{4}/\d{1,2}/\d{1,2}'
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, content)
            dates.extend(matches)
        
        return dates
    
    def _extract_numbers(self, content: str) -> List[Dict[str, Any]]:
        """提取数字"""
        number_patterns = [
            (r'\d+元', 'money'),
            (r'\d+万元', 'money'),
            (r'\d+年', 'year'),
            (r'\d+个月', 'month'),
            (r'\d+天', 'day')
        ]
        
        numbers = []
        for pattern, num_type in number_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                numbers.append({
                    "text": match.group(),
                    "type": num_type,
                    "position": match.start()
                })
        
        return numbers
    
    def _extract_references(self, content: str) -> List[str]:
        """提取引用"""
        reference_patterns = [
            r'《[^》]+》',
            r'第[一二三四五六七八九十百千万\d]+条',
            r'根据[^，。]+',
            r'依据[^，。]+'
        ]
        
        references = []
        for pattern in reference_patterns:
            matches = re.findall(pattern, content)
            references.extend(matches)
        
        return references
    
    def generate_summary(self, content: str, max_length: int = 200) -> str:
        """生成内容摘要"""
        try:
            # 简单的摘要生成：取前几个句子
            sentences = re.split(r'[。！？]', content)
            summary = ""
            
            for sentence in sentences:
                if len(summary + sentence) <= max_length:
                    summary += sentence + "。"
                else:
                    break
            
            return summary.strip()
            
        except Exception as e:
            logger.error(f"生成摘要失败: {e}")
            return content[:max_length] + "..."
    
    def calculate_similarity(self, content1: str, content2: str) -> float:
        """计算内容相似度"""
        try:
            # 简单的基于词汇重叠的相似度计算
            words1 = set(jieba.lcut(content1))
            words2 = set(jieba.lcut(content2))
            
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            
            if len(union) == 0:
                return 0.0
            
            return len(intersection) / len(union)
            
        except Exception as e:
            logger.error(f"计算相似度失败: {e}")
            return 0.0

# 全局知识处理器实例
knowledge_processor = LegalKnowledgeProcessor()






