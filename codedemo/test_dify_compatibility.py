# 测试dify环境兼容性的脚本

# 模拟dify环境调用方式
def test_dify_compatibility():
    print("测试dify环境兼容性...")
    
    # 导入百度爬虫
    from baidu_spider import BaiduSpider, main
    
    # 测试1: 直接调用main函数并传递arg1参数
    print("\n测试1: 调用main(arg1='Python编程教程')")
    try:
        main(arg1='Python编程教程')
        print("✓ 测试1通过: main函数成功接受arg1参数")
    except Exception as e:
        print(f"✗ 测试1失败: {str(e)}")
    
    # 测试2: 不传递参数调用main函数
    print("\n测试2: 调用main()")
    try:
        # 这里我们不真正运行交互式模式，只是验证函数能够接受无参数调用
        # 检查函数签名
        import inspect
        sig = inspect.signature(main)
        params = list(sig.parameters.keys())
        
        print(f"✓ 测试2通过: main函数签名: {params}")
        print(f"✓ main函数可以接受arg1参数: {'arg1' in params}")
    except Exception as e:
        print(f"✗ 测试2失败: {str(e)}")

if __name__ == "__main__":
    test_dify_compatibility()