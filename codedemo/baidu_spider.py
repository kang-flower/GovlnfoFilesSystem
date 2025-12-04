#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
网络数据抓取工具
功能: 用于通过互联网接口检索所需要的数据，并形成数据集
目标接口: 百度搜索
"""

import requests
import urllib.parse
import re
import time
import random
import json
import logging
from urllib.parse import urlparse

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BaiduSpider:
    """
    百度搜索爬虫类，用于抓取百度搜索结果，支持精准搜索和结果验证
    """
    
    def __init__(self):
        # 初始化会话，启用重定向跟踪
        self.session = requests.Session()
        self.session.allow_redirects = True
        
        # 添加一些初始cookie以模拟已访问过百度
        self.session.cookies.set('BDORZ', 'B490B5EBF6F3CD402E515D22BCDA1598')  # 百度常见cookie
        self.session.cookies.set('BAIDUID', '0A1E45A76B7F15035D5D42A6B5A2F1F3:FG=1')
        self.session.cookies.set('H_PS_PSSID', '38004_37989_38040_38091_38094')
        
        # 初始化访问计数和时间戳
        self.visit_count = 0
        self.last_visit_time = time.time()
    
    def _get_headers(self):
        """生成更接近真实浏览器的请求头，减少被检测到的风险"""
        # 随机选择一个User-Agent
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0'
        ]
        
        headers = {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://www.baidu.com/'
        }
        
        # 随机添加一些额外的头信息，增加变化性
        extra_headers = {
            'DNT': '1',
            'Pragma': 'no-cache',
            'TE': 'Trailers',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1'
        }
        
        # 随机选择1-3个额外的头信息添加
        num_extra = random.randint(1, 3)
        selected_extra_keys = random.sample(list(extra_headers.keys()), num_extra)
        for key in selected_extra_keys:
            headers[key] = extra_headers[key]
            
        return headers
    
    def _simulate_human_behavior(self):
        """模拟人类行为，避免被反爬"""
        # 更新访问计数
        self.visit_count += 1
        current_time = time.time()
        time_since_last_visit = current_time - self.last_visit_time
        self.last_visit_time = current_time
        
        # 根据访问次数增加延迟
        if self.visit_count <= 3:
            # 初始访问，延迟较小
            delay = random.uniform(1.5, 2.5)
        elif self.visit_count <= 10:
            # 多次访问，增加延迟
            delay = random.uniform(3, 5)
        else:
            # 频繁访问，较大延迟
            delay = random.uniform(5, 8)
        
        # 确保两次访问之间至少有1秒间隔
        if time_since_last_visit < 1:
            delay += 1 - time_since_last_visit
        
        logger.info(f"模拟人类行为，延迟 {delay:.2f} 秒")
        time.sleep(delay)
    
    def search(self, keyword, timeout=20):
        """
        根据关键词精准搜索百度
        
        Args:
            keyword: 搜索关键词
            timeout: 请求超时时间
            
        Returns:
            dict: 搜索结果字典，包含状态码和数据
        """
        try:
            logger.info(f"开始搜索关键词: {keyword}")
            
            # 模拟人类行为
            self._simulate_human_behavior()
            
            # 对关键词进行URL编码
            encoded_keyword = urllib.parse.quote(keyword)
            
            # 构造优化的百度搜索URL，添加安全参数
            search_url = f"https://www.baidu.com/s?wd={encoded_keyword}&ie=utf-8&rsv_idx=1&rsv_pq=f2e85d230002a446&rsv_t=e0a21Bc5R8I4s4%2FhXr2Jvq%2FdDw"
            
            # 使用持久会话
            session = self.session
            
            # 设置更真实的请求头
            headers = self._get_headers()
            
            logger.info(f"搜索URL: {search_url}")
            logger.info("发送搜索请求...")
            
            # 发送请求，使用HTTPS以提高安全性
            response = session.get(search_url, headers=headers, timeout=timeout, allow_redirects=True)
            
            # 尝试多种方式解码响应内容
            html_content = None
            
            # 方法1：让requests自动处理
            try:
                html_content = response.text
                logger.info("使用requests自动解码获取HTML内容")
            except Exception as e:
                logger.error(f"自动解码失败: {e}")
                # 如果自动解码失败，尝试手动解码
                try:
                    # 首先尝试GBK，百度常用
                    html_content = response.content.decode('gbk', errors='replace')
                    logger.info("使用gbk解码获取HTML内容")
                except Exception as e:
                    logger.error(f"gbk解码失败: {e}")
                    # 尝试UTF-8
                    try:
                        html_content = response.content.decode('utf-8', errors='replace')
                        logger.info("使用utf-8解码获取HTML内容")
                    except Exception as e:
                        logger.error(f"utf-8解码失败: {e}")
                        # 最后使用原始内容
                        html_content = str(response.content)
                        logger.warning("使用原始内容字符串表示")
            
            # 确保html_content不为None
            if html_content is None:
                html_content = ''
            
            # 打印一些调试信息
            logger.info(f"请求头中的User-Agent: {headers['User-Agent']}")
            logger.info(f"Cookie数量: {len(session.cookies)}")
            logger.info(f"响应状态码: {response.status_code}")
            
            response.raise_for_status()  # 检查请求是否成功
            
            # 保存响应文本用于调试
            logger.info(f"HTML内容长度: {len(html_content)} 字符")
            
            # 检查是否包含验证码或反爬信息
            anti_crawl_patterns = ["验证码", "验证", "antirobot", "安全验证", "请输入验证码", "确认您是用户", "您的访问过于频繁"]
            anti_crawl_detected = any(pattern in html_content for pattern in anti_crawl_patterns)
            
            if anti_crawl_detected:
                logger.warning("检测到可能的反爬机制或验证码")
                return {
                    'status': 'error',
                    'error_type': 'captcha',
                    'error_message': '检测到百度验证码或反爬机制',
                    'keyword': keyword
                }
            
            # 初始化结果列表和去重集合
            results = []
            seen_titles = set()  # 用于标题去重
            seen_urls_temp = set()  # 用于临时URL去重
            
            # 使用正则表达式提取搜索结果 - 使用更精准的模式
            logger.info("使用正则表达式提取搜索结果")
            
            # 显示页面的前300个字符，看看是否是正常的百度页面
            logger.info(f"HTML前300字符: {repr(html_content[:300])}")
            
            # 使用更精准的正则表达式匹配百度搜索结果
            # 匹配百度搜索结果的主要结构
            result_blocks = re.findall(r'<div class=["\']result["\'][^>]*>(.*?)</div>', html_content, re.DOTALL)
            logger.info(f"找到 {len(result_blocks)} 个结果块")
            
            # 对于每个结果块，提取标题、URL和摘要
            for block in result_blocks:
                # 提取标题和URL
                title_url_match = re.search(r'<h3[^>]*>.*?<a[^>]*?href=["\'](.*?)["\'][^>]*?>(.*?)</a>.*?</h3>', block, re.DOTALL)
                if title_url_match:
                    url = title_url_match.group(1)
                    title_html = title_url_match.group(2)
                    # 清理标题
                    title = re.sub(r'<[^>]*>', '', title_html).strip()
                    
                    # 提取摘要
                    abstract = ''
                    abstract_match = re.search(r'<div class=["\']c-abstract["\'][^>]*>(.*?)</div>', block, re.DOTALL)
                    if not abstract_match:
                        abstract_match = re.search(r'<div class=["\']content["\'][^>]*>(.*?)</div>', block, re.DOTALL)
                    if abstract_match:
                        abstract = re.sub(r'<[^>]*>', '', abstract_match.group(1)).strip()
                    
                    # 提取来源信息
                    source = ''
                    source_match = re.search(r'<span class=["\']c-showurl["\'][^>]*>(.*?)</span>', block, re.DOTALL)
                    if source_match:
                        source = re.sub(r'<[^>]*>', '', source_match.group(1)).strip()
                    
                    # 验证和清理URL
                    clean_url = self._clean_url(url)
                    if not clean_url:
                        continue
                    
                    # 筛选条件：确保标题不为空，长度合适
                    if title and len(title) > 2 and len(title) < 150 and clean_url not in seen_urls_temp:
                        # 添加结果
                        results.append({
                            'title': title,
                            'abstract': abstract[:200] if abstract else '',  # 限制摘要长度
                            'url': clean_url,
                            'source': source
                        })
                        seen_urls_temp.add(clean_url)
                        
                        # 限制结果数量
                        if len(results) >= 15:
                            break
            
            # 如果上述方法没有找到结果，尝试备用的正则表达式
            if not results:
                logger.info("尝试备用的结果提取方法")
                # 尝试匹配更多可能的链接模式
                pattern = r'<a[^>]*?href=["\'](https?://[^"\']*)["\'][^>]*?class=["\'](?:mnav|c-title-text|result-title)["\'][^>]*?>(.*?)</a>'
                matches = re.findall(pattern, html_content, re.DOTALL)
                
                logger.info(f"备用正则匹配找到 {len(matches)} 个潜在链接")
                
                for href, title_html in matches[:50]:
                    # 清理标题
                    title = re.sub(r'<[^>]*>', '', title_html).strip()
                    
                    # 验证和清理URL
                    clean_url = self._clean_url(href)
                    if not clean_url:
                        continue
                    
                    # 筛选条件
                    if title and len(title) > 2 and len(title) < 150 and clean_url not in seen_urls_temp:
                        # 提取摘要（如果可能）
                        abstract = ''
                        abstract_pattern = re.escape(title) + r'[^<]*<[^>]*>(.*?)<'  # 尝试找到标题附近的摘要
                        abstract_match = re.search(abstract_pattern, html_content, re.DOTALL)
                        if abstract_match:
                            abstract = re.sub(r'<[^>]*>', '', abstract_match.group(1)).strip()[:200]
                        
                        results.append({
                            'title': title,
                            'abstract': abstract,
                            'url': clean_url,
                            'source': ''
                        })
                        seen_urls_temp.add(clean_url)
                        
                        if len(results) >= 10:
                            break
            
            # 对结果进行验证和过滤，确保与关键词相关
            validated_results = self._validate_results(results, keyword)
            
            # 实现高级去重逻辑
            final_results = self._deduplicate_results(validated_results)
            
            logger.info(f"原始结果数: {len(results)}, 验证后结果数: {len(validated_results)}, 最终去重结果数: {len(final_results)}")
            
            return {
                'status': 'success',
                'status_code': response.status_code,
                'keyword': keyword,
                'search_url': search_url,
                'result_count': len(final_results),
                'results': final_results
            }
        except Exception as e:
            logger.error(f"搜索过程中出错: {str(e)}")
            return {
                'status': 'error',
                'error_type': 'exception',
                'error_message': str(e),
                'keyword': keyword
            }
    
    def _validate_results(self, results, keyword):
        """验证搜索结果是否与关键词相关"""
        validated_results = []
        keyword_lower = keyword.lower()
        
        # 关键词变体，用于更灵活的匹配
        keyword_variations = [keyword_lower]
        if '大学' in keyword_lower:
            keyword_variations.append(keyword_lower.replace('大学', ''))
        
        for result in results:
            title_lower = result['title'].lower()
            abstract_lower = result.get('abstract', '').lower()
            
            # 计算相关性分数
            relevance_score = 0
            
            # 标题中包含关键词或其变体
            for variation in keyword_variations:
                if variation in title_lower:
                    relevance_score += 10
                    # 完全匹配加分
                    if variation == title_lower:
                        relevance_score += 20
                    # 关键词出现在开头加分
                    if title_lower.startswith(variation):
                        relevance_score += 5
            
            # 摘要中包含关键词
            for variation in keyword_variations:
                relevance_score += abstract_lower.count(variation) * 2
            
            # 只保留相关性分数大于0的结果
            if relevance_score > 0:
                result['relevance_score'] = relevance_score
                validated_results.append(result)
        
        # 按相关性分数排序
        return sorted(validated_results, key=lambda x: x.get('relevance_score', 0), reverse=True)
        
    def _deduplicate_results(self, results):
        """高级去重方法，基于URL和内容相似度"""
        if not results:
            return []
            
        unique_results = []
        seen_urls = set()
        seen_titles = set()
        
        for result in results:
            url = result.get('url', '')
            title = result.get('title', '').strip().lower()
            
            # 基于URL去重
            if url and url not in seen_urls:
                # 基于标题相似度去重（忽略标点符号和空格）
                normalized_title = re.sub(r'[\s\p{P}]+', '', title)
                title_duplicate = False
                
                for seen_title in seen_titles:
                    # 如果相似度超过80%，视为重复
                    if self._string_similarity(normalized_title, seen_title) > 0.8:
                        title_duplicate = True
                        break
                
                if not title_duplicate:
                    seen_urls.add(url)
                    seen_titles.add(normalized_title)
                    unique_results.append(result)
                    
                    # 保留最多10个结果
                    if len(unique_results) >= 10:
                        break
        
        # 确保至少有5个结果
        if len(unique_results) < 5 and len(results) > len(unique_results):
            logger.info("结果数量不足5个，放宽去重条件")
            for result in results:
                url = result.get('url', '')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_results.append(result)
                    if len(unique_results) >= 5:
                        break
        
        # 保留前5-8个最相关的结果
        return unique_results[:min(8, len(unique_results))]
    
    def _string_similarity(self, s1, s2):
        """计算两个字符串的相似度"""
        if not s1 or not s2:
            return 0
        
        # 简单的基于交集的相似度计算
        set1 = set(s1)
        set2 = set(s2)
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0
    
    # _process_and_add_result方法已移除，使用正则表达式直接处理结果
        
    def _clean_url(self, url):
        """高级URL清理方法，处理各种URL格式"""
        try:
            if not url:
                return None
            
            # 移除空格和换行符
            url = url.strip()
            
            # 处理百度跳转链接
            if 'baidu.com/link?' in url:
                # 提取真实URL（如果可能）
                real_url_match = re.search(r'url=([^&]+)', url)
                if real_url_match:
                    try:
                        return urllib.parse.unquote(real_url_match.group(1))
                    except:
                        pass
                # 如果无法提取，保留原始链接
                return url if url.startswith(('http://', 'https://')) else 'https://' + url
            
            # 确保URL有协议
            if not url.startswith(('http://', 'https://')):
                # 尝试从百度内部链接提取真实URL
                if url.startswith('//'):
                    return 'https:' + url
                # 其他情况，尝试解析为完整URL
                parsed = urlparse(url)
                if parsed.netloc:
                    return 'https://' + url if not url.startswith('http') else url
                return None
            
            # 移除末尾标点
            url = url.rstrip(',.?!;:')
            
            # 过滤无效URL
            invalid_patterns = ['javascript:', 'data:', 'about:blank']
            if any(pattern in url.lower() for pattern in invalid_patterns):
                return None
            
            # 检查URL长度
            if len(url) > 500:
                return None
            
            return url
        except Exception as e:
            logger.warning(f"URL清理失败: {e}")
            return None
    
    def _is_baidu_internal(self, url):
        """高级百度内部链接检查"""
        try:
            if not url:
                return True
            
            # 解析URL获取域名
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # 检查是否是百度域名
            if 'baidu.com' not in domain:
                return False
            
            # 保留有价值的百度内容域名
            valuable_domains = [
                'baike.baidu.com',  # 百度百科
                'zhidao.baidu.com',  # 百度知道
                'wenku.baidu.com',  # 百度文库
                'map.baidu.com',    # 百度地图
                'image.baidu.com',  # 百度图片
                'video.baidu.com',  # 百度视频
                'news.baidu.com',   # 百度新闻
                'tieba.baidu.com',  # 百度贴吧
                'xueshu.baidu.com'  # 百度学术
            ]
            
            # 检查是否是有价值的百度域名
            for valuable_domain in valuable_domains:
                if valuable_domain in domain:
                    return False
            
            # 其他百度域名视为内部链接
            return True
        except Exception as e:
            logger.warning(f"百度内部链接检查失败: {e}")
            return True
    
    def main(self, arg1=None):
        """dify环境调用入口方法"""
        keyword = arg1 or ""
        logger.info(f"dify环境调用，搜索关键词: {keyword}")
        # 直接调用search方法
        return self.search(keyword)
    
    def batch_search(self, keywords, delay_range=(1, 3)):
        """
        批量搜索多个关键词
        
        Args:
            keywords: 关键词列表
            delay_range: 请求间隔时间范围（秒）
            
        Returns:
            list: 搜索结果列表
        """
        all_results = []
        
        for i, keyword in enumerate(keywords):
            result = self.search(keyword)
            all_results.append(result)
            
            # 避免频繁请求，添加随机延迟
            if i < len(keywords) - 1:
                delay = random.uniform(delay_range[0], delay_range[1])
                print(f"等待 {delay:.2f} 秒后继续搜索...")
                time.sleep(delay)
        
        return all_results
    
    def format_result_text(self, result):
        """
        将搜索结果格式化为文本
        
        Args:
            result: 搜索结果字典
            
        Returns:
            str: 格式化后的文本
        """
        if result['status'] != 'success':
            return f"搜索失败: {result['error_message']}"
        
        text = []
        text.append(f"搜索关键词: {result['keyword']}")
        text.append(f"请求URL: {result['search_url']}")
        text.append(f"状态码: {result['status_code']}")
        text.append(f"搜索结果数量: {result['result_count']}")
        text.append("")
        
        # 添加百度百科信息
        if result.get('baike_info'):
            text.append("=== 百度百科信息 ===")
            text.append(f"标题: {result['baike_info'].get('title', '')}")
            text.append(f"内容: {result['baike_info'].get('content', '')}")
            text.append("")
        
        # 添加搜索结果
        text.append("=== 搜索结果 ===")
        for i, item in enumerate(result['results'], 1):
            text.append(f"[{i}]")
            text.append(f"标题: {item['title']}")
            
            # 处理概要显示
            summary = item.get('summary', '')
            text.append(f"概要: {summary if summary else 'N/A'}")
            
            # 处理URL显示，避免过长
            url = item.get('url', '')
            if len(url) > 100:
                url = url[:97] + '...'
            text.append(f"URL: {url}")
            
            # 处理封面URL显示
            cover_url = item.get('cover_url', '')
            if len(cover_url) > 100:
                cover_url = cover_url[:97] + '...'
            text.append(f"封面URL: {cover_url if cover_url else 'N/A'}")
            text.append("")
        
        # 添加相关搜索
        if result.get('related_searches'):
            text.append("=== 相关搜索 ===")
            text.append(', '.join(result['related_searches']))
        
        return '\n'.join(text)

def main(arg1=None):
    """
    主函数，支持dify环境传入arg1参数或本地交互式运行
    
    Args:
        arg1: dify环境传入的搜索关键词
    """
    spider = BaiduSpider()
    
    if arg1:
        # dify环境调用模式
        keyword = arg1.strip()
        if keyword:
            logger.info(f"dify环境调用，搜索关键词: {keyword}")
            result = spider.search(keyword)
            
            # 格式化输出结果
            print(spider.format_result_text(result))
        else:
            print("请提供有效的搜索关键词")
    else:
        # 示例搜索
        print("网络数据抓取工具 - 百度搜索")
        print("=" * 50)
        
        # 支持动态参数输入
        while True:
            keyword = input("请输入搜索关键词（输入'q'退出，输入'b'批量搜索）: ")
            
            if keyword.lower() == 'q':
                print("感谢使用，再见！")
                break
            
            if keyword.lower() == 'b':
                # 批量搜索
                keywords_input = input("请输入多个关键词，用逗号分隔: ")
                keywords = [k.strip() for k in keywords_input.split(',') if k.strip()]
                
                if keywords:
                    print(f"即将搜索 {len(keywords)} 个关键词")
                    results = spider.batch_search(keywords)
                    
                    # 移除文件保存操作，直接打印结果
                    print(f"批量搜索完成，找到 {len(results)} 组结果")
                    for i, result in enumerate(results, 1):
                        print(f"\n===== 关键词 '{result.get('keyword', '未知')}' 的搜索结果 =====")
                        print(spider.format_result_text(result))
                else:
                    print("请输入有效的关键词")
            else:
                # 单次搜索
                if keyword.strip():
                    result = spider.search(keyword)
                    
                    # 打印结果
                    print("\n" + "=" * 50)
                    print(spider.format_result_text(result))
                    print("=" * 50 + "\n")
                else:
                    print("请输入有效的关键词")

if __name__ == "__main__":
    main()