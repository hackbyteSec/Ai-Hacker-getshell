"""
苹果CMS扫描后端服务
功能：FOFA搜索、指纹识别爬取验证
"""

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
import base64
import urllib3
import re
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time
import sys

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
# CORS配置，添加预检缓存时间（减少OPTIONS请求）
CORS(app, max_age=3600, supports_credentials=True)

# FOFA API 配置 (已混淆)
def _decode(s):
    return base64.b64decode(s[::-1]).decode()

_c = {
    'a': '==QbvNmLslWYt52b09mcwBkeyVmdlx2Y',
    'b': '=cTM1UTN2YjNiFjZmRTOmNGN1YjZmJzYzIjMhFjY1UjN',
    'c': 'xY3LpBXYv8mZulmLhZ2bm9yL6MHc0RHa'
}

FOFA_EMAIL = _decode(_c['a'])
FOFA_KEY = _decode(_c['b'])
FOFA_BASE_URL = _decode(_c['c'])

# 苹果CMS指纹特征配置
# 格式: { 路径: { 'keywords': [关键词列表], 'case_sensitive': 是否区分大小写 } }
MACCMS_FINGERPRINTS = {
    '/static/js/player.js': {
        'keywords': ['MacPlayer'],
        'case_sensitive': True  # 区分大小写，精确匹配
    },
    '/static/js/home.js': {
        'keywords': ['maccms', 'MacCMS', 'mac_url', 'vodlist'],
        'case_sensitive': False
    },
    '/application/common.php': {
        'keywords': ['ThinkPHP', 'think\\', 'namespace app'],
        'case_sensitive': False
    },
    '/template/default/html': {
        'keywords': ['maccms', 'MacCMS', 'vod-list'],
        'case_sensitive': False
    },
    '/static/css/style.css': {
        'keywords': ['maccms', 'vod-', 'type-'],
        'case_sensitive': False
    },
    '/application/config.php': {
        'keywords': ['database', 'hostname'],
        'case_sensitive': False
    }
}

def fofa_search(query, page=1, size=10000, max_retries=3):
    """FOFA搜索 - 单页（带重试机制）"""
    for retry in range(max_retries):
        try:
            qbase64 = base64.b64encode(query.encode()).decode()
            fields = 'host,ip,port,protocol,domain,title,server,country_name'
            
            url = f"{FOFA_BASE_URL}/search/all"
            params = {
                'email': FOFA_EMAIL,
                'key': FOFA_KEY,
                'qbase64': qbase64,
                'page': page,
                'size': size,
                'fields': fields
            }
            
            print(f"\n" + "#"*60, flush=True)
            print(f"# [FOFA API] 请求第 {page} 页, size={size}", flush=True)
            print(f"#"*60, flush=True)
            
            response = requests.get(url, params=params, timeout=60)
            data = response.json()
            
            # 检查错误
            if data.get('error'):
                error_msg = data.get('errmsg', '查询失败')
                print(f"# [FOFA API] !!! 错误: {error_msg}", flush=True)
                return {'success': False, 'error': error_msg}
            
            # 解析结果
            results = []
            field_list = fields.split(',')
            raw_results = data.get('results', [])
            total_size = data.get('size', 0)
            result_count = len(raw_results)
            
            print(f"# [FOFA API] 第 {page} 页返回: {result_count} 条", flush=True)
            print(f"# [FOFA API] FOFA报告总数: {total_size}", flush=True)
            
            # 第2页及之后返回空数据的警告
            if page > 1 and result_count == 0:
                print(f"# [FOFA API] !!! 警告: 第{page}页返回0条 - FOFA会员等级限制!", flush=True)
            elif page > 1 and result_count > 0:
                print(f"# [FOFA API] ✓ 第{page}页成功获取 {result_count} 条!", flush=True)
            
            print(f"#"*60 + "\n", flush=True)
            
            for item in raw_results:
                obj = {}
                for i, field in enumerate(field_list):
                    obj[field] = item[i] if i < len(item) else ''
                results.append(obj)
            
            return {
                'success': True,
                'total': total_size,
                'page_total': len(results),
                'results': results
            }
        except requests.exceptions.Timeout:
            print(f"[FOFA API] 超时 (重试 {retry+1}/{max_retries})")
            if retry < max_retries - 1:
                time.sleep(2)  # 等待2秒后重试
                continue
            return {'success': False, 'error': '连接FOFA超时，请检查网络连接'}
        except requests.exceptions.ConnectionError:
            print(f"[FOFA API] 连接错误 (重试 {retry+1}/{max_retries})")
            if retry < max_retries - 1:
                time.sleep(2)
                continue
            return {'success': False, 'error': '无法连接FOFA服务器'}
        except Exception as e:
            print(f"[FOFA API] 异常: {str(e)}")
            if retry < max_retries - 1:
                time.sleep(1)
                continue
            return {'success': False, 'error': str(e)}
    
    return {'success': False, 'error': '请求失败'}


