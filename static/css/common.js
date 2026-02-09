/**
 * XHSecTeam 通用 JavaScript 工具库
 * 被 single.html 和 maccmsBAI.html 共同引用
 */

// API 基础地址
const API_BASE = 'http://127.0.0.1:5000';

/**
 * HTML 转义函数，防止 XSS
 * @param {string|*} text - 需要转义的文本
 * @returns {string} 转义后的安全 HTML 字符串
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text == null ? '' : String(text);
    return div.innerHTML;
}

/**
 * 检查扫描引擎服务器状态
 * 自动更新页面上的状态指示器
 */
async function checkServer() {
    const dot = document.getElementById('engineDot');
    const text = document.getElementById('engineText');
    const pillDot = document.getElementById('serverDot');
    const pillText = document.getElementById('serverText');
    
    try {
        const resp = await fetch(API_BASE + '/');
        if (resp.ok) {
            // 服务器在线
            if (dot) dot.style.background = '#22c55e';
            if (text) text.textContent = '扫描引擎在线';
            if (pillDot) pillDot.classList.remove('offline');
            if (pillText) pillText.textContent = '服务运行中';
            return true;
        } else {
            throw new Error('服务响应异常');
        }
    } catch (e) {
        // 服务器离线
        if (dot) dot.style.background = '#ef4444';
        if (text) text.textContent = '扫描引擎未启动';
        if (pillDot) pillDot.classList.add('offline');
        if (pillText) pillText.textContent = '服务未启动';
        return false;
    }
}

/**
 * 发送 AI 消息（基础版本）
 * 可在各页面中重写或扩展
 */
function sendAiMessage() {
    const input = document.getElementById('aiInput');
    const messagesDiv = document.getElementById('aiMessages');
    if (!input || !messagesDiv) return;
    
    const text = input.value.trim();
    if (!text) return;
    
    // 添加用户消息
    const userMsg = document.createElement('div');
    userMsg.className = 'ai-message user';
    userMsg.textContent = text;
    messagesDiv.appendChild(userMsg);
    
    // 添加 AI 回复（基础回复，可在页面中重写 generateAiResponse 来自定义）
    const aiMsg = document.createElement('div');
    aiMsg.className = 'ai-message assistant';
    if (typeof generateAiResponse === 'function') {
        aiMsg.innerHTML = generateAiResponse(text);
    } else {
        aiMsg.textContent = '我已收到你的问题，正在分析中...';
    }
    messagesDiv.appendChild(aiMsg);
    
    // 滚动到底部
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    
    // 清空输入框
    input.value = '';
}

/**
 * 添加 AI 对话消息
 * @param {string} userMsg - 用户消息（可选）
 * @param {string} response - AI 回复（可选）
 */
