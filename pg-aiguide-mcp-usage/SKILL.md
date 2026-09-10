---
name: pg-aiguide-mcp-usage
description: 调用 pg-aiguide MCP 获取 PostgreSQL / TimescaleDB / PostGIS / pgvector 的版本准确文档与设计技能。用于建表选型、索引、hypertable、向量检索、混合搜索、零停机迁移等问题，替代凭记忆作答。
---

# pg-aiguide MCP 使用指导

TigerData 官方文档 MCP（`type: http`，`https://mcp.tigerdata.com/docs`）。两个工具：`search_docs` 检索文档片段，`view_skill` 读取成套设计方法论。

**用它而不是凭记忆**：PostgreSQL / TimescaleDB 的语法与最佳实践按版本分化严重，训练数据里的写法常已过时（例：TimescaleDB 2.29 的 `direct_compress` 是 tech preview，较早的记忆里没有）。

## 何时触发

- 建表、选数据类型、约束、索引策略
- 时序数据、hypertable、压缩策略、连续聚合、保留策略
- pgvector 嵌入存储、HNSW/IVFFlat 索引、RAG 检索
- 全文检索、BM25、混合搜索、RRF
- PostGIS 空间数据
- 零停机 schema 迁移、ALTER TABLE 锁级别

## search_docs — 文档检索

四个参数**全部必填**。`limit` 和 `semanticWeight` 即使想用默认值也必须显式给出（可传 `null`），否则报 `is required`。

```json
{"source": "tiger", "query": "compression policy", "limit": 5, "semanticWeight": 0.5}
```

`source` 枚举（必须精确匹配）：

| 值 | 覆盖范围 |
|---|---|
| `tiger` | Tiger Cloud + TimescaleDB |
| `postgres_14` … `postgres_18` | 对应大版本 PostgreSQL |
| `postgis_3.3` … `postgis_3.6` | PostGIS |

**没有不带版本号的 `postgres`**。写 `postgres` 会校验失败，必须选定版本；不确定用户环境版本时先问，或取最新 `postgres_18`。

`semanticWeight`：`0` 纯 BM25 关键词，`1` 纯向量语义，`0.5` 等权 RRF 融合，默认 `0.7` 偏语义。查确切函数名 / GUC 名用低值，查概念用高值。

返回 `results[]`，每项含 `content`（markdown 片段）、`metadata`（含 `source_url`，可给用户引用）、`rrf_score`。分数量级在 0.015 左右属正常，不要当作低置信度。

## view_skill — 设计方法论

两个参数**全部必填**：`skill_name` + `path`。看 SKILL.md 时 `path` 传空字符串，列目录传 `.`。

```json
{"skill_name": "setup-timescaledb-hypertables", "path": ""}
```

`skill_name` 传 `.` 列出全部可用技能。当前 9 个：

| 技能 | 用途 |
|---|---|
| `postgres` | 总入口，泛 PostgreSQL 工作 |
| `design-postgres-tables` | 通用建表、数据类型、约束、JSONB |
| `design-postgis-tables` | 空间表设计、坐标系、空间索引 |
| `setup-timescaledb-hypertables` | 建 hypertable、压缩、保留、连续聚合 |
| `find-hypertable-candidates` | 扫现有库，评分哪些表该转 hypertable |
| `migrate-postgres-tables-to-hypertables` | 执行迁移，含蓝绿方案 |
| `pgvector-semantic-search` | 向量检索、HNSW 调参、量化 |
| `postgres-hybrid-text-search` | BM25 + 向量混合检索、RRF |
| `postgres-database-migration` | 零停机迁移、DDL 锁级别参考、回滚 |

先 `view_skill` 拿方法论，再 `search_docs` 补具体语法 —— 反过来容易只见树木。

## 边界

- **只读文档服务**，不连接任何数据库、不执行 SQL。要跑 SQL 另找连接方式。
- 返回的是 TigerData 视角的文档。纯 PostgreSQL 问题选 `postgres_NN` source，别让 Tiger 的商业特性混进通用建议。
- 文档与用户实际库版本不一致时以实测为准，先确认对方 `SELECT version()` 与扩展的 `extversion`。
- 标记 tech preview / 非生产就绪的特性（如 `direct_compress`）转述时必须带上该警告。
