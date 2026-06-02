# MySQL 速查手册

> 一份通俗易懂的 MySQL 文档，涵盖日常开发中最常用的操作和概念，适合快速查阅和上手。

---

## 目录

- [1. 基础概念](#1-基础概念)
- [2. 安装与连接](#2-安装与连接)
- [3. 数据库操作](#3-数据库操作)
- [4. 表操作](#4-表操作)
- [5. 数据类型](#5-数据类型)
- [6. 增删改查 (CRUD)](#6-增删改查-crud)
- [7. 查询进阶](#7-查询进阶)
- [8. 索引](#8-索引)
- [9. 事务与锁](#9-事务与锁)
  - [9.4 锁的类型全景](#94-锁的类型全景)
  - [9.5 场景实战（秒杀/余额/间隙锁/读写互斥/死锁复现/行锁升级表锁）](#95-场景实战)
  - [9.6 锁监控与排查](#96-锁监控与排查)
  - [9.7 乐观锁 vs 悲观锁](#97-乐观锁-vs-悲观锁)
  - [9.8 锁的常见误区与最佳实践](#98-锁的常见误区与最佳实践)
- [10. 视图、存储过程与触发器](#10-视图存储过程与触发器)
- [11. 用户权限管理](#11-用户权限管理)
- [12. 备份与恢复](#12-备份与恢复)
- [13. 性能优化](#13-性能优化)
- [14. 常见问题排查](#14-常见问题排查)
- [15. 系统数据库](#15-系统数据库)
  - [15.1 mysql — 账号权限](#151-mysql--账号权限)
  - [15.2 information_schema — 元数据](#152-information_schema--元数据)
  - [15.3 performance_schema — 性能监控](#153-performance_schema--性能监控)
  - [15.4 sys — 运维诊断](#154-sys--运维诊断)
  - [15.5 四库关系图谱](#155-四库关系图谱)

---

## 1. 基础概念

### 1.1 什么是 MySQL？

MySQL 是一个**关系型数据库管理系统**（RDBMS）。你可以把它理解为一个"超级 Excel"：

- **数据库（Database）** = 一个 Excel 文件
- **表（Table）** = 文件里的一个 Sheet
- **行（Row）** = Sheet 里的一行数据
- **列（Column）** = Sheet 里的一列

### 1.2 核心术语

| 术语 | 说明 | 类比 |
|------|------|------|
| 数据库 Database | 存放表的容器 | 文件夹 |
| 表 Table | 存储数据的结构 | Excel 的 Sheet |
| 字段 Column | 表的一列，定义数据类型 | Sheet 的表头 |
| 记录 Row | 表的一行数据 | Sheet 的一行 |
| 主键 Primary Key | 唯一标识一条记录 | 身份证号 |
| 外键 Foreign Key | 关联另一张表的主键 | 引用关系 |
| 索引 Index | 加速查询的数据结构 | 书的目录 |
| SQL | 操作数据库的语言 | 你跟数据库说的话 |

---

## 2. 安装与连接

### macOS

```bash
brew install mysql
brew services start mysql
```

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install mysql-server
sudo systemctl start mysql
```

### 连接数据库

```bash
# 终端连接
mysql -u root -p

# 连接远程数据库
mysql -h 192.168.1.100 -u root -p -P 3306
```

### 常用客户端工具

- **命令行**：`mysql` CLI（自带）
- **图形化**：DBeaver（免费）、Navicat（收费）、TablePlus（macOS）
- **VS Code 插件**：MySQL 扩展

---

## 3. 数据库操作

```sql
-- 查看所有数据库
SHOW DATABASES;

-- 创建数据库（指定字符集）
CREATE DATABASE shop CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 查看创建语句
SHOW CREATE DATABASE shop;

-- 切换数据库
USE shop;

-- 查看当前使用的数据库
SELECT DATABASE();

-- 删除数据库（危险操作！）
DROP DATABASE shop;
```

> **注意**：`utf8mb4` 是真正的 UTF-8，支持 emoji。不要用 `utf8`（它只支持 3 字节，存不了 emoji）。

---

## 4. 表操作

### 4.1 创建表

```sql
CREATE TABLE users (
    id          INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID',
    username    VARCHAR(50)  NOT NULL UNIQUE  COMMENT '用户名',
    email       VARCHAR(100) NOT NULL         COMMENT '邮箱',
    password    VARCHAR(255) NOT NULL         COMMENT '密码',
    age         TINYINT      DEFAULT 0       COMMENT '年龄',
    balance     DECIMAL(10,2) DEFAULT 0.00   COMMENT '余额',
    is_active   TINYINT(1)   DEFAULT 1       COMMENT '是否激活 1=是 0=否',
    created_at  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';
```

### 4.2 查看表

```sql
-- 查看所有表
SHOW TABLES;

-- 查看表结构
DESC users;
-- 或
DESCRIBE users;

-- 查看建表语句
SHOW CREATE TABLE users;

-- 查看表的所有列信息
SHOW FULL COLUMNS FROM users;
```

### 4.3 修改表（ALTER）

```sql
-- 添加列
ALTER TABLE users ADD COLUMN phone VARCHAR(20) AFTER email;

-- 修改列类型
ALTER TABLE users MODIFY COLUMN age SMALLINT;

-- 重命名列
ALTER TABLE users CHANGE COLUMN phone mobile VARCHAR(20);

-- 删除列
ALTER TABLE users DROP COLUMN mobile;

-- 添加索引
ALTER TABLE users ADD INDEX idx_email (email);

-- 重命名表
RENAME TABLE users TO accounts;
-- 或
ALTER TABLE users RENAME TO accounts;
```

### 4.4 删除表

```sql
-- 删除表（不可恢复！）
DROP TABLE users;

-- 如果存在才删除（推荐）
DROP TABLE IF EXISTS users;

-- 清空表数据，保留表结构
TRUNCATE TABLE users;

-- TRUNCATE vs DELETE 区别：
-- TRUNCATE: 快，重置自增ID，不可回滚（DDL）
-- DELETE:   慢，逐行删除，可回滚（DML）
```

---

## 5. 数据类型

### 5.1 整数类型

| 类型 | 字节 | 有符号范围 | 无符号范围 | 常用场景 |
|------|------|-----------|-----------|---------|
| TINYINT | 1 | -128 ~ 127 | 0 ~ 255 | 状态标识、年龄 |
| SMALLINT | 2 | -32768 ~ 32767 | 0 ~ 65535 | 小数值 |
| INT | 4 | -21亿 ~ 21亿 | 0 ~ 42亿 | 主键ID、数量 |
| BIGINT | 8 | 很大 | 更大 | 超大ID、时间戳 |

```sql
-- 使用示例
age TINYINT UNSIGNED           -- 年龄 0-255
status TINYINT DEFAULT 0       -- 状态 0-127
id BIGINT UNSIGNED AUTO_INCREMENT -- 大表主键
```

### 5.2 浮点数与定点数

```sql
-- FLOAT/DOUBLE: 近似值，有精度问题
price FLOAT           -- 不要存金额！

-- DECIMAL(M, D): 精确值，M=总位数, D=小数位
balance DECIMAL(10, 2)  -- 最大 99999999.99，适合金额
```

### 5.3 字符串类型

| 类型 | 最大长度 | 说明 |
|------|---------|------|
| CHAR(N) | 255 | 定长，浪费空间但快，适合固定长度 |
| VARCHAR(N) | 65535 | 变长，省空间，适合可变长度 |
| TEXT | 65535 | 长文本 |
| LONGTEXT | 4GB | 超长文本 |

```sql
-- 使用建议
CHAR(2)        -- 省份缩写、性别（定长场景）
VARCHAR(50)    -- 用户名、邮箱（变长场景）
VARCHAR(255)   -- URL、标题
TEXT           -- 文章内容、评论
```

### 5.4 日期时间类型

| 类型 | 格式 | 范围 | 用途 |
|------|------|------|------|
| DATE | YYYY-MM-DD | 1000-01-01 ~ 9999-12-31 | 生日、日期 |
| TIME | HH:MM:SS | - | 时长 |
| DATETIME | YYYY-MM-DD HH:MM:SS | 1000 ~ 9999 | 日期+时间 |
| TIMESTAMP | YYYY-MM-DD HH:MM:SS | 1970 ~ 2038 | 自动更新 |

```sql
-- 推荐做法
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP          -- 创建时自动填
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP  -- 更新时自动改
```

### 5.5 其他类型

```sql
-- 布尔值（实际是 TINYINT(1)，0=false, 非0=true）
is_deleted TINYINT(1) DEFAULT 0

-- JSON（MySQL 5.7+）
extra_info JSON

-- 枚举
gender ENUM('male', 'female', 'other')

-- 二进制
avatar BLOB
```

---

## 6. 增删改查 (CRUD)

### 6.1 插入数据 (INSERT)

```sql
-- 插入单行（完整字段）
INSERT INTO users (username, email, password, age)
VALUES ('zhangsan', 'zhangsan@example.com', '123456', 25);

-- 插入单行（自增字段可省略）
INSERT INTO users (username, email, password)
VALUES ('lisi', 'lisi@example.com', '123456');

-- 批量插入（效率高）
INSERT INTO users (username, email, password) VALUES
    ('user1', 'u1@test.com', 'pwd1'),
    ('user2', 'u2@test.com', 'pwd2'),
    ('user3', 'u3@test.com', 'pwd3');

-- 从查询结果插入
INSERT INTO users_backup SELECT * FROM users WHERE created_at < '2024-01-01';

-- 存在则更新，不存在则插入（常用！）
INSERT INTO users (id, username, email) VALUES (1, 'zhangsan', 'new@test.com')
ON DUPLICATE KEY UPDATE email = VALUES(email), updated_at = NOW();

-- 批量"存在更新，不存在插入"
INSERT INTO users (id, username, email) VALUES
    (1, 'user1', 'e1@test.com'),
    (2, 'user2', 'e2@test.com')
ON DUPLICATE KEY UPDATE email = VALUES(email);
```

### 6.2 查询数据 (SELECT)

```sql
-- 查询所有列（生产环境慎用）
SELECT * FROM users;

-- 查询指定列
SELECT id, username, email FROM users;

-- 去重
SELECT DISTINCT age FROM users;
```

### 6.3 条件查询 (WHERE)

```sql
-- 比较运算符
SELECT * FROM users WHERE age > 18;
SELECT * FROM users WHERE age BETWEEN 18 AND 30;
SELECT * FROM users WHERE username = 'zhangsan';

-- NULL 的判断（不能用 = NULL）
SELECT * FROM users WHERE email IS NULL;
SELECT * FROM users WHERE email IS NOT NULL;

-- IN / NOT IN
SELECT * FROM users WHERE age IN (18, 20, 25);
SELECT * FROM users WHERE id IN (1, 2, 3);

-- LIKE 模糊匹配（% 匹配任意字符，_ 匹配一个字符）
SELECT * FROM users WHERE username LIKE 'zhang%';   -- 以 zhang 开头
SELECT * FROM users WHERE email LIKE '%@gmail.com';  -- gmail 邮箱
SELECT * FROM users WHERE username LIKE '_hang%';    -- 第二个字符是 h

-- AND / OR
SELECT * FROM users WHERE age > 18 AND is_active = 1;
SELECT * FROM users WHERE age < 18 OR age > 60;

-- 注意 AND 优先级高于 OR，用括号明确意图！
SELECT * FROM users WHERE (age = 18 OR age = 20) AND is_active = 1;
```

### 6.4 更新数据 (UPDATE)

```sql
-- 更新单列
UPDATE users SET age = 26 WHERE id = 1;

-- 更新多列
UPDATE users SET age = 27, email = 'new@test.com' WHERE id = 1;

-- 批量更新
UPDATE users SET is_active = 0 WHERE last_login_at < '2023-01-01';

-- 🚨 危险：不带 WHERE 会更新全表！
-- UPDATE users SET age = 0;  -- 千万别这样！

-- 安全做法：先用 SELECT 确认
-- SELECT id FROM users WHERE age < 0;  -- 确认范围
-- UPDATE users SET age = 0 WHERE age < 0;
```

### 6.5 删除数据 (DELETE)

```sql
-- 删除指定行
DELETE FROM users WHERE id = 1;

-- 批量删除
DELETE FROM users WHERE is_active = 0 AND created_at < '2023-01-01';

-- 🚨 危险：不带 WHERE 会删除全表！
-- DELETE FROM users;

-- 软删除（推荐，数据可恢复）
UPDATE users SET is_deleted = 1, deleted_at = NOW() WHERE id = 1;

-- 查询时过滤软删除
SELECT * FROM users WHERE is_deleted = 0;
```

---

## 7. 查询进阶

### 7.1 排序 (ORDER BY)

```sql
-- 升序（默认）
SELECT * FROM users ORDER BY age ASC;

-- 降序
SELECT * FROM users ORDER BY created_at DESC;

-- 多字段排序：先按年龄降序，年龄相同按创建时间升序
SELECT * FROM users ORDER BY age DESC, created_at ASC;
```

### 7.2 分页 (LIMIT)

```sql
-- 前 10 条
SELECT * FROM users LIMIT 10;

-- 跳过 10 条，取 10 条（第 2 页）
SELECT * FROM users LIMIT 10, 10;
-- 或（推荐写法）
SELECT * FROM users LIMIT 10 OFFSET 10;

-- 第 N 页：LIMIT (page-1)*pageSize, pageSize
-- 第 3 页，每页 20 条
SELECT * FROM users LIMIT 40, 20;
```

### 7.3 聚合函数

```sql
-- 计数
SELECT COUNT(*) FROM users;                -- 总记录数
SELECT COUNT(email) FROM users;            -- email 不为 NULL 的数量
SELECT COUNT(DISTINCT age) FROM users;     -- 不重复年龄数

-- 求和
SELECT SUM(balance) FROM users WHERE is_active = 1;

-- 平均值
SELECT AVG(age) FROM users;

-- 最大值 / 最小值
SELECT MAX(balance) FROM users;
SELECT MIN(age) FROM users;
```

### 7.4 分组 (GROUP BY)

```sql
-- 按年龄分组，统计各年龄人数
SELECT age, COUNT(*) AS cnt
FROM users
GROUP BY age;

-- 分组后过滤（WHERE 在分组前，HAVING 在分组后）
SELECT age, COUNT(*) AS cnt
FROM users
WHERE is_active = 1          -- 分组前：只统计活跃用户
GROUP BY age
HAVING cnt > 5               -- 分组后：只要人数 > 5 的
ORDER BY cnt DESC;

-- WHERE vs HAVING：
-- WHERE: 过滤原始行（分组前），不能用聚合函数
-- HAVING: 过滤分组结果（分组后），能用聚合函数
```

### 7.5 连接查询 (JOIN)

**这是 MySQL 最核心、最常用的高级功能。**

```sql
-- 准备示例数据
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    amount DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============ JOIN 类型速查 ============

-- 1. INNER JOIN（交集，最常用）
-- 只返回两表都有匹配的行
SELECT u.username, o.amount, o.created_at
FROM users u
INNER JOIN orders o ON u.id = o.user_id;

-- 2. LEFT JOIN（左表全保留）
-- 左表所有行都返回，右表没匹配就填 NULL
-- 经典用法：找出没下过单的用户
SELECT u.username, o.id AS order_id
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE o.id IS NULL;  -- 没有订单的用户

-- 3. RIGHT JOIN（右表全保留，很少用）
-- 用 LEFT JOIN 改写即可

-- 4. FULL OUTER JOIN（MySQL 不直接支持，用 UNION 模拟）
SELECT u.username, o.amount
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
UNION
SELECT u.username, o.amount
FROM users u
RIGHT JOIN orders o ON u.id = o.user_id;
```

**JOIN 可视化记忆：**

```
INNER JOIN:  两个圆的交集
LEFT JOIN:   左圆 + 交集
RIGHT JOIN:  右圆 + 交集
FULL JOIN:   两个圆的并集
```

### 7.6 子查询

```sql
-- WHERE 中的子查询
SELECT * FROM users
WHERE id IN (SELECT user_id FROM orders WHERE amount > 100);

-- FROM 中的子查询（派生表）
SELECT avg_amount
FROM (
    SELECT user_id, AVG(amount) AS avg_amount
    FROM orders
    GROUP BY user_id
) AS user_avg
WHERE avg_amount > 50;

-- SELECT 中的子查询
SELECT username, (
    SELECT SUM(amount) FROM orders WHERE user_id = users.id
) AS total_spent
FROM users;
```

### 7.7 UNION

```sql
-- 合并两个查询结果（自动去重）
SELECT username FROM users WHERE age < 20
UNION
SELECT username FROM users WHERE balance > 1000;

-- UNION ALL（不去重，更快）
SELECT username FROM users WHERE age < 20
UNION ALL
SELECT username FROM users WHERE balance > 1000;

-- 注意事项：
-- 1. 两个查询的列数必须相同
-- 2. 列名以第一个查询为准
-- 3. 排序放在最后一个查询后面
```

---

## 8. 索引

### 8.1 什么是索引？

索引就像**书的目录**。没有索引时，查询需要从头到尾翻遍整本书（全表扫描）。有了索引，直接翻到对应页码即可。

### 8.2 索引类型

```sql
-- 1. 主键索引（自动创建，唯一，不能为 NULL）
PRIMARY KEY (id)

-- 2. 唯一索引（值不能重复）
CREATE UNIQUE INDEX idx_email ON users(email);

-- 3. 普通索引（加速查询，值可重复）
CREATE INDEX idx_username ON users(username);
-- 或建表时指定
INDEX idx_username (username)

-- 4. 联合索引（多列组合，注意最左前缀原则！）
CREATE INDEX idx_age_city ON users(age, city);
-- 这个索引对以下查询有效：
-- WHERE age = 18                     ✅ 用到 age
-- WHERE age = 18 AND city = '北京'    ✅ 用到全部
-- WHERE city = '北京'                 ❌ 用不到！（不满足最左前缀）

-- 5. 全文索引（文本搜索，MyISAM 或 InnoDB 5.6+）
CREATE FULLTEXT INDEX idx_content ON articles(title, body);
SELECT * FROM articles WHERE MATCH(title, body) AGAINST('MySQL 教程');
```

### 8.3 查看和管理索引

```sql
-- 查看表的索引
SHOW INDEX FROM users;

-- 删除索引
DROP INDEX idx_email ON users;
ALTER TABLE users DROP INDEX idx_email;

-- 删除主键（自增列不能直接删，要先去掉 AUTO_INCREMENT）
ALTER TABLE users DROP PRIMARY KEY;
```

### 8.4 索引使用建议

**什么时候加索引？**

- WHERE 条件经常用到的列
- ORDER BY 的列
- JOIN 的关联列
- 数据量大的表（小表全表扫描反而更快）

**什么时候不加索引？**

- 表数据很少（几百行）
- 频繁更新的列（维护索引有代价）
- 区分度低的列，如性别（只有男/女，加了也没用）
- WHERE 条件中从来不用的列

```sql
-- 查看索引是否被使用
EXPLAIN SELECT * FROM users WHERE email = 'test@test.com';
```

### 8.5 用 EXPLAIN 看查询计划

```sql
EXPLAIN SELECT * FROM users WHERE email = 'zhangsan@test.com';
```

关键字段：

| 字段 | 含义 | 好 | 差 |
|------|------|---|----|
| type | 访问类型 | const, ref, range | ALL（全表扫描） |
| key | 使用的索引 | 有值 | NULL（没用到索引） |
| rows | 扫描行数 | 越少越好 | 越大越差 |
| Extra | 额外信息 | Using index（覆盖索引） | Using filesort, Using temporary |

---

## 9. 事务与锁

### 9.1 什么是事务？

事务是一组 SQL 操作，要么**全部成功**，要么**全部失败**。经典例子：转账。

```sql
-- 转账：A 扣 100，B 加 100，必须同时成功或同时失败
START TRANSACTION;

UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;

-- 如果都成功
COMMIT;

-- 如果出问题
-- ROLLBACK;
```

### 9.2 事务四大特性 (ACID)

| 特性 | 说明 | 实现机制 |
|------|------|---------|
| 原子性 Atomicity | 要么全做，要么全不做 | undo log（回滚日志） |
| 一致性 Consistency | 事务前后数据一致 | 其他三个特性共同保证 |
| 隔离性 Isolation | 多个事务互不干扰 | **锁 + MVCC**（多版本并发控制） |
| 持久性 Durability | 提交后永久保存 | redo log（重做日志） |

### 9.3 事务隔离级别

```sql
-- 查看当前隔离级别
SELECT @@transaction_isolation;  -- MySQL 8.0+
-- SELECT @@tx_isolation;         -- MySQL 5.7

-- 设置隔离级别
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ;  -- MySQL 默认
```

| 级别 | 脏读 | 不可重复读 | 幻读 | 说明 |
|------|------|-----------|------|------|
| READ UNCOMMITTED | ✅ | ✅ | ✅ | 最低，基本不用 |
| READ COMMITTED | ❌ | ✅ | ✅ | 每次读已提交数据 |
| REPEATABLE READ | ❌ | ❌ | ❌ | **MySQL 默认**（通过 MVCC + 间隙锁解决幻读） |
| SERIALIZABLE | ❌ | ❌ | ❌ | 最高，串行执行 |

#### 三种并发问题的具体表现

**准备测试表：**

```sql
CREATE TABLE products (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    stock INT
);
INSERT INTO products VALUES (1, 'iPhone', 100);
```

**脏读（Dirty Read）—— READ UNCOMMITTED 下发生：**

```sql
-- 时间线 ────────────────────────────────────────────
-- 事务A（READ UNCOMMITTED）         事务B
-- ──────────────────────────────────────────────
BEGIN;
UPDATE products SET stock = 50 WHERE id = 1;
--                                   BEGIN;
--                                   -- 读到 stock=50（脏数据！）
--                                   SELECT stock FROM products WHERE id = 1;
ROLLBACK;  -- 事务A 回滚了！
--                                   -- 事务B 读到的 50 是脏数据，实际是 100
```

**不可重复读（Non-Repeatable Read）—— READ COMMITTED 下发生：**

```sql
-- 事务A（READ COMMITTED）            事务B
-- ──────────────────────────────────────────────
BEGIN;
SELECT stock FROM products WHERE id = 1;
-- 结果: 100
--                                   BEGIN;
--                                   UPDATE products SET stock = 80 WHERE id = 1;
--                                   COMMIT;
SELECT stock FROM products WHERE id = 1;
-- 结果: 80（同一事务内两次读到不同结果！）
COMMIT;
```

**幻读（Phantom Read）—— READ COMMITTED 下发生，REPEATABLE READ 通过间隙锁解决：**

```sql
-- 事务A                               事务B
-- ──────────────────────────────────────────────
BEGIN;
SELECT * FROM products WHERE id BETWEEN 1 AND 10;
-- 结果: 1 条记录 (id=1)
--                                   BEGIN;
--                                   INSERT INTO products VALUES (2, 'iPad', 50);
--                                   COMMIT;
SELECT * FROM products WHERE id BETWEEN 1 AND 10;
-- READ COMMITTED: 2 条（多了一条"幻影"！）
-- REPEATABLE READ: 还是 1 条（MVCC 快照读，不会被幻读影响）
COMMIT;
```

---

### 9.4 锁的类型全景

InnoDB 的锁体系分三个维度：

```
按粒度      按模式        按算法
───────    ────────      ────────
行锁       共享锁(S)      记录锁 (Record Lock)
表锁       排他锁(X)      间隙锁 (Gap Lock)
页锁       意向锁(IS/IX)   临键锁 (Next-Key Lock)
           自增锁(AI)    插入意向锁
```

#### 9.4.1 共享锁（S 锁）和排他锁（X 锁）

这是最基本的两种锁模式。**兼容矩阵**：

| | S 锁 | X 锁 |
|------|------|------|
| **S 锁** | ✅ 兼容 | ❌ 冲突 |
| **X 锁** | ❌ 冲突 | ❌ 冲突 |

```sql
-- 共享锁（S 锁）：其他人可读不可写
SELECT * FROM users WHERE id = 1 FOR SHARE;  -- MySQL 8.0+
-- SELECT * FROM users WHERE id = 1 LOCK IN SHARE MODE;  -- MySQL 5.7

-- 排他锁（X 锁）：其他人不可读不可写
SELECT * FROM users WHERE id = 1 FOR UPDATE;
```

**记住两条核心规则：**
1. **InnoDB 默认行锁**，MyISAM 默认表锁
2. **WHERE 条件用索引**才是行锁，否则退化为表锁

#### 9.4.2 记录锁 / 间隙锁 / 临键锁

这是 InnoDB 在 **REPEATABLE READ** 隔离级别下默认使用的三种行锁算法。

```
表数据：[ 1 ] [ 5 ] [ 10 ] [ 15 ]

间隙：  (-∞,1) (1,5) (5,10) (10,15) (15,+∞)
                     ↑
              这些"没有数据"的区间就是间隙
```

| 锁类型 | 锁定范围 | 解决的问题 |
|--------|---------|-----------|
| 记录锁 (Record Lock) | 锁住索引上的一条记录 | 防止其他事务 UPDATE/DELETE 该行 |
| 间隙锁 (Gap Lock) | 锁住索引记录之间的间隙 | **防止幻读**（其他事务不能在间隙中 INSERT） |
| 临键锁 (Next-Key Lock) | 记录锁 + 前面的间隙锁 | 防止幻读 + 防止修改 |

```sql
-- 假设 products 表有 id: 1, 5, 10, 15

-- 记录锁：只锁 id=5 这一行
SELECT * FROM products WHERE id = 5 FOR UPDATE;
-- 锁定: [5]

-- 间隙锁：锁住 (5,10) 这个区间（5和10之间的间隙）
SELECT * FROM products WHERE id = 8 FOR UPDATE;
-- 8 不存在，锁住区间 (5,10)
-- 其他事务不能 INSERT id=6,7,8,9

-- 临键锁：锁住 (5,10] 区间 + [10,15) 区间
SELECT * FROM products WHERE id BETWEEN 7 AND 12 FOR UPDATE;
-- 锁住: (5,10] + [10,15)  ← 这里有 id=10 的记录锁，以及两边的间隙锁
-- 其他事务不能 INSERT id=6,7,8,9,11,12,13,14
-- 其他事务不能 UPDATE/DELETE id=10
```

#### 9.4.3 意向锁（Intention Lock）

意向锁是**表级锁**，InnoDB 自动加，不需要手动操作。作用是快速判断表中是否有行锁。

```
IS 锁（意向共享锁）：事务想要在某些行上加 S 锁时，先在表上加 IS
IX 锁（意向排他锁）：事务想要在某些行上加 X 锁时，先在表上加 IX
```

```sql
-- 当你执行 SELECT ... FOR UPDATE 时，InnoDB 自动做两件事：
-- 1. 在表上加 IX 锁（意向排他锁）
-- 2. 在匹配的行上加 X 锁（排他行锁）

-- 当你执行 LOCK TABLES products WRITE 时，MySQL 检查表上是否有 IX/IS：
-- 如果有 IX  → 说明有行锁在 → 表锁等待
-- 如果没有   → 直接加表锁
```

#### 9.4.4 锁类型速查表

| 锁类型 | 级别 | 加锁方式 | 特点 |
|--------|------|---------|------|
| 共享锁 (S) | 行 | `SELECT ... FOR SHARE` | 读锁，允许其他 S 锁 |
| 排他锁 (X) | 行 | `SELECT ... FOR UPDATE`、`UPDATE`、`DELETE`、`INSERT` | 写锁，不允许任何其他锁 |
| 意向共享锁 (IS) | 表 | InnoDB 自动加 | 表级标记 |
| 意向排他锁 (IX) | 表 | InnoDB 自动加 | 表级标记 |
| 记录锁 | 行 | 等值查询命中索引时 | 锁住一条记录 |
| 间隙锁 | 区间 | 范围查询或等值查询未命中时 | 锁住间隙，防 INSERT |
| 临键锁 | 行+间隙 | RR 隔离级别默认 | 记录锁 + 前间隙锁 |
| 自增锁 | 表 | `AUTO_INCREMENT` 插入时 | 自增 ID 不重复 |
| 元数据锁 (MDL) | 表 | DDL 操作自动加 | 防止 DDL 和 DML 冲突 |

---

### 9.5 场景实战

#### 场景 1：秒杀/抢单 — SELECT FOR UPDATE 防止超卖

**需求**：秒杀场景，100 件库存，1000 人同时抢，库存不能扣成负数。

**错误写法（会超卖）：**

```sql
-- ❌ 错误：先读后写，并发时两个事务可能读到同一个 stock 值
BEGIN;
SELECT stock FROM products WHERE id = 1;  -- 两个事务同时读到 stock=100
-- 业务层判断 stock > 0
UPDATE products SET stock = stock - 1 WHERE id = 1;  -- 两个都执行了！
COMMIT;
-- 结果：只剩 1 件的商品可能被 2 个事务各-1 → 变成 -1！
```

**正确写法（行锁串行化）：**

```sql
-- ✅ 正确：SELECT ... FOR UPDATE 加排他锁
BEGIN;

-- 关键：FOR UPDATE 对 id=1 这一行加 X 锁
-- 事务B 执行到这里时会阻塞，等事务A 提交后才能读取
SELECT stock FROM products WHERE id = 1 FOR UPDATE;
-- 读到 stock=100（保证是最新值，且此行被锁住）

-- 业务层判断
IF stock > 0 THEN
    UPDATE products SET stock = stock - 1 WHERE id = 1;
    -- 创建订单...
END IF;

COMMIT;
-- 事务B 现在才能执行 SELECT ... FOR UPDATE，读到 stock=99
```

**执行过程拆解：**

```
时间线 ────────────────────────────────────────
事务A                                  事务B
──────────────────────────────────────────────
BEGIN;
SELECT stock FROM products
  WHERE id=1 FOR UPDATE;
-- ✓ 读到 stock=100
-- ⚡ id=1 被 X 锁锁定
                                        BEGIN;
                                        SELECT stock FROM products
                                          WHERE id=1 FOR UPDATE;
                                        -- ⏳ 阻塞！等待事务A 释放 X 锁
UPDATE products
  SET stock = 99 WHERE id=1;
-- ✓ 更新成功
COMMIT;
-- ⚡ 释放 X 锁
                                        -- ▶ 事务B 现在获取 X 锁
                                        -- 读到 stock=99
                                        UPDATE products
                                          SET stock=98 WHERE id=1;
                                        COMMIT;
```

#### 场景 2：用户余额扣减 — 共享锁做双重保险

**需求**：用户下单时扣余额，要求余额扣减和订单创建在同一事务中。使用 `FOR UPDATE` 防止并发扣款导致余额为负。

```sql
-- 完整的"下单+扣余额"事务
BEGIN;

-- 1. 对用户余额行加 X 锁（FOR UPDATE）
SELECT balance FROM user_wallet WHERE user_id = 100 FOR UPDATE;
-- 读到 balance=500

-- 2. 业务判断
IF balance >= 300 THEN  -- 订单金额 300

    -- 3. 扣余额
    UPDATE user_wallet SET balance = balance - 300 WHERE user_id = 100;

    -- 4. 创建订单
    INSERT INTO orders (user_id, amount, status) VALUES (100, 300, 'paid');

    -- 5. 记录流水
    INSERT INTO wallet_logs (user_id, amount, type, created_at)
    VALUES (100, -300, 'order_pay', NOW());

    COMMIT;
ELSE
    ROLLBACK;
END IF;
```

**为什么不用 UPDATE 直接判断：**

```sql
-- ❌ 不行：UPDATE 本身加 X 锁，但你无法获取"更新前的旧值"用于判断
UPDATE user_wallet SET balance = balance - 300
WHERE user_id = 100 AND balance >= 300;

-- 问题是：如果余额 200，UPDATE 影响 0 行，你只知道"没扣成功"
-- 但不知道是因为"余额不足"还是"用户不存在"
-- 而且此时没有事务保护，其他操作无法和这个扣款原子化

-- ✅ 正确：FOR UPDATE 读 + 业务判断 + UPDATE 写，全部在事务中
```

#### 场景 3：库存流水记录 — 间隙锁防止并发插入问题

**需求**：同一商品在同一秒内只能有一条库存变更流水（防止重复记录）。

```sql
-- 流水表
CREATE TABLE inventory_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    change_time DATETIME NOT NULL,
    change_type VARCHAR(20),
    quantity INT,
    UNIQUE KEY uk_product_time (product_id, change_time)
);

-- 事务A：为商品 100 记录"出库"流水
BEGIN;
-- 插入时间精确到秒
INSERT INTO inventory_logs (product_id, change_time, change_type, quantity)
VALUES (100, '2024-06-01 10:30:25', 'outbound', -5);
-- ✓ 成功

-- 事务B：同一秒内也尝试插入
BEGIN;
INSERT INTO inventory_logs (product_id, change_time, change_type, quantity)
VALUES (100, '2024-06-01 10:30:25', 'outbound', -5);
-- ⏳ 阻塞！

-- 阻塞原因：
-- 事务A 插入 product_id=100, change_time='2024-06-01 10:30:25'
-- InnoDB 在该索引记录上加 Next-Key Lock
-- 事务B 要插入相同唯一键值 → 被间隙锁阻塞

-- 事务A COMMIT 后：
-- 事务B 报错：Duplicate entry '100-2024-06-01 10:30:25' for key 'uk_product_time'
-- 这正是我们想要的：同一秒不允许重复流水
```

#### 场景 4：读写互斥 — 防止读取到未提交的中间状态

**需求**：财务对账时，需要读取一个"一致性快照"，不能读到其他事务修改了一半的数据。

```sql
-- ===== 读事务（对账）=====
BEGIN;
-- FOR SHARE：加共享锁，阻止其他事务修改这些行
-- 但对账场景通常不需要锁，用 REPEATABLE READ + 快照读就够了
SELECT SUM(amount) FROM orders
WHERE created_at BETWEEN '2024-06-01' AND '2024-06-30'
FOR SHARE;
-- 此时这些订单行都被加了 S 锁
-- 其他事务仍然可以读（S 锁和 S 锁兼容）
-- 但不能改（S 锁和 X 锁冲突）

-- 处理对账逻辑...

COMMIT;

-- ===== 写事务（退款）=====
BEGIN;
UPDATE orders SET status='refunded' WHERE id = 12345;
-- ⏳ 如果 id=12345 在对账范围内，被对账事务加了 S 锁，这里阻塞
-- 等对账事务 COMMIT 后才能执行
COMMIT;
```

#### 场景 5：死锁的产生、复现与解决

**准备数据：**

```sql
CREATE TABLE accounts (
    id INT PRIMARY KEY,
    user_name VARCHAR(50),
    balance DECIMAL(10,2)
);
INSERT INTO accounts VALUES (1, '张三', 1000), (2, '李四', 1000);
```

**死锁复现（在两个终端同时执行）：**

```sql
-- 终端A                              终端B
-- ──────────────────────────────────────────────
BEGIN;
UPDATE accounts SET balance = 900
  WHERE id = 1;
-- ✓ 锁住 id=1（X 锁）
                                      BEGIN;
                                      UPDATE accounts SET balance = 800
                                        WHERE id = 2;
                                      -- ✓ 锁住 id=2（X 锁）

UPDATE accounts SET balance = 1100
  WHERE id = 2;
-- ⏳ 等待 B 释放 id=2 的 X 锁
                                      UPDATE accounts SET balance = 1200
                                        WHERE id = 1;
                                      -- ⏳ 等待 A 释放 id=1 的 X 锁

-- 💀 死锁！A 等 B 的 id=2，B 等 A 的 id=1
-- MySQL 自动检测到死锁，回滚其中一个事务
-- ERROR 1213: Deadlock found when trying to get lock; try restarting transaction
```

**为什么会产生死锁：**

```
事务A: 持有 id=1(X), 等待 id=2(X)
事务B: 持有 id=2(X), 等待 id=1(X)
         ↓
    循环等待 → 死锁
```

**三种解决方案：**

```sql
-- 方案 1（推荐）：保持加锁顺序一致
-- 所有事务都先操作 id=1 再操作 id=2
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;  -- 永远先锁小的 id
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;

-- 方案 2：一次锁住所有需要的行
BEGIN;
SELECT id FROM accounts WHERE id IN (1, 2) FOR UPDATE;  -- 先锁住所有行
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;

-- 方案 3：缩短事务，减少锁持有时间
BEGIN;
-- 只做必要的操作
UPDATE accounts SET balance = 900 WHERE id = 1;
COMMIT;  -- 尽快提交释放锁
```

#### 场景 6：WHERE 条件没走索引导致行锁升级为表锁

**这是最常见的性能问题！**

```sql
-- 准备（name 列没有索引）
CREATE TABLE orders (
    id INT PRIMARY KEY,
    user_name VARCHAR(50),
    amount DECIMAL(10,2)
);
CREATE INDEX idx_id ON orders(id);  -- 只有主键索引
-- name 列没有索引！

-- 事务A
BEGIN;
SELECT * FROM orders WHERE user_name = '张三' FOR UPDATE;
-- ⚠️ name 没有索引 → 全表扫描 → MySQL 对所有扫描到的行加 X 锁
-- 实际效果：锁全表！

-- 事务B
BEGIN;
INSERT INTO orders VALUES (10, '王五', 500);
-- ⏳ 阻塞！即使和"张三"无关，也被表级锁阻塞
```

```sql
-- ✅ 解决：给 WHERE 条件列加索引
CREATE INDEX idx_user_name ON orders(user_name);

-- 事务A
BEGIN;
SELECT * FROM orders WHERE user_name = '张三' FOR UPDATE;
-- ✓ 走索引 → 只锁匹配行 → 行锁

-- 事务B
BEGIN;
INSERT INTO orders VALUES (10, '王五', 500);
-- ✓ 成功！不受事务A 影响
```

**验证是否走索引：**

```sql
EXPLAIN SELECT * FROM orders WHERE user_name = '张三' FOR UPDATE;
-- 看 key 列：有值=用了索引，NULL=没走索引（会锁全表！）
-- 看 type 列：ref/const=行锁，ALL=全表扫描=表锁
```

---

### 9.6 锁监控与排查

```sql
-- 1. 查看当前所有锁（MySQL 8.0+）
SELECT
    lock_type,           -- TABLE（表锁）/ RECORD（行锁）
    lock_mode,           -- S, X, IS, IX, AUTO_INC
    lock_status,         -- GRANTED（已获取）/ WAITING（等待中）
    lock_data,           -- 锁定的数据（行值或表名）
    object_name          -- 被锁的表
FROM performance_schema.data_locks;

-- 2. 查看锁等待关系（谁在等谁）
SELECT
    waiting_trx_id,      -- 等待的事务ID
    waiting_thread_id,   -- 等待的线程ID
    blocking_trx_id,     -- 阻塞的事务ID
    blocking_thread_id,  -- 阻塞的线程ID
    wait_age              -- 等待了多少秒
FROM performance_schema.data_lock_waits;

-- 3. 查看当前所有事务
SELECT
    trx_id,
    trx_state,           -- RUNNING, LOCK WAIT
    trx_started,         -- 事务开始时间
    trx_mysql_thread_id, -- 线程ID
    trx_query,           -- 当前执行的SQL
    trx_rows_locked,     -- 锁定的行数
    trx_rows_modified    -- 修改的行数
FROM information_schema.INNODB_TRX
WHERE trx_state = 'LOCK WAIT';

-- 4. 查看锁等待超时设置
SHOW VARIABLES LIKE 'innodb_lock_wait_timeout';
-- 默认 50 秒，等待超过这个时间自动报错回滚

-- 5. 手动终止阻塞事务
-- 先用上面的查询找到 blocking_thread_id
KILL <blocking_thread_id>;

-- 6. 查看最近一次死锁详情
SHOW ENGINE INNODB STATUS\G
-- 找到 "LATEST DETECTED DEADLOCK" 段落
-- 会详细列出死锁涉及的事务、持有的锁、等待的锁
```

---

### 9.7 乐观锁 vs 悲观锁

| | 乐观锁 | 悲观锁 |
|------|--------|--------|
| **实现方式** | 版本号/时间戳 WHERE 条件 | `SELECT ... FOR UPDATE` |
| **适用场景** | **读多写少**，冲突概率低 | **写多**，冲突概率高 |
| **性能** | 无锁等待，高并发 | 有锁等待，并发受限 |
| **失败处理** | 重试（业务层） | 等待或超时（数据库层） |

**乐观锁实现（版本号）：**

```sql
-- 建表时加 version 字段
CREATE TABLE products (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    stock INT,
    version INT DEFAULT 0   -- 版本号
);

-- 乐观锁更新
-- 每个连接都能同时执行，不会阻塞
UPDATE products
SET stock = stock - 1, version = version + 1
WHERE id = 1 AND version = 5;  -- 关键：带上旧版本号

-- 检查 affected rows：
-- affected_rows = 1 → 成功，版本号变为 6
-- affected_rows = 0 → 被别人抢先改了，重试

-- 应用层重试逻辑（Python 伪代码）
def deduct_stock(product_id, quantity):
    for _ in range(3):  # 最多重试 3 次
        product = SELECT id, stock, version FROM products WHERE id = product_id
        if product.stock < quantity:
            return "库存不足"

        affected = UPDATE products
                   SET stock = stock - quantity, version = version + 1
                   WHERE id = product_id AND version = product.version

        if affected > 0:
            return "扣减成功"
        # affected = 0 → 版本号已变，重试
    return "系统繁忙，请重试"
```

**悲观锁 vs 乐观锁选型示例：**

```python
# 场景1：秒杀（并发极高，冲突概率高）→ 悲观锁
def seckill_order(product_id, user_id):
    with transaction.atomic():
        # SELECT FOR UPDATE 排队执行，保证不超卖
        product = Product.objects.select_for_update().get(id=product_id)
        if product.stock < 1:
            raise SoldOutError()
        product.stock -= 1
        product.save()
        Order.objects.create(user_id=user_id, product_id=product_id)

# 场景2：用户修改个人资料（并发低，冲突概率低）→ 乐观锁
def update_profile(user_id, nickname, bio):
    for attempt in range(3):
        profile = UserProfile.objects.get(user_id=user_id)
        affected = UserProfile.objects.filter(
            user_id=user_id,
            version=profile.version  # 乐观锁条件
        ).update(nickname=nickname, bio=bio, version=profile.version + 1)
        if affected:
            return "修改成功"
    return "请重试"
```

---

### 9.8 锁的常见误区与最佳实践

**误区：**

| 误区 | 真相 |
|------|------|
| "InnoDB 的行锁就是锁一行" | 实际上是锁索引记录，可能锁多行（间隙锁） |
| "FOR UPDATE 只锁查询出来的行" | 如果没走索引，会锁全表 |
| "READ COMMITTED 没有间隙锁就没问题" | 但没有间隙锁 = 有幻读风险 |
| "事务越短越好" | 正确，但也要注意不要拆得太碎（影响业务原子性） |
| "死锁是 bug" | 死锁是正常现象，正确做法是**捕获重试** |

**最佳实践：**

```sql
-- 1. 事务尽量短：把耗时操作放到事务外
-- ❌ 不好
BEGIN;
UPDATE products SET stock = stock - 1 WHERE id = 1;
-- ... 发送 HTTP 请求通知仓库（耗时 2 秒）...
COMMIT;  -- 锁持有了 2 秒！

-- ✅ 好
BEGIN;
UPDATE products SET stock = stock - 1 WHERE id = 1;
COMMIT;  -- 锁只持有了几毫秒
-- 发 HTTP 请求...

-- 2. 加锁顺序一致（避免死锁）
-- 总是按 id 升序加锁: id=1 → id=2 → id=3

-- 3. 用 EXPLAIN 验证走索引
EXPLAIN SELECT * FROM orders WHERE user_id = 123 FOR UPDATE;
-- key 列必须有值！

-- 4. 应用层捕获死锁重试
DELIMITER //
CREATE PROCEDURE safe_transfer(IN from_id INT, IN to_id INT, IN amt DECIMAL)
BEGIN
    DECLARE EXIT HANDLER FOR 1213  -- 1213 是死锁错误码
    BEGIN
        ROLLBACK;
        -- 重试一次
        CALL safe_transfer(from_id, to_id, amt);
    END;

    START TRANSACTION;
    UPDATE accounts SET balance = balance - amt WHERE id = from_id;
    UPDATE accounts SET balance = balance + amt WHERE id = to_id;
    COMMIT;
END //
DELIMITER ;

-- 5. 对热数据考虑乐观锁替代悲观锁
-- 避免大量 FOR UPDATE 排队影响性能
```

---

## 10. 视图、存储过程与触发器

### 10.1 视图 (VIEW)

视图是一个**保存的查询结果**，可以当作虚拟表来查询。

```sql
-- 创建视图（封装复杂查询）
CREATE VIEW user_order_summary AS
SELECT u.id, u.username, COUNT(o.id) AS order_count, COALESCE(SUM(o.amount), 0) AS total_amount
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id;

-- 像查表一样查视图
SELECT * FROM user_order_summary WHERE order_count > 5;

-- 查看视图定义
SHOW CREATE VIEW user_order_summary;

-- 删除视图
DROP VIEW IF EXISTS user_order_summary;
```

**视图 vs 表的区别：**
- 视图不存数据，每次查询实时计算
- 视图封装复杂逻辑，简化查询
- 可以给不同用户看不同的视图（权限控制）

### 10.2 存储过程

存储过程是**保存在数据库里的一组 SQL**，可以像函数一样调用。

```sql
-- 修改分隔符（因为存储过程里有;）
DELIMITER //

CREATE PROCEDURE get_user_orders(IN uid INT)
BEGIN
    SELECT u.username, o.id AS order_id, o.amount, o.created_at
    FROM users u
    INNER JOIN orders o ON u.id = o.user_id
    WHERE u.id = uid
    ORDER BY o.created_at DESC;
END //

DELIMITER ;

-- 调用
CALL get_user_orders(1);

-- 带输出参数的存储过程
DELIMITER //

CREATE PROCEDURE get_order_count(IN uid INT, OUT cnt INT)
BEGIN
    SELECT COUNT(*) INTO cnt FROM orders WHERE user_id = uid;
END //

DELIMITER ;

-- 调用
CALL get_order_count(1, @result);
SELECT @result;

-- 删除
DROP PROCEDURE IF EXISTS get_user_orders;
```

### 10.3 触发器 (TRIGGER)

触发器是**在某事件发生时自动执行的 SQL**。

```sql
-- 插入 orders 时自动更新 users 的订单计数
CREATE TRIGGER after_order_insert
AFTER INSERT ON orders
FOR EACH ROW
BEGIN
    UPDATE users SET order_count = order_count + 1 WHERE id = NEW.user_id;
END;

-- 可用时点: BEFORE / AFTER
-- 可用事件: INSERT / UPDATE / DELETE
-- NEW: 新行（INSERT, UPDATE 中有）
-- OLD: 旧行（UPDATE, DELETE 中有）

-- 查看触发器
SHOW TRIGGERS;

-- 删除触发器
DROP TRIGGER IF EXISTS after_order_insert;
```

> **注意**：触发器会增加复杂度和调试难度，能用应用层逻辑替代就替代。

---

## 11. 用户权限管理

### 11.1 用户管理

```sql
-- 创建用户
CREATE USER 'appuser'@'localhost' IDENTIFIED BY 'SecurePass123';
CREATE USER 'appuser'@'%' IDENTIFIED BY 'SecurePass123';  -- % = 任何主机

-- 修改密码
ALTER USER 'appuser'@'localhost' IDENTIFIED BY 'NewPass456';

-- 删除用户
DROP USER 'appuser'@'localhost';

-- 查看所有用户
SELECT user, host FROM mysql.user;
```

### 11.2 权限管理

```sql
-- 授权
GRANT SELECT, INSERT, UPDATE ON shop.* TO 'appuser'@'localhost';     -- 某库所有表
GRANT ALL PRIVILEGES ON shop.* TO 'admin'@'localhost';                -- 全部权限
GRANT SELECT ON shop.users TO 'readonly'@'%';                         -- 只给某表

-- 立即生效
FLUSH PRIVILEGES;

-- 查看用户权限
SHOW GRANTS FOR 'appuser'@'localhost';

-- 撤销权限
REVOKE INSERT, UPDATE ON shop.* FROM 'appuser'@'localhost';

-- 常用权限
-- SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, ALTER, INDEX
```

---

## 12. 备份与恢复

### 12.1 备份

```bash
# 备份单个数据库
mysqldump -u root -p shop > shop_backup.sql

# 备份所有数据库
mysqldump -u root -p --all-databases > all_backup.sql

# 只备份表结构，不要数据
mysqldump -u root -p --no-data shop > shop_structure.sql

# 只备份数据，不要表结构
mysqldump -u root -p --no-create-info shop > shop_data.sql

# 备份指定表
mysqldump -u root -p shop users orders > shop_tables.sql

# 压缩备份
mysqldump -u root -p shop | gzip > shop_backup.sql.gz
```

### 12.2 恢复

```bash
# 从 SQL 文件恢复
mysql -u root -p shop < shop_backup.sql

# 从压缩文件恢复
gunzip < shop_backup.sql.gz | mysql -u root -p shop

# 恢复时指定字符集
mysql -u root -p --default-character-set=utf8mb4 shop < shop_backup.sql
```

### 12.3 使用二进制日志做时间点恢复

```sql
-- 查看 binlog 是否开启
SHOW VARIABLES LIKE 'log_bin';

-- 查看 binlog 文件列表
SHOW BINARY LOGS;

-- 查看 binlog 内容
SHOW BINLOG EVENTS IN 'binlog.000001';
```

---

## 13. 性能优化

### 13.1 查询优化清单

```sql
-- 1. SELECT 只取需要的列，避免 SELECT *

-- 2. WHERE 条件列加索引
EXPLAIN SELECT * FROM users WHERE email = 'test@test.com';  -- key 列是否有值？

-- 3. 避免在 WHERE 中对列做函数运算（会导致索引失效）
-- ❌ 差
SELECT * FROM users WHERE YEAR(created_at) = 2024;
-- ✅ 好
SELECT * FROM users WHERE created_at BETWEEN '2024-01-01' AND '2024-12-31';

-- 4. LIKE 避免前置 %（索引失效）
-- ❌ 差
SELECT * FROM users WHERE username LIKE '%zhang%';
-- ✅ 好（前缀匹配用得到索引）
SELECT * FROM users WHERE username LIKE 'zhang%';

-- 5. 大偏移量分页优化（记录上次 ID）
-- ❌ 慢（越往后越慢）
SELECT * FROM users ORDER BY id LIMIT 100000, 20;
-- ✅ 快（基于上次记录的 ID）
SELECT * FROM users WHERE id > 100000 ORDER BY id LIMIT 20;

-- 6. 用 EXISTS 代替 IN（子查询结果大时）
-- 如果子查询结果大，EXISTS 更快
SELECT * FROM users u
WHERE EXISTS (SELECT 1 FROM orders o WHERE o.user_id = u.id AND o.amount > 100);
```

### 13.2 慢查询分析

```sql
-- 查看慢查询是否开启
SHOW VARIABLES LIKE 'slow_query%';

-- 开启慢查询日志
SET GLOBAL slow_query_log = ON;
SET GLOBAL long_query_time = 1;  -- 超过 1 秒就记录

-- 查看慢查询日志位置
SHOW VARIABLES LIKE 'slow_query_log_file';
```

### 13.3 表优化

```sql
-- 查看表状态
SHOW TABLE STATUS LIKE 'users';

-- 分析表（更新索引统计信息）
ANALYZE TABLE users;

-- 优化表（整理碎片）
OPTIMIZE TABLE users;

-- 检查并修复表
CHECK TABLE users;
REPAIR TABLE users;
```

### 13.4 连接池常用配置

```ini
# my.cnf 或 my.ini
[mysqld]
# 最大连接数
max_connections = 500

# InnoDB 缓冲池（最重要的参数，设为可用内存的 50%-70%）
innodb_buffer_pool_size = 2G

# 连接超时
wait_timeout = 300
interactive_timeout = 300
```

---

## 14. 常见问题排查

### 14.1 连接数满了

```sql
-- 查看当前连接
SHOW PROCESSLIST;
-- 或
SHOW FULL PROCESSLIST;

-- 查看最大连接数
SHOW VARIABLES LIKE 'max_connections';

-- 查看当前连接数
SHOW STATUS LIKE 'Threads_connected';

-- 临时调大
SET GLOBAL max_connections = 500;

-- 杀死指定连接
KILL 123;  -- 123 是连接 ID
```

### 14.2 锁等待超时

```sql
-- 查看锁等待
-- MySQL 8.0
SELECT * FROM performance_schema.data_lock_waits;

-- 查看正在执行的事务
SELECT * FROM information_schema.INNODB_TRX;

-- 查看锁等待超时时间
SHOW VARIABLES LIKE 'innodb_lock_wait_timeout';
```

### 14.3 磁盘空间不足

```sql
-- 查看各数据库/表大小
SELECT
    table_schema AS '数据库',
    table_name AS '表名',
    ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS '大小(MB)'
FROM information_schema.tables
GROUP BY table_schema, table_name
ORDER BY SUM(data_length + index_length) DESC;

-- 查看数据库总大小
SELECT
    table_schema AS '数据库',
    ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS '总大小(MB)'
FROM information_schema.tables
GROUP BY table_schema
ORDER BY SUM(data_length + index_length) DESC;

-- 查看 binlog 占用
SHOW BINARY LOGS;
```

### 14.4 字符集乱码

```sql
-- 查看字符集配置
SHOW VARIABLES LIKE 'character_set_%';

-- 建库指定 utf8mb4
CREATE DATABASE your_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 修改现有字符集
ALTER DATABASE your_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE your_table CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

---

## 15. 系统数据库

MySQL 除了用户创建的库，还自带四个系统数据库，各司其职：

```
mysql                →  谁能进来？（账号权限配置，持久化）
information_schema   →  系统里有什么？（表结构/索引/列的元数据）
performance_schema   →  发生了什么？（实时性能指标：锁/内存/IO）
sys                  →  翻译成人话（把上面两个封装成易读视图）
```

### 15.1 mysql — 账号权限

`mysql` 库是 MySQL 的**系统核心库**，存放用户、权限、存储过程等配置，**持久化**在磁盘。修改后直接影响 MySQL 行为。

**核心表：**

| 表名 | 内容 | 重要度 |
|------|------|--------|
| **user** | 用户账号 + 全局权限 | 最重要 |
| **db** | 数据库级别的权限 | 常用 |
| **tables_priv** | 表级别的权限 | 偶用 |
| **columns_priv** | 列级别的权限 | 少用 |
| **proc** | 存储过程定义 | 常用 |
| **func** | 函数定义 | 常用 |

**权限的层级关系（自上而下匹配）：**

```
mysql.user        → 全局权限（SUPER、FILE 等最高权限在这里）
  ↓ 如果 user 表权限字段 = 'N'
mysql.db          → 数据库级别权限（对某库有 SELECT/INSERT 等）
  ↓ 如果 db 表权限字段 = 'N'
mysql.tables_priv → 表级别权限（精确到某张表能做什么）
  ↓ 仍然不够
mysql.columns_priv → 列级别权限（精确到"某表.某列"只读）
```

**常用查询：**

```sql
-- 查看所有用户
SELECT user, host, account_locked FROM mysql.user;

-- 查看谁有 SUPER 权限（危险权限，可修改全局变量）
SELECT user, host FROM mysql.user WHERE Super_priv = 'Y';

-- 查看某用户对某库的具体权限
SELECT * FROM mysql.db WHERE user = 'appuser' AND db = 'shop';

-- 查看存储过程
SELECT db, name, type FROM mysql.proc WHERE db = 'shop';
```

> **注意**：权限管理优先用 `GRANT` / `REVOKE` 语句，不要直接改 `mysql.*` 表（容易出错且不刷新）。

---

### 15.2 information_schema — 元数据

`information_schema` 是 ANSI SQL 标准的**元数据视图库**，内容从 `.frm` 文件和内部数据字典实时提取，**只读、内存临时表**。

**核心表：**

| 表名 | 内容 |
|------|------|
| **SCHEMATA** | 所有数据库 |
| **TABLES** | 所有表（含引擎、行数、数据/索引大小） |
| **COLUMNS** | 所有列（含类型、可空、默认值、注释） |
| **STATISTICS** | 所有索引（含唯一/非唯一、类型） |
| **TABLE_CONSTRAINTS** | 主键、外键、唯一约束 |
| **KEY_COLUMN_USAGE** | 约束涉及哪些列 |
| **ENGINES** | 支持的存储引擎 |
| **ROUTINES** | 存储过程、函数 |
| **VIEWS** | 视图定义 |

**最常用的查询：**

```sql
-- 1. 查表大小（运维必备）
SELECT
    TABLE_NAME                                      AS '表名',
    TABLE_ROWS                                      AS '约行数',
    ROUND(DATA_LENGTH / 1024 / 1024, 2)            AS '数据(MB)',
    ROUND(INDEX_LENGTH / 1024 / 1024, 2)           AS '索引(MB)',
    ROUND((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024, 2) AS '总(MB)'
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'shop'
ORDER BY (DATA_LENGTH + INDEX_LENGTH) DESC;

-- 2. 查表的所有列（替代 DESC）
SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT, COLUMN_COMMENT
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = 'shop' AND TABLE_NAME = 'users'
ORDER BY ORDINAL_POSITION;

-- 3. 查表的所有索引（替代 SHOW INDEX）
SELECT INDEX_NAME, COLUMN_NAME, NON_UNIQUE, INDEX_TYPE
FROM information_schema.STATISTICS
WHERE TABLE_SCHEMA = 'shop' AND TABLE_NAME = 'users';

-- 4. 找出没有主键的表（危险！主键缺失 → 主从延迟、行锁问题）
SELECT TABLE_NAME
FROM information_schema.TABLES t
WHERE TABLE_SCHEMA = 'shop'
  AND TABLE_NAME NOT IN (
      SELECT TABLE_NAME FROM information_schema.TABLE_CONSTRAINTS
      WHERE TABLE_SCHEMA = 'shop' AND CONSTRAINT_TYPE = 'PRIMARY KEY'
  );

-- 5. 查外键关系
SELECT
    TABLE_NAME              AS '表',
    COLUMN_NAME             AS '列',
    REFERENCED_TABLE_NAME   AS '引用表',
    REFERENCED_COLUMN_NAME  AS '引用列'
FROM information_schema.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = 'shop' AND REFERENCED_TABLE_NAME IS NOT NULL;
```

---

### 15.3 performance_schema — 性能监控

`performance_schema` 是 MySQL 的**实时性能采集引擎**，纯内存表，重启后清空。它是 `sys` 库的数据来源。

**能查什么：**

| 维度 | 关键表 | 典型问题 |
|------|--------|---------|
| **锁** | `data_locks`、`data_lock_waits` | 谁在等锁？谁阻塞的？ |
| **SQL 统计** | `events_statements_summary_by_digest` | 哪条 SQL 最慢？执行多少次？ |
| **事务** | `events_transactions_current` | 当前有哪些活跃事务？运行多久了？ |
| **内存** | `memory_summary_*` | 各模块用了多少内存？峰值多少？ |
| **文件 IO** | `file_summary_by_instance` | 哪个表 IO 最密集？ |
| **等待** | `events_waits_current` | 当前等待什么事件？ |

**最常用的查询：**

```sql
-- 1. 🔴 锁等待排查（最重要的运维场景）
SELECT
    r.trx_id                  AS '等待者事务',
    r.trx_mysql_thread_id     AS '等待者线程ID',
    b.trx_id                  AS '阻塞者事务',
    b.trx_mysql_thread_id     AS '阻塞者线程ID',
    b.trx_query               AS '阻塞者 SQL'
FROM information_schema.INNODB_LOCK_WAITS w
JOIN information_schema.INNODB_TRX r ON r.trx_id = w.requesting_trx_id
JOIN information_schema.INNODB_TRX b ON b.trx_id = w.blocking_trx_id;

-- MySQL 8.0+ 用这个（更精确）
SELECT
    waiting_trx_id,
    waiting_thread_id,
    blocking_trx_id,
    blocking_thread_id,
    wait_age
FROM performance_schema.data_lock_waits;

-- 2. 当前所有行锁
SELECT lock_type, lock_mode, lock_status, object_name, lock_data
FROM performance_schema.data_locks;

-- 3. 找出执行最慢的 10 种 SQL
SELECT
    DIGEST_TEXT,
    COUNT_STAR            AS '执行次数',
    ROUND(AVG_TIMER_WAIT / 1e9, 2) AS '平均耗时(ms)',
    SUM_ROWS_EXAMINED     AS '扫描行数'
FROM performance_schema.events_statements_summary_by_digest
ORDER BY AVG_TIMER_WAIT DESC
LIMIT 10;

-- 4. 当前活跃事务（长时间未提交的事务是隐患）
SELECT
    trx_id,
    trx_state,
    trx_mysql_thread_id   AS '线程ID',
    trx_rows_locked        AS '锁定行数',
    trx_rows_modified      AS '修改行数',
    TIMESTAMPDIFF(SECOND, trx_started, NOW()) AS '已运行(秒)'
FROM information_schema.INNODB_TRX;

-- 5. 哪个文件 IO 最频繁？
SELECT FILE_NAME,
       ROUND(SUM_NUMBER_OF_BYTES_READ / 1024 / 1024, 2)  AS '读(MB)',
       ROUND(SUM_NUMBER_OF_BYTES_WRITE / 1024 / 1024, 2) AS '写(MB)'
FROM performance_schema.file_summary_by_instance
ORDER BY SUM_NUMBER_OF_BYTES_READ + SUM_NUMBER_OF_BYTES_WRITE DESC
LIMIT 10;

-- 6. 确认是否开启
SHOW VARIABLES LIKE 'performance_schema';  -- ON = 开启
```

---

### 15.4 sys — 运维诊断

`sys` 库是 MySQL 5.7+ 的**运维辅助库**，把 `performance_schema` 的复杂查询封装成**易读视图 + 函数**。

**为什么要有 sys？手写 `performance_schema` 的查询又长又难记：**

```sql
-- ❌ performance_schema 原文（几十行 JOIN）
-- ✅ sys 一句话搞定
SELECT * FROM sys.statement_analysis ORDER BY total_latency DESC LIMIT 10;
```

**最常用的视图：**

| 视图 | 作用 | 一句话 |
|------|------|--------|
| `statement_analysis` | 所有 SQL 的性能排名 | 哪条 SQL 最耗时间？ |
| `innodb_lock_waits` | InnoDB 锁等待完整信息 | **谁阻塞了谁？含双方 SQL 内容！** |
| `schema_unused_indexes` | 从未使用的索引 | 哪些索引可以删？ |
| `schema_redundant_indexes` | 重复/冗余索引 | 哪些索引是多余的？ |
| `user_summary` | 每个用户的总 IO/延迟 | 哪个用户最费资源？ |
| `host_summary` | 每台主机的连接/IO | 哪台机器连接最多？ |
| `io_global_by_file_by_bytes` | 文件 IO 排名 | 哪个文件的 IO 最密集？ |
| `memory_global_total` | 全局内存使用 | MySQL 用了多少内存？ |
| `schema_object_overview` | 各库对象统计 | 每库多少表/视图/存储过程？ |

**常用查询：**

```sql
-- 1. 🥇 最耗时间的 SQL 排名
SELECT query, exec_count, total_latency, avg_latency, lock_latency
FROM sys.statement_analysis
ORDER BY total_latency DESC LIMIT 10;

-- 2. 🔴 当前锁等待（含双方 SQL 内容！最重要！）
SELECT
    waiting_pid          AS '等待者PID',
    waiting_statement    AS '等待中SQL',
    blocking_pid         AS '阻塞者PID',
    blocking_statement   AS '阻塞者SQL'
FROM sys.innodb_lock_waits;

-- 3. 哪些索引从未被查过？（可安全删除）
SELECT * FROM sys.schema_unused_indexes
WHERE object_schema = 'shop';

-- 4. 哪个用户扫描行数最多？（全表扫描大户）
SELECT user, total_connections, rows_examined, rows_sent
FROM sys.user_summary
ORDER BY rows_examined DESC;

-- 5. 整体内存使用
SELECT * FROM sys.memory_global_total;

-- 6. 哪个表 IO 最重
SELECT * FROM sys.io_global_by_file_by_bytes
WHERE file LIKE '%shop%'
ORDER BY total DESC;
```

---

### 15.5 四库关系图谱

```
                        ┌──────────────────────────┐
                        │       MySQL Server        │
                        └──────────────────────────┘
                                       │
        ┌──────────────┬───────────────┼───────────────┬──────────────┐
        ▼              ▼               ▼               ▼              ▼
  ┌──────────┐  ┌────────────────┐ ┌──────────┐  ┌──────────┐
  │  mysql   │  │information_schema│ │performance│  │   sys    │
  │           │  │                │ │  _schema │  │          │
  │ 账号权限  │  │  元数据/定义    │ │  性能指标  │  │ 运维诊断  │
  │ InnoDB    │  │  MEMORY 临时表  │ │ MEMORY    │  │ 易读视图  │
  │ 持久化    │  │  只读          │ │ 实时采集  │  │ 封装查询  │
  └──────────┘  └────────────────┘ └──────────┘  └──────────┘
        │              │               │               │
        │              │               └───────┬───────┘
        │              │                       │
        │              │              sys 的数据来自
        │              │              performance_schema
        │              │              + information_schema
        │              │
    GRANT/REVOKE    SHOW CREATE TABLE   先看 sys.xxx
    改权限           DESC                 解决不了再查
                    查元数据              performance_schema
```

| 库 | 记住一句话 | 最常用 |
|------|----------|--------|
| `mysql` | **谁能进来？** | `SELECT user, host FROM mysql.user` |
| `information_schema` | **系统里有什么？** | 查表大小、索引、列定义 |
| `performance_schema` | **发生了什么？** | 查锁等待、慢 SQL 统计 |
| `sys` | **翻译成人话** | 一键看锁等待含 SQL 内容 |

**日常排查口诀：**

```
查权限        → mysql.user
查表结构/大小 → information_schema.TABLES
查锁等待      → performance_schema.data_lock_waits
查慢SQL       → sys.statement_analysis
锁等待含SQL   → sys.innodb_lock_waits  ← 最好用！
```

---

## 速查卡片

### SQL 执行顺序

```
FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT
```

写 SQL 时按 `SELECT ... FROM ... WHERE ... GROUP BY ... HAVING ... ORDER BY ... LIMIT` 的顺序写，
但数据库实际按上面顺序执行。所以不能在 WHERE 中用别名！

### 常用函数

```sql
-- 字符串
CONCAT('Hello', ' ', 'World')     -- Hello World
SUBSTRING('Hello', 1, 2)          -- He
LENGTH('中文')                     -- 字节数
CHAR_LENGTH('中文')                -- 字符数（推荐）
REPLACE('ABCD', 'A', 'Z')         -- ZBCD
TRIM('  hello  ')                 -- hello

-- 数字
ROUND(3.14159, 2)                 -- 3.14
CEIL(3.1)                         -- 4（向上取整）
FLOOR(3.9)                        -- 3（向下取整）
RAND()                            -- 0~1 随机数

-- 日期
NOW()                             -- 当前日期时间
CURDATE()                         -- 当前日期
DATE_FORMAT(NOW(), '%Y-%m-%d')    -- 2024-01-01
DATEDIFF('2024-12-31', '2024-01-01')  -- 365
DATE_ADD(NOW(), INTERVAL 7 DAY)   -- 7天后

-- 条件判断
IF(age > 18, '成年', '未成年')
IFNULL(phone, '未填写')            -- 如果 phone 是 NULL 则显示 '未填写'
COALESCE(phone, email, '无')      -- 返回第一个非 NULL 值

-- 类型转换
CAST('123' AS SIGNED)             -- 转为数字
CONVERT('2024-01-01', DATE)       -- 转为日期
```

### CRUD 模板

```sql
-- 查
SELECT 列名 FROM 表名 WHERE 条件 ORDER BY 排序列 LIMIT 数量;

-- 增
INSERT INTO 表名 (列1, 列2) VALUES (值1, 值2);
INSERT INTO 表名 (列1, 列2) VALUES (值1, 值2), (值3, 值4);  -- 批量

-- 改
UPDATE 表名 SET 列1 = 值1, 列2 = 值2 WHERE 条件;  -- ⚠️ 必须带 WHERE

-- 删
DELETE FROM 表名 WHERE 条件;  -- ⚠️ 必须带 WHERE
```

### 新手常见错误 Top 5

| # | 错误 | 正确做法 |
|---|------|---------|
| 1 | UPDATE/DELETE 忘写 WHERE | 养成先写 WHERE 再写前面内容的习惯 |
| 2 | WHERE 中对列用函数 | 改写为范围查询 |
| 3 | 建表用 utf8 字符集 | 用 utf8mb4 |
| 4 | SELECT * 查出所有列 | 只查需要的列 |
| 5 | 金额用 FLOAT 存 | 用 DECIMAL(10,2) |

---

> **坚持手写 SQL，IDE 补全是辅助，理解每句话的意思才是关键。**
