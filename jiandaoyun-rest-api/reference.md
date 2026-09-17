# 简道云 API 完整参考手册（本地版）

> 本副本来自 jdy-action 工程（`.omp/skills/jiandaoyun-rest-api/reference.md`），
> 原样继承，sha256 前 12 位 `088907950ae8`。**本文件是唯一事实源**；
> `SKILL.md` 只是它的速查摘要，两者冲突时以本文件为准。
>
> 来源：https://hc.jiandaoyun.com/open/11261
> 整理时间：2026-07-22
> 复核时间：2026-09-11 —— 已对照线上逐页复核「应用/表单/数据/文件/流程/通讯录/角色/企业互联/资源用量/审计日志」共 60+ 个接口页。
> 所有接口均包含完整的请求地址、参数表、请求/响应示例，无任何省略
>
> 复核结论：无接口新增或下线；全部路由、版本号、频率均未变。本次修正的实质内容：
> 1. 修改单条数据的**子表单为整体覆盖语义**（原文表述与真实行为相反，见第 8 节注意事项）；
> 2. filter 的 `in`/`nin`/`all` **各最多 1000 个值**；
> 3. `data_creator` 不能使用互联组织外部对接人的 username；
> 4. 添加成员接口 2024.01.19 起做部门存在性校验；
> 5. 查询流程实例信息补「子流程/插件节点/抄送节点动态无法获取」；
> 6. 平台/应用资源用量接口补 v2（2026.06.29）版本表。
>
> 线上文档自身的已知瑕疵（本文已修正，勿据线上回退）：数据接口总览称「7 个接口」实为 8 个；筛选器流水号行首项误写 `en`（应为 `eq`）；待办列表 `task_id` 标注 Number 但实际传字符串。

---

## 一、基础规则

### 1.1 访问地址

```
https://api.jiandaoyun.com/api/{version}/...
```

- 所有请求必须通过 **HTTPS**
- 统一采用 **POST** 请求
- 数据编码 **UTF-8**
- 文件上传接口为 `form-data` 格式，其他均为 **JSON** 格式

### 1.2 鉴权

通过 HTTP Header 设置：

```
Authorization: Bearer YOUR_APIKEY
```

- API KEY 在「开放平台 >> 密钥管理 >> 创建 API KEY」生成
- 一个企业最多 500 个 API KEY
- API KEY 可配置：应用授权范围、接口授权范围、IP 白名单
- 支持启用、停用和删除 API KEY

### 1.3 频率限制

- 全局：**50 次/秒**
- 各接口有独立频率限制（见各接口说明）

### 1.4 错误响应格式

```json
HTTP/1.1 400
Content-Type: application/json
{
  "code": 8303,
  "msg": "超出请求频率限制"
}
```

### 1.5 关键 ID 说明

- `app_id`：应用 ID
- `entry_id`：表单 ID
- `app_id + entry_id` = 全局唯一表单标识
- 在「开放平台 >> 参数说明」中查看，也可在「API 调试台」调试

### 1.6 版本兼容性

从 v6 版本开始，开放 API 在保证兼容性的情况下，简道云可能会增加（不会减少）相应的出入参数。

### 1.7 代码示例

官方多语言示例仓库：https://github.com/jiandaoyun/api-demo

- Python: https://github.com/jiandaoyun/api-demo/tree/master/python
- C#: https://github.com/jiandaoyun/api-demo/tree/master/csharp
- Go: https://github.com/jiandaoyun/api-demo/tree/master/go
- Java: https://github.com/jiandaoyun/api-demo/tree/master/java
- Node: https://github.com/jiandaoyun/api-demo/tree/master/node

---

## 二、字段与数据类型对照表

### 2.1 表单字段

| 字段名称 | 字段类型 | 数据类型 | 数据样例 | 备注 |
|----------|----------|----------|----------|------|
| 单行文本 | text | String | `"张三"` | |
| 多行文本 | textarea | String | `"我爱简道云"` | |
| 流水号 | sn | String | `"00001"` | |
| 数字 | number | Number | `10` | |
| 日期时间 | datetime | String | `"2018-01-01T10:10:10.000Z"` | UTC 格式 |
| 单选按钮组 | radiogroup | String | `"一年级"` | |
| 复选框组 | checkboxgroup | Array | `["选项1","选项2"]` | |
| 下拉框 | combo | String | `"女"` | |
| 下拉复选框 | combocheck | Array | `["选项1","选项2"]` | |
| 地址 | address | JSON | `{"province":"江苏省","city":"无锡市","district":"梁溪区","detail":"清扬路138号"}` | |
| 定位 | location | JSON | 同地址 + `"lnglatXY":[120.31,31.49]` | lnglatXY = [经度,纬度] |
| 图片 | image | Array | `[{"name":"a.png","size":262144,"mime":"image/png","url":"..."}]` | url 15天有效 |
| 附件 | upload | Array | `[{"name":"a.pdf","size":524288,"mime":"application/pdf","url":"..."}]` | url 15天有效 |
| 子表单 | subform | Array | `[{"_id":"...","_widget_xxx":...}]` | _id 由服务端生成 |
| 选择数据 | linkdata | JSON | `{"id":"5b237548b22ab14884086cc0"}` | 关联数据 ID |
| 手写签名 | signature | JSON | `{"name":"sig.png","size":1024,"mime":"image/png","url":"..."}` | url 15天有效 |
| 成员单选 | user | JSON | `{"name":"小简","username":"xiaojian","status":1,"type":0,"departments":[1,3],"integrate_id":"xiaojian"}` | username=成员编号(企业内唯一)；status: -1离职, 0未加入, 1已加入 |
| 成员多选 | usergroup | Array | 同成员单选数组 | |
| 部门单选 | dept | JSON | `{"name":"经理部","dept_no":1,"type":0,"parent_no":2,"status":1,"integrate_id":1}` | dept_no=部门编号(企业内唯一) |
| 部门多选 | deptgroup | Array | 同部门单选数组 | |
| 手机 | phone | JSON | `{"phone":"13566666666","verified":true}` | 提交时 verified 不需要 |
| 关联数据 | lookup | String | `"66e10594b3eeff4d9888ad43"` | 数据全局唯一 ID |
| 计算 | aggregation | Number/String | `20` 或 `"发货成功"` | |
| 富文本 | richtext | JSON | `{"html":"<p>...</p>","attachments":[...]}` | url 15天有效 |

### 2.2 系统字段

| 系统字段 | 字段名 | 类型 | 备注 |
|----------|--------|------|------|
| 应用 ID | appId | String | |
| 表单 ID | entryId | String | appId+entryId 唯一 |
| 数据 ID | _id | String | 数据全局唯一 |
| 扩展字段 | ext | String | |
| 提交时间 | createTime | String | ISO 格式 |
| 修改时间 | updateTime | String | |
| 提交人 | creator | JSON | 同成员结构 |
| 修改人 | updater | JSON | 同成员结构 |
| 流程状态 | flowState | Number | 仅流程表单：0=进行中, 1=流转完成, 2=手动结束, 3=否决 |

### 2.3 时间格式

写入数据支持的时间格式：

| 格式 | 示例 | 备注 |
|------|------|------|
| ISO 日期 | `2018-11-09T10:00:00Z` / `2018-11-09T10:00:00` | Z 代表 UTC 0时区，查询结果会差8小时 |
| 毫秒时间戳 | `1639106951523` | 不支持秒级时间戳(如1639106951)、不支持0 |
| yyyy-MM-dd HH:mm:ss | `2021-10-10 10:10:10` | |
| yyyy-MM-dd | `2021-10-10` | |
| RFC 3339 | `2020-06-04 14:41:54.767135400+08:00` | |

**不支持的格式**：`null`、`undefined`、`''`、IETF格式(`Thu, 04 Jun 2020 13:54:52 +0800`)、`2021/10/10 10:10:10`、数组格式(`["2021-03-19 23:10:00"]`)、`Mar 31 10:10:43 UTC+0800 2012`、`2020-06-04T14:41:54,767+08:00`(逗号分隔毫秒)、`~`、空格。

### 2.4 API 操作关联关系

| 功能 | create | update | delete | batch_create | batch_update |
|------|--------|--------|--------|--------------|--------------|
| 数据工厂延时计算 | 触发 | 触发 | 触发 | 触发 | 触发 |
| 数据消息推送 | 触发 | 触发 | 不触发 | 触发 | 触发 |
| 触发聚合表 | 触发 | 触发 | 触发 | 触发 | 触发 |
| 数据操作日志 | 记录 | 记录 | 记录 | 记录 | 记录 |
| webhook 数据推送 | 不触发 | 不触发 | 不触发 | 不触发 | 不触发 |
| 智能助手 | 可触发 | 可触发 | 可触发 | 不触发 | 不触发 |
| 重复值校验 | 不校验 | 不校验 | - | 不校验 | 不校验 |
| 表单校验 | 不校验 | 不校验 | - | 不校验 | 不校验 |
| 必填校验 | 不校验 | 不校验 | - | 不校验 | 不校验 |
| 流程节点校验 | 不校验 | 不校验 | - | 不校验 | 不校验 |
| 触发流程 | 可触发 | 不触发 | - | 可触发 | 不触发 |
| 聚合表校验 | 校验 | 校验 | 触发 | 不校验 | 不校验 |
| 字段联动/公式 | 不触发 | 不触发 | - | 不触发 | 不触发 |
| 表单推送提醒 | 触发 | 触发 | - | 不触发 | 不触发 |

---

## 三、应用接口 + 表单和数据接口（详细）


# 简道云开放平台 API 接口文档

---

## 1. 用户应用查询接口

**接口名称**：用户应用查询接口

**请求地址**：`https://api.jiandaoyun.com/api/v5/app/list`

**请求方式**：POST

**请求频率**：30 次/秒

### 接口版本

| 接口版本 | 更新时间 | 版本说明 |
|---------|---------|--------|
| v1 | 2021.6.1 | 原始接口 |
| v5 | 2022.10.28 | 在 v1 的基础上，接口调用频率由 5 次/秒提升至 30 次/秒；接口路由 POST app/retrieve_all 修改为 POST app/list |

### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| limit | Number | 否 | 单次取数的数据条数，1~100，默认 100 |
| skip | Number | 否 | 需要跳过的数据条数，默认 0 |

**参数释义**：
- 目的：想要查询数据库中第 500～599 的数据
- 分析：查询的数据条数为 100 条；需要跳过的数据条数为 499
- 参数：那么请求参数 skip 可以设置为：499；limit 设置为 100

### 请求示例

```json
{
    "limit": 100,
    "skip": 499
}
```

### 响应参数

| 参数 | 含义 |
|------|------|
| apps | 应用信息 |
| apps[].name | 应用名称 |
| apps[].app_id | 应用id |

### 响应示例

```json
{
    "apps": [
        {
            "name": "应用名称1",
            "app_id": "5e0dca0cc9a2790006c11e02"
        }
    ]
}
```

---

## 2. 用户表单查询接口

**接口名称**：用户表单查询接口

**接口简介**：获取当前应用下所有表单信息。

**请求地址**：`https://api.jiandaoyun.com/api/v5/app/entry/list`

**请求方式**：POST

**请求频率**：30 次/秒

### 接口版本

| 接口版本 | 更新时间 | 版本说明 |
|---------|---------|--------|
| v1 | 2021.6.1 | 原始接口 |
| v5 | 2022.10.28 | 在 v1 的基础上，接口调用频率由 5 次/秒提升至 30 次/秒；参数 app_id 放入 body，接口路由 POST app/{app_id}/entry_retrieve 修改为 POST app/entry/list |

### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| app_id | String | 是 | 应用ID |
| limit | Number | 否 | 单次取数的数据条数，1~100，默认 100 |
| skip | Number | 否 | 需要跳过的数据条数，默认 0 |

### 请求示例

```json
{
    "app_id": "5e0dca0cc9a2790006c11e02"
}
```

### 响应参数

| 参数 | 含义 |
|------|------|
| forms | 表单信息 |
| forms[].name | 表单名称 |
| forms[].app_id | 应用id |
| forms[].entry_id | 表单id |

### 响应示例

```json
{
    "forms": [
        {
            "name": "表单名称1",
            "app_id": "5e0dca0cc9a2790006c11e02",
            "entry_id": "56fcab0f02c4675e3fe9694a"
        },
        {
            "name": "表单名称2",
            "app_id": "5e0dca0cc9a2790006c11e02",
            "entry_id": "5ed750af3c07c70f9c6eef78"
        }
    ]
}
```

---

## 3. 表单接口（表单字段查询接口V5）

**接口名称**：表单接口

**接口简介**：获取指定表单的字段/字段信息，除分割线字段和查询字段以外。

**请求地址**：`https://api.jiandaoyun.com/api/v5/app/entry/widget/list`

**请求方式**：POST

**请求频率**：30 次/秒

### 接口版本

| 接口版本 | 更新时间 | 版本说明 |
|---------|---------|--------|
| v1 | 2021.6.1 | 原始接口 |
| v2 | 2021.10.26 | V2 在 V1 的基础之上新增了系统字段及表单数据修改时间的获取 |
| v5 | 2022.10.28 | 在 v1 的基础上，接口调用频率由 5 次/秒提升至 30 次/秒；参数 app_id 和 entry_id 放入 body，接口路由修改为 POST app/entry/widget/list |

### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| app_id | String | 是 | 应用ID |
| entry_id | String | 是 | 表单ID |

### 请求示例

```json
{
    "app_id": "59264073a2a60c0c08e20bfb",
    "entry_id": "59264073a2a60c0c08e20bfd"
}
```

### 响应参数

| 参数 | 含义 |
|------|------|
| widgets | 字段信息 |
| widgets[].label | 字段标题 |
| widgets[].name | 字段名（设置了字段别名则采用别名，未设置则采用字段ID） |
| widgets[].widgetName | 字段 ID |
| widgets[].type | 字段类型；每种字段类型都有对应的数据类型 |
| widgets[].items | 仅子表单控件有；数组里包含了每个子字段的信息 |
| sysWidgets | 系统字段列表（扩展字段、流程字段受功能开关影响，微信增强一旦开启会始终返回） |
| sysWidgets[].name | 系统字段名称 |
| dataModifyTime | 表单内数据最新修改时间（可用于判断表单内的数据是否发生变更） |

### 响应示例

```json
{
    "widgets": [
        {
            "name": "_widget_1529400746031",
            "widgetName": "_widget_1529400746031",
            "label": "单行文本",
            "type": "text"
        },
        {
            "name": "_widget_1529400746045",
            "widgetName": "_widget_1529400746045",
            "label": "多行文本",
            "type": "textarea"
        },
        {
            "name": "_widget_1529400746056",
            "widgetName": "_widget_1529400746056",
            "label": "数字",
            "type": "number"
        },
        {
            "name": "_widget_1529400746068",
            "widgetName": "_widget_1529400746068",
            "label": "日期",
            "type": "datetime"
        },
        {
            "name": "_widget_1529400746090",
            "widgetName": "_widget_1529400746090",
            "label": "单选按钮组",
            "type": "radiogroup"
        },
        {
            "name": "_widget_1529400746105",
            "widgetName": "_widget_1529400746105",
            "label": "复选框组",
            "type": "checkboxgroup"
        },
        {
            "name": "_widget_1529400746119",
            "widgetName": "_widget_1529400746119",
            "label": "下拉框",
            "type": "combo"
        },
        {
            "name": "_widget_1529400746136",
            "widgetName": "_widget_1529400746136",
            "label": "下拉复选框",
            "type": "combocheck"
        },
        {
            "name": "_widget_1529400746157",
            "widgetName": "_widget_1529400746157",
            "label": "地址",
            "type": "address"
        },
        {
            "name": "_widget_1529400746173",
            "widgetName": "_widget_1529400746173",
            "label": "定位",
            "type": "location"
        },
        {
            "name": "_widget_1529400746191",
            "widgetName": "_widget_1529400746191",
            "label": "图片",
            "type": "image"
        },
        {
            "name": "_widget_1529400746209",
            "widgetName": "_widget_1529400746209",
            "label": "附件",
            "type": "upload"
        },
        {
            "name": "_widget_1529400746221",
            "widgetName": "_widget_1529400746221",
            "label": "子表单",
            "type": "subform",
            "items": []
        },
        {
            "name": "_widget_1529400746242",
            "widgetName": "_widget_1529400746242",
            "label": "选择数据",
            "type": "linkdata"
        },
        {
            "name": "_widget_1529400746242",
            "widgetName": "_widget_1529400746242",
            "label": "关联数据",
            "type": "lookup"
        },
        {
            "name": "_widget_1529400746254",
            "widgetName": "_widget_1529400746254",
            "label": "手写签名",
            "type": "signature"
        },
        {
            "name": "_widget_1529400746696",
            "widgetName": "_widget_1529400746696",
            "label": "成员单选",
            "type": "user"
        },
        {
            "name": "_widget_1529400746713",
            "widgetName": "_widget_1529400746713",
            "label": "成员多选",
            "type": "usergroup"
        },
        {
            "name": "_widget_1529400746729",
            "widgetName": "_widget_1529400746729",
            "label": "部门单选",
            "type": "dept"
        },
        {
            "name": "_widget_1529400746746",
            "widgetName": "_widget_1529400746746",
            "label": "部门多选",
            "type": "deptgroup"
        }
    ],
    "sysWidgets": [
        {"name": "flowState"},
        {"name": "wx_open_id"},
        {"name": "wx_nickname"},
        {"name": "wx_gender"},
        {"name": "creator"},
        {"name": "updater"},
        {"name": "deleter"},
        {"name": "ext"},
        {"name": "createTime"},
        {"name": "updateTime"},
        {"name": "deleteTime"}
    ],
    "dataModifyTime": "2021-09-08T03:40:26.586Z"
}
```

**注**：只要每一个表单字段不删除，字段 ID 就不会变化。

---

## 4. 查询单条数据接口

**接口名称**：查询单条数据接口

**接口简介**：通过查询单条数据接口，可以查询表单中的指定数据。

**请求地址**：`https://api.jiandaoyun.com/api/v5/app/entry/data/get`

**请求方式**：POST

**请求频率**：30 次/秒

### 接口版本

| 接口版本 | 更新时间 | 版本说明 |
|---------|---------|--------|
| v1 | 2018.6.21 | 原始接口 |
| v2 | 2021.3.11 | 子表单新增数据 ID 参数 |
| v4 | 2022.4.21 | 新增互联组织部门/成员获取，新增 type 参数类型：0（内部）、2（外部） |
| v5 | 2022.10.28 | 接口请求频率由 5 次/秒提升至 30 次/秒；参数 app_id 和 entry_id 放入 body，接口路由修改为 POST app/entry/data/get |

### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| app_id | String | 是 | 应用ID |
| entry_id | String | 是 | 表单ID |
| data_id | String | 是 | 数据 ID |

### 请求示例

```json
{
    "app_id": "59264073a2a60c0c08e20bfb",
    "entry_id": "59264073a2a60c0c08e20bfd",
    "data_id": "59e9a2fe283ffa7c11b1ddbf"
}
```

### 响应参数

| 参数 | 类型 | 说明 |
|------|------|------|
| data | JSON | 单条数据 |

### 响应示例

```json
{
    "data": {
        "_id": "59e9a2fe283ffa7c11b1ddbf",
        "appId": "59264073a2a60c0c08e20bfb",
        "entryId": "59264073a2a60c0c08e20bfd",
        "creator": {
            "name": "小简",
            "username": "xiaojian",
            "status": 1,
            "type": 0,
            "departments": [1, 3],
            "integrate_id": "xiaojian"
        },
        "updater": {
            "name": "小简",
            "username": "xiaojian",
            "status": 1,
            "type": 0,
            "departments": [1, 3],
            "integrate_id": "xiaojian"
        },
        "createTime": "2017-10-20T22:41:51.430Z",
        "updateTime": "2017-10-20T11:12:15.293Z",
        "_widget_1432728651402": "简道云",
        "_widget_1432728651403": 100,
        "_widget_1432728651404": "简道云是一个强大易用的应用搭建工具",
        "_widget_1432728651405": "选项一",
        "_widget_1432728651406": ["选项一", "选项二", "选项三"],
        "_widget_1432728651407": "2018-01-01T10:10:10.000Z",
        "_widget_1432728651408": {"id": "5b28effa49b561455dfda91e"},
        "_widget_1432728651409": [{"name": "image.jpg", "size": 262144, "mime": "image/jpeg", "url": "https://files.jiandaoyun.com/xxx"}],
        "_widget_1432728651410": [{"name": "产品说明文档.pdf", "size": 524288, "mime": "application/pdf", "url": "https://files.jiandaoyun.com/xxx"}],
        "_widget_1432728651412": {"province": "江苏省", "city": "无锡市", "district": "梁溪区", "detail": "清扬路138号茂业天地"},
        "_widget_1432728651413": {"province": "江苏省", "city": "无锡市", "district": "梁溪区", "detail": "清扬路138号茂业天地", "lnglatXY": [120.31237, 31.49099]},
        "_widget_1652345009097": {"verified": false, "phone": "15852540044"},
        "_widget_1432728651414": {"name": "小简", "username": "xiaojian", "status": 1, "type": 0, "departments": [1, 3], "integrate_id": "xiaojian"},
        "_widget_1432728651415": [{"name": "小简", "username": "xiaojian", "status": 1, "type": 0, "departments": [1, 3], "integrate_id": "xiaojian"}],
        "_widget_1432728651416": {"name": "经理部", "dept_no": 1, "type": 0, "parent_no": 2, "status": 1, "integrate_id": 1},
        "_widget_1432728651417": [{"name": "经理部", "dept_no": 1, "type": 0, "parent_no": 2, "status": 1, "integrate_id": 1}],
        "_widget_1432728651408": [{}],
        "wx_open_id": "wx98fb14481b3ab5a3",
        "wx_nickname": "jiandaoyun",
        "wx_gender": "男"
    }
}
```

---

## 5. 查询多条数据接口

**接口名称**：查询多条数据接口

**接口简介**：通过查询多条数据接口，可以一次查询表单中的多条数据。

**请求地址**：`https://api.jiandaoyun.com/api/v5/app/entry/data/list`

**请求方式**：POST

**请求频率**：30 次/秒

### 接口版本

