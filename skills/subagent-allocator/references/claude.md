# Claude 平台档位对照

来源：用户提供的选型文档（2026 年 11 月）。模型或价格变动时改这个文件即可，SKILL.md 不用动。

## 档位 → 模型

| 档位 | 模型 | 起步 effort | 输入/输出价（每百万 token） | 相对 T2 |
| --- | --- | --- | --- | --- |
| T0 轻量 | Haiku 5.5 | medium | $0.10 / $0.50（≤100K），$0.50 / $2.50（>100K） | 约 1/40（短提示时） |
| T1 标准 | Sonnet 5.5 | medium；写文档、表格、幻灯片用 high | $2 / $10 | 1/2 |
| T2 主力 | Opus 5.5 | medium，可升 high | $4 / $20 | 1 |
| T3 旗舰 | Fable 5.2 | medium，可升 high | $8 / $40 | 2 |

effort 档位：low、medium、high，以及 high 以上的更高档。超过 high 后再升一档的成本接近换上一档模型，一般不建议在子代理上用。

## 平台特点

- **Haiku 与其他档差距极大**（比 Sonnet 便宜约 20 倍），所以最大的节省来自把读取、搜索、跑测试这类工作推到 T0，而不是在 T1/T2 之间抠。
- **Haiku 的低价只在提示 ≤100K 时成立**。给 T0 子代理的输入要精简，超过 100K 价格变 5 倍。大目录的读取拆成多个小任务。
- **Opus 和 Fable 的 thinking 始终开启**，Sonnet 和 Haiku 默认可关。T0 的纯机械任务（分类、抽取）可以关掉。
- **提示缓存属于写入它的模型**。主会话中途换模型等于重付上下文。在阶段断点换，换之前先 `/compact` 或开新会话并附一份简短计划。子代理有独立上下文，不受影响。
- **主代理默认用 Opus 5.5 / medium**。只有计划里存在 T3 任务、且需要旗舰模型持续指挥多个子代理时，才把主代理升到 Fable 5.2。更省的做法是主代理留在 Opus，只把 T3 那一两个决策单独交给 Fable（或用 Advisor 工具咨询）。
- 交互式、有人等回复的任务：Sonnet 5.5 + low/medium。
- 计算机使用、视觉密集的长循环：Opus 5.5 / medium。

## 升级阶梯

| 当前 | 下一步 |
| --- | --- |
| Haiku medium | Haiku high → Sonnet medium |
| Sonnet medium | Sonnet high → Opus medium |
| Opus medium | Opus high → Fable medium |
| Fable medium | Fable high，再不行说明任务需要重新拆分或人工介入 |

每一级升级之前先确认子代理手里有能自检的命令。
