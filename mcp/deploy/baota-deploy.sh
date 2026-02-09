#!/bin/bash
# ============================================
# MCP AI Red Team 宝塔部署脚本
# 适用于 CentOS 7/8, Ubuntu 18/20/22
# ============================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "============================================"
echo "  MCP AI Red Team 宝塔部署脚本"
echo "============================================"
echo -e "${NC}"

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}请使用root用户运行此脚本${NC}"
    exit 1
fi

# 项目路径配置
PROJECT_NAME="mcp-redteam"
PROJECT_DIR="/www/wwwroot/${PROJECT_NAME}"
PYTHON_VERSION="3.10"
VENV_DIR="${PROJECT_DIR}/venv"

echo -e "${GREEN}[1/8] 创建项目目录...${NC}"
mkdir -p ${PROJECT_DIR}
mkdir -p ${PROJECT_DIR}/logs

echo -e "${GREEN}[2/8] 安装系统依赖...${NC}"
# 检测系统类型
if [ -f /etc/redhat-release ]; then
    # CentOS/RHEL
    yum install -y epel-release
    yum install -y python3 python3-pip python3-devel gcc make
    yum install -y nmap whois bind-utils curl wget git
    yum install -y openssl-devel libffi-devel
elif [ -f /etc/debian_version ]; then
    # Ubuntu/Debian
    apt update
    apt install -y python3 python3-pip python3-venv python3-dev gcc make
    apt install -y nmap whois dnsutils curl wget git
    apt install -y libssl-dev libffi-dev
fi

echo -e "${GREEN}[3/8] 创建Python虚拟环境...${NC}"
cd ${PROJECT_DIR}
python3 -m venv ${VENV_DIR}
source ${VENV_DIR}/bin/activate

echo -e "${GREEN}[4/8] 安装Python依赖...${NC}"
pip install --upgrade pip
pip install flask flask-cors python-socketio eventlet gunicorn
pip install python-nmap dnspython requests httpx beautifulsoup4
pip install pyyaml python-dotenv colorama rich click pydantic
pip install openai anthropic langchain

echo -e "${GREEN}[5/8] 安装安全工具 (可选)...${NC}"
# 这些工具需要手动安装或使用包管理器
echo -e "${YELLOW}以下工具需要手动安装:${NC}"
echo "  - subfinder: go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"
echo "  - httpx: go install github.com/projectdiscovery/httpx/cmd/httpx@latest"
echo "  - nuclei: go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest"

echo -e "${GREEN}[6/8] 创建Supervisor配置...${NC}"
cat > /etc/supervisord.d/${PROJECT_NAME}.ini << EOF
[program:${PROJECT_NAME}]
directory=${PROJECT_DIR}
command=${VENV_DIR}/bin/gunicorn -w 4 -b 127.0.0.1:5000 --timeout 300 "core.mcp_server:create_app()"
user=www
autostart=true
autorestart=true
startsecs=10
stopwaitsecs=60
stdout_logfile=${PROJECT_DIR}/logs/access.log
stderr_logfile=${PROJECT_DIR}/logs/error.log
environment=PYTHONUNBUFFERED="1",PATH="${VENV_DIR}/bin:/usr/local/bin:/usr/bin:/bin"
EOF

echo -e "${GREEN}[7/8] 创建Nginx配置...${NC}"
cat > /www/server/panel/vhost/nginx/${PROJECT_NAME}.conf << 'EOF'
server {
    listen 80;
    server_name your_domain.com;  # 修改为你的域名
    
    # 静态文件
    location / {
        root /www/wwwroot/mcp-redteam;
        index test-tools.html index.html;
        try_files $uri $uri/ =404;
    }
    
    # API代理
    location /api/ {
        proxy_pass http://127.0.0.1:5000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_connect_timeout 300s;
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
    }
    
    # MCP服务直接代理
    location ~ ^/(execute|chat|tools|health|logs|session|chain|workflow|report|ai|events) {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_buffering off;
        proxy_cache off;
        proxy_connect_timeout 300s;
        proxy_read_timeout 600s;
    }
    
    # SSE事件流
    location /events {
        proxy_pass http://127.0.0.1:5000/events;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_buffering off;
        proxy_cache off;
        chunked_transfer_encoding off;
        proxy_read_timeout 86400s;
    }
    
    access_log /www/wwwlogs/${PROJECT_NAME}.access.log;
    error_log /www/wwwlogs/${PROJECT_NAME}.error.log;
}
EOF

echo -e "${GREEN}[8/8] 启动服务...${NC}"
supervisorctl reread
supervisorctl update
supervisorctl start ${PROJECT_NAME}
nginx -s reload

echo -e "${CYAN}"
echo "============================================"
echo "  部署完成!"
echo "============================================"
echo -e "${NC}"
echo -e "MCP服务: http://127.0.0.1:5000"
echo -e "测试页面: http://your_domain.com/test-tools.html"
echo ""
echo -e "${YELLOW}重要提示:${NC}"
echo "1. 请修改Nginx配置中的域名"
echo "2. 请上传项目文件到 ${PROJECT_DIR}"
echo "3. 建议配置SSL证书"
echo ""
