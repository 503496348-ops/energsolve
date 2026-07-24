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

## J-Space 增强（实证/假设验证）

基于 J-Space Cognition Suite v3.2 的实证协议增强竞品分析：
- 溺水检测器（7种信号→触发实证转向）
- 命名未知→参数化→独立参考→区分测试
- 证据回写（匹配/不匹配/不确定→行动）
- 最小复现（一个变量改变的最小测试）

详见 `references/j-space-empirics.md`
