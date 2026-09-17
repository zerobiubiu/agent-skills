---
name: serena
description: "驱动 Serena MCP（符号级检索/编辑）时使用 —— 项目激活、find_symbol/name_path 寻址、符号级编辑与 rename_symbol/safe_delete_symbol 重构、跨上下文工具面差异、记忆（mem 引用）机制，以及在 omp 下启动/接线和常见故障的定位。当任务涉及 Serena、semantic code tools、name_path、或「用 serena 分析/改代码」时使用。"
---

# Serena 使用指导

Serena MCP 把 LSP（或 JetBrains）能力暴露成符号级工具：按 `name_path` 定位、只读符号体、按符号边界编辑与重命名。目标是**少读文件、按结构定位**，而不是让 agent 多几个 grep。

本机实测环境：`serena 1.7.0`（`uv tool install -p 3.13 serena-agent`），MCP SDK 1.28.1，LSP 后端，Windows。下文标注「实测」的行为均来自 1.7.0 + 项目级 stdio 会话的实跑。

## 0. 先确认工具是否真的挂上了

Serena 在 omp 里是**项目级 stdio MCP**，配置在 `~/.omp/agent/mcp.json`：

```json
"serena": {
  "type": "stdio",
  "command": "serena",
  "args": ["start-mcp-server", "--context", "claude-code", "--project-from-cwd", "--open-web-dashboard", "false"],
  "enabled": true
}
```

调用前先看工具列表里有没有 `mcp__serena_*`。**没有就是没挂上**，不要去猜 `find_symbol` 的参数——会话根本没这个工具。（实测：本机 omp 会话中该 server 未出现在 mounted devices 里，只有 nushell / pg-aiguide。）

手工验证通道（脱离 omp 也能证明 server 活着）：

```bash
printf '%s\n' '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"probe","version":"0"}}}' \
  | serena start-mcp-server --context claude-code --project-from-cwd --open-web-dashboard false
```

返回 `serverInfo.name = "Serena"` 即握手成功。**注意 `serverInfo.version` 报的是 mcp SDK 版本（本机 `1.28.1`），不是 Serena 版本**；要 Serena 版本用 `serena --version`（实测 1.7.0）或看日志里的 `Starting Serena server (version=...)`。别把 1.28.1 当成 Serena 版本去比对文档。

## 1. 上下文（context）决定工具面——先搞清你在哪个

`--context` 在**启动时固定**，中途不可改。实测四种上下文的暴露工具数：

| context | 工具数 | 被排除的工具 |
|---|---|---|
| `desktop-app` | 30 | 无（默认，全量） |
| `agent` | 29 | `initial_instructions` |
| `codex` | 24 | `create_text_file` `read_file` `execute_shell_command` `replace_content` `find_file` `list_dir` |
| `ide` | 23 | `create_text_file` `read_file` `execute_shell_command` `find_file` `list_dir`（保留 `search_for_pattern`）+ 单项目排除 `activate_project` `get_current_config` |
| `claude-code` | 22 | `create_text_file` `read_file` `execute_shell_command` `find_file` `list_dir` `search_for_pattern` + 单项目排除 `activate_project` `get_current_config` |

（`ide` / `claude-code` 的数字为**已激活项目**时实测；无活跃项目时单项目排除不生效，会多出 `activate_project`、`get_current_config` 两个。）

要点：

- `ide`、`claude-code` 等是 **single-project 上下文**：启动时若指定了项目，`activate_project` 与 `get_current_config` 会被排除，**换了工具就换不回项目**。
- `ide-assistant` 这个名字**已废弃**，会告警并静默映射到 `claude-code`（实测 stderr：`Context name 'ide-assistant' is deprecated and has been renamed to 'claude-code'`）。写配置时直接用 `claude-code`。历史文档/cmd 里出现 `ide-assistant` 不要照抄。
- 想让 Serena 自己读文件/跑 shell 才用 `desktop-app`；用 agent 客户端（Claude Code / omp / Codex）时选对应上下文，让文件与 shell 操作交回宿主。
- `serena context list` 可列出实际可用名（本机 16 个内置 context）。自定义 context 放用户目录。

## 2. 项目激活：没有激活项目 = 几乎所有工具报错

实测（1.7.0，无活跃项目时逐个调用）——仍可用的工具只有：`initial_instructions`、`open_dashboard`、`activate_project`（三者已实调验证通过），以及源码中带 `ToolMarkerDoesNotRequireActiveProject` 标记的 `remove_project`、`list_queryable_projects`、`query_project`（后者需 `query-projects` 模式）。

**其余全部报错**，包括容易被误认为「本地/只读」的那些：`list_memories`、`read_memory`、`onboarding`、`get_current_config`、`find_symbol`、`replace_in_files` 实测均为：

