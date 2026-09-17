---
name: jiandaoyun-rest-api
description: 开发、审阅、修正简道云开放平台 REST API（api.jiandaoyun.com）调用代码时使用——读写表单数据、跑流程待办、维护通讯录。覆盖 v1/v2/v5/v6 混用路由、{"value":...} 写入包装、data_id 游标分页、filter 按字段类型可用的方法、batch 100 条与 transaction_id 幂等、子表单整体覆盖、只读字段清单、时间格式与错误码定位。也用于判断某件事该走 REST 还是简道云 MCP、以及排查 8302/17053 这类授权失败。
---

# 简道云开放平台 REST API

完整接口手册（本地副本，含全部参数表与请求/响应示例）：`skill://jiandaoyun-rest-api/reference.md`。

**本文只放写代码前必须知道的规则与易错点。** 查某个接口的具体字段表时再去读 `reference.md`——那是唯一事实源，本文与它冲突时以它为准。

## 0. 先决定走 MCP 还是 REST

本项目 `.omp/mcp.json` 已挂 `简道云-测试`（http 型，URL 路径段即令牌）。

- **交互式探查**（列应用/表单、看字段 key、抽查几条数据）→ 用 MCP，省去自己处理签名与分页。
- **批量灌数据、批改、删除、跑流程动作、通讯录维护、写进代码的自动化** → 用 REST。MCP 不适合这些：它受个人视角的数据权限约束，也没有流程与通讯录功能面。
- **两套凭证互相独立，失败原因不能互相推断**：MCP 报 `4010` 是个人视角无数据权限；REST 报 `8302`/`17053` 是 API Key 授权范围问题。看到 4010 不要去查 Key，看到 8302 不要去查成员权限。

**MCP 工具名的坑**：`简道云-测试` 无 ASCII 字符可保留，工具名 mint 时会塌缩成 `mcp__server_*`。若再加一个同样无 ASCII 区分度的中文服务器名（如 `天久简道云`），会 mint 出**完全相同**的工具名，其中一个被静默丢弃（只有 logger.warn，界面无提示）。需要多环境时用纯 ASCII 名（如 `jiandaoyun-dev`）。

三个工具的服务端契约：当前任务首次调用前必须先调 `get_tool_help(tool_name=...)`，涉及 `member_data_list`、`member_managed_data_list`、`member_data_create`。这是契约不是建议。`member_managed_*` 系列需管理员身份。

## 1. 基础规则

- Base：`https://api.jiandaoyun.com/api/{version}/...`，**一律 POST + JSON + UTF-8**（只有文件上传是 form-data）。
- 鉴权 header：`Authorization: Bearer <API_KEY>`。Key 在「开放平台 >> 密钥管理」创建，可限定应用授权范围、接口授权范围、IP 白名单。
- **API Key 绝不硬编码进仓库**，走环境变量或 `.env`。本项目 `.omp/mcp.json` 是唯一允许内联令牌的位置。
- 频率：全局 50 次/秒，各接口另有独立上限（查询类多为 30/s，写入 20/s，批量 10/s，抄送 5/s）。命中返回 `8303`（企业级）或 `8304`（接口级），退避 1s 重试。另有 `8309`（成员级，个人视角连续调用触发，**官方错误码表未收录**）。
- 定位一张表需要 `app_id + entry_id` 两个 ID；单条数据用全局唯一 `_id`（在各接口里叫 `data_id`）。
- HTTP 400 才带业务码：`{"code": 8303, "msg": "..."}`；429 是并发超限；579 是文件上传失败；502 是网关。
- 版本号**不统一**：数据接口全 v5；流程实例与待办列表是 v6，多数流程动作 v1/v2（加签 v2）；部门列表/创建/修改 v6，删除 v5。别把 v5 套到 workflow 上。

## 2. 常用路由速查

