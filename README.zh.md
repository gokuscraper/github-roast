<p align="center">
  <img src="xpose-logo.jpg" width="60" alt="X-POSE logo">
</p>

<h1 align="center">X照妖镜</h1>

<p align="center">
  <em>AI 驱动的 Twitter 人格分析器 — 毒舌、可分享、适合截图转发</em>
</p>

<p align="center">
  <a href="./README.md">English</a>
</p>

---

## 概述

X照妖镜是一个单人 Twitter 人格分析工具。输入用户名 → 抓取资料和最新推文 → DeepSeek V4 Pro 生成 15 维人格分析报告，包含吐槽、长处、弱点、爱情观等卡片。

灵感来自 [Wordware](https://wordware.ai) 那个刷屏的 Twitter 人格项目。

## 功能

- **抓取** — 通过 Playwright/CloakBrowser 抓取用户资料 + 最新推文
- **分析** — 将资料 + 推文发送给 DeepSeek V4 Pro，返回结构化 JSON
- **15 张报告卡片** — 介绍、吐槽、长处、弱点、爱情、金钱、健康等 15 个维度
- **下载为图片** — 一键截图保存为 PNG（基于 html2canvas）
- **分享到 X** — 预填好推文文案的一键分享
- **中英文切换** — 简体中文 / English 实时切换
- **并发限流** — 防止 Streamlit Cloud 单容器过载

## 快速开始

### 在线体验

👉 **[xpose7.streamlit.app](https://xpose7.streamlit.app)**

### 本地运行

```bash
# 1. 克隆仓库
git clone https://github.com/gokuscraper/x-pose.git
cd x-pose

# 2. 安装 Python 依赖
pip install -r requirements.txt

# 3. 安装 Playwright 浏览器（CloakBrowser 需要）
playwright install chromium

# 4. 配置 API 密钥
# 创建 .streamlit/secrets.toml，内容：
# SILICON_API_KEY = "sk-your-key-here"

# 5. 启动
streamlit run streamlit_app.py
```

### API 密钥

X照妖镜使用 [SiliconFlow](https://siliconflow.cn) 的 DeepSeek V4 Pro。到 [SiliconFlow 控制台](https://cloud.siliconflow.cn) 获取 API Key。

## 项目结构

```
x-pose/
├── streamlit_app.py        # 首页 — 输入用户名 → 抓取
├── pages/
│   └── 1_Analysis.py       # 分析报告页
├── lib/
│   ├── ai.py               # AI 提示词 & API 调用
│   ├── tweet_utils.py      # 推文格式化 & 统计
│   └── sidebar.py          # 侧边栏导航
├── scraper/
│   ├── worker.py           # 子进程入口（避免事件循环冲突）
│   ├── subprocess_client.py# 子进程通信层
│   ├── client.py           # CloakBrowser 封装
│   ├── fetcher.py          # 抓取用户 + 推文
│   ├── parser.py           # 解析原始 API 数据 → 模型
│   ├── models.py           # TwitterUser, Tweet 数据类
│   ├── storage.py          # 本地 JSON 缓存
│   └── config.py           # API 端点配置
├── locales/
│   ├── zh.json             # 中文界面文案
│   └── en.json             # 英文界面文案
├── i18n.py                 # 国际化辅助
├── requirements.txt
└── packages.txt            # Streamlit Cloud 系统依赖
```

## 工作原理

```mermaid
flowchart LR
    A[用户输入] --> B[Playwright 子进程]
    B --> C[资料 JSON + 推文]
    C --> D[DeepSeek V4 Pro]
    D --> E[15 字段 JSON 报告]
    E --> F[卡片网格 UI]
    F --> G[下载 PNG / 分享到 X]
```

1. **输入** — 用户名（支持 `@user`、`https://x.com/user`、裸用户名）
2. **抓取** — 子进程通过 CloakBrowser 运行 Playwright，绕过 Vercel 验证
3. **分析** — 资料 + 推文发送给 DeepSeek V4 Pro，搭配毒舌提示词
4. **报告** — 15 张卡片在自适应网格中渲染
5. **分享** — 下载为 PNG 或一键分享到 X

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | [Streamlit](https://streamlit.io)（单页应用） |
| AI 模型 | [DeepSeek V4 Pro](https://platform.deepseek.ai) 通过 SiliconFlow API |
| 爬虫 | [CloakBrowser](https://cloakbrowser.com)（基于 Playwright） |
| 部署 | [Streamlit Cloud](https://streamlit.io/cloud) |
| 协议 | Apache 2.0 |

## 许可证

[Apache 2.0](LICENSE)
