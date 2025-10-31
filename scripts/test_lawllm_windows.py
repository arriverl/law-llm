#!/usr/bin/env python3
"""
测试 LawLLM-7B 模型集成 - Windows兼容版本
"""
import os
import sys
import asyncio
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.services.lawllm_service_windows import LawLLMServiceWindows

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_lawllm_windows():
    """测试 LawLLM-7B 模型 - Windows兼容版本"""
    logger.info("🧪 开始测试 LawLLM-7B 模型 (Windows兼容版本)")
    logger.info("=" * 60)
    
    try:
        # 1. 初始化服务
        logger.info("1. 初始化 LawLLM-7B 服务...")
        service = LawLLMServiceWindows()
        service.initialize()
        
        # 2. 测试法律咨询
        logger.info("\n2. 测试法律咨询...")
        test_questions = [
            "生产销售假冒伪劣商品罪如何判刑？",
            "劳动合同解除需要什么条件？",
            "知识产权侵权如何维权？",
            "公司股东有哪些权利？",
            "环境污染的法律责任是什么？"
        ]
        
        for i, question in enumerate(test_questions, 1):
            logger.info(f"\n问题 {i}: {question}")
            response = service.legal_consultation(question)
            logger.info(f"回答: {response['answer'][:200]}...")
            logger.info(f"置信度: {response['confidence']:.2f}")
        
        # 3. 测试法律分析
        logger.info("\n3. 测试法律案例分析...")
        case_text = """
        某公司员工张某在工作期间受伤，公司拒绝支付医疗费用。
        张某要求公司承担工伤责任，但公司认为张某违反安全规定导致受伤。
        请分析此案例的法律关系和可能的法律后果。
        """
        
        analysis = service.legal_analysis(case_text)
        logger.info(f"案例分析: {analysis['analysis'][:200]}...")
        logger.info(f"置信度: {analysis['confidence']:.2f}")
        
        # 4. 测试法律文档审查
        logger.info("\n4. 测试法律文档审查...")
        document_text = """
        本合同约定甲方应向乙方支付服务费用，但未明确支付时间和方式。
        合同还约定如发生争议，双方应友好协商解决。
        """
        
        review = service.legal_document_review(document_text)
        logger.info(f"文档审查: {review['review'][:200]}...")
        logger.info(f"置信度: {review['confidence']:.2f}")
        
        # 5. 测试法律研究
        logger.info("\n5. 测试法律研究...")
        research_topic = "粤港澳大湾区法律一体化发展研究"
        
        research = service.legal_research(research_topic)
        logger.info(f"研究报告: {research['research_report'][:200]}...")
        logger.info(f"置信度: {research['confidence']:.2f}")
        
        # 6. 测试批量咨询
        logger.info("\n6. 测试批量咨询...")
        batch_questions = [
            "什么是合同？",
            "如何申请专利？",
            "劳动法保护哪些权益？"
        ]
        
        batch_results = service.batch_consultation(batch_questions)
        logger.info(f"批量咨询结果: {len(batch_results)} 条")
        for result in batch_results:
            logger.info(f"  - {result['question']}: {result['answer'][:100]}...")
        
        # 7. 获取模型信息
        logger.info("\n7. 获取模型信息...")
        model_info = service.get_model_info()
        logger.info(f"模型名称: {model_info['model_name']}")
        logger.info(f"是否已初始化: {model_info['is_initialized']}")
        logger.info(f"设备: {model_info['device']}")
        logger.info(f"版本: {model_info['version']}")
        
        logger.info("\n🎉 LawLLM-7B 模型测试完成 (Windows兼容版本)!")
        logger.info("✅ 所有功能测试通过")
        
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_lawllm_windows())






