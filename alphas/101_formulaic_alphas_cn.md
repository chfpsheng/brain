# 101 Formulaic Alphas（中文翻译 + BRAIN 提交可行性）

原文：Zura Kakushadze, *101 Formulaic Alphas*, SSRN 2701346 (2015-12-09)
WorldQuant LLC 授权公开，作者强调这些是**真实生产环境在用**的 alpha（写作时有 80 个在实盘）。

---

## 一、论文核心内容（翻译要点）

### 摘要
- 给出 **101 个真实量化交易 alpha 的显式公式（同时也是代码）**。
- 平均持仓周期约 **0.6–6.4 天**（偏中高频）。
- 这 101 个 alpha 的**平均两两相关系数仅 15.9%**（中位数 14.3%）——天然低相关，正是能组合成"超级 alpha"的基础。
- alpha 收益**与波动率强相关**，但**与换手率无显著依赖**（直接证实了早期基于更间接分析的结论）。
- 换手率对 alpha 之间的相关性**解释力很差**。

### 引言
- 现代量化两条趋势：① 用更复杂技术挖 alpha，alpha 越来越弱、越来越短命；② 技术让"挖 alpha"流程自动化，alpha 数量可达几十万、几百万甚至上十亿。
- 把海量（大多微弱、短命的）alpha 组合成一个统一"mega-alpha"来交易，可自动内部对冲成交、降低成本、做组合分散。
- 本文目的：揭开量化交易的神秘面纱，给读者看"真实 alpha 长什么样"，并可复现、做新研究。

### 信号大致分两类（第 2 节）
- **均值反转（mean-reversion）**：符号与所基于的收益相反。例：`−ln(今开 / 昨收)`（delay-0，赌隔夜跳空回吐）。
- **动量（momentum）**：`ln(昨收 / 昨开)`（delay-1，赌昨日趋势今日延续）。
- "delay-0"= 用当天数据、当天（贴近收盘）交易；"delay-1"= 用最新数据、次日交易。
- 复杂 alpha 里两者常混合。

### 数据与方法（第 3 节）
- 数据区间 **2010-01-04 ~ 2013-12-31**，样本协方差矩阵非奇异（1006 个观测）。
- 指标定义：年化 Sharpe `3 = √252 · (日均PnL / 日波动)`；换手 `4`；每手美分 `4`（原文记号）。
- 实证：收益~波动率缩放 `≈ 0.76`；换手对相关性解释力弱。

### 结论
- 这些不是"玩具"alpha，是真实生产信号；据作者所知，这是文献中**首次一次性公开如此大量的真实公式化 alpha**。
- 自动化挖 alpha + 组合成 mega-alpha，靠内部成交交叉大幅省交易成本。

---

## 二、算子 / 函数对照（论文 → BRAIN FASTEXPR）

