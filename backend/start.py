#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能瞭望数据分析处理系统 - 启动脚本
"""

import os
import sys

# 确保在正确的目录下运行
if not os.path.exists('app.py'):
    print("错误：请在backend目录下运行此脚本")
    sys.exit(1)

print("智能瞭望数据分析处理系统启动中...")
print("正在启动Flask应用服务器...")

# 导入并运行app
from app import app, init_db

if __name__ == '__main__':
    # 确保数据库已初始化
    init_db()
    print("数据库初始化完成")
    print("应用服务正在运行...")
    print("访问地址: http://localhost:5000")
    print("登录账户: admin / admin888")
    print("按 Ctrl+C 停止服务")
    print("-" * 60)
    
    # 启动应用
    app.run(host='0.0.0.0', port=5000, debug=True)