| 目的 | 路由 | 频率 |
|---|---|---|
| 应用列表 | `v5/app/list` | 30/s |
| 表单列表 | `v5/app/entry/list` | 30/s |
| 字段元信息 | `v5/app/entry/widget/list` | 30/s |
| 查单条 | `v5/app/entry/data/get` | 30/s |
| 查多条 | `v5/app/entry/data/list` | 30/s |
| 新建单条 / 多条 | `v5/app/entry/data/create` / `batch_create` | 20/s / 10/s |
| 改单条 / 多条 | `v5/app/entry/data/update` / `batch_update` | 20/s / 10/s |
| 删单条 / 多条 | `v5/app/entry/data/delete` / `batch_delete` | 20/s / 10/s |
| 上传凭证 | `v5/app/entry/file/get_upload_token` | 20/s |
| 流程实例 | `v6/workflow/instance/get`、`v1/workflow/instance/logs`、`v1/workflow/instance/close`、`v1/workflow/instance/activate` | 30/s、30/s、20/s、20/s |
| 待办 | `v6/workflow/task/list`、`v1/workflow/task/approve`、`v2/workflow/task/rollback`、`v1/workflow/task/transfer`、`v2/workflow/task/add_sign`、`v2/workflow/task/revoke`、`v1/workflow/task/reject` | 20/s |
| 审批意见 | `v1/app/{app_id}/entry/{entry_id}/data/{data_id}/approval_comments`（**唯一的路径参数接口**） | 30/s |
| 抄送列表 | `v1/workflow/cc/list` | 5/s |
| 通讯录 | `v5/corp/user/*`、`v5/corp/department/*`、`v6/corp/department/*` | 见 reference |

注意：数据类与通讯录类的 `app_id`/`entry_id` 都放 **body**，只有审批意见那条把三个 ID 放进 URL 路径。

## 3. 写入的五个硬规则

**规则 1：写入值必须包 `{"value": ...}`，读出来的不包。**

```jsonc
// create / update 请求
"data": { "_widget_1432728651402": {"value": "简道云"} }
// get / list 响应
"_widget_1432728651402": "简道云"
```

**这是本套 API 最高频的 bug**：把查询结果原样回填给 update。读出来的是裸值，写进去必须重新包 `value`。漏包不报错或报 `3005`/`17017`。

**规则 2：这些字段写不进去。** 分割线、手写签名 `signature`、选择数据 `linkdata`、查询字段、流水号 `sn`（提交后系统生成）、以及全部系统字段（`_id`/`createTime`/`creator`/`updater`/`appId`/`entryId`）。塞进 `data` 不会明确报错，只是不生效或整体失败（`17032`/`17034`）。

**规则 3：主键用 username / dept_no，不是 _id。** 成员字段传 `{"value": "jian"}` 或 `{"value": ["jian","dao"]}`（成员编号）；部门字段传 `{"value": 12}` / `{"value": [12,13]}`（部门编号）。v1 时代的 `_id` 主键已废弃。

**规则 4：API 写入绕过校验。** create/update/batch_* **都不触发**重复值校验、表单校验、必填校验、字段联动与公式。数据合法性必须由调用方自己保证——该查重的自己查，该拦的自己拦。会触发的只有：聚合表计算、数据操作日志、数据工厂延时计算、数据消息推送。**webhook 数据推送任何 API 写入都不触发**。智能助手仅 create/update/delete 可用 `is_start_trigger`（batch 系列没有该参数）；发起流程仅 create/batch_create 可用 `is_start_workflow`。

**规则 5：`data_creator` 不能填互联组织的外部对接人，且只有 create/batch_create 支持。** 取成员编号 username，默认记为企业创建者。指定后，智能助手执行人、流程发起人、CRM 关联修改的修改人也一并记为此人。

## 4. 分页：三套语义，别混

`data/list` 的 `data_id` 是**游标不是 offset**，结果恒按 data_id 正序：

1. 首次不传 `data_id`，`limit` 最大 100（**默认只有 10，几乎总要显式传**）。
2. 之后每次传上一批**最后一条**的 `_id`。
3. 返回条数 < limit 即结束（用这个判断，不要靠总数）。

其余两套：`app/list`、`app/entry/list` 用 `skip`/`limit`；`workflow/task/list` 的 v6 **已取消 `skip`**，改用 `task_id` 游标；抄送列表仍用 `skip`/`limit`。共三套，不要互相套用。

## 5. filter：过滤方法受字段类型限制

结构 `{"rel": "and"|"or", "cond": [{"field","type","method","value"}]}`。方法全集 `eq ne in nin like range gt lt all empty not_empty verified unverified`，但每类字段只接受一部分：