def fofa_search_multi_page(query, max_results=None):
    """FOFA搜索 - 多页获取，获取全部数据"""
    all_results = []
    page = 1
    per_page = 10000  # FOFA高级会员单页最多10000条
    total_count = 0
    
    print(f"\n[FOFA] 开始搜索: {query}")
    
    while True:
        print(f"[FOFA] 正在获取第 {page} 页...")
        result = fofa_search(query, page=page, size=per_page)
        
        if not result['success']:
            print(f"[FOFA] 第 {page} 页获取失败: {result.get('error', '未知错误')}")
            if page == 1:
                return result  # 第一页就失败，返回错误
            break  # 后续页失败，返回已获取的数据
        
        page_results = result.get('results', [])
        if not page_results:
            print(f"[FOFA] 第 {page} 页无数据，停止获取")
            break  # 没有更多数据
        
        all_results.extend(page_results)
        
        # 获取总数（只在第一页时设置）
        if page == 1:
            total_count = result.get('total', 0)
            print(f"[FOFA] 总共 {total_count} 条结果")
        
        print(f"[FOFA] 第 {page} 页获取 {len(page_results)} 条，累计 {len(all_results)}/{total_count}")
        
        # 检查是否还有更多
        if len(all_results) >= total_count:
            print(f"[FOFA] 已获取全部数据")
            break
        
        # 如果设置了最大限制，检查是否达到
        if max_results and len(all_results) >= max_results:
            print(f"[FOFA] 达到最大限制 {max_results}")
            break
        
        # 检查是否还有下一页（如果返回的数据少于per_page，说明是最后一页）
        if len(page_results) < per_page:
            print(f"[FOFA] 本页数据不足 {per_page}，应该是最后一页")
            break
        
        page += 1
        time.sleep(0.5)  # 避免请求过快，FOFA有请求频率限制
    
    print(f"[FOFA] 搜索完成，共获取 {len(all_results)} 条\n")
    
    return {
        'success': True,
        'total': total_count,
        'fetched': len(all_results),
        'results': all_results
    }


