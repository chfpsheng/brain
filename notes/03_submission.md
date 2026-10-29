# 03 · Alpha 提交标准与 Checklist 详解

> 提交前逐条核对。不同 region / universe 阈值不同，以下为常见基准（以平台实际显示为准）。

---

## 一、提交检查项（Check 1~N）

| 检查 | 常见门槛（TOP3000） | 含义 |
|---|---|---|
| **Sharpe** | ≥ 1.25（部分 region 1.0） | IS Sharpe 必须过线 |
| **Fitness** | ≥ 1.0 | 综合分 = Sharpe 相关 − turnover 惩罚 |
| **Turnover** | 1% ~ 70% | 换手率区间，太低(<1%)或太高都不行 |
| **Sub-universe Sharpe** | ≥ 0.53（小池如 TOP500） | 更小子池也要有表现 |
| **Self-correlation** | ≤ 0.7 | 与**自己已提交** alpha 相关性上限 |
| **Prod-correlation** | ≤ 0.7 | 与**平台生产** alpha 相关性上限 |
| **Weight / Max-pos** | 单票权重不超限 | 防押单只（Long/Short Count 不过度集中） |
| **Single Data Set** | 徽标（非硬卡） | 只用单一数据字段，可能有限制/乘子 |

### Self-correlation 豁免规则
> 若新 alpha 的 Sharpe ≥ 相关旧 alpha 的 Sharpe × **1.10**，即使相关性 > 0.7 也通过。

**怎么查旧 alpha 的 Sharpe**：Alphas → OS(已提交) 列表 → 点开 → IS Summary → Sharpe。

---

## 二、相关性检查在哪看
- **Alpha 详情页 → Correlation 区块**：含 Self-correlation 与 Prod-correlation，点 `∨` 展开看撞了哪些 alpha ID 及系数。
- **Submit 面板**：检查清单里直接列出 Self-correlation 数值 + 触发 alpha + PASS/FAIL。

---

## 三、IS / OS / TEST
- **IS（In-Sample，样本内）**：开发调参用的历史区间。指标好看≠有效，**过拟合风险**。
- **OS（Out-of-Sample，样本外）**：开发时没碰过的历史区间，用于验证。OS Sharpe 需足够接近 IS。
- **TEST（实测）**：提交后平台用持续新数据做实时/纸面评分，决定能否拿真金白银。

流程：**IS 开发 → OS 验证 → TEST 实盘评分**。

---

## 四、提交 Do & Don't

**Do ✅**
- 先确认 OS 稳健再提交
- 做好 neutralization（行业/市值）
- 覆盖广、turnover 合理
- 确保 alpha **独特**（与已有低相关，或走 10% 豁免）
- 简单优先，避免过度复杂
- 提交前用本 checklist 逐条过

**Don't ❌**
- 别在 IS 上过拟合
- 别提交与已有 alpha **高相关**的「克隆」信号
- 别忽略 turnover（实盘会被成本吃掉）
- 别用含**前视偏差**的数据（基本面/预期时点错）
- 别跳过 OS 验证就提交
- 别超提交配额 / 触代码复用规则

---

## 五、提交前自测清单（打勾）

- [ ] IS Sharpe ≥ 阈值
- [ ] Fitness ≥ 1.0
- [ ] Turnover 在 1%~70%
- [ ] Sub-universe Sharpe 达标
- [ ] Self-correlation < 0.7（或 Sharpe 好 ≥10% → 豁免）
- [ ] Prod-correlation < 0.7
- [ ] 单票权重 / Long·Short Count 不过度集中
- [ ] Neutralization 已做、无前视偏差
- [ ] Coverage 广、无严重 2023/近期崩塌
- [ ] OS 与 IS 一致（非过拟合）

---

## 六、实战教训（见 alphas/EXP_leverage_combo.md）
- 纯 `liabilities/assets` 强但被判克隆（自相关=1）→ 必须用组合/技术面去相关。
- 去相关手段优先级：**换中性化基准 < 掺第三字段 < 加技术面（与基本面正交，必降相关）**。
- 加权 cashflow / ts_delta 版本会崩 Sharpe；revenue/assets 是「免费」去相关成分。
- **先查已提交旧 alpha 的 Sharpe**，10% 豁免线常是比硬压相关性更快的路。
