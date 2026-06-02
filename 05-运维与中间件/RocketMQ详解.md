# RocketMQ 速查手册

> 一份通俗易懂的 RocketMQ 文档，涵盖日常开发中最常用的操作和概念，适合快速查阅和上手。

---

## 目录

- [1. 基础概念](#1-基础概念)
- [2. 安装与部署](#2-安装与部署)
- [3. 核心架构](#3-核心架构)
- [4. Topic 与消息类型](#4-topic-与消息类型)
- [5. 生产者 (Producer)](#5-生产者-producer)
- [6. 消费者 (Consumer)](#6-消费者-consumer)
- [7. 顺序消息](#7-顺序消息)
- [8. 延迟消息](#8-延迟消息)
- [9. 事务消息](#9-事务消息)
- [10. 消息可靠性](#10-消息可靠性)
- [11. 运维管理](#11-运维管理)
- [12. 监控与排查](#12-监控与排查)
- [13. RocketMQ vs Kafka 选型](#13-rocketmq-vs-kafka-选型)

---

## 1. 基础概念

### 1.1 什么是 RocketMQ？

RocketMQ 是阿里巴巴开源的**分布式消息中间件**，经过历年双 11 万亿级消息验证，特点是**金融级可靠性**和**丰富的消息类型**。

你可以把它理解为一个"高可靠消息快递系统"：

- **发消息** = 把包裹交到驿站
- **收消息** = 从驿站取包裹
- **不丢件** = 所有环节都有确认机制
- **定时送** = 可以指定延迟时间投递

### 1.2 核心术语

| 术语 | 说明 | 类比 |
|------|------|------|
| **NameServer** | 路由注册中心，无状态 | 驿站地址簿 |
| **Broker** | 消息存储和转发节点 | 驿站 |
| **Topic** | 消息的逻辑分类 | 快递类型 |
| **Tag** | Topic 下的子标签，消费者可过滤 | 快递的二级分类 |
| **Message Queue** | Topic 下的物理分片 | 驿站的货架 |
| **Producer** | 生产者，发消息 | 寄件人 |
| **Consumer** | 消费者，收消息 | 收件人 |
| **Consumer Group** | 消费者组，组内竞争消费 | 一个团队轮流取件 |
| **Offset** | 消费位置 | 取到了第几个包裹 |
| **CommitLog** | 所有消息的物理存储文件 | 驿站的入库总账本 |
| **ConsumeQueue** | 消费队列索引，指向 CommitLog | 每种快递的取件目录 |

### 1.3 RocketMQ 能做什么？

| 场景 | 说明 | 例子 |
|------|------|------|
| **异步解耦** | 系统间通过消息通信 | 下单后发消息 → 扣库存/发短信/加积分 |
| **削峰填谷** | 高峰请求暂存，慢慢处理 | 秒杀 10 万 QPS → 后端 5 千 QPS 消费 |
| **分布式事务** | 事务消息保证最终一致性 | 下单(DB) + 扣库存(RPC) → 最终一致 |
| **定时任务** | 延迟消息替代定时任务轮询 | 30 分钟后检查支付状态 |
| **顺序处理** | 严格顺序的消息处理 | 订单状态流转（待支付→已支付→已发货） |

---

## 2. 安装与部署

### 2.1 Python 客户端安装

```bash
# RocketMQ Python 客户端（基于 C++ 客户端封装）
pip install rocketmq-client-python
```

### 2.2 Docker 快速启动（单机测试）

```bash
# NameServer（必装）
docker run -d --name rmq-namesrv \
  -p 9876:9876 \
  -e "MAX_POSSIBLE_HEAP=200000000" \
  apache/rocketmq:latest sh mqnamesrv

# Broker（需要先启动 NameServer）
docker run -d --name rmq-broker \
  -p 10911:10911 -p 10909:10909 \
  -e "NAMESRV_ADDR=host.docker.internal:9876" \
  -e "MAX_POSSIBLE_HEAP=200000000" \
  apache/rocketmq:latest sh mqbroker \
  -n host.docker.internal:9876 \
  -c /home/rocketmq/rocketmq-5.3.0/conf/broker.conf
```

### 2.3 控制台（Dashboard）

```bash
# RocketMQ Dashboard（Web 管理界面）
docker run -d --name rmq-console \
  -p 8080:8080 \
  -e "JAVA_OPTS=-Drocketmq.namesrv.addr=host.docker.internal:9876" \
  apacherocketmq/rocketmq-dashboard:latest
```

访问 `http://localhost:8080` 即可查看集群状态、消息内容、消费进度。

### 2.4 生产环境最小配置

```
┌─────────────┐  ┌─────────────┐
│ NameServer 1│  │ NameServer 2│  （无状态，多个互备）
└─────────────┘  └─────────────┘

┌───────────┐  ┌───────────┐
│ Broker A  │  │ Broker B  │  （Master-Slave 或 Dledger 多副本）
│ Master    │──│ Slave     │
└───────────┘  └───────────┘
```

---

## 3. 核心架构

### 3.1 整体架构图

```
┌──────────────────────────────────────────────────┐
│              NameServer Cluster                   │
│           (路由注册，无状态，互为备)                 │
└────┬────────────────────────────────┬────────────┘
     │ 注册/心跳                       │ 注册/心跳
┌────▼──────────┐              ┌─────▼─────────┐
│  Broker A     │              │  Broker B      │
│  Master       │─────同步────▶│  Slave          │
│               │              │                │
│  CommitLog ──▶ ConsumeQueue │  ConsumeQueue   │
└────▲──────────┘    └─────────┘ ──────────────┐
     │ 发送消息                         拉取消息 │
┌────┴──────────┐              ┌───────────────▼┐
│  Producer     │              │  Consumer      │
│  (生产者)      │              │  (消费者组)     │
└───────────────┘              └────────────────┘
```

### 3.2 存储架构（最核心的设计）

RocketMQ 的存储设计是其高性能的关键：

```
Broker 磁盘存储结构：

~/store/
├── commitlog/                    ← 所有消息顺序写入到这里！
│   ├── 00000000000000000000      ← 1GB 一个文件
│   └── 00000000001073741824
│
├── consumequeue/                 ← 消费队列（只是指向 CommitLog 的索引）
│   └── TopicA/                   ← 每个 Topic 一个目录
│       └── queue0/               ← 每个队列一个目录
│           └── 0000000000000000
│
│── index/                        ← 索引文件（按 key 查消息）
│   └── ...
└── config/                       ← 配置信息
```

**关键设计：**

| 特点 | 说明 |
|------|------|
| **单文件顺序写** | 所有 Topic 的消息都写入同一个 CommitLog，纯顺序追加，无随机写 |
| **读写分离** | 写入 CommitLog → 异步构建 ConsumeQueue 索引 |
| **零拷贝** | 使用 `mmap` + `sendfile` 减少数据拷贝 |
| **物理偏移量** | 消息位置用 CommitLog 的物理偏移量标识，精确查找 |

### 3.3 NameServer（轻量级路由中心）

| 特性 | 说明 |
|------|------|
| **无状态** | 不存数据，不选举，互不通信 |
| **去中心化** | 每个 Broker 向**所有** NameServer 注册 |
| **最终一致** | Broker 定时心跳上报，NameServer 仅内存存储 |
| **不可用影响** | NameServer 挂了不影响已有的连接，只影响新建立连接 |

NameServer 和 ZooKeeper 的对比：

| 维度 | NameServer | ZooKeeper |
|------|-----------|-----------|
| 一致性 | AP（可用性优先） | CP（一致性优先） |
| 选举 | 不需要 | 需要 |
| 复杂度 | 低 | 高 |
| RocketMQ 使用方式 | 内置依赖 | 不需要 |

---

## 4. Topic 与消息类型

### 4.1 Topic 管理

```bash
# 查看所有 Topic
./mqadmin topicList -n localhost:9876

# 创建 Topic
./mqadmin updateTopic -n localhost:9876 \
  -t OrderTopic \
  -b localhost:10911 \
  -w 8 \      # 写队列数
  -r 8        # 读队列数

# 查看 Topic 详情
./mqadmin topicStatus -n localhost:9876 -t OrderTopic

# 删除 Topic
./mqadmin deleteTopic -n localhost:9876 -t OrderTopic
```

### 4.2 Tag（消息子标签）

RocketMQ 特有功能：Topic 下的二级分类，消费者端 Broker 直接过滤，不需要的消息根本不拉。

```python
from rocketmq.client import Message

# 生产者：打 Tag
msg = Message(
    topic="OrderTopic",
    tags="pay_success",       # Tag ← 消息子分类
    keys="orderId_12345",     # Key
    body="订单已支付".encode('utf-8')  # 消息体
)

# 消费者：按 Tag 过滤（Broker 端过滤，不拉不需要的消息！）
consumer.subscribe("OrderTopic", "pay_success || refund_success")
# Consumer 只会收到 pay_success 和 refund_success 这两类消息
```

### 4.3 Message Queue（队列粒度）

```
Topic "OrderTopic"
├── Message Queue 0 ← 一个分区
├── Message Queue 1
├── Message Queue 2
└── Message Queue 3

每个队列和 Kafka 的 Partition 类似：
- 同一队列的消息顺序消费
- 不同队列并行消费
- 每个消费者组内，一个队列只被一个消费者占用
```

---

## 5. 生产者 (Producer)

### 5.1 发送消息

**Python 客户端：**

```python
from rocketmq.client import Producer, Message

# 1. 创建生产者
producer = Producer("order-producer-group")
producer.set_namesrv_addr("localhost:9876")
producer.start()

# 2. 构建消息
msg = Message(
    topic="OrderTopic",       # Topic
    tags="pay_success",       # Tag
    keys="order_12345",       # Key（用于查询消息）
    body="订单已支付".encode('utf-8')  # Body（bytes）
)

# 设置用户属性（可选，用于 SQL 过滤）
msg.set_property("order_id", "12345")
msg.set_property("amount", "299.00")

try:
    # 同步发送（等待确认，可靠性最高）
    result = producer.send_sync(msg)
    print(f"发送成功: msgId={result.msg_id}, queueId={result.send_status}")

except Exception as e:
    # 发送失败处理（重试或落库）
    print(f"发送失败: {e}")
    # 落库兜底
    save_to_backup_db(msg)

# 3. 关闭
producer.shutdown()
```

### 5.2 四种发送方式

| 方式 | 特点 | 场景 |
|------|------|------|
| **同步发送** | 等待 Broker 确认 | 重要消息，如订单、支付 |
| **异步发送** | 不阻塞，回调通知 | 高吞吐，如日志 |
| **单向发送** | 发了不管 | 可丢场景，如心跳 |
| **批量发送** | 多条打包一次发 | 高吞吐，如批量同步 |

```python
# 异步发送
def on_success(result):
    print(f"发送成功: {result.msg_id}")

def on_error(exc):
    print(f"发送失败: {exc}")

producer.send_async(msg, on_success, on_error)

# 单向发送（不关心结果）
producer.send_oneway(msg)

# 批量发送
msgs = [
    Message("OrderTopic", "TagA", "order1", b"body1"),
    Message("OrderTopic", "TagB", "order2", b"body2"),
    Message("OrderTopic", "TagC", "order3", b"body3"),
]
result = producer.send_sync(msgs)
```

### 5.3 消息队列选择机制

```python
# RocketMQ 消息落到哪个队列？

# 默认：轮询（顺序消费场景别用）
# 消息在队列间轮询，保证队列负载均衡
msg = Message("OrderTopic", "TagA", body=b"data")

# 指定队列：同 Key 进同一队列（顺序消费用这个）
def select_queue(queues, msg, arg):
    order_id = arg
    index = hash(order_id) % len(queues)
    return queues[index]

producer.send_orderly_with_sharding_key(
    msg,
    sharding_key=str(order_id),  # 相同 key → 同一队列
)
```

---

## 6. 消费者 (Consumer)

### 6.1 Push 消费（推荐）

```python
from rocketmq.client import PushConsumer

# Push 消费：Broker 推送，RocketMQ 控制拉取节奏
consumer = PushConsumer("order-consumer-group")
consumer.set_namesrv_addr("localhost:9876")

# 订阅（按 Tag 过滤）
consumer.subscribe("OrderTopic", "pay_success || refund_success")

# 注册回调函数
def handle_message(msg):
    try:
        body = msg.body.decode('utf-8')
        print(f"消费: {body}")

        # 处理业务...
        process_order(msg)

    except Exception as e:
        print(f"消费失败: {e}")
        # 返回 RECONSUME_LATER → 消息重新入队
        return False  # False = RECONSUME_LATER

    # 返回 True = SUCCESS
    return True

consumer.set_callback(handle_message)

# 启动消费
consumer.start()

# 保持进程运行
import time
try:
    while True:
        time.sleep(60)
except KeyboardInterrupt:
    consumer.shutdown()
```

### 6.2 消费模式

| 模式 | 说明 |
|------|------|
| **集群消费**（默认） | 同组内竞争消费，一条消息只被一个人消费 |
| **广播消费** | 同组内每个消费者都能收到同一条消息 |

```python
from rocketmq.client import PushConsumer

# 集群消费（默认）：一条消息只被组内一个消费者消费
consumer = PushConsumer("group")
consumer.set_message_model("CLUSTERING")   # 集群模式

# 广播消费：一条消息会被组内所有消费者消费
consumer = PushConsumer("group")
consumer.set_message_model("BROADCASTING") # 广播模式
```

### 6.3 消息过滤

```python
# 方式 1：Tag 过滤（推荐，Broker 端过滤，不拉不需要的消息）
consumer.subscribe("OrderTopic", "pay_success || pay_failed")

# 方式 2：SQL92 表达式过滤（更灵活，需 Broker 开启 enablePropertyFilter=true）
consumer.subscribe("OrderTopic", "*")
consumer.set_message_selector_type("SQL92")
consumer.set_message_selector_expression("amount > 100 AND city = 'beijing'")

# 生产者需要先 set_property
# msg.set_property("amount", "299")
# msg.set_property("city", "beijing")
```

### 6.4 消费重试与死信队列

RocketMQ 的消费重试机制是其可靠性保障的核心：

```
消费失败 → 回调返回 False
    │
    ▼
消息重新入队（延时等级递增）
    │
    ▼
重试 16 次后仍失败 → 进入死信队列（DLQ）
```

```python
def handle_message(msg):
    try:
        process(msg)
        return True  # SUCCESS
    except Exception:
        return False  # RECONSUME_LATER → 重试

# 重试延迟等级
# 1s → 5s → 10s → 30s → 1m → 2m → 3m → 4m → 5m → 6m → 7m → 8m →
# 9m → 10m → 20m → 30m → 1h → 2h
# 16 次重试后进入死信队列

# 死信队列命名规则
# %DLQ% + ConsumerGroupName
# 例：%DLQ%order-consumer-group

# 消费死信队列（人工处理失败的消息）
consumer.subscribe("%DLQ%order-consumer-group", "*")
```

---

## 7. 顺序消息

### 7.1 什么是顺序消息？

RocketMQ 支持**全局有序**（非常少见）和**分区有序**（常用）。

```
场景：订单状态流转
待支付 → 已支付 → 已发货 → 已签收

这三条消息必须按顺序处理，不能先处理"已签收"再处理"已支付"。
```

### 7.2 分区有序（常用）

```python
from rocketmq.client import Producer, PushConsumer

# 生产者：同订单 ID 的消息发送到同一个队列
# 使用 send_orderly_with_sharding_key
producer.send_orderly_with_sharding_key(
    msg,
    sharding_key=str(order_id),   # 相同 key → Hash 到同一队列
)

# 消费者：用顺序消费（consumer 的 callback 会按队列串行化）
def handle_order_message(msg):
    process_order_message(msg)
    return True  # 有序回调中返回 SUCCESS

# 注意：同一个 MessageQueue 内的消息会被串行调用
# 底层通过分布式锁保证同一队列内串行消费
```

**顺序消息 key 两点：**
1. 生产者：同一业务 ID → 同一队列（用 `send_orderly_with_sharding_key`）
2. 消费者：同队列消息串行消费（RocketMQ 内部保证）

---

## 8. 延迟消息

### 8.1 RocketMQ 原生支持延迟消息

这是 RocketMQ 相比 Kafka 的一个重要优势。

```python
from rocketmq.client import Message

# 延迟消息：30 分钟后检查支付状态
msg = Message(
    topic="OrderTopic",
    tags="check_pay",
    keys=str(order_id),
    body="检查支付状态".encode('utf-8'),
)
# 设置延迟等级：level 16 = 30 分钟
msg.set_delay_time_level(16)

producer.send_sync(msg)
```

### 8.2 延迟等级对照表

| Level | 延迟时间 | 场景 |
|-------|---------|------|
| 1 | 1s | - |
| 2 | 5s | 快速重试 |
| 3 | 10s | - |
| 4 | 30s | - |
| 5 | 1m | - |
| 6 | 2m | - |
| 7 | 3m | - |
| 8 | 4m | - |
| 9 | 5m | - |
| 10 | 6m | - |
| 11 | 7m | - |
| 12 | 8m | - |
| 13 | 9m | - |
| 14 | 10m | - |
| 15 | 20m | - |
| 16 | 30m | 支付超时检查 |
| 17 | 1h | 订单超时取消 |
| 18 | 2h | 长时间延迟 |

### 8.3 延迟消息典型场景

```
场景 1：订单超时取消
  创建订单 → 30 分钟后检查支付状态 → 未支付则取消

场景 2：延迟通知
  注册成功 → 3 天后发"欢迎回来"短信

场景 3：定时对账
  交易完成 → 1 小时后自动对账
```

---

## 9. 事务消息

### 9.1 什么是事务消息？

RocketMQ 的**杀手级功能**，解决分布式事务的最终一致性。

```
场景：下单 + 扣库存

错误做法：
  1. 下单成功 → 发消息让库存扣
  2. 但发消息可能失败！→ 数据不一致

RocketMQ 事务消息：
  1. 先发"半消息"给 Broker（此时消费者不可见）
  2. 执行本地事务（下单）
  3. 本地事务成功 → 提交半消息（消费者可见）
  4. 本地事务失败 → 回滚半消息（消费者永远看不到）
```

### 9.2 完整实现

```python
from rocketmq.client import TransactionMQProducer, TransactionStatus, Message

class OrderTransactionListener:
    """事务消息监听器"""

    def execute_local_transaction(self, msg, arg):
        """执行本地事务"""
        order_id = arg
        try:
            # 下单入库（本地数据库事务）
            order_service.create_order(order_id)
            return TransactionStatus.COMMIT  # 提交 → 消息可消费
        except Exception:
            return TransactionStatus.ROLLBACK  # 回滚 → 消息丢弃

    def check_local_transaction(self, msg):
        """回查本地事务状态（半消息长时间未确认时触发）"""
        order_id = msg.properties.get('order_id')
        try:
            order_exists = order_service.exists(order_id)
            return TransactionStatus.COMMIT if order_exists else TransactionStatus.ROLLBACK
        except Exception:
            return TransactionStatus.UNKNOWN  # 等下次回查

# 创建事务生产者
producer = TransactionMQProducer("transaction-producer-group")
producer.set_namesrv_addr("localhost:9876")
producer.set_transaction_listener(OrderTransactionListener())
producer.start()

# 发送事务消息
msg = Message(
    topic="OrderTopic",
    tags="create_order",
    body=f"order:{order_id}".encode('utf-8'),
)
msg.set_property('order_id', str(order_id))

result = producer.send_message_in_transaction(msg, arg=str(order_id))
print(f"事务消息发送结果: {result}")
```

### 9.3 事务消息流程

```
  Producer                Broker                Consumer
     │                      │                      │
     │── 1. 发送半消息 ────▶│ （暂存，不可见）      │
     │                      │                      │
     │── 2. 执行本地事务 ── │                      │
     │                      │                      │
     │── 3. 提交/回滚 ────▶│                      │
     │                      │── 提交后可见 ──────▶│
     │                      │                      │
     │ （异常：长时间未确认）  │                      │
     │ ◀── 4. 回查状态 ─────│                      │
     │── 5. 确认提交/回滚 ─▶│                      │
```

---

## 10. 消息可靠性

### 10.1 消息不丢的全链路保障

| 阶段 | 保障方式 |
|------|---------|
| **生产端** | 同步发送 + 重试 + 失败落库 |
| **Broker 端** | 同步刷盘 + 主从同步复制 |
| **消费端** | 消费成功才返回 SUCCESS，失败重试 16 次 |

```python
# Producer：同步发送 + 重试
producer.set_retry_times(3)             # 最多重试 3 次
producer.set_send_msg_timeout(3000)     # 超时 3s

# 失败落库（兜底）
try:
    result = producer.send_sync(msg)
except Exception as e:
    # 落库到数据库，定时补偿发送
    message_backup_db.save({
        'topic': msg.topic,
        'tags': msg.tags,
        'keys': msg.keys,
        'body': msg.body,
        'created_at': datetime.now(),
    })
```

```properties
# Broker 刷盘策略（broker.conf）
# ASYNC_FLUSH：异步刷盘（默认，性能高，可能丢少量）
# SYNC_FLUSH：同步刷盘（不丢，性能低）
flushDiskType = SYNC_FLUSH

# 主从复制策略
# ASYNC_MASTER：异步复制（默认）
# SYNC_MASTER：同步复制（不丢，等 Slave ACK）
brokerRole = SYNC_MASTER
```

### 10.2 消费幂等

RocketMQ 保证 **At least once**，业务层需做幂等处理：

```python
import redis

r = redis.Redis(host='localhost', port=6379, db=0)

def handle_message(msg):
    biz_id = msg.keys  # 业务唯一 ID
    key = f"msg:consumed:{biz_id}"

    # 幂等检查
    if r.exists(key):
        print(f"重复消息，跳过: {biz_id}")
        return True  # 已消费，跳过

    try:
        # 处理业务
        process_business(msg)

        # 标记已消费（24 小时过期）
        r.setex(key, 86400, '1')
        return True  # SUCCESS
    except Exception as e:
        print(f"处理失败: {e}")
        return False  # RECONSUME_LATER
```

---

## 11. 运维管理

### 11.1 查看集群状态

```bash
# 查看 NameServer 注册的 Broker
./mqadmin clusterList -n localhost:9876

# 查看所有 Topic
./mqadmin topicList -n localhost:9876

# 查看某个 Topic 的队列分布
./mqadmin topicStatus -n localhost:9876 -t OrderTopic

# 查看消费者组列表
./mqadmin consumerProgress -n localhost:9876 -g order-consumer-group

# 查看消息积压（diff 列）
./mqadmin consumerProgress -n localhost:9876
```

### 11.2 消息查询

```bash
# 按 Key 查询消息（精确）
./mqadmin queryMsgByKey -n localhost:9876 -t OrderTopic -k order_12345

# 按 UniqueId 查询（精确到一条）
./mqadmin queryMsgByUniqueId -n localhost:9876 -i C0A8019300002A9F0000000000000000

# 按 Topic + 时间查消息
./mqadmin queryMsgByTopic -n localhost:9876 -t OrderTopic
```

### 11.3 消费进度管理

```bash
# 重置消费位点（回溯消费）
./mqadmin resetOffsetByTime -n localhost:9876 \
  -g order-consumer-group \
  -t OrderTopic \
  -s 2024-06-01#00:00:00:000

# 跳过积压消息
./mqadmin skipAccumulatedMessage -n localhost:9876 \
  -g order-consumer-group \
  -t OrderTopic
```

---

## 12. 监控与排查

### 12.1 常见问题

| 问题 | 现象 | 原因 | 解决方案 |
|------|------|------|---------|
| **消息积压** | diff 值持续增长 | 消费速度跟不上 | 加消费者实例、优化消费逻辑 |
| **重复消费** | 同一消息处理多次 | 回调返回 False | 业务层做幂等 |
| **发送失败** | send timeout | Broker 繁忙或网络问题 | 增加重试次数、检查 Broker |
| **NameServer 连接不上** | 客户端报错 | NameServer 不可用 | 检查 NameServer 进程 |
| **死信队列堆积** | 重试 16 次仍失败 | 业务逻辑有 bug | 修复 bug 并手动处理死信 |
| **消费不均衡** | 某队列 diff 很大 | 消息队列 hash 不均匀 | 检查 Key 的分布 |

### 12.2 Broker 日志排查

```bash
# Broker 日志位置
tail -f ~/logs/rocketmqlogs/broker.log

# 关键搜索词
grep "ERROR" broker.log | tail -20     # 最近错误
grep "STATE" broker.log                # Broker 状态变更
grep "PUT Message" broker.log          # 消息写入确认
grep "PULL Message" broker.log         # 消息拉取确认
```

### 12.3 消费端日志排查

```bash
# Consumer 日志
tail -f ~/logs/rocketmqlogs/consumer.log

# 关键搜索词
grep "rebalance" consumer.log          # Rebalance 日志
grep "RECONSUME_LATER" consumer.log    # 重试消息
grep "CONSUME_SUCCESS" consumer.log    # 消费成功
```

### 12.4 RocketMQ Dashboard（推荐）

Dashboard 能直观看到：

- **Cluster 页**：Broker 状态、TPS、主从同步延迟
- **Topic 页**：各 Topic 的消息量、TPS
- **Consumer 页**：消费进度、积压量（LAG）、消费 TPS
- **Message 页**：按 Key/Topic 精确查询消息内容

---

## 13. RocketMQ vs Kafka 选型

### 13.1 核心差异

| 维度 | RocketMQ | Kafka |
|------|----------|-------|
| **吞吐量** | 十万级 TPS | 百万级 TPS |
| **延迟** | 毫秒级 | 毫秒级 |
| **事务消息** | ✅ **原生支持**，分布式事务利器 | ⚠️ 支持（2.0+）但使用复杂 |
| **延迟消息** | ✅ **原生 18 级延迟** | ❌ 需插件或自己实现 |
| **顺序消息** | ✅ 全局 + 分区有序 | 仅分区内有序 |
| **消息过滤** | ✅ Tag / SQL 表达式（Broker 端） | ❌ 客户端自己过滤 |
| **存储设计** | CommitLog 统一顺序写 | 每分区独立顺序写 |
| **路由中心** | NameServer（无状态、轻量） | ZooKeeper / KRaft |
| **生态** | 阿里系生态 | **Apache 大数据生态**（事实标准） |
| **运维复杂度** | 较低 | 中等 |

### 13.2 选型决策树

```
                         你的场景是？
                            │
          ┌─────────────────┼─────────────────┐
          ▼                 ▼                  ▼
    大数据/日志/       业务异步/订单/        超低延迟/
    流计算            分布式事务            IoT
          │                 │                  │
          ▼                 ▼                  ▼
       Kafka            RocketMQ            MQTT Broker
                                             (EMQX 等)

具体判断：

1. 需要 百万 TPS？ → Kafka
2. 需要 事务消息 / 延迟消息？ → RocketMQ
3. 需要对接 Flink/Spark/大数据管道？ → Kafka
4. 需要严格顺序消息？ → RocketMQ
5. 电商/金融 业务场景？ → RocketMQ
6. 已有阿里云/Apache Flink 生态？ → RocketMQ

两者都不差，选型看生态和业务需求。
```

### 13.3 Python API 快速对比

| 操作 | RocketMQ | Kafka (kafka-python) |
|------|----------|-------|
| 同步发送 | `producer.send_sync(msg)` | `future = producer.send(...); future.get()` |
| 异步发送 | `producer.send_async(msg, on_success, on_error)` | `future.add_callback(...).add_errback(...)` |
| 事务消息 | `TransactionMQProducer` | `producer.init_transactions()` |
| 延迟消息 | `msg.set_delay_time_level(16)` | ❌ 不支持原生 |
| 顺序消费 | `send_orderly_with_sharding_key` | 单分区 |
| 消息过滤 | `consumer.subscribe("topic", "tag")` | ❌ 客户端自行过滤 |

---

## 速查卡片

### 快速入门

```python
# === 安装 ===
# pip install rocketmq-client-python

# === 生产者 ===
from rocketmq.client import Producer, Message

producer = Producer("group")
producer.set_namesrv_addr("localhost:9876")
producer.start()

msg = Message("Topic", "Tag", "Key", b"body")
result = producer.send_sync(msg)

producer.shutdown()


# === 消费者 ===
from rocketmq.client import PushConsumer

consumer = PushConsumer("group")
consumer.set_namesrv_addr("localhost:9876")
consumer.subscribe("Topic", "Tag")

def handle(msg):
    print(msg.body.decode())
    return True  # SUCCESS

consumer.set_callback(handle)
consumer.start()
```

### 消息类型速查

```python
from rocketmq.client import Producer, Message, TransactionMQProducer, TransactionStatus

# 同步消息
result = producer.send_sync(msg)

# 异步消息
producer.send_async(msg, on_success, on_error)

# 顺序消息（相同 sharding_key → 同一队列）
producer.send_orderly_with_sharding_key(msg, sharding_key=str(order_id))

# 延迟消息（level 16 = 30 分钟）
msg.set_delay_time_level(16)
producer.send_sync(msg)

# 事务消息
tx_producer = TransactionMQProducer("tx_group")
tx_producer.set_transaction_listener(listener)  # 必须设置回查逻辑
tx_producer.send_message_in_transaction(msg, arg=str(order_id))
```

### 消费者配置要点

```python
# 消费模式
consumer.set_message_model("CLUSTERING")     # 集群（默认）
consumer.set_message_model("BROADCASTING")   # 广播

# 消费线程数
consumer.set_consume_thread_cnt(20)

# Tag 过滤（推荐）
consumer.subscribe("Topic", "tagA || tagB")

# SQL 过滤
consumer.subscribe("Topic", "*")
consumer.set_message_selector_type("SQL92")
consumer.set_message_selector_expression("amount > 100")
```

### 新手常见错误 Top 5

| # | 错误 | 正确做法 |
|---|------|---------|
| 1 | 消费失败返回 True（SUCCESS） | 返回 False（RECONSUME_LATER），让消费者重试 |
| 2 | 顺序消息设为轮询发送 | 用 `send_orderly_with_sharding_key` 指定分片键 |
| 3 | 事务消息不设回查 | 必须实现 `check_local_transaction` 回查逻辑 |
| 4 | 忘记做消费幂等 | 用业务 Key + Redis 或 DB 去重 |
| 5 | 从不消费死信队列 | 监听 `%DLQ%` 开头的死信 Topic，人工处理 |

---

> **RocketMQ 是金融级业务消息利器，事务消息和延迟消息是它的标志性功能。选择消息队列，先看业务需要什么。**