| 接口版本 | 更新时间 | 版本说明 |
|---------|---------|--------|
| v1 | 2018.6.21 | 原始接口 |
| v2 | 2021.3.11 | 子表单新增数据 ID 参数 |
| v4 | 2022.4.21 | 新增互联组织部门/成员获取，新增 type 参数类型：0（内部）、2（外部） |
| v5 | 2022.10.28 | 接口请求频率由 5 次/秒提升至 30 次/秒；参数 app_id 和 entry_id 放入 body，接口路由修改为 POST app/entry/data/list |

### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| app_id | String | 是 | 应用ID |
| entry_id | String | 是 | 表单ID |
| data_id | String | 否 | 分页符，上一次查询数据结果的最后一条数据的 ID，没有则留空 |
| fields | Array | 否 | 需要查询的数据字段 |
| filter | JSON | 否 | 数据筛选器 |
| limit | Number | 否 | 查询的数据条数，1~100，默认10 |

### 数据筛选器

**筛选结构：**

| 参数 | 必需 | 类型 | 说明 |
|------|------|------|------|
| rel | 是 | String | 筛选组合关系；"and"(满足所有过滤条件), "or"(满足任一过滤条件) |
| cond | 是 | [JSON] | 过滤条件列表 |

**过滤条件结构：**

| 参数 | 必需 | 类型 | 说明 |
|------|------|------|------|
| field | 是 | String | 字段名 |
| type | 否 | String | 字段类型 |
| method | 是 | String | 过滤方法：not_empty、empty、eq、ne、in、range、nin、like、verified、unverified、all、gt、lt。**其中 in、nin、all 每个最多可传递 1000 个值** |
| value | 否 | Array | 过滤值 |

**支持的字段类型及过滤方式：**

| 字段类型 | 支持的过滤方式 | 说明 |
|---------|--------------|------|
| flowState | eq, ne, in, nin, empty, not_empty | 流程状态，仅对流程表单有效 |
| data_id | eq, in, empty, not_empty | 数据 id 字段，是数据唯一性的标识 |
| 提交人 | eq, ne, in, nin, empty, not_empty | — |
| 日期时间 | eq, ne, range, empty, not_empty | 包含日期时间字段和提交时间字段 |
| 数字 | eq, ne, range, empty, not_empty, gt, lt | — |
| 文本 | eq, ne, in, nin, empty, not_empty | 包括单行文本、下拉框、单选按钮组 |
| 复选框组/下拉复选框 | in, all, empty, not_empty | — |
| 手机 | like, verified, unverified, empty, not_empty | verified 表示填写了手机号且已验证的值；unverified 表示填写了手机号但未验证的值 |
| 成员单选/部门单选 | eq, ne, in, nin, empty, not_empty | 支持筛选内部组织成员、外部组织对接人、内部组织部门、外部组织互联企业 |
| 成员多选/部门多选 | in, all, empty, not_empty | — |
| 流水号 | eq, ne, in, nin, like, empty, not_empty | 线上文档此处首项误写为 `en`，实为 `eq` |
| 关联数据 | eq, ne, in, nin, empty, not_empty | — |
| 其他表单字段（不支持子表单字段） | empty, not_empty | — |

### 请求示例

```json
{
    "app_id": "59264073a2a60c0c08e20bfb",
    "entry_id": "59264073a2a60c0c08e20bfd",
    "data_id": "59e9a2fe283ffa7c11b1ddbf",
    "limit": 100,
    "fields": ["_widget_1508400000001", "_widget_1508400000002"],
    "filter": {
        "rel": "and",
        "cond": [
            {
                "field": "flowState",
                "type": "flowstate",
                "method": "eq",
                "value": [0]
            }
        ]
    }
}
```

### 响应参数

| 参数 | 类型 | 说明 |
|------|------|------|
| data | Array | 多条数据的集合 |

### 响应示例

```json
{
    "data": [
        {
            "_id": "59e9a2fe283ffa7c11b1ddbe",
            "appId": "59264073a2a60c0c08e20bfb",
            "entryId": "59264073a2a60c0c08e20bfd",
            "creator": {
                "name": "小简",
                "username": "xiaojian",
                "status": 1,
                "type": 0,
                "departments": [1, 3],
                "integrate_id": "xiaojian"
            },
            "createTime": "2017-10-20T22:41:51.430Z",
            "updateTime": "2017-10-20T11:12:15.293Z",
            "_widget_1432728651402": "A班",
            "_widget_1615777739673": [
                {"_id": "604ed0298e2ade077c7245f1", "_widget_1615777739744": "子表单数据1"},
                {"_id": "604ed0298e2ade077c7245f2", "_widget_1615777739744": "子表单数据2"}
            ]
        }
    ]
}
```

### 注意事项

该接口的返回数据始终按照数据 ID 正序排列。若要设置循环调取数据，可以利用 data_id 字段来设置参数避免调取重复数据：
- 第一次查询时可以不传 data_id 字段，若设置 limit 为 100，则第一次返回了前 100 条数据
- 第二次，用第 100 条数据的 data_id 进行查询，若设置 limit 为100，则第二次返回 101～200 这 100 条数据
- 第三次，用第 200 条数据的 data_id 进行查询，若设置 limit 为100，则第三次返回 201～230 这 30 条数据
- 由于第三次返回结果只有 30 条，未达到设置的 limit 上限100，则说明查询结束

**注：当成员字段使用的过滤方法为 nin（不等于任意一个）时，若查询的 username 不存在，则整个 nin 过滤条件将失效。**

---

## 6. 新建单条数据接口

**接口名称**：新建单条数据接口

**接口简介**：通过新建单条数据接口，可以向指定的表单中添加单条数据。

**请求地址**：`https://api.jiandaoyun.com/api/v5/app/entry/data/create`

**请求方式**：POST

**请求频率**：20 次/秒

### 接口版本

| 接口版本 | 更新时间 | 版本说明 |
|---------|---------|--------|
| v1 | 2018.6.21 | 部门和成员均使用_id为主键 |
| v2 | 2019.6.21 | 成员字段使用 username 为主键，部门字段使用 dept_no 为主键 |
| v3 | 2021.3.31 | 子表单新增数据 ID 参数 |
| v4 | 2022.4.21 | 新增互联组织部门/成员获取，新增 type 参数类型：0（内部）、2（外部） |
| v5 | 2022.10.28 | 接口请求频率由 5 次/秒提升至 20 次/秒；参数 app_id 和 entry_id 放入 body，接口路由修改为 POST app/entry/data/create。2023.08.31 新增请求参数 data_creator |

### 请求参数

| 参数 | 类型 | 必需 | 说明 | 默认 |
|------|------|------|------|------|
| app_id | String | 是 | 应用ID | |
| entry_id | String | 是 | 表单ID | |
| data | JSON | 是 | 数据内容 | |
| data_creator | String | 否 | 数据提交人（取成员编号 username，可从通讯录接口获取）。**注：不能使用互联组织中外部对接人的 username** | 企业创建者 |
| is_start_workflow | Bool | 否 | 是否发起流程（仅流程表单有效） | false |
| is_start_trigger | Bool | 否 | 是否触发智能助手 | false |
| transaction_id | String | 否 | 事务ID；用于绑定一批上传的文件，若数据中包含附件或图片控件，则 transaction_id 必须与"获取文件上传凭证和上传地址接口"中的 transaction_id 参数相同 | |

### 请求示例

```json
{
    "app_id": "59264073a2a60c0c08e20bfb",
    "entry_id": "59264073a2a60c0c08e20bfd",
    "transaction_id": "87cd7d71-c6df-4281-9927-469094395677",
    "data_creator": "Yonne",
    "data": {
        "_widget_1432728651402": {"value": "简道云"},
        "_widget_1432728651403": {"value": 100},
        "_widget_1432728651404": {"value": "简道云是一个强大易用的应用搭建工具"},
        "_widget_1432728651405": {"value": "选项一"},
        "_widget_1432728651406": {"value": ["选项一", "选项二", "选项三"]},
        "_widget_1432728651407": {"value": "2018-01-01T10:10:10.000Z"},
        "_widget_1432728651412": {"value": {"province": "江苏省", "city": "无锡市", "district": "梁溪区", "detail": "清扬路138号茂业天地"}},
        "_widget_1432728651413": {"value": {"province": "江苏省", "city": "无锡市", "district": "梁溪区", "detail": "清扬路138号茂业天地", "lnglatXY": [120.31237, 31.49099]}},
        "_widget_1528854613291": {"value": [{"_widget_1528854614409": {"value": "子表单数据1"}, "_widget_1528854615499": {"value": 1001}}]},
        "_widget_1652345009097": {"value": {"phone": "15852540044"}},
        "_widget_1652345009126": {"value": "jian"},
        "_widget_1652345009143": {"value": ["jian", "dao"]},
        "_widget_1652345009157": {"value": 12},
        "_widget_1652345009174": {"value": [12, 13]},
        "_widget_1432728651408": {"value": ["6b559cf1-b16c-43bd-a211-8fa8fdeae2ef"]},
        "_widget_1432728652567": {"value": ["6b559cf1-b16c-43bd-a211-74389cd8ae76"]}
    }
}
```

### 响应参数

| 参数 | 类型 | 说明 |
|------|------|------|
| data | JSON | 返回提交后的完整数据，内容同查询单条数据接口 |

### 响应示例

```json
{
    "data": {
        "_id": "59e9a2fe283ffa7c11b1ddbf",
        "appId": "59264073a2a60c0c08e20bfb",
        "entryId": "59264073a2a60c0c08e20bfd",
        "creator": {
            "name": "小简",
            "username": "xiaojian",
            "status": 1,
            "type": 0,
            "departments": [1, 3],
            "integrate_id": "xiaojian"
        },
        "createTime": "2017-10-20T22:41:51.430Z",
        "updateTime": "2017-10-20T11:12:15.293Z"
    }
}
```

### 注意事项

- 使用 API 添加数据时，会触发的事件有新数据提交提醒、聚合表计算&校验、数据操作日志、数据量统计。也可以通过请求参数来控制是否发起流程。但是不会触发重复值校验、必填校验。
- 系统字段和以下所列举的字段不支持添加和修改数据：分割线、手写签名、选择数据、查询、流水号（提交后系统生成）
- 如果请求中指定了 data_creator，则关联触发的以下成员也会被记录为 data_creator：智能助手执行人、流程发起人、由跟进记录关联修改的客户表/线索表/商机表的修改人、由商机表关联修改的客户表的修改人。

---

## 7. 新建多条数据接口

**接口名称**：新建多条数据接口

**接口简介**：通过新建多条数据接口，可以向指定的表单中添加多条数据。

**请求地址**：`https://api.jiandaoyun.com/api/v5/app/entry/data/batch_create`

**请求方式**：POST

**请求频率**：10 次/秒

### 接口版本

| 接口版本 | 更新时间 | 版本说明 |
|---------|---------|--------|
| v1 | 2021.12.30 | 原始接口 |
| v5 | 2022.10.28 | 接口请求频率由 5 次/秒提升至 10 次/秒；参数 app_id 和 entry_id 放入 body，接口路由修改为 POST app/entry/data/batch_create。2023.08.31 新增请求参数 data_creator |

### 请求参数

| 参数 | 类型 | 必需 | 说明 | 默认 |
|------|------|------|------|------|
| app_id | String | 是 | 应用ID | |
| entry_id | String | 是 | 表单ID | |
| data_list | Array | 是 | 数据内容数组 | |
| data_creator | String | 否 | 数据提交人（取成员编号 username，可从通讯录接口获取）。**注：不能使用互联组织中外部对接人的 username** | 企业创建者 |
| transaction_id | String | 否 | 事务ID；用于表示一次事务，用于防止因重试而导致重复创建同一批数据，也用于绑定一批文件，建议使用 UUID | |
| is_start_workflow | Bool | 否 | 是否发起流程（仅流程表单有效） | false |

### 请求示例

```json
{
    "app_id": "59264073a2a60c0c08e20bfb",
    "entry_id": "59264073a2a60c0c08e20bfd",
    "transaction_id": "87cd7d71-c6df-4281-9927-469094395677",
    "data_list": [
        {
            "_widget_1432728651402": {"value": "简道云1"},
            "_widget_1432728651403": {"value": 100},
            "_widget_1528854613291": {"value": [{"_widget_1528854614409": {"value": "子表单数据11"}, "_widget_1528854615499": {"value": 1001}}]}
        },
        {
            "_widget_1432728651402": {"value": "简道云2"},
            "_widget_1432728651403": {"value": 200}
        },
        {
            "_widget_1432728651402": {"value": "简道云3"},
            "_widget_1432728651403": {"value": 300}
        }
    ],
    "is_start_workflow": true
}
```

### 响应参数

| 参数 | 类型 | 说明 |
|------|------|------|
| status | String | 返回请求结果 |
| success_count | Number | 该 transaction_id 创建成功的数据条数 |
| success_ids | Array | 本次请求创建成功的数据的 ID 列表 |

### 响应示例

```json
{
    "status": "success",
    "success_count": 3,
    "success_ids": [
        "200001181fe09728936510eb",
        "200001181fe09728936510ec",
        "200001181fe09728936510ed"
    ]
}
```

### 注意事项

- 创建多条数据接口最多支持 **100** 条数据。
- 新建多条数据，部分数据新建时可能出现失败的情况。处理方法：使用同一个 transaction_id 再次请求新建多条，传入全部数据。传入后，第二次执行的数据将会完全覆盖掉第一次执行的数据。
- transaction_id 的有效期为 1 小时。1 小时内传入相同的 id 将按照同一批任务处理，会覆盖掉前一次的数据；超过 1 小时后不会按照同一批任务处理，将会创建一批新数据。
- 如果请求中指定了 data_creator，则关联触发的以下成员也会被记录为 data_creator：智能助手执行人、流程发起人、由跟进记录关联修改的客户表/线索表/商机表的修改人、由商机表关联修改的客户表的修改人。

---

## 8. 修改单条数据接口

**接口名称**：修改单条数据接口

**接口简介**：通过修改单条数据接口，可以对指定的单条数据进行修改。

**请求地址**：`https://api.jiandaoyun.com/api/v5/app/entry/data/update`

**请求方式**：POST

**请求频率**：20 次/秒

### 接口版本

| 接口版本 | 更新时间 | 版本说明 |
|---------|---------|--------|
| v1 | 2018.6.21 | 部门和成员均使用_id为主键 |
| v2 | 2019.6.21 | 成员字段使用 username 为主键，部门字段使用 dept_no 为主键 |
| v3 | 2021.3.31 | 子表单新增数据 ID 参数 |
| v4 | 2022.4.21 | 新增互联组织部门/成员获取，新增 type 参数类型：0（内部）、2（外部） |
| v5 | 2022.10.28 | 接口请求频率由 5 次/秒提升至 20 次/秒；参数 app_id 和 entry_id 放入 body，接口路由修改为 POST app/entry/data/update |

### 请求参数

| 参数 | 类型 | 必需 | 说明 | 默认 |
|------|------|------|------|------|
| app_id | String | 是 | 应用ID | |
| entry_id | String | 是 | 表单ID | |
| data_id | String | 是 | 数据 ID | |
| data | JSON | 是 | 数据内容，其他同新建单条数据接口，子表单需要注明子表单数据 ID | |
| is_start_trigger | Bool | 否 | 是否触发智能助手 | false |
| transaction_id | String | 否 | 事务 ID；用于绑定一批上传的文件。若数据中包含附件或图片控件，则 transaction_id 必须与「获取文件上传凭证和上传地址接口」中的 transaction_id 参数相同 | |

### 请求示例

```json
{
    "app_id": "604eb6eea71d720006e1336e",
    "entry_id": "604ecfca8e2ade077c72453a",
    "transaction_id": "87cd7d71-c6df-4281-9927-469094395677",
    "data_id": "6052e8072315c0075001d65e",
    "data": {
        "_widget_1615777739654": {"value": "张三"},
        "_widget_1615777739673": {
            "value": [
                {
                    "_widget_1615777739744": {"value": "张三"}
                },
                {
                    "_id": {"value": "606290aba392ca00076da0a9"},
                    "_widget_1615777739744": {"value": "李四"}
                }
            ]
        }
    }
}
```

### 响应参数

| 参数 | 类型 | 说明 |
|------|------|------|
| data | JSON | 返回修改后的完整数据，内容同查询单条数据接口 |

### 响应示例

```json
{
    "data": {
        "_id": "6052e8072315c0075001d65e",
        "appId": "604eb6eea71d720006e1336e",
        "entryId": "604ecfca8e2ade077c72453a",
        "creator": {
            "name": "小简",
            "username": "xiaojian",
            "status": 1,
            "type": 0,
            "departments": [1, 3],
            "integrate_id": "xiaojian"
        },
        "createTime": "2017-10-20T22:41:51.430Z",
        "updateTime": "2017-10-20T11:12:15.293Z"
    }
}
```

### 注意事项

- 使用 API 修改数据时，会触发的事件有新数据提交提醒、聚合表计算&校验、数据操作日志、数据量统计。但是不会触发重复值校验、必填校验。
- 系统字段和以下所列举的字段不支持添加和修改数据：分割线、手写签名、选择数据、查询、流水号（提交后系统生成）
- **子表单为整体覆盖，不是增量合并。** 调用 v3/v4/v5 修改单条数据时，只要 data 里带了子表单字段：
  - 每次调用会**清空**该条数据原本的子表单数据，填入本次请求的子表单数据；
  - 给**未传递** `_id` 或**传递了错误** `_id` 的子表单行**生成新的子表单数据 ID**（表现为该行被重建，不是追加一行）；
  - 数据管理的数据日志会记录「子表单变更」，即使子表单内容没有任何变化。
  - 传递了**正确** `_id` 的行，维持原 `_id` 不变；仅重置未传/传错的那些，调用一次重置一次。
  - v1、v2 接口不发生此变化。
- **子表单及子字段必须整体请求和修改**，不支持按子表单数据 ID 只改某一行，也不支持按子字段 ID 只改某个子字段：
  - 原有 3 行、请求里只写 2 行 → 即使这 2 行 `_id` 都传对，修改后也只剩 2 行；
  - 某行原有 3 个子字段、请求里只写 2 个 → 即使字段 ID 都传对，修改后该行也只剩 2 个子字段。

---

## 9. 修改多条数据接口

**接口名称**：修改多条数据接口

**接口简介**：通过修改多条数据接口，可以批量修改多条数据。

**请求地址**：`https://api.jiandaoyun.com/api/v5/app/entry/data/batch_update`

**请求方式**：POST

**请求频率**：10 次/秒

### 接口版本

| 接口版本 | 更新时间 | 版本说明 |
|---------|---------|--------|
| v1 | 2021.12.30 | 原始接口 |
| v5 | 2022.10.28 | 接口请求频率由 5 次/秒提升至 10 次/秒；参数 app_id 和 entry_id 放入 body，接口路由修改为 POST app/entry/data/batch_update |

### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| app_id | String | 是 | 应用ID |
| entry_id | String | 是 | 表单ID |
| data_ids | Array | 是 | 要更新的数据 ID 数组 |
| data | JSON | 是 | 数据内容，暂不支持子表单 |
| transaction_id | String | 否 | 事务 ID；用于绑定一批上传的文件 |

### 请求示例

```json
{
    "app_id": "59264073a2a60c0c08e20bfb",
    "entry_id": "59264073a2a60c0c08e20bfd",
    "transaction_id": "87cd7d71-c6df-4281-9927-469094395677",
    "data_ids": [
        "200001181fe09728936510eb",
        "200001181fe09728936510ec",
        "200001181fe09728936510ed"
    ],
    "data": {
        "_widget_1432728651402": {"value": "简道云1"},
        "_widget_1432728651403": {"value": 100}
    }
}
```

### 响应参数

| 参数 | 类型 | 说明 |
|------|------|------|
| status | String | 返回请求结果 |
| success_count | Number | 修改成功的数据条数 |

### 响应示例

```json
{
    "status": "success",
    "success_count": 3
}
```

### 注意事项

- 修改多条数据接口暂不支持子表单。
- 最多支持修改 100 条数据。
- 附件和图片字段更新时会清除字段中原有的文件。
- 修改多条数据是指把多条数据的字段修改成一个固定值。

---

## 10. 删除单条数据接口

**接口名称**：删除单条数据接口

**接口简介**：通过删除单条数据接口，可以对指定的数据进行删除。

**请求地址**：`https://api.jiandaoyun.com/api/v5/app/entry/data/delete`

**请求方式**：POST

**请求频率**：20 次/秒

### 接口版本

| 接口版本 | 更新时间 | 版本说明 |
|---------|---------|--------|
| v1 | 2018.6.21 | 原始接口 |
| v5 | 2022.10.28 | 接口请求频率由 5 次/秒提升至 20 次/秒；参数 app_id 和 entry_id 放入 body，接口路由修改为 POST app/entry/data/delete |

### 请求参数

| 参数 | 类型 | 必需 | 说明 | 默认 |
|------|------|------|------|------|
| app_id | String | 是 | 应用ID | |
| entry_id | String | 是 | 表单ID | |
| data_id | String | 是 | 数据 ID | |
| is_start_trigger | Bool | 否 | 是否触发智能助手 | false |

### 请求示例

```json
{
    "app_id": "59264073a2a60c0c08e20bfb",
    "entry_id": "59264073a2a60c0c08e20bfd",
    "data_id": "6052e8072315c0075001d65e"
}
```

### 响应参数

| 参数 | 类型 | 说明 |
|------|------|------|
| status | String | 返回请求结果 |

### 响应示例

```json
{
    "status": "success"
}
```

---

## 11. 删除多条数据接口

**接口名称**：删除多条数据接口

**接口简介**：通过删除多条数据接口，可以批量删除数据。

**请求地址**：`https://api.jiandaoyun.com/api/v5/app/entry/data/batch_delete`

**请求方式**：POST

**请求频率**：10 次/秒

### 接口版本

| 接口版本 | 更新时间 | 版本说明 |
|---------|---------|--------|
| v1 | 2022.6.14 | 原始接口 |
| v5 | 2022.10.28 | 接口请求频率由 5 次/秒提升至 10 次/秒；参数 app_id 和 entry_id 放入 body，接口路由修改为 POST app/entry/data/batch_delete |

### 请求参数

