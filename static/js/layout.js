/**
 * XHSecTeam 通用布局组件
 * 从外部 HTML 文件加载导航栏、浮动导航栏组件
 * 统一管理，便于维护
 */

// 默认基础路径（用于子目录页面调整）
let BASE_PATH = '';

// 组件文件路径（相对于根目录）
const COMPONENT_PATHS = {
    navbar: 'static/components/navbar.html',
    floatingNav: 'static/components/floating-nav.html'
};

// 设置基础路径（子目录页面使用）
function setBasePath(path) {
    BASE_PATH = path;
}

// 获取完整路径
function getPath(pageName) {
    return BASE_PATH + pageName;
}

// ============ 底部版权 HTML 模板 ============
const FOOTER_TEMPLATE = `
<footer class="site-footer">
    <div class="footer-content">
        <span class="footer-copyright">© 2026 XHSecTeam. All Rights Reserved.</span>
        <span class="footer-sep">|</span>
        <span class="footer-text">Asset Mapping & Security Platform</span>
    </div>
</footer>
`;

// ============ 漏洞分析页面搜索框 HTML ============
const FLOATING_NAV_SEARCH_HTML = `
<div class="floating-nav-search">
    <input type="text" id="floatingVulnSearch" placeholder="搜索漏洞..." class="floating-nav-search-input">
    <button class="floating-nav-search-btn" onclick="if(typeof searchVulnerabilities==='function')searchVulnerabilities()">
        <svg viewBox="0 0 24 24" width="16" height="16"><circle cx="11" cy="11" r="8" stroke="currentColor" fill="none" stroke-width="2"/><path d="m21 21-4.35-4.35" stroke="currentColor" fill="none" stroke-width="2" stroke-linecap="round"/></svg>
    </button>
</div>
`;

// ============ 从外部文件加载 HTML 组件 ============

/**
 * 加载 HTML 组件文件
 * @param {string} componentPath - 组件文件路径（相对于根目录）
 * @returns {Promise<string>} HTML 内容
 */
async function fetchComponent(componentPath) {
    try {
        const fullPath = getPath(componentPath);
        // 添加时间戳防止缓存
        const cacheBuster = `?t=${Date.now()}`;
        console.log('[Layout] 加载组件:', fullPath + cacheBuster);
        const response = await fetch(fullPath + cacheBuster, {
            cache: 'no-store'
        });
        if (!response.ok) {
            throw new Error(`Failed to load component: ${fullPath} (${response.status})`);
        }
        const html = await response.text();
        console.log('[Layout] 组件加载成功，长度:', html.length);
        return html;
    } catch (error) {
        console.error('[Layout] 组件加载失败:', error);
        return '';
    }
}

/**
 * 调整容器内所有链接的路径
 * @param {HTMLElement} container - 容器元素
 * @param {string} basePath - 基础路径前缀
 */
function adjustPaths(container, basePath) {
    if (!basePath) return;
    
    // 调整所有带 data-link 属性的元素
    container.querySelectorAll('[data-link]').forEach(el => {
        const originalPath = el.getAttribute('data-link');
        const newPath = basePath + originalPath;
        
        // 根据元素类型设置对应属性
        if (el.tagName === 'A') {
            el.href = newPath;
        } else if (el.tagName === 'IMG') {
            el.src = newPath;
        } else if (el.tagName === 'BUTTON') {
            el.onclick = () => location.href = newPath;
        }
    });
}

// ============ 加载导航栏组件 ============

/**
 * 加载导航栏组件（从 navbar.html）
 * @param {Object} config 配置项
 * @param {string} config.activeTab - 当前活动的标签 (dashboard, aisearch, single, vuln-analysis)
 * @param {string} config.basePath - 基础路径（子目录页面使用，如 '../'）
 */
async function loadNavbar(config = {}) {
    const navbar = document.getElementById('navbar');
    if (!navbar) {
        console.error('Navbar container not found');
        return null;
    }
    
    const { activeTab = '', basePath = '' } = config;
    
    // 设置基础路径
    if (basePath) setBasePath(basePath);
    
    // 从外部文件加载 HTML
    const html = await fetchComponent(COMPONENT_PATHS.navbar);
    if (!html) {
        console.error('Failed to load navbar component');
        return null;
    }
    
    // 填充导航栏 HTML
    navbar.innerHTML = html;
    
    // 调整路径
    adjustPaths(navbar, basePath);
    
    // 设置活动标签
    if (activeTab) {
        navbar.querySelectorAll('.nav-tab').forEach(tab => {
            tab.classList.remove('active');
            if (tab.dataset.tab === activeTab) {
                tab.classList.add('active');
            }
        });
    }
    
    return navbar;
}

