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
- [13. 分布式锁](#13-分布式锁)
  - [13.1 基础实现 — SET NX EX](#131-基础实现--set-nx-ex)
  - [13.2 严谨实现 — Lua 原子释放](#132-严谨实现--lua-原子释放)
  - [13.3 锁续期 (Watchdog)](#133-锁续期-watchdog)
  - [13.4 生产级封装 — python-redis-lock](#134-生产级封装--python-redis-lock)
  - [13.5 Redlock — 多节点分布式锁](#135-redlock--多节点分布式锁)
  - [13.6 基于 ZooKeeper / etcd 的锁](#136-基于-zookeeper--etcd-的锁)
  - [13.7 数据库悲观锁与乐观锁](#137-数据库悲观锁与乐观锁)
  - [13.8 分布式锁选型指南](#138-分布式锁选型指南)
  - [13.9 常见误区与最佳实践](#139-常见误区与最佳实践)
- [14. Django 集成](#14-django-集成)
- [15. Celery 集成](#15-celery-集成)
- [16. 常见问题排查](#16-常见问题排查)

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

## 13. 分布式锁

分布式锁是分布式系统中保证**多进程/多服务互斥访问共享资源**的核心机制。Redis 是实现分布式锁最常用的方案。

### 13.1 基础实现 — SET NX EX

**核心命令**：`SET key value NX EX seconds`

```bash
# NX = 仅当 key 不存在时设置（Not eXists）
# EX = 设置过期时间（EXpire），防止死锁
SET lock:order:123 uuid-token NX EX 10
# 返回 OK = 获取锁成功，返回 nil = 锁已被占用
```

**Python 手写版：**

```python
import redis
import uuid
import time

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

class SimpleRedisLock:
    """基础版分布式锁 — 仅用于理解原理，生产环境别用在关键业务"""

    def __init__(self, key, expire=30):
        self.client = r
        self.key = f"lock:{key}"
        self.expire = expire
        self.token = uuid.uuid4().hex  # 唯一标识，防止误删别人的锁

    def acquire(self) -> bool:
        """获取锁"""
        return self.client.set(self.key, self.token, nx=True, ex=self.expire)

    def release(self):
        """释放锁（注意：这里释放的是不是自己的锁？）"""
        # ⚠️ 基础版的问题：直接 DEL 可能误删别人的锁
        self.client.delete(self.key)


# 使用
lock = SimpleRedisLock("order:123", expire=10)
if lock.acquire():
    try:
        # 执行业务逻辑
        process_order(123)
    finally:
        lock.release()
else:
    print("获取锁失败，稍后重试")
```

> **基础版的致命缺陷**：如果 A 的锁到期自动过期 → B 获取了锁 → A 的 `release()` 删除了 B 的锁！这就是"**锁误删**"问题。

---

### 13.2 严谨实现 — Lua 原子释放

用 **Lua 脚本**保证"判断 + 删除"是原子操作：只有值匹配（证明是自己的锁）才删除。

```python
class RobustRedisLock:
    """严谨版分布式锁：Lua 原子释放 + 重试机制"""

    def __init__(self, key, expire=30, retry_times=3, retry_delay=0.1):
        self.client = r
        self.key = f"lock:{key}"
        self.expire = expire
        self.token = uuid.uuid4().hex
        self.retry_times = retry_times
        self.retry_delay = retry_delay

        # Lua 脚本：原子化 "判断值 → 删除"
        self._release_script = r.register_script("""
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
        """)

    def acquire(self) -> bool:
        """获取锁，失败则重试"""
        for _ in range(self.retry_times):
            if self.client.set(self.key, self.token, nx=True, ex=self.expire):
                return True
            time.sleep(self.retry_delay)
        return False

    def release(self):
        """Lua 脚本原子释放：只释放自己的锁"""
        self._release_script(keys=[self.key], args=[self.token])

    def __enter__(self):
        if not self.acquire():
            raise RuntimeError(f"获取锁失败: {self.key}")
        return self

    def __exit__(self, *args):
        self.release()
```

**为什么必须用 Lua？**

```
非原子操作（有风险）：
  ① GET lock:order    → "token_A"
  ② 判断 (token == token_A) → TRUE
  ③ DEL lock:order    → 删除了！

问题：在 ② 和 ③ 之间，token_A 可能已过期，B 获取了 token_B 的锁
结果：A 误删了 B 的锁！

原子操作（Lua 脚本）：
  ①②③ 在 Redis 服务端一次性执行完毕，中间不会有其他操作插入 ✅
```

---

### 13.3 锁续期 (Watchdog)

**问题**：业务执行时间不确定，如果超过 `expire`，锁会提前释放。

**解决**：后台线程定期续期。

```python
import threading

class AutoRenewLock:
    """带自动续期的分布式锁"""

    def __init__(self, key, expire=30, renew_interval=None):
        self.client = r
        self.key = f"lock:{key}"
        self.expire = expire
        self.token = uuid.uuid4().hex
        self._renew_interval = renew_interval or max(1, expire // 3)  # 每 1/3 过期时间续一次
        self._renew_thread = None
        self._renew_stop = threading.Event()

        self._release_script = r.register_script("""
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
        """)

        self._renew_script = r.register_script("""
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("expire", KEYS[1], ARGV[2])
            else
                return 0
            end
        """)

    def _auto_renew(self):
        """后台续期线程"""
        while not self._renew_stop.wait(self._renew_interval):
            result = self._renew_script(
                keys=[self.key], args=[self.token, self.expire]
            )
            if not result:
                # 锁已经不属于自己了（被抢占或已过期）
                break

    def acquire(self) -> bool:
        if not self.client.set(self.key, self.token, nx=True, ex=self.expire):
            return False

        # 启动后台续期
        self._renew_thread = threading.Thread(target=self._auto_renew, daemon=True)
        self._renew_thread.start()
        return True

    def release(self):
        self._renew_stop.set()  # 停止续期
        if self._renew_thread:
            self._renew_thread.join(timeout=1)
        self._release_script(keys=[self.key], args=[self.token])


# 使用（上下文管理器）
lock = AutoRenewLock("long_task", expire=30)
if lock.acquire():
    try:
        time.sleep(60)  # 模拟长任务（锁会自动续期）
    finally:
        lock.release()
```

---

### 13.4 生产级封装 — python-redis-lock

生产环境**直接用现成库**，避免自己造轮子出问题：

```bash
pip install python-redis-lock
```

```python
import redis
from redis_lock import Lock

r = redis.Redis(host='localhost', port=6379)

# 基础用法
lock = Lock(r, "order:123", expire=10, auto_renewal=True)
with lock:
    # auto_renewal=True: 自动续期，不会因为业务超时而提前释放
    do_something()

# 非阻塞获取（立即返回）
lock = Lock(r, "task:export", expire=60)
if lock.acquire(blocking=False):
    try:
        do_export()
    finally:
        lock.release()
else:
    print("任务正在执行中，跳过")

# 阻塞获取（等待最多 5 秒）
lock = Lock(r, "task:process", expire=30)
if lock.acquire(blocking=True, timeout=5):
    try:
        do_process()
    finally:
        lock.release()
else:
    print("5 秒内未获取到锁，放弃")
```

---

### 13.5 Redlock — 多节点分布式锁

**为什么需要 Redlock？**

单 Redis 节点：Master 宕机 → Slave 提升 → 锁可能丢失（主从复制是异步的）。

Redlock 算法：向 **N 个独立 Redis 节点**（推荐 5 个）依次获取锁，大多数（>= N/2+1）同意才算成功。

```bash
pip install redlock-py
```

```python
from redlock import Redlock

# 连接 5 个独立 Redis 节点
dlm = Redlock([
    {"host": "redis-node-1", "port": 6379},
    {"host": "redis-node-2", "port": 6379},
    {"host": "redis-node-3", "port": 6379},
    {"host": "redis-node-4", "port": 6379},
    {"host": "redis-node-5", "port": 6379},
])

# 获取锁
lock = dlm.lock("critical:resource", ttl=10000)  # TTL 单位毫秒
if lock:
    try:
        do_critical_operation()
    finally:
        dlm.unlock(lock)
else:
    print("获取锁失败")
```

| 方案 | 可靠性 | 性能 | 适用场景 |
|------|--------|------|---------|
| 单节点 Redis | 中 | 高 | 日常开发（90% 场景） |
| Redlock | 高 | 中 | 金融、支付关键业务 |
| Redis Cluster | 中 | 高 | 不是为锁设计的，不推荐直接用 |

---

### 13.6 基于 ZooKeeper / etcd 的锁

当 Redis 的 AP 特性不够时，用 CP 一致性系统。

**ZooKeeper（kazoo）：**

```bash
pip install kazoo
```

```python
from kazoo.client import KazooClient
from kazoo.recipe.lock import Lock

zk = KazooClient(hosts='localhost:2181')
zk.start()

lock = zk.Lock("/locks/order:123", "identifier")

with lock:
    # ZK 保证：只有持锁者才能执行
    # 特性：临时顺序节点 + Watch 机制，天然防死锁
    do_critical_work()
```

**etcd（etcd3）：**

```bash
pip install etcd3
```

```python
import etcd3

client = etcd3.client(host='localhost', port=2379)

lock = client.lock("order:123", ttl=10)

with lock:
    # etcd 使用 Lease 租约机制，过时自动释放
    do_work()
```

---

### 13.7 数据库悲观锁与乐观锁

当没有 Redis/ZK 等中间件时，直接利用数据库。

**悲观锁（`SELECT ... FOR UPDATE`）：**

```python
# Django 示例
from django.db import transaction

with transaction.atomic():
    # FOR UPDATE = 行级排他锁，阻塞其他事务读取
    order = Order.objects.select_for_update().get(id=123)

    if order.status == 'pending':
        order.status = 'processing'
        order.save()
    # 事务提交后释放锁
```

**乐观锁（版本号 / 时间戳）：**

```python
# 不阻塞，冲突时重试
affected = Product.objects.filter(
    id=1,
    stock__gte=1,              # 库存充足
    version=current_version,    # 版本号匹配
).update(
    stock=models.F('stock') - 1,
    version=current_version + 1,
)

if affected == 0:
    # 被其他进程抢先了，重试
    raise RetryException("请重试")
```

---

### 13.8 分布式锁选型指南

```
                        需要分布式锁
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
        已有 Redis？    已有 ZK/etcd？   只有数据库？
            │               │               │
            ▼               ▼               ▼
     ┌──────────┐   ┌──────────┐   ┌──────────┐
     │单节点Redis│   │kazoo/etcd3│  │悲观锁/乐观锁│
     │(90%场景)  │   │(强一致性) │   │(无额外组件)│
     └──────────┘   └──────────┘   └──────────┘
            │
     是否关键业务？
        │       │
        ▼       ▼
     简单业务   金融/支付
    单节点锁   Redlock
```

| 方案 | 可靠性 | 性能 | 复杂度 | 典型场景 |
|------|--------|------|--------|---------|
| **Redis 单节点** | 中 | 高 | 低 | 通用场景，**首选** |
| **Redis Redlock** | 高 | 中 | 中 | 需要高可靠性的关键业务 |
| **ZooKeeper** | 极高（CP） | 低 | 中 | 金融、强一致性场景 |
| **etcd** | 极高（CP） | 低 | 中 | K8s 环境、强一致性场景 |
| **数据库行锁** | 中 | 低 | 低 | 无中间件时的兜底方案 |
| **数据库乐观锁** | 中 | 中 | 低 | 读多写少、冲突少的场景 |

---

### 13.9 常见误区与最佳实践

| 误区 | 真相 |
|------|------|
| "SETNX + EXPIRE 就够了" | 这不是原子操作！SETNX 后宕机 → 死锁。必须用 `SET ... NX EX` 一次完成 |
| "DEL 删除锁就行" | 可能误删别人的锁！必须用 Lua 脚本"先判断值再删除" |
| "过期时间设长一点就不会有问题" | 进程崩溃会持有锁直到过期，阻塞所有竞争者。设合理的 expire + 续期机制 |
| "Redis 做锁肯定不丢" | Redis 主从异步复制，主宕机锁可能丢。关键业务用 Redlock |
| "分布式锁保证绝对互斥" | 即使是 Redlock，极端情况下也可能不互斥（时钟跳跃、GC 暂停）。业务层必须做好并发兼容 |

**一段代码记忆所有要点：**

```python
# 一个严谨的分布式锁必须具备的 5 个要素

# ① 防死锁：一口气设置 NX + EX
acquired = r.set("lock:key", token, nx=True, ex=10)

# ② 防误删：Lua 原子化释放（只删自己的锁）
release = r.register_script("""
    if redis.call("get",KEYS[1]) == ARGV[1] then
        return redis.call("del",KEYS[1])
    else return 0 end
""")

# ③ 防超时：后台续期（Watchdog 线程）
# ④ 防饥饿：获取失败要重试（retry）
# ⑤ 业务幂等：有了并发，业务本身必须支持幂等
```

---

## 14. Django 集成

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

## 15. Celery 集成

```python
CELERY_BROKER_URL = "redis://127.0.0.1:6379/0"      # 任务队列
CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379/2"   # 结果存储
```

---

## 16. 常见问题排查

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
