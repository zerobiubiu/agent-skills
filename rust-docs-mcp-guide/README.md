# rust-docs-mcp-guide

一个以 `rust-docs-mcp` 为主的 Rust crate intelligence 使用指导 Skill，并将 Ix 作为自动探测、按需启用的可选 first-party codebase 增强层。

核心边界：

- `rust-docs-mcp` 始终负责 crate API / rustdoc / source / dependency / module facts。
- Ix 只在当前问题需要项目内部结构、调用流或影响范围时启用。
- Ix 不可用不阻断主流程。
- 不自动安装任何工具或修改 MCP 配置。

入口：`SKILL.md`
