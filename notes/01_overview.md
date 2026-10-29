# 01 · Alpha 原理 / Simulation 设置 / 操作符分类 / 回测指标

> 零基础学量化 · 概览笔记（基于 BRAIN 平台）

---

## 一、Alpha 是什么 & BRAIN 运行原理

**Alpha**：一个预测资产未来收益的量化信号。在 BRAIN 里就是一个表达式（Fast Expression），
每天对 universe 里每只股票算一个值（排名/标准化），用于做多/做空。目标：高 Sharpe、低 decay、
低 turnover、覆盖广、与已有 alpha 低相关。

**BRAIN 运行链路**：
1. 数据层：平台预清洗行情/基本面/另类数据，按 region / universe / asset class 组织。
2. Alpha 层：用 Alpha Expression Language 写表达式，平台每天在指定 universe 上向量化计算信号。
3. 模拟层（Simulation）：历史回测，产出 Sharpe、IC、turnover 等指标。
4. 验证层：IS（样本内）→ OS（样本外）→ TEST（实盘/纸面评分）。
5. 闭环：开发 → 模拟 → 分析 → 提交 → 评分 → 迭代。

**Universe（股票池）**：alpha 在哪些股票上同时计算。表达式在 universe 内逐日、逐股计算，
横截面操作符（rank/zscore/group_rank）都在「当天、universe 内」对全部股票排序。
平台从中做多高分、做空低分。

---

## 二、Simulation 各项 Settings

| 设置 | 含义 | 注意事项 |
|---|---|---|
| **Universe** | 回测股票池（USA / JAPAN / ESTU 扩展池…） | 覆盖度影响 alpha 广度 |
| **Start/End date** | 回测区间 | 要足够长、跨牛熊 |
| **Delay（0/1）** | 信号用当天收盘还是隔日算 | 实盘有延迟，常用 delay=1 更真实，防前视 |
| **Decay** | 持仓多日时权重衰减（如 4） | 降低 turnover、平滑信号 |
| **Neutralization** | 按行业/板块/市值/国家中性化 | 去掉系统性暴露，避免押赛道 |
| **Pasteurization** | 风险过滤（剔低流动性/高风险股） | 提升稳健性 |
| **Truncation** | 对 alpha 值 winsorize 截尾（如 0.08） | 防极端值 |
| **Region / Asset class** | 地区/资产类别 | 不同 region 提交门槛不同 |
| **NaN / Unit Handling** | 空值/单位处理 | 校验数据可用性 |
| **Max Trade / Max Pos** | 单日最大交易/单一持仓 | OFF=不限制 |

---

## 三、Fast Expression 语言 & 操作符分类

本质是嵌套函数调用，向量化作用于「时间 × 股票」两维。平台自动向量化，不写循环。

### 1. 数据字段（operands）
- 行情 Market：`close, open, high, low, volume, vwap, adv20, returns, fwd_return`
- 基本面 Fundamentals：`eps, book_value, sales, liabilities, assets, cashflow, revenue, equity`
- 估值：`pe, pb`
- 另类/宏观/情感等

### 2. 操作符结构
- **时序类 `ts_*`**：`ts_mean, ts_std_dev, ts_rank, ts_delay, ts_delta, ts_min/max,
  ts_arg_max, ts_covariance, ts_correlation, ts_regression, ts_zscore, ts_scale`
  → 捕捉时间维度规律（动量/反转/波动）。例：`ts_delta(x, d) = x(今天) − x(d 天前)`，252=1 年。
- **横截面类**：`rank(x), zscore(x), scale(x), normalize(x), winsorize(x)`
  → 每天在股票间排序/标准化，使信号可比、可组合。
- **分组类 `group_*`**：`group_rank, group_mean, group_neutralize`
  → 按行业/板块控制暴露。例：`group_neutralize(x, sector)`。
- **统计/回归类**：`regression, covariance, correlation, slope`
  → 刻画变量间关系。
- **算术/数学**：`+ - * / , log, exp, abs, sign, power, sqrt`
- **逻辑/条件**：`if(cond, a, b), greater, less, equal`

### 3. 语法注意
- 单表达式、嵌套调用；经典语言不支持多行变量（新版有 Alpha Variables 可定义中间变量）。
- `group_*` 通常带 group 参数（如 `group_rank(x, sector)`）。
- 比率分子分母量纲差异大时务必都 `rank()` 再加减，勿裸加。

---

## 四、数据字段分类（结构差异 & 注意）

