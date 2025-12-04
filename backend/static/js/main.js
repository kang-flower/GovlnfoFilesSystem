// 搜索功能主脚本

// 搜索表单提交处理
document.getElementById('searchForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const keyword = document.getElementById('keyword').value.trim();
    if (!keyword) {
        showStatus('请输入搜索关键词', 'error');
        return;
    }
    
    // 显示加载状态
    showLoading(true);
    showStatus('', '');
    document.getElementById('searchResults').innerHTML = '';
    
    // 使用重试函数发送搜索请求
    fetchWithRetry('/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ keyword: keyword })
    }, 3, 10000)
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        showLoading(false);
        
        if (data.status === 'success') {
            displaySearchResults(data.data, keyword);
        } else {
            const errorMsg = data.message || '搜索失败，请稍后重试';
            showStatus(errorMsg, 'error');
            document.getElementById('searchResults').innerHTML = `
                <div class="empty-state">
                    <p>${errorMsg}</p>
                </div>
            `;
        }
    })
    .catch(error => {
        showLoading(false);
        console.error('搜索请求错误:', error);
        
        let errorMsg = '网络错误，请检查您的连接';
        if (error.message && error.message.includes('timeout')) {
            errorMsg = '请求超时，请稍后重试';
        }
        
        showStatus(errorMsg, 'error');
        document.getElementById('searchResults').innerHTML = `
            <div class="empty-state">
                <p>搜索失败，请稍后重试</p>
            </div>
        `;
    });
});

// 带重试和超时的fetch函数
const fetchWithRetry = async (url, options, retries = 3) => {
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000);
        
        const response = await fetch(url, {
            ...options,
            signal: controller.signal,
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                ...options.headers
            }
        });
        
        clearTimeout(timeoutId);
        return response;
    } catch (error) {
        if (retries <= 0) throw error;
        await new Promise(res => setTimeout(res, 1000 * (4 - retries)));
        return fetchWithRetry(url, options, retries - 1);
    }
};

// 显示加载状态
function showLoading(show) {
    const loadingIndicator = document.getElementById('loadingIndicator');
    if (show) {
        loadingIndicator.style.display = 'flex';
    } else {
        loadingIndicator.style.display = 'none';
    }
}

// 显示状态消息
function showStatus(message, type) {
    const statusElement = document.getElementById('searchStatus');
    
    statusElement.className = 'status-message';
    statusElement.textContent = message;
    
    if (message && type) {
        statusElement.classList.add(type);
    }
}

// 显示搜索结果
function displaySearchResults(results, keyword) {
    const resultsContainer = document.getElementById('searchResults');
    
    // 确保results是数组
    const resultsArray = Array.isArray(results) ? results : [];
    
    if (!resultsArray || resultsArray.length === 0) {
        resultsContainer.innerHTML = `
            <div class="empty-state">
                <p>没有找到相关结果</p>
            </div>
        `;
        return;
    }
    
    // 保存当前关键词
    window.currentKeyword = keyword;
    
    let html = '';
    resultsArray.forEach((item, index) => {
        html += `
            <div class="result-item" data-index="${index}">
                <div class="result-header">
                    <input type="checkbox" class="result-checkbox" data-index="${index}">
                    <div>
                        <div class="result-title">
                            <a href="${item.url}" target="_blank" rel="noopener noreferrer">
                                ${item.title || '无标题'}
                            </a>
                        </div>
                        <div class="result-url">${item.url}</div>
                        ${item.summary ? `<div class="result-summary">${item.summary}</div>` : ''}
                    </div>
                </div>
            </div>
        `;
    });
    
    resultsContainer.innerHTML = html;
    
    // 保存结果到全局变量
    window.searchResults = resultsArray;
    
    // 绑定复选框事件
    bindCheckboxEvents();
    
    // 绑定结果项点击事件
    bindResultItemClickEvents();
    
    // 启用保存按钮
    document.getElementById('saveSelectedButton').disabled = false;
}

// 绑定复选框事件
function bindCheckboxEvents() {
    const checkboxes = document.querySelectorAll('.result-checkbox');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const index = this.getAttribute('data-index');
            const resultItem = document.querySelector(`.result-item[data-index="${index}"]`);
            
            if (this.checked) {
                resultItem.classList.add('selected');
            } else {
                resultItem.classList.remove('selected');
            }
            
            updateSaveButtonState();
        });
    });
}

// 绑定结果项点击事件
function bindResultItemClickEvents() {
    const resultItems = document.querySelectorAll('.result-item');
    resultItems.forEach(item => {
        item.addEventListener('click', function(e) {
            // 如果点击的是链接或复选框，不触发选择
            if (e.target.tagName === 'A' || e.target.tagName === 'INPUT') {
                return;
            }
            
            const index = this.getAttribute('data-index');
            const checkbox = this.querySelector('.result-checkbox');
            
            checkbox.checked = !checkbox.checked;
            
            if (checkbox.checked) {
                this.classList.add('selected');
            } else {
                this.classList.remove('selected');
            }
            
            updateSaveButtonState();
        });
    });
}

// 更新保存按钮状态
function updateSaveButtonState() {
    const checkedBoxes = document.querySelectorAll('.result-checkbox:checked');
    const saveButton = document.getElementById('saveSelectedButton');
    
    saveButton.disabled = checkedBoxes.length === 0;
}

// 保存选中数据
function saveSelectedData() {
    const checkedBoxes = document.querySelectorAll('.result-checkbox:checked');
    
    if (checkedBoxes.length === 0) {
        showStatus('请至少选择一条数据进行保存', 'error');
        return;
    }
    
    const selectedResults = [];
    checkedBoxes.forEach(checkbox => {
        const index = checkbox.getAttribute('data-index');
        if (window.searchResults && window.searchResults[index]) {
            selectedResults.push(window.searchResults[index]);
        }
    });
    
    // 显示加载状态
    showLoading(true);
    showStatus('', '');
    
    // 发送保存请求
    fetch('/save_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            results: selectedResults,
            keyword: window.currentKeyword
        })
    })
    .then(response => response.json())
    .then(data => {
        showLoading(false);
        
        if (data.status === 'success') {
            showStatus(data.message, 'success');
            
            // 清空选中状态
            const checkboxes = document.querySelectorAll('.result-checkbox:checked');
            checkboxes.forEach(checkbox => {
                checkbox.checked = false;
                const index = checkbox.getAttribute('data-index');
                const resultItem = document.querySelector(`.result-item[data-index="${index}"]`);
                if (resultItem) {
                    resultItem.classList.remove('selected');
                }
            });
            
            updateSaveButtonState();
        } else {
            showStatus(data.message || '保存失败', 'error');
        }
    })
    .catch(error => {
        showLoading(false);
        showStatus('网络错误，请检查您的连接', 'error');
    });
}

// 保存按钮点击事件
document.getElementById('saveSelectedButton').addEventListener('click', saveSelectedData);

// 页面加载完成后初始化
window.addEventListener('DOMContentLoaded', function() {
    // 初始化保存按钮状态
    updateSaveButtonState();
    
    // 初始化全局变量
    window.searchResults = [];
    window.currentKeyword = '';
});