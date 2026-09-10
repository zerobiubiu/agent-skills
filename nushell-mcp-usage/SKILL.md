---
name: nushell-mcp-usage
description: 配置与调用 nushell MCP：stdio 接入验证（探测二进制、JSON-RPC 握手、stdout 纯净性）、--no-config-file 与 --no-std-lib 取舍、evaluate / list_commands / command_help 三工具分工、$history 索引复用与首跑不限流、stdio 下裸 print 输出丢失、evaluate 等同本地 shell 执行权的安全边界。写法与语法陷阱见 nushell-style。
---

# nushell MCP 调用指导

Nushell 内置 MCP（`nu --mcp --no-config-file`，stdio）。三个工具：`evaluate`、`list_commands`、`command_help`。

写法约束、语法陷阱、版本漂移见 `nushell-style`（与执行方式无关）。何时该选 Nushell 见 AGENTS.md 第 1 节。

## 安全边界（先读）

`evaluate` 可执行**任意 Nushell 命令及外部程序**，等同本地 shell 执行权，且绕过常规 bash 工具的审查面。因此：

- 只读查询、数据处理、格式转换：直接用
- 删文件、改配置、装包、网络提交、动生产数据：先确认再跑
- 「帮我看看」「检查一下」不构成执行授权

## 三个工具

| 工具 | 用途 |
|---|---|
| `evaluate` | 执行代码，持久 REPL |
| `list_commands` | 列原生命令 |
| `command_help` | 查单个命令帮助，**仅限原生命令** |

`command_help` 对外部程序无效，先用 `list_commands` 确认是不是原生命令。

## 状态与 $history

REPL 跨调用存活：变量、`$env` 修改、`cd` 后的 cwd 都保留。

每次返回含 `history_index`。**用返回的显式索引，不要用 `$history | last`** —— 第二次调用时 `last` 指向它自己。

```nu
$history.7 | where status == "err"   # 重切第 7 次调用的完整结果
```

- 响应超 `NU_MCP_OUTPUT_LIMIT`（默认 10kb）时返回 `note` 而非 `output`，完整值仍在 `$history` 里
- 因此**首次运行的管道不要加 `first N` / `last N` / `head` 限流**，跑完再从 `$history` 切片
- `complete` 把 `stdout` / `stderr` / `exit_code` 拆成独立列，优于 `o+e>|` 合流

## 输出丢失陷阱

stdio 模式下裸 `print` 的输出**会丢失**，返回空 `[]`。改用：

- `print -e "msg"` 写 stderr
- 或直接让值成为最后一个表达式（隐式返回）

## 接入配置

Nushell 自带 MCP server，预编译二进制**通常已含该特性 —— 先探测再考虑重编**。

### 1. 探测二进制（只读）

```bash
nu --version
nu --help | grep -i mcp    # 找 --mcp / --mcp-transport / --mcp-port
```

flag 缺失才需要 `cargo build --release --features mcp`，此时**停下来请求授权**，不要擅自 clone 编译。

实测：Windows 上 scoop 装的 Nushell 0.115.1 **已包含**该特性，与「默认关闭」的网络文档相反。以二进制探测为准，不信文档。

### 2. JSON-RPC 握手确认

`echo '' | nu --mcp` 只会返回 `ConnectionClosed("initialize request")`，这是预期行为不是失败。要发真实请求：

```python
import subprocess, json
req = [
 {"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe","version":"1"}}},
 {"jsonrpc":"2.0","method":"notifications/initialized"},
 {"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}},
]
inp = "\n".join(json.dumps(r) for r in req) + "\n"
p = subprocess.run(["nu","--mcp","--no-config-file"], input=inp.encode(), capture_output=True, timeout=30)
out = p.stdout.decode("utf-8", "replace")
```

`input` 必须传 **bytes**；用 `text=True` 时管道可能返回 `None`，`.strip()` 会抛 `AttributeError`。

预期 `serverInfo.name == "nushell-mcp-server"`，工具为 `evaluate` / `list_commands` / `command_help`。

### 3. 校验 stdout 纯净

stdout 每行必须以 `{` 开头。任何 banner / `print` / 提示符输出都会污染 JSON-RPC 流。

```python
lines = [l for l in out.strip().split("\n") if l.strip()]
assert all(l.lstrip().startswith("{") for l in lines)
```

### 4. 写入配置

```json
"nushell": {
  "_comment": "Nushell MCP (nu 0.115.1 内置) | stdio | ⚠️ evaluate 可执行任意 Nushell 命令及外部程序，等同本地 shell 执行权，绕过常规 bash 工具审查面 | --no-config-file 防止 config.nu 输出污染 JSON-RPC 流",
  "type": "stdio",
  "command": "nu",
  "args": ["--mcp", "--no-config-file"]
}
```

`command: "nu"` 走 PATH 解析即可（scoop shim 可用），无需绝对路径。默认 transport 已是 stdio，不用写 `--mcp-transport stdio`。

写完用**配置里的完整 argv** 重跑第 2 步握手，再重启 agent 加载。

### flag 取舍

| Flag | 结论 |
|---|---|
| `--no-config-file` | **用**。跳过 env.nu / config.nu，阻断 banner、print、starship 污染 stdout |
| `--no-std-lib` | **别用**。会让 `use std` 报 `nu::parser::module_not_found`，`evaluate` 里失去 assert / log / iter / formats / dt / bench；它唯一的好处（去 banner）在非交互的 `--mcp` 下本就不触发 |
| `--config <path>` | MCP 会话确实需要自定义函数时的替代方案，指向一个保证 stdout 静默的最小配置 |

多数 std 命令不预加载：裸写 `assert true` 会被当外部命令而失败，需先 `use std *`。默认只注入 `banner` / `pwd`。

