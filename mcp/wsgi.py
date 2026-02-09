#!/usr/bin/env python3
"""
WSGI入口文件 - 用于Gunicorn/uWSGI部署
"""
import os
import sys

# 确保项目目录在Python路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.mcp_server import create_app
from mcp_tools import register_all_tools

# 创建应用实例
app = create_app()

# 注册所有工具
class ToolServer:
    def __init__(self, app_instance):
        self.app = app_instance
        self._tools = {}
    
    def register_tool(self, name, description, schema, handler):
        self._tools[name] = {
            'name': name,
            'description': description,
            'schema': schema,
            'handler': handler
        }

# 注册MCP工具
tool_server = ToolServer(app)
register_all_tools(tool_server)

# 获取Flask应用
application = app.app

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=5000, debug=False)
