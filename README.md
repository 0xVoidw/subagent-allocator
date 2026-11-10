# subagent-allocator

读取一份已经写好的 `plan.md`，把任务拆给子代理，并为每个子代理确定角色、模型和思考强度，输出 `plan.dispatch.md`。目的是在质量和效率基本不变的前提下减少额度消耗。

## 效果示例

以 [`examples/plan-small.dispatch.md`](examples/plan-small.dispatch.md) 的“总览”表为例：

| # | 任务 | 执行者 | 档位 | 模型 | effort | 依赖 | 可并行 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 探查 oldLogger 的全部调用点 | 探查员 | T0 | Haiku 5.5 | medium | 无 | 与 4、7 |
| 2 | 按清单替换并适配 formatter | 实现者 | T1 | Sonnet 5.5 | medium | 1 | 无 |
| 3 | 为日志适配层补单元测试 | 测试员 | T1 | Sonnet 5.5 | medium | 2 | 与 5 |
| 4 | 排查设置页偶发白屏 | 调试者 | T2 | Opus 5.5 | high | 无 | 与 1、7 |

完整输出还包含执行阶段、每个子代理的角色卡、假设与注意事项，以及节省幅度的量级估计。

## 安装

### Claude Code

安装到 `~/.claude/skills/`。

- 从 Release 下载 `subagent-allocator.skill`，解压：
  ```bash
  unzip subagent-allocator.skill -d ~/.claude/skills/
  ```
- 或克隆仓库后复制目录：
  ```bash
  git clone https://github.com/0xVoidw/subagent-allocator.git
  cp -r subagent-allocator/skills/subagent-allocator ~/.claude/skills/
  ```

### pi

安装到 `~/.pi/agent/skills/`。

- 从 Release 下载 `subagent-allocator.skill`，解压：
  ```bash
  unzip subagent-allocator.skill -d ~/.pi/agent/skills/
  ```
- 或克隆仓库后复制目录：
  ```bash
  git clone https://github.com/0xVoidw/subagent-allocator.git
  cp -r subagent-allocator/skills/subagent-allocator ~/.pi/agent/skills/
  ```

### Codex

复制到 Codex 的 skills 目录，具体路径以所用版本的官方文档为准。

- 从 Release 下载 `subagent-allocator.skill`，解压到该目录。
- 或克隆仓库后，把 `skills/subagent-allocator/` 目录整体复制过去。

## 使用

在对话里说：

- “根据 plan.md 给子代理分配模型，平台 claude，取向省”
- “按这个计划安排子代理，用 Codex”
- “帮我看看这份 plan 怎么分配模型和思考强度”

技能接受三个输入：plan 文件路径（缺省找当前目录的 `plan.md`）、目标平台（`claude`、`codex` 或 `both`）、取向（`省`、`均衡` 或 `稳`，默认 `均衡`）。输出写在 plan 同目录的 `plan.dispatch.md`。

## 工作原理

技能把任务分成四个档位：T0 负责查和读，T1 负责按规格改代码和写测试，T2 负责跨模块改动和调试，T3 负责架构级决策。

拿不准时先假设 T1，再根据明确度、出错代价、可验证性、读取量和影响面上下调整。性能不够时按固定顺序升级：

1. 先补验证手段（测试或检查命令）；
2. effort 升一档，最多到 `high`；
3. 换上一档模型，effort 从该档的起步值开始。

细节见 [`skills/subagent-allocator/SKILL.md`](skills/subagent-allocator/SKILL.md)。

## 更新模型信息

模型名、价格比例和 effort 档位都在 `skills/subagent-allocator/references/` 下的两个文件里：

- `claude.md`
- `codex.md`

模型换代时只需改这两个文件，`SKILL.md` 不用动。

## 局限

- 只生成分配文档，不会自动创建或配置子代理。
- 节省幅度是估计值，实际效果取决于任务和上下文，建议对照用量统计调整。
- 参考数据截至 2026 年 11 月，模型和价格可能已经变化。

## 开发

```bash
python3 scripts/validate.py
python3 scripts/check_dispatch.py examples/plan-small.dispatch.md examples/plan-small.md
bash scripts/package.sh
```

`validate.py` 检查技能目录结构；`check_dispatch.py` 检查输出文档是否符合约定；`package.sh` 先校验再打包出 `dist/subagent-allocator.skill`。

## License

MIT，见 [`LICENSE`](LICENSE)。