- 文本 / 文本域 / 下拉 / 单选：`eq ne in nin empty not_empty`（**没有 like**）
- 流水号：额外支持 `like`
- 数字：`eq ne range gt lt empty not_empty`
- 日期时间（含 createTime）：`eq ne range empty not_empty`
- 复选框组 / 下拉复选框 / 成员多选 / 部门多选：`in all empty not_empty`（仅此四种）
- 成员单选 / 部门单选 / 关联数据 / `flowState` / 提交人：`eq ne in nin empty not_empty`
- `data_id`：`eq in empty not_empty`（**无 ne**）
- 手机：`like verified unverified empty not_empty`
- 其余字段（子表单除外）：只有 `empty not_empty`

`in`/`nin`/`all` **每个最多 1000 个值**。

**两个静默陷阱**：
- 成员字段用 `nin` 时，若传入的 username 不存在，**整个 nin 条件静默失效并返回全量**，不报错。传 username 前先用 `v5/corp/user/get` 确认存在。
- 文本类字段用 `like` 不是报错就是行为不符预期。要模糊匹配就拉回来在客户端过滤。

条件过长或方法不匹配会返回 `4815`。

## 6. batch 与 transaction_id

- `batch_create` / `batch_update` / `batch_delete` 单次上限均为 **100** 条（超限分别报 `17024` / `17023` / `17033`）。
- `transaction_id` 有效期 **1 小时**，语义是「同一批任务」：
  - 1 小时内用**相同** id 重发 `batch_create`，第二次会**完全覆盖**第一次的数据 —— 这正是部分失败后的正确重试方式（**传全量，不要只补失败的那几条**）。
  - 超过 1 小时同 id 会当成新批次，直接产生重复数据。
- 建议用 UUID；格式不合法报 `17025`，重复报 `17026`。不允许含 `${var}`、`$(var)` 这类模式。
- `batch_update` 是「把多条数据的某些字段改成**同一个固定值**」，**不支持子表单**，且**附件/图片字段更新会清空该字段原有文件**。

## 7. 子表单：整体覆盖，不是增量合并

这是本套 API 最容易造成**静默数据丢失**的地方。

- 读出来是数组，每项带服务端生成的 `_id`。
- `update` 只要在 `data` 里带了子表单字段，就会**清空该条数据原有的整个子表单**，再写入本次请求的数组。不是按行合并。
  - 原有 3 行、请求只写 2 行 → 即使这 2 行 `_id` 都传对，改完**只剩 2 行**，第 3 行被删掉。
  - 某行原有 3 个子字段、请求只写 2 个 → 改完该行**只剩 2 个子字段**。
  - **正确姿势：先 `data/get` 读回完整子表单，在完整数组上改，整份提交。** 不能只发要改的那几行。
- `_id` 决定的是「这一行保不保留原 ID」，不是「新增还是修改」：
  - 传**正确** `_id` → 该行保持原 `_id`；
  - **不传**或传**错** `_id` → 该行以**新的 `_id`** 重建（行数仍由请求数组长度决定，不会凭空多一行）。
  - 副作用：数据日志会记一条「子表单变更」，哪怕内容一个字没改。
- v1、v2 接口无此行为；**v3/v4/v5 才是上述语义**。
- `batch_update` 干脆不支持子表单。
- 写法：`{"value": [{"_id": {"value": "606290..."}, "_widget_xxx": {"value": "李四"}}]}`。

## 8. 附件/图片上传（三步，1 小时内完成）

1. `POST v5/app/entry/file/get_upload_token`，带 `transaction_id`（UUID），一次返回最多 100 组 `{url, token}`。
2. 逐个 `POST {url}` form-data 上传：`token` 在前、`file` **必须是最后一个参数**，且要正确指定 mime（PDF 必须 `application/pdf`）。一个 token 只能传一个文件、不可覆盖。返回 `{"key": "..."}`。
3. `data/create` 或 `data/update` 时，附件/图片字段填 `{"value": ["<key1>", "<key2>"]}`，并且 **`transaction_id` 必须与第 1 步完全相同**，否则 key 绑不上。

token 与 transaction_id 均 1 小时过期，过期后 key 作废。