| 参数 | 必须 | 类型 | 说明 |
|------|------|------|------|
| app_id | 是 | String | 应用ID |
| entry_id | 是 | String | 表单ID |
| data_ids | 是 | String[] | 要删除的数据ID数组 |

### 请求示例

```json
{
    "app_id": "59264073a2a60c0c08e20bfb",
    "entry_id": "59264073a2a60c0c08e20bfd",
    "data_ids": [
        "200001181fe09728936510eb",
        "200001181fe09728936510ec",
        "200001181fe09728936510ed"
    ]
}
```

### 响应参数

| 参数 | 类型 | 说明 |
|------|------|------|
| status | String | 成功返回'success' |
| success_count | Number | 删除成功的数据条数 |

### 响应示例

```json
{
    "status": "success",
    "success_count": 3
}
```

### 注意事项

- 删除多条数据接口一次最多支持删除 100 条数据。


---

## 四、文件接口（详细）

### 4.1 获取文件上传凭证和上传地址

- **请求地址**：`POST https://api.jiandaoyun.com/api/v5/app/entry/file/get_upload_token`
- **频率**：20 次/秒
- **说明**：每次获取 100 个上传凭证，文件与 `transaction_id` 绑定

**请求参数**：

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| app_id | String | 是 | 应用 ID |
| entry_id | String | 是 | 表单 ID |
| transaction_id | String | 是 | 事务 ID（推荐 UUID，不允许含 `${var}`、`$(var)`、`$(var}`、`${var)` 模式） |

**请求示例**：

```json
{
  "app_id": "59264073a2a60c0c08e20bfb",
  "entry_id": "59264073a2a60c0c08e20bfd",
  "transaction_id": "87cd7d71-c6df-4281-9927-469094395677"
}
```

**响应参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| token_and_url_list | JSON | 文件上传凭证和上传地址 |
| token_and_url_list[].url | String | 文件上传地址 |
| token_and_url_list[].token | String | 文件上传凭证 |

**响应示例**：

```json
{
  "token_and_url_list": [
    {
      "url": "https://upload.qiniup.com",
      "token": "bM7UwVPyBBdPaleBZt21SWKzMy2qPUpn-05jZlas:ELIqACNut-t52UMPD-DZNrX8hTU=:eyJmc2l6ZU1pbiI6..."
    }
  ]
}
```

### 4.2 文件上传

- **请求地址**：`POST {url}`（上一步获取的 url）
- **频率**：20 次/秒
- **格式**：`form-data`
- **说明**：一个 token 只能上传一个文件，不允许覆盖

**请求参数**：

| 参数 | 必需 | 类型 | 说明 |
|------|------|------|------|
| token | 是 | String | 上传凭证 |
| file | 是 | 文件 | 要上传的文件（必须作为最后一个参数，需正确指定 mime 类型） |

**响应参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| key | String | 文件 key |

**响应示例**：

```json
{
  "key": "6b559cf1-b16c-43bd-a211-8fa8fdeae2ef"
}
```

返回的 `key` 用于创建/修改接口中填写附件或图片控件值。

### 4.3 注意事项

- token 有效时间 **1 小时**
- transaction_id 有效时间 **1 小时**，失效后 key 也无法使用
- 上传 PDF 文件需要指定 mime 为 `application/pdf`




---

## 五、流程接口（详细）


# 简道云流程接口 API 文档

---

## 1. 查询流程实例审批意见

- **接口名称**: 查询流程实例审批意见
- **请求地址**: `https://api.jiandaoyun.com/api/v1/app/{app_id}/entry/{entry_id}/data/{data_id}/approval_comments`
- **请求方式**: POST
- **请求频率**: 30 次/秒
- **接口版本**: v1 (2020.7.7 原始接口)

### URL 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| appId | String | 应用 ID |
| entryId | String | 表单 ID |
| dataId | String | 流程表单数据 ID |

### Body 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| skip | Number | 偏移量，即跳过多少条审批意见。每次最多返回 100 条，查询第 100 条之后设为 100，第 200 条之后设为 200，以此类推 |

### 响应参数

| 属性 | 类型 | 说明 |
|------|------|------|
| approveCommentList | [JSON] | 审批意见列表 |
| approveCommentList[*].flowNodeName | String | 流程节点名称 |
| approveCommentList[*].flowAction | String | 动作枚举: forward-提交, transfer-转交, back-回退, close-结束, sign_before-前加签, sign_after-后加签, sign_parallel-添加审批人 |
| approveCommentList[*].comment | String | 审批意见评论 |
| approveCommentList[*].signature_url? | String | 审批意见手写签名 URL, 可选, 15 天有效期 |

### 响应示例

```json
{
  "approveCommentList": [
    {
      "operator": {
        "_id": "5ed78abead7b951a243cc828",
        "username": "jdy-y69rlimdfquz",
        "status": 1,
        "name": "AngelMsger"
      },
      "flowAction": "forward",
      "comment": "一条审批意见",
      "flowNodeName": "必须手写签名",
      "signature_url": "https://files.jiandaoyun.com/FtMNaGofTPeLMFW5_5SCs8w2mX8h?e=1595347199&token=..."
    }
  ]
}
```

---

## 2. 查询流程实例信息

- **接口名称**: 查询流程实例信息
- **请求地址**: `https://api.jiandaoyun.com/api/v6/workflow/instance/get`
- **请求方式**: POST
- **请求频率**: 30 次/秒
- **接口版本**: v1(2022.10.28) → v6(2024.12.26)

### 版本说明
- v1 2022.10.28: 原始接口
- V2 2023.03.02: 新增 app_id；entry_id 变更为 form_id
- V3 2023.04.17: 新增 url、tasks[].app_id/form_id/form_title/instance_id/task_id/url/creator；node_list 变更为 tasks；assignee_list 变更为 tasks[].assignee
- V4 2023.09.18: 新增 tasks_type 请求参数；新增 finish_time、tasks[].title/create_time/finish_time/status
- V5 2023.12.01: 新增 tasks[].create_action、tasks[].finish_action
- v6 2024.12.26: 新增 result；tasks[].finish_action 新增 reject

### 请求参数

| 参数 | 必须 | 类型 | 说明 |
|------|------|------|------|
| instance_id | 是 | String | 实例 id，同 data_id |
| tasks_type | 否 | number | 返回待办种类，0 表示不返回；1 表示全部返回 |

### 请求示例

```json
{
  "instance_id": "63ff32d918fbc20007a4a082",
  "tasks_type": 1
}
```

### 响应参数

| 参数 | 类型 | 说明 |
|------|------|------|
| app_id | String | 应用 id |
| form_id | String | 表单 id |
| form_title | String | 表单名称 |
| instance_id | String | 实例 id |
| url | String | 实例访问链接 |
| update_time | String | 实例修改时间 |
| create_time | String | 创建时间 |
| finish_time | String | 结束时间 |
| creator | Object | 创建者信息（同成员实体结构） |
| status | Number | 实例状态: 0-进行中, 1-流程已完成（含流程否决）, 2-手动结束 |
| result | Number | 审批结果（仅已完成时存在）: 0-否决, 1-流转完成 |
| tasks | Object | 待办任务列表 |
| tasks[].app_id | String | 应用 id |
| tasks[].form_id | String | 表单 id |
| tasks[].form_title | String | 表单名称 |
| tasks[].title | String | 待办名称 |
| tasks[].instance_id | String | 实例 id |
| tasks[].task_id | String | 待办 id |
| tasks[].flow_id | Number | 节点 id |
| tasks[].flow_name | String | 节点名称 |
| tasks[].url | String | 待办访问链接 |
| tasks[].assignee | Object | 待办人信息（同成员实体结构） |
| tasks[].creator | Object | 实例创建者信息（同成员实体结构） |
| tasks[].create_time | String | 待办开始时间 |
| tasks[].create_action | String | 创建待办的流程动作: auto_approve/forward/back/transfer/revoke/activate/auto_forward/auto_back/batch_forward/batch_transfer/sign_before/sign_after/sign_parallel/invoke_plugin |
| tasks[].finish_time | String | 完成待办时间 |
| tasks[].finish_action | String | 完成待办的流程动作: auto_approve/forward/back/close/transfer/batch_forward/sign_after/reject |
| tasks[].status | Number | 待办状态: 0-进行中, 1-已完成, 2-手动结束, 4-被激活, 5-任务被暂停 |

### 响应示例

```json
{
  "app_id": "628d8c0d73544c0006a54bfd",
  "form_id": "63f31ae8144f4a09ec197163",
  "form_title": "物品信息借用",
  "instance_id": "63ff32d918fbc20007a4a082",
  "url": "https://www.jiandaoyun.com/workflow/process_instance/63ff32d918fbc20007a4a082",
  "update_time": "2022-10-26T13:18:57.605Z",
  "create_time": "2022-10-26T13:11:45.087Z",
  "finish_time": null,
  "status": 0,
  "creator": {
    "username": "xiaojian",
    "name": "小简",
    "departments": [1],
    "type": 0,
    "status": 1
  },
  "tasks": [
    {
      "app_id": "628d8c0d73544c0006a54bfd",
      "form_id": "63f31ae8144f4a09ec197163",
      "form_title": "物品信息借用",
      "title": "流程发起节点",
      "instance_id": "63ff32d918fbc20007a4a082",
      "task_id": "63f31ae8144f4a09ec197162",
      "flow_id": 0,
      "flow_name": "流程发起节点",
      "url": "https://www.jiandaoyun.com/workflow/process_instance/63ff32d918fbc20007a4a082/task/63f31ae8144f4a09ec197162",
      "assignee": { "username": "xiaoyun", "name": "小云", "departments": [1], "type": 0, "status": 1 },
      "creator": { "username": "xiaojian", "name": "小简", "departments": [1], "type": 0, "status": 1 },
      "create_time": "2022-10-26T13:11:45.087Z",
      "create_action": "forward",
      "finish_time": "2022-10-26T13:11:45.087Z",
      "finish_action": "forward",
      "status": 1
    }
  ]
}
```

### 注意事项

部分流程动态，如子流程、插件节点以及抄送节点，无法用该接口获取到。

---

## 3. 查询流程日志

- **接口名称**: 查询流程日志
- **请求地址**: `https://api.jiandaoyun.com/api/v1/workflow/instance/logs`
- **请求方式**: POST
- **请求频率**: 30 次/秒
- **接口版本**: v1 (2024.01.19 原始接口)
- **说明**: 目前仅支持返回包含审批意见的流程日志

### 请求参数

| 参数 | 必须 | 类型 | 说明 |
|------|------|------|------|
| instance_id | 是 | string | 实例 id，同 data_id |
| types | 是 | string[] | 返回的日志类型，可选项: 审批意见 "comment" |
| limit | 否 | number | 分页参数，页大小默认 100，最大 100 |
| skip | 否 | number | 分页参数，跳过前面数据条数，默认为 0 |

### 请求示例

```json
{
  "instance_id": "659cba93489a49c06f7d4281",
  "types": ["comment"],
  "skip": 0,
  "limit": 10
}
```

### 响应参数

| 参数 | 类型 | 说明 |
|------|------|------|
| logs | object[] | 日志列表 |
| logs[].flow_id | number | 节点 ID |
| logs[].flow_name | string | 节点名称 |
| logs[].create_action | string | 创建待办的流程动作 |
| logs[].create_time | Date | 待办开始时间 |
| logs[].finish_action | string | 完成待办的流程动作 |
| logs[].finish_time | Date | 待办完成时间 |
| logs[].comment | string | 审批意见内容 |
| logs[].signature | object | 审批意见手写签名 |
| logs[].signature.url | string | 审批意见手写签名URL，15 天有效期 |
| logs[].attachments | object[] | 附件列表 |
| logs[].attachments[].name | string | 附件文件名 |
| logs[].attachments[].size | number | 附件文件大小 |
| logs[].attachments[].mime | string | 附件文件类型 |
| logs[].attachments[].url | string | 附件文件URL，15 天有效期 |
| logs[].operator | object | 审批/操作人信息（同成员实体结构） |

### 响应示例

```json
{
  "logs": [
    {
      "flow_id": 1,
      "flow_name": "必须手写签名",
      "create_time": "2024-01-09T03:16:35.447Z",
      "create_action": "forward",
      "finish_time": "2024-01-09T03:17:03.239Z",
      "finish_action": "forward",
      "operator": { "username": "xiaojian", "name": "小简", "departments": [1], "type": 0, "status": 1 },
      "comment": "一条审批意见",
      "signature": { "url": "https://files.jiandaoyun.com/..." },
      "attachments": [
        { "name": "WechatIMG21.jpeg", "size": 74935, "mime": "image/jpeg", "url": "https://files.jiandaoyun.com/..." }
      ]
    }
  ]
}
```

---

## 4. 结束流程实例

- **接口名称**: 结束流程实例
- **请求地址**: `https://api.jiandaoyun.com/api/v1/workflow/instance/close`
- **请求方式**: POST
- **请求频率**: 20 次/秒
- **接口版本**: v1 (2022.10.28 原始接口)
- **说明**: 该接口用于管理员结束当前流程实例

### 请求参数

| 参数 | 必须 | 类型 | 说明 |
|------|------|------|------|
| instance_id | 是 | String | 实例 id，同 data_id。结束对应的流程实例 |

### 请求示例

```json
{
  "instance_id": "6358a65878b1fb0007aba61b"
}
```

### 响应参数

| 参数 | 类型 | 说明 |
|------|------|------|
| status | String | success：接口调用成功；failure：接口调用失败 |
| code | Number | 错误码 |
| message | String | 返回码的描述 |

### 响应示例

成功：
```json
{ "status": "success" }
```

失败：
```json
{ "code": 4008, "message": "操作失败,流程已经关闭", "status": "failure" }
```

---

## 5. 激活流程实例

- **接口名称**: 激活流程实例
- **请求地址**: `https://api.jiandaoyun.com/api/v1/workflow/instance/activate`
- **请求方式**: POST
- **请求频率**: 20 次/秒
- **接口版本**: v1 (2023.08.01 原始接口)
- **说明**: 流程激活接口用于激活当前流程实例

### 请求参数

| 参数 | 必须 | 类型 | 说明 |
|------|------|------|------|
| instance_id | 是 | string | 激活对应的流程实例 |
| flow_id | 是 | number | 激活的节点 id |

### 请求示例

```json
{
  "instance_id": "64c7274cd172150007f2533d",
  "flow_id": 1
}
```

### 响应参数

| 参数 | 类型 | 说明 |
|------|------|------|
| status | string | success 表示接口调用成功；failure 表示接口调用失败 |
| code | number | 错误码（仅 failure 时返回） |
| message | string | 返回码的描述（仅 failure 时返回） |

### 响应示例

```json
{ "status": "success" }
```

---

## 6. 查询我的待办

- **接口名称**: 查询我的待办
- **请求地址**: `https://api.jiandaoyun.com/api/v6/workflow/task/list`
- **请求方式**: POST
- **请求频率**: 20 次/秒
- **接口版本**: v1(2022.10.12) → v6(2026.05.28)

### 版本说明
- v1 2022.10.12: 原始接口
- v1 2022.10.28: 频率由 5 次/秒调整为 30 次/秒
- v2 2023.03.02: 新增 tasks[].app_id/form_id；调整 tasks[].task_id 名称为待办 id
- v3 2023.03.17: 新增 flow_id、flow_name
- v4 2023.09.18: 新增 tasks[].create_time/finish_time/status
- v5 2023.12.01: 新增 tasks[].create_action/finish_action
- v6 2026.05.28: 取消分页参数 skip；新增请求参数 task_id；频率由 30 次/秒调整为 20 次/秒

### 请求参数

| 参数 | 必须 | 类型 | 说明 |
|------|------|------|------|
| username | 是 | String | 用户名，即成员编号 |
| limit | 否 | Number | 分页参数，页大小默认 10 最大 100 |
| task_id | 否 | Number | 分页符，上一次查询待办列表时最后一条数据的 task_id，没有则留空 |

### 请求示例

```json
{
  "username": "xiaoyun",
  "task_id": "63f31ae8144f4a09ec197163",
  "limit": 10
}
```

### 响应参数

| 参数 | 类型 | 说明 |
|------|------|------|
| has_more | Boolean | 后面是否还有数据 |
| tasks | Object[] | 待办列表 |
| tasks[].app_id | String | 应用 id |
| tasks[].form_id | String | 表单 id |
| tasks[].task_id | String | 待办 id |
| tasks[].instance_id | String | 实例 id，同 data_id |
| tasks[].form_title | String | 表单名称 |
| tasks[].title | String | 待办名称 |
| tasks[].flow_id | Number | 节点 id |
| tasks[].flow_name | String | 节点名称 |
| tasks[].url | String | 待办访问链接 |
| tasks[].assignee | Object | 待办人信息（同成员实体结构） |
| tasks[].creator | Object | 待办创建者信息（同成员实体结构） |
| tasks[].create_time | String | 待办开始时间 |
| tasks[].create_action | String | 创建待办的流程动作: auto_approve/forward/back/transfer/revoke/activate/auto_forward/auto_back/batch_forward/batch_transfer/sign_before/sign_after/sign_parallel/invoke_plugin |
| tasks[].finish_time | String | 待办结束时间 |
| tasks[].finish_action | String | 完成待办的流程动作，恒为 null |
| tasks[].status | Number | 待办状态，恒为 0（进行中） |

### 响应示例

```json
{
  "has_more": false,
  "tasks": [
    {
      "app_id": "628d8c0d73544c0006a54bfd",
      "task_id": "63f31ae8144f4a09ec197163",
      "form_id": "63ff33531c2f7e5fe8789b4b",
      "instance_id": "628d8c0d73544c0006a54bfc",
      "form_title": "待办测试表单标题",
      "title": "待办标题",
      "flow_id": 1,
      "flow_name": "节点1",
      "url": "",
      "assignee": { "username": "xiaoyun", "name": "小云", "departments": [1, 3], "type": 0, "status": 1, "integrate_id": "xiaoyun" },
      "creator": { "username": "xiaojian", "name": "小简", "departments": [1, 3], "type": 0, "status": 1, "integrate_id": "xiaojian" },
      "create_time": "2022-10-26T13:18:57.605Z",
      "create_action": "forward",
      "finish_time": null,
      "finish_action": null,
      "status": 0
    }
  ]
}
```

---

## 7. 流程待办提交

- **接口名称**: 流程待办提交
- **请求地址**: `https://api.jiandaoyun.com/api/v1/workflow/task/approve`
- **请求方式**: POST
- **请求频率**: 20 次/秒
- **接口版本**: v1 (2022.10.28 原始接口)

### 请求参数

| 参数 | 必须 | 类型 | 说明 |
|------|------|------|------|
| username | 是 | String | 用户名，即成员编号 |
| instance_id | 是 | String | 实例 id，同 data_id |
| task_id | 是 | String | 任务 id（需要和 username 一一对应） |
| comment | 否 | String | 审批意见 |

### 请求示例

```json
{
  "username": "xiaoyun",
  "instance_id": "6358a65878b1fb0007aba61b",
  "task_id": "6358a65878b1fb0007aba63c"
}
```

### 响应参数

| 参数 | 类型 | 说明 |
|------|------|------|
| status | String | success：接口调用成功；failure：接口调用失败 |
| code | Number | 错误码 |
| message | String | 返回码的描述 |

### 响应示例

成功：
```json
{ "status": "success" }
```

失败：
```json
{ "code": 1010, "message": "用户不存在", "status": "failure" }
```

---

## 8. 流程待办回退

- **接口名称**: 流程待办回退
- **请求地址**: `https://api.jiandaoyun.com/api/v2/workflow/task/rollback`
- **请求方式**: POST
- **请求频率**: 20 次/秒
- **接口版本**: v1(2022.10.28) → v2(2025.12.17 新增 back_type)

### 请求参数

| 参数 | 必须 | 类型 | 说明 |
|------|------|------|------|
| username | 是 | String | 用户名，即成员编号 |
| instance_id | 是 | String | 实例 id，同 data_id |
| task_id | 是 | String | 任务 id（需要和 username 一一对应） |
| flow_id | 否 | Number | 回退目标节点：节点配置为回退到指定节点时需要设置；配置为回退到上一节点时无需设置 |
| comment | 否 | String | 审批意见 |
| back_type | 否 | Number | 回退人选择（节点配置「回退人选择」时需要）: 1-正常流转, 2-直达目标节点 |

### 请求示例

```json
{
  "username": "xiaojian",
  "instance_id": "635919d1a2cca9000734511c",
  "task_id": "635919d1a2cca9000734513b",
  "comment": "回退",
  "back_type": 1
}
```

### 响应参数

| 参数 | 类型 | 说明 |
|------|------|------|
| status | String | success：接口调用成功；failure：接口调用失败 |
| code | Number | 错误码 |
| message | String | 返回码的描述 |

### 响应示例

成功：
```json
{ "status": "success" }
```

失败：
```json
{ "code": 1010, "message": "用户不存在", "status": "failure" }
```

---

## 9. 流程待办转交

- **接口名称**: 流程待办转交
- **请求地址**: `https://api.jiandaoyun.com/api/v1/workflow/task/transfer`
- **请求方式**: POST
- **请求频率**: 20 次/秒
- **接口版本**: v1 (2022.10.28 原始接口)

### 请求参数

| 参数 | 必须 | 类型 | 说明 |
|------|------|------|------|
| username | 是 | String | 用户名，即成员编号。**注：此处用户名指的是当前节点的负责人，而非流程表单的创建者** |
| instance_id | 是 | String | 实例 id，同 data_id |
| task_id | 是 | String | 任务 id（需要和 username 一一对应） |
| transfer_username | 是 | String | 转交用户 |
| comment | 否 | String | 审批意见 |

### 请求示例

```json
{
  "username": "xiaoyun",
  "instance_id": "6358af7c1f4eab0007704076",
  "task_id": "6358af8446f8db00072d6121",
  "transfer_username": "xiaojian"
}
```

### 响应参数

| 参数 | 类型 | 说明 |
|------|------|------|
| status | String | success：接口调用成功；failure：接口调用失败 |
| code | Number | 错误码 |
| message | String | 返回码的描述 |

### 响应示例

成功：
```json
{ "status": "success" }
```

失败：
```json
{ "code": 1010, "message": "用户不存在", "status": "failure" }
```

---

## 10. 流程待办加签