```
Error executing tool get_symbols_overview: No active project.
Ask the user to provide the project path or to select a project from this list of known projects: ['serena-proj']
```

（实测原文，注意它会把**已注册项目名**一并列出——这就是给 `activate_project` 用的候选。）

激活方式二选一：

- 启动参数：`--project <路径|名字>`，或 `--project-from-cwd`。后者从 cwd 向上找最近的含 `.serena/project.yml` 或 `.git` 的祖先目录；**找不到就不激活，只打一条 WARNING，server 照常启动**（实测：在无 `.git` 的临时目录启动，`initialize` 成功但全程无项目）。所以「server 起来了」≠「项目激活了」。
- 运行时：调 `activate_project`，传路径或已在 `serena_config.yml` 里注册的项目名。

首次激活**会在项目里落文件**（实测一次激活的产物）：

```
<proj>/.serena/project.yml          # 项目配置（project_name 默认取目录名）
<proj>/.serena/project.local.yml    # 本地覆盖，.serena/.gitignore 默认忽略它
<proj>/.serena/.gitignore           # 内容: /cache 与 /project.local.yml
<proj>/.serena/memories/            # 记忆目录
<proj>/.serena/cache/<lang>/…       # 符号缓存，会增长
```

工作区不是干净仓库时，先确认这些文件是否该进版本库（`.serena/project.yml` 与 `memories/` 建议提交，`cache/` 已被自带 gitignore 挡掉）。

## 3. 符号寻址：`name_path` 是核心概念

Serena 用 `name_path`（层级路径）+ `relative_path`（项目内相对文件路径）定位符号，**不是**行列号。

- `name_path` 用 `/` 嵌套：`Box/put`、`Foo/__init__`。
- `relative_path` 是相对**项目根**的路径，工具返回的也是这个口径，可直接回灌给下一个工具。

标准读法（省 token 的关键）：

1. `get_symbols_overview(relative_path)` —— 只看某文件的顶层结构，不含函数体。实测返回极小：
   `{"Function": ["greet"], "Class": ["Box"]}`
2. `find_symbol(name_path_pattern, include_body=True, depth=?)` —— 按需取体。
3. `find_referencing_symbols(name_path, relative_path)` —— 找引用/调用者。

`find_symbol` 实测要点：

- 必填只有 `name_path_pattern`（全局搜，可省 `relative_path`）；给了 `relative_path` 就变成该文件内局部搜。
- 返回是 JSON 数组，每项含 `name_path` / `kind` / `relative_path` / `body_location{start_line,end_line}` / `body`。
- **行号是 0-based**（系统提示词原文：`Line numbers returned by Serena's tools are 0-based!`）。
- `include_body=False` + `depth=1` 可先列成员再决定读哪个体；不知道确切名字时用 `substring_matching`。

## 4. 编辑：优先符号级，其次文件级

上下文决定你能不能自己改文件：

- `ide` / `claude-code` / `codex` 上下文里 `read_file` / `create_text_file` 已被排除，**只能**用 Serena 的编辑工具。
- `desktop-app` / `agent` 才有全量文件工具。

按操作选工具：

| 目的 | 工具 | 必填参数（实测） |
|---|---|---|
| 替换整个符号定义 | `replace_symbol_body` | `name_path` `relative_path` `body` |
| 在符号后插入 | `insert_after_symbol` | `name_path` `relative_path` `body` |
| 在符号前插入 | `insert_before_symbol` | `name_path` `relative_path` `body` |
| 文件内替换（支持 regex） | `replace_content` | `relative_path` `needle` `repl` `mode` |
| 跨文件批量替换 | `replace_in_files` | `needle` `repl` `mode`（+ `dry_run`、`paths_include_glob`） |
| 正则搜索 | `search_for_pattern` | `substring_pattern` |

要点：

- `replace_content` / `replace_in_files` 的 `mode` **是必填**（`literal` 或 `regex`）。实测 `replace_content` 成功返回纯文本 `OK`；`search_for_pattern` 返回 `{"file": ["  行号:匹配行", …]}`（含匹配行文本，不是只有位置）。
- `replace_symbol_body` **只给新符号体，不含签名**——签名要一致就别改；要改签名得连签名一起写进 `body`。`insert_*_symbol` 的 docstring 明确说**不要**用它插到赋值/字段之后。
- 改完代码类型可能立刻失衡时，顺手 `get_diagnostics_for_file(relative_path)`（可选 `start_line`/`end_line`/`min_severity`）拿编译/静态检查结果。

## 5. 重构：`rename_symbol` 与 `safe_delete_symbol` 是引用感知的

