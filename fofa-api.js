/**
 * FOFA API 调用模块
 * API文档: https://fofa.info/api
 */

// 配置解码器
const _d = (s) => atob(s.split('').reverse().join(''));
const _c = {
    a: '',  // FOFA Email - 请在此处填入你的 FOFA 邮箱（Base64 反转编码）
    b: '',  // FOFA Key - 请在此处填入你的 FOFA API Key（Base64 反转编码）
    c: 'xY3LpBXYv8mZulmLhZ2bm9yL6MHc0RHa'  // FOFA Base URL
};

const FofaAPI = {
    // 配置
    config: {
        get email() { return _d(_c.a); },
        get key() { return _d(_c.b); },
        get baseUrl() { return _d(_c.c); }
    },

    /**
     * Base64 编码（支持中文）
     * @param {string} str - 要编码的字符串
     * @returns {string} - Base64 编码后的字符串
     */
    base64Encode(str) {
        return btoa(unescape(encodeURIComponent(str)));
    },

    /**
     * 构建 API URL
     * @param {string} endpoint - API 端点
     * @param {object} params - 查询参数
     * @returns {string} - 完整的 API URL
     */
    buildUrl(endpoint, params = {}) {
        const url = new URL(`${this.config.baseUrl}${endpoint}`);
        
        // 添加认证参数
        url.searchParams.append('email', this.config.email);
        url.searchParams.append('key', this.config.key);
        
        // 添加其他参数
        Object.keys(params).forEach(key => {
            if (params[key] !== undefined && params[key] !== null) {
                url.searchParams.append(key, params[key]);
            }
        });
        
        return url.toString();
    },

    /**
     * 查询接口 - 搜索资产
     * @param {string} query - 查询语句，如 "port=443 && country=CN"
     * @param {object} options - 可选参数
     * @param {number} options.page - 页码，默认 1
     * @param {number} options.size - 每页数量，默认 100，最大 10000
     * @param {string} options.fields - 返回字段
     * @param {boolean} options.full - 是否获取全部数据（需要会员）
     * @returns {Promise<object>} - 查询结果
     */
    async search(query, options = {}) {
        // 默认获取常用字段（排除需要VIP权限的字段）
        const defaultFields = [
            'host', 'ip', 'port', 'protocol', 'country', 'country_name',
            'region', 'city', 'title', 'server', 'banner', 'header',
            'icp', 'as_number', 'as_organization',
            'lastupdatetime', 'domain', 'os', 'link',
            'product'
        ].join(',');

        const {
            page = 1,
            size = 20,
            fields = defaultFields,
            full = false
        } = options;

        const params = {
            qbase64: this.base64Encode(query),
            page,
            size,
            fields,
            full: full ? 'true' : 'false'
        };

        const url = this.buildUrl('/search/all', params);
        
        try {
            const response = await fetch(url);
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.errmsg || '查询失败');
            }
            
            return {
                success: true,
                query: query,
                mode: data.mode,
                page: data.page,
                size: data.size,
                total: data.size,
                results: this.parseResults(data.results, fields),
                raw: data
            };
        } catch (error) {
            console.error('FOFA API 查询错误:', error);
            return {
                success: false,
                error: error.message,
                query: query
            };
        }
    },

    /**
     * 解析查询结果
     * @param {array} results - 原始结果数组
     * @param {string} fields - 字段列表
     * @returns {array} - 解析后的对象数组
     */
    parseResults(results, fields) {
        if (!results || !Array.isArray(results)) {
            return [];
        }

        const fieldList = fields.split(',');
        
        return results.map(item => {
            const obj = {};
            fieldList.forEach((field, index) => {
                obj[field.trim()] = item[index] || '';
            });
            return obj;
        });
    },

    /**
     * 统计聚合接口
     * @param {string} query - 查询语句
     * @param {string} fields - 聚合字段，如 "port,server,country,product"
     * @returns {Promise<object>} - 聚合结果
     */
    async stats(query, fields = 'protocol,country,city') {
        const params = {
            qbase64: this.base64Encode(query),
            fields
        };
        
        const url = this.buildUrl('/search/stats', params);
        console.log('[FOFA API] Stats URL:', url);
        
        try {
            console.log('[FOFA API] 正在调用 stats 接口...');
            const response = await fetch(url);
            const data = await response.json();
            
            console.log('[FOFA API] Stats 返回:', data.error ? data.errmsg : 'success');
            
            if (data.error) {
                console.warn('[FOFA API] Stats 错误:', data.errmsg);
                return {
                    success: false,
                    error: data.errmsg || '统计失败'
                };
            }
            
            if (data.aggs) {
                Object.keys(data.aggs).forEach(key => {
                    console.log(`[FOFA API] aggs.${key}: ${data.aggs[key] ? data.aggs[key].length : 0}条`);
                });
            }
            
            return {
                success: true,
                query: query,
                distinct: data.distinct,
                aggs: data.aggs,
                raw: data
            };
        } catch (error) {
            console.error('[FOFA API] Stats 异常:', error.message);
            return {
                success: false,
                error: error.message
            };
        }
    },

    /**
     * Host 聚合接口 - 获取主机详细信息
     * @param {string} host - 主机地址，如 "example.com" 或 IP
     * @param {boolean} detail - 是否获取详细信息
     * @returns {Promise<object>} - 主机信息
     */
    async hostInfo(host, detail = false) {
        const params = {
            host,
            detail: detail ? 'true' : 'false'
        };

        const url = this.buildUrl('/host', params);
        
        try {
            const response = await fetch(url);
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.errmsg || '查询失败');
            }
            
            return {
                success: true,
                host: data.host,
                ip: data.ip,
                asn: data.asn,
                org: data.org,
                country: data.country_name,
                countryCode: data.country_code,
                ports: data.ports || [],
                protocols: data.protocols || [],
                categories: data.categories || [],
                products: data.products || [],
                updateTime: data.update_time,
                raw: data
            };
        } catch (error) {
            console.error('FOFA Host 查询错误:', error);
            return {
                success: false,
                error: error.message
            };
        }
    },
    /**
     * 获取账户信息
     * @returns {Promise<object>} - 账户信息
     */
    async getAccountInfo() {
        const url = this.buildUrl('/info/my');
        
        try {
            const response = await fetch(url);
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.errmsg || '获取账户信息失败');
            }
            
            return {
                success: true,
                email: data.email,
                username: data.username,
                fcoin: data.fcoin,           // F币余额
                fofa_point: data.fofa_point, // FOFA积分
                isVip: data.isvip,           // 是否VIP
                vipLevel: data.vip_level,    // VIP等级
                avatar: data.avatar,
                raw: data
            };
        } catch (error) {
            console.error('获取账户信息错误:', error);
            return {
                success: false,
                error: error.message
            };
        }
    },

    /**
     * 图标搜索 - 通过 favicon hash 搜索
     * @param {string} iconHash - 图标 hash 值
     * @param {object} options - 查询选项
     * @returns {Promise<object>} - 查询结果
     */
    async searchByIcon(iconHash, options = {}) {
        const query = `icon_hash="${iconHash}"`;
        return await this.search(query, options);
    },

    /**
     * 证书搜索
     * @param {string} certKeyword - 证书关键词
     * @param {object} options - 查询选项
     * @returns {Promise<object>} - 查询结果
     */
    async searchByCert(certKeyword, options = {}) {
        const query = `cert="${certKeyword}"`;
        return await this.search(query, options);
    },

    /**
     * 批量查询 IP
     * @param {array} ipList - IP 列表
     * @param {object} options - 查询选项
     * @returns {Promise<object>} - 查询结果
     */
    async batchSearchIP(ipList, options = {}) {
        if (!Array.isArray(ipList) || ipList.length === 0) {
            return { success: false, error: 'IP 列表不能为空' };
        }
        
        const query = ipList.map(ip => `ip="${ip}"`).join(' || ');
        return await this.search(query, options);
    },

    /**
     * 子域名查询
     * @param {string} domain - 主域名
     * @param {object} options - 查询选项
     * @returns {Promise<object>} - 查询结果
     */
    async searchSubdomain(domain, options = {}) {
        const query = `domain="${domain}"`;
        const defaultFields = 'host,ip,port,title,protocol';
        return await this.search(query, {
            ...options,
            fields: options.fields || defaultFields
        });
    },

    /**
     * 常用查询语法示例
     */
    querySyntax: {
        // 基础查询
        byIP: (ip) => `ip="${ip}"`,
        byPort: (port) => `port="${port}"`,
        byProtocol: (protocol) => `protocol="${protocol}"`,
        byDomain: (domain) => `domain="${domain}"`,
        byHost: (host) => `host="${host}"`,
        byTitle: (title) => `title="${title}"`,
        byBody: (keyword) => `body="${keyword}"`,
        byHeader: (keyword) => `header="${keyword}"`,
        byServer: (server) => `server="${server}"`,
        
        // 地理位置
        byCountry: (country) => `country="${country}"`,
        byCity: (city) => `city="${city}"`,
        byRegion: (region) => `region="${region}"`,
        
        // 组织信息
        byOrg: (org) => `org="${org}"`,
        byASN: (asn) => `asn="${asn}"`,
        
        // 证书相关
        byCert: (cert) => `cert="${cert}"`,
        byCertSubject: (subject) => `cert.subject="${subject}"`,
        byCertIssuer: (issuer) => `cert.issuer="${issuer}"`,
        
        // 其他
        byIconHash: (hash) => `icon_hash="${hash}"`,
        byJarm: (jarm) => `jarm="${jarm}"`,
        
        // 组合查询
        combine: (...queries) => queries.join(' && '),
        combineOr: (...queries) => queries.join(' || ')
    }
};

