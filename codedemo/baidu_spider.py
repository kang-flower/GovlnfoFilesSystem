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

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BaiduSpider:
    """
    百度搜索爬虫类，用于抓取百度搜索结果
    """
    
    def __init__(self):
        # 初始化会话，启用重定向跟踪
        self.session = requests.Session()
        self.session.allow_redirects = True
        
        # 添加一些初始cookie以模拟已访问过百度
        self.session.cookies.set('BDORZ', 'B490B5EBF6F3CD402E515D22BCDA1598')  # 百度常见cookie
    
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
            'Cache-Control': 'max-age=0'
        }
        
        # 随机添加一些额外的头信息，增加变化性
        extra_headers = {
            'Referer': 'https://www.baidu.com/',
            'DNT': '1',
            'Pragma': 'no-cache',
            'Accept-Encoding': 'gzip, deflate'
        }
        
        # 随机选择0-2个额外的头信息添加
        num_extra = random.randint(0, 2)
        selected_extra_keys = random.sample(list(extra_headers.keys()), num_extra)
        for key in selected_extra_keys:
            headers[key] = extra_headers[key]
            
        return headers
    
    def search(self, keyword, timeout=15):
        """
        根据关键词搜索百度
        
        Args:
            keyword: 搜索关键词
            timeout: 请求超时时间
            
        Returns:
            dict: 搜索结果字典，包含状态码和数据
        """
        try:
            logger.info(f"开始搜索关键词: {keyword}")
            
            # 对关键词进行URL编码
            encoded_keyword = urllib.parse.quote(keyword)
            
            # 简化的百度搜索URL，避免使用过多随机参数
            search_url = f"https://www.baidu.com/s?wd={encoded_keyword}"
            
            # 使用基本的会话设置
            session = requests.Session()
            
            # 设置更真实的请求头
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Referer': 'https://www.baidu.com/',
                'Cache-Control': 'max-age=0'
            }
            
            # 随机延迟，模拟人类行为
            time.sleep(random.uniform(0.5, 1.5))
            
            logger.info(f"搜索URL: {search_url}")
            logger.info("发送搜索请求...")
            
            # 使用HTTP而不是HTTPS，避免某些重定向问题
            search_url = search_url.replace('https://', 'http://')
            
            # 发送请求
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
            if html_content is None or len(html_content.strip()) == 0:
                try:
                    html_content = response.content.decode('utf-8', errors='replace')
                    logger.info("使用utf-8解码获取HTML内容")
                except Exception as e:
                    logger.error(f"utf-8解码失败: {e}")
            
            # 如果还是失败，尝试gbk解码（百度常用）
            if html_content is None or len(html_content.strip()) == 0:
                try:
                    html_content = response.content.decode('gbk', errors='replace')
                    logger.info("使用gbk解码获取HTML内容")
                except Exception as e:
                    logger.error(f"gbk解码失败: {e}")
                    # 最后使用原始内容
                    html_content = str(response.content)
                    logger.warning("使用原始内容字符串表示")
            
            # 确保html_content不为None
            if html_content is None:
                html_content = ''
            
            # 打印一些调试信息
            logger.info(f"请求头中的User-Agent: {headers['User-Agent']}")
            logger.info(f"Cookie数量: {len(self.session.cookies)}")
            logger.info(f"Cookie详情: {dict(self.session.cookies)}")
            logger.info(f"响应状态码: {response.status_code}")
            
            response.raise_for_status()  # 检查请求是否成功
            
            # 保存响应文本用于调试
            html_content = response.text
            logger.info(f"HTML内容长度: {len(html_content)} 字符")
            
            # 检查是否包含验证码或反爬信息
            if "验证码" in html_content or "验证" in html_content or "antirobot" in html_content or "安全验证" in html_content:
                logger.warning("检测到可能的反爬机制或验证码")
                logger.warning("HTML内容包含验证码或反爬提示")
                return {
                    'status': 'error',
                    'error_type': 'captcha',
                    'error_message': '检测到百度验证码或反爬机制',
                    'keyword': keyword
                }
            
            # 初始化结果列表和去重集合
            results = []
            seen_titles = set()  # 用于标题去重
            seen_urls_temp = set()  # 用于临时URL去重（在处理过程中）
            
            # 使用正则表达式提取搜索结果
            logger.info("使用正则表达式提取搜索结果")
            
            # 显示页面的前300个字符，看看是否是正常的百度页面
            logger.info(f"HTML前300字符: {repr(html_content[:300])}")
            
            # 优化的结果提取逻辑，使用更通用的正则模式匹配百度搜索结果
            # 尝试匹配多种可能的搜索结果链接模式
            pattern = r'<a[^>]*?href=["\'](https?://[^"\']*)["\'][^>]*?>([^<]*?)</a>'
            matches = re.findall(pattern, html_content, re.DOTALL)
            
            logger.info(f"正则匹配找到 {len(matches)} 个潜在链接")
            
            # 限制处理的结果数量，避免超时
            for href, title_html in matches[:50]:  # 大幅减少处理数量
                # 快速清理标题
                title = re.sub(r'<[^>]*>', '', title_html).strip()
                href = href.strip()
                
                # 简化的筛选条件
                if title and len(title) > 2 and len(title) < 100 and href and len(href) > 5:
                    # 快速清理URL
                    clean_url = href.strip()
                    
                    # 确保URL有协议
                    if not clean_url.startswith(('http://', 'https://')):
                        continue
                    
                    # 基本过滤：跳过JavaScript链接和百度内部链接
                    if 'javascript:' not in clean_url and 'baidu.com/link?' not in clean_url:
                        if clean_url not in seen_urls_temp:
                            results.append({
                                'title': title,
                                'summary': '',  # 不提取摘要，减少处理时间
                                'url': clean_url,
                                'cover_url': ''
                            })
                            seen_urls_temp.add(clean_url)
                            
                            # 立即限制结果数量
                            if len(results) >= 10:
                                break
            
            # 实现高级去重逻辑
            final_results = self._deduplicate_results(results)
            
            logger.info(f"原始结果数: {len(results)}, 最终去重结果数: {len(final_results)}")
            
            # 更新unique_results变量名以匹配后续使用
            unique_results = final_results
            
            return {
                'status': 'success',
                'status_code': response.status_code,
                'keyword': keyword,
                'search_url': search_url,
                'result_count': len(unique_results),
                'results': unique_results
            }
        except Exception as e:
            logger.error(f"搜索过程中出错: {str(e)}")
            return {
                'status': 'error',
                'error_type': 'exception',
                'error_message': str(e),
                'keyword': keyword
            }
        
    def _deduplicate_results(self, results):
        """极致简化的去重方法，最大限度减少处理时间"""
        if not results:
            return []
            
        unique_results = []
        seen_urls = set()
        
        # 超快速去重，只保留前几个唯一URL
        for result in results:
            url = result.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
                # 立即限制结果数量到5个
                if len(unique_results) >= 5:
                    break
        
        # 移除排序，直接返回结果
        return unique_results
    
    # _process_and_add_result方法已移除，使用正则表达式直接处理结果
        
    def _clean_url(self, url):
        """简化的URL清理方法，减少处理时间"""
        try:
            # 只保留基本的URL清理
            if url.startswith(('http://', 'https://')):
                # 移除空格和末尾标点
                clean = url.split()[0].rstrip(',.?!;:')
                return clean
            elif 'baidu.com/link?' in url:
                return 'http://' + url if not url.startswith('http') else url
            # 移除其他复杂处理
            return None
        except:
            # 出错时简单返回None，不记录详细错误
            return None
    
    def _is_baidu_internal(self, url):
        """简化的百度内部链接检查"""
        try:
            # 只检查是否包含baidu.com域名
            if 'baidu.com' in url:
                # 保留主要的百度内容域名
                content_domains = ['baike.baidu.com', 'zhidao.baidu.com', 'tieba.baidu.com', 
                                  'wenku.baidu.com', 'map.baidu.com']
                for domain in content_domains:
                    if domain in url:
                        return False
                # 其他baidu.com链接视为内部链接
                return True
            return False
        except:
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