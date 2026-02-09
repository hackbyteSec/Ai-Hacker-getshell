#!/bin/bash
# ============================================
# 离线安装预下载的安全工具
# 在服务器上运行此脚本
# ============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
TOOLS_DIR="$SCRIPT_DIR/linux-amd64"
INSTALL_DIR="/usr/local/bin"

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  安装预下载的安全工具${NC}"
echo -e "${GREEN}============================================${NC}"

cd "$TOOLS_DIR"

# 解压并安装 subfinder
if [ -f "subfinder.zip" ]; then
    echo -e "${YELLOW}[1/6] 安装 subfinder...${NC}"
    unzip -o subfinder.zip -d subfinder_temp
    mv subfinder_temp/subfinder "$INSTALL_DIR/" 2>/dev/null || mv subfinder "$INSTALL_DIR/"
    rm -rf subfinder_temp subfinder.zip
fi

# 解压并安装 httpx
if [ -f "httpx.zip" ]; then
    echo -e "${YELLOW}[2/6] 安装 httpx...${NC}"
    unzip -o httpx.zip -d httpx_temp
    mv httpx_temp/httpx "$INSTALL_DIR/" 2>/dev/null || mv httpx "$INSTALL_DIR/"
    rm -rf httpx_temp httpx.zip
fi

# 解压并安装 nuclei
if [ -f "nuclei.zip" ]; then
    echo -e "${YELLOW}[3/6] 安装 nuclei...${NC}"
    unzip -o nuclei.zip -d nuclei_temp
    mv nuclei_temp/nuclei "$INSTALL_DIR/" 2>/dev/null || mv nuclei "$INSTALL_DIR/"
    rm -rf nuclei_temp nuclei.zip
fi

# 解压并安装 naabu
if [ -f "naabu.zip" ]; then
    echo -e "${YELLOW}[4/6] 安装 naabu...${NC}"
    unzip -o naabu.zip -d naabu_temp
    mv naabu_temp/naabu "$INSTALL_DIR/" 2>/dev/null || mv naabu "$INSTALL_DIR/"
    rm -rf naabu_temp naabu.zip
fi

# 解压并安装 ffuf
if [ -f "ffuf.tar.gz" ]; then
    echo -e "${YELLOW}[5/6] 安装 ffuf...${NC}"
    tar -xzf ffuf.tar.gz
    mv ffuf "$INSTALL_DIR/"
    rm -f ffuf.tar.gz
fi

# 解压并安装 gobuster
if [ -f "gobuster.tar.gz" ]; then
    echo -e "${YELLOW}[6/6] 安装 gobuster...${NC}"
    tar -xzf gobuster.tar.gz
    mv gobuster "$INSTALL_DIR/" 2>/dev/null || true
    rm -f gobuster.tar.gz
fi

# 设置执行权限
chmod +x "$INSTALL_DIR/subfinder" 2>/dev/null || true
chmod +x "$INSTALL_DIR/httpx" 2>/dev/null || true
chmod +x "$INSTALL_DIR/nuclei" 2>/dev/null || true
chmod +x "$INSTALL_DIR/naabu" 2>/dev/null || true
chmod +x "$INSTALL_DIR/ffuf" 2>/dev/null || true
chmod +x "$INSTALL_DIR/gobuster" 2>/dev/null || true

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  安装验证${NC}"
echo -e "${GREEN}============================================${NC}"

tools=("subfinder" "httpx" "nuclei" "naabu" "ffuf" "gobuster")

for tool in "${tools[@]}"; do
    if command -v $tool &> /dev/null; then
        version=$($tool -version 2>/dev/null | head -1 || echo "已安装")
        echo -e "  ${GREEN}✓${NC} $tool - $version"
    else
        echo -e "  ${RED}✗${NC} $tool (安装失败)"
    fi
done

echo ""
echo -e "${GREEN}工具安装完成!${NC}"
echo -e "${YELLOW}提示: 可能还需要安装系统工具:${NC}"
echo -e "  apt install -y nmap nikto sqlmap hydra sslscan whatweb wafw00f"
