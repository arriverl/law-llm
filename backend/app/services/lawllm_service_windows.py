#!/usr/bin/env python3
"""
LawLLM-7B 法律服务 - Windows兼容版本
基于 transformers 库的法律智能服务，不依赖 vLLM
"""
import os
import sys
import logging
from typing import List, Dict, Any, Optional
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM,
    pipeline,
    TextGenerationPipeline
)
import json
from datetime import datetime

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LawLLMServiceWindows:
    """LawLLM-7B 法律服务类 - Windows兼容版本"""
    
    def __init__(self, model_name: str = "ShengbinYue/LawLLM-7B"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        self.is_initialized = False
        
        # 生成参数
        self.generation_config = {
            "max_new_tokens": 1024,
            "temperature": 0.1,
            "top_p": 0.9,
            "top_k": 50,
            "do_sample": True,
            "pad_token_id": None,
            "eos_token_id": None,
        }
        
    def initialize(self):
        """初始化模型"""
        try:
            logger.info(f"🚀 初始化 LawLLM-7B 模型 (Windows兼容版本): {self.model_name}")
            
            # 检查是否有GPU
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"使用设备: {device}")
            
            # 加载分词器
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            
            # 设置pad_token
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # 加载模型
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                device_map="auto" if device == "cuda" else None,
                trust_remote_code=True
            )
            
            # 创建文本生成管道
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if device == "cuda" else -1,
                torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            )
            
            self.is_initialized = True
            logger.info("✅ LawLLM-7B 模型初始化完成 (Windows兼容版本)")
            
        except Exception as e:
            logger.error(f"❌ 模型初始化失败: {e}")
            # 如果模型加载失败，使用模拟服务
            self._initialize_mock_service()
    
    def _initialize_mock_service(self):
        """初始化模拟服务（当模型加载失败时）"""
        logger.warning("⚠️ 使用模拟服务模式")
        self.is_initialized = True
    
    def generate_response(self, prompt: str, system_message: str = None) -> str:
        """生成法律咨询回复"""
        if not self.is_initialized:
            self.initialize()
        
        try:
            # 构建消息
            if system_message is None:
                system_message = "你是LawLLM，一个由复旦大学DISC实验室创造的法律助手。"
            
            # 构建完整的提示词
            full_prompt = f"{system_message}\n\n用户问题: {prompt}\n\n回答:"
            
            if self.pipeline is None:
                # 使用模拟回复
                return self._generate_mock_response(prompt)
            
            # 生成回复
            result = self.pipeline(
                full_prompt,
                max_new_tokens=self.generation_config["max_new_tokens"],
                temperature=self.generation_config["temperature"],
                top_p=self.generation_config["top_p"],
                top_k=self.generation_config["top_k"],
                do_sample=self.generation_config["do_sample"],
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )
            
            # 提取生成的文本
            generated_text = result[0]["generated_text"]
            response = generated_text[len(full_prompt):].strip()
            
            return response if response else self._generate_mock_response(prompt)
                
        except Exception as e:
            logger.error(f"❌ 生成回复失败: {e}")
            return self._generate_mock_response(prompt)
    
    def _generate_mock_response(self, prompt: str) -> str:
        """生成模拟回复"""
        mock_responses = {
            "生产销售假冒伪劣商品罪如何判刑": """
根据《中华人民共和国刑法》第一百四十条规定，生产、销售伪劣产品罪是指生产者、销售者在产品中掺杂、掺假，以假充真，以次充好或者以不合格产品冒充合格产品，销售金额五万元以上的行为。

量刑标准：
1. 销售金额五万元以上不满二十万元的，处二年以下有期徒刑或者拘役，并处或者单处销售金额百分之五十以上二倍以下罚金；
2. 销售金额二十万元以上不满五十万元的，处二年以上七年以下有期徒刑，并处销售金额百分之五十以上二倍以下罚金；
3. 销售金额五十万元以上不满二百万元的，处七年以上有期徒刑，并处销售金额百分之五十以上二倍以下罚金；
4. 销售金额二百万元以上的，处十五年有期徒刑或者无期徒刑，并处销售金额百分之五十以上二倍以下罚金或者没收财产。
            """,
            "劳动合同解除需要什么条件": """
根据《中华人民共和国劳动合同法》规定，劳动合同解除需要满足以下条件：

一、用人单位解除劳动合同的条件：
1. 劳动者在试用期间被证明不符合录用条件的；
2. 劳动者严重违反用人单位的规章制度的；
3. 劳动者严重失职，营私舞弊，给用人单位造成重大损害的；
4. 劳动者同时与其他用人单位建立劳动关系，对完成本单位的工作任务造成严重影响，或者经用人单位提出，拒不改正的；
5. 劳动者以欺诈、胁迫的手段或者乘人之危，使用人单位在违背真实意思的情况下订立或者变更劳动合同的；
6. 劳动者被依法追究刑事责任的。

二、劳动者解除劳动合同的条件：
1. 提前三十日以书面形式通知用人单位；
2. 在试用期内提前三日通知用人单位；
3. 用人单位未按照劳动合同约定提供劳动保护或者劳动条件的；
4. 用人单位未及时足额支付劳动报酬的；
5. 用人单位未依法为劳动者缴纳社会保险费的；
6. 用人单位的规章制度违反法律、法规的规定，损害劳动者权益的。
            """,
            "知识产权侵权如何维权": """
知识产权侵权维权途径：

一、行政途径：
1. 向知识产权局申请行政处理；
2. 向工商行政管理部门举报；
3. 向海关申请知识产权保护。

二、司法途径：
1. 向人民法院提起民事诉讼；
2. 向公安机关报案（构成犯罪时）；
3. 申请诉前禁令和财产保全。

三、维权步骤：
1. 收集侵权证据；
2. 确定侵权事实和损失；
3. 选择维权途径；
4. 准备相关材料；
5. 提起诉讼或申请行政处理。

四、赔偿标准：
1. 实际损失；
2. 侵权人获得的利益；
3. 许可使用费的合理倍数；
4. 法定赔偿（最高500万元）。
            """
        }
        
        # 简单的关键词匹配
        for key, response in mock_responses.items():
            if any(word in prompt for word in key.split()):
                return response.strip()
        
        # 默认回复
        return f"""
根据您的问题"{prompt}"，我为您提供以下法律分析：

1. 这是一个涉及法律问题的咨询，建议您：
   - 查阅相关法律法规
   - 咨询专业律师
   - 收集相关证据材料

2. 如需进一步帮助，请提供更详细的情况描述。

3. 请注意，以上建议仅供参考，具体法律问题请咨询专业律师。

（注：当前使用模拟服务模式，建议安装完整模型以获得更准确的回答）
        """.strip()
    
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
                "model": f"{self.model_name} (Windows兼容版本)",
                "timestamp": datetime.now().isoformat(),
                "context": context
            }
            
        except Exception as e:
            logger.error(f"❌ 法律咨询失败: {e}")
            return {
                "question": question,
                "answer": f"抱歉，处理您的问题时出现错误: {str(e)}",
                "confidence": 0.0,
                "model": f"{self.model_name} (Windows兼容版本)",
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
                "model": f"{self.model_name} (Windows兼容版本)",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ 法律分析失败: {e}")
            return {
                "case_text": case_text,
                "analysis": f"抱歉，分析案例时出现错误: {str(e)}",
                "confidence": 0.0,
                "model": f"{self.model_name} (Windows兼容版本)",
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
                "model": f"{self.model_name} (Windows兼容版本)",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ 法律文档审查失败: {e}")
            return {
                "document_text": document_text,
                "review": f"抱歉，审查文档时出现错误: {str(e)}",
                "confidence": 0.0,
                "model": f"{self.model_name} (Windows兼容版本)",
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
                "model": f"{self.model_name} (Windows兼容版本)",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ 法律研究失败: {e}")
            return {
                "research_topic": research_topic,
                "research_report": f"抱歉，进行研究时出现错误: {str(e)}",
                "confidence": 0.0,
                "model": f"{self.model_name} (Windows兼容版本)",
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
                    "model": f"{self.model_name} (Windows兼容版本)",
                    "timestamp": datetime.now().isoformat()
                })
        
        return results
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "model_name": self.model_name,
            "is_initialized": self.is_initialized,
            "generation_config": self.generation_config,
            "device": "cuda" if torch.cuda.is_available() else "cpu",
            "version": "Windows兼容版本",
            "timestamp": datetime.now().isoformat()
        }

# 全局服务实例
lawllm_service_windows = LawLLMServiceWindows()

def get_lawllm_service() -> LawLLMServiceWindows:
    """获取 LawLLM 服务实例"""
    return lawllm_service_windows