def fofa_search_stream_generator(query, max_results=None, max_pages=100):
    """
    FOFA搜索 - 流式生成器
    支持自动分割查询突破单次查询10000条限制
    不去重，返回所有数据
    """
    page = 1
    per_page = 10000
    total_count = 0
    fetched_count = 0
    split_mode_triggered = False
    
    print(f"\n{'='*60}", flush=True)
    print(f"[FOFA Stream] 开始流式搜索: {query}", flush=True)
    print(f"{'='*60}", flush=True)
    
    # 第一阶段：尝试直接分页获取
    while page <= max_pages:
        print(f"\n[FOFA Stream] >>> 正在获取第 {page} 页...", flush=True)
        result = fofa_search(query, page=page, size=per_page)
        
        if not result['success']:
            if page == 1:
                yield {'type': 'error', 'error': result.get('error', '查询失败')}
                return
            break
        
        page_results = result.get('results', [])
        page_count = len(page_results)
        
        if page == 1:
            total_count = result.get('total', 0)
            print(f"[FOFA Stream] FOFA 报告总数: {total_count} 条", flush=True)
            yield {'type': 'total', 'total': total_count}
        
        # 检查是否需要触发分割查询
        if page == 2 and (not page_results or page_count == 0):
            if total_count > 10000:
                print(f"\n" + "!"*60, flush=True)
                print(f"!!! 第2页返回空, 检测到会员限制 !!!", flush=True)
                print(f"!!! 启用分割查询模式 !!!", flush=True)
                print(f"!"*60 + "\n", flush=True)
                
                split_mode_triggered = True
                yield {'type': 'split_start', 'message': '检测到会员限制，启用分割查询模式'}
                
                # 使用分割查询获取更多数据
                for item_data in split_query_generator(query, fetched_count, total_count):
                    if item_data['type'] == 'item':
                        fetched_count += 1
                        item_data['fetched_count'] = fetched_count
                    yield item_data
                break
            else:
                print(f"[FOFA Stream] 第 2 页无数据，停止", flush=True)
                break
        
        if not page_results or page_count == 0:
            print(f"[FOFA Stream] 第 {page} 页无数据，停止", flush=True)
            break
        
        # 处理本页数据 - 不去重
        for item in page_results:
            item_data = process_fofa_item_simple(item)
            if item_data:
                fetched_count += 1
                yield {
                    'type': 'item',
                    'item': item_data,
                    'fetched_count': fetched_count,
                    'total': total_count,
                    'current_page': page
                }
        
        print(f"[FOFA Stream] 第 {page} 页完成: {fetched_count} 条", flush=True)
        
        if max_results and fetched_count >= max_results:
            break
        
        if page_count < per_page:
            print(f"[FOFA Stream] 本页不足{per_page}条，停止分页", flush=True)
            break
        
        page += 1
    
    print(f"\n{'='*60}", flush=True)
    print(f"[FOFA Stream] 完成! 总计获取: {fetched_count} 条", flush=True)
    print(f"{'='*60}\n", flush=True)
    
    yield {
        'type': 'done',
        'total': total_count,
        'fetched': fetched_count,
        'unique_count': fetched_count,
        'pages': page,
        'split_mode': split_mode_triggered
    }


def process_fofa_item_simple(item):
    """处理单个FOFA结果项 - 不去重"""
    host = item.get('host', '')
    domain = item.get('domain', '')
    ip = item.get('ip', '')
    port = str(item.get('port', '80'))
    protocol = item.get('protocol', 'http')
    
    # 过滤无效数据
    if ip == '0.0.0.0' or port == '0':
        return None
    
    # 确定显示名称
    if domain and domain.strip():
        display = f"{domain}:{port}" if port not in ['80', '443'] else domain
    elif ip:
        display = f"{ip}:{port}" if port not in ['80', '443'] else ip
    else:
        display = host
    
    # 构建URL
    if '://' in host:
        full_url = host
    else:
        proto = 'https' if protocol == 'https' or port == '443' else 'http'
        base = domain if domain else ip
        full_url = f"{proto}://{base}"
        if port not in ['80', '443']:
            full_url += f":{port}"
    
    return {
        'display': display,
        'url': full_url,
        'ip': ip,
        'port': port,
        'domain': domain,
        'title': item.get('title', ''),
        'server': item.get('server', ''),
        'country': item.get('country_name', ''),
        'protocol': protocol
    }


