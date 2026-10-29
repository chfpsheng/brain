# BRAIN 量化研究工程

WorldQuant BRAIN 平台学习与实践工程。用于管理 alpha 表达式、学习笔记、数据探索与回测分析。

## 目录结构
- `alphas/` —— alpha 表达式与回测记录（按思路分文件，如 leverage.py / momentum.py）
- `notes/` —— 零基础学量化课程笔记（各课知识点、作业）
- `data/` —— 数据探索脚本、字段清单、覆盖率分析
- `tools/` —— 临时验证 / 分析脚本（用完即清）

## 研究闭环
开发表达式 → Simulation 回测 → 分析指标(Sharpe/IC/Turnover/Fitness) → 提交(IS/OS/TEST) → 迭代

## 提交自查清单
- [ ] IS Sharpe 过阈值（region 不同门槛不同）
- [ ] OS 与 IS 一致（无过拟合）
- [ ] Turnover 合理（1%~70%）
- [ ] 与已有 alpha 低相关（<0.7，或 Sharpe 好 ≥10%）
- [ ] 中性化 / 无前视偏差 / 覆盖广