/**
 * 加载浮动导航栏组件（从 floating-nav.html）
 * @param {Object} config 配置项
 * @param {string} config.title - 标题
 * @param {string} config.activePage - 当前活动页面 (index, single, vuln-analysis, aisearch, logs)
 * @param {string} config.extraHtml - 额外的HTML（如搜索框）
 * @param {string} config.basePath - 基础路径
 */
async function loadFloatingNav(config = {}) {
    const floatingNav = document.getElementById('floatingNav');
    if (!floatingNav) {
        console.error('FloatingNav container not found');
        return null;
    }
    
    const { title = '仪表盘', activePage = '', extraHtml = '', basePath = '' } = config;
    
    // 设置基础路径
    if (basePath) setBasePath(basePath);
    
    // 从外部文件加载 HTML
    const html = await fetchComponent(COMPONENT_PATHS.floatingNav);
    if (!html) {
        console.error('Failed to load floating-nav component');
        return null;
    }
    
    // 填充浮动导航栏 HTML
    floatingNav.innerHTML = html;
    
    // 调整路径
    adjustPaths(floatingNav, basePath);
    
    // 为浮动导航按钮绑定点击事件
    floatingNav.querySelectorAll('.floating-nav-btn[data-link]').forEach(btn => {
        const link = btn.getAttribute('data-link');
        btn.onclick = () => location.href = basePath + link;
    });
    
    // 设置标题
    const titleEl = floatingNav.querySelector('#floatingNavTitle');
    if (titleEl && title) {
        titleEl.textContent = title;
    }
    
    // 设置活动按钮
    if (activePage) {
        floatingNav.querySelectorAll('.floating-nav-btn').forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.page === activePage) {
                btn.classList.add('active');
            }
        });
    }
    
    // 添加额外内容（如搜索框）- 插入到头像前面
    const extraContainer = floatingNav.querySelector('#floatingNavExtra');
    if (extraContainer && extraHtml) {
        const avatar = extraContainer.querySelector('.floating-nav-avatar');
        if (avatar) {
            avatar.insertAdjacentHTML('beforebegin', extraHtml);
        } else {
            extraContainer.insertAdjacentHTML('afterbegin', extraHtml);
        }
    }
    
    // 初始化指示器动画
    setTimeout(() => initFloatingNavIndicator(), 100);
    
    return floatingNav;
}

/**
 * 加载AI面板组件（预留接口，目前各页面保留原有HTML结构）
 * @param {Object} config 配置项
 */
function loadAiPanel(config = {}) {
    // 目前各页面保留原有的AI面板HTML结构
    // 此函数预留用于后续扩展
    return document.getElementById('aiPanel');
}

/**
 * 加载底部版权组件
 */
function loadFooter() {
    const content = document.querySelector('.content');
    if (!content) {
        console.error('Content container not found');
        return null;
    }
    
    // 创建并插入底部版权
    const footerDiv = document.createElement('div');
    footerDiv.innerHTML = FOOTER_TEMPLATE;
    content.appendChild(footerDiv.firstElementChild);
    
    return content.querySelector('.site-footer');
}

/**
 * 一次性加载所有组件
 * @param {Object} config 配置项
 */
async function loadAllComponents(config = {}) {
    const results = {};
    
    if (config.navbar !== false) {
        results.navbar = await loadNavbar(config.navbar || {});
    }
    
    if (config.floatingNav !== false) {
        results.floatingNav = await loadFloatingNav(config.floatingNav || {});
    }
    
    if (config.aiPanel !== false) {
        results.aiPanel = loadAiPanel(config.aiPanel || {});
    }
    
    // 检测服务器状态
    if (typeof checkServer === 'function') {
        checkServer();
    }
    
    return results;
}

// ============ 通用辅助函数 ============

// 防抖函数
if (typeof debounce === 'undefined') {
    window.debounce = function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    };
}

