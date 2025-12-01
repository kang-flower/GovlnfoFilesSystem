import json
from baidu_spider import BaiduSpider

# 测试百度爬虫功能
def test_baidu_spider():
    print("开始测试百度爬虫（无bs4依赖版本）...")
    
    # 创建爬虫实例
    spider = BaiduSpider()
    
    # 测试搜索功能
    keyword = "Python编程教程"
    print(f"\n搜索关键词: {keyword}")
    
    try:
        # 执行搜索
        result = spider.search(keyword)
        
        # 打印结果
        print("\n搜索结果:")
        print(f"状态: {result.get('status', 'unknown')}")
        print(f"状态码: {result.get('status_code', 'unknown')}")
        print(f"搜索URL: {result.get('search_url', 'unknown')}")
        print(f"结果数量: {result.get('result_count', 0)}")
        
        # 打印具体结果
        results = result.get('results', [])
        print(f"\n详细结果:")
        for i, item in enumerate(results[:5], 1):  # 只打印前5个结果
            print(f"\n{i}. 标题: {item.get('title', '无标题')}")
            print(f"   URL: {item.get('url', '无URL')}")
            print(f"   摘要: {item.get('summary', '无摘要')[:100]}...")
        
        print(f"\n测试完成，共找到 {len(results)} 个结果")
        return True
        
    except Exception as e:
        print(f"\n测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_baidu_spider()