# Ix 可选增强策略

## 定位

Ix 是项目内部结构增强器，不是 rust-docs-mcp 的替代品。

- rust-docs-mcp：third-party / target crate intelligence。
- Ix：first-party repository intelligence。

## 探测矩阵

| 能力 | 如何判断 | 可直接执行？ | 建议 |
|---|---|---:|---|
| Ix MCP | Agent 当前工具列表中出现 Ix graph 工具 | 是 | 首选 |
| Ix CLI | `ix` 在 PATH 且可执行 | 是 | MCP 不可用时使用 |
| Ix Skill | Agent skill inventory 或常见 `skills/ix/SKILL.md` | 不一定 | 只说明有指导层，仍检查底层工具 |

常见 Ix MCP server 由 `ix mcp` 启动，官方注册名常见 `ix-memory`。不要依赖固定 namespace；以工具能力识别为主。

## 何时启用

推荐启用：

- “这个 Diesel/SQLx API 在我的项目哪里被包装/调用？”
- “如果按新版 API 改这个 repository，会影响哪些模块？”
- “这个 PgPool/PgConnection/transaction 从哪里创建并一路传到这里？”
- “某 crate 类型穿过哪些 service/handler/module？”
- “需要理解调用链、blast radius 或 first-party architecture。”

不启用：

- “Diesel 这个 trait 怎么用？”
- “SQLx Transaction 当前版本签名是什么？”
- “某 crate feature 做什么？”
- “某 API 在 0.7 与 0.8 有何不同？”
- 只需要 external crate source/docs。

## Ix MCP 优先

如果 MCP 工具可用，优先使用，因为输出天然结构化，且不需要 shell 解析。

典型意图路由：

- component context → `explain` / `context`
- flow → `trace`
- change blast radius → `impact`
- relation lookup → `search` / `callers` / `callees` / imports 等

不要假设所有宿主暴露的工具名完全一致；按语义选择。

## Ix CLI fallback

如果没有 MCP 但 `ix` CLI 可用：

```bash
ix explain <symbol> --format llm
ix context <symbol> --max-entities 20 --format llm
ix trace <flow-or-symbol> --format llm
ix impact <symbol> --format llm
```

机器串联或需要 entity id 时优先 `--format json`。

只在 graph 确实需要更新时执行 `ix map --silent`。本 Skill 不负责自动安装 Ix 或自动启动 Docker/backend。

## Ix Skill 的角色

若官方 `ix` Skill 已加载：

- 可借用它的命令路由、output format、troubleshooting 方法。
- 不复制其职责。
- 不因为 Skill 存在就强制 Ix。
- 如果 Ix Skill 与本 Skill 的 Ix 细节冲突，优先遵循已安装且版本更新的 Ix Skill；本 Skill 只保留“可选增强”的边界。

## 决策伪代码

```text
ix_capability = detect(ix_mcp, ix_cli, ix_skill)

if not task.needs_project_structure:
    use_ix = false
elif not (ix_mcp or ix_cli):
    use_ix = false
elif project_evidence_already_sufficient and ix_cost > expected_gain:
    use_ix = false
else:
    use_ix = true

if use_ix:
    interface = ix_mcp if available else ix_cli
```

## 禁止事项

- 不 map `~/.rust-docs-mcp/cache` 来代替 rust-docs-mcp。
- 不把第三方 crate 的 Ix graph 当作版本权威文档。
- 不因 Ix 不可用而阻断普通 rust-docs-mcp 查询。
- 不自动执行 `ix mcp install`、安装 Ix、安装 Docker 或改 MCP 配置。
