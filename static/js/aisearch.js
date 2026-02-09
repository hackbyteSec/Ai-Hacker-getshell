/**
 * 资产测绘页面脚本
 * aisearch/index.html 专用
 */

// ============ 页面初始化 ============
document.addEventListener('DOMContentLoaded', async function() {
    // 加载导航栏（子目录页面需要使用 basePath）
    await XHLayout.loadNavbar({ activeTab: 'aisearch', basePath: '../' });
    
    // 加载底部版权
    XHLayout.loadFooter();
    
    // 检查账户状态
    checkAccountStatus();
    
    // 绑定快捷标签点击事件
    document.querySelectorAll('.ai-shortcut').forEach(el => {
        el.addEventListener('click', function() {
            const query = this.getAttribute('data-query');
            if (query) setAiInput(query);
        });
    });
    
    // 绑定工具按钮点击事件
    document.querySelectorAll('.tool-btn').forEach(el => {
        el.addEventListener('click', function() {
            const query = this.getAttribute('data-query');
            if (query) setAiInput(query);
        });
    });
    
    // 绑定发送按钮
    document.querySelector('.ai-send').addEventListener('click', sendAiMessage);
    
    // AI输入框回车搜索 + 字数限制
    const aiInput = document.getElementById('aiInput');
    const MAX_CHARS = 200;
    
    aiInput.addEventListener('keypress', e => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendAiMessage();
        }
    });
    
    // 字数限制
    aiInput.addEventListener('input', function() {
        if (this.value.length > MAX_CHARS) {
            this.value = this.value.substring(0, MAX_CHARS);
        }
    });

    const exportBtn = document.getElementById('exportBtn');
    if (exportBtn) {
        exportBtn.addEventListener('click', exportResultsAsTxt);
    }
});

// ============ AI 助手相关函数 ============
function setAiInput(text) {
    document.getElementById('aiInput').value = text;
    document.getElementById('aiInput').focus();
}

let pendingKeyword = null;

// 检测是否是搜索语法
function isSearchQuery(text) {
    const searchPatterns = /^\s*(title|ip|domain|port|body|server|country|host|header|cert|protocol|os|app|fid|icp)\s*[=]/i;
    return searchPatterns.test(text);
}

