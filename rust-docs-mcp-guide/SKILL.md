---
name: rust-docs-mcp-guide
description: "Use rust-docs-mcp to obtain version-accurate Rust crate API, rustdoc, source, dependency, and module-structure evidence. Prefer the rust-docs MCP when available, fall back to the rust-docs-mcp CLI when necessary, and optionally augment project-internal reasoning with Ix after automatically detecting Ix MCP, CLI, or Skill capabilities. Ix is never required and must not replace rust-docs-mcp for external crate facts."
license: MIT
metadata:
  version: 1.0.0
  primary_tool: rust-docs-mcp
  optional_enhancement: ix
---

# rust-docs-mcp 使用指导

## 目标

使用 `rust-docs-mcp` 获取**项目实际 Rust crate 版本**对应的 API、rustdoc、源码、依赖和模块结构事实，避免依赖模型记忆猜测当前 API。

本 Skill 的主工具始终是 `rust-docs-mcp`。Ix 只作为可选的**项目内部代码结构增强层**：当任务同时涉及“这个 crate 本身怎么工作”和“当前项目怎样使用它”时，才考虑启用 Ix。

## 核心原则

1. **版本优先**：能从 `Cargo.lock` 得到精确版本时，不使用 `latest` 或模糊版本代替。
2. **Feature 一致**：需要生成/缓存 crate 文档时，优先使用项目实际启用的 Cargo features。
3. **事实分层**：
   - `rust-docs-mcp`：外部 crate 的 API / docs / source / dependency / module facts。
   - 项目文件与编译结果：当前仓库真实使用方式。
   - Ix（可选）：当前项目的 symbol / caller / callee / flow / impact 等结构关系。
4. **渐进查询**：先轻量定位，再读取细节；避免直接拉取大段完整文档。
5. **不强制 Ix**：没有 Ix、Ix 未初始化、Ix 对当前问题无增益时，正常继续完成任务。
6. **不自动安装**：能力缺失时只降级，不自行安装 `rust-docs-mcp`、Ix、MCP、Skill、Docker 或其他依赖，除非用户明确要求。
7. **不把 Ix 当 crate 文档源**：即使 Ix 能扫描第三方源码，也优先用 `rust-docs-mcp` 查询外部 crate；不要为了回答 crate API 问题去 map `~/.rust-docs-mcp/cache`。

## 触发场景

在以下任务中使用本 Skill：

- 查询某 Rust crate 当前/指定版本的 API、trait、struct、enum、function、macro 或 module。
- 需要确认方法签名、trait bound、feature gate、模块路径或版本差异。
- 需要读取 crate rustdoc 或源码来解释行为。
- 需要分析 crate 的直接/传递依赖或模块结构。
- Agent 对某个 Rust API 不确定，准备凭记忆猜测时。
- 修改项目中的 SQLx、Diesel、Tokio、Axum、Tonic、Serde 等依赖相关代码，需要先确认项目实际 crate 版本的事实。
- 用户明确要求使用 `rust-docs-mcp`。

不用于纯 Rust 语言基础问题、与 crate 无关的普通算法问题，或用户已经提供了足够且可信的目标 API 文档内容时。

## 第 0 阶段：能力探测

每次首次需要本 Skill 时做一次轻量探测；同一任务内复用结果，不要反复探测。

### A. 探测 rust-docs-mcp

按以下优先级确定调用通道：

1. **已连接的 rust-docs MCP**：如果当前 Agent 工具列表中存在与以下能力等价的工具，视为 MCP 可用：
   `cache_crate`、`list_cached_crates`、`list_crate_versions`、`search_items_fuzzy`、`search_items_preview`、`get_item_details`、`get_item_docs`、`get_item_source`、`get_dependencies`、`structure`。
2. **CLI fallback**：若没有 MCP，检查 `rust-docs-mcp` 是否可执行。可运行 `scripts/detect_local_tools.py`，或使用当前 shell 的命令发现能力。
3. 两者均不可用：明确说明缺少 `rust-docs-mcp` 运行能力；不要伪造查询结果。若任务仍可由项目源码/已有文档完成，可降级继续。

优先使用 MCP；只有 MCP 不可用或当前宿主无法调用时才使用 CLI。CLI one-shot 对应关系见 `references/rust-docs-mcp.md`。

### B. 探测 Ix（可选）

Ix 的探测只决定是否有资格成为增强源，不代表一定启用。

按以下顺序记录能力：

