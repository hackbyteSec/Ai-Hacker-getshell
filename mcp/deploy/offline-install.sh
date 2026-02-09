#!/bin/bash
# ============================================
# MCP 离线部署脚本
# 无需联网，使用本地packages目录安装依赖
# ============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  MCP AI Red Team 离线部署${NC}"
echo -e "${GREEN}============================================${NC}"

PROJECT_DIR=$(dirname "$(readlink -f "$0")")
cd "$PROJECT_DIR"

echo -e "${YELLOW}[1/4] 创建Python虚拟环境...${NC}"
python3 -m venv venv
source venv/bin/activate

echo -e "${YELLOW}[2/4] 从本地packages目录安装依赖...${NC}"
pip install --no-index --find-links=./packages -r requirements.txt

echo -e "${YELLOW}[3/4] 安装Gunicorn...${NC}"
pip install --no-index --find-links=./packages gunicorn || pip install gunicorn

echo -e "${YELLOW}[4/4] 创建日志目录...${NC}"
mkdir -p logs
mkdir -p reports

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  离线部署完成!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "启动服务: ${YELLOW}source venv/bin/activate && python main.py${NC}"
echo -e "或使用Gunicorn: ${YELLOW}gunicorn -w 4 -b 0.0.0.0:5000 wsgi:application${NC}"
echo ""
