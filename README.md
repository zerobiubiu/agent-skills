# agent-skills

个人使用的 coding agent skills 集合，目录结构遵循 Agent Skills 约定：每个技能一个目录，内含 `SKILL.md`（带 YAML frontmatter 的 `name` / `description`），可选 `references/` 与 `scripts/`。

在 [omp / oh-my-pi](https://github.com/badlogic/oh-my-pi) 下实际使用并验证，同样适用于其他读取 `SKILL.md` 的 agent harness（Claude Code、Codex 等）。

## 技能清单

| 技能 | 触发场景 |
| --- | --- |
| [`ix`](ix/SKILL.md) | 代码库结构性问题：符号定义、调用链追踪、变更影响面、导入关系、架构坏味道。驱动 Ix CLI 查询持久化代码图谱，替代 grep 猜测 |
| [`rust-docs-mcp-guide`](rust-docs-mcp-guide/SKILL.md) | 获取版本准确的 Rust crate API / rustdoc / 源码 / 依赖信息。优先走 rust-docs MCP，降级到 CLI；可选叠加 Ix 做项目内推理 |
| [`pg-aiguide-mcp-usage`](pg-aiguide-mcp-usage/SKILL.md) | PostgreSQL / TimescaleDB / PostGIS / pgvector 的建表选型、索引、hypertable、向量检索、零停机迁移 |
| [`nushell-style`](nushell-style/SKILL.md) | 编写任何 Nushell 代码时的写法约束与语法陷阱。与执行方式无关，MCP、`nu -c`、`.nu` 脚本均适用 |
| [`nushell-mcp-usage`](nushell-mcp-usage/SKILL.md) | 配置与调用 nushell MCP：stdio 接入验证、三工具分工、`$history` 索引复用、安全边界 |
| [`herdr`](herdr/SKILL.md) | 控制 Herdr 终端复用器的 pane / tab / workspace（仅在用户明确提及 Herdr 时使用） |

`nushell-style` 与 `nushell-mcp-usage` 按触发面拆分：前者管「怎么写」，后者管「怎么调」，双向交叉引用。

## 使用方式

克隆到 agent 读取的 skills 目录：

```bash
# omp / oh-my-pi
git clone https://github.com/zerobiubiu/agent-skills.git ~/.omp/agent/skills

# 通用 agents 目录
git clone https://github.com/zerobiubiu/agent-skills.git ~/.agents/skills
```

或只取单个技能——每个技能目录自包含，直接复制即可。

## 外部依赖

部分技能依赖外部工具，不装则技能不可用：

- `ix` — Ix CLI + 本地后端，见 `ix/scripts/bootstrap.sh` / `bootstrap.ps1`
- `rust-docs-mcp-guide` — `rust-docs-mcp` CLI 或对应 MCP server
- `pg-aiguide-mcp-usage` — pg-aiguide MCP server
- `nushell-mcp-usage` — nushell + 其 MCP 接入（`nu --mcp`）
- `herdr` — Herdr 运行环境（`HERDR_ENV=1`）

## 许可

MIT，见 [LICENSE](LICENSE)。
