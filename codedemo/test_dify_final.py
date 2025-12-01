#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试百度爬虫在dify环境中的最终兼容性
"""

import logging
from baidu_spider import BaiduSpider

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def test_dify_compatibility():
    """测试dify环境下的百度搜索功能"""
    try:
        logger.info("===== 开始测试dify环境兼容性 =====")
        
        # 创建百度爬虫实例
        spider = BaiduSpider()
        
        # 测试搜索关键词"成都"
        keyword = "成都"
        logger.info(f"搜索关键词: {keyword}")
        
        # 调用main方法模拟dify环境调用（传入arg1参数）
        result = spider.main("成都")
        
        # 打印结果
        logger.info(f"搜索状态: {result.get('status')}")
        logger.info(f"状态码: {result.get('status_code')}")
        logger.info(f"结果数量: {result.get('result_count')}")
        
        # 显示前3个结果
        results = result.get('results', [])
        if results:
            logger.info("\n前3个搜索结果:")
            for i, item in enumerate(results[:3], 1):
                logger.info(f"[{i}]")
                logger.info(f"标题: {item.get('title')}")
                logger.info(f"URL: {item.get('url')}")
                logger.info(f"摘要: {item.get('summary') or 'N/A'}")
                logger.info("")
        else:
            logger.warning("未找到搜索结果")
        
        logger.info("===== dify环境兼容性测试完成 =====")
        return result
        
    except Exception as e:
        logger.error(f"测试过程中出现错误: {str(e)}")
        return {"status": "error", "error_message": str(e)}

if __name__ == "__main__":
    test_dify_compatibility()