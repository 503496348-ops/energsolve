# 🚀⚡ Energsolve 元气方程 — Agent竞品分析系统

<div align="center">

**AI驱动网页爬取 + 结构化数据提取 + 竞品情报聚合**

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

</div>

---

## 🇨🇳 中文介绍

**Energsolve（元气方程）** 是一个融合三大开源爬取引擎能力的Agent竞品分析系统，由 **AtomCollide-智械工坊** 团队打造。

### 核心能力

| 模块 | 来源 | 能力 |
|------|------|------|
| 🕷️ 智能爬取 | Crawl4AI | LLM友好Markdown输出、异步浏览器池、自适应爬取 |
| 🧠 图驱动提取 | Energsolve | LLM+有向图流水线、结构化数据抽取 |
| 📖 URL转文本 | Energsolve | 任意URL→Markdown、搜索聚合、PDF/Office支持 |

### 使用场景

- **竞品监控**：定期爬取竞品网站，提取产品更新与定价变化
- **市场情报**：多源数据聚合，生成结构化竞品报告
- **Agent数据管线**：为RAG和Agent系统提供高质量网页内容
- **产品对比**：自动化产品特性矩阵生成

### 安装

```bash
pip install -U energsolve
playwright install
```

### 快速示例

```python
import asyncio
from crawl4ai import AsyncWebCrawler, SimpleReader, SmartExtractionPipeline

# 1. 基础爬取
async def analyze_competitor(url):
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
        # 获取LLM友好的Markdown内容
        print(result.markdown)

# 2. 一键阅读器（Jina Reader风格）
async def quick_read(url):
    reader = SimpleReader()
    result = await reader.read(url)
    print(result.markdown)

# 3. 智能图提取（Scrapegraph-ai风格）
async def smart_extract(url):
    pipeline = SmartExtractionPipeline(provider="openai/gpt-4o")
    result = await pipeline.run(
        prompt="提取产品名称、价格和描述",
        url=url,
    )
    print(result.data)

asyncio.run(analyze_competitor("https://competitor.com"))
```

---

## 🇺🇸 English Introduction

**Energsolve (元气方程)** is an AI-powered competitive analysis system that fuses capabilities from three best-in-class open-source crawling engines, built by the **AtomCollide-智械工坊** team.

### Core Capabilities

| Module | Origin | Capability |
|--------|--------|------------|
| 🕷️ Smart Crawling | Crawl4AI | LLM-friendly Markdown, async browser pool, adaptive crawling |
| 🧠 Graph-driven Extraction | Energsolve | LLM + directed graph pipelines, structured data extraction |
| 📖 URL-to-Text | Energsolve | Any URL → Markdown, search aggregation, PDF/Office support |

### Use Cases

- **Competitor Monitoring**: Periodically scrape competitor sites for product updates and pricing changes
- **Market Intelligence**: Aggregate multi-source data into structured competitive reports
- **Agent Data Pipelines**: Feed high-quality web content to RAG and Agent systems
- **Product Comparison**: Automated product feature matrix generation

### Installation

```bash
pip install -U energsolve
playwright install
```

### Quick Example

```python
import asyncio
from crawl4ai import AsyncWebCrawler, SimpleReader, SmartExtractionPipeline

# 1. Basic crawling
async def analyze_competitor(url):
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
        print(result.markdown)  # LLM-ready output

# 2. Simple Reader API (one-call URL-to-Markdown, like Jina Reader)
async def quick_read(url):
    reader = SimpleReader()
    result = await reader.read(url)
    print(result.markdown)

# 3. Smart Pipeline (LLM-planned graph extraction, like Scrapegraph-ai)
async def smart_extract(url):
    pipeline = SmartExtractionPipeline(provider="openai/gpt-4o")
    result = await pipeline.run(
        prompt="Extract product name, price, and description",
        url=url,
    )
    print(result.data)

asyncio.run(analyze_competitor("https://competitor.com"))
```

---

## Architecture

```
Energsolve
├── crawl4ai/          # Core crawling engine (async, browser-based)
├── docs/              # Documentation
├── examples/          # Usage examples
└── SKILL.md           # Agent skill definition
```

### Integrated Patterns

**Graph-driven Extraction:**
- Graph-based scraping pipelines with LLM reasoning
- `SmartScraperGraph` pattern for single-page extraction
- Multi-LLM backend support (OpenAI, Ollama, Gemini, etc.)

**URL-to-Markdown Conversion:**
- URL-to-Markdown conversion patterns
- Search-to-content aggregation
- PDF/Office document parsing (PDF.js + LibreOffice)
- Headless Chrome + curl-impersonate dual-mode rendering

## License

Apache-2.0

## Author

**AtomCollide-智械工坊团队**

Copyright 2026 AtomCollide-智械工坊

---

## 🚀 加入AtomCollide-AI智能体实验室

**元素碰撞-AtomCollide-AI 智能体实验室** 是一个专注于AI领域的开源组织，汇聚了众多优秀学习者。

### 核心价值

**找工作：更省力，也更精准**
- 一线大厂内推通道（字节、阿里、腾讯等）
- 全链路求职赋能包（面试题库、简历优化、晋升指导）
- 线下技术沙龙 & 人脉网络

**学AI测试：真正落地，拒绝空谈**
- 从0到1实战落地体系（Skills、MCP、RAG、AI IDE等）
- 独家自研资料与工具矩阵
- 前沿技术同步与提效方案

### 加入社群

- [知识库入口](https://vcnvmnln7wit.feishu.cn/wiki/WpK2wAcV8i6P8tke8X9cLcmDnSh)
- [AI探索交流群](https://applink.feishu.cn/client/chat/chatter/add_by_link?link_token=074vd565-6084-455c-ac52-9703e89a0697)

---

*AtomCollide-智械工坊团队出品*