- **接口名称**: 流程待办加签
- **请求地址**: `https://api.jiandaoyun.com/api/v2/workflow/task/add_sign`
- **请求方式**: POST
- **请求频率**: 20 次/秒
- **接口版本**: v1(2023.08.01) → v2(2026.06.12: add_sign_username 更名为 add_sign_usernames，类型更新为 string[])

### 请求参数

| 参数 | 必须 | 类型 | 说明 |
|------|------|------|------|
| instance_id | 是 | string | 对应的流程实例 |
| task_id | 是 | string | 待办实例 id |
| username | 是 | string | 待办对应的用户名 |
| comment | 否 | String | 审批意见（选填） |
| add_sign_type | 是 | number | 加签类型: 0-前加签, 1-后加签, 2-并加签 |
| add_sign_usernames | 是 | string[] | 被加签人的用户名 |

### 请求示例

```json
{
  "instance_id": "64c72a03561073000755afd8",
  "task_id": "64c72a03561073000755b001",
  "username": "jdy-90ahnts5a6rh",
  "comment": "Approval",
  "add_sign_type": 1,
  "add_sign_usernames": ["R-vmTE0o3N", "R-vmTE0o3P"]
}
```

### 响应参数

| 参数 | 类型 | 说明 |
|------|------|------|
| status | string | success 表示接口调用成功；failure 表示接口调用失败 |
| code | number | 错误码（仅 failure 时返回） |
| message | string | 返回码的描述（仅 failure 时返回） |

### 响应示例

```json
{ "status": "success" }
```

---

## 11. 流程待办撤回

- **接口名称**: 流程待办撤回
- **请求地址**: `https://api.jiandaoyun.com/api/v2/workflow/task/revoke`
- **请求方式**: POST
- **请求频率**: 20 次/秒
- **接口版本**: v1(2023.08.01) → v2(2026.04.21 新增 comment 撤回理由)

### 请求参数

| 参数 | 必须 | 类型 | 说明 |
|------|------|------|------|
| instance_id | 是 | string | 对应的流程实例 |
| task_id | 否 | string | 需要撤回的待办实例 id（是指之前进行提交操作过的待办 id，不是当前的待办实例 id，选填：不传默认进行发起节点的撤回操作） |
| username | 是 | string | 处理待办对应的用户名 |
| comment | 否 | string | 撤回理由。当流程节点为「仅允许发起节点撤回」，且流程流转到不与发起节点相连的节点时，发起人在发起节点撤回流程时必填撤回理由 |

### 请求示例

```json
{
  "instance_id": "64c72910561073000755af52",
  "task_id": "64c72910561073000755af7c",
  "username": "jdy-90ahnts5a6rh",
  "comment": "因XXX需要撤回至发起节点"
}
```

### 响应参数

| 参数 | 类型 | 说明 |
|------|------|------|
| status | string | success 表示接口调用成功；failure 表示接口调用失败 |
| code | number | 错误码（仅 failure 时返回） |
| message | string | 返回码的描述（仅 failure 时返回） |

### 响应示例

```json
{ "status": "success" }
```

---

## 12. 流程待办否决

- **接口名称**: 流程待办否决
- **请求地址**: `https://api.jiandaoyun.com/api/v1/workflow/task/reject`
- **请求方式**: POST
- **请求频率**: 20 次/秒
- **接口版本**: V1 (2024.12.26 原始接口)

### 请求参数

| 参数 | 必须 | 类型 | 说明 |
|------|------|------|------|
| instance_id | 是 | string | 对应的流程实例 |
| task_id | 是 | string | 待办实例 id |
| username | 是 | string | 待办对应的用户名 |
| comment | 否 | String | 审批意见（选填） |

### 请求示例

```json
{
  "instance_id": "64c72a03561073000755afd8",
  "task_id": "64c72a03561073000755b001",
  "username": "jdy-90ahnts5a6rh",
  "comment": "不同意"
}
```

### 响应参数

| 参数 | 类型 | 说明 |
|------|------|------|
| status | string | 请求结果状态: success-接口调用成功, failure-接口调用失败 |
| code | number | 错误码 |
| message | string | 错误码描述信息 |

### 响应示例

成功：
```json
{ "status": "success" }
```

失败：
```json
{ "status": "failure", "code": 5004, "message": "No comment for approval." }
```

---

## 13. 查询抄送列表

- **接口名称**: 查询抄送列表
- **请求地址**: `https://api.jiandaoyun.com/api/v1/workflow/cc/list`
- **请求方式**: POST
- **请求频率**: 5 次/秒
- **接口版本**: V1 (2025.07.22 原始接口)
- **说明**: 目前仅支持查询 90 天内的抄送数据

### 请求参数

| 参数 | 必须 | 类型 | 说明 |
|------|------|------|------|
| username | 是 | string | 用户名，即成员编号 |
| skip | 否 | number | 分页参数，跳过前面数据条数，默认 0 |
| limit | 否 | number | 分页参数，页大小默认 10，最大 100 |
| read_status | 否 | string | 已读状态: "read"-已读, "unread"-未读, "all"-全部（默认） |

### 请求示例

```json
{
  "username": "xiaoyun",
  "skip": 0,
  "limit": 1,
  "read_status": "all"
}
```

### 响应参数

| 参数 | 类型 | 说明 |
|------|------|------|
| has_more | boolean | 后面是否还有数据 |
| cc_list | object[] | 抄送列表（仅支持查询 90 天内的抄送数据） |
| cc_list[].app_id | string | 应用 ID |
| cc_list[].form_id | string | 表单 ID |
| cc_list[].task_id | string | 抄送 ID |
| cc_list[].instance_id | string | 实例 ID，同数据 ID |
| cc_list[].form_title | string | 表单名称 |
| cc_list[].title | string | 提醒标题（节点名称） |
| cc_list[].flow_id | number | 节点 ID |
| cc_list[].flow_name | string | 节点名称 |
| cc_list[].url | string | 抄送访问链接 |
| cc_list[].assignee | object | 抄送人（同成员实体结构） |
| cc_list[].creator | object | 流程发起人（同成员实体结构） |
| cc_list[].create_time | Date | 流程发起时间 |
| cc_list[].status | number | 状态: 0-未读, 1-已读 |
| cc_list[].start_time | Date | 提醒创建时间 |
| cc_list[].start_action | string | 创建提醒的流程动作 |
| cc_list[].finish_time | Date | 标记已读时间，仅 status 为 1 时存在 |

### 响应示例

```json
{
  "cc_list": [
    {
      "app_id": "67c1584ea70e38aa41a9b466",
      "form_id": "67c1649dfee1fc583c98be20",
      "task_id": "67c164a8fee1fc583c98be7f",
      "instance_id": "67c164a8fee1fc583c98be59",
      "form_title": "抄送全部已读",
      "title": "节点1",
      "flow_id": 1,
      "flow_name": "节点1",
      "url": "https://www.jiandaoyun.com/workflow/process_instance/67c164a8fee1fc583c98be59/task/67c164a8fee1fc583c98be7f",
      "assignee": { "username": "xiaoyun", "name": "小云", "departments": [1, 3], "type": 0, "status": 1, "integrate_id": "xiaoyun" },
      "creator": { "username": "xiaojian", "name": "小简", "departments": [1, 3], "type": 0, "status": 1, "integrate_id": "xiaojian" },
      "create_time": "2025-02-28T07:24:24.321Z",
      "status": 1,
      "start_time": "2025-02-28T07:24:24.323Z",
      "finish_time": "2025-02-28T07:24:27.608Z",
      "start_action": "forward"
    }
  ],
  "has_more": true
}
```



---

## 六、通讯录 - 成员与部门接口（详细）


# 简道云成员与部门 API 接口文档

---

## 1. 获取成员信息接口

- **接口名称**：获取成员信息接口
- **请求地址**：`https://api.jiandaoyun.com/api/v5/corp/user/get`
- **请求方式**：POST
- **请求频率**：30 次/秒
- **简介**：根据 username 获取指定成员的名称和部门编号。支持公共模式和集成模式。

### 请求参数

| 参数 | 必需 | 类型 | 说明 |
|------|------|------|------|
| username | 是 | String | 成员编号 |

### 请求示例

```json
{
  "username": "jiandaoyun"
}
```

### 响应参数

| 参数 | 含义 |
|------|------|
| user | 成员信息，同单个成员的返回数据结构 |

### 响应示例

```json
{
  "user": {
    "username": "jiandaoyun",
    "name": "小云",
    "departments": [1, 3],
    "type": 0,
    "status": 1,
    "integrate_id": "jiandaoyun"
  }
}
```

### 版本说明

| 版本 | 更新时间 | 说明 |
|------|----------|------|
| v1 | 2018.12.4 | 使用 _id 作为 id |
| v2 | 2019.6.21 | 使用 username 作为 id |
| v4 | 2022.6.30 | 返回值新增字段 type、status、integrate_id |
| v5 | 2022.10.28 | 频率提升至 30 次/秒；参数 username 放入 body，路由改为 POST corp/user/get |

---

## 2. 添加成员接口

- **接口名称**：添加成员接口
- **请求地址**：`https://api.jiandaoyun.com/api/v5/corp/user/create`
- **请求方式**：POST
- **请求频率**：20 次/秒
- **简介**：在指定部门下添加一位成员，该成员用户自动激活（可直接通过单点登录进行访问，并且会占用1个用户数），但是没有手机、邮箱和密码等个人注册信息。仅支持公共模式。

### 请求参数

| 参数 | 是否必需 | 类型 | 说明 |
|------|----------|------|------|
| name | 是 | String | 昵称 |
| departments | 否 | Number[] | 用户所属部门列表 |
| username | 否 | String | 成员编号（成员编号仅支持字母、数字和下划线） |

### 请求示例

```json
{
  "username": "jiandaoyun",
  "name": "小云",
  "departments": [1, 3]
}
```

### 响应参数

| 参数 | 类型 | 说明 |
|------|------|------|
| user | Json | 新添加的该成员信息，同单个成员的返回数据结构 |

### 响应示例

```json
{
  "user": {
    "username": "jiandaoyun",
    "name": "小云",
    "departments": [1, 3],
    "type": 0,
    "status": 1
  }
}
```

### 注意事项

自 2024.01.19 起，本接口会对传入的 departments 做**部门存在性校验**：若列表中含不存在的部门，则添加成员失败，并在错误信息中返回不存在的部门编号。

### 版本说明

| 版本 | 更新时间 | 说明 |
|------|----------|------|
| v1 | 2018.12.4 | 使用 _id 作为 id |
| v2 | 2019.6.21 | 使用 username 作为 id |
| v4 | 2022.6.30 | 返回值新增字段 type、status、integrate_id |
| v5 | 2022.10.28 | 频率提升至 20 次/秒；路由改为 POST corp/user/create |

---

## 3. 修改成员接口

- **接口名称**：修改成员接口
- **请求地址**：`https://api.jiandaoyun.com/api/v5/corp/user/update`
- **请求方式**：POST
- **请求频率**：20 次/秒
- **简介**：修改指定成员的信息，比如部门、昵称。仅支持公共模式。
- **注意**：成员编号不允许修改。

### 请求参数

| 参数 | 是否必需 | 类型 | 说明 |
|------|----------|------|------|
| username | 是 | String | 成员编号 |
| name | 否 | String | 昵称 |
| departments | 否 | Number[] | 用户所属部门列表 |

### 请求示例

```json
{
  "username": "jiandaoyun",
  "name": "小云",
  "departments": [4]
}
```

### 响应参数

| 参数 | 类型 | 说明 |
|------|------|------|
| user | Json | 修改后的该成员信息，同单个成员的返回数据结构 |

### 响应示例

```json
{
  "user": {
    "username": "jiandaoyun",
    "name": "小云",
    "departments": [1, 3],
    "type": 0,
    "status": 1
  }
}
```

### 版本说明

| 版本 | 更新时间 | 说明 |
|------|----------|------|
| v1 | 2018.12.4 | 使用 _id 作为 id |
| v2 | 2019.6.21 | 使用 username 作为 id |
| v4 | 2022.6.30 | 返回值新增字段 type、status、integrate_id |
| v5 | 2022.10.28 | 频率提升至 20 次/秒；参数 username 放入 body，路由改为 POST corp/user/update |

---

## 4. 删除成员接口

- **接口名称**：删除成员接口
- **请求地址**：`https://api.jiandaoyun.com/api/v5/corp/user/delete`
- **请求方式**：POST
- **请求频率**：20 次/秒
- **简介**：从通讯录中删除指定成员编号的用户。仅支持公共模式。

### 请求参数

| 参数 | 必需 | 类型 | 说明 |
|------|------|------|------|
| username | 是 | String | 成员编号 |

### 请求示例

```json
{
  "username": "jiandaoyun"
}
```

### 响应参数

| 参数 | 类型 | 说明 |
|------|------|------|
| status | String | 返回请求结果 |

### 响应示例

```json
{
  "status": "success"
}
```

### 注意事项

删除成员即将在职成员转离职，并不是彻底删除。转离职成员可以在离职成员管理页面进行管理。

### 版本说明

| 版本 | 更新时间 | 说明 |
|------|----------|------|
| v1 | 2018.12.4 | 使用 _id 作为 id |
| v2 | 2019.6.21 | 使用 username 作为 id |
| v4 | 2022.6.30 | 返回值新增字段 type、status、integrate_id |
| v5 | 2022.10.28 | 频率提升至 20 次/秒；参数 username 放入 body，路由改为 POST corp/user/delete |

---

## 5. 批量删除成员接口

- **接口名称**：批量删除成员接口
- **请求地址**：`https://api.jiandaoyun.com/api/v5/corp/user/batch_delete`
- **请求方式**：POST
- **请求频率**：10 次/秒
- **简介**：对成员进行批量删除。仅支持公共模式。

### 请求参数

| 参数 | 是否必需 | 类型 | 说明 |
|------|----------|------|------|
| usernames | 是 | Array | 成员编号列表 |

### 请求示例

```json
{
  "usernames": ["tester", "developer"]
}
```

### 响应参数

| 参数 | 类型 | 说明 |
|------|------|------|
| status | String | 返回请求结果 |

### 响应示例

```json
{
  "status": "success"
}
```

### 注意事项

删除成员即将在职成员转离职，并不是彻底删除。转离职成员可以在离职成员管理页面进行管理。

### 版本说明

| 版本 | 更新时间 | 说明 |
|------|----------|------|
| v1 | 2018.12.4 | 使用 _id 作为 id |
| v2 | 2019.6.21 | 使用 username 作为 id |
| v4 | 2022.6.30 | 返回值新增字段 type、status、integrate_id |
| v5 | 2022.10.28 | 频率提升至 10 次/秒；路由改为 POST corp/user/batch_delete |

---

## 6. 增量导入成员接口

- **接口名称**：增量导入成员接口
- **请求地址**：`https://api.jiandaoyun.com/api/v5/corp/user/import`
- **请求方式**：POST
- **请求频率**：10 次/秒
- **简介**：本接口以企业内的 username（成员编号）为主键，更新创建企业成员。仅支持公共模式。

### 注意事项

1. 成员编号在企业内唯一，仅支持由字母、数字、下划线组成；
2. 成员昵称最长为 80 个字符；
3. 所有成员必须在部门下，如果导入成员不存在部门，则会移动到根部门下；
4. 通过该接口导入的成员会自动激活，且没有邮箱、密码、手机号等信息，可以配合单点登录功能实现企业用户登录；
5. 如果导入数据存在，但是现有企业通讯录中不存在该成员，则新建成员；
6. 如果导入数据存在，且现有企业通讯录中存在该成员，则更新成员信息；
7. 该接口不会执行删除成员操作；
8. 该接口每次调用允许导入的成员数为 20000；
9. 该接口调用执行期间，将无法同时调用其他对通讯录的修改、删除、新增接口。

### 请求参数

| 参数 | 是否必需 | 类型 | 说明 |
|------|----------|------|------|
| users | 是 | Json[] | 成员列表 |
| users[].username | 是 | String | 成员编号 |
| users[].name | 是 | String | 昵称 |
| users[].departments | 是 | Number[] | 所在部门编号列表 |

### 请求示例

```json
{
  "users": [{
    "username": "coding_master",
    "name": "小简",
    "departments": [1, 3]
  }]
}
```

### 响应参数

| 参数 | 类型 | 说明 |
|------|------|------|
| status | String | 返回请求结果 |

### 响应示例

```json
{
  "status": "success"
}
```

### 版本说明

| 版本 | 更新时间 | 说明 |
|------|----------|------|
| v1 | 2018.12.4 | 使用 _id 作为 id |
| v2 | 2019.6.21 | 使用 username 作为 id |
| v4 | 2022.6.30 | 返回值新增字段 type、status、integrate_id |
| v5 | 2022.10.28 | 频率提升至 10 次/秒；路由改为 POST corp/user/import |

---

## 7. （递归）获取部门成员接口

- **接口名称**：（递归）获取部门成员接口
- **请求地址**：`https://api.jiandaoyun.com/api/v5/corp/department/user/list`
- **请求方式**：POST
- **请求频率**：10 次/秒
- **简介**：能够（递归）获取指定部门编号下的所有成员。支持公共模式和集成模式。

### 请求参数

| 参数 | 类型 | 是否必需 | 说明 |
|------|------|----------|------|
| dept_no | Number | 是 | 部门编号 |
| has_child | Boolean | 否 | 是否递归获取所有成员。默认为 false，即只获取当前部门下的成员，而不获取其子部门的成员。 |

### 请求示例

```json
{
  "dept_no": 1,
  "has_child": true
}
```

### 响应参数

| 参数 | 含义 |
|------|------|
| users | 当前指定部门下的成员列表 |

单个成员的返回数据结构：

| 参数 | 含义 | 备注 |
|------|------|------|
| name | 昵称 | name 可以重复，重名成员的 name 相同 |
| username | 成员编号 | username 在企业内是唯一的，不同企业之间可能存在重复 |
| departments | 用户所属的部门编号列表 | |
| type | 部门类型 | 0: 常规部门；2: 企业互联外部部门 |
| status | 部门状态 | 1: 使用中的部门；-1: 集成模式下同步后删除的部门 |
| integrate_id | 集成模式同步部门关联 ID | 仅在集成模式下返回，且在企业互联接口(外部对接人)不返回 |

### 响应示例

```json
{
  "users": [
    {
      "username": "aubrey",
      "name": "aubrey",
      "departments": [1],
      "type": 0,
      "status": 1
    }
  ]
}
```

### 版本说明

| 版本 | 更新时间 | 说明 |
|------|----------|------|
| v1 | 2018.12.4 | 使用 _id 作为 id |
| v2 | 2019.6.21 | 使用 dept_no 作为 id |
| v4 | 2022.6.30 | 返回值新增字段 type、status、integrate_id |
| v5 | 2022.10.28 | 频率提升至 10 次/秒；参数 dept_no 放入 body，路由改为 POST corp/department/user/list |

---

## 8. （递归）获取部门列表接口

- **接口名称**：（递归）获取部门列表接口
- **请求地址**：`https://api.jiandaoyun.com/api/v6/corp/department/list`
- **请求方式**：POST
- **请求频率**：10 次/秒
- **简介**：能够（递归）获取指定部门编号的所有子部门。支持公共模式和集成模式。

### 请求参数

| 参数 | 是否必需 | 类型 | 说明 |
|------|----------|------|------|
| dept_no | 是 | Number | 部门编号 |
| has_child | 否 | Boolean | 是否递归获取所有子部门。默认为 false，即只获取一级子部门。 |

### 请求示例

递归获取当前企业的根部门下所有部门列表。注：数字 1 为根部门编号。

```json
{
  "dept_no": 1,
  "has_child": true
}
```

### 响应参数

| 参数 | 类型 | 说明 |
|------|------|------|
| departments | Array | 当前指定部门下的子部门列表，值结构同部门实体结构 |

### 响应示例

```json
{
  "departments": [
    {
      "dept_no": 3,
      "name": "销售部",
      "parent_no": 1,
      "type": 0,
      "status": 1
    },
    {
      "dept_no": 33,
      "name": "华东区销售小组",
      "parent_no": 3,
      "type": 0,
      "status": 1,
      "seq": 2
    }
  ]
}
```

### 版本说明

| 版本 | 更新时间 | 说明 |
|------|----------|------|
| v1 | 2018.12.4 | 使用 _id 作为 id |
| v2 | 2019.6.21 | 使用 dept_no 作为 id |
| v4 | 2022.6.30 | 返回值新增字段 type、status、integrate_id |
| v5 | 2022.10.28 | 频率提升至 10 次/秒；参数 dept_no 放入 body，路由改为 POST corp/department/list |
| v6 | 2022.08.01 | 部门实体结构中新增响应参数 seq，支持对部门进行排序 |

---

## 9. 创建部门接口

- **接口名称**：创建部门接口
- **请求地址**：`https://api.jiandaoyun.com/api/v6/corp/department/create`
- **请求方式**：POST
- **请求频率**：20 次/秒
- **简介**：创建一个新部门。仅支持公共模式。

### 请求参数

| 参数 | 是否必需 | 类型 | 说明 |
|------|----------|------|------|
| name | 是 | String | 部门名称（最多不超过 50 个字符） |
| parent_no | 否 | Number | 父部门编号，不传默认为根部门 |
| dept_no | 否 | Number | 部门编号，不传自动生成（上限 9007199254740991） |

### 请求示例

```json
{
  "name": "研发部门",
  "parent_no": 1,
  "dept_no": 2
}
```

### 响应参数

| 参数 | 类型 | 说明 |
|------|------|------|
| department | Json | 创建的部门信息，同部门实体结构 |
| dept_no | Number | 部门编号 |
| name | String | 部门名称 |
| parent_no | Number | 父部门编号 |
| type | Number | 部门类型 |
| status | Number | 部门状态 |
| integrate_id | String | 集成模式同步部门关联 ID，仅在集成模式下返回，且在企业互联接口(外部对接人)不返回 |
| seq | number | 部门排序 |

### 响应示例

```json
{
  "department": {
    "dept_no": 2,
    "name": "研发部门",
    "parent_no": 1,
    "type": 0,
    "status": 1,
    "seq": 1
  }
}
```

### 版本说明