- `rename_symbol(name_path, relative_path, new_name)`——跨整个代码库改所有引用（含导入/覆写），不用自己 grep。
- `safe_delete_symbol(name_path_pattern, relative_path)`——**无引用才删**，有引用则返回引用列表而不删。

这两个是 Serena 相对宿主 grep/edit 的**主要增量**：一次调用即原子完成，成功后**不要再重读文件或跑全套测试去复核**（重试一次纯浪费）。反之，`replace_symbol_body` 这类是文本级替换，只改你指定的那个符号，不保证引用方一致。

## 6. 记忆与 onboarding

- 项目记忆落 `<proj>/.serena/memories/`，全局记忆走 `global/` 前缀（默认 `~/.serena/memories/global/`），可跨项目共享。
- 名字用 `/` 分组主题（如 `modules/frontend`），`list_memories(topic=…)` 可按主题筛。
- 记忆之间用反引号包 `` `mem:NAME` `` 互相引用：`rename_memory` 会**自动改写所有 `mem:` 引用**，没加前缀的普通提及不会。改名前先确认引用是否带前缀。
- 首次接触项目时 `onboarding` 会读一堆文件并生成记忆——**它会吃掉大量上下文**，做完换新会话。`onboarding` 只在有 `write_memory`（未禁记忆模式）时有效，否则返回 "Memory writing tool not activated, skipping onboarding."
- 不用记忆体系：全局配置 `base_modes` 加 `no-memories`（连 onboarding 一起禁）或 `no-onboarding`（仅禁 onboarding）。

## 7. 在 omp 下接线与排障

**接线**（`~/.omp/agent/mcp.json` 的 `mcpServers.serena`，见第 0 节）。改完**需要新会话或重连**才加载；用第 0 节的手工 `initialize` 探针先证明 server 本身健康，再判断是不是 omp 侧没挂上。

**高频故障**：

- **工具不在列表里** → 该 server 未挂载或被禁用（`enabled: false` / `disabledServers`）。别怀疑参数。
- **server 能起但所有工具报 "No active project"** → cwd 不在项目内（无 `.git`/`.serena`），或忘传 `--project`/`--project-from-cwd`；或调用 `activate_project` 激活。
- **`serena` 命令找不到** → uv tool 的 shim 目录（`UV_TOOL_BIN_DIR`）不在 PATH。本机 shim 在 `…/scoop/persist/uv/tools/shims/serena.exe`。
- **从 Python 子进程 spawn serena 立刻崩**（`sys.flags`/`logging` import 报错、进程秒退）→ 父进程的 **`PYTHONHOME` 污染**：serena 是 3.13 自带 venv，却继承了外面 3.14 的 `PYTHONHOME`，解释器版本错配（实测报 `AttributeError: 'sys.flags' object has no attribute 'context_aware_warnings'`）。**spawn 时剔除所有 `PYTHON*` 环境变量**即可。
- **改项目设置不生效** → 检查是否被 `project.local.yml` 或全局 `serena_config.yml` 覆盖；`project.yml` 与全局是叠加/覆盖关系并非替换。

**自身诊断命令**（不依赖 MCP）：`serena --version`、`serena context list`、`serena tools list`、`serena project health-check`、`serena memories check`（`mem:` 引用完整性）、`serena config edit`。日志与 dashboard：`~/.serena/logs/<日期>/mcp_*.txt`，默认 dashboard `http://localhost:24282/dashboard/index.html`（多实例递增端口）。

## 8. 底线规则

1. **先 `get_symbols_overview`，再 `find_symbol(include_body=True)`**——不要为了找个函数先整文件读进来。
2. **能符号级就别文本级**：改符号体用 `replace_symbol_body`，改名字/删符号用 `rename_symbol`/`safe_delete_symbol`，不要 grep 加手工 edit。
3. **`name_path` + `relative_path` 成对给**（除纯全局搜），返回里的 `relative_path` 直接复用。
4. **不要读已被 Serena 读过的整个文件再符号分析**——已有内容就别重来。
5. 记忆能用就用：开工前 `list_memories` 看名字，相关的 `read_memory`；学到稳定事实用 `write_memory` 落库。

## References

- 项目工作流/激活/多项目：`https://oraios.github.io/serena/02-usage/040_workflow.html`
- 上下文与模式、配置分层：`https://oraios.github.io/serena/02-usage/050_configuration.html`
- 记忆与 onboarding：`https://oraios.github.io/serena/02-usage/045_memories.html`
- 客户端接线（各 agent 的配置片段）：`https://oraios.github.io/serena/02-usage/030_clients.html`
- 工具清单与说明：`serena tools list --all`（本地权威，随版本变）
- 与 Ix 的分工：Ix 给项目级图/影响面，Serena 给符号级定位与编辑，见 `skill://ix`。
