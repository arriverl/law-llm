"""
AI模型集成模块
集成DeepSeek R1和BERT机制
"""
import torch
import numpy as np
from transformers import (
    AutoTokenizer, 
    AutoModel, 
    BertTokenizer, 
    BertModel,
    pipeline
)
from typing import List, Dict, Any, Optional
import openai
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging

from ..core.config import settings

logger = logging.getLogger(__name__)

class LegalAIModel:
    """法律AI模型集成类"""
    
    def __init__(self):
        self.deepseek_client = None
        self.bert_tokenizer = None
        self.bert_model = None
        self.legal_classifier = None
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    async def initialize(self):
        """初始化AI模型"""
        try:
            # 初始化DeepSeek客户端
            if settings.DEEPSEEK_API_KEY:
                openai.api_key = settings.DEEPSEEK_API_KEY
                openai.api_base = settings.DEEPSEEK_BASE_URL
                self.deepseek_client = openai
                logger.info("DeepSeek R1模型初始化成功")
            
            # 初始化BERT模型
            await self._load_bert_model()
            
            # 初始化法律分类器
            await self._load_legal_classifier()
            
            logger.info("所有AI模型初始化完成")
            
        except Exception as e:
            logger.error(f"AI模型初始化失败: {e}")
            raise
    
    async def _load_bert_model(self):
        """加载BERT模型"""
        try:
            self.bert_tokenizer = BertTokenizer.from_pretrained('bert-base-chinese')
            self.bert_model = BertModel.from_pretrained('bert-base-chinese')
            self.bert_model.eval()
            logger.info("BERT模型加载成功")
        except Exception as e:
            logger.error(f"BERT模型加载失败: {e}")
    
    async def _load_legal_classifier(self):
        """加载法律分类器"""
        try:
            # 使用预训练的法律分类模型
            self.legal_classifier = pipeline(
                "text-classification",
                model="hfl/chinese-legal-electra-base",
                tokenizer="hfl/chinese-legal-electra-base"
            )
            logger.info("法律分类器加载成功")
        except Exception as e:
            logger.error(f"法律分类器加载失败: {e}")
    
    async def generate_legal_response(self, question: str, context: str = "") -> Dict[str, Any]:
        """生成法律咨询回复"""
        try:
            # 1. 使用BERT进行意图识别和分类
            intent_result = await self._analyze_intent_with_bert(question)
            
            # 2. 使用DeepSeek R1生成回复
            response = await self._generate_with_deepseek(question, context, intent_result)
            
            # 3. 后处理和质量评估
            processed_response = await self._post_process_response(response, intent_result)
            
            return {
                "answer": processed_response["content"],
                "confidence": processed_response["confidence"],
                "category": intent_result["category"],
                "intent": intent_result["intent"],
                "sources": processed_response.get("sources", []),
                "model_version": "DeepSeek-R1-BERT-Hybrid"
            }
            
        except Exception as e:
            logger.error(f"生成法律回复失败: {e}")
            return {
                "answer": "抱歉，我暂时无法处理您的法律问题，请稍后再试。",
                "confidence": 0.0,
                "category": "unknown",
                "intent": "unknown",
                "sources": [],
                "error": str(e)
            }
    
    async def _analyze_intent_with_bert(self, text: str) -> Dict[str, Any]:
        """使用BERT分析用户意图"""
        try:
            # 使用BERT进行文本编码
            inputs = self.bert_tokenizer(text, return_tensors="pt", max_length=512, truncation=True)
            
            with torch.no_grad():
                outputs = self.bert_model(**inputs)
                # 获取[CLS]标记的表示
                cls_embedding = outputs.last_hidden_state[:, 0, :].numpy()
            
            # 使用法律分类器进行分类
            if self.legal_classifier:
                classification_result = self.legal_classifier(text)
                category = classification_result[0]["label"]
                confidence = classification_result[0]["score"]
            else:
                category = "general"
                confidence = 0.5
            
            return {
                "category": category,
                "confidence": float(confidence),
                "intent": "legal_consultation",
                "embedding": cls_embedding.tolist()
            }
            
        except Exception as e:
            logger.error(f"BERT意图分析失败: {e}")
            return {
                "category": "general",
                "confidence": 0.0,
                "intent": "unknown",
                "embedding": []
            }
    
    async def _generate_with_deepseek(self, question: str, context: str, intent_result: Dict) -> str:
        """使用DeepSeek R1生成回复"""
        try:
            if not self.deepseek_client:
                return "DeepSeek服务暂不可用"
            
            # 构建提示词
            system_prompt = f"""
            你是一个专业的法律AI助手，具备以下能力：
            1. 提供准确的法律咨询和建议
            2. 分析法律条文和案例
            3. 协助处理法律文档
            4. 提供法律风险评估
            
            当前问题分类：{intent_result.get('category', 'general')}
            请基于专业法律知识回答用户问题。
            """
            
            user_prompt = f"""
            问题：{question}
            
            {f"上下文：{context}" if context else ""}
            
            请提供专业、准确的法律建议。
            """
            
            response = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: self.deepseek_client.ChatCompletion.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=settings.MAX_TOKENS,
                    temperature=settings.TEMPERATURE
                )
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"DeepSeek生成失败: {e}")
            return "抱歉，AI服务暂时不可用，请稍后再试。"
    
    async def _post_process_response(self, response: str, intent_result: Dict) -> Dict[str, Any]:
        """后处理回复内容"""
        try:
            # 计算置信度
            confidence = intent_result.get("confidence", 0.5)
            
            # 提取可能的法律条文引用
            sources = self._extract_legal_sources(response)
            
            # 质量检查
            quality_score = self._assess_response_quality(response)
            
            return {
                "content": response,
                "confidence": min(confidence * quality_score, 1.0),
                "sources": sources,
                "quality_score": quality_score
            }
            
        except Exception as e:
            logger.error(f"后处理失败: {e}")
            return {
                "content": response,
                "confidence": 0.5,
                "sources": [],
                "quality_score": 0.5
            }
    
    def _extract_legal_sources(self, text: str) -> List[str]:
        """提取法律条文引用"""
        # 简化的法律条文提取逻辑
        sources = []
        # 这里可以实现更复杂的法律条文识别逻辑
        return sources
    
    def _assess_response_quality(self, response: str) -> float:
        """评估回复质量"""
        # 简化的质量评估逻辑
        if len(response) < 50:
            return 0.3
        elif "抱歉" in response or "无法" in response:
            return 0.4
        else:
            return 0.8

# 全局AI模型实例
legal_ai_model = LegalAIModel()






