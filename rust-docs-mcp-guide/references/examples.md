# 示例工作流

## 示例 1：Diesel trait 使用问题，不需要 Ix

问题：当前项目的 `diesel` 版本里 `RunQueryDsl::execute` 怎么用？

1. 从 `Cargo.lock` 得到 Diesel 精确版本。
2. 从 manifest 得到 `postgres` 等 features。
3. rust-docs-mcp 检查缓存；必要时缓存。
4. `search_items_fuzzy("RunQueryDsl")`。
5. `get_item_details` 确认 trait/method 签名。
6. `get_item_docs` 读取语义。
7. 必要时 source 下钻。
8. 不启用 Ix，因为问题没有 first-party structural component。

## 示例 2：SQLx Transaction 在项目中怎么传递，启用 Ix

问题：项目里 `sqlx::Transaction<Postgres>` 为什么传到 service 后无法继续执行查询？

1. rust-docs-mcp：确认项目 SQLx 精确版本下的 `Transaction`、`Executor`、`Acquire` 等 API。
2. 探测 Ix。
3. 如果 Ix MCP/CLI 可执行：
   - 定位 transaction 创建点；
   - trace/context 它进入 repository/service 的路径；
   - 找到项目 wrapper/type alias；
4. 组合 external API 事实 + first-party dataflow。
5. 最后用 `cargo check` 验证修复。

## 示例 3：crate 升级影响

问题：把 Diesel A 升到 B 会影响哪些项目代码？

1. rust-docs-mcp 分别缓存/查询 A 与 B 的目标 API，确认真实 API 差异。
2. 如果任务涉及当前仓库 blast radius 且 Ix 可执行：用 Ix `impact` / `search` / callers 等定位项目依赖点。
3. Ix 不可用时，用项目搜索和编译器 diagnostics 降级完成。

## 示例 4：纯 crate 架构探索

问题：SQLx 为什么拆成 `sqlx-core` / `sqlx-postgres`？

1. `get_dependencies(sqlx)`。
2. 必要时分别缓存相关子 crate。
3. `structure` 查看 module hierarchy。
4. docs/source 下钻。
5. 不启用 Ix。
