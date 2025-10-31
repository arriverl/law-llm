#!/usr/bin/env python3
"""
LawLLM-7B 法律服务
基于 ShengbinYue/LawLLM-7B 模型的法律智能服务
"""
import os
import sys
import logging
from typing import List, Dict, Any, Optional
import torch
from transformers import AutoTokenizer
from vllm import LLM, SamplingParams
import json
from datetime import datetime

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LawLLMService:
    """LawLLM-7B 法律服务类"""
    
    def __init__(self, model_name: str = "ShengbinYue/LawLLM-7B"):
        self.model_name = model_name
        self.llm = None
        self.tokenizer = None
        self.sampling_params = None
        self.is_initialized = False
        
    def initialize(self):
        """初始化模型"""
        try:
            logger.info(f"🚀 初始化 LawLLM-7B 模型: {self.model_name}")
            
            # 设置采样参数
            self.sampling_params = SamplingParams(
                temperature=0.1,
                top_p=0.9,
                top_k=50,
                max_tokens=4096
            )
            
            # 初始化 LLM
            self.llm = LLM(model=self.model_name)
            
            # 初始化分词器
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            self.is_initialized = True
            logger.info("✅ LawLLM-7B 模型初始化完成")
            
        except Exception as e:
            logger.error(f"❌ 模型初始化失败: {e}")
            raise
    
    def generate_response(self, prompt: str, system_message: str = None) -> str:
        """生成法律咨询回复"""
        if not self.is_initialized:
            self.initialize()
        
        try:
            # 构建消息
            if system_message is None:
                system_message = "你是LawLLM，一个由复旦大学DISC实验室创造的法律助手。"
            
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ]
            
            # 应用聊天模板
            text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            
            # 生成回复
            outputs = self.llm.generate([text], self.sampling_params)
            
            for output in outputs:
                generated_text = output.outputs[0].text
                return generated_text.strip()
                
        except Exception as e:
            logger.error(f"❌ 生成回复失败: {e}")
            return f"抱歉，生成回复时出现错误: {str(e)}"
    
    def legal_consultation(self, question: str, context: str = None) -> Dict[str, Any]:
        """法律咨询"""
        try:
            # 构建提示词
            if context:
                prompt = f"问题: {question}\n\n背景信息: {context}\n\n请提供详细的法律分析和建议。"
            else:
                prompt = question
            
            # 生成回复
            response = self.generate_response(prompt)
            
            # 分析回复质量
            confidence = self._analyze_response_quality(response)
            
            return {
                "question": question,
                "answer": response,
                "confidence": confidence,
                "model": self.model_name,
                "timestamp": datetime.now().isoformat(),
                "context": context
            }
            
        except Exception as e:
            logger.error(f"❌ 法律咨询失败: {e}")
            return {
                "question": question,
                "answer": f"抱歉，处理您的问题时出现错误: {str(e)}",
                "confidence": 0.0,
                "model": self.model_name,
                "timestamp": datetime.now().isoformat(),
                "context": context
            }
    
    def legal_analysis(self, case_text: str) -> Dict[str, Any]:
        """法律案例分析"""
        try:
            prompt = f"请分析以下法律案例，包括案件性质、适用法律、可能的法律后果等:\n\n{case_text}"
            
            response = self.generate_response(prompt)
            confidence = self._analyze_response_quality(response)
            
            return {
                "case_text": case_text,
                "analysis": response,
                "confidence": confidence,
                "model": self.model_name,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ 法律分析失败: {e}")
            return {
                "case_text": case_text,
                "analysis": f"抱歉，分析案例时出现错误: {str(e)}",
                "confidence": 0.0,
                "model": self.model_name,
                "timestamp": datetime.now().isoformat()
            }
    
    def legal_document_review(self, document_text: str) -> Dict[str, Any]:
        """法律文档审查"""
        try:
            prompt = f"请审查以下法律文档，指出潜在的法律风险、合规问题和改进建议:\n\n{document_text}"
            
            response = self.generate_response(prompt)
            confidence = self._analyze_response_quality(response)
            
            return {
                "document_text": document_text,
                "review": response,
                "confidence": confidence,
                "model": self.model_name,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ 法律文档审查失败: {e}")
            return {
                "document_text": document_text,
                "review": f"抱歉，审查文档时出现错误: {str(e)}",
                "confidence": 0.0,
                "model": self.model_name,
                "timestamp": datetime.now().isoformat()
            }
    
    def legal_research(self, research_topic: str) -> Dict[str, Any]:
        """法律研究"""
        try:
            prompt = f"请就以下法律研究主题提供详细的研究报告，包括相关法律条文、案例分析、学术观点等:\n\n{research_topic}"
            
            response = self.generate_response(prompt)
            confidence = self._analyze_response_quality(response)
            
            return {
                "research_topic": research_topic,
                "research_report": response,
                "confidence": confidence,
                "model": self.model_name,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ 法律研究失败: {e}")
            return {
                "research_topic": research_topic,
                "research_report": f"抱歉，进行研究时出现错误: {str(e)}",
                "confidence": 0.0,
                "model": self.model_name,
                "timestamp": datetime.now().isoformat()
            }
    
    def _analyze_response_quality(self, response: str) -> float:
        """分析回复质量"""
        try:
            # 简单的质量评估指标
            quality_score = 0.0
            
            # 长度检查
            if len(response) > 50:
                quality_score += 0.2
            
            # 法律关键词检查
            legal_keywords = ["法律", "法规", "条文", "规定", "条款", "案例", "判决", "法院", "律师", "诉讼"]
            keyword_count = sum(1 for keyword in legal_keywords if keyword in response)
            quality_score += min(keyword_count * 0.1, 0.4)
            
            # 结构检查
            if "。" in response and "，" in response:
                quality_score += 0.2
            
            # 完整性检查
            if len(response.split()) > 20:
                quality_score += 0.2
            
            return min(quality_score, 1.0)
            
        except Exception as e:
            logger.error(f"❌ 质量分析失败: {e}")
            return 0.5
    
    def batch_consultation(self, questions: List[str]) -> List[Dict[str, Any]]:
        """批量法律咨询"""
        results = []
        
        for question in questions:
            try:
                result = self.legal_consultation(question)
                results.append(result)
            except Exception as e:
                logger.error(f"❌ 批量咨询失败: {e}")
                results.append({
                    "question": question,
                    "answer": f"处理失败: {str(e)}",
                    "confidence": 0.0,
                    "model": self.model_name,
                    "timestamp": datetime.now().isoformat()
                })
        
        return results
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "model_name": self.model_name,
            "is_initialized": self.is_initialized,
            "sampling_params": {
                "temperature": self.sampling_params.temperature if self.sampling_params else None,
                "top_p": self.sampling_params.top_p if self.sampling_params else None,
                "top_k": self.sampling_params.top_k if self.sampling_params else None,
                "max_tokens": self.sampling_params.max_tokens if self.sampling_params else None
            },
            "timestamp": datetime.now().isoformat()
        }

# 全局服务实例
lawllm_service = LawLLMService()

def get_lawllm_service() -> LawLLMService:
    """获取 LawLLM 服务实例"""
    return lawllm_service






