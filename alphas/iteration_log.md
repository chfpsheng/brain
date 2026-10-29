# Alpha 迭代留档（WorldQuant BRAIN）

> 账号：CY81054（权限 TUTORIAL，API 限额严，主要在网页控制台跑）
> 基础设置：Region=USA, Delay=1, Language=FASTEXPR, Truncation=0.08
> 提交门槛参考：IS Sharpe ≥ 1.25、Fitness ≥ 1、Turnover ≤ 70%、与已有 alpha 相关 < 0.7

---

## ✅ 当前最优可提交 alpha（待跑相关性）

**表达式**
```text
rank(-(close - open) / open)
```

**设置**
- Universe: TOP3000
- Neutralization: SUBINDUSTRY
- Decay: **7**（关键，见下）
- Truncation: 0.08
- Delay: 1

**结果**：IS Testing 全过（6 PASS），Fitness ≥ 1。
**最后一步**：点 `Check Submission` 跑 Pearson 相关性，相关 < 0.7 即可正式提交。

**含义**：`(close-open)/open` 是日内收益率，`-(...)` 取反转，`rank(...)` 横截排名。
即"做多今天开盘后跌最狠的股票、做空涨最狠的"，赌日内动量反转（short-term reversal）。

**为什么 Decay=7 才过**：Fitness 同时吃 Sharpe（信号要新鲜）和 Turnover（要少换）。
Decay 太低（1）→ 天天全换、Turnover >70% 挂；Decay 太高（10~12）→ 太"念旧"、信号滞后、Sharpe/收益掉、Fitness 卡 0.97；Decay=7 是甜点——持仓跟手又没破 70% 换手，Fitness 过线。

---

## 📋 全量试错记录（按时间）

| # | 表达式 | 关键设置 | Sharpe | Fitness | Turnover | 结果 |
|---|---|---|---|---|---|---|
| 1 | `rank(ts_delta(close, 60))` | — | -1.00 | -0.76 | 10.13% | 方向反了（亏） |
| 2 | `rank(-ts_delta(close, 60))` | — | 0.89 | 0.66 | — | 2 FAIL（Sharpe/Fitness） |
| 3 | `rank(-ts_mean(ts_delta(close,1),60))` | — | 0.91 | 0.75 | — | 6 PASS/1 FAIL(Fitness)；2022=0.34 拖累 |
| 4 | `rank(-ts_delta(60)) + rank(-ts_std_dev(returns,60))` | — | 0.63 | 0.47 | — | 低波腿为负，拖垮 |
| 5 | `0.7*rank(-ts_delta(60)) + 0.3*rank(ts_rank(volume,20))` | — | 0.88 | 0.54 | — | 量能腿无效 |
| 6 | `rank(-(close-vwap)/vwap)` | Decay4 | 过 | 0.79 | 83.18% | 2 FAIL（Fitness/Turnover） |
| 7 | `rank(-(close-vwap)/vwap)` | Decay10/12, SUBIND | 过 | 0.77 | ~55% | 6 PASS/1 FAIL(Fitness) |
| 8 | `rank(-(close-vwap)/vwap)` | TOP1000 | 1.23 | 0.58 | — | 3 FAIL（更差，退回 TOP3000） |
| 9 | `rank(-ts_rank((close-vwap)/vwap,10))` | TOP3000 | 过 | 0.65 | — | 比裸版差，撤回 |
| A | `rank(ts_std_dev(returns,60))`（高波腿） | — | -0.14 | -0.07 | — | 负，淘汰 |
| B | `rank(ts_rank(volume,20))`（量能腿） | — | 0.36 | 0.08 | — | 弱正，仅小权重备选 |
| C | `rank(-(close-open)/open)`（日内反转） | Decay10/12 | 过 | 0.97 | — | 6 PASS/1 FAIL(Fitness 0.97) |
| **C✅** | `rank(-(close-open)/open)` | **Decay7, SUBIND** | 过 | **≥1** | 在限内 | **全过，待相关性** |

---

## 🧩 待验证的腿（D 还没跑）

```text
D. rank(ts_mean(abs(returns)/volume, 20))   # 非流动性溢价腿
```

若 D 也为正，可做成三腿组合提升分散度/稳定性。

---

## 💡 经验沉淀

1. 经典单因子（60日动量）被挖烂，裸跑 Sharpe 上不了 1.25。
2. 同族微调（换窗口/平滑/换 universe/调 decay）有"平台期"，到头就换结构。
3. 组合前**必须先单独验证每条腿**（A 就因低波为负拖垮了整体）。
4. 日内反转类（VWAP 偏离、开盘-收盘反转）在美股是强且稳的方向。
5. Decay 是 Sharpe↔Turnover 的甜点旋钮，不是越大越好。
6. 提交前必须过 **相关性 < 0.7**，否则白忙。
