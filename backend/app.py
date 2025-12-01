#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能瞭望数据分析处理系统 - 后端应用
功能：用户认证、数据爬取、数据存储与管理
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
import sqlite3
import os
import sys
import json
import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# 添加codedemo目录到系统路径，以便导入baidu_spider
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
CODEDEMO_DIR = os.path.join(PROJECT_DIR, 'codedemo')
sys.path.insert(0, CODEDEMO_DIR)

# 导入百度爬虫模块
from baidu_spider import BaiduSpider

# 初始化Flask应用
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # 生产环境需要修改为更安全的密钥

# 数据库配置
DATABASE = os.path.join(BASE_DIR, 'database.db')

# 初始化数据库
def init_db():
    """初始化SQLite数据库，创建用户表和数据仓库表"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # 创建用户表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 创建数据仓库表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS data_repository (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        url TEXT NOT NULL,
        summary TEXT,
        search_keyword TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 检查是否已有管理员用户
    cursor.execute("SELECT * FROM users WHERE username='admin'")
    if not cursor.fetchone():
        # 创建默认管理员用户，密码：admin888
        admin_password = generate_password_hash('admin888')
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            ('admin', admin_password)
        )
    
    conn.commit()
    conn.close()

# 登录装饰器
def login_required(f):
    """验证用户是否已登录的装饰器"""
    # 使用原始函数名作为endpoint名称
    def decorated_view(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_view.__name__ = f.__name__
    decorated_view.__doc__ = f.__doc__
    return decorated_view

# 登录路由
@app.route('/login', methods=['GET', 'POST'])

def login():
    """用户登录页面"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect(url_for('dashboard'))
        else:
            flash('用户名或密码错误')
    
    return render_template('login.html')

# 注销路由
@app.route('/logout')
def logout():
    """用户注销"""
    session.clear()
    return redirect(url_for('login'))

# 仪表盘路由
@app.route('/')
@login_required
def dashboard():
    """后台主页"""
    return render_template('dashboard.html')

# 搜索路由
@app.route('/search', methods=['POST'])
@login_required
def search():
    """调用百度爬虫进行搜索"""
    try:
        keyword = request.form['keyword']
        
        if not keyword or len(keyword.strip()) == 0:
            return jsonify({
                'status': 'error',
                'message': '请输入搜索关键词'
            })
        
        # 调用百度爬虫
        spider = BaiduSpider()
        result = spider.search(keyword)
        
        return jsonify({
            'status': 'success',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'搜索失败: {str(e)}'
        })

# 保存数据路由
@app.route('/save_data', methods=['POST'])
@login_required
def save_data():
    """批量保存搜索结果到数据库"""
    try:
        data = request.json
        results = data.get('results', [])
        keyword = data.get('keyword', '')
        
        if not results:
            return jsonify({
                'status': 'error',
                'message': '没有数据需要保存'
            })
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        saved_count = 0
        for item in results:
            title = item.get('title', '')
            url = item.get('url', '')
            summary = item.get('summary', '')
            
            # 插入数据
            cursor.execute(
                "INSERT INTO data_repository (title, url, summary, search_keyword) VALUES (?, ?, ?, ?)",
                (title, url, summary, keyword)
            )
            saved_count += 1
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'message': f'成功保存 {saved_count} 条数据',
            'count': saved_count
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'保存失败: {str(e)}'
        })

# 获取数据仓库路由
@app.route('/data_repository')
@login_required
def data_repository():
    """数据仓库页面"""
    return render_template('data_repository.html')

# 查询数据仓库数据路由
@app.route('/get_repository_data')
@login_required
def get_repository_data():
    """获取数据仓库中的数据"""
    try:
        # 获取查询参数
        keyword = request.args.get('keyword', '')
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')
        
        # 构建查询
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        query = "SELECT id, title, url, summary, search_keyword, created_at FROM data_repository WHERE 1=1"
        params = []
        
        if keyword:
            query += " AND (title LIKE ? OR summary LIKE ? OR search_keyword LIKE ?)"
            params.extend([f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'])
        
        if date_from:
            query += " AND created_at >= ?"
            params.append(date_from)
        
        if date_to:
            query += " AND created_at <= ?"
            params.append(date_to)
        
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        # 格式化结果
        formatted_results = []
        for row in results:
            formatted_results.append({
                'id': row[0],
                'title': row[1],
                'url': row[2],
                'summary': row[3],
                'search_keyword': row[4],
                'created_at': row[5]
            })
        
        return jsonify({
            'status': 'success',
            'data': formatted_results
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'查询失败: {str(e)}'
        })

if __name__ == '__main__':
    # 初始化数据库
    init_db()
    
    # 启动应用
    app.run(host='0.0.0.0', port=5000, debug=True)