function addAiMessage(userMsg, response) {
    const messagesDiv = document.getElementById('aiMessages');
    if (!messagesDiv) return;
    
    if (userMsg) {
        const uMsg = document.createElement('div');
        uMsg.className = 'ai-message user';
        uMsg.textContent = userMsg;
        messagesDiv.appendChild(uMsg);
    }
    
    if (response) {
        const aMsg = document.createElement('div');
        aMsg.className = 'ai-message assistant';
        aMsg.innerHTML = response;
        messagesDiv.appendChild(aMsg);
    }
    
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

/**
 * 聚焦到 AI 输入框
 */
function focusAi() {
    const input = document.getElementById('aiInput');
    if (input) {
        input.focus();
    }
}

/**
 * 自动调整 textarea 高度
 * @param {HTMLTextAreaElement} textarea - 文本域元素
 */
function autoResize(textarea) {
    textarea.style.height = 'auto';
    const newHeight = Math.min(textarea.scrollHeight, 568);
    textarea.style.height = newHeight + 'px';
}

/**
 * 切换 AI 面板显示状态（移动端）
 */
function toggleAiPanel() {
    const panel = document.getElementById('aiPanel');
    if (panel) {
        panel.classList.toggle('active');
    }
}

/**
 * 打开 AI 面板
 */
function openAiPanel() {
    const panel = document.getElementById('aiPanel');
    if (panel && !panel.classList.contains('active')) {
        panel.classList.add('active');
    }
}

/**
 * 页面导航相关
 */
let navCollapsed = false;

/**
 * 切换导航栏展开/收起状态
 */
function toggleNavbar() {
    navCollapsed = !navCollapsed;
    const navbar = document.getElementById('navbar');
    const mainLayout = document.querySelector('.main-layout');
    if (navbar) navbar.classList.toggle('collapsed', navCollapsed);
    if (mainLayout) mainLayout.classList.toggle('nav-collapsed', navCollapsed);
}

/**
 * 收起导航栏
 */
function collapseNavbar() {
    if (!navCollapsed) {
        navCollapsed = true;
        const navbar = document.getElementById('navbar');
        const mainLayout = document.querySelector('.main-layout');
        if (navbar) navbar.classList.add('collapsed');
        if (mainLayout) mainLayout.classList.add('nav-collapsed');
    }
}

/**
 * 展开导航栏
 */
function expandNavbar() {
    if (navCollapsed) {
        navCollapsed = false;
        const navbar = document.getElementById('navbar');
        const mainLayout = document.querySelector('.main-layout');
        if (navbar) navbar.classList.remove('collapsed');
        if (mainLayout) mainLayout.classList.remove('nav-collapsed');
    }
}

/**
 * 代码复制功能增强
 * 为 .vuln-item-code 元素添加复制按钮
 */
function enhanceVulnCodeBlocks() {
    document.querySelectorAll('.vuln-item-code').forEach((el) => {
        if (el.querySelector('.code-copy-btn')) return;
        
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'code-copy-btn';
        btn.textContent = '复制';
        
        btn.addEventListener('click', async () => {
            const raw = (el.innerText || '').trim();
            const text = raw.replace(/^利用方法:\s*/g, '').trim();
            
            try {
                await navigator.clipboard.writeText(text);
                btn.classList.add('copied');
                const prev = btn.textContent;
                btn.textContent = '已复制';
                setTimeout(() => {
                    btn.classList.remove('copied');
                    btn.textContent = prev;
                }, 1100);
            } catch (_) {
                // 降级方案：使用 execCommand
                const textarea = document.createElement('textarea');
                textarea.value = text;
                textarea.style.position = 'fixed';
                textarea.style.left = '-9999px';
                document.body.appendChild(textarea);
                textarea.focus();
                textarea.select();
                const ok = document.execCommand('copy');
                document.body.removeChild(textarea);
                if (ok) {
                    btn.classList.add('copied');
                    const prev = btn.textContent;
                    btn.textContent = '已复制';
                    setTimeout(() => {
                        btn.classList.remove('copied');
                        btn.textContent = prev;
                    }, 1100);
                }
            }
        });
        
        el.appendChild(btn);
    });
}

/**
 * 初始化通用功能
 * 在 DOMContentLoaded 时自动调用
 */
function initCommon() {
    // 检查服务器状态
    checkServer();
    
    // 初始化代码块复制按钮
    enhanceVulnCodeBlocks();
    
    // 监听 AI 输入框键盘事件
    const aiInput = document.getElementById('aiInput');
    if (aiInput) {
        aiInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendAiMessage();
            }
        });
        
        // 自动调整高度
        aiInput.addEventListener('input', () => {
            autoResize(aiInput);
        });
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', initCommon);

/**
 * 切换明暗主题
 */
function toggleTheme() {
    const body = document.body;
    const isDark = body.classList.toggle('dark-theme');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    // TODO: 实现完整的主题切换逻辑
    console.log('主题切换为:', isDark ? '暗色' : '亮色');
}

/**
 * 打开订阅会员页面
 * @param {Event} event - 点击事件
 */
function openSubscription(event) {
    if (event) event.preventDefault();
    alert('订阅会员功能开发中...');
}

/**
 * 打开设置面板
 */
function openSettings() {
    // TODO: 实现设置面板
    console.log('打开设置');
    alert('设置功能开发中...');
}

/**
 * 打开个人中心
 */
function openProfile() {
    // TODO: 实现个人中心
    console.log('打开个人中心');
    alert('个人中心功能开发中...');
}

/**
 * 初始化主题（根据本地存储）
 */
function initTheme() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
    }
}
initTheme();
