# 🔥 SKILLHack 在线自动GetShell （可批量和单站进行自动渗透）

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Web-FF6B6B?style=for-the-badge" alt="Web Platform"/>
  <img src="https://img.shields.io/badge/FOFA-Integration-00ADD8?style=for-the-badge" alt="FOFA"/>
  <img src="https://img.shields.io/badge/AI-Powered-3776AB?style=for-the-badge" alt="AI Powered"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License"/>
</p>

<p align="center">
  <b>🎯 一站式资产测绘与漏洞风险洞察平台 | FOFA + AI + 智能扫描</b>
</p>

<p align="center">
  <b>🌐 官网：<a href="https://hackbyte.io">hackbyte.io</a> | 🚀 演示站：<a href="https://scan.hackbyte.io">scan.hackbyte.io</a></b>
</p>

---

## 📖 项目简介

**XHSecTeam 资产安全测绘平台**是由 [黑客字节社区（HackByte）](https://hackbyte.io) 开发的一款集成化安全测试平台。平台将互联网资产搜索、漏洞扫描、DDoS 流量观测与 AI 安全助手融合在同一套界面中，帮助安全研究人员快速摸清攻击面、定位高危资产，并持续监控风险变化。

### 🎯 核心价值

- ✅ **资产测绘引擎** - 基于 FOFA 语法的强大资产发现能力
- ✅ **智能漏洞扫描** - 集成多种漏洞检测引擎，覆盖常见 CVE
- ✅ **AI 协同分析** - 自然语言转换为 FOFA 查询语句
- ✅ **可视化仪表盘** - 直观展示漏洞分布与风险趋势
- ✅ **攻防知识库** - 沉淀实战经验与测绘语法

---

## ✨ 功能特性

### 🔍 资产测绘中心
- **FOFA 语法支持** - title、ip、domain、port、body、server 等 15+ 字段
- **组合搜索** - 支持 `&&` / `||` 逻辑组合，构建精准查询语句
- **AI 智能助手** - 自然语言转换为 FOFA 查询，降低学习成本
- **批量导出** - 一键导出搜索结果，支持多种格式

### 🛡️ 单站渗透扫描
- **指纹识别** - 自动识别 Web 技术栈、框架、中间件
- **POC 验证** - 针对性漏洞检测与验证
- **可视化仪表盘** - 漏洞分布、风险等级、修复建议
- **扫描日志** - 完整记录扫描过程与结果

### 📊 DDoS 防护分析
- **流量监控** - 带宽峰值、异常请求比例、告警事件
- **压测配置** - 模拟不同攻击类型，评估防护能力
- **可视化图表** - 直观展示流量趋势与异常事件

### 🤖 AI 安全助手
- **智能对话** - 自然语言描述需求，AI 自动生成查询语句
- **语法推荐** - 根据场景推荐最佳 FOFA 语法组合
- **历史记录** - 保存搜索历史，快速复用

### 📚 安全知识库
- **FOFA 语法进阶** - 从基础到组合检索的完整教程
- **暴露面收缩** - 基于测绘结果的攻面梳理方法
- **实战案例** - 真实攻防场景下的资产测绘实践

---

## 🎨 界面预览

### 首页 - 资产安全总览
- 优雅的现代化设计
- 核心能力模块展示
- 安全知识库快速入口

### 资产测绘 - FOFA 搜索
- 实时搜索结果展示
- AI 助手侧边栏
- 快捷语法输入

### 单站扫描 - 漏洞仪表盘
- 高危/中危/低危漏洞分级
- 漏洞趋势图表
- 详细扫描日志

### DDoS 分析 - 流量监控
- 实时流量曲线
- 异常事件告警
- 防护建议推荐

---

## 🚀 快速开始

### 在线体验

访问我们的演示站点：**[scan.hackbyte.io](https://scan.hackbyte.io)**

> 💡 **提示**：后端服务已开发完成并稳定运行。如需完整功能体验，请前往 [黑客字节社区（hackbyte.io）](https://hackbyte.io) 申请测试权限。

### 本地部署

#### 1. 克隆项目
```bash
git clone https://github.com/HackByteSec/XHSecTeam-Platform.git
cd XHSecTeam-Platform
```

#### 2. 配置 FOFA API
编辑 `fofa-api.js` 文件，填入你的 FOFA 凭证：
```javascript
const _c = {
    a: 'YOUR_FOFA_EMAIL_BASE64_REVERSE',  // FOFA 邮箱（Base64 反转编码）
    b: 'YOUR_FOFA_KEY_BASE64_REVERSE',    // FOFA API Key（Base64 反转编码）
    c: 'xY3LpBXYv8mZulmLhZ2bm9yL6MHc0RHa'  // FOFA Base URL
};
```

> 📌 **编码方法**：将你的 FOFA Email 和 API Key 先进行 Base64 编码，然后反转字符串。

#### 3. 启动服务
```bash
# 如果有后端服务
cd api
python server.py

# 或直接打开 HTML 文件（前端演示）
# 在浏览器中打开 index.html
```

#### 4. 访问平台
打开浏览器，访问：
- 首页：`http://localhost/index.html`
- 资产测绘：`http://localhost/aisearch/`
- 单站扫描：`http://localhost/aibug/single.html`

---

## 📁 项目结构

```
XHSecTeam-Platform/
├── index.html                  # 首页
├── fofa-api.js                 # FOFA API 封装
│
├── aisearch/                   # 资产测绘模块
│   └── index.html
│
├── aibug/                      # 漏洞扫描模块
│   ├── single.html             # 单站扫描仪表盘
│   ├── ai-assistant.html       # AI 助手
│   ├── vuln-analysis.html      # 漏洞分析报告
│   ├── ddos-test.html          # DDoS 压力测试
│   ├── logs.html               # 扫描日志
│   ├── poc-library.html        # POC 漏洞库
│   ├── shell-manager.html      # WebShell 管理
│   └── getshell.html           # GetShell 工具
│
├── knowledge/                  # 安全知识库
│   ├── index.html
│   └── articles/               # 知识文章
│
├── static/                     # 静态资源
│   ├── css/
│   │   ├── common.css
│   │   ├── aisearch.css
│   │   └── knowledge.css
│   ├── js/
│   │   ├── layout.js
│   │   └── aisearch.js
│   └── components/             # 公共组件
│
├── api/                        # 后端 API（已完成）
│   └── server.py
│
└── mcp/                        # MCP 红队工具集成
    ├── main.py
    ├── auto_recon.py           # 自动侦察引擎
    ├── mcp_tools.py            # 60+ 工具集成
    └── ...
```

---

## 🔒 后端服务说明

### ✅ 后端已开发完成

我们的后端服务已经完成开发并部署在生产环境，包括：

1. **资产测绘 API** - FOFA 查询、结果解析、数据缓存
2. **漏洞扫描引擎** - 集成 Nuclei、Nikto、自定义 POC
3. **AI 智能分析** - 自然语言处理、查询优化、结果分析
4. **数据存储服务** - 扫描历史、漏洞库、用户管理
5. **实时监控服务** - DDoS 流量监控、告警推送

### 🎯 体验完整功能

由于我们掌握了**大量未公开的 0day 漏洞和 POC**，为防止滥用，完整后端功能需要申请权限：

1. 访问 [黑客字节社区（hackbyte.io）](https://hackbyte.io)
2. 注册账号并完成身份验证
3. 在社区申请测试权限
4. 审核通过后，获得完整 API 访问权限

### 🔐 我们的优势

- ✅ **独家 0day 漏洞库** - 持续更新的未公开漏洞
- ✅ **定制化 POC** - 针对主流框架与中间件
- ✅ **实战验证** - 所有 POC 均经过真实环境测试
- ✅ **快速响应** - 新漏洞 24 小时内集成

> ⚠️ **安全提示**：我们的漏洞库仅供授权测试使用，请遵守相关法律法规。

---

## 🛠️ 技术栈

### 前端
- **框架** - 纯原生 JavaScript（无依赖，轻量高效）
- **样式** - 现代化 CSS3，响应式设计
- **可视化** - Chart.js / ECharts（图表展示）
- **交互** - 原生 Fetch API（FOFA API 调用）

### 后端
- **语言** - Python 3.10+
- **框架** - Flask / FastAPI
- **数据库** - SQLite / PostgreSQL
- **缓存** - Redis
- **AI 集成** - OpenAI API / Claude API

### 安全工具集成
- **资产测绘** - FOFA API
- **漏洞扫描** - Nuclei、Nikto、SQLMap、XSStrike
- **端口扫描** - Nmap、Masscan
- **子域名枚举** - Subfinder、OneForAll
- **指纹识别** - WhatWeb、Wappalyzer
- **POC 验证** - 自研框架 + 开源工具

---

## 🎓 使用教程

### FOFA 语法快速入门

#### 基础查询
```
title="后台"               # 搜索标题包含"后台"
ip="1.1.1.1"              # 搜索指定 IP
domain="gov.cn"           # 搜索指定域名
port="3306"               # 搜索指定端口
body="password"           # 搜索页面内容
server="nginx"            # 搜索服务器类型
```

#### 组合查询
```
title="后台" && port="443"                    # 标题包含"后台"且端口为 443
domain="edu.cn" && title="登录"              # 教育网站的登录页面
server="Apache" && country="CN"             # 中国的 Apache 服务器
port="80" && body="jQuery" && city="北京"   # 北京使用 jQuery 的网站
```

#### 高级技巧
```
cert="example.com"                          # 证书包含特定域名
icon_hash="123456"                          # favicon 特征搜索
protocol="https"                            # 仅搜索 HTTPS 站点
is_domain=true                              # 仅显示主域名
```

### AI 助手使用示例

直接在 AI 助手中输入自然语言：
```
"找出所有使用 Apache 的中国政府网站"
"搜索开放 3306 端口的 MySQL 服务器"
"查询标题包含'管理后台'且使用 Tomcat 的站点"
```

AI 会自动生成对应的 FOFA 语法并执行搜索。

---

## 📊 扫描能力矩阵

| 漏洞类型 | 支持程度 | 检测方式 |
|---------|---------|---------|
| SQL 注入 | ⭐⭐⭐⭐⭐ | SQLMap + 自定义 POC |
| XSS 跨站 | ⭐⭐⭐⭐⭐ | XSStrike + 模糊测试 |
| 文件上传 | ⭐⭐⭐⭐⭐ | 字典爆破 + 绕过技巧 |
| RCE 命令执行 | ⭐⭐⭐⭐⭐ | 框架漏洞 + 中间件漏洞 |
| SSRF | ⭐⭐⭐⭐ | 协议探测 + Bypass |
| XXE | ⭐⭐⭐⭐ | XML 注入检测 |
| 反序列化 | ⭐⭐⭐⭐⭐ | Shiro/Fastjson/Log4j |
| 弱口令 | ⭐⭐⭐⭐⭐ | 常见口令字典 |
| 敏感信息泄露 | ⭐⭐⭐⭐ | 目录扫描 + 指纹识别 |
| 权限绕过 | ⭐⭐⭐⭐ | 认证测试 + 越权检测 |

---

## ⚠️ 安全声明

### 法律责任

1. 本平台**仅供授权的安全测试和研究使用**
2. 在使用前，请确保已获得目标系统所有者的**书面授权**
3. 未经授权对系统进行渗透测试是**违法行为**
4. 开发者不对任何滥用行为承担法律责任
5. 请遵守当地法律法规和道德准则

### 合规使用

- ✅ **合法授权测试** - 获得明确书面授权的安全测试
- ✅ **安全研究学习** - 用于学习和研究网络安全技术
- ✅ **漏洞赏金计划** - 参与官方漏洞赏金项目
- ❌ **未授权攻击** - 禁止对未授权系统进行任何测试
- ❌ **恶意破坏** - 禁止用于破坏、窃取、勒索等违法行为

### 0day 漏洞使用规范

我们承诺：
1. **仅向授权用户开放** - 需通过社区审核
2. **负责任的披露** - 遵循漏洞披露流程
3. **禁止恶意利用** - 发现滥用将立即封禁账号
4. **持续更新维护** - 及时跟进最新安全动态

---

## 🗺️ 开发路线图

### 已完成 ✅
- [x] 前端界面与交互设计
- [x] FOFA API 集成
- [x] AI 智能助手
- [x] 单站漏洞扫描仪表盘
- [x] DDoS 流量分析界面
- [x] 安全知识库
- [x] 后端服务架构
- [x] 60+ 安全工具集成
- [x] 0day 漏洞库构建

### 进行中 🚧
- [ ] Web UI 管理后台
- [ ] 分布式扫描节点
- [ ] 更多 AI 能力集成
- [ ] 移动端适配

### 计划中 📋
- [ ] 云平台集成（AWS/Azure/GCP）
- [ ] 社区共享漏洞库
- [ ] 自动化漏洞利用链
- [ ] 实时威胁情报订阅

---

## 🤝 贡献指南

我们欢迎社区贡献！你可以通过以下方式参与：

1. **提交 Issue** - 报告 Bug 或提出新功能建议
2. **Pull Request** - 提交代码改进或新功能
3. **完善文档** - 改进使用教程和 API 文档
4. **分享案例** - 在社区分享你的使用经验

### 贡献流程
```bash
# 1. Fork 本仓库
# 2. 创建特性分支
git checkout -b feature/your-feature-name

# 3. 提交更改
git commit -m "Add: 你的功能描述"

# 4. 推送到分支
git push origin feature/your-feature-name

# 5. 提交 Pull Request
```

---

## 📮 联系我们

### 官方渠道
- 🌐 **官网**：[hackbyte.io](https://hackbyte.io)
- 🚀 **演示站**：[scan.hackbyte.io](https://scan.hackbyte.io)
- 📧 **邮箱**：support@hackbyte.io
- 💬 **社区**：[黑客字节社区](https://hackbyte.io/community)

### 问题反馈
- 提交 [GitHub Issue](https://github.com/HackByteSec/XHSecTeam-Platform/issues)
- 加入我们的 Discord 频道
- 在社区论坛发帖讨论

### 商务合作
如需商业授权、定制开发或企业培训，请发送邮件至：business@hackbyte.io

---

## 📄 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。

你可以自由地：
- ✅ 商业使用
- ✅ 修改源码
- ✅ 分发代码
- ✅ 私人使用

但请注意：
- ⚠️ 必须保留原作者版权声明
- ⚠️ 不提供任何担保

---

## 🌟 致谢

感谢以下开源项目和服务：
- [FOFA](https://fofa.info) - 互联网资产搜索引擎
- [Nuclei](https://github.com/projectdiscovery/nuclei) - 漏洞扫描引擎
- [Nmap](https://nmap.org) - 网络扫描工具
- [SQLMap](https://sqlmap.org) - SQL 注入检测工具
- [OpenAI](https://openai.com) - AI 能力支持

特别感谢 **黑客字节社区（HackByte）** 的所有成员和贡献者！

---

<p align="center">
  <b>⭐ 如果这个项目对你有帮助，请给我们一个 Star！</b>
</p>

<p align="center">
  <b>🔗 加入 <a href="https://hackbyte.io">黑客字节社区</a>，获取更多安全资源和技术支持！</b>
</p>

<p align="center">
  Made with ❤️ by <a href="https://hackbyte.io">HackByte Security Team</a>
</p>