// 代码复制功能
function copyCode(button) {
    const codeBlock = button.closest('.vuln-item-code');
    if (!codeBlock) return;
    
    const codeText = codeBlock.innerText.replace(button.innerText, '').trim();
    
    navigator.clipboard.writeText(codeText).then(() => {
        const originalText = button.textContent;
        button.textContent = '已复制';
        button.classList.add('copied');
        setTimeout(() => {
            button.textContent = originalText;
            button.classList.remove('copied');
        }, 2000);
    }).catch(() => {
        const textarea = document.createElement('textarea');
        textarea.value = codeText;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        
        button.textContent = '已复制';
        button.classList.add('copied');
        setTimeout(() => {
            button.textContent = '复制';
            button.classList.remove('copied');
        }, 2000);
    });
}

// 浮动导航指示器动画
function initFloatingNavIndicator() {
    const navBtns = document.querySelectorAll('.floating-nav-btn');
    const indicator = document.getElementById('floatingNavIndicator');
    if (!indicator || navBtns.length === 0) return;

    function updateIndicator(btn, animate = true) {
        if (!btn) return;
        const rect = btn.getBoundingClientRect();
        const innerRect = document.getElementById('floatingNavInner').getBoundingClientRect();
        const offset = rect.left - innerRect.left;
        indicator.style.display = 'block';
        if (animate) {
            indicator.style.transition = 'transform 0.28s cubic-bezier(0.4, 0, 0.2, 1), width 0.28s cubic-bezier(0.4, 0, 0.2, 1)';
        } else {
            indicator.style.transition = 'none';
        }
        indicator.style.transform = `translateX(${offset}px)`;
        indicator.style.width = `${rect.width}px`;
    }

    const activeBtn = document.querySelector('.floating-nav-btn.active');
    if (activeBtn) {
        updateIndicator(activeBtn, false);
    }

    navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            navBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            updateIndicator(btn, true);
        });
    });
}

// 清除所有本地缓存
function clearAllCache() {
    try {
        const keysToRemove = [];
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key && (key.startsWith('fofa_') || key.startsWith('xh_') || key.startsWith('vuln_') || key.startsWith('scan_'))) {
                keysToRemove.push(key);
            }
        }
        keysToRemove.forEach(key => localStorage.removeItem(key));
        
        showCacheToast('✅ 缓存已清除', 'success');
        
        setTimeout(() => {
            location.reload();
        }, 1000);
    } catch (e) {
        console.error('清除缓存失败:', e);
        showCacheToast('❌ 清除失败', 'error');
    }
}

// 缓存操作提示
function showCacheToast(msg, type = 'info') {
    const existing = document.querySelector('.cache-toast');
    if (existing) existing.remove();
    
    const toast = document.createElement('div');
    toast.className = 'cache-toast';
    toast.style.cssText = `
        position: fixed;
        top: 80px;
        left: 50%;
        transform: translateX(-50%);
        padding: 12px 24px;
        background: ${type === 'success' ? 'rgba(16, 185, 129, 0.95)' : type === 'error' ? 'rgba(239, 68, 68, 0.95)' : 'rgba(59, 130, 246, 0.95)'};
        color: #fff;
        border-radius: 999px;
        font-size: 14px;
        font-weight: 500;
        z-index: 10000;
        animation: cacheToastIn 0.3s ease;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    `;
    toast.textContent = msg;
    
    if (!document.getElementById('cacheToastStyle')) {
        const style = document.createElement('style');
        style.id = 'cacheToastStyle';
        style.textContent = `
            @keyframes cacheToastIn {
                from { opacity: 0; transform: translateX(-50%) translateY(-20px); }
                to { opacity: 1; transform: translateX(-50%) translateY(0); }
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.3s';
        setTimeout(() => toast.remove(), 300);
    }, 2500);
}

// 初始化布局
async function initLayout(config = {}) {
    await loadAllComponents(config);
    
    const aiInput = document.getElementById('aiInput');
    if (aiInput) {
        aiInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendAiMessage();
            }
        });
    }
}

// 导出到全局
window.XHLayout = {
    loadNavbar,
    loadFloatingNav,
    loadAiPanel,
    loadFooter,
    loadAllComponents,
    initLayout,
    copyCode,
    initFloatingNavIndicator,
    clearAllCache,
    showCacheToast,
    FLOATING_NAV_SEARCH_HTML,
    FOOTER_TEMPLATE
};

// 全局函数别名（兼容性）
window.loadNavbar = loadNavbar;
window.loadFloatingNav = loadFloatingNav;
window.loadFooter = loadFooter;
window.clearAllCache = clearAllCache;
