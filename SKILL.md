---
name: energsolve
description: "元气方程竞品分析 — 基于 crawl4ai 的竞品爬取、内容分析、报告生成"
license: MIT
metadata:
  author: 503496348-ops
  version: 1.0.0
---

# Energsolve — 元气方程竞品分析

## 触发条件

- "竞品分析"
- "爬取"
- "crawl"
- "竞品报告"
- "energsolve"
- "元气方程"

基于 crawl4ai 的竞品页面爬取 + 内容分析 + 报告生成。

## 核心能力

| 命令 | 说明 |
|------|------|
| `energsolve crawl <url>` | 爬取竞品页面 |
| `energsolve analyze <input>` | 分析竞品内容 |
| `energsolve report` | 生成分析报告 |
| `energsolve info` | 产品信息（含 crawl4ai 状态） |

## 快速开始

```bash
# 查看产品状态
python3 scripts/cli.py info

# 爬取竞品页面
python3 scripts/cli.py crawl https://example.com --depth 2

# 生成报告
python3 scripts/cli.py report --format html -o report.html
```

## 架构

- `crawl4ai/` — 爬虫引擎（异步爬取 + 浏览器管理 + 提取策略）
- `scripts/cli.py` — 统一 CLI 入口

## 测试

```bash
python3 -m pytest tests/ -q
```