1. **Ix MCP**：当前 Agent 工具列表中是否存在 Ix graph 工具，例如 `overview`、`explain`、`context`、`trace`、`impact`、`search`、`callers`、`callees` 等；服务名可能表现为 `ix-memory` 或宿主自定义 namespace。
2. **Ix CLI**：`ix` 是否在 PATH；如有需要确认 MCP server 能力，可检查 `ix mcp --help`，但不要为了本 Skill 自动执行 `ix mcp install`。
3. **Ix Skill**：当前 Agent 是否已经加载/可调用名为 `ix` 的 Skill。若宿主没有 Skill inventory，可把下列文件位置作为弱信号：
   - `~/.agents/skills/ix/SKILL.md`
   - `~/.claude/skills/ix/SKILL.md`
   - 项目内 `.agents/skills/ix/SKILL.md`
   - 项目内 `.claude/skills/ix/SKILL.md`

**探测优先级不等于使用优先级。** 如果同时存在 Ix MCP 和 CLI，优先使用 MCP 的结构化工具；如果只存在 Ix Skill，该 Skill 可能仍依赖 CLI，因此仍需确认其底层执行能力可用。

## 第 1 阶段：解析项目真实依赖

当问题与当前项目有关时，先确定：

1. crate 名称；
2. `Cargo.lock` 中解析出的精确版本；
3. 当前 workspace/member；
4. `Cargo.toml` 中直接启用的 features；
5. 是否存在 feature forwarding / workspace dependency 继承；
6. 必要时用 `cargo tree -e features` 辅助确认最终 feature 集。

若只是研究一个与项目无关的指定 crate/version，可直接使用用户给出的版本。

**不要因为 `Cargo.toml` 写了 `"2"` 就把查询版本当成 `2.x latest`；优先以 lockfile 的解析结果为准。**

## 第 2 阶段：确认缓存

优先调用：

1. `list_crate_versions`：查看目标版本是否已缓存；
2. 必要时 `list_cached_crates` / metadata 工具；
3. 未缓存时才调用 `cache_crate`。

缓存时：

- crates.io crate：使用 `source_type = cratesio` + 精确 `version`。
- Git dependency：优先使用实际 Git URL + tag/branch；若项目锁定 commit 而工具接口不能精确表达该 revision，必须说明证据边界，不要假装是完全相同源码。
- path/local workspace crate：使用 `source_type = local` + 实际路径。
- features：有明确项目 feature 集时显式传递；不要无理由使用 `--all-features` 语义。

MCP 的 `cache_crate` 可能异步返回任务；需要时使用缓存任务管理工具等待/检查完成。CLI `call cache-crate` 是阻塞式。

## 第 3 阶段：渐进式 crate 查询

默认查询梯度：

### 3.1 定位

优先：

- `search_items_fuzzy`：不知道精确名称、可能有拼写差异时。
- `search_items_preview`：知道关键词，希望低 token 定位候选 item 时。
- `list_crate_items`：需要按 kind/path 浏览时。

避免一上来使用返回完整文档的 `search_items`，除非目标非常窄且结果数量可控。

### 3.2 结构事实

定位到目标 item 后调用 `get_item_details`，优先确认：

- canonical path / module path；
- item kind；
- signature；
- fields / variants / methods；
- trait / impl 相关结构信息。

如果用户问“这个 API 到底怎么调用”，先以 details 的签名事实约束推理。

### 3.3 文档语义

需要解释官方意图、使用条件、约束或示例时调用 `get_item_docs`。

不要把 rustdoc 的说明与自己的工程建议混为一谈；回答中区分：

- crate 文档明确说明；
- 从源码/类型关系推导；
- Agent 的工程建议。

### 3.4 源码下钻

只有在以下情况才调用 `get_item_source`：

- rustdoc 不足以解释行为；
- 需要确认实现细节；
- trait/blanket impl/内部 dispatch 关系不清；
- 用户明确要求看实现。

不要为了“更全面”默认读取大量源码。

### 3.5 依赖与模块

- `get_dependencies`：回答 crate 依赖、子 crate、直接/传递依赖相关问题。
- `structure`：首次探索大型 crate 或需要理解 module hierarchy 时。

## 第 4 阶段：决定是否启用 Ix

只有同时满足以下条件时才启用 Ix：

### 必要条件

1. 至少存在一种**可实际执行**的 Ix 能力：Ix MCP 或可工作的 Ix CLI；仅发现 Ix Skill 文件但底层工具不可用，不算可执行能力。
2. 当前任务包含**项目内部结构问题**，例如：
   - 项目哪里使用这个 crate/API；
   - 某 wrapper / repository / service 如何传递连接、事务或对象；
   - callers / callees / imports / dependency path；
   - 一个依赖 API 修改会影响项目哪些模块；
   - 数据/调用流程如何穿过多个项目模块；
   - 需要在修改前定位 blast radius。

