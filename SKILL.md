---
name: energsolve
version: 1.0.0
description: "AI驱动竞品分析系统。智能网页爬取+结构化数据提取+竞品情报聚合。当需要爬取竞品网站、分析市场情报、提取产品数据时使用。"
author: AtomCollide-智械工坊团队
license: Apache-2.0
triggers:
  - 竞品分析
  - 网页爬取
  - 竞品监控
  - competitor analysis
  - web scraping
  - 元气方程
  - energsolve
  - 公司速读
  - 三角验证
  - 研究memo
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

### 2. 图驱动结构化提取
- LLM + 有向图逻辑构建爬取流水线
- SmartScraperGraph：单页结构化数据提取
- 支持本地文件（XML, HTML, JSON, Markdown）
- 多LLM后端支持（OpenAI, Ollama, Gemini等）

### 3. URL到Markdown转换
- URL-to-Markdown转换 — 任意URL转LLM友好输入
- 网页搜索+内容提取
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

## 工作流

使用此技能时，按以下步骤执行：
- [ ] 1. 确认用户需求和使用场景
- [ ] 2. 加载相关代码和配置
- [ ] 3. 执行核心功能
- [ ] 4. 验证输出结果
- [ ] 5. 反馈给用户

## 公司研究双层 Memo（v1.1.0）

新增 `energsolve_intel/company_research.py`，用于把竞品/公司调研从“资料汇总”升级为“可审计结论”：

- **速读区只放双信源确认事实**：融资、创始人、客户、估值、关键业务数字等事实必须至少两个独立来源才进入 read-first 层。
- **深读区保留审计轨迹**：单一来源、自报数据、冲突事实、未披露字段全部进入 audit_trail，不污染核心结论。
- **验证矩阵标准化**：每条事实输出 category / claim / status / independent_sources / conflicts，便于飞书文档、看板和后续刷新复用。
- **用户视角锚定**：`build_company_memo(company, facts, lens)` 支持潜在合作、投资标的、竞品对比等不同研究视角。

### 快速调用

```python
from energsolve_intel.company_research import CompanyFact, build_company_memo

memo = build_company_memo("目标公司", [
    CompanyFact("融资", "B轮5000万美元", sources=("https://source-a", "https://source-b")),
    CompanyFact("客户", "服务300家客户", sources=("https://company-site"), reported_by_company=True),
], lens="竞品对比")
print(memo.thirty_second_card())
```

## 2026-07-03 产品收敛门禁

- 新增 `scripts/product_convergence_gate.py`：从远端干净 clone 后可运行 `python3 scripts/product_convergence_gate.py --json`，检查 SKILL/README、入口文件、smoke 目标、测试与外部融合引用是否自洽。
- 新增 `tests/test_product_convergence_gate.py`：确保门禁在产品仓库中真实可执行，避免后续增强只停留在孤岛模块。
