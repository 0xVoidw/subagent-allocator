# Codex 平台档位对照

来源：用户提供的选型文档（2026 年 11 月）。模型或价格变动时改这个文件即可，SKILL.md 不用动。

## 档位 → 模型

| 档位 | 模型 | 模型 ID | 起步 effort | 输入/输出价（每百万 token） | 相对 T2 |
| --- | --- | --- | --- | --- | --- |
| T0 轻量 | GPT-6 Luna | `gpt-6-luna` | low（分类、抽取）；high（检索、读日志） | $0.10 / $0.50 | 1/20 |
| T1 标准 | GPT-6.1 Terra | `gpt-6.1-terra` | medium | $1 / $5 | 1/2 |
| T2 主力 | GPT-6.1 Sol | `gpt-6.1-sol` | medium，可升 high | $2 / $10 | 1 |
| T3 旗舰 | GPT-6 Astra | `gpt-6-astra` | medium；从 Sol 升上来时用 low 起步 | $10 / $50 | 5 |

effort 档位：low、medium、high、xhigh、max。

## 平台特点

- **Astra 是 Sol 的 5 倍价**，跨度比 Claude 那边的 2 倍大得多。进 T3 的门槛要更严：Sol 开到 high 甚至 xhigh 通常仍比 Astra medium 便宜，先试前者。
- **Luna 开高 effort 是官方推荐用法**。需要多步检索、跨多处收集上下文、按明确约束排序的任务，用 Luna + xhigh/max，而不是升到 Terra。这是通用规则"effort 最多升到 high"在 Codex 上的例外，只适用于 T0。
- **Terra 比 Sol 和 Astra 快 3 倍以上**，视觉推理接近 Sol。UI 还原、截图排错、常规 computer use、有人等结果的任务优先 Terra / medium。
- **272K 阶梯计费**：单次请求上下文超过 272,000 token 时，整个请求按长上下文费率算（输入 2 倍，输出约 1.5 倍）。任何子代理预计会超过这个量，就拆任务或先让 Luna 做摘要。主会话同理，保持精简。
- **会话中途改 effort 或增减工具不会破坏缓存**。所以同一个模型的任务可以连着做、逐个调 effort（规划用 high，后续小改降到 low），不必为了调 effort 另开会话。
- **批量任务的省钱模式**：先用 Luna 或 Terra 全量跑一遍，只把没通过自动检查的失败项交给 Sol 重试。
- **Astra 比较谨慎**，做完第一版会停下来等审查。希望它跑完闭环，要在角色卡的约束里明确授权（例如"测试使用一次性数据，可直接运行并修复本次改动引起的报错，无需逐步确认"）。
- **主代理默认用 Sol / medium**。只有计划里有架构级决策时才考虑 Astra 做主控。
- 子代理的模型绑定写在 `.codex/config.toml` 或子代理配置里；角色卡的四项（目标、上下文、约束、完成标准）对应官方推荐的四要素提示词。

## 升级阶梯

| 当前 | 下一步 |
| --- | --- |
| Luna low | Luna high → Luna xhigh/max → Terra medium |
| Terra medium | Terra high → Sol medium |
| Sol medium | Sol high → Sol xhigh → Astra low |
| Astra low/medium | Astra xhigh，再不行说明任务需要重新拆分或人工介入 |

每一级升级之前先确认子代理手里有能自检的命令。
