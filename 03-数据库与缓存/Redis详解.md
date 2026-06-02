# Redis 速查手册

> 一份通俗易懂的 Redis 文档，涵盖日常开发中最常用的命令和场景，适合快速查阅和上手。

---

## 目录

- [1. 基础概念](#1-基础概念)
- [2. 安装与连接](#2-安装与连接)
- [3. 基础数据类型](#3-基础数据类型)
- [4. 进阶命令](#4-进阶命令)
- [5. 发布订阅](#5-发布订阅)
- [6. 事务](#6-事务)
- [7. Pipeline](#7-pipeline)
- [8. 过期策略与内存淘汰](#8-过期策略与内存淘汰)
- [9. 持久化](#9-持久化)
- [10. 主从与哨兵](#10-主从与哨兵)
- [11. 集群](#11-集群)
- [12. 缓存实战](#12-缓存实战)
- [13. Django 集成](#13-django-集成)
- [14. Celery 集成](#14-celery-集成)
- [15. 常见问题排查](#15-常见问题排查)

---

## 1. 基础概念

### 什么是 Redis？

Redis（**RE**mote **DI**ctionary **S**erver）是一个**基于内存的键值存储数据库**。

- 数据存在**内存**中，速度极快（读写 10万+/秒）
- 支持数据**持久化**到硬盘
- 不仅仅是 key-value，支持丰富的数据结构

### 核心用途

| 场景 | 说明 |
|------|------|
| **缓存** | 热点数据缓存，减轻数据库压力 |
| **分布式锁** | 多进程/多服务互斥 |
| **消息队列** | List/Stream 实现异步任务 |
| **排行榜** | Sorted Set 天然支持 |
| **计数器** | 点赞数、浏览量、限流计数 |
| **会话存储** | Session 共享 |
| **发布订阅** | 实时消息推送 |

### Redis vs MySQL

| | Redis | MySQL |
|------|-------|-------|
| **存储位置** | 内存 | 硬盘 |
| **速度** | 微秒级 | 毫秒级 |
| **数据结构** | String/List/Set/Hash/ZSet | 表 |
| **持久性** | 可选（RDB/AOF） | 默认持久 |
| **查询能力** | 简单 | SQL 强大 |
| **典型角色** | 缓存 + 临时数据 | 主存储 |

---

## 2. 安装与连接

### macOS

```bash
brew install redis
brew services start redis
```

### Linux

```bash
sudo apt install redis-server    # Ubuntu/Debian
sudo systemctl start redis
```

### Docker（推荐开发用）

```bash
docker run -d --name redis -p 6379:6379 redis:7-alpine
```

### 连接

```bash
# 本地
redis-cli

# 远程
redis-cli -h 192.168.1.100 -p 6379 -a mypassword

# 测试
127.0.0.1:6379> PING
PONG
```

---

## 3. 基础数据类型

### 3.1 String（字符串）

最基础的类型，可以存字符串、数字、JSON 等。

```bash
# 写
SET key value
SET user:1:name "张三"
SET count 100

# 读
GET key
GET user:1:name         # "张三"

# 带过期时间（秒）
SETEX token 3600 "abc123"   # 3600秒后自动删除

# 仅在 key 不存在时设置（分布式锁核心）
SETNX lock:order:123 1      # 返回 1=成功, 0=已存在

# 数字操作
INCR count              # 101（原子递增）
INCRBY count 10         # 111
DECR count              # 110

# 批量读写
MSET a 1 b 2 c 3
MGET a b c              # 1, 2, 3

# 查看剩余时间（秒）
TTL key                 # -1=永不过期, -2=已过期/不存在

# 删除
DEL key
```

### 3.2 Hash（哈希）

存对象属性，类似字典。

```bash
# 设置单个字段
HSET user:1 name "张三" age 25 email "zhangsan@test.com"

# 获取单个字段
HGET user:1 name              # "张三"

# 获取所有字段和值
HGETALL user:1                # name, 张三, age, 25, email, ...

# 获取多个字段
HMGET user:1 name age         # "张三", "25"

# 字段是否存在
HEXISTS user:1 email          # 1（存在）

# 删除字段
HDEL user:1 email

# 获取所有字段名
HKEYS user:1
```

### 3.3 List（列表）

有序的字符串列表，**头尾操作 O(1)**。

```bash
# 左端插入（头部）
LPUSH queue "task1" "task2"
# 右端插入（尾部）
RPUSH queue "task3"

# 左端弹出（头部）
LPOP queue                    # "task2"

# 右端弹出（尾部）
RPOP queue                    # "task3"

# 阻塞弹出（队列消费端，等有新元素才返回）
BLPOP queue 5               # 5秒超时

# 查看范围
LRANGE queue 0 -1            # 所有元素
LRANGE queue 0 4             # 前5个

# 长度
LLEN queue

# 按索引获取
LINDEX queue 0               # 第一个元素
```

**实战：消息队列（生产者-消费者）**

```bash
# 生产者
LPUSH myqueue "msg1"
LPUSH myqueue "msg2"

# 消费者
BRPOP myqueue 0    # 阻塞等待，有新消息立即消费
```

### 3.4 Set（集合）

无序不重复的字符串集合，支持**交/并/差集运算**。

```bash
# 添加
SADD tags:article:1 "Python" "Django" "Redis"

# 查看所有
SMEMBERS tags:article:1

# 是否成员
SISMEMBER tags:article:1 "Python"  # 1

# 随机弹出
SPOP tags:article:1            # 随机移除并返回一个

# 大小
SCARD tags:article:1

# 集合运算
SADD tags:article:2 "Django" "Celery"
SINTER tags:article:1 tags:article:2   # 交集：Django
SUNION tags:article:1 tags:article:2   # 并集
SDIFF tags:article:1 tags:article:2    # 差集：Python, Redis
```

**实战：共同好友**

```bash
SADD friends:user:1 "A" "B" "C"
SADD friends:user:2 "B" "C" "D"
SINTER friends:user:1 friends:user:2   # B, C（共同好友）
```

### 3.5 Sorted Set（有序集合）

每个成员关联一个**分数（score）**，按分数排序。

```bash
# 添加（需指定 score）
ZADD ranking 100 "张三" 90 "李四" 85 "王五"

# 按分数升序
ZRANGE ranking 0 -1                # 王五, 李四, 张三

# 按分数降序
ZREVRANGE ranking 0 -1             # 张三, 李四, 王五

# 带分数返回
ZREVRANGE ranking 0 -1 WITHSCORES
# 张三 100, 李四 90, 王五 85

# 查看某成员分数
ZSCORE ranking "张三"               # 100

# 增减分数
ZINCRBY ranking 5 "张三"            # 105

# 按分数范围查
ZRANGEBYSCORE ranking 85 95        # 李四, 王五

# 查看排名
ZRANK ranking "张三"               # 2（从0开始，升序）
ZREVRANK ranking "张三"            # 0（降序排名）

# 删除
ZREM ranking "王五"
```

**实战：排行榜**

```bash
# 商品销量排行
ZINCRBY product:sales 1 "商品A"     # 每卖一件 +1
ZINCRBY product:sales 1 "商品A"
ZREVRANGE product:sales 0 9 WITHSCORES  # Top 10
```

---

## 4. 进阶命令

### 通用命令

```bash
# 查看所有 key（生产环境慎用！）
KEYS *                           # 全量扫描，会阻塞！
KEYS user:*                      # 匹配 user: 开头的

# 渐进式扫描（生产环境推荐）
SCAN 0 MATCH user:* COUNT 100    # 游标 + 匹配模式 + 每次数量

# 判断 key 是否存在
EXISTS key

# 查看 key 类型
TYPE key                         # string, hash, list, set, zset

# 删除
DEL key1 key2

# 重命名
RENAME old new

# 设置过期时间
EXPIRE key 300                   # 300秒后过期
PEXPIRE key 1000                 # 1000毫秒后过期

# 移除过期时间（变为永久）
PERSIST key
```

### Bitmap（位图）

```bash
# 用户签到（每个用户一个 bit，0=未签, 1=已签）
SETBIT sign:2024-06-01 1001 1     # 用户1001签到
SETBIT sign:2024-06-01 1002 1

# 检查是否签到
GETBIT sign:2024-06-01 1001       # 1（已签）

# 统计签到人数
BITCOUNT sign:2024-06-01          # 2
```

### HyperLogLog（基数统计）

```bash
# UV 统计（不存具体用户，只估算独立访客数，误差约 0.81%）
PFADD uv:page:home user1 user2 user3
PFCOUNT uv:page:home              # 3
```

---

## 5. 发布订阅

```bash
# 终端1：订阅频道
SUBSCRIBE news                    # 阻塞等待消息

# 终端2：发布消息
PUBLISH news "Breaking News!"     # 终端1 立即收到

# 模式订阅（* 匹配任意）
PSUBSCRIBE news:*                 # 接收 news:sport, news:tech 等
```

---

## 6. 事务

Redis 事务保证**原子性**（要么全执行，要么全不执行），但不支持回滚。

```bash
# 开启事务
MULTI

SET a 1
SET b 2
INCR a

# 执行（原子执行）
EXEC
# 返回：OK, OK, 2

# 或放弃
DISCARD     # 丢弃 MULTI 之后的命令
```

**乐观锁：WATCH**

```bash
# 监控某个 key，如果从 WATCH 到 EXEC 之间被改了，事务不执行
WATCH stock:product:1
GET stock:product:1            # 100

MULTI
DECRBY stock:product:1 1       # 减库存
EXEC                           # 如果有人抢先改了库存，返回 nil
```

---

## 7. Pipeline

批量发送命令，减少网络往返（RTT），大幅提升批量操作性能。

```bash
# Redis CLI 不支持 pipeline 写法，但在代码中这样用：# Python 示例
pipe = r.pipeline()
pipe.set("a", 1)
pipe.set("b", 2)
pipe.incr("a")
results = pipe.execute()    # 一次发送 3 条命令
# [True, True, 2]

# 性能对比：1000 次 SET
# 普通方式：1000 次 RTT  ~ 100ms
# Pipeline：1 次 RTT      ~ 1ms
```

---

## 8. 过期策略与内存淘汰

### 过期键删除策略

| 策略 | 说明 |
|------|------|
| **惰性删除** | 访问 key 时检查是否过期，过期则删 |
| **定期删除** | 每隔 100ms 随机抽查一批 key，删掉过期的 |

两者配合使用。

### 内存淘汰策略（内存满了怎么办？）

```bash
# 查看当前配置
CONFIG GET maxmemory-policy

# 设置
CONFIG SET maxmemory-policy allkeys-lru

# 持久化配置（redis.conf）
maxmemory 2gb
maxmemory-policy allkeys-lru
```

| 策略 | 说明 |
|------|------|
| `noeviction` | 不淘汰，写入报错（默认） |
| `allkeys-lru` | 所有 key 中淘汰最近最少用的（**推荐**） |
| `allkeys-lfu` | 所有 key 中淘汰最不常用的 |
| `volatile-lru` | 只在设置了过期时间的 key 中淘汰 |
| `allkeys-random` | 随机淘汰 |
| `volatile-ttl` | 淘汰 TTL 最短的 |

---

## 9. 持久化

### RDB（快照）

定期把内存数据保存到 `.rdb` 文件。

```bash
# redis.conf
save 900 1        # 900秒内有1次修改就快照
save 300 10       # 300秒内有10次修改就快照
save 60 10000     # 60秒内有10000次修改就快照
```

- 优点：恢复快、文件小
- 缺点：两次快照之间可能丢数据

### AOF（追加日志）

把每条写命令追加到 `.aof` 文件。

```bash
# redis.conf
appendonly yes
appendfsync everysec    # 每秒同步一次（推荐）
# appendfsync always    # 每条都同步（最安全，最慢）
# appendfsync no        # 不主动同步
```

- 优点：数据更安全，最多丢 1 秒
- 缺点：文件大、恢复慢

### 生产建议

**RDB + AOF 同时开启**，用 RDB 做备份恢复，用 AOF 保证数据安全。

---

## 10. 主从与哨兵

### 主从复制

```
┌─────────┐     复制     ┌─────────┐
│  Master │  ──────────→ │  Slave  │
│  (写)    │              │  (读)    │
└─────────┘              └─────────┘
```

```bash
# 从节点配置
# redis.conf
replicaof 192.168.1.100 6379
masterauth mypassword    # 主节点密码
```

### 哨兵（Sentinel）

自动监控主节点健康，**主节点挂了自动选举新主**。

```bash
# sentinel.conf
sentinel monitor mymaster 192.168.1.100 6379 2
# 2=至少2个哨兵同意才判定主节点挂了

sentinel down-after-milliseconds mymaster 5000  # 5秒无响应判定下线
sentinel failover-timeout mymaster 60000        # 故障转移超时60秒

# 启动哨兵
redis-sentinel sentinel.conf
```

---

## 11. 集群

数据分片，每个节点只存一部分数据。

```
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Master 1 │  │ Master 2 │  │ Master 3 │
│ 槽0-5460 │  │5461-10922│  │10923-16383│
└──────────┘  └──────────┘  └──────────┘
```

```bash
# 启动 6 个 Redis 实例（3 主 3 从）
# 创建集群
redis-cli --cluster create \
  192.168.1.1:6379 192.168.1.2:6379 192.168.1.3:6379 \
  192.168.1.4:6379 192.168.1.5:6379 192.168.1.6:6379 \
  --cluster-replicas 1

# 连接集群
redis-cli -c -h 192.168.1.1 -p 6379
```

---

## 12. 缓存实战

### 缓存穿透

**问题**：查一个数据库中不存在的 key，每次请求都穿透缓存打到 DB。

**解决**：

```python
# 方案 1：缓存空值
def get_product(product_id):
    key = f"product:{product_id}"
    data = cache.get(key)
    if data is not None:
        return data if data != "NULL" else None  # NULL 是空标记

    product = db.query(product_id)
    if product:
        cache.set(key, product, 300)
    else:
        cache.set(key, "NULL", 60)  # 空值也缓存，短过期
    return product

# 方案 2：布隆过滤器（Bloom Filter）
# 把所有存在的 ID 预先存入布隆过滤器
# 请求先过布隆过滤器，不存在的直接拒绝
```

### 缓存击穿

**问题**：一个热点 key 过期瞬间，大量请求同时打到 DB。

**解决**：

```python
# 互斥锁：只让一个请求去加载 DB
def get_hot_product(product_id):
    key = f"product:{product_id}"
    data = cache.get(key)
    if data:
        return data

    lock_key = f"lock:product:{product_id}"
    # 尝试获取锁
    if cache.add(lock_key, 1, 10):  # add = Redis SETNX + EXPIRE
        try:
            data = db.query(product_id)
            cache.set(key, data, 300)
        finally:
            cache.delete(lock_key)
    else:
        time.sleep(0.1)
        data = cache.get(key)  # 重试读缓存
    return data
```

### 缓存雪崩

**问题**：大量 key 在同一时间过期，DB 瞬间压力过大。

**解决**：

```python
# 1. 过期时间加随机偏移
import random
cache.set(key, data, 300 + random.randint(0, 60))  # 300~360秒

# 2. 永不过期 + 异步更新（热点 key）
cache.set(key, data)  # 不设过期
# 后台异步任务更新
```

### 缓存一致性

```python
# 先更新数据库，再删缓存（Cache Aside 模式）
def update_product(product_id, data):
    db.update(product_id, data)       # 1. 写 DB
    cache.delete(f"product:{product_id}")  # 2. 删缓存
    # 等下次读时，缓存未命中，自动从 DB 加载最新数据
```

---

## 13. Django 集成

```bash
pip install redis django-redis
```

```python
# settings.py
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": "mypassword",  # 可选
            "CONNECTION_POOL_KWARGS": {"max_connections": 50},
            "SERIALIZER": "django_redis.serializers.json.JSONSerializer",
        },
        "KEY_PREFIX": "myapp",
    }
}

# Session 用 Redis 存储
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
```

```python
# 使用
from django.core.cache import cache

# 基础读写
cache.set("key", "value", timeout=300)
value = cache.get("key")

# 不存在则设
cache.get_or_set("counter", 0, 300)

# 不存在才设（SETNX）
cache.add("lock:task", 1, 60)     # 返回 True/False

# 增减
cache.incr("counter")              # 1→2
cache.decr("counter")              # 2→1

# 删除
cache.delete("key")

# 批量
cache.set_many({"a": 1, "b": 2}, 300)
cache.get_many(["a", "b"])         # {"a": 1, "b": 2}
cache.delete_many(["a", "b"])

# 视图缓存
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)     # 缓存 15 分钟
def product_list(request):
    products = Product.objects.all()
    return render(request, "list.html", {"products": products})

# 模板缓存
{% load cache %}
{% cache 300 product_sidebar %}
  ... 耗时渲染内容 ...
{% endcache %}
```

### 直接使用 Redis 原生命令

```python
from django_redis import get_redis_connection

conn = get_redis_connection("default")

# 不用 Django Cache 抽象，直接操作 Redis
conn.hset("user:1", mapping={"name": "张三", "age": 25})
conn.hgetall("user:1")

conn.zadd("ranking", {"张三": 100, "李四": 90})
conn.zrevrange("ranking", 0, -1, withscores=True)

conn.lpush("queue", "task1", "task2")
conn.brpop("queue", timeout=5)
```

---

## 14. Celery 集成

```python
# settings.py
CELERY_BROKER_URL = "redis://127.0.0.1:6379/0"      # 任务队列
CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379/2"   # 结果存储
```

```python
# 分布式锁（Django 项目中使用 Redlock）
import redis
import uuid
import time

class RedisLock:
    """基于 Redis 的分布式锁"""

    def __init__(self, client, key, expire=30):
        self.client = client
        self.key = f"lock:{key}"
        self.expire = expire
        self.token = str(uuid.uuid4())

    def __enter__(self):
        # 循环获取锁
        while True:
            if self.client.set(self.key, self.token, nx=True, ex=self.expire):
                return self
            time.sleep(0.1)

    def __exit__(self, *args):
        # Lua 脚本保证原子性：只有持锁者才能释放
        script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        self.client.eval(script, 1, self.key, self.token)

# 使用
r = redis.Redis()
with RedisLock(r, "order:123", expire=30):
    # 业务逻辑（同一时间只有一个进程能执行）
    process_order(123)
```

---

## 15. 常见问题排查

```bash
# 查看所有配置
CONFIG GET *
CONFIG GET maxmemory

# 内存使用
INFO memory
# used_memory_human: 1.2G
# used_memory_rss_human: 1.5G

# 统计信息
INFO stats
# keyspace_hits: 缓存命中次数
# keyspace_misses: 缓存未命中次数
# 命中率 = hits / (hits + misses)

# 客户端连接
INFO clients
CLIENT LIST

# 慢查询
SLOWLOG GET 10           # 最近 10 条慢查询
CONFIG SET slowlog-log-slower-than 10000  # 超过 10ms 就记录（微秒）

# 大 key 排查
redis-cli --bigkeys

# 热点 key 监控
redis-cli --hotkeys

# 持久化状态
INFO persistence

# 主从状态
INFO replication
```

### 生产环境常用配置

```bash
# redis.conf
maxmemory 2gb                         # 最大内存
maxmemory-policy allkeys-lru          # 淘汰策略
save 900 1                            # RDB 快照
save 300 10
appendonly yes                        # 开启 AOF
appendfsync everysec                  # 每秒同步
timeout 300                           # 空闲连接超时
requirepass strongpassword            # 密码
rename-command FLUSHDB ""             # 禁用危险命令
rename-command FLUSHALL ""
rename-command KEYS ""                # 禁用 KEYS *
```

---

## 速查卡片

### 五大类型操作

```bash
# String
SET key value    GET key    INCR key    SETEX key 300 value

# Hash
HSET key field value    HGET key field    HGETALL key

# List
LPUSH key val    RPUSH key val    LPOP key    LRANGE key 0 -1

# Set
SADD key member    SMEMBERS key    SINTER k1 k2

# Sorted Set
ZADD key score member    ZRANGE key 0 -1    ZREVRANGE key 0 -1 WITHSCORES
```

### Python 客户端

```python
import redis
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# String
r.set("key", "value", ex=300)
r.get("key")

# Hash
r.hset("user:1", mapping={"name": "张三", "age": 25})
r.hgetall("user:1")

# List
r.lpush("queue", "task")
r.brpop("queue", 5)

# Set
r.sadd("tags", "Python", "Redis")
r.smembers("tags")

# Sorted Set
r.zadd("rank", {"张三": 100})
r.zrevrange("rank", 0, -1, withscores=True)
```

### Django 缓存

```python
from django.core.cache import cache
cache.set("key", value, 300)
cache.get("key")
cache.get_or_set("key", default, 300)
cache.delete("key")
```

---

> **Redis 的核心优势：快、数据结构丰富、原子操作。用对数据结构能极大简化业务代码。**
