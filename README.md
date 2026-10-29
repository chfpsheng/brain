# BRAIN 量化研究工程

WorldQuant BRAIN 平台学习与实践工程。用于管理 alpha 表达式、学习笔记、数据探索与回测分析。

## 环境准备

```bash
pip install requests
```

## 凭据配置（重要）

用户名/密码**不写在代码里**，而是放在运行目录下的凭据文件中，且该文件已被 `.gitignore` 忽略，不会上传到 GitHub。

1. 在仓库根目录创建 `brain_credentials_copy.txt`
2. 内容为 JSON 数组，第一项是邮箱（用户名），第二项是密码：

```json
["你的邮箱", "你的密码"]
```

`day1.py` 与 `day1_batch.py` 会读取此文件进行 `HTTP Basic Auth` 认证。

> 注意：本文件含敏感信息，请勿提交、勿分享。

## 运行方式

```bash
# 单 alpha 认证 + 回测（见 day1.py）
python day1.py

# 批量回测，结束后拉取并打印各 alpha 指标（见 day1_batch.py）
python day1_batch.py
```

## 目录结构
- `alphas/` —— alpha 表达式与回测记录（按思路分文件，如 `momentum.txt` / `reversal.txt` / `quality.txt`）
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
