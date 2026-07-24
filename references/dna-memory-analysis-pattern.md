# DNA Memory 分析记忆融合

> 来源: [DNA Memory](https://github.com/AIPMAndy/dna-memory) — 决策记忆与验证结晶
> 融合目标: 竞品分析历史决策、验证结晶、开放事项追踪

## 竞品分析记忆分型

| 类型 | 分析应用 |
|------|---------|
| decision | 分析策略选择（选哪些竞品、用什么维度） |
| fact | 竞品已验证事实（功能/定价/市场份额） |
| insight | 竞品规律（某类竞品普遍在X方面弱） |
| project_state | 分析进度（已完成/进行中/待启动） |
| open_loop | 待验证假设 |
| workflow | 有效分析流程 |
| error_lesson | 分析失败经验（数据源不可靠等） |

## 验证结晶流程

```
假设 → 数据采集 → 交叉验证
  → 验证通过: 结晶为fact（confidence=high）
  → 验证失败: 记录为error_lesson
  → 部分验证: 记录为insight（confidence=medium）
```

## 开放事项管理

open_loop类型追踪：
- 待验证假设
- 待采集数据
- 待深入分析的方向
- 定期检查是否已闭环