## 9. 时间格式

写入接受：ISO（`2018-11-09T10:00:00Z` 或不带 Z）、毫秒时间戳（`1639106951523`）、`yyyy-MM-dd HH:mm:ss`、`yyyy-MM-dd`、RFC3339 带时区。

拒绝：`null`、`undefined`、空串、**秒级时间戳**、`0`、`2021/10/10 10:10:10`、数组包裹、IETF 格式、逗号分隔毫秒。

**带 `Z` 表示 UTC**，查询结果会与本地（东八区）相差 8 小时——报表口径对不上先查这里。

## 10. 流程

- `instance_id` 就是 `data_id`，同一个值。
- 实例 `status`：0 进行中 / 1 流转完成或否决 / 2 手动结束；`result` 仅完成后存在：0 否决 / 1 同意。
  表单数据里的 `flowState`：0 进行中 / 1 完成 / 2 手动结束 / 3 否决。**两者不是同一套取值，不要互相套用。**
- 待办动作（approve/rollback/transfer/add_sign/revoke/reject）都要 `username` + `task_id` **一一对应**，且 `username` 指**当前节点负责人**，不是流程发起人。
- `rollback` 的 `flow_id` 只在节点配置为「回退到指定节点」时才传；节点开了「回退人选择」则必须传 `back_type`（1 正常流转 / 2 直达目标节点），缺了报 `50082`。
- `add_sign` 必须由用户明确选 `add_sign_type`：**0 前加签 / 1 后加签 / 2 并加签**，被加签人走 `add_sign_usernames`（数组）。不要替用户推断，也不要用已废弃的 `sign_type` / `sign_user_names` / `add_sign_username`。
- `instance/get` 的 `tasks_type`：0 不返回待办，1 全部返回。
- 抄送列表只有 5 次/秒，且只查得到 **90 天内**的数据。

## 11. 报错定位

先看 HTTP：429=并发超限，579=文件上传失败，502=网关，**400 才读 body 里的 `code`**。

高频码速记：

| code | 含义 | 动作 |
|---|---|---|
| 8301 / 17018 | API Key 校验失败 / 无效 | 检查 Key 是否正确、是否启用 |
| 8302 / 17052 / 17053 / 17054 | 无接口权限 / 不在 IP 白名单 / 不在应用授权范围 / 不在接口授权范围 | **改 API Key 配置，不是改代码** |
| 8303 / 8304 | 企业级 / 接口级频率超限 | 退避 1s 重试 |
| 8309 | 成员级限流（官方表未收录） | 个人视角连续调用触发，降速 |
| 2004 / 3000 / 4001 | 应用 / 表单 / 数据不存在 | 核对 app_id、entry_id、data_id |
| 3005 / 17017 | 参数不正确 | 多半是漏包 `{"value":...}` 或字段类型不符 |
| 17032 / 17034 | 不支持的字段类型 / 子表单字段类型 | 命中了只读字段清单（§3 规则 2） |
| 17023 / 17024 / 17033 | 批改 / 批建 / 批删 超 100 | 分片 |
| 17025 / 17026 | transaction_id 格式错 / 重复 | 换 UUID |
| 4815 | 过滤条件设置有误 | 条件过长或方法与字段类型不匹配（§5） |
| 1010 | 用户不存在 | username 拼错，或误传了 name/昵称 |
| 7212 / 7221 / 7103 / 7206 | 数据流量、API 新增数据、系统用量超版本限制 | 业务侧升级，重试无用 |

完整对照表见 `reference.md` 第十节：HTTP 状态码 5 条、业务错误码 127 条、流程专用补充 23 条。

## 12. 调用骨架

```bash
curl -sS -X POST 'https://api.jiandaoyun.com/api/v5/app/entry/data/list' \
  -H "Authorization: Bearer $JDY_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"app_id":"...","entry_id":"...","limit":100}'
```

写代码的顺序永远是：**`widget/list` 拿字段 key 和 type → 按 type 决定写入形状 → 小样本 `create` 验证形状 → 再放量 `batch_create`**。

跳过第一步、凭表单界面上的中文字段名猜 `_widget_*`，是这套 API 上最常见的返工来源。另外 label 会重名，**定位字段一律用 widget id**。
