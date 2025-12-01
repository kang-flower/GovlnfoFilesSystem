#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试脚本，用于验证百度搜索爬虫的基本功能
"""

from baidu_spider import BaiduSpider
import time

def test_spider():
    """
    测试爬虫的基本功能
    """
    print("开始测试百度搜索爬虫...")
    print("=" * 50)
    
    # 创建爬虫实例
    spider = BaiduSpider()
    
    # 测试单个关键词搜索
    test_keyword = "成都"
    print(f"\n测试搜索关键词: {test_keyword}")
    
    try:
        # 执行搜索
        result = spider.search(test_keyword)
        
        # 打印结果状态
        print(f"\n搜索状态: {result.get('status')}")
        if result.get('status') == 'success':
            print(f"状态码: {result.get('status_code')}")
            print(f"返回结果数量: {result.get('result_count')}")
            
            # 打印前3个结果，使用更简洁的方式
            print(f"\n前3个搜索结果:")
            for i, item in enumerate(result.get('results', [])[:3], 1):
                print(f"[{i}]")
                # 标题
                title = item.get('title', 'N/A')
                print(f"标题: {title[:100] + '...' if len(title) > 100 else title}")
                
                # 概要
                summary = item.get('summary', 'N/A')
                print(f"概要: {summary[:100] + '...' if summary else 'N/A'}")
                
                # URL - 只显示一次，确保格式正确
                url = item.get('url', 'N/A')
                # 添加调试信息，查看URL的原始内容
                print(f"DEBUG - URL原始内容: {repr(url)}")
                print(f"DEBUG - URL长度: {len(url)}")
                print(f"DEBUG - URL类型: {type(url)}")
                # 清理URL，移除可能的省略号
                if url.endswith('...'):
                    url = url[:-3]
                # 移除所有不可见字符
                url = ''.join(char for char in url if char.isprintable())
                # 如果URL中包含多个http，只保留第一个完整URL
                if 'http' in url[7:]:
                    url = 'http' + url.split('http', 1)[1]
                # 如果URL中包含空格，只取第一个完整URL部分
                if ' ' in url:
                    url = url.split()[0].rstrip(',.?!;:')
                # 限制显示长度
                if len(url) > 100:
                    url = url[:97] + '...'
                print(f"URL: {url}")
                
                # 封面URL
                cover_url = item.get('cover_url', 'N/A')
                if len(cover_url) > 100:
                    cover_url = cover_url[:97] + '...'
                print(f"封面URL: {cover_url if cover_url else 'N/A'}")
                print()
            
            # 打印百度百科信息（如果有）
            if result.get('baike_info'):
                print("百度百科信息:")
                print(f"标题: {result['baike_info'].get('title', 'N/A')}")
                print(f"内容: {result['baike_info'].get('content', 'N/A')[:150]}..." if result['baike_info'].get('content') else "内容: N/A")
                print()
            
            # 打印相关搜索
            if result.get('related_searches'):
                print(f"相关搜索: {', '.join(result['related_searches'][:5])}")
                if len(result['related_searches']) > 5:
                    print(f"... 等共{len(result['related_searches'])}个相关搜索")
        else:
            print(f"搜索失败: {result.get('error_message', '未知错误')}")
        
        print("\n" + "=" * 50)
        print("爬虫基本功能测试完成！")
        print("\n提示:")
        print("1. 如需使用完整功能，请运行: python baidu_spider.py")
        print("2. 支持交互式搜索、批量搜索和结果保存")
        print("3. 详细使用说明请查看README.md文件")
        
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        print("\n请检查网络连接或依赖包安装情况")
        print("依赖包安装命令: pip install requests beautifulsoup4")

if __name__ == "__main__":
    test_spider()