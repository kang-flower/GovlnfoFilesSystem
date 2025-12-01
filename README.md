# 智能瞭望数据分析处理系统

一个基于Flask的数据分析处理系统，集成百度爬虫功能，支持数据采集、存储、查询和管理。

## 功能特点

- **用户认证**：基于SQLite的用户登录系统，默认管理员账户：admin/admin888
- **数据搜索**：对接百度爬虫，获取搜索结果
- **数据管理**：批量保存搜索结果到数据库
- **数据仓库**：支持按关键词和日期范围查询数据
- **响应式设计**：适配各种屏幕尺寸的设备

## 技术栈

- **后端**：Python 3 + Flask
- **数据库**：SQLite
- **前端**：HTML5 + CSS3 + JavaScript

## 安装指南

### 1. 环境要求

- Python 3.6+
- pip（Python包管理器）

### 2. 安装步骤

1. **克隆项目（如果适用）**

2. **创建虚拟环境**
   ```bash
   python -m venv venv
   ```

3. **激活虚拟环境**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

5. **启动应用**
   ```bash
   cd backend
   python start.py
   ```

6. **访问系统**
   打开浏览器，访问 http://localhost:5000

## 使用说明

### 登录
- 输入用户名：admin
- 输入密码：admin888
- 点击"登录"按钮

### 数据搜索
1. 在首页输入搜索关键词
2. 点击"搜索"按钮
3. 查看搜索结果
4. 勾选需要保存的数据
5. 点击"保存选中数据"按钮

### 数据仓库
1. 点击导航栏中的"数据仓库"
2. 输入查询条件（可选）：
   - 关键词搜索
   - 日期范围筛选
3. 点击"查询"按钮查看结果
4. 点击URL链接可在新标签页中打开原始页面

## 开发说明

### 项目结构

```
GovlnfoFilesSystem/
├── backend/                 # 后端应用目录
│   ├── templates/           # HTML模板
│   │   ├── login.html       # 登录页面
│   │   ├── dashboard.html   # 仪表盘页面
│   │   └── data_repository.html  # 数据仓库页面
│   ├── static/              # 静态资源
│   │   ├── css/             # 样式文件
│   │   ├── js/              # JavaScript脚本
│   │   └── images/          # 图片资源
│   ├── app.py               # Flask应用主文件
│   └── start.py             # 启动脚本
├── codedemo/                # 百度爬虫目录
│   └── baidu_spider.py      # 百度爬虫模块
├── requirements.txt         # Python依赖列表
└── 开发日志.md              # 开发日志
```

### 待开发功能

- AI数据提炼功能
- PDF生成和预览下载
- 数据分页加载
- 系统性能优化

## 注意事项

- 本系统仅用于学习和演示
- 生产环境部署时请修改`app.py`中的`secret_key`
- 爬虫功能可能受到百度反爬机制的限制
- 定期备份数据库文件（database.db）