| 论文算子 | 含义 | BRAIN 写法 |
|---|---|---|
| `rank(x)` | 横截面排名 | `rank(x)` |
| `delay(x, d)` | d 天前的值 | `ts_delay(x, d)` |
| `correlation(x, y, d)` | 过去 d 天时序相关 | `ts_corr(x, y, d)` |
| `covariance(x, y, d)` | 过去 d 天时序协方差 | `ts_covariance(x, y, d)` |
| `scale(x, a)` | 重缩放使 `sum(abs(x))=a`（默认1） | `scale(x, a)` |
| `delta(x, d)` | 今值 − d 天前值 | `ts_delta(x, d)` |
| `signedpower(x, a)` | `x^a`（带符号） | `signed_power(x, a)` 或 `pow(x, a)` |
| `decay_linear(x, d)` | 线性衰减加权移动平均 | `ts_decay_linear(x, d)` |
| `indneutralize(x, g)` | 按行业组横截面去均值 | **用 Settings 的 `neutralization`（SUBINDUSTRY/INDUSTRY/MARKET）替代** |
| `ts_min/max(x,d)` | 时序最小/最大 | `ts_min(x,d)` / `ts_max(x,d)` |
| `ts_argmax/argmin(x,d)` | 极值出现在第几天 | `ts_arg_max(x,d)` / `ts_arg_min(x,d)` |
| `ts_rank(x, d)` | 过去 d 天时序排名 | `ts_rank(x, d)` |
| `min/max(x,d)` | = ts_min/ts_max | `ts_min` / `ts_max` |
| `sum(x, d)` | 时序求和 | `ts_sum(x, d)` |
| `product(x, d)` | 时序连乘 | `ts_product(x, d)` |
| `stddev(x, d)` | 移动标准差 | `ts_std_dev(x, d)` |
| `abs / log / sign / sqrt` | 标准 | 同名 |
| `x ? y : z` | 三元条件 | BRAIN 用 `where(cond, y, z)`（若不支持三元则替换） |
| `adv{d}` | 过去 d 日平均成交额(ADV) | `ts_mean(volume * close, d)`（或 BRAIN `adv` 算子） |
| `cap` | 市值 | `market_cap`（在 Data 页确认字段名，如 `fnd6_marketcap`） |
| `returns` | 收盘对收盘收益 | `(close - ts_delay(close,1)) / ts_delay(close,1)` |

> 结论：**全部 101 个 alpha 都能在 BRAIN 表达并提交**。区别只在复杂度与"是否需要额外数据/中性粒度"。

---

## 三、输入数据
- `returns`：日收盘对收盘收益
- `open/close/high/low/volume`：日价格与成交量
- `vwap`：日均成交量加权价
- `cap`：市值（基本面）
- `adv{d}`：过去 d 日平均成交额
- `IndClass`：行业分类占位符（sector/industry/subindustry），用于 `indneutralize`

---

## 四、101 条 Alpha 中文速查与提交可行性

> 标记：✅ 纯量价/VWAP 可直接提交 ｜ ⚠️ 含 `cap`(市值) ｜ ⚙️ 含 `indneutralize`(用 Settings 中性替代) ｜ 💧 含 `adv{d}`(用 `ts_mean(volume*close,d)` 替代) ｜ 🔀 含三元 `? :`(用 `where` 替代)

