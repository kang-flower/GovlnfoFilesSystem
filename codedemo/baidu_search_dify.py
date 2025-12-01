#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
百度搜索Dify逻辑代码
用于在Dify平台中执行百度搜索功能
移除了bs4依赖，使用正则表达式解析HTML
"""

import requests
import urllib.parse
import re
import time
import random

# 禁用日志，使用print输出信息
def log_info(msg):
    print(f"INFO: {msg}")

def log_error(msg):
    print(f"ERROR: {msg}")

def _clean_url(url):
    """清理URL，确保只返回一个完整有效的URL"""
    try:
        # 1. 移除所有不可见字符（换行符、制表符等）
        url = ''.join(char for char in url if char.isprintable()).strip()
        
        # 2. 移除URL末尾的标点符号
        url = url.rstrip(',.?!;:')
        
        # 3. 检查是否包含多个http(s)，只保留第一个完整URL
        http_positions = []
        for protocol in ['http://', 'https://']:
            pos = url.find(protocol)
            if pos != -1:
                http_positions.append((pos, protocol))
        
        # 如果找到多个http，只保留第一个完整URL
        if len(http_positions) > 1:
            # 按位置排序
            http_positions.sort()
            # 取第一个http的位置作为起始
            start_pos = http_positions[0][0]
            # 查找下一个http的位置作为结束
            end_pos = http_positions[1][0]
            url = url[start_pos:end_pos]
        
        # 4. 处理URL中可能的空格，只取第一个部分
        if ' ' in url:
            # 使用正则表达式提取第一个完整的URL
            url_match = re.search(r'https?://[^\s]+', url)
            if url_match:
                url = url_match.group(0)
            else:
                # 简单地分割并取第一个部分
                url = url.split()[0]
        
        # 5. 确保URL格式正确
        if url.startswith(('http://', 'https://')):
            # 验证URL格式是否基本有效
            if len(url) > 10 and '.' in url[8:]:  # 确保有域名部分
                return url
        elif url.startswith('/') and not url.startswith('//'):
            # 处理相对路径
            return f"https://www.baidu.com{url}"
        elif 'baidu.com/link?' in url:
            # 处理百度跳转链接
            if not url.startswith(('http://', 'https://')):
                return f"http://{url}"
            return url
        else:
            # 尝试从URL字符串中提取完整URL
            url_match = re.search(r'https?://[^\s"\'>]+', url)
            if url_match:
                return url_match.group(0)
        
        return None
    except Exception as e:
        log_error(f"清理URL时出错: {e}, URL='{url[:100]}...'")
        return None

def _is_baidu_internal(url):
    """检查是否为百度内部非结果链接"""
    # 排除百度搜索结果页面的内部链接，但保留百度百科等内容链接
    internal_patterns = [
        'baidu.com/s?wd=',  # 搜索结果页
        'baidu.com/more',   # 更多选项
        'baidu.com/baidu',  # 百度主页链接
        'passport.baidu.com',  # 登录页
        'baidu.com/favicon.ico',  # 图标
        'baidustatic.com',  # 静态资源
        'bdstatic.com',  # 静态资源
        'baidu.com/img',  # 图片资源
        'baidu.com/js',   # JS资源
        'baidu.com/css',  # CSS资源
        'baidu.com/nslog',  # 日志
        'baidu.com/ubbc',  # 百度统计
        'baidu.com/cache',  # 缓存
        'baidu.com/t.jpg',  # 跟踪图片
    ]
    
    # 应该保留的百度内容链接
    content_patterns = [
        'baike.baidu.com',  # 百度百科
        'zhidao.baidu.com',  # 百度知道
        'tieba.baidu.com',  # 百度贴吧
        'map.baidu.com',    # 百度地图
        'wenku.baidu.com',  # 百度文库
        'music.baidu.com',  # 百度音乐
        'image.baidu.com',  # 百度图片
        'video.baidu.com',  # 百度视频
    ]
    
    # 首先检查是否是应该保留的内容链接
    for pattern in content_patterns:
        if pattern in url:
            return False
    
    # 然后检查是否是应该排除的内部链接
    for pattern in internal_patterns:
        if pattern in url:
            return True
    
    return False

def _deduplicate_results(results):
    """简单的去重逻辑"""
    if not results:
        return []
        
    unique_results = []
    seen_urls = set()
    
    for result in results:
        url = result['url']
        # 简化的URL去重（只使用域名+路径）
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        except:
            clean_url = url
        
        if clean_url not in seen_urls:
            seen_urls.add(clean_url)
            unique_results.append(result)
    
    # 限制结果数量
    return unique_results[:10]

# 删除_process_link函数，因为现在直接在main函数中使用正则处理

def _get_headers():
    """生成随机的请求头"""
    # 随机选择一个User-Agent
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    ]
    
    return {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Referer': 'https://www.baidu.com/',
        'Connection': 'keep-alive',
    }

def main(arg1: str):
    """
    百度搜索主函数 - 用于Dify平台
    
    Args:
        arg1: 搜索关键词
    
    Returns:
        dict: 包含搜索结果的字典
    """
    try:
        # 参数验证
        keyword = arg1.strip()
        if not keyword:
            return {
                "result": "错误: 搜索关键词不能为空"
            }
        
        log_info(f"开始搜索关键词: {keyword}")
        
        # 初始化会话
        session = requests.Session()
        session.allow_redirects = True
        session.cookies.set('BDORZ', 'B490B5EBF6F3CD402E515D22BCDA1598')
        
        # 访问百度首页获取cookie（可选，这里简化）
        try:
            home_headers = _get_headers()
            home_headers['Referer'] = 'https://www.google.com/'
            home_response = session.get('https://www.baidu.com', headers=home_headers, timeout=5)
            log_info(f"首页访问状态码: {home_response.status_code}")
            time.sleep(random.uniform(0.5, 1.0))  # 简短延迟
        except Exception as e:
            log_info(f"首页访问失败，继续搜索: {e}")
        
        # 对关键词进行URL编码
        encoded_keyword = urllib.parse.quote(keyword)
        
        # 构建搜索URL
        random_param = random.randint(1000000000, 9999999999)
        search_url = f"https://www.baidu.com/s?wd={encoded_keyword}&rsv_spt=1&rsv_iqid=0x{random_param:x}"
        
        log_info(f"搜索URL: {search_url}")
        
        # 发送搜索请求
        headers = _get_headers()
        headers['Referer'] = 'https://www.baidu.com/'
        
        # 简短延迟后发送请求
        time.sleep(random.uniform(0.3, 1.0))
        
        try:
            response = session.get(search_url, headers=headers, timeout=10, allow_redirects=True)
            response.encoding = 'utf-8'
            response.raise_for_status()
            log_info(f"搜索请求状态码: {response.status_code}")
        except requests.exceptions.RequestException as e:
            return {
                "result": f"错误: 搜索请求失败 - {str(e)}"
            }
        
        # 检查是否包含验证码
        html_content = response.text
        if "验证码" in html_content or "验证" in html_content or "安全验证" in html_content:
            return {
                "result": "错误: 检测到百度验证码，搜索失败"
            }
        
        # 初始化结果
        results = []
        seen_titles = set()
        seen_urls = set()
        
        # 使用正则表达式提取搜索结果
        log_info("使用正则表达式提取搜索结果")
        
        # 尝试提取搜索结果的不同正则模式
        # 模式1: 匹配带有标题和链接的搜索结果
        pattern1 = r'<a[^>]*?href=["\'](.*?)["\'][^>]*?>(.*?)</a>'
        matches = re.findall(pattern1, html_content, re.DOTALL)
        
        log_info(f"正则匹配1找到 {len(matches)} 个链接")
        
        for href, title_html in matches[:200]:  # 限制处理数量
            # 清理标题，移除HTML标签
            title = re.sub(r'<[^>]*>', '', title_html).strip()
            href = href.strip()
            
            # 筛选条件
            if title and len(title) > 5 and len(title) < 150 and href and len(href) > 8:
                if title not in seen_titles:
                    # 使用正则提取可能的摘要
                    summary = ""
                    # 查找标题附近的文本作为摘要
                    summary_pattern = re.escape(title) + r'[^<]*</a>[^<]*<span[^>]*>(.*?)</span>'
                    summary_match = re.search(summary_pattern, html_content, re.DOTALL)
                    if summary_match:
                        summary = re.sub(r'<[^>]*>', '', summary_match.group(1)).strip()
                    
                    # 清理URL
                    clean_url = _clean_url(href)
                    
                    # 跳过无效URL或百度内部非结果链接
                    if clean_url and not _is_baidu_internal(clean_url):
                        if clean_url not in seen_urls:
                            results.append({
                                'title': title,
                                'summary': summary[:300],
                                'url': clean_url
                            })
                            seen_titles.add(title)
                            seen_urls.add(clean_url)
        
        # 尝试额外的模式提取结果
        # 模式2: 匹配特定的百度搜索结果格式
        pattern2 = r'<div[^>]*class=["\'].*?(result|c-container).*?["\'][^>]*>.*?<a[^>]*?href=["\'](.*?)["\'][^>]*?>(.*?)</a>.*?</div>'
        matches2 = re.findall(pattern2, html_content, re.DOTALL)
        
        log_info(f"正则匹配2找到 {len(matches2)} 个结果")
        
        for _, href, title_html in matches2[:100]:
            title = re.sub(r'<[^>]*>', '', title_html).strip()
            href = href.strip()
            
            if title and len(title) > 5 and title not in seen_titles:
                clean_url = _clean_url(href)
                if clean_url and not _is_baidu_internal(clean_url) and clean_url not in seen_urls:
                    # 提取摘要
                    summary = ""
                    # 在结果块中查找可能的摘要
                    result_block_pattern = re.escape(href) + r'[^<]*</a>.*?</div>'
                    block_match = re.search(result_block_pattern, html_content, re.DOTALL)
                    if block_match:
                        block_content = block_match.group(0)
                        # 尝试提取摘要文本
                        text_matches = re.findall(r'<[^>]*class=["\'](?:c-abstract|content|summary)["\'][^>]*>(.*?)</div>', block_content, re.DOTALL)
                        if text_matches:
                            summary = re.sub(r'<[^>]*>', '', text_matches[0]).strip()[:300]
                    
                    results.append({
                        'title': title,
                        'summary': summary,
                        'url': clean_url
                    })
                    seen_titles.add(title)
                    seen_urls.add(clean_url)
        
        # 去重处理
        unique_results = _deduplicate_results(results)
        
        # 格式化结果
        formatted_results = []
        for i, item in enumerate(unique_results, 1):
            formatted_results.append(f"[{i}] 标题: {item['title']}")
            formatted_results.append(f"   URL: {item['url']}")
            if item['summary']:
                formatted_results.append(f"   摘要: {item['summary']}")
            formatted_results.append("")
        
        # 构建返回结果
        result_text = "\n".join(formatted_results)
        if result_text:
            return {
                "result": f"百度搜索结果 '{keyword}':\n\n{result_text}搜索完成，共找到 {len(unique_results)} 个结果"
            }
        else:
            return {
                "result": f"搜索 '{keyword}' 未找到有效结果"
            }
    
    except Exception as e:
        log_error(f"搜索过程中发生错误: {str(e)}")
        return {
            "result": f"错误: {str(e)}"
        }

# 用于测试
if __name__ == "__main__":
    # 测试搜索
    test_result = main("Python编程教程")
    print(test_result["result"])