| 版本 | 更新时间 | 说明 |
|------|----------|------|
| v1 | 2018.12.4 | 使用 _id 作为 id |
| v2 | 2019.6.21 | 使用 dept_no 作为 id |
| v4 | 2022.6.30 | 返回值新增字段 type、status、integrate_id |
| v5 | 2022.10.28 | 频率提升至 20 次/秒；路由改为 POST corp/department/create |
| v6 | 2023.08.01 | 新增响应参数 seq，支持对部门进行排序 |

---

## 10. 修改部门接口

- **接口名称**：修改部门接口
- **请求地址**：`https://api.jiandaoyun.com/api/v6/corp/department/update`
- **请求方式**：POST
- **请求频率**：20 次/秒
- **简介**：修改指定部门的部门信息。仅支持公共模式。

### 请求参数

| 参数 | 是否必需 | 类型 | 说明 |
|------|----------|------|------|
| name | 否 | String | 部门名称 |
| parent_no | 否 | Integer | 上级部门编号 |
| dept_no | 是 | Number | 部门编号 |
| seq | 否 | number | 部门排序 |

> 注：请求参数中的 name、parent_no 和 seq 至少填写一个。

### 请求示例

```json
{
  "dept_no": 3,
  "name": "测试部门",
  "parent_no": 1,
  "seq": 1
}
```

### 响应参数

| 参数 | 类型 | 说明 |
|------|------|------|
| department | Json | 修改后的部门信息 |
| department.dept_no | Number | 部门编号 |
| department.name | String | 部门名称 |
| department.parent_no | Number | 父部门编号 |
| type | Number | 部门类型 |
| status | Number | 部门状态 |
| integrate_id | String | 集成模式同步部门关联 ID，仅在集成模式下返回，且在企业互联接口(外部对接人)不返回 |
| seq | number | 部门排序 |

### 响应示例

```json
{
  "department": {
    "dept_no": 3,
    "name": "测试部门",
    "parent_no": 2,
    "type": 0,
    "status": 1,
    "seq": 1
  }
}
```

### 版本说明

| 版本 | 更新时间 | 说明 |
|------|----------|------|
| v1 | 2018.12.4 | 使用 _id 作为 id |
| v2 | 2019.6.21 | 使用 dept_no 作为 id |
| v4 | 2022.6.30 | 返回值新增字段 type、status、integrate_id |
| v5 | 2022.10.28 | 频率提升至 20 次/秒；参数 dept_no 放入 body，路由改为 POST corp/department/update |
| v6 | 2023.08.01 | 新增请求参数和响应参数 seq，支持进行部门排序 |

---

## 11. 删除部门接口

- **接口名称**：删除部门接口
- **请求地址**：`https://api.jiandaoyun.com/api/v5/corp/department/delete`
- **请求方式**：POST
- **请求频率**：20 次/秒
- **简介**：将指定部门从组织架构中移除。仅支持公共模式。

### 请求参数

| 参数 | 类型 | 是否必需 | 说明 |
|------|------|----------|------|
| dept_no | Number | 是 | 部门编号 |

### 请求示例

```json
{
  "dept_no": 1
}
```

### 响应参数

| 参数 | 类型 | 说明 |
|------|------|------|
| status | String | 返回请求结果 |

### 响应示例

```json
{
  "status": "success"
}
```

### 版本说明

| 版本 | 更新时间 | 说明 |
|------|----------|------|
| v1 | 2018.12.4 | 使用 _id 作为 id |
| v2 | 2019.6.21 | 使用 dept_no 作为 id |
| v4 | 2022.6.30 | 返回值新增字段 type、status、integrate_id |
| v5 | 2022.10.28 | 频率提升至 20 次/秒；参数 dept_no 放入 body，路由改为 POST corp/department/delete |

---

## 12. 获取集成模式部门编号接口

- **接口名称**：获取集成模式部门编号接口
- **请求地址**：`https://api.jiandaoyun.com/api/v6/corp/department/dept_no/get`
- **请求方式**：POST
- **请求频率**：30 次/秒
- **简介**：本接口可以通过第三方平台的通讯录部门的 ID 获取其对应的简道云通讯录部门编号。仅支持集成模式。

### 请求参数

| 参数 | 是否必需 | 类型 | 说明 |
|------|----------|------|------|
| integrate_id | 是 | String | 第三方平台通讯录的部门 ID，如钉钉/企业微信/飞书的通讯录部门 ID。 |

### 请求示例

```json
{
  "integrate_id": "1005"
}
```

### 响应参数

| 参数 | 类型 | 说明 |
|------|------|------|
| department | json | 返回部门编号。同部门实体结构。 |

### 响应示例

```json
{
  "department": {
    "dept_no": 1005,
    "name": "产品部门",
    "parent_no": 2,
    "type": 0,
    "status": 1,
    "integrate_id": "1005",
    "seq": 1
  }
}
```

### 注意事项

由于企业微信/钉钉与简道云通讯录的当前部门规则一致，因此 integrate_id 与 dept_no 的值是保持一致的，并不一定需要使用此接口；而飞书平台的部门 ID 是由字符串组成，因此与简道云通讯录的部门 ID 不一致，需要使用此接口。

### 版本说明

| 版本 | 更新时间 | 说明 |
|------|----------|------|
| v1 | 2018.12.4 | 使用 _id 作为 id |
| v2 | 2019.6.21 | 使用 dept_no 作为 id |
| v4 | 2022.6.30 | 返回值新增字段 type、status、integrate_id |
| v5 | 2022.10.28 | 频率提升至 30 次/秒；路由改为 POST corp/department/dept_no/get |
| v6 | 2022.08.01 | 部门实体结构中新增响应参数 seq，支持对部门进行排序 |

---

## 13. 全量导入部门接口

- **接口名称**：全量导入部门接口
- **请求地址**：`https://api.jiandaoyun.com/api/v5/corp/department/import`
- **请求方式**：POST
- **请求频率**：10 次/秒
- **简介**：本接口以 dept_no（部门编号）为主键，全量覆盖企业内的通讯录部门树。仅支持公共模式。

### 注意事项

1. 部门编号为数字类型且唯一。
2. 除了根部门以外所有部门的父部门必须存在。如果新导入列表中不存在根部门，则会自动插入根部门，且部门名称为企业名称。
3. 同级部门名称不能有重复。
4. 部门层级不能超过 16 级。
5. 如果导入数据存在，且现有企业通讯录中也存在，则更新该部门的信息。
6. 如果导入数据存在，而现有企业通讯录中不存在，则新建该部门。
7. 如果导入数据不存在，但现有企业通讯录中存在，则继续判断该部门下是否存在子部门和成员，如果都没有则自动删除该部门，否则将子部门和成员转移到根部门下继续保留。
8. 该接口允许导入的部门数上限为 100000。
9. 该接口调用执行期间，将无法同时调用其他对通讯录的修改、删除、新增接口。

### 请求参数

| 参数 | 是否必需 | 类型 | 说明 |
|------|----------|------|------|
| departments | 是 | Array | 部门列表 |
| departments[].dept_no | 是 | Number | 部门编号（上限 9007199254740991） |
| departments[].name | 是 | String | 部门名称 |
| departments[].parent_no | 否 | Number | 父部门编号，不传默认为根部门下 |

### 请求示例

```json
{
  "departments": [{
    "dept_no": 11,
    "name": "研发部门",
    "parent_no": 1
  }, {
    "dept_no": 12,
    "name": "测试部门",
    "parent_no": 1
  }]
}
```

> 注：在使用批量导入部门的 API 接口时，在传入新部门的同时，还需要写入新部门的根部门，以保证部门树结构的完整性。例如，想在 SSO_dept 这个部门下插入一个新的子部门，如果只传新部门的话，会报错父部门不存在。此时需要把 SSO_dept 部门也传一下，即使该部门已经存在了，但为了树结构的完整性以及新部门的准确插入，需要再次写入。

### 响应参数

| 参数 | 类型 | 说明 |
|------|------|------|
| status | String | 返回请求结果 |

### 响应示例

```json
{
  "status": "success"
}
```

### 版本说明

| 版本 | 更新时间 | 说明 |
|------|----------|------|
| v1 | 2018.12.4 | 使用 _id 作为 id |
| v2 | 2019.6.21 | 使用 dept_no 作为 id |
| v4 | 2022.6.30 | 返回值新增字段 type、status、integrate_id |
| v5 | 2022.10.28 | 频率提升至 10 次/秒；路由改为 POST corp/department/import |

---

## 14. 获取部门主管列表接口

- **接口名称**：获取部门主管列表接口
- **请求地址**：`https://api.jiandaoyun.com/api/v6/corp/department/manager/get`
- **请求方式**：POST
- **请求频率**：20 次/秒
- **简介**：获取指定部门下的主管成员列表。

### 请求参数

| 参数 | 类型 | 是否必需 | 说明 |
|------|------|----------|------|
| dept_no | number | 是 | 部门编号 |

### 请求示例

```json
{
  "dept_no": 1
}
```

### 响应参数

| 参数 | 类型 | 说明 |
|------|------|------|
| dept_managers | array | 部门主管成员列表 |

成员对象字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| username | string | 成员用户名 |
| name | string | 成员昵称 |
| departments | number[] | 所属部门编号列表 |
| type | number | 成员类型：0：常规成员；2：企业互联外部对接人。注：部门主管只能是内部成员，所以该接口中返回值仅会为 0。 |
| status | number | 成员状态：0：未确认的成员；1：已加入 |
| integrate_id | string | 第三方平台集成 ID（仅集成模式企业返回） |

### 响应示例

```json
{
  "dept_managers": [
    {
      "username": "zhangsan",
      "name": "张三",
      "departments": [1, 2],
      "type": 0,
      "status": 1
    }
  ]
}
```

### 版本说明

| 版本 | 更新时间 | 说明 |
|------|----------|------|
| v6 | 2026.06.12 | 原始接口 |

---

## 15. 设置部门主管接口

- **接口名称**：设置部门主管接口
- **请求地址**：`https://api.jiandaoyun.com/api/v6/corp/department/manager/update`
- **请求方式**：POST
- **请求频率**：20 次/秒
- **简介**：设置指定部门的主管成员，以全量覆盖方式更新。

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| dept_no | number | 是 | 部门编号 |
| managers | string[] | 是 | 主管成员用户名列表，传入空数组 [] 可清空所有主管 |

### 请求示例

```json
{
  "dept_no": 1,
  "managers": ["zhangsan", "lisi"]
}
```

### 响应参数

| 参数 | 类型 | 说明 |
|------|------|------|
| dept_managers | array | 部门主管成员列表 |

成员对象字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| username | string | 成员用户名 |
| name | string | 成员昵称 |
| departments | number[] | 所属部门编号列表 |
| type | number | 成员类型：0：常规成员；2：企业互联外部对接人。注：部门主管只能是内部成员，所以该接口中返回值仅会为 0。 |
| status | number | 成员状态：0：未确认的成员；1：已加入 |
| integrate_id | string | 第三方平台集成 ID（仅集成模式企业返回） |

### 响应示例

```json
{
  "dept_managers": [
    {
      "username": "zhangsan",
      "name": "张三",
      "departments": [1, 2],
      "type": 0,
      "status": 1
    },
    {
      "username": "lisi",
      "name": "李四",
      "departments": [1],
      "type": 0,
      "status": 1
    }
  ]
}
```

### 版本说明

| 版本 | 更新时间 | 说明 |
|------|----------|------|
| v6 | 2026.06.12 | 原始接口 |


---

## 七、通讯录实体结构与注意事项

### 7.1 部门实体结构（department）

| 属性 | 类型 | 含义 | 备注 |
|------|------|------|------|
| dept_no | Number | 部门编号，企业内唯一 | 不同企业之间可能存在重复 |
| name | String | 部门名称 | |
| parent_no | Number | 父部门编号 | 在企业互联接口中(外部部门)不存在 |
| type | Number | 部门类型 | 0: 常规部门；2: 企业互联外部部门 |
| status | Number | 部门状态 | 1: 使用中的部门；-1: 集成模式下同步后删除的部门 |
| integrate_id | String | 集成模式同步部门关联 ID | 仅在集成模式下返回，且在企业互联接口(外部部门)不返回 |
| seq | Number | 部门排序 | 部门在父部门内的序号，从小到大排列 |

### 7.2 成员实体结构（user）

| 属性 | 类型 | 含义 | 备注 |
|------|------|------|------|
| username | String | 成员编号，企业内唯一 | 不同企业之间可能存在重复 |
| name | String | 昵称 | |
| departments | Number[] | 成员所在部门编号列表 | |
| type | Number | 成员类型 | 0: 常规成员；2: 企业互联外部对接人 |
| status | Number | 成员状态 | 0: 未确认的成员；1: 已加入 |
| integrate_id | String | 集成模式同步成员关联 ID | 仅在集成模式下返回，且在企业互联接口(外部对接人)不返回 |

### 7.3 角色实体结构（role）

| 属性 | 类型 | 含义 | 备注 |
|------|------|------|------|
| role_no | Number | 角色编号，企业内唯一 | 不同企业之间可能存在重复 |
| group_no | Number | 角色组编号，企业内唯一 | 不同企业之间可能存在重复 |
| name | String | 角色名称 | |
| type | Number | 角色类型 | 0: 常规角色；2: 企业互联外部角色 |
| status | Number | 角色状态 | 1: 使用中 |
| integrate_id | String | 集成模式同步成员关联 ID | 仅在集成模式下返回 |

### 7.4 角色组实体结构（role_group）

| 属性 | 类型 | 含义 | 备注 |
|------|------|------|------|
| group_no | Number | 角色组编号，企业内唯一 | 不同企业之间可能存在重复 |
| name | String | 角色组名称 | |
| type | Number | 角色组类型 | 0: 常规角色组；2: 企业互联外部角色组 |
| status | Number | 角色组状态 | 1: 使用中 |
| integrate_id | String | 集成模式同步角色组关联 ID | 仅在集成模式下(飞书除外)同步的角色组返回 |

### 7.5 版本差异对比

| 接口类型 | v1 | v2 | v4 | v5 |
|----------|----|----|----|----|
| 成员 | 使用 _id 作为 id | 使用 username 作为 id | 返回值新增 type、status、integrate_id | 频率提升 |
| 部门 | 使用 _id 作为 id | 使用 dept_no 作为 id | 返回值新增 type、status、integrate_id | 频率提升 |
| 角色 | 无 | 角色使用 role_no，角色组使用 group_no，包含 integrate_id、type | 返回值新增 status | 频率提升 |
| 企业互联 | 无 | 无 | 成员使用 username，部门使用 dept_no，包含 type、status | 频率提升 |

### 7.6 注意事项

1. 每个通讯录都是一棵部门树，且**根部门的部门编号都是 1**。
2. 对公共模式和集成模式支持的程度不同，会在每个接口上备注。
3. 由于企业微信/钉钉与简道云通讯录的当前部门规则一致，因此 integrate_id 与 dept_no 的值暂时保持一致；而飞书平台的部门 ID 是由字符串组成，因此与简道云通讯录的部门 dept_no 不一致。integrate_id 与 dept_no 的含义不同，后续更新中不保证使用相同的值，使用时须加以区分。
4. 部门树深度限制为 **16** 层。
5. 单次导入部门上限 **10 万**，成员上限 **2 万**。




---

## 八、通讯录 - 角色/角色组/企业互联接口（详细）


# 简道云开放平台 API 文档

> **本章接口的版本沿革**（线上每页单列，此处合并，避免重复 14 张相同的表）：
>
> - **角色 / 角色组接口**：v2 2022.4.8 初始版本（角色用 role_no、角色组用 group_no 作主键，含 integrate_id、type）→ v4 2022.6.30 返回值新增 status → v5 2022.10.28 提升频率，路由加 `corp/` 前缀。
> - **企业互联接口**：v4 2022.4.21 初始版本（成员用 username、部门用 dept_no，含 type、status）→ v4 2022.6.30 返回值新增 status → v5 2022.10.28 提升频率。
> - **列出角色下的成员**：2023.10.11 新增请求参数 `has_manage_range`、响应参数 `departments_range` 与 `has_child`；仅配置了分管部门的成员才会返回后两者。

## 1. 列出角色接口

- **接口名称**：列出角色接口
- **请求地址**：`https://api.jiandaoyun.com/api/v5/corp/role/list`
- **请求方式**：POST
- **请求频率**：30 次/秒
- **接口简介**：将角色列出来。支持公共模式和集成模式。

### 请求参数

| 参数 | 类型 | 是否必需 | 说明 |
|------|------|----------|------|
| skip | Number | 否 | 偏移量 |
| limit | Number | 否 | limit，不传递时默认值为 1 |
| has_internal | Boolean | 否 | 是否包含自建角色，默认为 true |
| has_sync | Boolean | 否 | 是否包含集成角色，默认为 true |

### 请求示例

```json
{
  "skip": 0,
  "limit": 3,
  "has_internal": true,
  "has_sync": true
}
```

### 响应参数

| 参数 | 类型 | 是否必需 | 说明 |
|------|------|----------|------|
| role_no | Number | 是 | 角色编号 |
| group_no | Number | 否 | 角色组编号 |
| name | String | 是 | 角色名称 |
| type | Number | 是 | 角色类型，若为 0 则表示为常规角色 |
| status | Number | 是 | 成员状态：0-未确认的成员，1-已加入 |
| integrate_id | String | 否 | 集成模式同步角色关联 ID，仅在集成模式下返回 |

### 响应示例

```json
{
  "roles": [
    {
      "role_no": 3,
      "group_no": 2547,
      "name": "设计中心",
      "type": 0,
      "status": 1
    },
    {
      "role_no": 2551,
      "group_no": 2550,
      "name": "销售总监",
      "type": 0,
      "status": 1
    },
    {
      "role_no": 2552,
      "group_no": 2550,
      "name": "销售主管",
      "type": 0,
      "status": 1
    }
  ]
}
```

---

## 2. 创建一个自建角色

- **接口名称**：创建一个自建角色
- **请求地址**：`https://api.jiandaoyun.com/api/v5/corp/role/create`
- **请求方式**：POST
- **请求频率**：20 次/秒
- **接口简介**：只能创建内部自建角色。支持公共模式和集成模式。

### 请求参数

| 参数 | 类型 | 是否必需 | 说明 |
|------|------|----------|------|
| name | String | 是 | 角色名称 |
| group_no | Number | 是 | 角色组编号 |

### 请求示例

```json
{
  "group_no": 2547,
  "name": "研发中心"
}
```

### 响应参数

| 参数 | 类型 | 是否必须 | 说明 |
|------|------|----------|------|
| role_no | Number | 是 | 角色编号 |
| group_no | Number | 否 | 角色组编号 |
| name | String | 是 | 角色名称 |
| type | Number | 是 | 角色类型：0-常规角色，2-外部角色 |
| status | Number | 是 | 成员状态：0-未确认的成员，1-已加入 |
| integrate_id | String | 否 | 集成模式同步角色关联 ID，仅在集成模式下返回 |

### 响应示例

```json
{
  "role": {
    "role_no": 2558,
    "group_no": 2547,
    "name": "研发中心",
    "type": 0,
    "status": 1
  }
}
```

---

## 3. 更新一个自建角色

- **接口名称**：更新一个自建角色
- **请求地址**：`https://api.jiandaoyun.com/api/v5/corp/role/update`
- **请求方式**：POST
- **请求频率**：20 次/秒
- **接口简介**：对自建角色进行更新。支持公共模式和集成模式，但集成模式下只支持对自建角色的操作，不支持对第三方同步过来的角色操作。

### 请求参数

| 参数 | 类型 | 是否必需 | 说明 |
|------|------|----------|------|
| role_no | Number | 是 | 角色编号 |
| group_no | Number | 是 | 角色组编号 |
| name | String | 否 | 角色名称 |

### 请求示例

```json
{
  "role_no": 2558,
  "group_no": 2547,
  "name": "研发部门"
}
```

### 响应参数

| 参数 | 类型 | 是否必需 | 说明 |
|------|------|----------|------|
| role_no | Number | 是 | 角色编号 |
| group_no | Number | 否 | 角色组编号 |
| name | String | 是 | 角色名称 |
| type | Number | 是 | 角色类型：0-常规角色，2-外部角色 |
| status | Number | 是 | 成员状态：0-未确认的成员，1-已加入 |
| integrate_id | String | 否 | 集成模式同步角色关联 ID，仅在集成模式下返回 |

### 响应示例

```json
{
  "role": {
    "role_no": 2558,
    "group_no": 2547,
    "name": "研发部门",
    "type": 0,
    "status": 1
  }
}
```

---

## 4. 删除一个自建角色

- **接口名称**：删除一个自建角色
- **请求地址**：`https://api.jiandaoyun.com/api/v5/corp/role/delete`
- **请求方式**：POST
- **请求频率**：20 次/秒
- **接口简介**：对某个自建角色进行删除。支持公共模式和集成模式，但集成模式下只支持对自建角色的操作，不支持对第三方同步过来的角色操作。

### 请求参数

| 参数 | 类型 | 是否必需 | 说明 |
|------|------|----------|------|
| role_no | Number | 是 | 角色编号 |

### 请求示例

```json
{
  "role_no": 2558
}
```

### 响应内容

状态码：200。

---

## 5. 列出角色下的成员

- **接口名称**：列出角色下的成员
- **请求地址**：`https://api.jiandaoyun.com/api/v5/corp/role/user/list`
- **请求方式**：POST
- **请求频率**：30 次/秒
- **接口简介**：列出角色下的所有成员信息。支持公共模式和集成模式。
- **注意**：只会返回邀请中和已激活的成员。

### 请求参数

| 参数 | 类型 | 是否必需 | 说明 |
|------|------|----------|------|
| skip | Number | 否 | 分页偏移 |
| limit | Number | 否 | 分页大小，最大值为 10000 |
| role_no | Number | 是 | 角色编号 |
| has_manage_range | Boolean | 否 | 是否包含分管部门信息，默认值为 false |

### 请求示例

```json
{
  "skip": 0,
  "limit": 3,
  "role_no": 72,
  "has_manage_range": true
}
```

### 响应参数

| 参数 | 类型 | 是否必须 | 说明 |
|------|------|----------|------|
| username | String | 是 | 成员的编号，企业内唯一 |
| name | String | 是 | 成员昵称 |
| departments | Number[] | 是 | 成员所在部门编号列表 |
| type | Number | 是 | 成员类型：0-常规成员，2-企业互联外部对接人 |
| status | Number | 是 | 成员状态：0-未确认的成员，1-已加入 |
| integrate_id | String | 否 | 集成模式同步角色关联 ID，仅在集成模式下返回 |
| departments_range | Number[] | 否 | 角色分管部门编号（只有配置了分管部门的成员才会显示） |
| has_child | Boolean | 否 | 是否包含子部门（只有配置了分管部门的成员才会显示） |

