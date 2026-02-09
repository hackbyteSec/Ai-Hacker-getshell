#!/bin/bash
# ============================================
# 安全工具离线下载脚本
# 下载预编译的Linux二进制文件
# ============================================

TOOLS_DIR="./tools/linux-amd64"
mkdir -p "$TOOLS_DIR"
cd "$TOOLS_DIR"

echo "============================================"
echo "  下载安全工具 (Linux amd64)"
echo "============================================"

# ProjectDiscovery 工具下载
echo "[1/6] 下载 subfinder..."
curl -sL https://github.com/projectdiscovery/subfinder/releases/latest/download/subfinder_linux_amd64.zip -o subfinder.zip
unzip -o subfinder.zip && rm subfinder.zip

echo "[2/6] 下载 httpx..."
curl -sL https://github.com/projectdiscovery/httpx/releases/latest/download/httpx_linux_amd64.zip -o httpx.zip
unzip -o httpx.zip && rm httpx.zip

echo "[3/6] 下载 nuclei..."
curl -sL https://github.com/projectdiscovery/nuclei/releases/latest/download/nuclei_linux_amd64.zip -o nuclei.zip
unzip -o nuclei.zip && rm nuclei.zip

echo "[4/6] 下载 naabu..."
curl -sL https://github.com/projectdiscovery/naabu/releases/latest/download/naabu_linux_amd64.zip -o naabu.zip
unzip -o naabu.zip && rm naabu.zip

echo "[5/6] 下载 ffuf..."
curl -sL https://github.com/ffuf/ffuf/releases/latest/download/ffuf_linux_amd64.tar.gz -o ffuf.tar.gz
tar -xzf ffuf.tar.gz && rm ffuf.tar.gz

echo "[6/6] 下载 gobuster..."
curl -sL https://github.com/OJ/gobuster/releases/latest/download/gobuster_linux_amd64.tar.gz -o gobuster.tar.gz
tar -xzf gobuster.tar.gz && rm gobuster.tar.gz

# 设置执行权限
chmod +x subfinder httpx nuclei naabu ffuf gobuster 2>/dev/null

echo ""
echo "============================================"
echo "  下载完成!"
echo "============================================"
ls -la
