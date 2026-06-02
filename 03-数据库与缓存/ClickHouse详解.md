# ClickHouse 速查手册

> 一份通俗易懂的 ClickHouse 文档，涵盖日常开发中最常用的操作和概念，适合快速查阅和上手。

---

## 目录

- [1. 基础概念](#1-基础概念)
- [2. 安装与连接](#2-安装与连接)
- [3. 数据库操作](#3-数据库操作)
- [4. 表操作与表引擎](#4-表操作与表引擎)
- [5. 数据类型](#5-数据类型)
- [6. 增删改查 (CRUD)](#6-增删改查-crud)
- [7. 查询进阶](#7-查询进阶)
- [8. 索引](#8-索引)
- [9. 物化视图与投影](#9-物化视图与投影)
- [10. 分布式与副本](#10-分布式与副本)
- [11. 用户权限管理](#11-用户权限管理)
- [12. 备份与恢复](#12-备份与恢复)
- [13. 性能优化](#13-性能优化)
- [14. 常见问题排查](#14-常见问题排查)
- [15. ClickHouse vs MySQL 对比](#15-clickhouse-vs-mysql-对比)

---

## 1. 基础概念

### 1.1 什么是 ClickHouse？

ClickHouse 是一个**列式存储的 OLAP 数据库管理系统**（Online Analytical Processing），由俄罗斯 Yandex 公司开源，专为**海量数据的实时分析查询**设计。

你可以把它理解为一个"超级分析引擎"：

- **行式数据库（MySQL）** = 按行存数据，适合"查某个用户的所有信息"
- **列式数据库（ClickHouse）** = 按列存数据，适合"统计 1 亿用户的平均年龄"

```
行式存储（MySQL）：
[id=1][name=张三][age=25][city=北京][id=2][name=李四][age=30][city=上海]...

列式存储（ClickHouse）：
id:    [1][2][3]...
name:  [张三][李四][王五]...
age:   [25][30][28]...
city:  [北京][上海][深圳]...

列式优势：SELECT AVG(age) 只需要读 age 这一列，其他列完全不碰！
```

### 1.2 ClickHouse vs MySQL 核心差异

| 维度 | MySQL | ClickHouse |
|------|-------|------------|
| 存储模型 | 行式存储 | **列式存储** |
| 场景 | OLTP（事务处理） | **OLAP（分析查询）** |
| 事务 | 完整 ACID 支持 | **不强调事务**，写入是批量追加 |
| 更新/删除 | 频繁 UPDATE/DELETE | **不适合频繁更新**，只适合批量写入 |
| 单点查询 | 按 ID 查一行很快 | 不是强项，更适合全量聚合 |
| 聚合查询 | 慢（需扫描所有行） | **极快**（只读需要的列 + 向量化执行） |
| 索引 | B+Tree 唯一索引 | **稀疏索引**，不保证唯一 |
| 并发 | 支持高并发读写 | **低并发**，QPS 通常几十到几百 |
| 数据压缩 | 一般 | **极高压缩比**（5-20 倍） |

### 1.3 核心术语

| 术语 | 说明 | 与 MySQL 的区别 |
|------|------|---------------|
| 数据库 Database | 存放表的容器 | 相同 |
| 表 Table | 存储数据的结构 | 但必须指定**表引擎** |
| 表引擎 Engine | 表的存储/查询实现方式 | **ClickHouse 特有**，最重要的概念 |
| 列 Column | 表的一列 | 可以为空数组、NULL 需额外开启 |
| 排序键 ORDER BY | 表的物理排序依据 | 类似 MySQL 的聚簇索引，但**不保证唯一** |
| 分区键 PARTITION BY | 表的分区依据 | 按年月分区，方便快速裁剪和过期 |
| 主键 PRIMARY KEY | 稀疏索引的关键字段 | **不等同于唯一约束**，可重复 |

---

## 2. 安装与连接

### macOS

```bash
# 方式一：Homebrew
brew install clickhouse
clickhouse server  # 启动服务端
clickhouse client  # 启动客户端

# 方式二：通过 Docker（推荐，方便管理）
docker run -d --name clickhouse-server \
  -p 8123:8123 -p 9000:9000 \
  clickhouse/clickhouse-server
```

### Linux (Ubuntu/Debian)

```bash
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv E0C56BD4
echo "deb https://packages.clickhouse.com/deb stable main" | sudo tee /etc/apt/sources.list.d/clickhouse.list
sudo apt update
sudo apt install clickhouse-server clickhouse-client

# 启动
sudo systemctl start clickhouse-server
```

### 连接方式

```bash
# 方式一：原生 TCP 客户端（端口 9000）
clickhouse-client -h 127.0.0.1 -u default --password 'your_password'

# 方式二：HTTP 接口（端口 8123）
curl 'http://localhost:8123/?query=SELECT%201'

# 方式三：MySQL 兼容协议（端口 9004）
mysql -h 127.0.0.1 -P 9004 -u default
```

### 常用客户端工具

- **命令行**：`clickhouse-client`（自带）
- **图形化**：DBeaver（免费，支持 ClickHouse）、Tabix（Web UI）
- **Grafana**：数据可视化，ClickHouse 官方数据源插件

### 端口一览

| 端口 | 协议 | 用途 |
|------|------|------|
| 9000 | TCP Native | 原生客户端协议（性能最好） |
| 8123 | HTTP | REST 接口、JDBC/ODBC 驱动 |
| 9004 | MySQL Wire | MySQL 兼容协议 |
| 9009 | TCP | 副本间复制通信 |
| 9010 | TCP | 分布式查询内部通信 |

---

## 3. 数据库操作

```sql
-- 查看所有数据库
SHOW DATABASES;

-- 创建数据库
CREATE DATABASE IF NOT EXISTS analytics;

-- 查看创建语句
SHOW CREATE DATABASE analytics;

-- 切换数据库
USE analytics;

-- 查看当前使用的数据库
SELECT currentDatabase();

-- 删除数据库（危险操作！）
DROP DATABASE IF EXISTS analytics;
```

> **注意**：ClickHouse 数据库不指定字符集（不像 MySQL 需要 `utf8mb4`），默认支持 UTF-8。

---

## 4. 表操作与表引擎

### 4.1 什么是表引擎？

**表引擎是 ClickHouse 最重要的概念**，它决定了：

- 数据如何存储、在哪里存储
- 支持哪些查询操作
- 是否支持索引、副本、分布式
- 数据如何合并、过期

### 4.2 核心引擎选型

| 引擎 | 用途 | 支持副本 | 支持 UPDATE/DELETE |
|------|------|---------|-------------------|
| **MergeTree** | 基础引擎，最常用 | 通过 ReplicatedMergeTree | 异步 mutation |
| **ReplacingMergeTree** | 自动去重（按排序键） | 同上 | 异步 mutation |
| **SummingMergeTree** | 自动汇总数值列 | 同上 | 异步 mutation |
| **AggregatingMergeTree** | 自动聚合 | 同上 | 异步 mutation |
| **CollapsingMergeTree** | 折叠更新（标记删除） | 同上 | 异步 mutation |
| **TinyLog** | 简单测试，不支持索引 | 否 | 否 |
| **Log** | 简单测试，支持并发读 | 否 | 否 |
| **Memory** | 内存存储，重启丢失 | 否 | 否 |
| **Distributed** | 分布式查询代理 | 无 | 代理到实际表 |
| **Kafka** | Kafka 消费到 ClickHouse | 无 | 否 |

### 4.3 创建表（MergeTree 家族）

**MergeTree 建表语法必须包含三个关键子句：**

```sql
-- 基础 MergeTree 表（最常用）
CREATE TABLE user_events (
    event_date  Date          COMMENT '事件日期',
    event_time  DateTime      COMMENT '事件时间',
    user_id     UInt64        COMMENT '用户ID',
    event_type  String        COMMENT '事件类型',
    page_url    String        COMMENT '页面URL',
    duration_ms UInt32        COMMENT '停留时长(ms)',
    extra_info  String        COMMENT '扩展信息'
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_date)       -- 按月分区（必须）
ORDER BY (event_date, user_id, event_type)  -- 排序键（必须）
PRIMARY KEY (event_date, user_id)       -- 主键（可选，默认等于 ORDER BY）
SETTINGS index_granularity = 8192;      -- 索引粒度（可选，默认8192行）
```

```sql
-- ReplacingMergeTree：自动去重（用在数据可能重复的场景）
CREATE TABLE user_latest (
    user_id     UInt64,
    name        String,
    email       String,
    updated_at  DateTime
) ENGINE = ReplacingMergeTree(updated_at)   -- 按 updated_at 保留最新
ORDER BY user_id;                            -- ORDER BY 是去重的判断依据

-- SummingMergeTree：自动汇总数值列（用在预聚合场景）
CREATE TABLE daily_sales (
    date        Date,
    product_id  UInt64,
    sales       UInt64,
    amount      Decimal(10, 2)
) ENGINE = SummingMergeTree(sales, amount)   -- 汇总这两列
ORDER BY (date, product_id);
```

### 4.4 ORDER BY vs PRIMARY KEY

这是 ClickHouse 最容易混淆的点：

```sql
-- 情况1：不指定 PRIMARY KEY → PRIMARY KEY = ORDER BY
ORDER BY (a, b, c)          → PRIMARY KEY = (a, b, c)

-- 情况2：指定 PRIMARY KEY → 必须是 ORDER BY 的前缀
ORDER BY (a, b, c, d)
PRIMARY KEY (a, b)          → 主键是 (a, b)，但数据按 (a, b, c, d) 排序
```

| 作用 | ORDER BY | PRIMARY KEY |
|------|----------|-------------|
| 数据物理排序 | ✅ 是 | ❌ 否 |
| 稀疏索引生成 | ✅ 基于此生成 | ❌ 仅决定索引覆盖字段 |
| 去重（Replacing等） | ✅ 以完整的 ORDER BY 为准 | ❌ 无关 |
| 主键是否唯一 | ❌ **不唯一** | ❌ **不唯一** |

### 4.5 查看和修改表

```sql
-- 查看所有表
SHOW TABLES;

-- 查看表结构
DESCRIBE TABLE user_events;
DESC user_events;

-- 查看建表语句
SHOW CREATE TABLE user_events;

-- 添加列
ALTER TABLE user_events ADD COLUMN device_type String AFTER page_url;

-- 修改列注释
ALTER TABLE user_events MODIFY COLUMN device_type String COMMENT '设备类型';

-- 删除列
ALTER TABLE user_events DROP COLUMN extra_info;

-- 重命名表
RENAME TABLE user_events TO user_events_backup;
```

> **注意**：所有 ALTER 操作在 MergeTree 引擎下是轻量级的（只改元数据），不会重写数据。

### 4.6 删除表

```sql
-- 删除表（不可恢复！）
DROP TABLE user_events;

-- 如果存在才删除（推荐）
DROP TABLE IF EXISTS user_events;

-- TRUNCATE（清空数据，保留表结构）
TRUNCATE TABLE user_events;

-- ClickHouse 没有 DELETE 全表的做法（太慢），用 TRUNCATE 替代
-- 如果要删除部分数据，用 ALTER TABLE ... DELETE 或分区 DROP
```

---

## 5. 数据类型

### 5.1 整数类型

| 类型 | 字节 | 范围 | 常用场景 |
|------|------|------|---------|
| UInt8 | 1 | 0 ~ 255 | 年龄、状态码 |
| UInt16 | 2 | 0 ~ 65535 | 端口号 |
| UInt32 | 4 | 0 ~ 42亿 | 数量、ID |
| UInt64 | 8 | 0 ~ 1.8×10^19 | 用户ID、时间戳 |
| Int8 | 1 | -128 ~ 127 | 偏移量 |
| Int32 | 4 | -21亿 ~ 21亿 | 普通整数 |

```sql
-- ClickHouse 强烈建议：使用有符号/无符号明确指定范围
user_id  UInt64          -- 用户ID（非负）
age      UInt8           -- 年龄（0-255）
delta    Int32           -- 可能为负的差值
```

**与 MySQL 的差异：ClickHouse 不需要 `BIGINT`/`INT` 这种模糊类型，直接选字节数。**

### 5.2 浮点数与定点数

```sql
-- Float32 / Float64：近似值，不推荐存金额
price_f Float64          -- ⚠️ 有精度问题

-- Decimal(P, S)：精确小数，强烈推荐用于金额！
amount  Decimal(10, 2)   -- 最大 99999999.99
ratio   Decimal(5, 4)    -- 0.0000 ~ 9.9999
```

### 5.3 字符串类型

| 类型 | 说明 | 与 MySQL 对比 |
|------|------|-------------|
| String | 变长，无上限 | 类似 TEXT/长 VARCHAR |
| FixedString(N) | 定长 N 字节 | 类似 CHAR(N) |

```sql
name    String          -- 通用字符串（推荐）
md5     FixedString(32) -- MD5 固定 32 字节
```

> **注意**：ClickHouse 没有 VARCHAR(N) 长度限制，直接用 String。

### 5.4 日期时间类型

| 类型 | 格式 | 说明 |
|------|------|------|
| Date | YYYY-MM-DD | 日期，2 字节 |
| DateTime | YYYY-MM-DD HH:MM:SS | 日期时间，4 字节 |
| DateTime64(3) | 同上 + 毫秒 | 高精度时间 |

```sql
event_date  Date          -- 事件日期（推荐做分区键）
event_time  DateTime      -- 事件时间
created_at  DateTime64(3) -- 毫秒级创建时间（默认东八区）
```

> **注意**：ClickHouse 没有 `TIMESTAMP ON UPDATE CURRENT_TIMESTAMP` 这样的自动更新机制，需要业务层传入。

### 5.5 特殊类型

```sql
-- 数组（原生支持，MySQL 没有）
tags Array(String)

-- 元组
point Tuple(Float64, Float64)

-- 低基数枚举（省空间，适合少数几个固定值）
event_type LowCardinality(String)  -- 如果只有 page_view/click/login 等几种值

-- JSON（ClickHouse 22.3+）
extra_info JSON

-- UUID
user_uuid UUID

-- 可为空（默认列不允许 NULL，需要显式指定）
nickname Nullable(String)   -- ⚠️ 有性能开销，尽量不用
```

---

## 6. 增删改查 (CRUD)

### 6.1 插入数据 (INSERT)

```sql
-- 插入单行
INSERT INTO user_events (event_date, event_time, user_id, event_type, page_url)
VALUES ('2024-06-01', '2024-06-01 10:30:00', 10001, 'page_view', '/home');

-- 批量插入（强烈推荐！ClickHouse 的写入优化就是为批量设计的）
INSERT INTO user_events (event_date, event_time, user_id, event_type, page_url) VALUES
    ('2024-06-01', '2024-06-01 10:30:00', 10001, 'page_view', '/home'),
    ('2024-06-01', '2024-06-01 10:31:00', 10002, 'click', '/products'),
    ('2024-06-01', '2024-06-01 10:32:00', 10003, 'login', '/');

-- 从查询结果插入
INSERT INTO user_events SELECT * FROM user_events_backup WHERE event_date = '2024-06-01';

-- 从文件导入（最高效的批量写入方式）
clickhouse-client --query "INSERT INTO user_events FORMAT CSV" < /data/events.csv

-- 批量提交建议：每次 1000~10000 行，每秒不超过 1 次提交
-- ❌ 单行逐条插入：极慢，ClickHouse 不是为 OLTP 设计的
-- ✅ 批量汇聚写入：快 100 倍以上
```

### 6.2 查询数据 (SELECT)

```sql
-- 查询所有列（分析场景可以，ClickHouse 本身就是全量扫描）
SELECT * FROM user_events WHERE event_date = '2024-06-01';

-- 查询指定列（更高效，列式存储天然优势）
SELECT event_date, user_id, event_type FROM user_events;

-- 去重
SELECT DISTINCT event_type FROM user_events;
```

### 6.3 条件查询 (WHERE)

```sql
-- 比较运算符
SELECT * FROM user_events WHERE user_id = 10001;
SELECT * FROM user_events WHERE duration_ms >= 1000;

-- IN / NOT IN
SELECT * FROM user_events WHERE event_type IN ('page_view', 'click');

-- LIKE（和 MySQL 一样）
SELECT * FROM user_events WHERE page_url LIKE '/product/%';

-- 正则（ClickHouse 特有）
SELECT * FROM user_events WHERE match(page_url, '^/product/[0-9]+');

-- 区间
SELECT * FROM user_events WHERE event_date BETWEEN '2024-06-01' AND '2024-06-30';

-- 多条件
SELECT * FROM user_events
WHERE event_date = '2024-06-01'
  AND event_type = 'page_view'
  AND duration_ms > 1000;
```

### 6.4 更新数据 (UPDATE) — ⚠️ 异步操作

```sql
-- ⚠️ ClickHouse 的 UPDATE 是异步 mutation，不是即时生效！
ALTER TABLE user_events
UPDATE page_url = '/new-home'
WHERE page_url = '/home';

-- 查看 mutation 执行状态
SELECT * FROM system.mutations WHERE is_done = 0;

-- 为什么要异步？
-- ClickHouse 是列存 + 批量写入设计，原地更新需要重写整列
-- 所以用 mutation 机制：标记 → 后台异步替换
-- 适合批量更新历史数据，不适合频繁小范围更新

-- ❌ 不要做的事：每条数据独立 UPDATE（MySQL 用惯了容易犯错）
-- ✅ 正确做法：如果业务频繁需要更新，考虑 ReplacingMergeTree 在上报端处理
```

### 6.5 删除数据 (DELETE) — ⚠️ 异步操作

```sql
-- ⚠️ DELETE 也是异步 mutation
ALTER TABLE user_events DELETE WHERE event_date < '2023-01-01';

-- 更快的方式：直接 DROP 分区
ALTER TABLE user_events DROP PARTITION '202301';

-- 查看所有分区
SELECT partition, name, rows
FROM system.parts
WHERE table = 'user_events';
```

> **MySQL → ClickHouse 思维转换：不要用 DELETE 删旧数据，用 TTL 自动过期或用 DROP PARTITION。**

### 6.6 TTL 自动过期（ClickHouse 特有）

```sql
-- 列 TTL：到期自动清除某列数据
CREATE TABLE user_events_ttl (
    event_date  Date,
    user_id     UInt64,
    page_url    String TTL event_date + INTERVAL 30 DAY,  -- 30天后该列置空
    event_time  DateTime
) ENGINE = MergeTree()
ORDER BY user_id;

-- 表 TTL：到期自动删除整行
CREATE TABLE user_events_ttl2 (
    event_date  Date,
    user_id     UInt64,
    page_url    String
) ENGINE = MergeTree()
ORDER BY user_id
TTL event_date + INTERVAL 90 DAY;  -- 90天后整行删除
```

---

## 7. 查询进阶

### 7.1 排序 (ORDER BY)

```sql
SELECT * FROM user_events
WHERE event_date = '2024-06-01'
ORDER BY duration_ms DESC
LIMIT 100;
```

### 7.2 分页 (LIMIT BY / LIMIT OFFSET)

```sql
-- 传统分页（数据量大时避免大 offset）
SELECT * FROM user_events
ORDER BY event_time DESC
LIMIT 10 OFFSET 0;

-- LIMIT BY：按某列分组取 TopN（ClickHouse 特有！）
-- 每个用户取最近 5 条事件
SELECT user_id, event_type, event_time
FROM user_events
ORDER BY event_time DESC
LIMIT 5 BY user_id;
```

### 7.3 聚合函数

```sql
-- 基本聚合（和 MySQL 一样）
SELECT
    event_type,
    COUNT(*)          AS pv,
    COUNT(DISTINCT user_id) AS uv,
    AVG(duration_ms)  AS avg_duration,
    MAX(duration_ms)  AS max_duration,
    MIN(duration_ms)  AS min_duration
FROM user_events
WHERE event_date = '2024-06-01'
GROUP BY event_type
ORDER BY pv DESC;

-- ClickHouse 特有聚合函数
SELECT
    -- 精确去重（比 COUNT(DISTINCT) 快得多）
    uniqExact(user_id)    AS exact_uv,

    -- 近似去重（亿级数据也秒出，误差约 2%）
    uniq(user_id)         AS approx_uv,

    -- 分位数
    quantile(0.5)(duration_ms)  AS p50,
    quantile(0.95)(duration_ms) AS p95,
    quantile(0.99)(duration_ms) AS p99,

    -- TopK
    topK(10)(event_type)        -- 返回出现频率最高的 10 个值
FROM user_events;
```

### 7.4 分组 (GROUP BY)

```sql
-- 基础分组
SELECT
    toStartOfHour(event_time) AS hour,
    event_type,
    COUNT(*) AS cnt
FROM user_events
WHERE event_date = '2024-06-01'
GROUP BY hour, event_type
ORDER BY hour, cnt DESC;

-- GROUP BY 的三种模式
-- WITH ROLLUP：逐级汇总（类似 MySQL 的 WITH ROLLUP）
SELECT event_date, event_type, COUNT(*)
FROM user_events
GROUP BY event_date, event_type WITH ROLLUP;

-- WITH CUBE：多维汇总
SELECT event_date, event_type, COUNT(*)
FROM user_events
GROUP BY event_date, event_type WITH CUBE;
```

### 7.5 连接查询 (JOIN)

**⚠️ ClickHouse 的 JOIN 和 MySQL 有很大不同，需要特别注意！**

```sql
-- 创建用户维度表（Memory 引擎，做 JOIN 的右表）
CREATE TABLE user_dim (
    user_id UInt64,
    name    String,
    city    String
) ENGINE = Memory;

-- 1. 普通 JOIN
SELECT
    e.event_type,
    u.name,
    u.city,
    COUNT(*) AS pv
FROM user_events e
INNER JOIN user_dim u ON e.user_id = u.user_id
WHERE e.event_date = '2024-06-01'
GROUP BY e.event_type, u.name, u.city;

-- 2. LEFT ANY JOIN（跟 MySQL 的 LEFT JOIN 语义不同）
-- 任意匹配一条即可，而不是多行展开
SELECT e.*, u.city
FROM user_events e
LEFT ANY JOIN user_dim u ON e.user_id = u.user_id;

-- 3. ASOF JOIN（时序关联，ClickHouse 特有！）
-- 查找每个用户事件"最近一次"的维度信息
SELECT e.*, u.city AS latest_city
FROM user_events e
ASOF LEFT JOIN user_dim u
ON e.user_id = u.user_id AND e.event_time >= u.updated_at;
```

**JOIN 性能建议：**

| 建议 | 说明 |
|------|------|
| 大表在左，小表在右 | ClickHouse 会把右表加载到内存 |
| 优先用字典代替 JOIN | `dictGet()` 比 JOIN 快 10-100 倍 |
| 避免跨分片 JOIN | 尽量让 JOIN 的两张表在同一节点 |
| 不要在大表之间 JOIN | 考虑用物化视图预关联 |

### 7.6 子查询

```sql
-- WHERE 中的子查询
SELECT *
FROM user_events
WHERE user_id IN (
    SELECT user_id
    FROM user_events
    WHERE event_type = 'purchase'
);

-- FROM 中的子查询（和 MySQL 一样）
SELECT event_type, avg_duration
FROM (
    SELECT event_type, AVG(duration_ms) AS avg_duration
    FROM user_events
    WHERE event_date = '2024-06-01'
    GROUP BY event_type
)
WHERE avg_duration > 1000;
```

### 7.7 WITH 子句 (CTE)

```sql
-- 定义临时结果集
WITH active_users AS (
    SELECT user_id
    FROM user_events
    WHERE event_date = '2024-06-01'
    GROUP BY user_id
    HAVING COUNT(*) > 10
)
SELECT e.*
FROM user_events e
INNER JOIN active_users a ON e.user_id = a.user_id;
```

### 7.8 ARRAY JOIN（展平数组，ClickHouse 特有）

```sql
-- 数组字段展平为多行
SELECT user_id, tag
FROM user_events
ARRAY JOIN tags AS tag;

-- 场景：用户有多个标签，展开后统计每个标签的用户数
SELECT tag, COUNT(DISTINCT user_id) AS user_cnt
FROM user_events
ARRAY JOIN tags AS tag
GROUP BY tag
ORDER BY user_cnt DESC;
```

---

## 8. 索引

### 8.1 ClickHouse 的索引和 MySQL 完全不同

| 维度 | MySQL (InnoDB) | ClickHouse (MergeTree) |
|------|---------------|----------------------|
| 索引类型 | B+Tree | **稀疏索引** |
| 每个索引行覆盖 | 1 行 | **8192 行**（默认 granularity） |
| 主键唯一性 | ✅ 唯一 | **❌ 不唯一** |
| 索引大小 | 较大 | **极小**（是 B+Tree 的 1/1000） |
| 等值查询 | 极快 | 还行 |
| 范围扫描 | 较慢 | **极快** |
| 聚合查询 | 慢 | **极快** |

### 8.2 稀疏索引原理

```
普通索引（MySQL B+Tree）：        稀疏索引（ClickHouse）：
每行一条索引记录                  每 8192 行一条索引记录

行索引:  ■■■■■■■■■■■■■■■■■     ■               ■
数据:    ■■■■■■■■■■■■■■■■■     ■■■■■■■■■■■■■■■■■
         ↑ 索引很大                 ↑ 索引极小，但一次要读 8192 行
```

### 8.3 主键索引（PRIMARY KEY / ORDER BY）

```sql
-- ORDER BY 是索引的核心
-- 数据按 ORDER BY 的顺序在磁盘上物理排序
-- PRIMARY KEY 必须从 ORDER BY 列的最左前缀选择

CREATE TABLE events (
    date      Date,
    user_id   UInt64,
    event     String,
    value     Float64
) ENGINE = MergeTree()
ORDER BY (date, user_id)     -- 物理排序 + 全字段索引
PRIMARY KEY (date);          -- 只用 date 做稀疏索引
```

### 8.4 二级索引（跳数索引 / Bloom Filter）

```sql
-- 1. minmax 索引：记录每个 granule 的 min/max（适合范围查询）
ALTER TABLE user_events
ADD INDEX idx_duration duration_ms TYPE minmax GRANULARITY 4;

-- 2. set 索引：记录每个 granule 的去重值（适合 in 查询）
ALTER TABLE user_events
ADD INDEX idx_event_type event_type TYPE set(100) GRANULARITY 4;

-- 3. Bloom filter：快速判断值是否存在（适合等值查询）
ALTER TABLE user_events
ADD INDEX idx_user_id user_id TYPE bloom_filter() GRANULARITY 4;

-- 查看索引
SELECT * FROM system.data_skipping_indices WHERE table = 'user_events';
```

### 8.5 分区裁剪（最重要的"索引"）

```sql
-- 分区裁剪是 ClickHouse 最快的过滤方式！
-- 在建表时用 PARTITION BY 定义

-- 按天分区
PARTITION BY toYYYYMMDD(event_date)

-- 按月份分区（推荐，单分区数据量在 1~10GB 为佳）
PARTITION BY toYYYYMM(event_date)

-- 查询时，ClickHouse 自动跳过不相关的分区
SELECT COUNT(*) FROM user_events
WHERE event_date = '2024-06-01';
-- 只读 202406 这一个分区！
```

### 8.6 用 EXPLAIN 看查询计划

```sql
-- 查看索引使用情况
EXPLAIN indexes = 1
SELECT COUNT(*) FROM user_events WHERE event_date = '2024-06-01';

-- 查看执行计划
EXPLAIN
SELECT event_type, COUNT(*) FROM user_events WHERE event_date = '2024-06-01' GROUP BY event_type;

-- 查看预估性能
EXPLAIN ESTIMATE
SELECT AVG(duration_ms) FROM user_events WHERE user_id = 10001;
```

---

## 9. 物化视图与投影

### 9.1 物化视图（Materialized View）

物化视图是 ClickHouse 最强大的功能之一，实现**预聚合加速**。

```sql
-- 1. 创建目标表（存聚合结果）
CREATE TABLE hourly_stats (
    hour        DateTime,
    event_type  String,
    pv          UInt64,
    uv          UInt64,
    avg_duration Float64
) ENGINE = SummingMergeTree()
ORDER BY (hour, event_type);

-- 2. 创建物化视图（自动从源表写入到目标表）
CREATE MATERIALIZED VIEW mv_hourly_stats
TO hourly_stats
AS
SELECT
    toStartOfHour(event_time) AS hour,
    event_type,
    COUNT(*)                  AS pv,
    uniq(user_id)             AS uv,
    AVG(duration_ms)          AS avg_duration
FROM user_events
GROUP BY hour, event_type;
```

**物化视图 vs 普通视图：**

| 维度 | 普通视图 | 物化视图 |
|------|---------|---------|
| 是否存数据 | ❌ 不存，每次查询实时计算 | ✅ 持久化存储聚合结果 |
| 查询速度 | 取决于原始数据量 | **极快**（已预聚合） |
| 数据延迟 | 无延迟 | 写入后几秒内可见 |
| 用途 | 封装复杂查询逻辑 | **加速固定模式的聚合查询** |

### 9.2 投影（Projection）

```sql
-- 为表添加投影（类似二级聚合索引）
ALTER TABLE user_events
ADD PROJECTION proj_user_type (
    SELECT
        user_id,
        event_type,
        COUNT(*),
        AVG(duration_ms)
    GROUP BY user_id, event_type
);

-- 后续查询自动使用投影加速
SELECT user_id, event_type, COUNT(*), AVG(duration_ms)
FROM user_events
GROUP BY user_id, event_type;
-- ClickHouse 自动扫描投影而非原始数据
```

---

## 10. 分布式与副本

### 10.1 分布式架构概览

```
                  ┌─────────────┐
                  │ Distributed │  ← 逻辑表，分发查询
                  └──────┬──────┘
         ┌───────────────┼───────────────┐
    ┌────▼────┐    ┌────▼────┐    ┌────▼────┐
    │ Shard 1 │    │ Shard 2 │    │ Shard 3 │  ← 物理分片
    │ ┌──────┐ │    │ ┌──────┐ │    │ ┌──────┐ │
    │ │Repl.1│ │    │ │Repl.1│ │    │ │Repl.1│ │
    │ │Repl.2│ │    │ │Repl.2│ │    │ │Repl.2│ │  ← 每分片有副本
    │ └──────┘ │    │ └──────┘ │    │ └──────┘ │
    └─────────┘    └─────────┘    └─────────┘
```

### 10.2 创建副本表（ReplicatedMergeTree）

```sql
-- 每个节点上创建相同的 ReplicatedMergeTree 表
CREATE TABLE user_events_repl ON CLUSTER 'my_cluster' (
    event_date  Date,
    event_time  DateTime,
    user_id     UInt64,
    event_type  String
) ENGINE = ReplicatedMergeTree(
    '/clickhouse/tables/{shard}/user_events',  -- ZooKeeper 路径
    '{replica}'                                  -- 副本标识
)
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_date, user_id);
```

### 10.3 创建分布式表（Distributed）

```sql
-- 分布式表本身不存数据，只是"代理"到各个分片
CREATE TABLE user_events_dist ON CLUSTER 'my_cluster' AS user_events_repl
ENGINE = Distributed(
    'my_cluster',        -- 集群名
    default,             -- 数据库名
    user_events_repl,    -- 本地表名
    rand()               -- 分片键（用 rand 随机分布，或用 user_id 按用户哈希）
);

-- 写入分布式表 → 自动分发到各个分片
INSERT INTO user_events_dist VALUES ('2024-06-01', now(), 10001, 'page_view');

-- 查询分布式表 → 自动汇总所有分片
SELECT event_type, COUNT(*) FROM user_events_dist GROUP BY event_type;
```

### 10.4 字典（Dictionary，替代 JOIN 的高效方式）

```sql
-- 创建字典（类似"全局维度表"）
CREATE DICTIONARY city_dict (
    city_id     UInt64,
    city_name   String,
    province    String
)
PRIMARY KEY city_id
SOURCE(CLICKHOUSE(TABLE 'city_dim' DB 'default'))
LAYOUT(FLAT())        -- FLAT = 按主键数组查找，最快
LIFETIME(3600);       -- 缓存 1 小时

-- 用字典函数查询（比 JOIN 快 10-100 倍）
SELECT
    user_id,
    dictGet('city_dict', 'city_name', city_id) AS city_name
FROM user_events;
```

---

## 11. 用户权限管理

### 11.1 配置文件管理（XML/yml）

```xml
<!-- /etc/clickhouse-server/users.d/appuser.xml -->
<clickhouse>
    <users>
        <appuser>
            <password>secure_password</password>
            <networks>
                <ip>10.0.0.0/8</ip>
                <ip>127.0.0.1</ip>
            </networks>
            <profile>default</profile>
            <quota>default</quota>
            <allow_databases>
                <database>analytics</database>
            </allow_databases>
        </appuser>
    </users>
</clickhouse>
```

### 11.2 SQL 驱动管理（24.11+ 版本）

```sql
-- 创建用户
CREATE USER appuser IDENTIFIED BY 'secure_password';

-- 授权
GRANT SELECT ON analytics.* TO appuser;
GRANT SELECT, INSERT ON analytics.user_events TO appuser;
GRANT ALL ON analytics.* TO admin_user;

-- 查看权限
SHOW GRANTS FOR appuser;

-- 撤销权限
REVOKE INSERT ON analytics.* FROM appuser;

-- 修改密码
ALTER USER appuser IDENTIFIED BY 'new_password';

-- 删除用户
DROP USER appuser;
```

### 11.3 客户端连接验证

```bash
# 带密码连接
clickhouse-client -h 127.0.0.1 -u appuser --password 'secure_password'

# HTTP 接口带认证
curl -u appuser:secure_password 'http://localhost:8123/?query=SELECT+1'
```

---

## 12. 备份与恢复

### 12.1 文件级冷备份（停服备份）

```bash
# 1. 停止 ClickHouse
sudo systemctl stop clickhouse-server

# 2. 复制数据目录
cp -r /var/lib/clickhouse /var/lib/clickhouse_backup_20240601

# 3. 启动 ClickHouse
sudo systemctl start clickhouse-server
```

### 12.2 使用 clickhouse-backup 工具（推荐）

```bash
# 安装
wget https://github.com/Altinity/clickhouse-backup/releases/download/v2.5.0/clickhouse-backup-linux-amd64.tar.gz
tar xf clickhouse-backup-linux-amd64.tar.gz
sudo mv clickhouse-backup /usr/local/bin/

# 创建备份（不停止服务）
clickhouse-backup create backup_20240601

# 查看备份列表
clickhouse-backup list

# 恢复备份
clickhouse-backup restore backup_20240601

# 上传到 S3
clickhouse-backup upload backup_20240601
```

### 12.3 导出数据

```bash
# 导出为 CSV
clickhouse-client --query "SELECT * FROM user_events WHERE event_date = '2024-06-01'" --format CSV > events.csv

# 导出为 Native 格式（二进制，最快）
clickhouse-client --query "SELECT * FROM user_events" --format Native > events.native

# 从 Native 文件恢复
clickhouse-client --query "INSERT INTO user_events FORMAT Native" < events.native

# 导出整个分区
ALTER TABLE user_events EXPORT PARTITION '202406';
```

---

## 13. 性能优化

### 13.1 写入优化

```sql
-- 1. 批量写入（最重要！）
-- ❌ 单行 INSERT：每次创建一个独立的 part，导致 merge 压力巨大
-- ✅ 批量 INSERT：建议每批 1000~100000 行

-- 2. 控制写入频率
-- 建议每秒不超过 1 次 INSERT，可用 Buffer 引擎缓冲
CREATE TABLE user_events_buffer AS user_events
ENGINE = Buffer(default, user_events, 16, 10, 60, 10000, 100000, 10000000, 10000000);

-- 写入 Buffer 表（自动缓冲后批量写入目标表）
INSERT INTO user_events_buffer VALUES (...);

-- 3. 避免过多分区
-- ❌ 按秒分区：产生几百万个分区，系统崩溃
-- ✅ 按天或按月分区
PARTITION BY toYYYYMM(event_date)  -- 按月，单分区百万到千万行
```

### 13.2 查询优化

```sql
-- 1. 优先用分区裁剪
-- ✅ 好：走分区
SELECT COUNT(*) FROM user_events WHERE event_date = '2024-06-01';
-- ❌ 差：对分区键做函数导致分区失效
SELECT COUNT(*) FROM user_events WHERE toYYYYMM(event_date) = 202406;

-- 2. 优先用 PREWHERE 替代 WHERE（自动优化）
-- ClickHouse 会自动将 WHERE 中"最过滤"的条件移到 PREWHERE 阶段
-- PREWHERE 是列存特有的：先在少量列上过滤，再读其他列

-- 3. 用物化视图做预聚合
-- 亿级数据直接查 → 1 秒写到聚合表 → 查聚合表只要 0.01 秒

-- 4. 避免 SELECT * 中的大字段
-- 如果只需要统计，不要拉出 String 大字段
SELECT event_type, COUNT(*) FROM user_events WHERE event_date = '2024-06-01' GROUP BY event_type;

-- 5. 用采样（SAMPLE）快速估算
SELECT event_type, COUNT(*) * 10 AS estimated_pv
FROM user_events SAMPLE 0.1  -- 只扫描 10% 的数据！
WHERE event_date = '2024-06-01'
GROUP BY event_type;
```

### 13.3 配置优化

```xml
<!-- /etc/clickhouse-server/config.xml -->

<!-- 最大并发查询数 -->
<max_concurrent_queries>100</max_concurrent_queries>

<!-- 最大并发插入数 -->
<max_concurrent_inserts>16</max_concurrent_inserts>

<!-- 后台 merge 线程数 -->
<background_pool_size>16</background_pool_size>
```

```sql
-- 查询常用配置
SHOW SETTINGS LIKE '%max_threads%';
SHOW SETTINGS LIKE '%memory%';

-- 单次查询最大内存
SET max_memory_usage = 10000000000;  -- 10GB

-- 单次查询最大执行时间
SET max_execution_time = 300;  -- 300 秒

-- 并行线程数（默认为 CPU 核数）
SET max_threads = 8;
```

### 13.4 数据分区和 TTL 设置最佳实践

```sql
-- 推荐配置：
-- 1. 单分区数据量：1~10GB
-- 2. 单分区行数：100万~1亿行
-- 3. 按天或按月分区
-- 4. 合理设置 TTL 自动清理

CREATE TABLE events_best_practice (
    event_date  Date,
    event_time  DateTime,
    user_id     UInt64,
    event_type  String,
    page_url    String,
    duration_ms UInt32
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_date)   -- 按月分区
ORDER BY (event_date, user_id, event_type)
TTL event_date + INTERVAL 90 DAY;  -- 90 天自动删除
```

---

## 14. 常见问题排查

### 14.1 慢查询分析

```sql
-- 查看当前运行的查询
SELECT
    query_id,
    user,
    query,
    elapsed,
    read_rows,
    formatReadableSize(read_bytes) AS read_size,
    memory_usage
FROM system.processes
WHERE elapsed > 5;

-- 终止慢查询
KILL QUERY WHERE query_id = 'xxxxx';

-- 查看查询日志
SELECT
    event_time,
    query_duration_ms,
    read_rows,
    formatReadableSize(read_bytes) AS read_size,
    result_rows,
    query
FROM system.query_log
WHERE type = 'QueryFinish'
  AND query_duration_ms > 1000
ORDER BY query_duration_ms DESC
LIMIT 10;
```

### 14.2 复制延迟

```sql
-- 查看复制表状态
SELECT
    table,
    is_leader,
    is_readonly,
    absolute_delay,       -- 复制延迟秒数
    queue_size,           -- 待复制队列大小
    inserts_in_queue
FROM system.replicas
WHERE absolute_delay > 10;

-- 手动同步副本
SYSTEM SYNC REPLICA user_events_repl;
```

### 14.3 Merge 卡住或积压

```sql
-- 查看当前 merge 操作
SELECT * FROM system.merges;

-- 查看 merge 积压情况
SELECT
    table,
    COUNT(*) AS part_count,
    SUM(rows) AS total_rows,
    SUM(data_compressed_bytes) AS compressed_bytes
FROM system.parts
WHERE active
GROUP BY table
HAVING part_count > 100;  -- 超过 100 个 part 说明积压严重

-- 优化 merge 积压
-- 1. 增大写入批量
-- 2. 减少写入频率
-- 3. 增加 background_pool_size
```

### 14.4 内存不足（OOM）

```sql
-- 查看查询级别的内存使用
SELECT
    query_id,
    formatReadableSize(memory_usage) AS mem,
    query
FROM system.processes
ORDER BY memory_usage DESC;

-- 限制查询内存
SET max_memory_usage = 5000000000;  -- 5GB

-- 限制 GROUP BY 内存
SET max_bytes_before_external_group_by = 2000000000;  -- 2GB 后写磁盘

-- 查看服务器内存
SELECT
    metric,
    formatReadableSize(value) AS val
FROM system.asynchronous_metrics
WHERE metric IN ('UncompressedCacheBytes', 'MarkCacheBytes', 'MMappedFileBytes');
```

### 14.5 磁盘空间不足

```sql
-- 查看表大小
SELECT
    database,
    table,
    formatReadableSize(SUM(data_compressed_bytes)) AS compressed_size,
    formatReadableSize(SUM(data_uncompressed_bytes)) AS uncompressed_size,
    round(SUM(data_uncompressed_bytes) / SUM(data_compressed_bytes), 2) AS compression_ratio,
    SUM(rows) AS rows
FROM system.parts
WHERE active
GROUP BY database, table
ORDER BY SUM(data_compressed_bytes) DESC
LIMIT 10;

-- 清理旧数据
ALTER TABLE user_events DROP PARTITION '202301';

-- 查看各磁盘使用
SELECT * FROM system.disks;
```

---

## 15. ClickHouse vs MySQL 对比

### 15.1 适用场景对比

| 场景 | MySQL | ClickHouse |
|------|-------|------------|
| 用户注册、登录（点查询） | ✅ 适合 | ❌ 不适合 |
| 订单增删改查（OLTP） | ✅ 适合 | ❌ 不适合 |
| 用户行为分析（PV/UV） | ❌ 慢 | ✅ 极快 |
| 实时大盘/仪表盘 | ❌ 查不动 | ✅ 秒出 |
| 日志分析 | ❌ 不适合 | ✅ 专为此设计 |
| 用户余额扣减（事务） | ✅ 适合 | ❌ 不支持 |
| 多维数据分析（OLAP） | ❌ 慢 | ✅ 极快 |
| 需要 UPDATE/DELETE | ✅ 即时生效 | ⚠️ 异步mutation |

### 15.2 SQL 语法差异速查

| 功能 | MySQL | ClickHouse |
|------|-------|------------|
| 创建表 | `CREATE TABLE ... ENGINE=InnoDB` | `CREATE TABLE ... ENGINE=MergeTree()` |
| 主键唯一 | ✅ 保证唯一 | ❌ 不保证 |
| ORDER BY 语法 | 查询时排序 | 表定义 + 查询排序 |
| UPDATE | `UPDATE ... SET ... WHERE` | `ALTER TABLE ... UPDATE ... WHERE`（异步） |
| DELETE | `DELETE FROM ... WHERE` | `ALTER TABLE ... DELETE WHERE`（异步） |
| 自动过期 | 需手动清理 | `TTL` 自动过期 |
| LIMIT BY | 不支持 | ✅ 支持 |
| ARRAY JOIN | 不支持 | ✅ 原生支持 |
| 物化视图 | 手动维护 | ✅ 自动同步 |
| REPLACE INTO | ✅ | ❌ 用 ReplacingMergeTree |
| INSERT ON DUPLICATE | ✅ | ❌ 用 ReplacingMergeTree |
| 事务 | ✅ ACID | ❌ 批量追加为主 |

### 15.3 从 MySQL 迁移数据到 ClickHouse

```sql
-- 方式一：通过 MySQL 表引擎直接读 MySQL
CREATE TABLE mysql_users
ENGINE = MySQL('mysql_host:3306', 'dbname', 'users', 'root', 'password');

INSERT INTO clickhouse_users SELECT * FROM mysql_users;

-- 方式二：clickhouse-client 管道
mysql -h mysql_host -u root -p'password' -D dbname \
  -e "SELECT * FROM users" \
  | clickhouse-client --query "INSERT INTO clickhouse_users FORMAT TabSeparated"

-- 方式三：使用外部工具 DataX / Flink CDC 做增量同步
```

### 15.4 典型架构：MySQL + ClickHouse 双写

```
┌──────────┐
│ 应用服务  │
└────┬─────┘
     │ 写入
     ├──────────► MySQL（OLTP：存用户、订单）
     │
     └──────────► ClickHouse（OLAP：存行为日志、聚合报表）

┌──────────┐       ┌────────────┐
│  MySQL   │──同步─►│ ClickHouse │（CDC / 定时同步）
└──────────┘       └────────────┘

应用查用户信息 → MySQL
应用查报表分析 → ClickHouse
```

---

## 速查卡片

### SQL 执行顺序

```
FROM → WHERE → PREWHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT
```

**ClickHouse 特有：PREWHERE** 在 WHERE 之前执行，先在少量列上过滤，减少后续读取。

### 常用函数

```sql
-- 时间
now()                                    -- 当前时间
today()                                  -- 今天日期
toYYYYMM(now())                          -- 202406
toStartOfHour(now())                     -- 对齐到小时
formatDateTime(now(), '%Y-%m-%d %H:%M') -- 格式化

-- 字符串
concat('Hello', ' ', 'World')            -- Hello World
substring('Hello', 1, 2)                 -- He
length('中文')                           -- 字节数或字符数
splitByString(',', 'a,b,c')             -- ['a','b','c']（数组）

-- 数组
arrayJoin(tags)                          -- 数组展开为行
arrayElement(arr, 1)                     -- 取第一个元素

-- 聚合
uniq(user_id)                            -- 近似去重（快）
uniqExact(user_id)                       -- 精确去重
quantile(0.95)(duration)                 -- p95 分位数
topK(10)(event_type)                     -- TopN

-- 条件
if(duration > 1000, '慢', '快')
multiIf(score >= 90, 'A', score >= 60, 'B', 'C')
```

### 新手常见错误 Top 5

| # | 错误 | 正确做法 |
|---|------|---------|
| 1 | 单行逐条 INSERT | 批量 INSERT，每批 1000+ 行 |
| 2 | 频繁 UPDATE/DELETE | 用 ReplacingMergeTree + 上报端去重 |
| 3 | 把 ClickHouse 当 MySQL 用 | ClickHouse 是 OLAP，不是 OLTP |
| 4 | ORDER BY 设为主键但不用于查询 | ORDER BY 应该是最常用的查询列 |
| 5 | 按秒/分钟分区 | 按天或按月分区，单分区数据量 1~10GB |

---

> **ClickHouse 是分析型利器，不是 MySQL 的替代品。OLTP 用 MySQL，OLAP 用 ClickHouse，各司其职。**
