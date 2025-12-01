// 数据仓库功能脚本

// 查询表单提交处理
document.getElementById('queryForm').addEventListener('submit', function(e) {
    e.preventDefault();
    queryRepositoryData();
});

// 重置查询按钮事件
document.getElementById('resetQuery').addEventListener('click', function() {
    document.getElementById('searchKeyword').value = '';
    document.getElementById('dateFrom').value = '';
    document.getElementById('dateTo').value = '';
    
    document.getElementById('repositoryData').innerHTML = `
        <div class="empty-state">
            <p>请输入查询条件获取数据</p>
        </div>
    `;
    
    showQueryStatus('', '');
});

// 查询数据仓库
function queryRepositoryData() {
    const keyword = document.getElementById('searchKeyword').value.trim();
    const dateFrom = document.getElementById('dateFrom').value;
    const dateTo = document.getElementById('dateTo').value;
    
    // 显示加载状态
    showQueryLoading(true);
    showQueryStatus('', '');
    document.getElementById('repositoryData').innerHTML = '';
    
    // 构建查询参数
    const params = new URLSearchParams();
    if (keyword) params.append('keyword', keyword);
    if (dateFrom) params.append('date_from', dateFrom);
    if (dateTo) params.append('date_to', dateTo);
    
    const queryString = params.toString();
    const url = `/get_repository_data${queryString ? `?${queryString}` : ''}`;
    
    // 发送查询请求
    fetch(url)
        .then(response => response.json())
        .then(data => {
            showQueryLoading(false);
            
            if (data.status === 'success') {
                displayRepositoryData(data.data);
            } else {
                showQueryStatus(data.message || '查询失败', 'error');
                document.getElementById('repositoryData').innerHTML = `
                    <div class="empty-state">
                        <p>查询失败，请稍后重试</p>
                    </div>
                `;
            }
        })
        .catch(error => {
            showQueryLoading(false);
            showQueryStatus('网络错误，请检查您的连接', 'error');
            document.getElementById('repositoryData').innerHTML = `
                <div class="empty-state">
                    <p>查询失败，请稍后重试</p>
                </div>
            `;
        });
}

// 显示查询加载状态
function showQueryLoading(show) {
    const loadingIndicator = document.getElementById('queryLoading');
    if (show) {
        loadingIndicator.style.display = 'flex';
    } else {
        loadingIndicator.style.display = 'none';
    }
}

// 显示查询状态消息
function showQueryStatus(message, type) {
    const statusElement = document.getElementById('queryStatus');
    
    statusElement.className = 'status-message';
    statusElement.textContent = message;
    
    if (message && type) {
        statusElement.classList.add(type);
    }
}

// 显示数据仓库数据
function displayRepositoryData(data) {
    const dataContainer = document.getElementById('repositoryData');
    
    if (!data || data.length === 0) {
        dataContainer.innerHTML = `
            <div class="empty-state">
                <p>没有找到符合条件的数据</p>
            </div>
        `;
        return;
    }
    
    // 创建表格
    let html = `
        <table class="data-table">
            <thead>
                <tr>
                    <th>标题</th>
                    <th>URL</th>
                    <th>摘要</th>
                    <th>搜索关键词</th>
                    <th>创建时间</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    data.forEach(item => {
        const formattedDate = formatDateTime(item.created_at);
        html += `
            <tr>
                <td>
                    <a href="${item.url}" target="_blank" rel="noopener noreferrer">
                        ${item.title || '无标题'}
                    </a>
                </td>
                <td>
                    <a href="${item.url}" target="_blank" rel="noopener noreferrer">
                        ${item.url}
                    </a>
                </td>
                <td>${item.summary || 'N/A'}</td>
                <td>${item.search_keyword}</td>
                <td>${formattedDate}</td>
            </tr>
        `;
    });
    
    html += `
            </tbody>
        </table>
    `;
    
    dataContainer.innerHTML = html;
    
    // 显示成功消息
    showQueryStatus(`共找到 ${data.length} 条数据`, 'info');
}

// 格式化日期时间
function formatDateTime(dateString) {
    if (!dateString) return '';
    
    try {
        const date = new Date(dateString);
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        const seconds = String(date.getSeconds()).padStart(2, '0');
        
        return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
    } catch (error) {
        return dateString;
    }
}

// 页面加载完成后初始化
window.addEventListener('DOMContentLoaded', function() {
    // 自动加载默认数据（可选）
    // queryRepositoryData();
});