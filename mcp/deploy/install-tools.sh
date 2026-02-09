#!/bin/bash
# ============================================
# MCP 安全工具一键安装脚本
# 适用于 CentOS 7/8, Ubuntu 18/20/22, Debian
# 版本: 2.0
# ============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  MCP 安全工具一键安装脚本 v2.0${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""

# 检测系统类型
detect_os() {
    if [ -f /etc/redhat-release ]; then
        OS="centos"
        PKG="yum"
    elif [ -f /etc/debian_version ]; then
        OS="ubuntu"
        PKG="apt"
    else
        echo -e "${RED}不支持的操作系统${NC}"
        exit 1
    fi
    echo -e "${GREEN}检测到系统: ${OS}${NC}"
}

# 安装基础工具
install_base() {
    echo -e "${YELLOW}[1/7] 安装基础工具...${NC}"
    if [ "$OS" == "centos" ]; then
        yum install -y epel-release
        yum install -y nmap whois bind-utils curl wget git unzip python3 python3-pip jq
        yum install -y net-snmp-utils openldap-clients
    else
        apt update
        apt install -y nmap whois dnsutils curl wget git unzip python3 python3-pip jq
        apt install -y snmp ldap-utils
    fi
}

# 安装Go语言
install_go() {
    echo -e "${YELLOW}[2/7] 安装Go语言...${NC}"
    if ! command -v go &> /dev/null; then
        GO_VERSION="1.22.0"
        wget -q https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz
        rm -rf /usr/local/go
        tar -C /usr/local -xzf go${GO_VERSION}.linux-amd64.tar.gz
        rm go${GO_VERSION}.linux-amd64.tar.gz
        
        # 配置环境变量
        echo 'export PATH=$PATH:/usr/local/go/bin:$HOME/go/bin' >> /etc/profile
        echo 'export GOPATH=$HOME/go' >> /etc/profile
        export PATH=$PATH:/usr/local/go/bin:$HOME/go/bin
        export GOPATH=$HOME/go
    fi
    echo -e "${GREEN}Go版本: $(go version)${NC}"
}

# 安装ProjectDiscovery工具链
install_pd_tools() {
    echo -e "${YELLOW}[3/7] 安装ProjectDiscovery工具...${NC}"
    
    export PATH=$PATH:/usr/local/go/bin:$HOME/go/bin
    export GOPATH=$HOME/go
    
    # subfinder - 子域名枚举
    echo -e "  ${BLUE}安装 subfinder...${NC}"
    go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest 2>/dev/null || true
    
    # httpx - HTTP探测
    echo -e "  ${BLUE}安装 httpx...${NC}"
    go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest 2>/dev/null || true
    
    # nuclei - 漏洞扫描
    echo -e "  ${BLUE}安装 nuclei...${NC}"
    go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest 2>/dev/null || true
    
    # naabu - 端口扫描
    echo -e "  ${BLUE}安装 naabu...${NC}"
    go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest 2>/dev/null || true
    
    # 更新nuclei模板
    echo -e "  ${BLUE}更新 nuclei 模板...${NC}"
    $HOME/go/bin/nuclei -update-templates 2>/dev/null || true
}

# 安装系统包安全工具
install_security_tools() {
    echo -e "${YELLOW}[4/7] 安装系统包安全工具...${NC}"
    
    if [ "$OS" == "centos" ]; then
        yum install -y nikto hydra sslscan
    else
        apt install -y nikto hydra whatweb wafw00f gobuster sslscan sqlmap testssl.sh enum4linux ssh-audit
    fi
    
    # 安装 ffuf (Go)
    echo -e "  ${BLUE}安装 ffuf...${NC}"
    go install github.com/ffuf/ffuf/v2@latest 2>/dev/null || true
    
    # 安装 gobuster (Go)
    echo -e "  ${BLUE}安装 gobuster...${NC}"
    go install github.com/OJ/gobuster/v3@latest 2>/dev/null || true
}

# 安装Python安全工具
install_python_tools() {
    echo -e "${YELLOW}[5/7] 安装Python安全工具...${NC}"
    
    # 确保 pip 是最新版
    python3 -m pip install --upgrade pip 2>/dev/null || true
    
    # sqlmap - SQL注入
    echo -e "  ${BLUE}安装 sqlmap...${NC}"
    pip3 install sqlmap 2>/dev/null || true
    
    # theHarvester - 信息收集
    echo -e "  ${BLUE}安装 theHarvester...${NC}"
    pip3 install theHarvester 2>/dev/null || true
    
    # wafw00f - WAF检测
    echo -e "  ${BLUE}安装 wafw00f...${NC}"
    pip3 install wafw00f 2>/dev/null || true
    
    # whatweb (如果系统包没安装)
    if ! command -v whatweb &> /dev/null; then
        echo -e "  ${BLUE}安装 whatweb (Ruby)...${NC}"
        if [ "$OS" == "centos" ]; then
            yum install -y ruby rubygems
        else
            apt install -y ruby
        fi
        gem install whatweb 2>/dev/null || true
    fi
    
    # XSStrike - XSS扫描
    echo -e "  ${BLUE}安装 XSStrike...${NC}"
    if [ ! -d "/opt/XSStrike" ]; then
        git clone https://github.com/s0md3v/XSStrike.git /opt/XSStrike 2>/dev/null || true
        pip3 install -r /opt/XSStrike/requirements.txt 2>/dev/null || true
        ln -sf /opt/XSStrike/xsstrike.py /usr/local/bin/xsstrike 2>/dev/null || true
    fi
    
    # ssh-audit (如果系统包没安装)
    if ! command -v ssh-audit &> /dev/null; then
        echo -e "  ${BLUE}安装 ssh-audit...${NC}"
        pip3 install ssh-audit 2>/dev/null || true
    fi
    
    # crackmapexec
    echo -e "  ${BLUE}安装 crackmapexec...${NC}"
    pip3 install crackmapexec 2>/dev/null || true
}