// ==================== 使用示例 ====================

/**
 * 示例：基础搜索
 */
async function exampleSearch() {
    // 搜索中国的 443 端口
    const result = await FofaAPI.search('port="443" && country="CN"', {
        page: 1,
        size: 10,
        fields: 'host,ip,port,title,country,city'
    });
    
    if (result.success) {
        console.log('查询成功，共找到', result.total, '条结果');
        console.log('结果:', result.results);
    } else {
        console.error('查询失败:', result.error);
    }
    
    return result;
}

/**
 * 示例：获取账户信息
 */
async function exampleAccountInfo() {
    const info = await FofaAPI.getAccountInfo();
    
    if (info.success) {
        console.log('账户:', info.email);
        console.log('F币余额:', info.fcoin);
        console.log('VIP等级:', info.vipLevel);
    }
    
    return info;
}

/**
 * 示例：统计聚合
 */
async function exampleStats() {
    const stats = await FofaAPI.stats('port="80"', 'country,protocol');
    
    if (stats.success) {
        console.log('统计结果:', stats.aggs);
    }
    
    return stats;
}

/**
 * 示例：使用查询语法助手
 */
function exampleQueryBuilder() {
    const syntax = FofaAPI.querySyntax;
    
    // 构建复杂查询
    const query = syntax.combine(
        syntax.byPort('443'),
        syntax.byCountry('CN'),
        syntax.byTitle('后台')
    );
    
    console.log('生成的查询语句:', query);
    // 输出: port="443" && country="CN" && title="后台"
    
    return query;
}

// 导出模块（如果在 Node.js 环境）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FofaAPI;
}
