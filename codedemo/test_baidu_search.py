#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试百度搜索功能
"""

from baidu_spider import BaiduSpider


def test_baidu_search():
    """
    测试百度搜索功能
    """
    print("=== 测试百度搜索功能 ===")
    
    # 创建百度爬虫实例
    spider = BaiduSpider()
    
    # 测试搜索关键词
    keyword = "成都"
    print(f"搜索关键词: {keyword}")
    
    # 执行搜索
    results = spider.search(keyword)
    
    # 输出搜索结果
    print(f"\n搜索状态: {results.get('status')}")
    print(f"状态码: {results.get('status_code')}")
    print(f"结果数量: {results.get('result_count', 0)}")
    
    # 输出详细结果
    if results.get('status') == 'success' and results.get('results'):
        print("\n=== 详细搜索结果 ===")
        for i, result in enumerate(results['results'], 1):
            print(f"\n[{i}]")
            print(f"标题: {result.get('title', 'N/A')}")
            print(f"URL: {result.get('url', 'N/A')}")
            print(f"摘要: {result.get('summary', 'N/A')[:100]}..." if result.get('summary') else "摘要: N/A")
    else:
        print(f"\n错误信息: {results.get('error_message', '无')}")
    
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    test_baidu_search()