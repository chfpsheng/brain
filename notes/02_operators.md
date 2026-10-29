# 02 · 操作符速查表（Operators Cheat Sheet）

> BRAIN Fast Expression：嵌套函数调用，向量化作用于「时间 × 股票」两维。平台自动向量化，不写循环。

---

## 一、时序类 `ts_*`（沿时间轴，每只股票单独算）

| 操作符 | 作用 | 示例 / 用途 |
|---|---|---|
| `ts_delta(x, d)` | x 今天 − x d 天前 | `ts_delta(close,252)` = 年动量 |
| `ts_delay(x, d)` | 把 x 往后移 d 期（取过去值） | `ts_delay(close,1)` = 昨收 |
| `ts_mean(x, d)` | d 期均值 | 移动平均 |
| `ts_std_dev(x, d)` | d 期标准差（波动） | `ts_std_dev(returns,60)` = 60 天波动 |
| `ts_min / ts_max(x, d)` | d 期最小/最大 | 区间高低 |
| `ts_arg_max / ts_arg_min(x, d)` | 最值出现位置 | 距高点多久 |
| `ts_rank(x, d)` | x 在自身 d 期历史里的排名 | 个股历史相对位置 |
| `ts_zscore(x, d)` | d 期 z 分数 | 时序标准化 |
| `ts_scale(x, d)` | d 期缩放到 [-1,1] | 去量纲 |
| `ts_covariance / ts_correlation(x,y,d)` | 两序列 d 期协方差/相关 | 量价关系 |
| `ts_regression(y,x,d)` | 滚动回归斜率 | 趋势强度 |
| `ts_decay_linear / ts_decay_exp(x,d)` | 线性/指数衰减加权 | 近期加权 |

**目的**：把「时间维度」信息转成信号（动量、反转、波动、趋势）。

---

## 二、横截面类（每天在股票间算）

| 操作符 | 作用 | 示例 / 用途 |
|---|---|---|
| `rank(x)` | 当天全 universe 百分位排名（0~1） | 交叉-sectional 排名，最常用 |
| `zscore(x)` | 当天横截面 z 分数 | 标准化 |
| `scale(x)` | 缩放到目标范围（默认 [-1,1]） | 控制暴露 |
| `normalize(x)` | 归一化 | — |
| `winsorize(x, a, b)` | 横截面截尾 | 防极端值 |

**目的**：使不同字段可比、可加减组合；构造多头/空头权重。

---

## 三、分组类 `group_*`（按行业/板块分组后再算）

| 操作符 | 作用 | 示例 / 用途 |
|---|---|---|
| `group_rank(x, g)` | 组内排名 | `group_rank(close, sector)` |
| `group_mean(x, g)` | 组内均值 | 行业平均 |
| `group_neutralize(x, g)` | 减组内均值 | 行业中性化（剔除行业暴露） |
| `group_zscore(x, g)` | 组内 z 分数 | 行业内标准化 |

**目的**：去掉系统性偏差（行业/市值/国家），避免「押赛道」而非押因子。
注：Settings 里的 Neutralization 是平台级一键中性化，与表达式内 `group_neutralize` 二选一或叠加。

---

## 四、统计 / 回归类

| 操作符 | 作用 | 用途 |
|---|---|---|
| `correlation(x, y, d)` | 滚动相关 | 数据探索：字段 vs `fwd_return` |
| `covariance(x, y, d)` | 滚动协方差 | — |
| `regression(y, x, d)` / `slope` | 斜率 | 因子暴露 |
| `decay_rate` 思路 | 预测力衰减 | 评估信号持续性 |

---

## 五、算术 / 数学 / 逻辑

| 类别 | 操作符 |
|---|---|
| 算术 | `+ - * /` |
| 数学 | `log, exp, abs, sign, power, sqrt` |
| 逻辑/条件 | `if(cond,a,b), greater, less, equal, is_null` |

---

## 六、编写铁律
1. 比率分子分母量纲差大时，**先各自 `rank()` 再加减**，勿裸加。
2. 基本面数据注意**前视偏差**：点到点数据通常已处理，但 Estimates 类需 `ts_delay` 偏移。
3. `group_*` 必须带 group 参数（如 `sector`）。
4. 复杂信号建议先 `rank()` 每字段 → 加权求和 → 必要时 `scale()`。

## 七、经典示例
- 动量：`rank(ts_delta(close, 60))`
- 反转：`rank(-returns)` 或 `rank(ts_delta(close, 5))` 取负
- 低波动：`-rank(ts_std_dev(returns, 60))`
- 价值：`-rank(pb)`
- 质量：`rank(cashflow/earnings)`
- 成长：`rank(ts_delta(revenue, 252))`