### 响应示例

```json
{
  "users": [
    {
      "username": "jdy-xulalikdbj82",
      "name": "frank",
      "departments": [212],
      "type": 0,
      "status": 1,
      "departments_range": [378, 1157],
      "has_child": true
    },
    {
      "username": "R-E9rRNbwL",
      "name": "成员删除1",
      "departments": [338, 226],
      "type": 0,
      "status": 1,
      "departments_range": [1157],
      "has_child": false
    },
    {
      "username": "UPDATE",
      "name": "testadmin",
      "departments": [1],
      "type": 0,
      "status": 1
    }
  ]
}
```

---

## 6. 为自建角色批量添加成员

- **接口名称**：为自建角色批量添加成员
- **请求地址**：`https://api.jiandaoyun.com/api/v5/corp/role/add_members`
- **请求方式**：POST
- **请求频率**：10 次/秒
- **接口简介**：为自建的角色批量添加成员。支持公共模式和集成模式，但集成模式下只支持对自建角色的操作，不支持对第三方同步过来的角色操作。

### 请求参数

| 参数 | 类型 | 是否必须 | 说明 |
|------|------|----------|------|
| role_no | Number | 是 | 角色编号 |
| usernames | String[] | 是 | 员工工号 |

### 请求示例

```json
{
  "role_no": 3,
  "usernames": [
    "fr0005",
    "fr008"
  ]
}
```

### 响应参数

| 参数 | 类型 | 是否必须 | 说明 |
|------|------|----------|------|
| status | String | 否 | 返回请求结果 |

### 响应示例

```json
{
  "status": "success"
}
```

---

## 7. 为自建角色批量移除成员

- **接口名称**：为自建角色批量移除成员
- **请求地址**：`https://api.jiandaoyun.com/api/v5/corp/role/remove_members`
- **请求方式**：POST
- **请求频率**：10 次/秒
- **接口简介**：将成员从角色中批量移除。支持公共模式和集成模式，但集成模式下只支持对自建角色的操作。

### 请求参数

| 参数 | 类型 | 是否必须 | 说明 |
|------|------|----------|------|
| role_no | Number | 是 | 角色编号 |
| usernames | String[] | 是 | 员工工号 |

### 请求示例

```json
{
  "role_no": 3,
  "usernames": [
    "fr0005",
    "fr008"
  ]
}
```

### 响应参数

| 参数 | 类型 | 是否必须 | 说明 |
|------|------|----------|------|
| status | String | 否 | 返回请求结果 |

### 响应示例

```json
{
  "status": "success"
}
```

---

## 8. 列出自建角色组

- **接口名称**：列出自建角色组
- **请求地址**：`https://api.jiandaoyun.com/api/v5/corp/role_group/list`
- **请求方式**：POST
- **请求频率**：30 次/秒
- **接口简介**：将角色组全部拉取出来。支持公共模式和集成模式。

### 请求参数

| 参数 | 类型 | 是否必需 | 说明 |
|------|------|----------|------|
| skip | Integer | 否 | 偏移量 |
| limit | Integer | 否 | limit |
| has_internal | Boolean | 否 | 是否包含自建角色组，默认为 true |
| has_sync | Boolean | 否 | 是否包含集成角色组，默认为 true |

### 请求示例

```json
{
  "skip": 0,
  "limit": 3,
  "has_internal": true,
  "has_sync": true
}
```

### 响应参数

| 参数 | 类型 | 是否必需 | 说明 |
|------|------|----------|------|
| group_no | Number | 是 | 角色组编号 |
| name | String | 是 | 角色组名称 |
| type | Number | 是 | 角色组类型：0-常规角色组，2-企业互联外部角色组 |
| status | Number | 是 | 1: 使用中 |
| integrate_id | String | 否 | 集成模式同步角色关联 ID，仅在集成模式下返回 |

### 响应示例

```json
{
  "role_groups": [
    {
      "group_no": 2547,
      "name": "默认",
      "type": 0,
      "status": 1
    },
    {
      "group_no": 2550,
      "name": "CRM角色组",
      "type": 0,
      "status": 1
    },
    {
      "group_no": 2556,
      "name": "营销中心",
      "type": 0,
      "status": 1
    }
  ]
}
```

---

## 9. 创建自建角色组

- **接口名称**：创建自建角色组
- **请求地址**：`https://api.jiandaoyun.com/api/v5/corp/role_group/create`
- **请求方式**：POST
- **请求频率**：20 次/秒
- **接口简介**：通过接口新建角色组。支持公共模式和集成模式。

### 请求参数

| 参数 | 类型 | 是否必需 | 说明 |
|------|------|----------|------|
| name | String | 是 | 角色组名称 |

### 请求示例

```json
{
  "name": "研发中心"
}
```

### 响应参数

| 参数 | 类型 | 是否必需 | 说明 |
|------|------|----------|------|
| group_no | Number | 是 | 角色组编号 |
| name | String | 是 | 角色组名称 |
| type | Number | 是 | 角色组类型：0-常规角色组，2-企业互联外部角色组 |
| status | Number | 是 | 1: 使用中 |
| integrate_id | String | 否 | 集成模式同步角色关联 ID，仅在集成模式下返回 |

### 响应示例

```json
{
  "role_group": {
    "group_no": 2559,
    "name": "研发中心",
    "type": 0,
    "status": 1
  }
}
```

---

## 10. 更新自建角色组

- **接口名称**：更新自建角色组
- **请求地址**：`https://api.jiandaoyun.com/api/v5/corp/role_group/update`
- **请求方式**：POST
- **请求频率**：20 次/秒
- **接口简介**：更新创建好的角色组信息。支持公共模式和集成模式，但集成模式下只支持对自建角色操作，不支持对第三方同步的角色操作。

### 请求参数

| 参数 | 类型 | 是否必须 | 说明 |
|------|------|----------|------|
| role_group_no | Integer | 是 | 角色组编号 |
| name | String | 是 | 角色组名称 |

### 请求示例

```json
{
  "role_group_no": 2559,
  "name": "研发部门"
}
```

### 响应参数

| 参数 | 类型 | 是否必需 | 说明 |
|------|------|----------|------|
| group_no | Number | 是 | 角色组编号 |
| name | String | 是 | 角色组名称 |
| type | Number | 是 | 角色组类型：0-常规角色组，2-企业互联外部角色组 |
| status | Number | 是 | 1: 使用中 |
| integrate_id | String | 否 | 集成模式同步角色关联 ID，仅在集成模式下返回 |

### 响应示例

```json
{
  "role_group": {
    "group_no": 2559,
    "name": "研发部门",
    "type": 0,
    "status": 1
  }
}
```

---

## 11. 删除自建角色组

- **接口名称**：删除自建角色组
- **请求地址**：`https://api.jiandaoyun.com/api/v5/corp/role_group/delete`
- **请求方式**：POST
- **请求频率**：20 次/秒
- **接口简介**：删除创建好的角色组信息。支持公共模式和集成模式，但集成模式下只支持对自建角色操作，不支持对第三方同步的角色操作。

### 请求参数

| 参数 | 类型 | 是否必须 | 说明 |
|------|------|----------|------|
| role_group_no | Number | 是 | 角色组编号 |

### 请求示例

```json
{
  "role_group_no": 2561
}
```

### 响应参数

| 参数 | 类型 | 是否必须 | 说明 |
|------|------|----------|------|
| status | String | 否 | 返回请求结果 |

### 响应示例

```json
{
  "status": "success"
}
```

---

## 12. 列出我连接的企业

- **接口名称**：列出我连接的企业
- **请求地址**：`https://api.jiandaoyun.com/api/v5/corp/guest/department/list`
- **请求方式**：POST
- **请求频率**：30 次/秒
- **接口简介**：能够获取所有外部部门的列表。支持公共模式和集成模式。
- **注意**：只返回已加入的，不返回未加入和已解除的。

### 请求参数

| 参数 | 类型 | 是否必须 | 说明 |
|------|------|----------|------|
| dept_no | Integer | 否 | 部门编号，不填则返回所有外部部门 |

### 请求示例

```json
{
  "dept_no": 1012
}
```

### 响应参数

| 参数 | 类型 | 是否必需 | 说明 |
|------|------|----------|------|
| dept_list | Array | 是 | 部门内容数组 |
| name | String | 是 | 部门名称 |
| dept_no | Integer | 是 | 部门编号 |
| type | Number | 是 | 部门类型：0-常规部门，2-企业互联外部部门 |
| status | Number | 是 | 部门状态：1-使用中的部门，-1-集成模式下同步后删除的部门 |
| integrate_id | String | 否 | 集成模式同步部门关联 ID |

### 响应示例

```json
{
  "dept_list": [
    {
      "name": "帆软软件有限公司",
      "dept_no": 1012,
      "type": 2,
      "status": 1
    }
  ]
}
```

---

## 13. 列出连接企业的对接人

- **接口名称**：列出我连接的企业的对接人
- **请求地址**：`https://api.jiandaoyun.com/api/v5/corp/guest/user/list`
- **请求方式**：POST
- **请求频率**：30 次/秒
- **接口简介**：能够获取外部对接人的列表。支持公共模式和集成模式。

### 请求参数

| 参数 | 类型 | 是否必需 | 说明 |
|------|------|----------|------|
| dept_no | Integer | 否 | 部门编号，不填则返回全部 |

### 请求示例

```json
{
  "dept_no": 19
}
```

### 响应参数

| 参数 | 类型 | 是否必需 | 说明 |
|------|------|----------|------|
| member_list | Array | 是 | 企业对接人内容数组 |
| name | String | 是 | 昵称 |
| username | String | 是 | 成员编号 |
| departments | Array[integer] | 是 | 部门编号 |
| type | Number | 是 | 类型：0-常规，2-企业互联外部 |
| status | Number | 是 | 状态：1-使用中，-1-集成模式下同步后删除 |
| integrate_id | String | 否 | 集成模式同步关联 ID |

### 响应示例

```json
{
  "member_list": [
    {
      "name": "Purl",
      "username": "R-ww9a61c11fc226842f-#admin",
      "departments": [19],
      "type": 2,
      "status": 1
    }
  ]
}
```

---

## 14. 获取对接人详细信息

- **接口名称**：获取我连接的企业对接人的详细信息
- **请求地址**：`https://api.jiandaoyun.com/api/v5/corp/guest/user/get`
- **请求方式**：POST
- **请求频率**：30 次/秒
- **接口简介**：获取某个对接人的详细信息。

### 请求参数

| 参数 | 类型 | 是否必需 | 说明 |
|------|------|----------|------|
| username | String | 是 | 成员编号 |

### 请求示例

```json
{
  "username": "R-611e10175402f70006bcdc2c-jdy-e4703i1mde61"
}
```

### 响应参数

| 参数 | 类型 | 是否必需 | 说明 |
|------|------|----------|------|
| name | String | 是 | 昵称 |
| username | String | 是 | 成员编号 |
| departments | Array[integer] | 是 | 部门编号 |
| type | Number | 是 | 类型：0-常规，2-企业互联外部 |
| status | Number | 是 | 状态：1-使用中，-1-集成模式下同步后删除 |
| integrate_id | String | 否 | 集成模式同步关联 ID |

### 响应示例

```json
{
  "member": {
    "name": "peach",
    "username": "R-611e10175402f70006bcdc2c-jdy-e4703i1mde61",
    "departments": [62],
    "type": 2,
    "status": 1
  }
}
```

---

## 15. 获取平台资源用量统计接口

- **接口名称**：获取平台资源用量统计接口
- **请求地址**：`https://api.jiandaoyun.com/api/v1/corp_usage/overview`
- **请求方式**：POST
- **请求频率**：1 次/秒
- **接口简介**：获取当前企业在指定日期的平台资源用量概览。接口只返回企业维度的汇总指标，不返回应用或成员明细。
- **版本说明**：本功能为付费高级功能，简道云旗舰版、独享版可用，其他版本请联系销售增购。

### 接口版本

| 接口版本 | 更新时间 | 版本说明 |
|---------|---------|--------|
| v1 | 2026.05.28 | 原始接口 |
| v2 | 2026.06.29 | 新增响应字段 daily_automation_exec（智能助手 Pro 日执行次数）、daily_attachment_upload（日附件上传量）。注：路由仍为 /api/v1/corp_usage/overview，版本号仅体现在文档 |

### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| date | String | 否 | 统计日期，格式 yyyy-MM-dd。不传或传空字符串表示查询当前日期的前一日（T-1）的统计信息 |

### 重要说明

1. date 默认为东八区时间，即中国时间。
2. 指定 date 时，不能晚于当前日期的前一日（T-1），最多支持查询最近 180 天。
3. 使用该接口时，若从未使用过「管理后台 > 管理工具 > 使用统计」功能，将无法获取相关数据，指标字段返回值为 0。
4. 当 date 合法但传入时间早于第一次使用「管理后台 > 管理工具 > 使用统计」功能时，也无法获取相关数据。

### 请求示例

```json
{
  "date": "2026-05-08"
}
```

### 响应参数

| 参数 | 含义 |
|------|------|
| date | 统计日期 |
| metrics | 企业用量指标对象 |
| metrics.app | 应用数 |
| metrics.form_coop | 普通表单数 |
| metrics.form_workflow | 流程表单数 |
| metrics.dash | 仪表盘数 |
| metrics.etl | 数据工厂数 |
| metrics.aggregate | 聚合表数 |
| metrics.public_link | 外链开启数 |
| metrics.data_trigger | 智能助手数 |
| metrics.automation | 智能助手 Pro 数 |
| metrics.bpa | 流程分析数 |
| metrics.data | 数据总量 |
| metrics.daily_automation_exec | 智能助手 Pro 日执行次数 |
| metrics.daily_attachment_upload | 日附件上传量，单位：byte |

### 响应示例

```json
{
  "date": "2026-06-29",
  "metrics": {
    "app": 34,
    "form_coop": 245,
    "form_workflow": 109,
    "dash": 75,
    "etl": 52,
    "aggregate": 29,
    "public_link": 0,
    "data_trigger": 100,
    "automation": 43,
    "bpa": 0,
    "data": 353,
    "daily_attachment_upload": 0,
    "daily_automation_exec": 0
  }
}
```

---

## 16. 获取应用资源用量统计接口

- **接口名称**：获取应用资源用量统计接口
- **请求地址**：`https://api.jiandaoyun.com/api/v1/corp_usage/app_metrics`
- **请求方式**：POST
- **请求频率**：1 次/秒
- **接口简介**：获取当前企业在指定日期的应用维度资源用量统计。
- **版本说明**：本功能为付费高级功能，简道云旗舰版、独享版可用，其他版本请联系销售增购。

### 接口版本

| 接口版本 | 更新时间 | 版本说明 |
|---------|---------|--------|
| v1 | 2026.05.28 | 原始接口 |
| v2 | 2026.06.29 | 新增响应字段 daily_automation_exec、daily_attachment_upload。注：路由仍为 /api/v1/corp_usage/app_metrics |

### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| date | String | 否 | 统计日期，格式 yyyy-MM-dd。不传或传空字符串表示查询当前日期的前一日（T-1）的统计信息 |
| app_ids | String[] | 否 | 应用 ID 列表，最多 10 个。空数组或不传表示分页查询全部应用 |
| skip | Number | 否 | 分页偏移，默认 0 |
| limit | Number | 否 | 分页大小，默认 20，最大 100 |

### 重要说明

1. date 默认为东八区时间，即中国时间。
2. 指定 date 时，不能晚于当前日期的前一日（T-1），最多支持查询最近 180 天。
3. 使用该接口时，若从未使用过「管理后台 > 管理工具 > 使用统计」功能，将无法获取相关数据，指标字段返回值为 0。
4. 当 date 合法但传入时间早于第一次使用「管理后台 > 管理工具 > 使用统计」功能时，也无法获取相关数据。

### 请求示例

```json
{
  "date": "2026-05-08",
  "app_ids": ["65f000000000000000000001"],
  "skip": 0,
  "limit": 20
}
```

### 响应参数

| 参数 | 含义 |
|------|------|
| date | 统计日期 |
| has_next | 是否存在下一页 |
| items | 应用统计列表 |
| items[].app_id | 应用 ID |
| items[].app_name | 应用名称 |
| items[].creator | 创建者基础信息 |
| items[].created_at | 创建时间 |
| items[].last_edit_at | 最近一次编辑时间 |
| items[].last_visit_at | 最近一次访问时间 |
| items[].metrics | 应用维度指标 |
| items[].metrics.app | 应用数，应用维度通常为 1 |
| items[].metrics.form_coop | 普通表单数 |
| items[].metrics.form_workflow | 流程表单数 |
| items[].metrics.dash | 仪表盘数 |
| items[].metrics.etl | 数据工厂数 |
| items[].metrics.aggregate | 聚合表数 |
| items[].metrics.public_link | 外链开启数 |
| items[].metrics.data_trigger | 智能助手数 |
| items[].metrics.automation | 智能助手 Pro 数 |
| items[].metrics.bpa | 流程分析数 |
| items[].metrics.data | 数据总量 |
| items[].metrics.daily_automation_exec | 智能助手 Pro 日执行次数 |
| items[].metrics.daily_attachment_upload | 日附件上传量，单位：byte |

### 响应示例

```json
{
  "date": "2026-05-08",
  "has_next": false,
  "items": [
    {
      "app_id": "65f000000000000000000001",
      "app_name": "CRM",
      "creator": {
        "member_id": "65f000000000000000000011",
        "name": "张三"
      },
      "created_at": "2026-01-01T00:00:00+08:00",
      "last_edit_at": "2026-05-06T12:00:00+08:00",
      "last_visit_at": "2026-05-06T18:00:00+08:00",
      "metrics": {
        "app": 1,
        "form_coop": 20,
        "form_workflow": 3,
        "dash": 2,
        "etl": 1,
        "aggregate": 1,
        "public_link": 5,
        "data_trigger": 2,
        "automation": 1,
        "bpa": 0,
        "data": 2,
        "daily_attachment_upload": 0,
        "daily_automation_exec": 0
      }
    }
  ]
}
```


---

## 九、资源用量与审计日志接口（详细）


# 接口1：获取成员资源用量统计接口

## 1. 简介

获取当前企业在指定日期的成员维度资源用量统计。

### 版本说明

本功能为付费高级功能，简道云旗舰版、独享版可用，其他版本请联系销售增购。

### 接口版本

| 接口版本 | 更新时间 | 版本说明 |
|---------|---------|----------|
| v1 | 2026.05.28 | 原始接口 |

## 2. 接口调用

- **请求地址**：`https://api.jiandaoyun.com/api/v1/corp_usage/member_metrics`
- **请求频率**：1 次/秒
- **请求方式**：POST

### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| date | String | 否 | 统计日期，格式 yyyy-MM-dd。不传或传空字符串表示查询**当前日期的前一日（T-1）**的统计信息 |
| member_ids | String[] | 否 | 成员 ID 列表，最多 10 个。空数组或不传表示分页查询全部成员 |
| skip | Number | 否 | 分页偏移，默认 0 |
| limit | Number | 否 | 分页大小，默认 20，最大 100 |

### 注意事项

1. date 默认为东八区时间，即中国时间。
2. 指定 date 时，不能晚于**当前日期的前一日（T-1）**，最多支持查询最近 180 天。
3. 使用该接口时，若从未使用过「管理后台 >> 管理工具 >> 使用统计」功能，将无法获取相关数据，指标字段返回值为 0。
4. 当 date 合法但传入时间早于第一次使用「管理后台 >> 管理工具 >> 使用统计」功能时，也无法获取相关数据。

### 请求示例

```json
{
  "date": "2026-05-08",
  "member_ids": [
    "65f000000000000000000011"
  ],
  "skip": 0,
  "limit": 20
}
```

### 响应参数

| 参数 | 含义 |
|------|------|
| date | 统计日期 |
| has_next | 是否存在下一页 |
| items | 成员统计列表 |
| items[].member | 成员基础信息 |
| items[].member.member_id | 成员 ID |
| items[].member.name | 成员名称 |
| items[].metrics | 成员维度指标（见下方指标字段说明） |

**指标字段说明：**

| 字段 | 含义 |
|------|------|
| app | 应用数 |
| form_coop | 普通表单数 |
| form_workflow | 流程表单数 |
| dash | 仪表盘数 |
| etl | 数据工厂数 |
| aggregate | 聚合表数 |
| public_link | 外链开启数 |
| data_trigger | 智能助手数 |
| automation | 智能助手 Pro 数 |
| bpa | 流程分析数 |
| data | 数据总量 |

### 响应示例

```json
{
  "date": "2026-05-08",
  "has_next": false,
  "items": [
    {
      "member": {
        "member_id": "65f000000000000000000011",
        "name": "张三"
      },
      "metrics": {
        "app": 2,
        "form_coop": 10,
        "form_workflow": 1,
        "dash": 3,
        "etl": 1,
        "aggregate": 0,
        "public_link": 2,
        "data_trigger": 1,
        "automation": 1,
        "bpa": 0
      }
    }
  ]
}
```

---

# 接口2：审计事件列表（参考文档）

> 审计事件列表是指用户获取到的日志范围（domain）中的具体事件名称。此文档为参考文档，非独立 API 接口。

文档有两个标记：
- **内测功能**：当用户加入功能内测时，才能获取到对应的数据，否则取不到数据；
- **独享版功能**：当简道云版本为独享版时才能获取到对应数据，否则取不到数据。

## 登录日志（login）

用户在简道云平台上的登录行为

| 功能模块 | 事件名称 | 事件参数 |
|---------|---------|----------|
| 登录登出 | 用户登录 | auth.session.login |

## 知识库管理（kms）

审计知识库管理员对知识库的操作行为