# 安装可选工具 (Metasploit, 云工具等)
install_optional_tools() {
    echo -e "${YELLOW}[6/7] 安装可选工具...${NC}"
    
    # searchsploit (exploit-db)
    if ! command -v searchsploit &> /dev/null; then
        echo -e "  ${BLUE}安装 searchsploit...${NC}"
        git clone https://github.com/offensive-security/exploitdb.git /opt/exploitdb 2>/dev/null || true
        ln -sf /opt/exploitdb/searchsploit /usr/local/bin/searchsploit 2>/dev/null || true
    fi
    
    # testssl.sh (如果系统包没安装)
    if ! command -v testssl &> /dev/null && ! command -v testssl.sh &> /dev/null; then
        echo -e "  ${BLUE}安装 testssl.sh...${NC}"
        git clone https://github.com/drwetter/testssl.sh.git /opt/testssl.sh 2>/dev/null || true
        ln -sf /opt/testssl.sh/testssl.sh /usr/local/bin/testssl 2>/dev/null || true
    fi
    
    # enum4linux-ng
    if ! command -v enum4linux &> /dev/null && ! command -v enum4linux-ng &> /dev/null; then
        echo -e "  ${BLUE}安装 enum4linux-ng...${NC}"
        pip3 install enum4linux-ng 2>/dev/null || true
    fi
    
    # AWS CLI (可选)
    if ! command -v aws &> /dev/null; then
        echo -e "  ${BLUE}安装 AWS CLI...${NC}"
        pip3 install awscli 2>/dev/null || true
    fi
    
    # kube-hunter (可选)
    echo -e "  ${BLUE}安装 kube-hunter...${NC}"
    pip3 install kube-hunter 2>/dev/null || true
    
    echo -e "  ${YELLOW}注意: Metasploit 需要单独安装，请参考官方文档${NC}"
    echo -e "  ${YELLOW}       Azure CLI 需要单独安装: curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash${NC}"
}

# 创建符号链接
create_symlinks() {
    echo -e "${YELLOW}[7/7] 创建符号链接...${NC}"
    
    # 将Go工具链接到/usr/local/bin
    for tool in subfinder httpx nuclei naabu ffuf gobuster; do
        if [ -f "$HOME/go/bin/$tool" ]; then
            ln -sf "$HOME/go/bin/$tool" /usr/local/bin/$tool
            echo -e "  ${GREEN}✓${NC} 已链接: $tool"
        fi
    done
}

# 验证安装
verify_installation() {
    echo ""
    echo -e "${GREEN}============================================${NC}"
    echo -e "${GREEN}  安装验证${NC}"
    echo -e "${GREEN}============================================${NC}"
    
    # 分类检查
    echo -e "\n${BLUE}[基础工具]${NC}"
    for tool in nmap whois dig curl wget; do
        check_tool $tool
    done
    
    echo -e "\n${BLUE}[信息收集]${NC}"
    for tool in subfinder httpx whatweb wafw00f theHarvester; do
        check_tool $tool
    done
    
    echo -e "\n${BLUE}[漏洞扫描]${NC}"
    for tool in nuclei nikto sslscan testssl searchsploit; do
        check_tool $tool
    done
    
    echo -e "\n${BLUE}[Web攻击]${NC}"
    for tool in sqlmap gobuster ffuf xsstrike; do
        check_tool $tool
    done
    
    echo -e "\n${BLUE}[网络攻击]${NC}"
    for tool in hydra crackmapexec enum4linux ssh-audit snmpwalk ldapsearch; do
        check_tool $tool
    done
    
    echo -e "\n${BLUE}[云安全]${NC}"
    for tool in aws az kube-hunter; do
        check_tool $tool
    done
    
    echo -e "\n${BLUE}[漏洞利用]${NC}"
    for tool in msfconsole msfvenom; do
        check_tool $tool
    done
}

# 检查单个工具
check_tool() {
    local tool=$1
    if command -v $tool &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} $tool"
    else
        echo -e "  ${RED}✗${NC} $tool (未安装)"
    fi
}

# 主流程
main() {
    detect_os
    install_base
    install_go
    install_pd_tools
    install_security_tools
    install_python_tools
    install_optional_tools
    create_symlinks
    verify_installation
    
    echo ""
    echo -e "${GREEN}============================================${NC}"
    echo -e "${GREEN}  安装完成!${NC}"
    echo -e "${GREEN}============================================${NC}"
    echo ""
    echo -e "${YELLOW}请运行 'source /etc/profile' 或重新登录使环境变量生效${NC}"
    echo ""
    echo -e "如需安装 Metasploit:"
    echo -e "  curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall"
    echo -e "  chmod 755 msfinstall && ./msfinstall"
    echo ""
}

main