def split_query_generator(base_query, current_count, total_count):
    """
    分割查询生成器 - 按国家分割查询来突破限制
    每个子查询可以获取最多10000条
    """
    # 按国家分割 - 覆盖更广的数据
    countries = [
        'CN', 'US', 'HK', 'TW', 'JP', 'KR', 'SG', 'DE', 'FR', 'GB',
        'NL', 'RU', 'CA', 'AU', 'IN', 'BR', 'ID', 'TH', 'VN', 'MY',
        'PH', 'IT', 'ES', 'PL', 'UA', 'TR', 'MX', 'AR', 'CL', 'CO'
    ]
    
    fetched_in_split = 0
    
    for country in countries:
        # 构建带国家过滤的查询
        split_query = f'({base_query}) && country="{country}"'
        
        print(f"\n[Split] 查询国家 {country}: {split_query}", flush=True)
        
        result = fofa_search(split_query, page=1, size=10000)
        
        if not result['success']:
            print(f"[Split] 国家 {country} 查询失败", flush=True)
            continue
        
        page_results = result.get('results', [])
        sub_total = result.get('total', 0)
        
        if not page_results:
            print(f"[Split] 国家 {country}: 0 条", flush=True)
            continue
        
        print(f"[Split] 国家 {country}: 匹配 {sub_total} 条, 获取 {len(page_results)} 条", flush=True)
        
        for item in page_results:
            item_data = process_fofa_item_simple(item)
            if item_data:
                fetched_in_split += 1
                yield {
                    'type': 'item',
                    'item': item_data,
                    'total': total_count,
                    'current_page': f'split-{country}'
                }
        
        print(f"[Split] 国家 {country} 完成, 累计新增 {fetched_in_split} 条", flush=True)
        
        # 短暂延迟避免请求过快
        time.sleep(0.3)
    
    print(f"\n[Split] 分割查询完成, 共新增 {fetched_in_split} 条", flush=True)


def check_fingerprint(url, finger_path, custom_keyword=None):
    """
    检测指纹 - 严谨的指纹识别逻辑
    
    Args:
        url: 目标URL
        finger_path: 指纹路径
        custom_keyword: 自定义关键词（可选，如果提供则只匹配这个关键词）
    
    Returns:
        dict: 包含检测结果的字典
    """
    result_base = {
        'success': False,
        'status': 'no_match',
        'error': None,
        'status_code': None,
        'matched_keyword': None
    }
    
    try:
        # 清理URL末尾的斜杠
        url = url.rstrip('/')
        # 确保path以/开头
        if not finger_path.startswith('/'):
            finger_path = '/' + finger_path
        
        target_url = url + finger_path
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'close',
            'Cache-Control': 'no-cache'
        }
        
        # 创建session以更好地处理SSL
        session = requests.Session()
        session.verify = False  # 忽略SSL证书验证（处理过期证书）
        
        # 禁用SSL警告已在文件顶部处理
        
        # 尝试请求，设置合理的超时（5秒内完成）
        try:
            response = session.get(
                target_url, 
                headers=headers, 
                timeout=(3, 4),  # (连接超时, 读取超时) 总共约7秒
                allow_redirects=True,
                stream=False
            )
        except requests.exceptions.SSLError as ssl_err:
            # SSL错误时，尝试降级到HTTP
            if target_url.startswith('https://'):
                http_url = target_url.replace('https://', 'http://', 1)
                try:
                    response = session.get(
                        http_url,
                        headers=headers,
                        timeout=(3, 4),
                        allow_redirects=True,
                        stream=False
                    )
                except Exception:
                    # HTTP也失败，返回原始SSL错误
                    return {
                        **result_base,
                        'status': 'no_match',
                        'error': f'SSL错误: {str(ssl_err)[:50]}'
                    }
            else:
                return {
                    **result_base,
                    'status': 'no_match',
                    'error': f'SSL错误: {str(ssl_err)[:50]}'
                }
        
        status_code = response.status_code
        result_base['status_code'] = status_code
        
        # 404、403、500等都视为未找到指纹
        if status_code != 200:
            return {
                **result_base,
                'status': 'no_match',
                'error': f'HTTP {status_code}'
            }
        
        # 获取响应内容
        try:
            # 尝试多种编码
            content = response.text
            if not content:
                content = response.content.decode('utf-8', errors='ignore')
        except Exception:
            content = response.content.decode('utf-8', errors='ignore')
        
        # 如果内容为空
        if not content or len(content.strip()) == 0:
            return {
                **result_base,
                'status': 'no_match',
                'error': '响应内容为空'
            }
        
        # 确定要匹配的关键词和匹配模式
        if custom_keyword:
            # 使用自定义关键词，区分大小写精确匹配
            keywords = [custom_keyword]
            case_sensitive = True
        else:
            # 使用预定义的指纹配置
            finger_config = MACCMS_FINGERPRINTS.get(finger_path, {'keywords': ['maccms'], 'case_sensitive': False})
            keywords = finger_config.get('keywords', ['maccms'])
            case_sensitive = finger_config.get('case_sensitive', False)
        
        # 检测关键词
        matched_keyword = None
        for keyword in keywords:
            if case_sensitive:
                # 区分大小写匹配
                if keyword in content:
                    matched_keyword = keyword
                    break
            else:
                # 不区分大小写匹配
                if keyword.lower() in content.lower():
                    matched_keyword = keyword
                    break
        
        if matched_keyword:
            # 找到匹配的关键词
            version = detect_version(content)
            return {
                'success': True,
                'status': 'found',
                'version': version,
                'matched_keyword': matched_keyword,
                'status_code': status_code,
                'error': None
            }
        else:
            # 未找到匹配的关键词
            return {
                **result_base,
                'success': True,
                'status': 'no_match',
                'status_code': status_code
            }
            
    except requests.exceptions.Timeout:
        return {**result_base, 'status': 'no_match', 'error': '连接超时'}
    except requests.exceptions.ConnectionError as ce:
        error_msg = str(ce)[:50] if str(ce) else '连接失败'
        return {**result_base, 'status': 'no_match', 'error': error_msg}
    except requests.exceptions.TooManyRedirects:
        return {**result_base, 'status': 'no_match', 'error': '重定向过多'}
    except Exception as e:
        error_msg = str(e)[:50] if str(e) else '未知错误'
        return {**result_base, 'status': 'no_match', 'error': error_msg}