### 不启用 Ix 的情况

- 只是询问 crate 自身 API / rustdoc /源码。
- 只是比较 crate 版本的 API。
- 只是查询 feature、trait signature 或 dependency tree。
- 项目很小，直接文件证据已经充分，Ix 不会减少歧义或上下文成本。
- Ix graph 未建立/明显过期，而当前任务不值得为此进行 map。
- 使用 Ix 会引入明显高于收益的启动、映射或上下文成本。

### Ix 启用后的职责

Ix 仅回答**first-party project context**：

- `explain` / `context`：项目内 symbol/module 的结构上下文；
- `trace`：项目内部流程；
- `impact`：修改项目代码时的影响范围；
- `search` / `callers` / `callees` / imports 等：项目内关系定位。

crate 本身的 API、文档和实现仍以 `rust-docs-mcp` 为主。

### Ix 接口选择

1. Ix MCP 可用：优先 MCP。
2. 否则 Ix CLI 可用：使用 CLI；优先 `--format llm` 阅读，机器串联时用 `--format json`。
3. 只有 Ix Skill 可用：加载它来指导 Ix；但不要把“Skill 存在”误判为 CLI/MCP 已经可执行。
4. Ix 完全不可用：静默降级到 `rust-docs-mcp + 项目文件/编译证据`，除非 Ix 缺失会阻断用户明确要求的 Ix 分析。

详细路由见 `references/ix-optional-enhancement.md`。

## 第 5 阶段：组合证据

需要同时使用两者时，按以下方向组合：

```text
Ix / 项目源码                       rust-docs-mcp
“项目怎么使用它”                   “这个 crate 本身是什么”
        │                                  │
        ├─ 调用点 / 包装层                 ├─ API 签名
        ├─ 事务/对象传递                   ├─ rustdoc
        ├─ flow / impact                  ├─ trait / impl
        └─ first-party architecture       └─ source / deps
                 \                         /
                  └────── 工程结论 ───────┘
```

若两边看似冲突：

- crate API 事实以目标版本的 rust-docs/source 为准；
- 项目使用事实以项目实际源码、编译结果和最新 Ix graph 为准；
- Ix 低置信度或 graph 过期时，不把结果当确定事实，必要时刷新 graph；
- 编译器/测试结果可以推翻纯静态推测。

## SQLx / Diesel 推荐流程

针对 SQLx、Diesel 这类版本和 trait 关系敏感的 crate：

1. 从 `Cargo.lock` 确定精确版本；
2. 从 Cargo manifests / feature tree 确定 features；
3. 检查目标 crate/version 是否已缓存；
4. fuzzy/preview 定位 symbol；
5. `get_item_details` 确认签名和 trait 结构；
6. `get_item_docs` 获取 rustdoc 语义；
7. 必要时读取源码；
8. 如果问题涉及“当前项目如何使用此 API”，再探测并按需启用 Ix；
9. 最终用 `cargo check` / 测试验证编译与行为（如果任务允许执行）。

## 失败与降级

- MCP 调用失败：尝试同能力 CLI one-shot（若可用）。
- CLI 不可用但 MCP 可用：继续 MCP，不要求 CLI。
- cache 失败：先查看错误；必要时运行 `rust-docs-mcp doctor --json`（CLI 可用时）。
- 指定 nightly / rustdoc JSON 不兼容：报告工具环境问题，不编造文档结果。
- Ix backend 不可达：跳过 Ix；只有用户明确要求 Ix 时才把它作为阻塞项。
- Ix graph 过期：如果 Ix 对当前任务确实有价值且允许执行，只做必要刷新；不要因为本 Skill 存在就强制 `ix map`。

## 输出要求

回答应优先给结论，再给必要证据。涉及版本/API 时至少说明：

- crate 名称；
- 实际/目标版本；
- 使用了 rust-docs-mcp 的哪类事实（details/docs/source/dependencies/structure）；
- 若启用了 Ix，说明它补充的是哪一类项目内部证据。

不要宣称“使用了 Ix”除非实际调用过 Ix MCP/CLI（或明确调用了可执行的 Ix Skill 流程）。

## References

- `references/rust-docs-mcp.md` — MCP/CLI 工具路由、缓存与查询策略。
- `references/ix-optional-enhancement.md` — Ix 自动探测、启用条件、MCP/CLI/Skill 优先级。
- `references/examples.md` — SQLx、Diesel 与通用 Rust crate 示例流程。

## Scripts

- `scripts/detect_local_tools.py` — 只读探测本机 `rust-docs-mcp` / `ix` CLI 与常见 Ix Skill 文件位置；输出 JSON，不安装、不修改配置、不启动服务。