| 功能模块 | 事件名称 | 事件参数 |
|---------|---------|----------|
| 知识库 | 开启知识库 | admin.kms.enable |
| 知识库 | 关闭知识库 | admin.kms.disable |
| 知识库 | 创建知识库 | admin.kms.space_create |
| 知识库 | 修改知识库基本信息 | admin.kms.space_update |
| 知识库 | 删除知识库 | admin.kms.space_delete |
| 知识库 | 新建知识库权限组 | admin.kms.perm_group_create |
| 知识库 | 修改知识库权限组 | admin.kms.perm_group_update |
| 知识库 | 删除知识库权限组 | admin.kms.perm_group_delete |

## 应用管理日志（app_builder）

审计应用管理员对应用的操作行为

| 功能模块 | 事件名称 | 事件参数 | 备注 |
|---------|---------|----------|------|
| 应用管理 | 创建应用 | admin.app.create | |
| 应用管理 | 删除应用 | admin.app.delete | |
| 应用管理 | 修改应用名称 | admin.app.rename | |
| 应用管理 | 恢复应用 | admin.app.recover | |
| 应用管理 | 调整跨应用设置 | admin.app.ref_forms_set_update | |
| 应用管理 | 调整应用首页 | admin.app.home_update | |
| 应用管理 | 调整应用 URL | admin.app.url_update | |
| 应用管理 | 开启应用水印 | admin.app.watermark_enable | |
| 应用管理 | 关闭应用水印 | admin.app.watermark_disable | |
| 应用管理 | 开启应用附件管控 | admin.app.attachment_control_enable | |
| 应用管理 | 关闭应用附件管控 | admin.app.attachment_control_disable | |
| 应用管理 | 修改应用附件管控 | admin.app.attachment_control_update | |
| 应用管理 | 添加应用管理员 | admin.app.manager_add | |
| 应用管理 | 删除应用管理员 | admin.app.manager_remove | |
| 应用管理 | 添加应用管理组 | admin.app.manage_group_create | |
| 应用管理 | 删除应用管理组 | admin.app.manage_group_delete | |
| 应用管理 | 修改应用管理组名称 | admin.app.manage_group_rename | |
| 应用管理 | 开启应用管理组 | admin.app.manage_group_enable | |
| 应用管理 | 关闭应用管理组 | admin.app.manage_group_disable | |
| 应用管理 | 修改产品风格 | admin.app.style_update | |
| 应用管理 | 开启多语言管理 | admin.app.locale_enable | 内测功能 |
| 应用管理 | 修改「多语言管理」默认语言 | admin.app.locale_change_locale | 内测功能 |
| 应用管理 | 修改「多语言管理」支持语言 | admin.app.locale_change_locales | 内测功能 |
| 应用管理 | 导出产品日志 | admin.app.log_export | |
| 应用管理 | 导出历史产品日志 | admin.app.history_log_export | |
| 表单管理 | 创建表单 | admin.form.create | |
| 表单管理 | 删除表单 | admin.form.delete | |
| 表单管理 | 修改表单名称 | admin.form.rename | |
| 表单管理 | 修改表单设计 | admin.form.update | |
| 表单管理 | 恢复表单 | admin.form.recover | |
| 表单管理 | 修改流程设计 | admin.form.flow_update | |
| 表单管理 | 调整表单权限 | admin.form.auth_update | |
| 表单管理 | 批量调整表单/仪表盘权限 | admin.form.auth_batch_update | |
| 表单管理 | 调整表单公开链接 | admin.form.public_link | |
| 表单管理 | 调整表单公开查询 | admin.form.public_query | |
| 表单管理 | 调整表单在线支付 | admin.form.online_pay | |
| 表单管理 | 切换表单类型 | admin.form.type_change | |
| 表单管理 | 编辑数据详情页 | admin.form.data_page_update | |
| 表单管理 | 切换数据详情页 | admin.form.data_page_switch | |
| 表单管理 | 删除数据详情页 | admin.form.data_page_delete | |
| 表单管理 | 开启流程分析 | admin.form.flow_analysis_enable | |
| 表单管理 | 关闭流程分析 | admin.form.flow_analysis_disable | |
| 数据操作 | 创建数据 | data.record.create | |
| 数据操作 | 修改数据 | data.record.update | |
| 数据操作 | 批量修改数据 | data.record.batch_update | |
| 数据操作 | 删除数据 | data.record.delete | |
| 数据操作 | 批量删除数据 | data.record.batch_delete | |
| 数据操作 | 恢复数据 | data.record.recover | |
| 数据操作 | 批量恢复数据 | data.record.batch_recover | |
| 数据操作 | 导入-新增数据 | data.record.import | |
| 数据操作 | 导入-更新数据 | data.record.import_update | |
| 数据操作 | 导入-更新和新增数据 | data.record.import_upsert | |
| 数据操作 | 导入附件 | data.record.import_file | |
| 数据操作 | 导出数据 | data.record.export | |
| 数据操作 | 打印数据 | data.record.print | |
| 数据操作 | 批量打印 | data.record.batch_print | |
| 数据操作 | 打印二维码/条形码 | data.record.print_qr | |
| 数据操作 | 下载文件 | data.file.download | |
| 数据操作 | 归档数据 | data.record.archive | 内测功能 |
| 数据操作 | 恢复归档数据 | data.record.unarchive | 内测功能 |
| 仪表盘 | 创建仪表盘 | admin.dash.create | |
| 仪表盘 | 删除仪表盘 | admin.dash.delete | |
| 仪表盘 | 恢复仪表盘 | admin.dash.recover | |
| 仪表盘 | 修改仪表盘设计 | admin.dash.update | |
| 仪表盘 | 修改仪表盘名称 | admin.dash.rename | |
| 仪表盘 | 调整仪表盘权限 | admin.dash.auth_update | |
| 仪表盘 | 调整仪表盘公开链接 | admin.dash.public_link | |
| 聚合表 | 创建聚合表 | admin.aggregate.create | |
| 聚合表 | 删除聚合表 | admin.aggregate.delete | |
| 聚合表 | 修改聚合表名称 | admin.aggregate.rename | |
| 聚合表 | 修改聚合表设计 | admin.aggregate.update | |
| 聚合表 | 迁移聚合表 | admin.aggregate.migrate | |
| 智能助手 | 创建智能助手 | system.automation.create | |
| 智能助手 | 删除智能助手 | system.automation.delete | |
| 智能助手 | 修改智能助手 | system.automation.update | |
| 智能助手 | 开启智能助手 | system.automation.start | |
| 智能助手 | 关闭智能助手 | system.automation.stop | |
| 数据工厂 | 创建数据流 | system.etl.create | |
| 数据工厂 | 删除数据流 | system.etl.delete | |
| 数据工厂 | 修改数据流名称 | system.etl.rename | |
| 数据工厂 | 修改数据流设计 | system.etl.update | |
| 其他应用能力 | 添加普通管理组 | admin.manage_group.create | |
| 其他应用能力 | 删除普通管理组 | admin.manage_group.delete | |
| 其他应用能力 | 修改普通管理组名称 | admin.manage_group.rename | |
| 其他应用能力 | 添加普通管理员 | admin.manage_group.manager_add | |
| 其他应用能力 | 删除普通管理员 | admin.manage_group.manager_remove | |
| 其他应用能力 | 修改企业工作台 | admin.workbench.update | |
| 其他应用能力 | 开启消息推送 | admin.webhook.enable | |
| 其他应用能力 | 关闭消息推送 | admin.webhook.disable | |
| 其他应用能力 | 修改消息推送 | admin.webhook.update | |
| 其他应用能力 | 开启待办委托 | admin.bpm.delegation_enable | |
| 其他应用能力 | 关闭待办委托 | admin.bpm.delegation_disable | |
| 其他应用能力 | 调整待办委托 | admin.bpm.delegation_update | |
| 其他应用能力 | 设置支付服务 | admin.pay.update | |

## 平台管理日志（platform）

审计平台管理员在平台中的操作行为

| 功能模块 | 事件名称 | 事件参数 | 备注 |
|---------|---------|----------|------|
| 平台管理员与企业设置 | 添加管理员 | admin.platform.manager_add | |
| 平台管理员与企业设置 | 移除管理员 | admin.platform.manager_remove | |
| 平台管理员与企业设置 | 添加通讯录管理组 | admin.platform.group_create | |
| 平台管理员与企业设置 | 删除通讯录管理组 | admin.platform.group_remove | |
| 平台管理员与企业设置 | 修改通讯录管理组名称 | admin.platform.group_rename | |
| 平台管理员与企业设置 | 修改企业名称 | admin.corp.rename | |
| 平台管理员与企业设置 | 修改绑定信息 | admin.corp.integrate_update | |
| 平台管理员与企业设置 | 修改企业账号 URL | admin.corp.url_update | |
| 平台管理员与企业设置 | 修改时区 | admin.corp.timezone_update | |
| 平台管理员与企业设置 | 修改系统区域 | admin.corp.region_update | 内测功能 |
| 平台管理员与企业设置 | 修改语言 | admin.corp.locale_update | 内测功能 |
| 平台管理员与企业设置 | 身份认证 | admin.corp.verify | |
| 平台管理员与企业设置 | 开启企业风格 | admin.corp.theme_enable | |
| 平台管理员与企业设置 | 关闭企业风格 | admin.corp.theme_disable | |
| 平台管理员与企业设置 | 修改企业风格 | admin.corp.theme_update | |
| 订单与云币 | 修改云币支付设置 | admin.coin.config_update | |
| 订单与云币 | 创建订单 | admin.order.create | |
| 订单与云币 | 支付订单 | admin.order.pay | |
| 订单与云币 | 取消订单 | admin.order.cancel | |
| 订单与云币 | 删除订单 | admin.order.delete | |
| 订单与云币 | 订单开票 | admin.order.receipt | |
| 集成、安全和套件 | 开启微信服务号集成 | admin.integration.wx_enable | |
| 集成、安全和套件 | 关闭微信服务号集成 | admin.integration.wx_disable | |
| 集成、安全和套件 | 开启自定义登录页 | admin.security.custom_login_enable | |
| 集成、安全和套件 | 关闭自定义登录页 | admin.security.custom_login_disable | |
| 集成、安全和套件 | 开启全局水印 | admin.security.watermark_enable | |
| 集成、安全和套件 | 关闭全局水印 | admin.security.watermark_disable | |
| 集成、安全和套件 | 开启全局附件管控 | admin.security.attachment_control_enable | |
| 集成、安全和套件 | 关闭全局附件管控 | admin.security.attachment_control_disable | |
| 集成、安全和套件 | 调整待办委托 | admin.bpm.delegation_update | |
| 集成、安全和套件 | 开启 AI 能力 | admin.ai.lab_enable | |
| 集成、安全和套件 | 关闭 AI 能力 | admin.ai.lab_disable | |
| 集成、安全和套件 | 启用产品 | admin.suite.enable | 内测功能 |
| 集成、安全和套件 | 停用产品 | admin.suite.disable | 内测功能 |
| 集成、安全和套件 | 设置产品可见范围 | admin.suite.scope_update | 内测功能 |
| 集成、安全和套件 | 调整提醒屏蔽 | admin.security.executive_update | |
| 审计与文件 | 恢复附件 | admin.file.recover | 独享版功能 |
| 审计与文件 | 清理附件 | admin.file.trash | 独享版功能 |
| 审计与文件 | 彻底删除附件 | admin.file.delete | 独享版功能 |
| 审计与文件 | 导出登录日志 | admin.audit.login_log_export | |
| 审计与文件 | 导出操作日志 | admin.audit.operate_log_export | |
| 审计与文件 | 导出云币使用日志 | admin.audit.coin_log_export | |
| 通讯录与角色 | 邀请成员 | admin.member.invite | |
| 通讯录与角色 | 主动退出企业 | admin.member.exit | |
| 通讯录与角色 | 转为离职 | admin.member.remove | |
| 通讯录与角色 | 修改成员信息 | admin.member.update | |
| 通讯录与角色 | 导出通讯录 | admin.member.export | |
| 通讯录与角色 | 停用成员 | admin.member.freeze | |
| 通讯录与角色 | 启用成员 | admin.member.recover | |
| 通讯录与角色 | 删除成员 | admin.member.hard_delete | |
| 通讯录与角色 | 添加部门 | admin.dept.create | |
| 通讯录与角色 | 删除部门 | admin.dept.delete | |
| 通讯录与角色 | 修改部门名称 | admin.dept.rename | |
| 通讯录与角色 | 修改部门主管 | admin.dept.manager_update | |
| 通讯录与角色 | 创建角色组 | admin.role_group.create | |
| 通讯录与角色 | 删除角色组 | admin.role_group.delete | |
| 通讯录与角色 | 修改角色组名称 | admin.role_group.rename | |
| 通讯录与角色 | 创建角色 | admin.role.create | |
| 通讯录与角色 | 删除角色 | admin.role.delete | |
| 通讯录与角色 | 修改角色名称 | admin.role.rename | |
| 通讯录与角色 | 调整角色分组 | admin.role.change_group | |
| 通讯录与角色 | 调整角色成员 | admin.role.member_update | |
| 通讯录与角色 | 设置分管部门 | admin.role.rel_update | |
| 通讯录与角色 | 交接工作 | admin.member.handover | |
| 通讯录与角色 | 导入角色 | admin.role.rel_import | |
| 通讯录与角色 | 导出角色 | admin.role.rel_export | |
| 互联组织与标签 | 邀请外部企业 | admin.coop.guest_connect | |
| 互联组织与标签 | 添加外部企业邀请链接 | admin.coop.link_create | |
| 互联组织与标签 | 删除外部企业邀请链接 | admin.coop.link_delete | |
| 互联组织与标签 | 编辑外部企业邀请链接 | admin.coop.link_update | |
| 互联组织与标签 | 修改外部企业信息 | admin.coop.guest_update | |
| 互联组织与标签 | 添加企业标签 | admin.dept_label.create | |
| 互联组织与标签 | 删除企业标签 | admin.dept_label.delete | |
| 互联组织与标签 | 修改企业标签名称 | admin.dept_label.update | |
| 互联组织与标签 | 调整企业标签内企业 | admin.dept_label.dept_update | |
| 互联组织与标签 | 修改外部对接人信息 | admin.coop.guest_docker_update | |
| 互联组织与标签 | 导出外部对接人 | admin.coop.guest_docker_export | |
| 互联组织与标签 | 添加外部对接人角色 | admin.coop.role_create | |
| 互联组织与标签 | 修改外部对接人角色名称 | admin.coop.role_rename | |
| 互联组织与标签 | 删除外部对接人角色 | admin.coop.role_delete | |
| 互联组织与标签 | 调整外部对接人角色成员 | admin.coop.role_update | |
| 互联组织与标签 | 添加我方对接人 | admin.coop.host_docker_create | |
| 互联组织与标签 | 移除我方对接人 | admin.coop.host_docker_delete | |
| 互联组织与标签 | 修改我方对接人信息 | admin.coop.host_docker_update | |
| 互联组织与标签 | 解除邀请我协作的企业的连接 | admin.coop.host_disconnect | |
| 互联组织与标签 | 申请代管通讯录 | admin.contact.tmp_owner_apply | |
| 互联组织与标签 | 移交代管权限 | admin.contact.tmp_owner_transfer | |
| API、插件和开放应用 | 新增密钥 | api.key.create | |
| API、插件和开放应用 | 启用密钥 | api.key.enable | |
| API、插件和开放应用 | 停用密钥 | api.key.disable | |
| API、插件和开放应用 | 删除密钥 | api.key.delete | |
| API、插件和开放应用 | 修改密钥 | api.key.update | |
| API、插件和开放应用 | 安装插件 | api.plugin.install | |
| API、插件和开放应用 | 启用插件 | api.agent.enable | |
| API、插件和开放应用 | 停用插件 | api.agent.disable | |
| API、插件和开放应用 | 删除插件 | api.agent.uninstall | |
| API、插件和开放应用 | 新建插件 | api.plugin.create | |
| API、插件和开放应用 | 修改插件 | api.plugin.update | |
| API、插件和开放应用 | 发布插件 | api.plugin.pull_request | |
| API、插件和开放应用 | 复制插件 | api.plugin.duplicate | |
| API、插件和开放应用 | 导出插件 | api.plugin.export | |
| API、插件和开放应用 | 导入插件 | api.plugin.import | |
| API、插件和开放应用 | 导入更新插件 | api.plugin.import_overwrite | |
| API、插件和开放应用 | 创建数据连接 | api.data_source.connection_create | |
| API、插件和开放应用 | 修改数据连接 | api.data_source.connection_update | |
| API、插件和开放应用 | 删除数据连接 | api.data_source.connection_delete | |
| API、插件和开放应用 | 创建同步表 | api.data_source.sync_table_create | |
| API、插件和开放应用 | 修改同步细节 | api.data_source.sync_table_update | |
| API、插件和开放应用 | 删除同步表 | api.data_source.sync_table_delete | |
| API、插件和开放应用 | 设置同步表定时 | api.data_source.sync_table_schedule_update | |
| API、插件和开放应用 | 批量定时同步 | api.data_source.sync_table_schedule_batch_update | |
| API、插件和开放应用 | 同步数据 | api.data_source.sync_table_trigger_sync | |
| API、插件和开放应用 | 停止同步 | api.data_source.sync_table_stop_sync | |
| API、插件和开放应用 | 同步指定范围数据 | api.data_source.sync_table_range_sync | |
| API、插件和开放应用 | 批量同步表 | api.data_source.sync_table_batch_sync | |
| API、插件和开放应用 | 新增授权 | api.oauth.create | |
| API、插件和开放应用 | 解除授权 | api.oauth.delete | |
| API、插件和开放应用 | 创建集成应用 | api.open_application.create | |
| API、插件和开放应用 | 修改集成应用 | api.open_application.update | |
| API、插件和开放应用 | 删除集成应用 | api.open_application.delete | |
| API、插件和开放应用 | 启用集成应用 | api.open_application.enable | |
| API、插件和开放应用 | 停用集成应用 | api.open_application.disable | |
| API、插件和开放应用 | 启用 MCP 服务 | api.member_mcp.enable | |
| API、插件和开放应用 | 停用 MCP 服务 | api.member_mcp.disable | |
| API、插件和开放应用 | 创建 MCP 服务 | api.member_mcp.create | |
| API、插件和开放应用 | 修改 MCP 服务 | api.member_mcp.update | |
| API、插件和开放应用 | 删除 MCP 服务 | api.member_mcp.delete | |
| API、插件和开放应用 | 重新授权 MCP 服务 | api.member_mcp.renew | |
| API、插件和开放应用 | 重置 MCP 服务链接 | api.member_mcp.refresh | |
| API、插件和开放应用 | 新建自定义环境 | api.custom_runtime.create | |
| API、插件和开放应用 | 删除自定义环境 | api.custom_runtime.delete | |
| API、插件和开放应用 | 修改自定义环境名称 | api.custom_runtime.rename | |

---

# 接口3：获取审计日志类型定义接口

## 1. 简介

获取当前企业支持的审计日志范围和事件类型定义。调用时可先调用本接口，获取「日志范围（domain）」与「事件名称（event_types）」后，再调用审计日志明细接口按范围查询日志。

### 支持获取的日志范围

| 日志范围（domain） | 说明 | 可用过滤字段 |
|-------------------|------|-------------|
| login | 用户登录日志 | filters.actor_ids |
| platform | 企业、通讯录、API 配置、插件、开放平台的管理日志 | filters.actor_ids |
| app_builder | 应用、表单、仪表盘、聚合表、智能助手、数据工厂等应用搭建日志 | filters.actor_ids, filters.app_ids, filters.entry_ids |
| kms | 知识库管理日志 | filters.actor_ids |

注：日志范围（domain）中的具体事件名称可参见：审计事件列表。

### 版本说明

本功能为付费高级功能，简道云旗舰版、独享版可用，其他版本请联系销售增购。

### 接口版本

| 接口版本 | 更新时间 | 版本说明 |
|---------|---------|----------|
| V1 | 2026.05.28 | 原始接口 |

## 2. 接口调用

仅获取当前 API Key 所属企业可查询的审计日志类型定义。

- **请求地址**：`https://api.jiandaoyun.com/api/v1/audit_log/domains`
- **请求频率**：30 次/秒
- **请求方式**：POST

### 请求参数

| 参数 | 必须 | 类型 | 说明 |
|------|------|------|------|
| —— | —— | —— | 请求体传入空对象 `{}` |

### 请求示例

```json
{}
```

### 响应参数

| 参数 | 类型 | 说明 |
|------|------|------|
| domains | String | 审计日志范围列表 |
| domains[].domain | String | 范围标识，查询明细时传入 domain |
| domains[].event_types | String | 当前范围支持的事件类型列表，查询明细时可传入 event_types |

### 响应示例

```json
{
  "domains": [
    {
      "domain": "login",
      "event_types": [
        "auth.session.login"
      ]
    },
    {
      "domain": "app_builder",
      "event_types": [
        "admin.app.create",
        "admin.app.watermark_enable"
      ]
    }
  ]
}
```

---

# 接口4：获取审计日志明细接口

## 1. 简介

按范围查询当前企业的审计日志明细。

### 版本说明

本功能为付费高级功能，简道云旗舰版、独享版可用，其他版本请联系销售增购。

### 接口版本

| 接口版本 | 更新时间 | 版本说明 |
|---------|---------|----------|
| v1 | 2026.05.28 | 原始接口 |

## 2. 接口调用

- **请求地址**：`https://api.jiandaoyun.com/api/v1/audit_log/list`
- **请求频率**：30 次/秒
- **请求方式**：POST

### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| domain | String | 是 | 日志范围 |
| time_range.start | String | 是 | 查询开始时间，UTC 时间。格式示例：2026-04-01T00:00:00.000Z |
| time_range.end | String | 是 | 查询结束时间，UTC 时间。格式示例：2026-04-13T23:59:59.000Z |
| event_types | String[] | 否 | 事件类型列表。不传表示查询当前日志范围（domain）支持的全部事件类型 |
| limit | Number | 否 | 单次返回条数，默认 200，最大 200 |
| cursor | String | 否 | 分页游标。首次查询不传；下一页使用上次响应的 cursor |
| filters | Object | 否 | 过滤条件，取值见【3. 过滤条件】 |

### 注意事项

1. time_range 的跨度不能超过 31 天。
2. 一次请求只能查询一个日志范围（domain）。
3. 传入当前日志范围（domain）不支持的 filters 字段会返回参数错误。
4. 分页按事件时间倒序。

### 请求示例

