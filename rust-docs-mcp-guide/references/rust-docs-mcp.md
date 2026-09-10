# rust-docs-mcp 路由参考

## 当前核心能力

MCP 模式主要提供：

- Cache: `cache_crate`, `remove_crate`, `list_cached_crates`, `list_crate_versions`, `get_crates_metadata`, `cache_operations`
- Docs: `list_crate_items`, `search_items`, `search_items_preview`, `get_item_details`, `get_item_docs`, `get_item_source`
- Search: `search_items_fuzzy`
- Dependencies: `get_dependencies`
- Structure: `structure`

CLI one-shot 使用：

```bash
rust-docs-mcp call <tool-name> --params '<json>'
```

当前常用映射：

| MCP | CLI one-shot |
|---|---|
| `cache_crate` | `cache-crate` |
| `search_items_fuzzy` | `search-items-fuzzy` |
| `search_items_preview` | `search-items-preview` |
| `search_items` | `search-items` |
| `list_crate_items` | `list-crate-items` |
| `get_item_details` | `get-item-details` |
| `get_item_docs` | `get-item-docs` |
| `get_item_source` | `get-item-source` |
| `list_cached_crates` | `list-cached-crates` |
| `list_crate_versions` | `list-crate-versions` |
| `get_dependencies` | `get-dependencies` |
| `structure` | `structure` |

MCP 比 one-shot CLI 多出完整的 cache lifecycle 管理，例如后台任务与删除缓存能力。CLI `cache-crate` 是阻塞式。

## 推荐查询顺序

```text
版本/features
   ↓
list_crate_versions
   ↓ 未缓存
cache_crate
   ↓
search_items_fuzzy / preview
   ↓
get_item_details
   ↓
get_item_docs
   ↓ 必要时
get_item_source
```

## Token 控制

- 默认用 fuzzy/preview，不先用完整 `search_items`。
- 只获取当前问题需要的 item。
- 源码只在文档不足时读取。
- 大型 crate 首次探索可用 `structure`，但不要把整个 module tree 与所有 item 同时塞入上下文。

## 项目版本解析

推荐顺序：

1. `Cargo.lock` — 精确解析版本。
2. workspace/root/member `Cargo.toml` — dependency 声明与 feature forwarding。
3. `cargo tree -e features` — 最终 features 有歧义时使用。
4. Git/path dependencies — 保留来源信息，不错误替换成 crates.io 同名版本。

## 缓存来源

### crates.io

MCP 概念参数：

```json
{
  "crate_name": "diesel",
  "source_type": "cratesio",
  "version": "<lockfile-version>",
  "features": ["postgres"]
}
```

### GitHub

使用真实仓库 URL，并尽量与项目 tag/branch 对齐。如果 Cargo.lock 锁定 commit，而工具无法表达精确 revision，则明确该限制。

### Local

适用于当前 workspace 或本地 path dependency：

```json
{
  "crate_name": "my-crate",
  "source_type": "local",
  "path": "/absolute/or/resolvable/path"
}
```

## 诊断

只有 CLI 可用且 rust-docs-mcp 自身出现环境问题时，使用：

```bash
rust-docs-mcp doctor --json
```

不要把 `doctor` 当每次查询前的固定步骤。