function extractDomain(text) {
    const match = text.match(/([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/);
    return match ? match[1] : '';
}

function isAffirmative(text) {
    const t = text.trim().toLowerCase();
    return t === 'yes' || t === 'y' || t === '是' || t === '对' || t === '好的' || t === '好';
}

function isNegative(text) {
    const t = text.trim().toLowerCase();
    return t === 'no' || t === 'n' || t === '不是' || t === '不用' || t === '不用了' || t === '算了';
}

function sendAiMessage() {
    const input = document.getElementById('aiInput');
    const message = input.value.trim();
    if (!message) return;

    const aiBody = document.getElementById('aiBody');
    const domain = extractDomain(message);
    
    if (pendingKeyword) {
        aiBody.innerHTML += `<div class="ai-message user">${escapeHtml(message)}</div>`;
        input.value = '';
        if (isAffirmative(message)) {
            const query = `title="${pendingKeyword}"`;
            pendingKeyword = null;
            state.page = 1;
            performSearch(query);
            setAiInput(query);
            setTimeout(() => {
                aiBody.innerHTML += `<div class="ai-message assistant">已根据标题关键词为您搜索: <code style="background:#f1f5f9;padding:2px 6px;border-radius:4px;">${escapeHtml(query)}</code><br><br>搜索结果已在左侧列表中显示。</div>`;
                aiBody.scrollTop = aiBody.scrollHeight;
            }, 400);
            aiBody.scrollTop = aiBody.scrollHeight;
            return;
        }
        if (isNegative(message)) {
            pendingKeyword = null;
            setTimeout(() => {
                aiBody.innerHTML += `<div class="ai-message assistant">好的，如需根据关键词搜索，可以再次输入关键词或完整搜索语句。</div>`;
                aiBody.scrollTop = aiBody.scrollHeight;
            }, 300);
            return;
        }
        pendingKeyword = null;
    }

    // 检测是否是搜索语句
    if (isSearchQuery(message)) {
        aiBody.innerHTML += `<div class="ai-message user">搜索: ${escapeHtml(message)}</div>`;
        aiBody.scrollTop = aiBody.scrollHeight;
        input.value = '';
        
        const query = message;
        state.page = 1;
        performSearch(query);
        
        setTimeout(() => {
            aiBody.innerHTML += `<div class="ai-message assistant">已为您搜索: <code style="background:#f1f5f9;padding:2px 6px;border-radius:4px;">${escapeHtml(message)}</code><br><br>搜索结果已在左侧列表中显示。</div>`;
            aiBody.scrollTop = aiBody.scrollHeight;
        }, 500);
        return;
    }

    if (domain && !isSearchQuery(message)) {
        aiBody.innerHTML += `<div class="ai-message user">${escapeHtml(message)}</div>`;
        input.value = '';
        const query = `domain="${domain}"`;
        state.page = 1;
        performSearch(query);
        setAiInput(query);
        setTimeout(() => {
            aiBody.innerHTML += `<div class="ai-message assistant">已为您按域名转换并搜索: <code style="background:#f1f5f9;padding:2px 6px;border-radius:4px;">${escapeHtml(query)}</code><br><br>搜索结果已在左侧列表中显示。</div>`;
            aiBody.scrollTop = aiBody.scrollHeight;
        }, 400);
        return;
    }
    
    aiBody.innerHTML += `<div class="ai-message user">${escapeHtml(message)}</div>`;
    input.value = '';

    setTimeout(() => {
        pendingKeyword = message;
        const tip = `我可以帮你根据标题关键词进行搜索，是否使用以下语句进行检索？<br><br><code style="background:#f1f5f9;padding:2px 6px;border-radius:4px;">title="${escapeHtml(message)}"</code><br><br>如果需要，请回复 <strong>是</strong>、<strong>对</strong> 或 <strong>yes</strong> 进行确认。`;
        aiBody.innerHTML += `<div class="ai-message assistant">${tip}</div>`;
        aiBody.scrollTop = aiBody.scrollHeight;
    }, 500);

    aiBody.scrollTop = aiBody.scrollHeight;
}

// ============ 本地缓存管理 ============
const Cache = {
    keys: {
        LAST_QUERY: 'fofa_last_query',
        LAST_RESULTS: 'fofa_last_results',
        LAST_STATE: 'fofa_last_state',
        SEARCH_HISTORY: 'fofa_search_history'
    },
    set(key, data) {
        try { localStorage.setItem(key, JSON.stringify(data)); } 
        catch (e) { console.warn('缓存写入失败:', e); }
    },
    get(key) {
        try {
            const data = localStorage.getItem(key);
            return data ? JSON.parse(data) : null;
        } catch (e) { console.warn('缓存读取失败:', e); return null; }
    },
    saveSearch(query, results, state) {
        this.set(this.keys.LAST_QUERY, query);
        this.set(this.keys.LAST_RESULTS, results);
        this.set(this.keys.LAST_STATE, { page: state.page, size: state.size, total: state.total });
        this.addToHistory(query);
    },
    addToHistory(query) {
        let history = this.get(this.keys.SEARCH_HISTORY) || [];
        history = history.filter(h => h !== query);
        history.unshift(query);
        history = history.slice(0, 20);
        this.set(this.keys.SEARCH_HISTORY, history);
    },
    getHistory() { return this.get(this.keys.SEARCH_HISTORY) || []; },
    restore() {
        const query = this.get(this.keys.LAST_QUERY);
        const results = this.get(this.keys.LAST_RESULTS);
        const savedState = this.get(this.keys.LAST_STATE);
        if (query && results && savedState) { return { query, results, savedState }; }
        return null;
    },
    clear() { Object.values(this.keys).forEach(key => localStorage.removeItem(key)); }
};

// ============ 状态管理 ============
const state = { page: 1, size: 20, total: 0, query: '', loading: false, startTime: 0, results: [] };
const $ = id => document.getElementById(id);

function escapeHtml(str) {
    if (!str) return '';
    const d = document.createElement('div');
    d.textContent = str;
    return d.innerHTML;
}

// DOM 元素引用（延迟初始化）
let assetList, resultBar, pagination, loading;

function initDomRefs() {
    assetList = $('assetList');
    resultBar = $('resultBar');
    pagination = $('pagination');
    loading = $('loading');
}

// 确保 DOM 加载后初始化引用
document.addEventListener('DOMContentLoaded', initDomRefs);

function normalizeQuery(query) {
    return query.replace(/(\w+)=([^"\s&|()]+)/g, (match, key, value) => {
        if (/^\d+$/.test(value)) return match;
        return `${key}="${value}"`;
    });
}

// ============ 浏览器历史状态管理 ============
let isPopState = false;
window.addEventListener('popstate', function(e) {
    if (e.state && e.state.query !== undefined) {
        isPopState = true;
        if (e.state.query) {
            state.page = e.state.page || 1;
            performSearch(e.state.query);
        } else {
            state.query = '';
            state.results = [];
            state.total = 0;
            state.page = 1;
            if (assetList) {
                assetList.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-icon">🔍</div>
                        <div class="empty-text">请在右侧 AI 助手中输入搜索语句</div>
                    </div>`;
            }
            if (resultBar) resultBar.style.display = 'none';
            if (pagination) pagination.style.display = 'none';
        }
    }
});

if (!history.state) {
    history.replaceState({ query: '', page: 1 }, '', location.pathname + location.search);
}

// ============ 搜索功能 ============
async function performSearch(query) {
    if (state.loading) return;
    state.loading = true;
    state.query = query;
    state.startTime = Date.now();
    showLoading(true);

    try {
        const result = await FofaAPI.search(query, { page: state.page, size: state.size });
        const time = Date.now() - state.startTime;

        if (result.success) {
            state.total = result.raw.size || result.results.length;
            state.results = result.results;
            Cache.saveSearch(query, result.results, state);
            
            if (!isPopState) {
                history.pushState({ query, page: state.page }, '', `#${encodeURIComponent(query)}`);
            }
            isPopState = false;
            
            renderResults(result.results);
            updateResultBar(time);
            updatePagination();
            showToast(`找到 ${state.total} 条结果`, 'success');
        } else {
            showToast('搜索失败: ' + result.error, 'error');
            renderEmpty(result.error);
        }
    } catch (err) {
        showToast('请求错误', 'error');
        renderEmpty(err.message);
    } finally {
        state.loading = false;
        showLoading(false);
    }
}

// ============ 渲染结果 ============
function renderResults(results) {
    if (!results || !results.length) {
        renderEmpty('未找到匹配资产');
        return;
    }

    const seen = new Set();
    const uniqueResults = results.filter(item => {
        const key = `${item.ip || ''}:${item.port || ''}`;
        if (seen.has(key)) return false;
        seen.add(key);
        return true;
    });

    if (resultBar) resultBar.style.display = 'flex';
    if (assetList) assetList.innerHTML = uniqueResults.map(item => createCard(item)).join('');

    document.querySelectorAll('.detail-tab').forEach(tab => {
        tab.addEventListener('click', function() {
            const panel = this.closest('.detail-panel');
            panel.querySelectorAll('.detail-tab').forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            const type = this.dataset.type;
            const headerEl = panel.querySelector('.header-content');
            const productsEl = panel.querySelector('.products-content');
            headerEl.style.display = type === 'header' ? 'block' : 'none';
            productsEl.style.display = type === 'products' ? 'block' : 'none';
        });
    });
}

function buildExportLines() {
    const results = state.results || [];
    if (!results.length) return [];
    const seen = new Set();
    const lines = [];
    results.forEach(item => {
        const ip = item.ip || '';
        const rawPort = item.port;
        const port = rawPort === 80 || rawPort === '80' || rawPort === 443 || rawPort === '443' ? '' : (rawPort || '');
        const domain = item.domain || item.host || '';
        const key = `${domain || ip}:${port || ''}`;
        if (!ip && !domain) return;
        if (seen.has(key)) return;
        seen.add(key);
        let value = '';
        if (domain) {
            value = domain + (port ? `:${port}` : '');
        } else if (ip) {
            value = ip + (port ? `:${port}` : '');
        }
        if (value) {
            lines.push(value);
        }
    });
    return lines;
}

function exportResultsAsTxt() {
    const lines = buildExportLines();
    if (!lines.length) return;
    const content = lines.join('\n');
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    const ts = new Date().toISOString().replace(/[:.]/g, '-');
    a.href = url;
    a.download = `fofa-assets-${ts}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function detectCdnProvider(server, header, org) {
    const text = (server + ' ' + header + ' ' + org).toLowerCase();
    if (!text.trim()) return '';
    if (text.includes('cloudflare')) return 'Cloudflare';
    if (text.includes('cloudfront') || text.includes('aws') || text.includes('amazon')) return 'Amazon CloudFront';
    if (text.includes('akamai')) return 'Akamai';
    if (text.includes('fastly')) return 'Fastly';
    if (text.includes('alicdn') || text.includes('aliyun') || text.includes('alibaba')) return 'Alibaba Cloud CDN';
    if (text.includes('tencent') || text.includes('qcloud')) return 'Tencent Cloud CDN';
    if (text.includes('azure') || text.includes('microsoft')) return 'Azure CDN';
    if (text.includes('baiducdn') || text.includes('baidubce')) return 'Baidu Cloud CDN';
    return '';
}

function createCard(item) {
    const ip = item.ip || '';
    const port = item.port || '';
    const host = item.host || ip;
    const title = item.title || '无标题';
    const protocol = (item.protocol || 'http').toUpperCase();
    const country = item.country_name || item.country || '';
    const region = item.region || '';
    const city = item.city || '';
    const location = [country, region, city].filter(Boolean).join(' / ') || '未知';
    const asn = item.as_number || '';
    const org = item.as_organization || '';
    const server = item.server || '';
    const product = item.product || '';
    const os = item.os || '';
    const date = item.lastupdatetime || '--';
    const header = item.header || item.banner || '';
    const link = item.link || `${protocol.toLowerCase()}://${host}${port ? ':' + port : ''}`;
    const domain = item.domain || item.host || '';
    const weight = item.weight || {};
    const baiduPc = weight.baidu_pc || '--';
    const baiduWap = weight.baidu_wap || '--';
    const sogouPc = weight.sogou_pc || '--';
    const sogouWap = weight.sogou_wap || '--';
    const soPc = weight.so_pc || '--';
    const soWap = weight.so_wap || '--';
    const shenma = weight.shenma || '--';
    const toutiao = weight.toutiao || '--';
    const google = weight.google || '--';
    const cdnProvider = detectCdnProvider(server, header, org);
    const cdnBadge = cdnProvider ? `
        <span class="card-cdn-badge" title="识别到 CDN: ${cdnProvider}">
            <svg viewBox="0 0 24 24" fill="currentColor" width="12" height="12">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
            </svg>
            CDN
        </span>` : '';

    // 构建链接
    const domainLink = domain ? `https://${domain}` : '';
    const ipLink = `http://${ip}${port ? ':' + port : ''}`;
    
    return `
    <div class="asset-card">
        <div class="card-header">
            <div class="header-left">
                ${domain ? `<a href="${domainLink}" target="_blank" class="host-link domain-link" title="点击访问 ${domainLink}">${domain}</a>` : ''}
                <a href="${ipLink}" target="_blank" class="host-link ip-link" title="点击访问 ${ipLink}">${ip}${port ? ':' + port : ''}</a>
                ${cdnBadge}
            </div>
            <div class="header-right">
                <span class="port-badge">${port || protocol}</span>
            </div>
        </div>
        <div class="card-body">
            <div class="info-panel">
                <div class="info-title">${escapeHtml(title)}</div>
                ${domain ? `<div class="info-row" style="margin-bottom: 12px;"><span class="info-label">域名</span><span class="info-value"><a href="${domainLink}" target="_blank" class="host-link domain-link" style="font-size: 13px;">${domain}</a></span></div>` : ''}
                <div class="info-ip" onclick="searchByIp('${ip}')" style="cursor:pointer;" title="点击搜索该IP">${ip}</div>
                <div class="info-row"><span class="info-label">位置</span><span class="info-value">${location}</span></div>
                ${asn ? `<div class="info-row"><span class="info-label">ASN</span><span class="info-value">${asn}</span></div>` : ''}
                ${org ? `<div class="info-row"><span class="info-label">组织</span><span class="info-value">${org}</span></div>` : ''}
                <div class="info-date">${date}</div>
                <div class="server-tags">
                    ${server ? `<span class="server-tag"><span class="icon">S</span>${server}</span>` : ''}
                    ${product ? `<span class="server-tag">${product}</span>` : ''}
                    ${os ? `<span class="server-tag">${os}</span>` : ''}
                </div>
            </div>
            <div class="detail-panel">
                <div class="detail-tabs">
                    <span class="detail-tab active" data-type="header">Header</span>
                    <span class="detail-tab" data-type="products">Products</span>
                </div>
                <div class="detail-content">
                    <div class="header-content">${parseHeader(header)}</div>
                    <div class="products-content" style="display:none;">
                        <div class="products-grid">
                            ${server ? `<span class="product-tag">${server}</span>` : ''}
                            ${product ? `<span class="product-tag">${product}</span>` : ''}
                            ${os ? `<span class="product-tag">${os}</span>` : ''}
                            ${protocol ? `<span class="product-tag">${protocol}</span>` : ''}
                        </div>
                    </div>
                </div>
            </div>
            <div class="rank-panel">
                <div class="rank-title">站点权重<span class="rank-title-vip">VIP解锁</span></div>
                <div class="rank-grid">
                    <div class="rank-row">
                        <div class="rank-item">
                            <span class="rank-icon rank-icon-baidu">度</span>
                            <div class="rank-meta">
                                <span class="rank-label">百度PC</span>
                                <span class="rank-value">${baiduPc}</span>
                            </div>
                        </div>
                        <div class="rank-item">
                            <span class="rank-icon rank-icon-baidu">度</span>
                            <div class="rank-meta">
                                <span class="rank-label">百度移动端</span>
                                <span class="rank-value">${baiduWap}</span>
                            </div>
                        </div>
                    </div>
                    <div class="rank-row">
                        <div class="rank-item">
                            <span class="rank-icon rank-icon-sogou">搜</span>
                            <div class="rank-meta">
                                <span class="rank-label">搜狗PC</span>
                                <span class="rank-value">${sogouPc}</span>
                            </div>
                        </div>
                        <div class="rank-item">
                            <span class="rank-icon rank-icon-sogou">搜</span>
                            <div class="rank-meta">
                                <span class="rank-label">搜狗移动端</span>
                                <span class="rank-value">${sogouWap}</span>
                            </div>
                        </div>
                    </div>
                    <div class="rank-row">
                        <div class="rank-item">
                            <span class="rank-icon rank-icon-360">360</span>
                            <div class="rank-meta">
                                <span class="rank-label">360PC</span>
                                <span class="rank-value">${soPc}</span>
                            </div>
                        </div>
                        <div class="rank-item">
                            <span class="rank-icon rank-icon-360">360</span>
                            <div class="rank-meta">
                                <span class="rank-label">360移动端</span>
                                <span class="rank-value">${soWap}</span>
                            </div>
                        </div>
                    </div>
                    <div class="rank-row">
                        <div class="rank-item">
                            <span class="rank-icon rank-icon-shenma">马</span>
                            <div class="rank-meta">
                                <span class="rank-label">神马</span>
                                <span class="rank-value">${shenma}</span>
                            </div>
                        </div>
                        <div class="rank-item">
                            <span class="rank-icon rank-icon-toutiao">头</span>
                            <div class="rank-meta">
                                <span class="rank-label">头条搜索</span>
                                <span class="rank-value">${toutiao}</span>
                            </div>
                        </div>
                    </div>
                    <div class="rank-row">
                        <div class="rank-item">
                            <span class="rank-icon rank-icon-google">G</span>
                            <div class="rank-meta">
                                <span class="rank-label">Google</span>
                                <span class="rank-value">${google}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>`;
}

function parseHeader(header) {
    if (!header) return '<span style="color:var(--text-tertiary)">无 Header 信息</span>';
    return header.split('\n').map(line => {
        const t = line.trim();
        if (!t) return '';
        if (t.startsWith('HTTP/')) {
            return `<div class="header-line"><span class="header-status">${escapeHtml(t)}</span></div>`;
        }
        const i = t.indexOf(':');
        if (i > 0) {
            return `<div class="header-line"><span class="header-key">${escapeHtml(t.substring(0, i))}:</span> ${escapeHtml(t.substring(i + 1))}</div>`;
        }
        return `<div class="header-line">${escapeHtml(t)}</div>`;
    }).join('');
}

function searchByIp(ip) {
    if (ip) {
        const query = `ip="${ip}"`;
        setAiInput(query);
        state.page = 1;
        performSearch(normalizeQuery(query));
        const aiBody = document.getElementById('aiBody');
        aiBody.innerHTML += `<div class="ai-message user">搜索: ${escapeHtml(query)}</div>`;
        setTimeout(() => {
            aiBody.innerHTML += `<div class="ai-message assistant">已为您搜索IP: <code style="background:#f1f5f9;padding:2px 6px;border-radius:4px;">${ip}</code></div>`;
            aiBody.scrollTop = aiBody.scrollHeight;
        }, 500);
    }
}

function updateResultBar(time) {
    $('totalCount').textContent = state.total;
    $('queryTime').textContent = time + ' ms';
}

function renderEmpty(msg) {
    if (resultBar) resultBar.style.display = 'none';
    if (pagination) pagination.style.display = 'none';
    if (assetList) {
        assetList.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">🔍</div>
                <div class="empty-text">${msg}</div>
            </div>`;
    }
}

// ============ 分页 ============
function updatePagination() {
    const total = Math.ceil(state.total / state.size);
    if (total <= 1) { 
        if (pagination) pagination.style.display = 'none'; 
        return; 
    }

    if (pagination) {
        pagination.style.display = 'flex';
        pagination.innerHTML = '';

        const prev = document.createElement('button');
        prev.className = 'page-btn';
        prev.textContent = '上一页';
        prev.disabled = state.page <= 1;
        prev.onclick = () => { state.page--; performSearch(state.query); };
        pagination.appendChild(prev);

        const start = Math.max(1, state.page - 2);
        const end = Math.min(total, start + 4);
        for (let i = start; i <= end; i++) {
            const btn = document.createElement('button');
            btn.className = 'page-btn' + (i === state.page ? ' active' : '');
            btn.textContent = i;
            btn.onclick = () => { state.page = i; performSearch(state.query); };
            pagination.appendChild(btn);
        }

        const next = document.createElement('button');
        next.className = 'page-btn';
        next.textContent = '下一页';
        next.disabled = state.page >= total;
        next.onclick = () => { state.page++; performSearch(state.query); };
        pagination.appendChild(next);
    }
}

// ============ 辅助函数 ============
function showLoading(show) {
    if (loading) loading.classList.toggle('show', show);
}

function showToast(msg, type = 'info') {
    // 已禁用弹窗提示
}

function initFromCache() {
    const cached = Cache.restore();
    if (cached) {
        const { query, results, savedState } = cached;
        state.query = query;
        state.page = savedState.page;
        state.total = savedState.total;
        state.results = results;
        renderResults(results);
        updateResultBar(0);
        updatePagination();
    }
}

async function checkAccountStatus() {
    try {
        const info = await FofaAPI.getAccountInfo();
        console.log('[FOFA] 账户信息:', info);
    } catch (e) {
        console.error('[FOFA] 账户检查异常:', e);
    }
}