**查询登录日志：**
```json
{
  "domain": "login",
  "time_range": {
    "start": "2026-04-01T00:00:00.000Z",
    "end": "2026-04-13T23:59:59.000Z"
  },
  "event_types": [
    "auth.session.login"
  ],
  "filters": {
    "actor_ids": [
      "660000000000000000000010",
      "660000000000000000000011"
    ]
  },
  "limit": 100,
  "cursor": ""
}
```

**查询平台管理日志：**
```json
{
  "domain": "platform",
  "time_range": {
    "start": "2026-04-01T00:00:00.000Z",
    "end": "2026-04-13T23:59:59.000Z"
  },
  "event_types": [
    "admin.member.invite",
    "admin.member.remove",
    "admin.dept.create",
    "api.key.create"
  ],
  "filters": {
    "actor_ids": [
      "660000000000000000000020",
      "660000000000000000000021"
    ]
  },
  "limit": 100,
  "cursor": ""
}
```

**查询应用搭建日志：**
```json
{
  "domain": "app_builder",
  "time_range": {
    "start": "2026-04-01T00:00:00.000Z",
    "end": "2026-04-13T23:59:59.000Z"
  },
  "event_types": [
    "data.record.create",
    "data.record.update",
    "data.record.batch_update",
    "data.record.delete",
    "data.record.import",
    "data.record.export",
    "admin.form.update",
    "admin.dash.export"
  ],
  "filters": {
    "actor_ids": [
      "660000000000000000000030",
      "660000000000000000000031"
    ],
    "app_ids": [
      "59264073a2a60c0c08e20bfb"
    ],
    "entry_ids": [
      "59264073a2a60c0c08e20bfd"
    ]
  },
  "limit": 100,
  "cursor": ""
}
```

**查询知识库日志：**
```json
{
  "domain": "kms",
  "time_range": {
    "start": "2026-04-01T00:00:00.000Z",
    "end": "2026-04-13T23:59:59.000Z"
  },
  "event_types": [
    "admin.kms.enable",
    "admin.kms.space_create",
    "admin.kms.space_update",
    "admin.kms.perm_group_update"
  ],
  "filters": {
    "actor_ids": [
      "660000000000000000000040",
      "660000000000000000000041"
    ]
  },
  "limit": 100,
  "cursor": ""
}
```

### 响应参数

| 参数 | 含义 |
|------|------|
| has_more | 是否有下一页 |
| cursor | 下一页游标（has_more 为 true 时返回） |
| items | 审计日志列表 |
| items[].event_id | 事件 ID |
| items[].event_time | 事件发生时间，UTC 时间字符串 |
| items[].event_type | 标准事件类型 |
| items[].domain | 审计日志范围 |
| items[].tenant | 企业的租户 ID |
| items[].actor | 操作人信息 |
| items[].actor.type | 操作人类型，一般为 user |
| items[].actor.id | 操作人 ID |
| items[].actor.name | 操作人名称 |
| items[].actor.ip | 操作客户端 IP 地址 |
| items[].actor.user_agent | 客户端用户代理信息 |
| items[].actor.geo | 地理位置，仅在日志范围是 login 时有值 |
| items[].event | 事件属性 |
| items[].event.category | 事件分类 |
| items[].event.action | 执行动作 |
| items[].event.outcome | 执行结果 |
| items[].event.severity | 严重等级 |
| items[].resource | 被操作资源信息 |
| items[].resource.type | 被操作资源类型 |
| items[].resource.id | 被操作资源 ID |
| items[].resource.name | 被操作资源名称 |
| items[].resource.parent_id | 被操作资源所属父资源 ID |
| items[].resource.parent_type | 被操作资源所属父资源类型 |
| items[].detail | 事件详情 |

### 响应示例

```json
{
  "has_more": true,
  "cursor": "MTc3NjE1OTAwMDAwMCw2NjExMjIzMzQ0NTU2Njc3ODg5OWFhYmI=",
  "items": [
    {
      "event_id": "681f2de2-9722-34ca-bd2a-dda99b615e46",
      "event_time": "2026-05-11T09:09:38.792Z",
      "event_type": "data.record.print",
      "domain": "app_builder",
      "tenant": {
        "id": "68665cf9f8acef49b8e29917"
      },
      "actor": {
        "type": "user",
        "id": "68665cf9f8acef49b8e29917",
        "name": "z3",
        "ip": "172.24.72.2",
        "user_agent": "Mozilla/5.0",
        "geo": null
      },
      "event": {
        "category": "data",
        "action": "print",
        "outcome": "success",
        "severity": "info"
      },
      "resource": {
        "type": "form",
        "id": "689d59d8d241955ee4908625",
        "name": "车辆信息基础表",
        "parent_id": "68994cb727cc65376feb985d",
        "parent_type": "app"
      },
      "detail": {
        "template": "data_print",
        "params": {
          "template_name": "系统模板",
          "data_label": "A",
          "link": "/dashboard/app/68994cb727cc65376feb985d/form/689d59d8d241955ee4908625/data/69c6297fbf7965a4d21e5ec2/qr_link"
        }
      }
    }
  ]
}
```

## 3. 过滤条件

| 日志范围（domain） | 支持的过滤字段 | 说明 |
|-------------------|---------------|------|
| login | actor_ids | 按操作人成员 ID 过滤 |
| platform | actor_ids | 按操作人成员 ID 过滤 |
| app_builder | actor_ids, app_ids, entry_ids | 按操作人成员 ID、应用 ID、表单/仪表盘 ID、操作对象过滤 |
| kms | actor_ids | 按操作人成员 ID 过滤 |

### 过滤字段说明

| 参数 | 类型 | 说明 |
|------|------|------|
| filters.actor_ids | String[] | 操作人成员 ID 列表 |
| filters.app_ids | String[] | 应用 ID 列表，仅日志范围为应用管理时支持 |
| filters.entry_ids | String[] | 表单、仪表盘等 ID 列表，仅当日志范围为应用管理（app_builder）时支持 |


---

## 十、完整错误码对照表

### 10.1 HTTP 状态码

| 状态码 | 说明 |
|--------|------|
| 2xx | 响应成功 |
| 400 | 接口错误统一返回（含 code + msg） |
| 429 | 超出请求并发限制 |
| 502 | 网关异常 |
| 579 | 文件上传失败 |

### 10.2 业务错误码（状态码 400 时返回）

| 错误码 | 英文说明 | 中文说明 | 排查建议 |
|--------|----------|----------|----------|
| 1 | The request is invalid. | 错误的请求 | 检查参数是否缺失 |
| 1005 | The email already exists. | 邮箱已存在 | 可尝试邮箱验证码登录确认是否已注册 |
| 1010 | The member doesn't exist. | 用户不存在 | 检查成员参数是否正确传入 |
| 1017 | The username is in an invalid format. | 用户名不符合格式要求 | 常规格式为字母数字下划线任意组合，长度50个字符以内 |
| 1018 | The email is in an invalid format. | 用户邮箱不符合格式要求 | 检查邮件地址 |
| 1019 | The member's nickname is in an invalid format. | 用户昵称不符合格式要求 | 检查是否长度在80个字符以下且无特殊字符 |
| 1022 | The member's current company/team doesn't exist. | 用户团队不存在 | 稍后重试，仍然出现可以咨询技术支持 |
| 1024 | The mobile number is invalid. | 手机号码不正确 | 请重新输入手机号 |
| 1027 | The phone number already exists. | 手机号码已存在 | 使用手机号验证码登录确认是否已注册 |
| 1058 | Do not have permission to call the task list. | 用户操作权限不足 | 检查权限配置 |
| 1065 | The member has already been added to the team. | 当前用户已加入团队 | 检查当前团队内是否已经有当前用户 |
| 1082 | The phone number/email is required. | 手机号和邮箱不能同时为空 | 至少填写一个 |
| 1085 | The member's nickname is required. | 昵称不能为空 | 填写昵称 |
| 1087 | Duplicate unique fields. | 唯一性字段重复 | 检查成员 ID 的重复情况 |
| 1092 | The length of the username has exceeded the limit. | 工号长度超出限制 | 确认工号长度在 50 个字符以内 |
| 1096 | The request contains invalid member parameter(s). | 用户参数不合法 | 请检查后重试 |
| 1201 | The role doesn't exist. | 企业角色信息不存在 | 检查参数后重试 |
| 1202 | Unable to operate synchronized role or role groups | 无法操作同步的角色/角色组 | 确认当前角色/角色组非其他平台同步而来 |
| 1203 | The role group/role information is invalid. | 角色/角色组信息不合法 | 检查参数后重试 |
| 1205 | The role group is required. | 必须指定角色组 | 检查参数后重试 |
| 1206 | The role group doesn't exist. | 指定的角色组不存在 | 检查参数后重试 |
| 1207 | The length of the role group name has exceeded the limit. | 角色/角色组名称长度超限 | 确保长度在 24 个字符以内 |
| 1208 | Can't delete a role group with member(s). | 非空角色组不能删除 | 确保删除角色组下角色后重试 |
| 2004 | The app doesn't exist. | 应用不存在 | 检查参数后重试 |
| 3000 | The form doesn't exist. | 表单不存在 | 检查参数后重试 |
| 3001 | The member or department name is required. | 名称不能为空 | 填写名称 |
| 3005 | The request contains invalid parameter(s). | 参数不正确 | 检查参数 |
| 3041 | The number of Serial No. fields has exceeded the limit. | 单个表单流水号控件数量超出上限 | 有且只能有一个 |
| 3042 | Failed to verify the field alias. | 字段别名校验失败 | 检查别名是否含有特殊字符，常规格式为字母数字下划线任意组合 |
| 3083 | The number of widgets has exceeded the limit. | 控件数量超过上限 | 一般情况下上限为 500 |
| 3091 | The number of characters in the form name exceeds 100. | 表单名称不能超过 100 个字符 | 缩短名称 |
| 3092 | The number of characters in the title exceeds 100. | 标题不能超过 100 个字符 | 缩短标题 |
| 4000 | Failed to submit data. | 数据提交失败 | 检查数据格式 |
| 4001 | Data doesn't exist. | 数据不存在 | 检查 data_id |
| 4007 | No approver for the workflow. | 操作失败，没有流程处理人 | 检查流程配置 |
| 4008 | The workflow was closed. | 操作失败，流程已经关闭 | 流程已结束 |
| 4009 | Do not have permission to approve. | 操作失败，无权限 | 检查权限 |
| 4012 | Operation failed. This form is being used in other batch editing tasks. | 操作失败，当前表单正在执行其他批量编辑任务 | 请稍后重试 |
| 4015 | The approver of the transferred node is invalid. | 操作失败，当前节点不存在该候选人 | 检查转交目标 |
| 4016 | The workflow can't be transferred to oneself. | 操作失败，流程不能转交给自己 | 选择其他转交人 |
| 4025 | Do not have permission for the workflow. | 您没有数据流程权限 | 检查权限配置 |
| 4042 | Failed to delete the data. | 数据删除失败 | 检查参数后重试 |
| 4402 | Failed to validate the aggregation calculation. | 聚合计算校验失败 | 检查参数后重试 |
| 4815 | The filter condition is invalid. | 过滤条件设置有误 | 可能是过滤条件过于冗长导致 |
| 5003 | The workflow node doesn't exist. | 流程节点不存在 | 检查节点配置 |
| 5004 | No comment for approval. | 未提交流程审批意见 | 填写审批意见 |
| 5009 | The approver of the returned node is invalid. | 找不到回退后的负责人 | 检查回退节点配置 |
| 5011 | The target node is invalid. | 找不到流转节点 | 检查流程配置 |
| 5012 | No signature for approval. | 未提交流程手写签名 | 提交手写签名 |
| 5034 | This node has child workflow(s)/plugin node(s). | 目标节点包含子流程/插件节点 | 调整目标节点 |
| 5044 | The child workflow is wrongly configured. | 子流程配置错误或找不到发起人 | 检查子流程配置 |
| 5045 | The number of child workflow exceeds 200. | 发起子流程数据超过上限 200 | 减少数据量 |
| 5049 | The Transfer feature hasn't been enabled at this node. | 当前流程节点未开启转交 | 在节点配置中开启转交 |
| 5053 | The initial department is invalid. | 流入多级主管审批节点失败，未指定发起部门 | 指定发起部门 |
| 6000 | There is a sub-department with the same name. | 已存在同名部门 | 检查同级的父部门下所有子部门，排查同名情况 |
| 6001 | The parent department doesn't exist. | 父部门不存在 | 检查 parent_no |
| 6002 | The department doesn't exist. | 部门不存在 | 检查参数后重试 |
| 6003 | Can't delete a department with sub-department(s). | 存在子部门，不能删除 | 先删除子部门 |
| 6004 | Failed to update the department. | 部门修改失败 | 检查参数 |
| 6005 | Failed to create the department. | 部门创建失败 | 稍后重试 |
| 6006 | Can't delete a department with member(s). | 部门内存在成员，不能删除 | 先转移成员 |
| 6010 | The department ID is in an invalid format. | 部门编号不在合法范围内 | 检查参数后重试 |
| 6011 | There is a circular relationship among departments. | 部门关系存在循环 | 不允许的部门树关系，检查参数 |
| 6012 | The department name is invalid. | 部门名称不合法 | 检查参数后重试 |
| 6013 | The department ID already exists. | 部门编号重复 | 检查同级的父部门下所有子部门，排查编号重复 |
| 6014 | There must be at least one sub-department belonging to the root department. | 至少需要一个子部门属于根部门 | 保留至少一个子部门 |
| 6015 | Can't delete a root department. | 根部门不能被删除 | 不可删除根部门 |
| 6017 | The number of cascade levels in the department exceeds the limit. | 部门级联层数超出限制 | 部门树深度限制为 16 |
| 6019 | The member list is required. | 成员列表不能为空 | 检查参数后重试 |
| 6020 | The number of departments in a single import exceeds the limit. | 单次导入部门数量超出限制 | 上限为 10 万 |
| 6021 | The number of members in a single import exceeds the limit. | 单次导入成员数量超出限制 | 上限为 2 万 |
| 6064 | The parent department already exists. | 已是目标部门的子部门 | 无需重复操作 |
| 7103 | System usage exceeds the limit. | 系统用量超出限制，系统已暂停使用 | 至「企业管理-版本信息」查看版本使用详情和升级版本以恢复系统 |
| 7206 | System limit exceeded. The system has been disabled. | 系统用量超出限制，系统已暂停使用 | 请尽快联系贵司简道云管理者升级版本以恢复系统 |
| 7212 | Monthly data exceeds the limit. | 该账号的本月数据流量已用完，无法提交新数据 | 请联系账号创建者升级版本 |
| 7216 | Attachment upload limit exceeded (link creator). | 附件上传量超过当前版本限制 | 请联系链接发布者开启云币支付 |
| 7217 | Attachment upload limit exceeded (business owner). | 附件上传量超过当前版本限制 | 请联系企业创建者开启云币支付 |
| 7218 | Attachment upload limit exceeded. Purchase cloud coins (link). | 附件上传量超过当前版本限制 | 请联系链接发布者充值云币 |
| 7219 | Attachment upload limit exceeded. Purchase cloud coins (owner). | 附件上传量超过当前版本限制 | 请联系企业创建者充值云币 |
| 7221 | This form has exceeded the limit. | API 新增数据超出当前版本限制 | 请联系企业创建者或系统管理员 |
| 8017 | Company/Team doesn't exist or has been closed. | 企业不存在或者已经被解散 | 检查参数后重试 |
| 8301 | Failed to verify the API key for authorization. | API 签名校验失败 | 检查 API Key 是否正确 |
| 8302 | Do not have permission for the API calls. | 没有接口请求权限 | 检查 API Key 授权范围 |
| 8303 | The call frequency of the company/team exceeds the frequency limit. | 企业 API 请求次数达到频率上限 | 可等待 1s 后重试，频繁发生可以排查企业 API 请求占用情况 |
| 8304 | The call frequency exceeds the frequency limit. | 当前接口请求次数达到频率上限 | 可等待 1s 后重试当前接口 |
| 9004 | Failed to create the task. | 队列任务创建失败 | 稍后重试 |
| 9007 | Failed to obtain the lock. | 锁获取失败 | 稍后重试 |
| 17017 | The request contains invalid parameter(s). | 平台 API 的参数异常 | 检查参数后重试 |
| 17018 | The API key is invalid. | 无效的 API Key | 检查 Key 是否启用/正确 |
| 17023 | The batch update at one time exceeds the limit. | 单次批量修改数量超出限制 | 上限为 100 |
| 17024 | The batch creation at one time exceeds the limit. | 单次批量创建数量超出限制 | 上限为 100 |
| 17025 | The transaction_id contains invalid parameter(s). | transaction_id 参数格式不正确 | 检查格式 |
| 17026 | The transaction_id already exists. | transaction_id 重复 | 请修改后重试 |
| 17027 | Failed to upload the API file. | API 文件上传失败 | 稍后重试 |
| 17032 | The field type isn't supported. | 不支持的字段类型 | 检查参数后重试 |
| 17033 | The limit for batch deletion quantity has been exceeded. | 批量删除数据超出数量限制 | 请调整数量后重试 |
| 17034 | The sub-field type isn't supported. | 不支持的子表单字段类型 | 检查参数后重试 |
| 17052 | Not included in the IP whitelist. | 不在 IP 白名单内 | 检查对应 API Key 相关配置 |
| 17053 | Not among the authorized apps. | 不在应用授权范围内 | 检查对应 API Key 相关配置 |
| 17054 | Not among the authorized APIs. | 不在接口授权范围内 | 检查对应 API Key 相关配置 |
| 30002 | Unable to retrieve the pre-set CRM form now. | CRM 预设表单暂不支持调用 | 使用自定义表单 |
| 50000 | The target node doesn't exist. | 目标节点不存在 | 检查节点 ID |
| 50004 | The task doesn't exist. | 待办任务不存在 | 检查 task_id |
| 50008 | Workflow processing error. | 流转异常 | 稍后重试 |
| 50011 | The task doesn't exist. | 执行实例不存在 | 检查实例 ID |
| 50014 | No permission to close the task. | 操作人不能为空 | 填写操作人 |
| 50016 | The instance_id is invalid. | 流程实例不存在 | 检查 instance_id |
| 50019 | The action is not supported. | 不支持的审批行为 | 检查参数后重试 |
| 50021 | The data_id is invalid. | 关联业务对象不存在 | 检查 data_id |
| 50031 | The data_id is invalid. | 流程数据不存在 | 检查 data_id |
| 50040 | This node can't be returned. | 当前节点禁止回退 | 检查节点配置并确认节点未在执行 |
| 50041 | Can't return to the current node. | 回退节点为当前节点 | 选择其他回退目标 |
| 50047 | Workflow being migrated. Try again later. | 流程迁移中 | 请稍后再试 |
| 50049 | Can't return to the Start Node without an initiator. | 不允许回退到没有创建者的发起节点 | 确认发起人存在 |
| 50051 | The workflow has been approved/transferred/returned. | 流程已被处理 | 请刷新后查看 |
| 50053 | No approver to add. | 加签候选人列表不能为空 | 检查参数后重试 |
| 50054 | Can't add nested approval. | 不支持嵌套加签 | 检查参数后重试 |
| 50055 | No pre-approver or post-approver was added. | 仅支持前后加签任务处理 | 检查参数后重试 |
| 50056 | The parent task is lost. | 加签父任务丢失，可能已经被处理 | 检查参数后重试 |
| 50057 | The Add Approver feature hasn't been enabled. | 加签配置未开启 | 在节点配置中开启加签 |
| 50059 | The member has been added as an approver. | 加签候选人不能选择节点负责人 | 选择其他候选人 |
| 50060 | The approver is invalid. | 加签候选人非法 | 检查候选人 |
| 50061 | Can't add more than one approver. | 不支持多人加签 | 只加签一人 |
| 50062 | The added approver is reviewing the task. | 待被加签人处理中 | 等待处理完成 |
| 50070 | Can't return to the plugin node. | 不允许回退到插件节点 | 选择其他回退目标 |
| 50073 | Can't return to the in-progress node. | 禁止回退到进行中节点 | 选择其他回退目标 |
| 50082 | The choice of back type is missing. | 缺少回退人选择 | 填写 back_type 参数 |

### 10.3 流程专用错误码补充

| 错误码 | 说明 |
|--------|------|
| 4005 | 操作失败，不允许撤回 |
| 4026 | 流程状态，进行中流程无法激活 |
| 5006 | 无法将数据流转到抄送节点 |
| 5008 | 找不到对应的负责人 |
| 5010 | 无效的流程数据 |
| 5024 | 当前用户对该节点无提交权限 |
| 5025 | 当前节点已经流转完成 |
| 5026 | 流程节点批量审批失败 |
| 5056 | 不能对非流程表单进行流程操作 |
| 5058 | 数据已关联流程，不可重复发起 |
| 5059 | 数据提交人已被删除 |
| 5060 | 非流程表单，不支持该操作 |
| 50009 | 流程已被处理，不允许撤回 |
| 50013 | 负责人调整前后数目必须一致 |
| 50015 | 负责人调整前后无实际变化 |
| 50024 | 调整后负责人不能为空 |
| 50034 | 不支持的流程操作类型 |
| 50046 | 历史待办（子流程）过多，不允许激活 |
| 50052 | 节点不支持该加签行为 |
| 50063 | 被加签待办不可批量提交 |
| 50064 | 异步子流程成环，请调整流程配置 |
| 50071 | 版本不支持插件节点 |
| 50076 | 该节点不可激活 |


---

## 十一、其他开放能力

| 能力 | 说明 | 文档入口 |
|------|------|----------|
| 数据推送（Webhook） | 数据/表单/流程/消息事件推送到自有服务器 | 开发指南 >> 数据推送 |
| 前端事件 | 表单内触发自定义 HTTP 请求（OCR、物流查询、短信等） | 开发指南 >> 前端事件 |
| 单点登录 | SAML2.0 / 自定义接口 / CAS | 开发指南 >> 单点登录 |
| 自建插件 | 在表单内运行自定义 JS 函数 | 开发者工具 >> 自建插件 |
| MCP 服务 (Beta) | AI 集成 | 开发者工具 >> MCP服务 |
| 插件市场 | 第三方插件（OCR、短信、电子签章、数据同步等） | 开放市场 >> 插件市场 |