def detect_version(content):
    """检测苹果CMS版本"""
    content_lower = content.lower()
    
    # ThinkPHP版本检测
    if 'thinkphp5' in content_lower or 'thinkphp 5' in content_lower:
        if 'v10' in content_lower or 'maccms10' in content_lower:
            return 'MacCMS V10 (ThinkPHP5)'
        return 'MacCMS V10+ (ThinkPHP5)'
    
    if 'thinkphp' in content_lower:
        return 'MacCMS V10 (ThinkPHP)'
    
    # 版本号检测
    version_patterns = [
        (r'maccms\s*v?(\d+)', 'MacCMS V'),
        (r'苹果cms\s*v?(\d+)', '苹果CMS V'),
        (r'version["\s:]+["\']?(\d+\.\d+)', 'MacCMS V')
    ]
    
    for pattern, prefix in version_patterns:
        match = re.search(pattern, content_lower)
        if match:
            return f"{prefix}{match.group(1)}"
    
    # 通用检测
    if 'maccms' in content_lower:
        return 'MacCMS (版本未知)'
    
    return 'MacCMS'


@app.route('/')
def index():
    return jsonify({
        'status': 'running',
        'service': 'MacCMS Scanner API',
        'endpoints': [
            '/api/search - FOFA搜索',
            '/api/fingerprint - 指纹识别',
            '/api/scan/start - 开始批量扫描',
            '/api/scan/status - 扫描状态',
            '/api/scan/stop - 停止扫描'
        ]
    })


@app.route('/api/search', methods=['GET', 'POST'])
def api_search():
    """FOFA搜索接口（非流式，备用）"""
    if request.method == 'POST':
        data = request.json or {}
        keyword = data.get('keyword', '')
        query = data.get('query', '')
    else:
        keyword = request.args.get('keyword', '')
        query = request.args.get('query', '')
    
    if keyword and not query:
        query = f'title="{keyword}"'
    
    if not query:
        return jsonify({'success': False, 'error': '请提供搜索关键词'})
    
    # 使用多页获取
    result = fofa_search_multi_page(query)
    
    if result['success']:
        # 处理结果，过滤无效数据
        valid_results = []
        for item in result['results']:
            ip = item.get('ip', '')
            port = str(item.get('port', '80'))
            domain = item.get('domain', '')
            host = item.get('host', '')
            protocol = item.get('protocol', 'http')
            
            # 过滤无效数据
            if ip == '0.0.0.0' or port == '0':
                continue
            
            # 构建显示名称和URL
            if domain and domain.strip():
                display = f"{domain}:{port}" if port not in ['80', '443'] else domain
            elif ip:
                display = f"{ip}:{port}" if port not in ['80', '443'] else ip
            else:
                display = host
            
            if '://' in host:
                full_url = host
            else:
                proto = 'https' if protocol == 'https' or port == '443' else 'http'
                base = domain if domain else ip
                full_url = f"{proto}://{base}"
                if port not in ['80', '443']:
                    full_url += f":{port}"
            
            valid_results.append({
                'display': display,
                'url': full_url,
                'ip': ip,
                'port': port,
                'domain': domain,
                'title': item.get('title', ''),
                'server': item.get('server', ''),
                'country': item.get('country_name', ''),
                'protocol': protocol
            })
        
        result['results'] = valid_results
        result['unique_count'] = len(valid_results)
    
    return jsonify(result)


