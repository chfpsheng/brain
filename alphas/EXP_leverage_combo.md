# EXP · 杠杆因子组合探索（liabilities/assets 去克隆）

> 目标 universe: USA / TOP3000 / Delay=1 / Decay=4 / Truncation=0.08 / Subindustry 中性化 / Pasteurization On
> 已提交 alpha: 裸 `liabilities/assets`（自相关检查的对比基准）

## 背景
纯 `liabilities/assets`（资产负债率）信号强（IS Sharpe ≈1.54），但已被自己提交过，
新提交会被判自相关 = 1.0（完全克隆）而 FAIL。需在不崩 Sharpe 的前提下把自相关压到 <0.7，
或走 10% Sharpe 豁免线。

## 变体实验记录

| # | 表达式 | Sharpe | Fitness | Sub-univ | Self-Corr | 结果 |
|---|---|---|---|---|---|---|
| 0 | `liabilities/assets` | 1.54 | 1.73 | ok | **1.00** | 7 PASS / 1 FAIL（克隆） |
| 1 | `rank(liabilities/assets) - rank(cashflow/assets)` | ~1.5 | ok | ok | 0.8073 | 7 PASS / 1 FAIL |
| 2 | `rank(liabilities/assets) - 2*rank(cashflow/assets)` | 1.22 | 0.90 | 0.48 | (PENDING) | 4 PASS / 3 FAIL（cashflow 加码崩） |
| 3 | `rank(ts_delta(liabilities/assets,252)) - rank(cashflow/assets)` | 0.94 | 0.55 | — | (PENDING) | 5 PASS / 2 FAIL（变化量太弱） |
| 4 | 同上但 Neutralization=Market | 0.80 | 0.73 | — | (PENDING) | 5 PASS / 2 FAIL（行业间杠杆差有毒，2023=-0.43） |
| 5 | `rank(liabilities/assets) - 1.5*rank(cashflow/assets) + rank(revenue/assets)` | ok | ok | ok | **0.7695** | 7 PASS / 1 FAIL |

## 关键结论
- cashflow 权重加码（2×）与 ts_delta 版本都因信号变弱而 Sharpe 跌破 1.25。
- Market 中性化反伤性能：赚钱的是「子行业内相对杠杆差」，行业间杠杆差近年亏钱。
- 第三字段 `revenue/assets`（资产周转率）是「免费」去相关成分——加了反而补 Sharpe/Fitness。
- 自相关从 1.0 → 0.8073 → 0.7695，仍差 0.07。

## 下一步路线
**A. 10% 豁免线（优先查）**：新 Sharpe ≥ 旧 Sharpe×1.10 即可提交，无视相关性。
   → 去 Alphas → OS 列表查裸 `liabilities/assets` 的 Sharpe。若 ≤ 新/1.1，直接过。
**B. 继续降相关**：
   - `… + 1.0*rank(revenue/assets)`（revenue 0.5→1.0）
   - 或 `… - 1.75*rank(cashflow/assets) + 1.0*rank(revenue/assets)`
**C. 技术面 + 基本面（正交，相关性必降）**：
   - 动量：`0.5*(组合) + 0.5*rank(ts_delta(close,60))`
   - 低波动：`0.5*(组合) - 0.5*rank(ts_std_dev(returns,60))`
   - 反转：`0.6*(组合) + 0.4*rank(-returns)`（换手高，慎）

## 字段含义速记
- `liabilities/assets` = 资产负债率（杠杆）
- `cashflow/assets` = 资产获现率
- `revenue/assets` = 资产周转率
- `ts_delta(x,252)` = x 的年度变化（252≈1 年交易日）
