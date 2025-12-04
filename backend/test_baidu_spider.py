#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
百度搜索爬虫测试脚本
自动测试百度搜索爬虫功能，无需交互式输入
"""

import os
import sys
import json
from baidu_search_spider import BaiduSearchSpider

def test_spider():
    """测试百度搜索爬虫的基本功能"""
    print("开始测试百度搜索爬虫...")
    print("=" * 50)
    
    # 初始化爬虫
    spider = BaiduSearchSpider()
    
    # 测试关键词
    test_keywords = ["四川农业大学", "百度搜索", "Python爬虫"]
    
    all_test_results = []
    
    for keyword in test_keywords:
        print(f"\n测试关键词: {keyword}")
        print("-" * 30)
        
        try:
            # 执行搜索
            result = spider.search(keyword, timeout=15)
            
            # 记录测试结果
            test_result = {
                'keyword': keyword,
                'status': result['status'],
                'result_count': result.get('result_count', 0),
                'error_message': result.get('error_message', '')
            }
            all_test_results.append(test_result)
            
            # 显示结果摘要
            if result['status'] == 'success':
                print(f"✓ 搜索成功")
                print(f"  状态码: {result.get('status_code')}")
                print(f"  结果数量: {result.get('result_count')}")
                print(f"  请求URL: {result.get('search_url')[:100]}..." if len(result.get('search_url', '')) > 100 else f"  请求URL: {result.get('search_url')}")
                
                # 显示前3个结果
                if result['results']:
                    print("\n  部分结果示例:")
                    for i, item in enumerate(result['results'][:3], 1):
                        print(f"  [{i}] {item['title'][:60]}..." if len(item['title']) > 60 else f"  [{i}] {item['title']}")
                        print(f"    URL: {item['url'][:80]}..." if len(item['url']) > 80 else f"    URL: {item['url']}")
            else:
                print(f"✗ 搜索失败")
                print(f"  错误类型: {result.get('error_type')}")
                print(f"  错误信息: {result.get('error_message')}")
                
        except Exception as e:
            print(f"✗ 执行出错: {str(e)}")
            all_test_results.append({
                'keyword': keyword,
                'status': 'exception',
                'error_message': str(e)
            })
    
    print("\n" + "=" * 50)
    print("测试总结:")
    
    # 统计测试结果
    success_count = sum(1 for r in all_test_results if r['status'] == 'success')
    total_count = len(all_test_results)
    
    print(f"总测试数: {total_count}")
    print(f"成功数: {success_count}")
    print(f"失败数: {total_count - success_count}")
    
    # 保存详细结果到文件
    with open('spider_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(all_test_results, f, ensure_ascii=False, indent=2)
    
    print("\n详细测试结果已保存到: spider_test_results.json")
    
    # 返回测试状态
    return success_count > 0

def test_batch_search():
    """测试批量搜索功能"""
    print("\n测试批量搜索功能...")
    print("-" * 50)
    
    spider = BaiduSearchSpider()
    keywords = ["测试关键词1", "测试关键词2"]
    
    try:
        results = spider.batch_search(keywords, delay_range=(1, 2))
        print(f"批量搜索完成，共搜索 {len(keywords)} 个关键词")
        print(f"成功获取 {len(results)} 组结果")
        return True
    except Exception as e:
        print(f"批量搜索测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("百度搜索爬虫自动测试脚本")
    print("=" * 50)
    
    try:
        # 测试基本搜索功能
        basic_test_passed = test_spider()
        
        # 测试批量搜索功能
        batch_test_passed = test_batch_search()
        
        print("\n" + "=" * 50)
        print("测试完成!")
        print(f"基本搜索测试: {'通过' if basic_test_passed else '失败'}")
        print(f"批量搜索测试: {'通过' if batch_test_passed else '失败'}")
        
        if basic_test_passed and batch_test_passed:
            print("\n🎉 所有测试通过！")
            return 0
        else:
            print("\n❌ 部分测试失败！")
            return 1
            
    except Exception as e:
        print(f"\n❌ 测试脚本执行出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return 2

if __name__ == "__main__":
    sys.exit(main())