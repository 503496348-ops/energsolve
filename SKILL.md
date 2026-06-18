---
name: energsolve
version: 1.0.0
description: 元气方程（Energsolve）— Agent竞品分析系统。AI驱动网页爬取+结构化数据提取+竞品情报聚合
author: AtomCollide-智械工坊团队
license: Apache-2.0
---

# Energsolve — 元气方程 Agent竞品分析系统

Energsolve（元气方程）是一个AI驱动的竞品分析系统，融合了三大开源爬取/提取引擎的核心能力：

## 核心能力

### 1. 智能网页爬取（基于 Crawl4AI）
- LLM友好的Markdown输出，支持标题、表格、代码、引用
- 异步浏览器池、缓存、最小跳转
- 会话管理、代理、Cookie、用户脚本、钩子
- 自适应智能：学习站点模式，只探索关键内容
- 零密钥部署，CLI和Docker支持

### 2. 图驱动结构化提取（基于 ScrapeGraphAI）
- LLM + 有向图逻辑构建爬取流水线
- SmartScraperGraph：单页结构化数据提取
- 支持本地文件（XML, HTML, JSON, Markdown）
- 多LLM后端支持（OpenAI, Ollama, Gemini等）

### 3. URL到Markdown转换（基于 Jina Reader）
- `r.jina.ai` — 任意URL转LLM友好输入
- `s.jina.ai` — 网页搜索+内容提取
- 支持PDF、Office文档、图片描述
- 无头Chrome渲染 + curl-impersonate轻量模式

## 使用场景

- **竞品监控**：定期爬取竞品网站，提取产品更新、定价变化
- **市场情报**：聚合多源数据，生成结构化竞品报告
- **Agent数据管线**：为RAG和Agent系统提供高质量网页内容
- **产品对比**：自动化产品特性矩阵生成

## 安装

```bash
pip install -U crawl4ai
playwright install
```

## 快速示例

```python
import asyncio
from crawl4ai import AsyncWebCrawler

async def analyze_competitor(url):
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
        print(result.markdown)  # LLM-ready output

asyncio.run(analyze_competitor("https://example.com"))
```

## License

Apache-2.0

## 作者

AtomCollide-智械工坊团队
