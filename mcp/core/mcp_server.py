#!/usr/bin/env python3
"""
AI Red Team MCP Server - 核心服务器
基于Kali Linux的AI自动化红队打点工具
"""

import json
import logging
import os
import sys
import time
import threading
import shutil
from collections import deque
from datetime import datetime
from functools import wraps
from typing import Any, Dict, List, Optional, Callable

from flask import Flask, jsonify, request, Response
from flask_cors import CORS

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tool_registry import ToolRegistry
from core.session_manager import SessionManager
from core.ai_engine import AIDecisionEngine
from core.attack_chain import AttackChainEngine
from utils.logger import setup_logger

# 配置日志
logger = setup_logger("mcp_server")

class MCPServer:
    """MCP服务器核心类"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.app = Flask(__name__)
        CORS(self.app)
        
        self.config = config or self._load_default_config()
        self.tool_registry = ToolRegistry()
        self.session_manager = SessionManager()
        self.ai_engine = AIDecisionEngine(self.config.get("ai", {}))
        self.attack_chain_engine = None  # 延迟初始化

        self._event_cond = threading.Condition()
        self._events = deque(maxlen=5000)
        self._next_event_id = 0
        
        self._register_routes()
        self._register_error_handlers()
        
        logger.info("MCP服务器初始化完成")

    def _ui_log_dir(self) -> str:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        p = os.path.join(base, "logs")
        os.makedirs(p, exist_ok=True)
        return p

    def _ui_log_file(self) -> str:
        return os.path.join(self._ui_log_dir(), "ui_status.jsonl")

    def _append_ui_log(self, record: Dict[str, Any]) -> None:
        rec = dict(record or {})
        rec.setdefault("ts", datetime.now().isoformat())
        path = self._ui_log_file()
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # 工具名到依赖的映射表
    TOOL_DEPENDENCY_MAP = {
        # 信息收集
        "nmap_scan": "nmap",
        "nmap_quick": "nmap",
        "subdomain_enum": "subfinder",
        "dns_enum": "dig",
        "zone_transfer": "dig",
        "whois_lookup": "whois",
        "theharvester": "theHarvester",
        "whatweb": "whatweb",
        "wafw00f": "wafw00f",
        "httpx_probe": "httpx",
        "quick_recon": "nmap",
        # 漏洞扫描
        "vuln_scan": "nuclei",
        "nikto_scan": "nikto",
        "sslscan": "sslscan",
        "testssl": "testssl.sh",
        "searchsploit": "searchsploit",
        "nuclei_full": "nuclei",
        "nuclei_cve": "nuclei",
        "nuclei_complete_scan": "nuclei",
        # Web攻击
        "sqli_test": "sqlmap",
        "xss_scan": "xsstrike",
        "dir_scan": "gobuster",
        "gobuster": "gobuster",
        "ffuf": "ffuf",
        # 网络攻击
        "brute_force": "hydra",
        "crackmapexec": "crackmapexec",
        "smb_enum": "enum4linux",
        "ssh_audit": "ssh-audit",
        "snmp_walk": "snmpwalk",
        "ldap_enum": "ldapsearch",
        # 漏洞利用
        "msf_search": "msfconsole",
        "msfvenom": "msfvenom",
        # 云安全
        "aws_enum": "aws",
        "s3_scanner": "aws",
        "azure_enum": "az",
        "kube_hunter": "kube-hunter",
    }

    def _check_dependency(self, tool_name: str) -> Dict[str, Any]:
        """检查工具的外部依赖是否已安装"""
        name = (tool_name or "").strip()
        
        # 先从映射表中查找
        dep = self.TOOL_DEPENDENCY_MAP.get(name)
        
        # 如果映射表中没有，尝试模糊匹配
        if not dep:
            name_lower = name.lower()
            if name_lower.startswith("nmap") or "_nmap" in name_lower:
                dep = "nmap"
            elif "nuclei" in name_lower:
                dep = "nuclei"
            elif "sqlmap" in name_lower or "sqli" in name_lower:
                dep = "sqlmap"
            elif "nikto" in name_lower:
                dep = "nikto"
            elif "gobuster" in name_lower or "dir_scan" in name_lower:
                dep = "gobuster"
            elif "hydra" in name_lower or "brute" in name_lower:
                dep = "hydra"
        
        # 无外部依赖
        if not dep:
            return {"dependency": None, "available": True}
        
        # 检查依赖是否存在
        available = shutil.which(dep) is not None
        
        # 特殊处理：某些工具可能有别名
        if not available:
            aliases = {
                "theHarvester": ["theharvester", "theHarvester.py"],
                "testssl.sh": ["testssl", "testssl.sh"],
                "ssh-audit": ["ssh_audit", "sshaudit"],
                "kube-hunter": ["kube_hunter", "kubehunter"],
                "enum4linux": ["enum4linux-ng", "enum4linux.pl"],
            }
            for alias in aliases.get(dep, []):
                if shutil.which(alias):
                    available = True
                    break
        
        return {"dependency": dep, "available": available}

    def _build_tools_link_status(self) -> List[Dict[str, Any]]:
        tools = self.tool_registry.list_tools()
        statuses = []
        for t in tools:
            tool_name = t.get("name")
            dep = self._check_dependency(tool_name)
            statuses.append({
                "tool": tool_name,
                "category": t.get("category"),
                "linked": True,
                "dependency": dep.get("dependency"),
                "dependency_ok": bool(dep.get("available")),
                "requires_root": bool(t.get("requires_root"))
            })
        return statuses

    def _emit_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        payload = dict(event or {})
        payload.setdefault("ts", datetime.now().isoformat())
        with self._event_cond:
            self._next_event_id += 1
            payload["id"] = self._next_event_id
            self._events.append(payload)
            self._event_cond.notify_all()
        return payload

    def _iter_events_since(self, since_id: int):
        with self._event_cond:
            return [e for e in list(self._events) if e.get("id", 0) > since_id]

    def _extract_target(self, text: str) -> Dict[str, str]:
        import re
        s = (text or "").strip()
        m = re.search(r'(https?://[^\s]+)', s, flags=re.IGNORECASE)
        if m:
            return {"type": "url", "value": m.group(1)}
        m = re.search(r'(\b\d{1,3}(?:\.\d{1,3}){3}/\d{1,2}\b)', s)
        if m:
            return {"type": "network", "value": m.group(1)}
        m = re.search(r'(\b\d{1,3}(?:\.\d{1,3}){3}\b)', s)
        if m:
            return {"type": "ip", "value": m.group(1)}
        m = re.search(r'([a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z]{2,})+)', s)
        if m:
            return {"type": "domain", "value": m.group(1)}
        return {"type": "unknown", "value": ""}

    def _extract_json_payload(self, text: str) -> Dict[str, Any]:
        if not text:
            return {}
        idx = text.rfind("{")
        if idx < 0:
            return {}
        try:
            return json.loads(text[idx:])
        except Exception:
            return {}

    def _infer_params_for_tool(self, tool_name: str, message: str, tool_params: Dict[str, Any]) -> Dict[str, Any]:
        tool = self.tool_registry.get_tool(tool_name)
        if not tool:
            raise ValueError(f"工具不存在: {tool_name}")

        params = dict(tool_params or {})
        target_info = self._extract_target(message)
        tv = target_info.get("value") or ""

        for p in tool.parameters:
            if not p.required:
                continue
            if p.name in params:
                continue
            if p.default is not None:
                params[p.name] = p.default
                continue

            name = p.name.lower()
            if name in ("target", "host"):
                if tv:
                    params[p.name] = tv
            elif name == "domain":
                if target_info.get("type") in ("domain", "url") and tv:
                    params[p.name] = tv.replace("http://", "").replace("https://", "").split("/")[0]
            elif name in ("url", "base_url"):
                if tv:
                    params[p.name] = tv if tv.lower().startswith(("http://", "https://")) else f"http://{tv}"
            elif name == "targets":
                if tv:
                    params[p.name] = tv

        missing = []
        for p in tool.parameters:
            if p.required and p.name not in params and p.default is None:
                missing.append(p.name)
        if missing:
            raise ValueError(f"缺少必需参数: {', '.join(missing)}")

        return params

    def _get_attack_chain_engine(self):
        """获取攻击链引擎(延迟初始化)"""
        if self.attack_chain_engine is None:
            self.attack_chain_engine = AttackChainEngine(self.tool_registry)
        return self.attack_chain_engine
    
    def _load_default_config(self) -> Dict[str, Any]:
        """加载默认配置"""
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "config", "config.yaml"
        )
        if os.path.exists(config_path):
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {
            "server": {"host": "127.0.0.1", "port": 5000},
            "ai": {"provider": "openai", "model": "gpt-4"},
            "logging": {"level": "INFO"}
        }
    
    def _register_routes(self):
        """注册API路由"""
        
        @self.app.route("/", methods=["GET"])
        def index():
            return jsonify({
                "name": "AI Red Team MCP Server",
                "version": "1.0.0",
                "status": "running",
                "timestamp": datetime.now().isoformat()
            })
        
        @self.app.route("/health", methods=["GET"])
        def health():
            return jsonify({"status": "healthy", "uptime": self._get_uptime()})

        @self.app.route("/logs/init", methods=["GET"])
        def logs_init():
            path = self._ui_log_file()
            created = not os.path.exists(path) or os.path.getsize(path) == 0
            statuses = self._build_tools_link_status()
            if created:
                self._append_ui_log({
                    "type": "init",
                    "message": "ui_status 初始化",
                    "total_tools": len(statuses)
                })
                for s in statuses:
                    self._append_ui_log({
                        "type": "tool_link_check",
                        **s
                    })
            return jsonify({
                "success": True,
                "created": created,
                "file": path,
                "total_tools": len(statuses),
                "ok": sum(1 for s in statuses if s.get("dependency_ok", True)),
                "missing": sum(1 for s in statuses if s.get("dependency_ok") is False),
                "statuses": statuses
            })

        @self.app.route("/logs/status", methods=["GET"])
        def logs_status():
            path = self._ui_log_file()
            if not os.path.exists(path):
                return jsonify({"success": False, "error": "ui_status 未初始化"}), 404
            latest = {}
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        rec = json.loads(line)
                    except Exception:
                        continue
                    if rec.get("type") == "tool_link_check" and rec.get("tool"):
                        latest[rec["tool"]] = rec
            statuses = list(latest.values())
            statuses.sort(key=lambda x: x.get("tool") or "")
            return jsonify({
                "success": True,
                "file": path,
                "total_tools": len(statuses),
                "ok": sum(1 for s in statuses if s.get("dependency_ok", True)),
                "missing": sum(1 for s in statuses if s.get("dependency_ok") is False),
                "statuses": statuses
            })

        @self.app.route("/events", methods=["GET"])
        def events():
            since = request.args.get("since", "")
            try:
                since_id = int(since) if since else 0
            except Exception:
                since_id = 0

            def gen():
                last_id = since_id
                yield ": connected\n\n"
                while True:
                    batch = self._iter_events_since(last_id)
                    if batch:
                        for e in batch:
                            last_id = max(last_id, int(e.get("id", 0) or 0))
                            yield f"data: {json.dumps(e, ensure_ascii=False)}\n\n"
                        continue
                    with self._event_cond:
                        self._event_cond.wait(timeout=2)
                    yield ": ping\n\n"

            headers = {
                "Content-Type": "text/event-stream",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
            return Response(gen(), headers=headers)
        
        @self.app.route("/tools", methods=["GET"])
        def list_tools():
            """列出所有可用工具"""
            tools = self.tool_registry.list_tools()
            return jsonify({
                "tools": tools,
                "total": len(tools)
            })
        
        @self.app.route("/tools/<tool_name>", methods=["GET"])
        def get_tool_info(tool_name: str):
            """获取工具详情"""
            tool = self.tool_registry.get_tool(tool_name)
            if tool:
                return jsonify(tool.to_dict())
            return jsonify({"error": f"工具 {tool_name} 不存在"}), 404
        
        @self.app.route("/execute", methods=["POST"])
        def execute_tool():
            """执行工具"""
            data = request.get_json()
            if not data:
                return jsonify({"error": "请求体为空"}), 400
            
            tool_name = data.get("tool")
            params = data.get("params", {})
            session_id = data.get("session_id")
            
            if not tool_name:
                return jsonify({"error": "未指定工具名称"}), 400
            
            try:
                self._emit_event({
                    "level": "INFO",
                    "status": "RUNNING",
                    "service": "/execute",
                    "tool": tool_name,
                    "params": params,
                    "session_id": session_id
                })
                start = time.perf_counter()
                result = self.tool_registry.execute(tool_name, params, session_id)
                duration = time.perf_counter() - start
                self._emit_event({
                    "level": "INFO",
                    "status": "SUCCESS",
                    "service": "/execute",
                    "tool": tool_name,
                    "params": params,
                    "duration": duration,
                    "session_id": session_id
                })
                return jsonify({
                    "success": True,
                    "tool": tool_name,
                    "result": result,
                    "duration": duration,
                    "timestamp": datetime.now().isoformat()
                })
            except ValueError as e:
                duration = None
                try:
                    duration = time.perf_counter() - start
                except Exception:
                    pass
                self._emit_event({
                    "level": "WARNING",
                    "status": "ERROR",
                    "service": "/execute",
                    "tool": tool_name,
                    "params": params,
                    "duration": duration,
                    "error": str(e),
                    "session_id": session_id
                })
                return jsonify({
                    "success": False,
                    "tool": tool_name,
                    "error": str(e),
                    "duration": duration
                }), 400
            except Exception as e:
                duration = None
                try:
                    duration = time.perf_counter() - start
                except Exception:
                    pass
                logger.error(f"执行工具 {tool_name} 失败: {str(e)}")
                self._emit_event({
                    "level": "ERROR",
                    "status": "ERROR",
                    "service": "/execute",
                    "tool": tool_name,
                    "params": params,
                    "duration": duration,
                    "error": str(e),
                    "session_id": session_id
                })
                return jsonify({
                    "success": False,
                    "tool": tool_name,
                    "error": str(e),
                    "duration": duration
                }), 500

        @self.app.route("/chat", methods=["POST"])
        def chat():
            data = request.get_json() or {}
            message = (data.get("message") or "").strip()
            tools = data.get("tools") or []
            context = data.get("context") or {}

            session_id = data.get("session_id") or context.get("session_id")
            if not session_id:
                session = self.session_manager.create_session("chat_session")
                session_id = session.id

            payload_json = self._extract_json_payload(message)
            tool_params_map = payload_json.get("tool_params") if isinstance(payload_json, dict) else None
            if not isinstance(tool_params_map, dict):
                tool_params_map = {}

            self._emit_event({
                "level": "INFO",
                "status": "RUNNING",
                "service": "/chat",
                "session_id": session_id,
                "params": {"message": message, "tools": tools, "context": context}
            })

            start = time.perf_counter()
            results = []
            try:
                if tools:
                    for tool_name in tools:
                        per_tool_params = tool_params_map.get(tool_name, {}) if isinstance(tool_params_map, dict) else {}
                        try:
                            inferred = self._infer_params_for_tool(tool_name, message, per_tool_params)
                        except Exception as e:
                            results.append({
                                "tool": tool_name,
                                "success": False,
                                "error": str(e),
                                "params": per_tool_params
                            })
                            continue

                        self._emit_event({
                            "level": "INFO",
                            "status": "RUNNING",
                            "service": "/chat.tool",
                            "tool": tool_name,
                            "params": inferred,
                            "session_id": session_id
                        })
                        t0 = time.perf_counter()
                        try:
                            tool_result = self.tool_registry.execute(tool_name, inferred, session_id)
                            tdur = time.perf_counter() - t0
                            results.append({
                                "tool": tool_name,
                                "success": True,
                                "duration": tdur,
                                "result": tool_result,
                                "params": inferred
                            })
                            self._emit_event({
                                "level": "INFO",
                                "status": "SUCCESS",
                                "service": "/chat.tool",
                                "tool": tool_name,
                                "params": inferred,
                                "duration": tdur,
                                "session_id": session_id
                            })
                        except Exception as e:
                            tdur = time.perf_counter() - t0
                            results.append({
                                "tool": tool_name,
                                "success": False,
                                "duration": tdur,
                                "error": str(e),
                                "params": inferred
                            })
                            self._emit_event({
                                "level": "ERROR",
                                "status": "ERROR",
                                "service": "/chat.tool",
                                "tool": tool_name,
                                "params": inferred,
                                "duration": tdur,
                                "error": str(e),
                                "session_id": session_id
                            })

                    ok = sum(1 for r in results if r.get("success"))
                    total = len(results)
                    duration = time.perf_counter() - start
                    response_text = f"已执行 {total} 个工具，成功 {ok} 个，会话 {session_id}。"
                    self._emit_event({
                        "level": "INFO",
                        "status": "SUCCESS",
                        "service": "/chat",
                        "session_id": session_id,
                        "duration": duration
                    })
                    return jsonify({
                        "session_id": session_id,
                        "response": response_text,
                        "results": results,
                        "duration": duration
                    })

                target_info = self._extract_target(message)
                target = target_info.get("value") or ""
                duration = time.perf_counter() - start
                if target:
                    analysis = self.ai_engine.analyze_target(target, context)
                    self._emit_event({
                        "level": "INFO",
                        "status": "SUCCESS",
                        "service": "/chat",
                        "session_id": session_id,
                        "duration": duration
                    })
                    return jsonify({
                        "session_id": session_id,
                        "response": json.dumps(analysis, ensure_ascii=False, indent=2),
                        "analysis": analysis,
                        "duration": duration
                    })

                self._emit_event({
                    "level": "WARNING",
                    "status": "WARNING",
                    "service": "/chat",
                    "session_id": session_id,
                    "duration": duration
                })
                return jsonify({
                    "session_id": session_id,
                    "response": "未检测到可分析目标；你可以输入 URL/IP/域名，或先选择工具后发送。",
                    "duration": duration
                })
            except Exception as e:
                duration = time.perf_counter() - start
                self._emit_event({
                    "level": "ERROR",
                    "status": "ERROR",
                    "service": "/chat",
                    "session_id": session_id,
                    "duration": duration,
                    "error": str(e)
                })
                return jsonify({
                    "session_id": session_id,
                    "success": False,
                    "error": str(e),
                    "response": f"处理失败: {str(e)}",
                    "duration": duration
                }), 500
        
        @self.app.route("/ai/analyze", methods=["POST"])
        def ai_analyze():
            """AI分析目标"""
            data = request.get_json()
            target = data.get("target")
            context = data.get("context", {})
            
            if not target:
                return jsonify({"error": "未指定目标"}), 400
            
            try:
                analysis = self.ai_engine.analyze_target(target, context)
                return jsonify({
                    "success": True,
                    "analysis": analysis
                })
            except Exception as e:
                logger.error(f"AI分析失败: {str(e)}")
                return jsonify({"success": False, "error": str(e)}), 500
        
        @self.app.route("/ai/plan", methods=["POST"])
        def ai_plan():
            """AI生成攻击计划"""
            data = request.get_json()
            target = data.get("target")
            recon_data = data.get("recon_data", {})
            
            try:
                plan = self.ai_engine.generate_attack_plan(target, recon_data)
                return jsonify({
                    "success": True,
                    "plan": plan
                })
            except Exception as e:
                logger.error(f"生成攻击计划失败: {str(e)}")
                return jsonify({"success": False, "error": str(e)}), 500
        
        @self.app.route("/session/create", methods=["POST"])
        def create_session():
            """创建新会话"""
            data = request.get_json() or {}
            session = self.session_manager.create_session(data.get("name"))
            return jsonify({
                "session_id": session.id,
                "created_at": session.created_at.isoformat()
            })
        
        @self.app.route("/session/<session_id>", methods=["GET"])
        def get_session(session_id: str):
            """获取会话信息"""
            session = self.session_manager.get_session(session_id)
            if session:
                return jsonify(session.to_dict())
            return jsonify({"error": "会话不存在"}), 404
        
        @self.app.route("/session/<session_id>/results", methods=["GET"])
        def get_session_results(session_id: str):
            """获取会话结果"""
            results = self.session_manager.get_results(session_id)
            return jsonify({"results": results})
        
        @self.app.route("/workflow/auto", methods=["POST"])
        def auto_workflow():
            """自动化工作流"""
            data = request.get_json()
            target = data.get("target")
            options = data.get("options", {})
            
            if not target:
                return jsonify({"error": "未指定目标"}), 400
            
            try:
                # 创建会话
                session = self.session_manager.create_session(f"auto_{target}")
                
                # 执行自动化流程
                from modules.workflow import AutoWorkflow
                workflow = AutoWorkflow(
                    self.tool_registry, 
                    self.ai_engine,
                    session
                )
                result = workflow.execute(target, options)
                
                return jsonify({
                    "success": True,
                    "session_id": session.id,
                    "result": result
                })
            except Exception as e:
                logger.error(f"自动化工作流失败: {str(e)}")
                return jsonify({"success": False, "error": str(e)}), 500
        
        @self.app.route("/report/generate", methods=["POST"])
        def generate_report():
            """生成报告"""
            data = request.get_json()
            session_id = data.get("session_id")
            format_type = data.get("format", "html")
            
            try:
                from utils.report_generator import ReportGenerator
                generator = ReportGenerator()
                report_path = generator.generate(session_id, format_type)
                return jsonify({
                    "success": True,
                    "report_path": report_path
                })
            except Exception as e:
                logger.error(f"报告生成失败: {str(e)}")
                return jsonify({"success": False, "error": str(e)}), 500
        
        # ===== 攻击链API =====
        
        @self.app.route("/chain/create", methods=["POST"])
        def create_attack_chain():
            """创建攻击链"""
            data = request.get_json()
            target = data.get("target")
            target_type = data.get("target_type", "ip")
            objectives = data.get("objectives", [])
            
            if not target:
                return jsonify({"error": "未指定目标"}), 400
            
            try:
                engine = self._get_attack_chain_engine()
                chain = engine.create_chain(target, target_type, objectives)
                return jsonify({
                    "success": True,
                    "chain_id": chain.id,
                    "nodes_count": len(chain.nodes),
                    "chain": engine.get_chain_status(chain.id)
                })
            except Exception as e:
                logger.error(f"创建攻击链失败: {str(e)}")
                return jsonify({"success": False, "error": str(e)}), 500
        
        @self.app.route("/chain/<chain_id>/execute", methods=["POST"])
        def execute_attack_chain(chain_id: str):
            """执行攻击链"""
            data = request.get_json() or {}
            session_id = data.get("session_id")
            
            try:
                engine = self._get_attack_chain_engine()
                result = engine.execute_chain(chain_id, session_id)
                return jsonify({
                    "success": True,
                    "result": result
                })
            except Exception as e:
                logger.error(f"执行攻击链失败: {str(e)}")
                return jsonify({"success": False, "error": str(e)}), 500
        
        @self.app.route("/chain/<chain_id>", methods=["GET"])
        def get_attack_chain(chain_id: str):
            """获取攻击链状态"""
            engine = self._get_attack_chain_engine()
            status = engine.get_chain_status(chain_id)
            if status:
                return jsonify(status)
            return jsonify({"error": "攻击链不存在"}), 404
        
        @self.app.route("/chain/<chain_id>/suggestions", methods=["GET"])
        def get_chain_suggestions(chain_id: str):
            """获取攻击建议"""
            engine = self._get_attack_chain_engine()
            suggestions = engine.suggest_next_steps(chain_id)
            return jsonify({
                "chain_id": chain_id,
                "suggestions": suggestions
            })
        
        # ===== 工具搜索API =====
        
        @self.app.route("/tools/search", methods=["GET"])
        def search_tools():
            """搜索工具"""
            keyword = request.args.get("q", "")
            if not keyword:
                return jsonify({"error": "请提供搜索关键词"}), 400
            
            results = self.tool_registry.search_tools(keyword)
            return jsonify({
                "query": keyword,
                "results": results,
                "count": len(results)
            })
        
        @self.app.route("/tools/stats", methods=["GET"])
        def tools_stats():
            """工具统计"""
            stats = self.tool_registry.get_stats()
            return jsonify(stats)
    
    def _register_error_handlers(self):
        """注册错误处理器"""
        
        @self.app.errorhandler(404)
        def not_found(e):
            return jsonify({"error": "资源不存在"}), 404
        
        @self.app.errorhandler(500)
        def server_error(e):
            return jsonify({"error": "服务器内部错误"}), 500
    
    def _get_uptime(self) -> str:
        """获取运行时间"""
        if hasattr(self, '_start_time'):
            delta = datetime.now() - self._start_time
            return str(delta)
        return "unknown"
    
    def register_tool(self, tool: 'BaseTool'):
        """注册工具"""
        self.tool_registry.register(tool)
    
    def run(self, host: str = None, port: int = None, debug: bool = False):
        """启动服务器"""
        self._start_time = datetime.now()
        host = host or self.config.get("server", {}).get("host", "127.0.0.1")
        port = port or self.config.get("server", {}).get("port", 5000)
        
        logger.info(f"MCP服务器启动: http://{host}:{port}")
        self.app.run(host=host, port=port, debug=debug, threaded=True)


def create_app(config: Dict[str, Any] = None) -> MCPServer:
    """创建MCP服务器实例"""
    server = MCPServer(config)
    
    # 注册所有模块
    from modules import register_all_modules
    register_all_modules(server)
    
    return server


if __name__ == "__main__":
    server = create_app()
    server.run(debug=True)