| 类别 | 例子 | 结构特点 | 注意事项 |
|---|---|---|---|
| **Market（行情）** | close, volume, adv20 | 每日、稠密、全 universe 有 | 最直接，lookahead 风险最低 |
| **Fundamentals（基本面）** | eps, book_value, liabilities | 季度/年度、稀疏、point-in-time | 注意报告滞后/前视偏差，常需 `ts_delay` 或 `-1` 偏移 |
| **Estimates（分析师预期）** | 盈利预测 | 稀疏、易前视 | 用错时点会偷看未来 |
| **Alternative（另类）** | 情感、宏观、搜索量 | 来源杂、覆盖不均 | 先查 coverage |
| **Reference（公司行动）** | 分红、拆细、复权 | 事件型 | 影响复权准确性 |

**通用注意**：每个字段有 category / universe / coverage 属性，用前务必查覆盖率和空值率。

### Data Explorer 看什么
- **Coverage**：非空股票占比（太低别用）
- **Null %**：空值比例
- **与 `fwd_return` 相关性**：预测力（越高越有 alpha 潜力）
- **Decay**：预测力衰减速度
- **时序图/分布**：看异常、是否需要 winsorize

### 常用数据探索表达式
- `correlation(field, fwd_return(d), d)` —— 测字段对未来收益预测力
- `coverage(field)` / 非 null 计数 —— 看可用性
- `rank(field)` / `zscore(field)` —— 看横截面分布
- `ts_mean / ts_std_dev` —— 看时序稳定性
- `group_rank(field, sector)` —— 看行业内相对位置

**探查铁律**：先查 coverage 和 null% → 再查与 fwd_return 相关 → 最后看 decay。

---

## 五、回测指标 & IS/OS/TEST

### 指标定义
- **Sharpe**：收益均值 / 收益标准差（风险调整后收益，越高越好）
- **IC（信息系数）**：alpha 与未来收益（常取 rank IC）的相关性，衡量纯预测力
- **Turnover（换手）**：组合每日变动比例（越低交易成本越低）
- **Fitness**：综合分（≈ Sharpe 相关 − turnover 惩罚），提交门槛看它
- **Decay**：预测力衰减速度
- **Drawdown / Volatility**：最大回撤 / 波动
- **Margin (bps)**：每单位交易额赚的基点收益（低换手+正 margin = 高质量）
- **Coverage**：有信号的股票占比
- **Long Count / Short Count**：每天多/空头持仓股票数（组合广度/分散度）

### IS / OS / TEST
- **IS（In-Sample，样本内）**：开发调参用的历史区间。指标好看≠有效，有**过拟合**风险。
- **OS（Out-of-Sample，样本外）**：开发时没碰过的历史区间，用于验证。OS Sharpe 需足够接近 IS。
- **TEST（实测）**：提交后平台用持续新数据做实时/纸面评分，决定能否拿真金白银。

流程：**IS 开发 → OS 验证 → TEST 实盘评分**。

---

## 六、Alpha 提交标准 & 测试（Check 1~4）

- **Check 1（Sharpe）**：IS Sharpe ≥ 阈值（region 不同，常见 ≥1.0~1.25）
- **Check 2（IS/OS 一致性）**：OS Sharpe 需达 IS 的足够比例（如 ≥0.7× 或 OS 本身 ≥ 某值）
- **Check 3（Turnover）**：换手率在区间内（常见 1%~70%）
- **Check 4（相关性/独特性）**：与已提交/平台 alpha 相关性 < 0.7（防克隆）；
  豁免：新 Sharpe 比相关旧 alpha 好 ≥10% 仍可过

附加检查：Fitness ≥1、子 universe Sharpe、单票权重（Long/Short Count 不过度集中）。

### 提交 Do & Don't
**Do ✅**：先确认 OS 稳健；做好 neutralization；覆盖广、turnover 合理；确保 alpha 独特；简单优先。
**Don't ❌**：别在 IS 上过拟合；别提交高相关「克隆」；别忽略 turnover；别用含前视偏差数据；
别跳过 OS 验证；别超提交配额/触代码复用规则。

---

## 七、实战要点（来自杠杆因子探索）

- 纯 `liabilities/assets`（资产负债率）强但易被自己已提交 alpha 判定克隆（自相关=1）。
- 用 `rank(liabilities/assets) - 1.5*rank(cashflow/assets) + rank(revenue/assets)`
  降相关，但需兼顾 Sharpe/Fitness/Sub-universe Sharpe。
- 去相关手段：换中性化基准、掺第三字段、加技术面（`ts_delta(close,60)` 等，与基本面正交）。
- 已提交 alpha 的 Sharpe 是关键：若其 Sharpe ≤ 新 Sharpe/1.1，走 10% 豁免线直接提交。
- 平台 Correlation 区块（Self / Prod）可展开看撞了哪些 alpha ID 及系数。
