# 04 · 数据探索（Data Explorer 实操 + 字段清单模板）

---

## 一、Data Explorer 是什么
BRAIN 平台内置于「Research → Data」的字段探查工具。不用写回测，直接看某个数据字段**长什么样、覆盖多广、有没有预测力**。是写 alpha 前的必做第一步。

## 二、看哪些指标（核心 4 项）
| 指标 | 看什么 | 决策 |
|---|---|---|
| **Coverage** | 非空的股票占比 | 太低（如 <50%）别上，会拖累子池 Sharpe |
| **Null %** | 空值比例 | 高空值需 `is_null` / `ts_delay` 处理 |
| **与 `fwd_return` 相关性** | 对未来收益的预测力（常取 rank IC） | 越高越有 alpha 潜力 |
| **Decay** | 预测力衰减速度 | 衰减慢=信号更持久、更值钱 |

辅助：时序图（看异常/断层）、横截面分布（看是否需 winsorize）、分年 Sharpe。

## 三、数据字段分类与结构差异
| 类别 | 例子 | 频率/稠密度 | 注意 |
|---|---|---|---|
| **Market（行情）** | close, volume, adv20, returns | 每日、稠密、全覆盖 | 最直接，前视风险最低 |
| **Fundamentals（基本面）** | eps, book_value, liabilities, assets, cashflow, revenue | 季/年度、稀疏、point-in-time | 注意报告滞后，别偷看未来 |
| **Estimates（预期）** | 分析师盈利预测 | 稀疏、易前视 | 时点必须用对 |
| **Alternative（另类）** | 情感、宏观、搜索量 | 来源杂、覆盖不均 | 先查 coverage |
| **Reference（公司行动）** | 分红、拆细、复权 | 事件型 | 影响复权准确 |

## 四、常用探索表达式
- 测预测力：`correlation(field, fwd_return(20), 60)`  （字段与 20 日后收益的 60 日滚动相关）
- 覆盖率：`coverage(field)` / 非 null 计数
- 横截面分布：`rank(field)` / `zscore(field)`
- 时序稳定：`ts_mean(field, 252)` / `ts_std_dev(field, 252)`
- 行业内位置：`group_rank(field, sector)`

**探查铁律**：先 coverage/null% → 再与 fwd_return 相关 → 最后看 decay。

## 五、字段清单模板（探索时复制填写）
| 字段名 | 类别 | Coverage | Null% | 与fwd_return相关 | Decay | 备注 |
|---|---|---|---|---|---|---|
| （例）revenue/assets | Fundamentals | 92% | 8% | 0.03 | 中 | 资产周转率，质量因子 |
| | | | | | | |
| | | | | | | |

## 六、示例表达式文件（见 alphas/）
- `alphas/momentum.txt` —— 60 天价格动量
- `alphas/reversal.txt` —— 1 天反转
- `alphas/quality.txt` —— 质量因子组合

三个文件**内容只有一行表达式**，可直接全选复制粘贴进 BRAIN 编辑器。建议设置：USA/TOP3000、Delay=1、Neutralization=Subindustry（动量/反转类可试 Industry）。
