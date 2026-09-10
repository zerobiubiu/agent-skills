---
name: nushell-style
description: 编写任何 Nushell 代码时的写法约束与语法陷阱 —— 函数式风格要求、$in 与字符串插值易错点、版本漂移验证法、Windows 注意事项。与执行方式无关，走 MCP、nu -c、.nu 脚本文件都适用。
---

# Nushell 写法约束

适用于**任何** Nushell 代码，与执行路径无关：MCP `evaluate`、`nu -c '<code>'`、`.nu` 脚本文件都一样。

何时该选 Nushell 而非 Bash / Python 见 AGENTS.md 第 1 节。走 MCP 时的 `$history` 复用、stdio 输出丢失等 transport 专有问题见 `nushell-mcp-usage`。

## 写法要求

函数式风格，下列视为缺陷：

- `mut` + `for` 当累加器 → `reduce` / `each` / `where` / `group-by` / `generate`；`mut` 只用于确实无法用过滤器表达的顺序状态
- 步骤间传字符串 → 传 record 与 table，只在边界处 `to json --raw` / `from json` 各一次
- 按值的形状写嵌套 `if/else` → `match`，含列表模式与守卫
- 为取数据 shell out → 原生命令优于 `^jq` / `^sed` / `^awk` / `^date`
- 纯副作用的 `each` 不收尾 → 结果不用时显式 `| ignore`

其他约定：

- 自定义命令标注类型签名（参数、`--flag`、返回类型），parse 阶段即检查
- 需要退出码与 stdout / stderr 而不抛错时用 `complete`；报错用 `error make`，不用哨兵返回值
- 时间戳用 `datetime`、时长用 `duration`，直接比较相减，不格式化成字符串再比
- CI 脚本的进度信息写 stderr，stdout 留给数据产物
- 外部命令的短横线参数会被 Nushell 抢解析时，用 `run-external` 并引号包裹 `'-L'` / `'-x'` 这类短 flag

## 高频易错点（0.115.1 实测）

| 写法 | 结果 |
|---|---|
| `$"hello {$name}"` | 错，花括号不插值 |
| `$"hello ($name)"` | ✅ 圆括号 |
| `$"(literal)"` | 报错，括号被当代码求值；字面括号转义 `\(text\)` |
| `where not ($in.col \| cmd)` | 报 `Variable not found` —— `not` 破坏 `$in` |
| `where ($in.col \| cmd) == false` | ✅ 绕过写法 |
| `where a > 1 and b > 3` | ✅ 裸列名可用 |
| `cmd1; cmd2` 代替 `cmd1 && cmd2` | 语义不等价，`;` 无短路 |

`&&` 需要短路时判断 `$env.LAST_EXIT_CODE` 或用 `complete` 取 `exit_code`。

## 版本漂移

Nushell 小版本间会改名和破坏兼容，**不要凭记忆写**。实证：`help commands | get usage` 在 0.115.1 报 `Cannot find column 'usage'`，列已改名 `description`。

不确定就先问解释器：

```nu
help commands | columns          # 看实际列名
help <command>                   # 单命令帮助
nu --ide-check 10 script.nu      # 静态检查脚本
version | get version            # 确认版本
```

## Windows 注意

- 路径反斜杠在双引号串里需转义，优先用单引号或正斜杠
- `$env.Path`（Windows）与 `$env.PATH` 大小写差异
- 外部命令用 `^` 前缀显式声明，避免与原生命令重名冲突

## 从 Bash 走 nu -c

```bash
nu -c 'ls | where size > 1mb | to json'
```

外层用单引号，避免 shell 抢解析 Nushell 的 `$`。多语句用 `;` 分隔。