@app.route('/api/search/stream', methods=['GET', 'POST'])
def api_search_stream():
    """FOFA流式搜索接口 - 边获取边去重边推送(SSE)"""
    if request.method == 'POST':
        data = request.json or {}
        keyword = data.get('keyword', '')
        query = data.get('query', '')
    else:
        keyword = request.args.get('keyword', '')
        query = request.args.get('query', '')
    
    if keyword and not query:
        query = f'title="{keyword}"'
    
    if not query:
        return jsonify({'success': False, 'error': '请提供搜索关键词'})
    
    def generate():
        for data in fofa_search_stream_generator(query):
            yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
    
    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
            'X-Accel-Buffering': 'no'
        }
    )


@app.route('/api/fingerprint', methods=['POST'])
def api_fingerprint():
    """单个目标指纹识别"""
    data = request.json or {}
    url = data.get('url', '')
    finger_path = data.get('finger_path', '/static/js/home.js')
    
    if not url:
        return jsonify({'success': False, 'error': '请提供目标URL'})
    
    result = check_fingerprint(url, finger_path)
    result['url'] = url
    result['finger_path'] = finger_path
    
    return jsonify(result)


@app.route('/api/scan/batch', methods=['POST'])
def api_batch_scan():
    """批量指纹扫描"""
    data = request.json or {}
    targets = data.get('targets', [])
    finger_path = data.get('finger_path', '/static/js/home.js')
    max_workers = data.get('max_workers', 10)
    
    if not targets:
        return jsonify({'success': False, 'error': '请提供扫描目标'})
    
    results = []
    
    def scan_target(target):
        url = target.get('url', '') if isinstance(target, dict) else target
        result = check_fingerprint(url, finger_path)
        result['url'] = url
        result['display'] = target.get('display', url) if isinstance(target, dict) else url
        return result
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(scan_target, t): t for t in targets}
        
        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                target = futures[future]
                url = target.get('url', str(target)) if isinstance(target, dict) else str(target)
                results.append({
                    'url': url,
                    'success': False,
                    'error': str(e),
                    'status': 'error'
                })
    
    # 统计
    found_count = sum(1 for r in results if r.get('status') == 'found')
    error_count = sum(1 for r in results if r.get('status') in ['error', 'timeout', 'connection_error'])
    
    return jsonify({
        'success': True,
        'total': len(targets),
        'found': found_count,
        'errors': error_count,
        'results': results
    })


@app.route('/api/scan/single', methods=['POST'])
def api_single_scan():
    """
    单个目标扫描（用于流式扫描）
    
    请求参数:
        url: 目标URL
        display: 显示名称
        finger_path: 指纹路径
        keyword: 要匹配的关键词（可选，区分大小写）
    """
    data = request.json or {}
    url = data.get('url', '')
    display = data.get('display', url)
    finger_path = data.get('finger_path', '/static/js/player.js')
    keyword = data.get('keyword', None)  # 自定义关键词
    
    if not url:
        return jsonify({'success': False, 'error': '请提供目标URL'})
    
    # 调用指纹检测，传入自定义关键词
    result = check_fingerprint(url, finger_path, custom_keyword=keyword)
    result['url'] = url
    result['display'] = display
    result['finger_path'] = finger_path
    
    return jsonify(result)


if __name__ == '__main__':
    print("=" * 50)
    print("MacCMS Scanner API 服务启动中...")
    print("=" * 50)
    print(f"服务地址: http://127.0.0.1:5000")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