| # | 中文含义 | 可行性 |
|---|---|---|
| 1 | 下跌放量时 close 平方的时序最大值位置排名减0.5（下跌反转） | ✅🔀 |
| 2 | 成交量2日变化排名 与 (收-开)/开 排名 的6日负相关 | ✅ |
| 3 | open 排名 与 volume 排名 10日负相关 | ✅ |
| 4 | low 的9日时序排名取负 | ✅ |
| 5 | (open−10日均vwap)排名 × (−|close−vwap|排名) | ✅ |
| 6 | open 与 volume 10日负相关 | ✅ |
| 7 | 若量>20日均额则取量价背离排名，否则−1 | ✅💧🔀 |
| 8 | 5日(open×收益)合计的10日延迟差分排名取负 | ✅ |
| 9 | 1日收益5日极值方向条件反转 | ✅🔀 |
| 10 | 同上4日窗口反转 | ✅🔀 |
| 11 | (vwap−close)3日极大+极小排名 × volume3日变化排名 | ✅ |
| 12 | 成交量1日变化符号 × (−1日close变化) | ✅ |
| 13 | close 与 volume 排名的5日协方差取负 | ✅ |
| 14 | −1日收益排名 × open−volume 10日相关 | ✅ |
| 15 | −(high与volume排名3日相关)的3日和排名 | ✅ |
| 16 | −close 与 volume 排名5日协方差 | ✅ |
| 17 | −close10日时序排名 × close二阶差分 × (量/adv20)5日排名 | ✅💧 |
| 18 | −[5日|收-开|标准差 + (收-开) + 收-开10日相关]排名 | ✅ |
| 19 | −(close与7日前差)符号 × (1+250日收益和排名) | ✅ |
| 20 | −(open相对昨高/昨收/昨低)三排名乘积 | ✅ |
| 21 | 均线与标准差比较 + 量比 的条件多空 | ✅💧🔀 |
| 22 | −(high−volume5日相关变化) × close20日标准差排名 | ✅ |
| 23 | 若20日均high<今high则−2日high变化，否则0 | ✅ |
| 24 | 100日均价变化率条件：偏低则取(close−100日低) | ✅🔀 |
| 25 | −(returns×adv20×vwap×(high−close))排名 | ✅💧 |
| 26 | −(volume与high5日时序排名相关)的3日max | ✅ |
| 27 | rank(6日volume−vwap相关)>0.5 则−1否则1 | ✅💧🔀 |
| 28 | scale(corr(adv20,low,5)+(high+low)/2−close) | ✅💧 |
| 29 | 多层 rank/scale/log/min 嵌套（复杂） | ✅🔀 |
| 30 | (1−3日close变化方向符号和) × 量比5/20 | ✅ |
| 31 | decay_linear(−delta(close,10)) + (−delta(close,3)) + sign(corr(adv20,low,12)) | ✅💧 |
| 32 | scale(7日均价−close) + 20×scale(corr(vwap,延迟close,230)) | ✅ |
| 33 | rank(1 − open/close)（隔夜跳空反转） | ✅ |
| 34 | rank(1−收益波动比) + rank(1−1日close变化) | ✅ |
| 35 | volume32日排名 × (1−(收+高−低)16日排名) × (1−收益32日排名) | ✅ |
| 36 | 多权重：(收-开)~量 相关 + 跳空 + 收益时序排名 + vwap-ad 相关 + 长期均值偏离 | ✅💧 |
| 37 | corr(delay(开-收,1),收,200) + rank(开-收) | ✅ |
| 38 | −rank(ts_rank(close,10)) × rank(close/open) | ✅ |
| 39 | −rank(delta(close,7)×(1−rank(decay(量/adv20,9)))) × (1+250日收益和排名) | ✅💧 |
| 40 | −rank(stddev(high,10)) × corr(high,volume,10) | ✅ |
| 41 | sqrt(high×low) − vwap（价格中枢偏离） | ✅ |
| 42 | rank(vwap−close)/rank(vwap+close)（VWAP相对位置反转） | ✅ |
| 43 | (量/adv20)20日排名 × (−1日close变化)8日排名 | ✅💧 |
| 44 | −corr(high, rank(volume), 5) | ✅ |
| 45 | rank(延迟close5/20均) × corr(收,量,2) × rank(corr(收5均,收20均,2)) 取负 | ✅ |
| 46 | 20日/10日斜率趋势条件多空 | ✅🔀 |
| 47 | (1/close排名×量/adv20×(high×(high−close)排名/5日均high)) − rank(vwap−延迟vwap5日) | ✅💧 |
| 48 | 行业中性(subindustry)的盈利自相关/close ÷ 收益平方250日和（盈利漂移） | ⚙️ |
| 49 | 类46，阈值−0.1 | ✅🔀 |
| 50 | −(rank(量)与rank(vwap)5日相关)的5日max | ✅ |
| 51 | 类46，阈值−0.05 | ✅🔀 |
| 52 | (−5日low最小+延迟5日low最小) × rank(长期−短期收益和) × volume5日排名 | ✅ |
| 53 | −delta(((收−低)−(高−收))/(收−低), 9)（日内影线反转） | ✅ |
| 54 | −((低−收)×open^5)/((低−高)×收^5)（开盘跳空反转） | ✅ |
| 55 | −corr(rank((收−12日低)/(12日高−12日低)), rank(量), 6) | ✅ |
| 56 | −(rank(10日收益和/2日收益和3日均) × rank(returns×cap))（小市值效应） | ⚠️ |
| 57 | −(close−vwap)/decay_linear(rank(ts_argmax(close,30)),2) | ✅ |
| 58 | −ts_rank(decay_linear(corr(IndNeutralize(vwap,sector),量,3.93),7.89),5.50) | ⚙️💧 |
| 59 | 类58，industry 中性 | ⚙️💧 |
| 60 | −(2×scale(影线×量排名) − scale(ts_argmax(close,10)排名)) | ✅ |
| 61 | rank(vwap−16日vwap最小) < rank(vwap−adv180相关) | ✅💧 |
| 62 | rank(vwap−adv22相关) < rank(open双排名<(高+低)/2+高排名) 取负 | ✅💧 |
| 63 | rank(decay(delta(IndNeutralize(收,industry),2.25),8.22)) − rank(decay(corr(混合价,adv180和,13.56),12.29)) 取负 | ⚙️💧 |
| 64 | rank(corr(混合价,adv120和,16.62)) < rank(delta(混合价,3.70)) 取负 | ⚙️💧 |
| 65 | rank(corr(混合价,adv60和,6.40)) < rank(open−open13日最小) 取负 | ⚙️💧 |
| 66 | rank(decay(delta(vwap,3.51),7.23)) + ts_rank(decay((混合低−vwap)/(开−中价),11.42),6.73) 取负 | ⚙️💧 |
| 67 | rank(high−2日high最小)^rank(corr(IndNeutralize(vwap,sector),IndNeutralize(adv20,subind),6.03)) 取负 | ⚙️💧 |
| 68 | ts_rank(corr(rank(high),rank(adv15),8.92),13.93) < rank(delta(混合价,1.06)) 取负 | ⚙️💧 |
| 69 | rank(delta(IndNeutralize(vwap,industry),2.72)的4.79日max)^ts_rank(corr(混合价,adv20,4.92),9.06) 取负 | ⚙️💧 |
| 70 | rank(delta(vwap,1.29))^ts_rank(corr(IndNeutralize(收,industry),adv50,17.83),17.92) 取负 | ⚙️💧 |
| 71 | max(ts_rank(decay(corr(ts_rank(收,3.44),ts_rank(adv180,12.06),18.02),4.21),15.69), ts_rank(decay((低+开−2vwap)^2排名,16.47),4.44)) | ⚙️💧 |
| 72 | rank(decay(corr((高+低)/2,adv40,8.93),10.15)) / rank(decay(corr(ts_rank(vwap,3.72),ts_rank(量,18.52),6.87),2.95)) | ⚙️💧 |
| 73 | max(rank(decay(delta(vwap,4.73),2.92)), ts_rank(decay(delta(混合低,2.04)/(混合低),−1),3.34),16.74)) 取负 | ⚙️💧 |
| 74 | rank(corr(收,adv30和,15.14)) < rank(corr(rank(混合价),rank(量),11.48)) 取负 | ⚙️💧 |
| 75 | rank(corr(vwap,量,4.24)) < rank(corr(rank(低),rank(adv50),12.44)) | ⚙️💧 |
| 76 | max(rank(decay(delta(vwap,1.24),11.83)), ts_rank(decay(corr(IndNeutralize(低,sector),adv81,8.15),19.57),17.15)) 取负 | ⚙️💧 |
| 77 | min(rank(decay((高+低)/2+高−(vwap+高),20.05)), rank(decay(corr((高+低)/2,adv40,3.16),5.64))) | ⚙️💧 |
| 78 | rank(delta(IndNeutralize(混合价,sector),1.23))^rank(corr(rank(vwap),rank(量),5.77)) | ⚙️💧 |
| 79 | rank(delta(IndNeutralize(混合价,sector),1.23)) < rank(corr(ts_rank(vwap,3.61),ts_rank(adv150,9.19),14.66)) | ⚙️💧 |
| 80 | rank(sign(delta(IndNeutralize(混合价,industry),4.05)))^ts_rank(corr(high,adv10,5.11),5.54) 取负 | ⚙️💧 |
| 81 | rank(log(product(rank(corr(vwap,adv10和,8.48)^4),14.97))) < rank(corr(rank(vwap),rank(量),5.08)) 取负 | ⚙️💧 |
| 82 | rank(delay((高−低)/(5日均收),2)) × rank(rank(量)) / (((高−低)/5日均收)/(vwap−收)) | ⚙️💧🔀 |
| 83 | min(rank(decay(delta(混合价,1.46),14.87)), ts_rank(decay(corr(IndNeutralize(量,sector),混合价,17.48),6.92),13.43)) 取负 | ⚙️💧 |
| 84 | signed_power(ts_rank(vwap−15日vwap最大,20.71), delta(close,4.97)) | ✅ |
| 85 | rank(corr(混合价,adv30,9.61))^rank(corr(ts_rank((高+低)/2,3.71),ts_rank(量,10.16),7.11)) | ⚙️💧 |
| 86 | ts_rank(corr(收,adv20和,6.00),20.42) < rank((开+收)−(vwap+开)) 取负 | ⚙️💧 |
| 87 | max(rank(decay(delta(混合价,1.91),2.65)), ts_rank(decay(abs(corr(IndNeutralize(adv81,industry),收,13.41)),4.90),14.45)) 取负 | ⚙️💧 |
| 88 | min(rank(decay((rank开+排名低)−(排名高+排名收),8.07)), ts_rank(decay(corr(ts_rank(收,8.45),ts_rank(adv60,20.70),8.01),6.65),2.62)) | ⚙️💧 |
| 89 | ts_rank(decay(corr(混合低,adv10,6.94),5.52),3.80) − ts_rank(decay(delta(IndNeutralize(vwap,industry),3.48),10.15),15.30) | ⚙️💧 |
| 90 | rank(close−4.67日close最大)^ts_rank(corr(IndNeutralize(adv40,subind),低,5.38),3.22) 取负 | ⚙️💧 |
| 91 | ts_rank(decay(decay(corr(IndNeutralize(收,industry),量,9.75),16.40),3.83),4.87) − rank(decay(corr(vwap,adv30,4.01),2.68)) 取负 | ⚙️💧 |
| 92 | min(ts_rank(decay(((高+低)/2+收)<(低+开),14.72),18.87), ts_rank(decay(corr(rank(低),rank(adv30),7.59),6.94),6.81)) | ⚙️💧 |
| 93 | ts_rank(decay(corr(IndNeutralize(vwap,industry),adv81,17.42),19.85),7.54) / rank(decay(delta(混合价,2.77),16.27)) | ⚙️💧 |
| 94 | rank(vwap−11.58日vwap最小)^ts_rank(corr(ts_rank(vwap,19.65),ts_rank(adv60,4.03),18.09),2.71) 取负 | ⚙️💧 |
| 95 | rank(open−12.41日open最小) < ts_rank((rank(corr((高+低)/2和,adv40和,12.87)^5),11.76) | ⚙️💧 |
| 96 | max(ts_rank(decay(corr(rank(vwap),rank(量),3.84),4.17),8.38), ts_rank(decay(ts_argmax(corr(ts_rank(收,7.45),ts_rank(adv60,4.13),3.65),12.66),14.04),13.41)) 取负 | ⚙️💧 |
| 97 | rank(decay(delta(IndNeutralize(混合价,industry),3.37),20.45)) − ts_rank(decay(corr(ts_rank(低,7.88),ts_rank(adv60,17.26),4.98),18.59),15.72) 取负 | ⚙️💧 |
| 98 | rank(decay(corr(vwap,adv5和,4.58),7.18)) − rank(decay(ts_rank(ts_argmin(corr(rank(开),rank(adv15),20.82),8.63),6.96),8.07)) | ⚙️💧 |
| 99 | rank(corr((高+低)/2和,adv60和,8.81)) < rank(corr(低,量,6.28)) 取负 | ⚙️💧 |
| 100 | −((1.5×scale(indneutralize(indneutralize(影线×量排名,subind),subind))) − scale(indneutralize(corr(收,rank(adv20),5)−rank(ts_argmin(收,30)),subind)) × (量/adv20)) | ⚙️💧 |
| 101 | (close − open) / ((high − low) + 0.001)（经典日内反转） | ✅ |

> 注：含 `indneutralize` 的（48, 58–100 等）在 BRAIN 里**用 Settings 的 `neutralization` 替代**即可提交；论文里 sector/industry/subindustry 的细粒度差异对结果影响通常很小。含 `adv{d}` 的用 `ts_mean(volume*close, d)`。含 `? :` 的用 `where(cond, a, b)`。

---

## 五、精选"可直接提交"短名单（已转成 BRAIN 表达式）

沿用你过关的设置：**Universe TOP3000 / Neutralization SUBINDUSTRY / Decay 7（可试5~12）/ Truncation 0.08 / Delay 1**。
这些彼此结构不同、相关性低（论文平均 15.9%），且大多已被 WorldQuant 实盘验证。

```text
# ★101 日内反转 —— 就是你已经验证通过的思路（基础版，更稳）
rank((close - open) / ((high - low) + 0.001))

# ★42 VWAP相对位置反转 —— 你另一个已验证信号
rank(vwap - close) / rank(vwap + close)

# 33 隔夜跳空反转（与日内反转不同机制，相关性低）
rank(1 - open / close)

# 12 量价反转（量能变化方向 × 价格变化）
sign(ts_delta(volume, 1)) * (-1 * ts_delta(close, 1))

# 38 短期反转 × 跳空
(-1 * rank(ts_rank(close, 10))) * rank(close / open)

# 53 日内影线反转
-ts_delta(((close - low) - (high - close)) / (close - low), 9)

# 54 开盘跳空反转（高阶）
(-1 * ((low - close) * pow(open, 5))) / ((low - high) * pow(close, 5))

# 2 量-价变化相关（不同维度）
(-1 * ts_corr(rank(ts_delta(log(volume), 2)), rank((close - open) / open), 6))

# 41 价格中枢偏离（sqrt(high*low) - vwap）
sqrt(high * low) - vwap

# 55 相对位置反转（离12日高低区间的位置）
-ts_corr(rank((close - ts_min(low, 12)) / (ts_max(high, 12) - ts_min(low, 12))), rank(volume), 6)

# 11 VWAP偏离 + 量能
(rank(ts_max(vwap - close, 3)) + rank(ts_min(vwap - close, 3))) * rank(ts_delta(volume, 3))

# 40 高波动反转
(-1 * rank(ts_std_dev(high, 10))) * ts_corr(high, volume, 10)

# 43 量比时序排名 × 价格反转
ts_rank(volume / ts_mean(volume * close, 20), 20) * ts_rank(-1 * ts_delta(close, 7), 8)

# ★56 小市值效应（需市值字段，不同数据集→相关性最低）
-(rank(ts_sum(returns, 10) / ts_sum(ts_sum(returns, 2), 3)) * rank(returns * market_cap))
# 注：market_cap 字段名请在 Data 页确认（如 fnd6_marketcap）；returns 用
# (close - ts_delay(close, 1)) / ts_delay(close, 1) 替代
```

> ★ = 与你已验证信号同族，最稳；其余为不同机制、可进一步拉低彼此相关性。

---

## 六、提交纪律（务必）
1. **一次一个**：每个表达式单独 Simulate，先看 IS（Sharpe≥1.25 / Fitness≥1 / Turnover≤70%）。
2. **降换手**：若 Turnover 高，把 `Decay` 往上调（7→10→12）或在表达式加 `ts_decay_linear(..., d)` / `ts_mean(..., d)` 平滑。
3. **相关性关**：每个跑通后点 **Check Submission**，相关 **< 0.7** 才算真能交。论文平均相关性仅 15.9%，所以这批彼此基本都过。
4. **字段核实**：`market_cap`、`cap` 等非价格字段，先用 Data 页确认真实 Field ID（同你之前查 `fnd6_*` 的办法）。
5. **TUTORIAL 限额**：网页提交/验指标不限流；脚本（`GET /alphas`）会 429，看指标优先用网页。
