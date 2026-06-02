# Kafka 速查手册

> 一份通俗易懂的 Kafka 文档，涵盖日常开发中最常用的操作和概念，适合快速查阅和上手。

---

## 目录

- [1. 基础概念](#1-基础概念)
- [2. 安装与部署](#2-安装与部署)
- [3. 核心架构](#3-核心架构)
- [4. Topic 管理](#4-topic-管理)
- [5. 生产者 (Producer)](#5-生产者-producer)
- [6. 消费者 (Consumer)](#6-消费者-consumer)
- [7. 消费者组与分区分配](#7-消费者组与分区分配)
- [8. 消息可靠性](#8-消息可靠性)
- [9. 性能优化](#9-性能优化)
- [10. 运维管理](#10-运维管理)
- [11. 监控与排查](#11-监控与排查)
- [12. Kafka vs RocketMQ 对比](#12-kafka-vs-rocketmq-对比)

---

## 1. 基础概念

### 1.1 什么是 Kafka？

Kafka 是一个**分布式流处理平台**，由 LinkedIn 开发后捐赠给 Apache 基金会。它既是一个**消息队列**，也是一个**流处理引擎**。

你可以把它理解为一个"超级日志系统"：

- **发消息** = 往日志末尾追加一行
- **收消息** = 从某个位置顺序读取
- **消息不删** = 日志保留一段时间（默认 7 天），过期自动清理

### 1.2 核心术语

| 术语 | 说明 | 类比 |
|------|------|------|
| **Broker** | Kafka 服务节点 | 一台服务器 |
| **Topic** | 消息的逻辑分类 | 日志文件的"主题分类" |
| **Partition** | Topic 的物理分片 | 一个日志文件，可有多个副本 |
| **Producer** | 生产者，发消息 | 写日志的程序 |
| **Consumer** | 消费者，收消息 | 读日志的程序 |
| **Consumer Group** | 消费者组，组内竞争消费 | 多个消费者共享消费进度 |
| **Offset** | 消息在分区中的位置 | 日志的第几行 |
| **Replica** | 分区副本，分布在不同的 Broker | 日志的备份 |
| **Leader** | 分区的主副本，负责读写 | 主本 |
| **Follower** | 备份副本，只同步不读写 | 备份 |
| **ISR** | In-Sync Replicas，与 Leader 同步的副本集合 | 活着的备份 |
| **ZooKeeper / KRaft** | 集群元数据管理 | 集群的大脑 |

### 1.3 Kafka 能做什么？

| 场景 | 说明 | 例子 |
|------|------|------|
| **异步解耦** | 系统间通过消息通信，不直接调用 | 下单 → 发消息 → 仓库/物流/短信独立处理 |
| **削峰填谷** | 请求高峰时消息暂存，消费者慢慢处理 | 秒杀 1 万 QPS → 后端 1 千 QPS 消费 |
| **日志收集** | 收集各服务的日志，统一处理 | 微服务日志 → Kafka → ELK |
| **流计算** | 实时计算消息流 | 用户行为 → Kafka → Flink/Spark → 实时报表 |
| **CDC 数据同步** | 捕获数据库变更，同步到其他系统 | MySQL binlog → Kafka → ClickHouse |

---

## 2. 安装与部署

### 2.1 Python 客户端安装

```bash
pip install kafka-python
```

### 2.2 Docker 快速启动（单机测试）

```bash
# 单节点 Kafka（KRaft 模式，无需 ZooKeeper，Kafka 3.3+）
docker run -d --name kafka \
  -p 9092:9092 \
  -e KAFKA_NODE_ID=1 \
  -e KAFKA_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093 \
  -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092 \
  -e KAFKA_CONTROLLER_LISTENER_NAMES=CONTROLLER \
  -e KAFKA_LISTENER_SECURITY_PROTOCOL_MAP=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT \
  -e KAFKA_CONTROLLER_QUORUM_VOTERS=1@localhost:9093 \
  -e KAFKA_PROCESS_ROLES=broker,controller \
  apache/kafka:latest
```

### 2.3 ZooKeeper 模式（传统部署）

```bash
# docker-compose.yml
version: '3'
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
    ports:
      - "2181:2181"

  kafka:
    image: confluentinc/cp-kafka:latest
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
```

### 2.4 macOS

```bash
brew install kafka
# ZooKeeper 模式
brew services start zookeeper
brew services start kafka
```

---

## 3. 核心架构

### 3.1 整体架构图

```
                    ┌─────────────────────────┐
                    │      Kafka Cluster       │
                    │                          │
 Producer ─────────►│  Broker 1    Broker 2    │─────────► Consumer Group A
 (发送消息)         │  ┌──────┐   ┌──────┐    │           (消费消息)
                    │  │Part 0│   │Part 1│    │
                    │  │Part 2│   │Part 3│    │
                    │  └──────┘   └──────┘    │
                    │                          │
                    │  Broker 3                │
                    │  ┌──────┐                │
                    │  │Part 0│← 副本(Follower) │
                    │  │Part 1│← 副本(Follower) │
                    │  └──────┘                │
                    └─────────────────────────┘
```

### 3.2 Partition（分区）详解

**分区是 Kafka 最核心的概念**，理解分区就能理解 Kafka。

```
Topic "user-events" 有 3 个分区：

Partition 0: [msg1][msg2][msg3]...  ← 有序消息序列
Partition 1: [msg4][msg5][msg6]...
Partition 2: [msg7][msg8][msg9]...
```

| 特性 | 说明 |
|------|------|
| **分区内有序** | 同一分区消息按发送顺序排列 |
| **分区间无序** | 不同分区之间不保证顺序 |
| **并行读写** | 多个分区可并行写入和消费 |
| **水平扩展** | 增加分区数 → 提高吞吐量 |
| **副本保障** | 每个分区有多副本（Leader + Follower） |

### 3.3 数据持久化

```
Broker 磁盘上的分段日志文件：

topic-0/
  ├── 00000000000000000000.log    ← 实际消息数据
  ├── 00000000000000000000.index  ← 偏移量索引（稀疏索引）
  ├── 00000000000000000000.timeindex ← 时间戳索引
  ├── 00000000000000500000.log    ← 第 500000 条后的消息
  ├── 00000000000000500000.index
  └── ...
```

- 消息按 **Segment（分段）** 存储，默认 1GB 一个文件
- 消息**顺序追加写入**，无随机写，这是 Kafka 快的关键
- 数据过期策略：**按时间**（`retention.ms`，默认 7 天）或**按大小**（`retention.bytes`）

---

## 4. Topic 管理

### 4.1 创建 Topic

```bash
# 创建 Topic
kafka-topics.sh --create \
  --bootstrap-server localhost:9092 \
  --topic user-events \
  --partitions 3 \
  --replication-factor 2

# 参数说明
# --partitions 3          → 3 个分区（并行度）
# --replication-factor 2  → 2 个副本（可靠性）
```

```bash
# 创建带清理策略的 Topic
# cleanup.policy=compact：只保留每个 key 的最新一条消息
kafka-topics.sh --create \
  --bootstrap-server localhost:9092 \
  --topic user-latest \
  --partitions 10 \
  --replication-factor 3 \
  --config cleanup.policy=compact \
  --config delete.retention.ms=86400000 \
  --config min.cleanable.dirty.ratio=0.5
```

### 4.2 查看和管理 Topic

```bash
# 列出所有 Topic
kafka-topics.sh --list --bootstrap-server localhost:9092

# 查看 Topic 详情
kafka-topics.sh --describe --bootstrap-server localhost:9092 --topic user-events

# 输出示例：
# Topic: user-events  PartitionCount: 3  ReplicationFactor: 2
#   Partition: 0  Leader: 1  Replicas: 1,3  Isr: 1,3
#   Partition: 1  Leader: 2  Replicas: 2,1  Isr: 2,1
#   Partition: 2  Leader: 3  Replicas: 3,2  Isr: 3,2

# 增加分区（只能增不能减！）
kafka-topics.sh --alter \
  --bootstrap-server localhost:9092 \
  --topic user-events \
  --partitions 6

# 删除 Topic
kafka-topics.sh --delete --bootstrap-server localhost:9092 --topic user-events
```

### 4.3 查看消息详情

```bash
# 查看最早的消息
kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic user-events \
  --from-beginning \
  --max-messages 10

# 查看最新 N 条（从末尾往前）
kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic user-events \
  --offset latest \
  --max-messages 10

# 查看指定分区的消息
kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic user-events \
  --partition 0 \
  --offset 100  # 从 offset=100 开始
```

### 4.4 分区数选择原则

| 场景 | 建议分区数 |
|------|-----------|
| 低吞吐（< 10 MB/s） | 3~6 |
| 中吞吐（10~50 MB/s） | 6~12 |
| 高吞吐（> 50 MB/s） | 12~24 |
| 极限吞吐 | 24~48（单 Topic 一般不超过 200） |

> **注意**：分区数越多 → 资源消耗越大（文件句柄、内存）。分区数只能增加不能减少，创建时慎重。

---

## 5. 生产者 (Producer)

### 5.1 发送消息

**命令行发送：**

```bash
# 从终端发送消息
kafka-console-producer.sh \
  --bootstrap-server localhost:9092 \
  --topic user-events

# 每条消息一行，Ctrl+C 退出
> {"userId": 10001, "event": "page_view", "timestamp": 1717200000}
> {"userId": 10002, "event": "click", "timestamp": 1717200001}
```

**Python 客户端：**

```python
from kafka import KafkaProducer
import json

# 基础配置
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    key_serializer=lambda k: k.encode('utf-8') if k else None,

    # 可靠性配置（重要！）
    acks='all',               # 所有 ISR 确认才算成功
    enable_idempotence=True,  # 幂等，防止重复
    retries=3,                # 重试次数
    max_in_flight_requests_per_connection=5,
)

# 异步发送（推荐）
future = producer.send(
    'user-events',
    key='key1',
    value={'userId': 10001, 'event': 'page_view'},
)
try:
    metadata = future.get(timeout=10)  # 等待确认
    print(f"发送成功: topic={metadata.topic}, partition={metadata.partition}, offset={metadata.offset}")
except Exception as e:
    print(f"发送失败: {e}")

# 带回调的异步发送
def on_send_success(metadata):
    print(f"发送成功: partition={metadata.partition}, offset={metadata.offset}")

def on_send_error(exc):
    print(f"发送失败: {exc}")

future = producer.send('user-events', key='key2', value={'event': 'click'})
future.add_callback(on_send_success)
future.add_errback(on_send_error)

# 同步发送（阻塞等待确认）
future = producer.send('user-events', key='key3', value={'event': 'login'})
try:
    metadata = future.get(timeout=10)
except Exception as e:
    print(f"同步发送失败: {e}")

# 刷新并关闭
producer.flush()
producer.close()
```

### 5.2 消息 Key 的作用

```python
# Key 相同 → 进入同一个分区 → 保证有序
producer.send('user-events', key='userId_10001', value={'event': 'click'})
#                               ↑ 相同 key 哈希到同一分区

# Key 为 None → 轮询分配分区（均匀分布）
producer.send('user-events', value={'event': 'page_view'})

# 自定义分区器（传入 callable）
def custom_partitioner(key, all_partitions, available_partitions):
    if key is None:
        return available_partitions[0]
    return hash(key) % len(available_partitions)

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    partitioner=custom_partitioner,
)
```

### 5.3 acks 参数详解

| acks | 含义 | 可靠性 | 性能 |
|------|------|--------|------|
| **0** | 不等确认，发了就算 | 极低（可能丢） | 最高 |
| **1** | Leader 确认即可 | 中（Leader 挂了可能丢） | 较高 |
| **all / -1** | 所有 ISR 副本确认 | **最高（推荐）** | 较低 |

```
acks=all 的执行流程：

Producer → [Broker 1 (Leader)] → [Broker 2 (Follower/ISR)] → [Broker 3 (Follower/ISR)]
                          ↓ 所有 ISR 写入成功后                        ↓
                         向 Producer 返回 ACK ✅
```

### 5.4 幂等与事务

```python
# 1. 幂等生产（enable_idempotence=True）
#   自动去重：相同 Producer 发送的重复消息只会被写入一次
#   非事务场景下的防重首选

# 2. 事务生产（跨分区/跨 Topic 原子写入）
#   需要指定 transactional_id
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    transactional_id='my-transactional-id',  # 开启事务
    enable_idempotence=True,
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
)

producer.init_transactions()
try:
    producer.begin_transaction()
    producer.send('topicA', key='key', value={'data': 'valueA'})
    producer.send('topicB', key='key', value={'data': 'valueB'})
    producer.commit_transaction()
    print("事务提交成功")
except Exception as e:
    producer.abort_transaction()
    print(f"事务回滚: {e}")
# 要么两个消息都成功，要么都不成功
```

---

## 6. 消费者 (Consumer)

### 6.1 消费消息

**命令行消费：**

```bash
# 从头开始消费
kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic user-events \
  --from-beginning
```

**Python 客户端：**

```python
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'user-events',
    bootstrap_servers='localhost:9092',
    group_id='user-event-consumer-group',  # 消费者组 ID
    auto_offset_reset='earliest',          # 无 offset 时从头开始
    enable_auto_commit=False,              # 关闭自动提交（推荐手动）

    key_deserializer=lambda k: k.decode('utf-8') if k else None,
    value_deserializer=lambda v: json.loads(v.decode('utf-8')),
    max_poll_records=500,                  # 每次最多拉 500 条
)

try:
    while True:
        # poll 拉取消息
        records = consumer.poll(timeout_ms=1000, max_records=100)
        for topic_partition, messages in records.items():
            for msg in messages:
                print(f"offset={msg.offset}, key={msg.key}, value={msg.value}")
                # 处理消息...
                process_message(msg.value)

        # 处理完后手动提交 offset（推荐）
        consumer.commit()
except KeyboardInterrupt:
    pass
finally:
    consumer.close()
```

### 6.2 消费模式对比

| 模式 | 说明 | 适用场景 |
|------|------|---------|
| **subscribe（订阅）** | 加入消费者组，自动分配分区 | **推荐**，自动负载均衡 |
| **assign（指定）** | 手动指定消费哪个分区 | 特殊场景，精确控制 |
| **seek（定位）** | 从指定 offset 开始消费 | 消息回溯、重放 |

```python
from kafka import TopicPartition, OffsetAndTimestamp

# 订阅模式（推荐）
consumer.subscribe(['user-events'])

# 指定分区模式
tp = TopicPartition('user-events', 0)
consumer.assign([tp])

# seek 定位到指定 offset（消息回溯）
consumer.seek(tp, 1000)  # 跳到 offset=1000

# 根据时间定位（回溯到某个时间点）
import datetime
target_time = int(datetime.datetime(2024, 6, 1, 10, 0).timestamp() * 1000)

# 先分配分区
consumer.assign([tp])
consumer.poll(timeout_ms=1000)  # 确保分区已分配

# 按时间查找 offset
timestamps = {tp: target_time}
offset_result = consumer.offsets_for_times(timestamps)
if offset_result[tp]:
    consumer.seek(tp, offset_result[tp].offset)
```

### 6.3 Offset 管理

```
Kafka 的 Offset 消费进度由消费者自己管理：

auto.offset.reset = earliest  → 无 offset 时从最旧消息开始（第一次消费）
auto.offset.reset = latest    → 无 offset 时从最新消息开始（默认，只消费新消息）
auto.offset.reset = none      → 无 offset 时报错
```

```
Offset 提交方式：

1. enable_auto_commit=True（默认，不推荐）
   Kafka 自动每 5 秒提交一次 offset
   缺点：如果处理失败但已提交 → 消息丢失！

2. enable_auto_commit=False + consumer.commit()（推荐）
   手动同步提交，处理完一批再提交
   优点：at-least-once 语义，消息不丢
   缺点：可能重复消费（提交前崩溃 → 重新消费）

3. enable_auto_commit=False + 批量处理完统一提交（高性能）
   攒一批消息后统一 commit
   优点：吞吐高
   缺点：提交间隔大，宕机时重复消费范围更大
```

---

## 7. 消费者组与分区分配

### 7.1 消费者组原理

**消费者组是 Kafka 消费的核心机制**：

```
Topic "user-events" 有 3 个分区

消费者组内有 3 个消费者：
  Consumer A → Partition 0
  Consumer B → Partition 1
  Consumer C → Partition 2
  每个消费者只处理 1 个分区，互不影响

消费者组内有 2 个消费者：
  Consumer A → Partition 0, Partition 1
  Consumer B → Partition 2
  Consumer A 要多处理一个分区

消费者组内有 4 个消费者：
  Consumer A → Partition 0
  Consumer B → Partition 1
  Consumer C → Partition 2
  Consumer D → 空闲！（分区不够分）
```

**两条铁律：**
1. **同一分区只能被同组内的一个消费者消费**
2. **不同组的消费者各自独立消费，互不影响**

### 7.2 Rebalance（重平衡）

当消费者**加入/退出**时，分区重新分配 → **Rebalance**。

```python
from kafka import KafkaConsumer
from kafka.coordinator.assignors.range import RangePartitionAssignor
from kafka.coordinator.assignors.roundrobin import RoundRobinPartitionAssignor
from kafka.coordinator.assignors.sticky.sticky_assignor import StickyPartitionAssignor

consumer = KafkaConsumer(
    'user-events',
    bootstrap_servers='localhost:9092',
    group_id='my-group',

    # 分区分配策略（推荐 CooperativeSticky，减少暂停时间）
    partition_assignment_strategy=[RoundRobinPartitionAssignor],

    # Rebalance 相关配置
    session_timeout_ms=30000,       # 心跳超时（超过则认为宕机）
    heartbeat_interval_ms=3000,     # 心跳间隔（timeout 的 1/10）
    max_poll_interval_ms=300000,    # 两次 poll 最大间隔（超时触发 Rebalance）
    max_poll_records=500,           # 每次 poll 最大拉取数（太多导致处理超时）
)
```

**避免频繁 Rebalance 的配置：**

| 配置 | 建议值 | 说明 |
|------|--------|------|
| `session_timeout_ms` | 30000 | 消费者心跳超时（超过则认为宕机） |
| `heartbeat_interval_ms` | 3000 | 心跳间隔（session.timeout 的 1/10） |
| `max_poll_interval_ms` | 300000 | 两次 poll 最大间隔（超过触发 Rebalance） |
| `max_poll_records` | 500 | 每次 poll 最大拉取数（太多导致处理超时） |

### 7.3 分区分配策略

```python
from kafka.coordinator.assignors.roundrobin import RoundRobinPartitionAssignor
from kafka.coordinator.assignors.range import RangePartitionAssignor
from kafka.coordinator.assignors.sticky.sticky_assignor import StickyPartitionAssignor

# RoundRobin：轮询分配，均匀
consumer = KafkaConsumer(
    partition_assignment_strategy=[RoundRobinPartitionAssignor],
)

# Range（默认）：按 Topic 范围分配，可能不均衡
consumer = KafkaConsumer(
    partition_assignment_strategy=[RangePartitionAssignor],
)

# Sticky：粘性分配，尽量保持原分配
consumer = KafkaConsumer(
    partition_assignment_strategy=[StickyPartitionAssignor],
)

# CooperativeSticky（推荐）：增量重平衡，减少暂停时间
# kafka-python 中可用自定义实现或升级到 confluent-kafka-python
# pip install confluent-kafka
# consumer = Consumer({"partition.assignment.strategy": "cooperative-sticky"})
```

---

## 8. 消息可靠性

### 8.1 消息不丢的三板斧

| 阶段 | 保障方式 |
|------|---------|
| **生产端** | `acks='all'` + `enable_idempotence=True` + 重试 |
| **服务端** | `replication.factor >= 3` + `min.insync.replicas >= 2` + `unclean.leader.election.enable=false` |
| **消费端** | 手动提交 offset，**先处理消息，再提交 offset** |

```bash
# 服务端配置（server.properties）
default.replication.factor=3             # 默认副本数 3
min.insync.replicas=2                    # 最少 2 个 ISR 副本确认
unclean.leader.election.enable=false     # 不允许非 ISR 副本成为 Leader
```

### 8.2 三种消息语义

| 语义 | 含义 | 实现方式 |
|------|------|---------|
| **At most once** | 最多一次（可能丢） | `enable_auto_commit=True` |
| **At least once** | 至少一次（可能重） | `enable_auto_commit=False` + 先处理后提交 |
| **Exactly once** | 精确一次（不丢不重） | 事务 API 或幂等 + 下游去重 |

### 8.3 重复消费处理

Kafka 默认保证 **At least once**，重复消费可能发生在：

1. 消费者处理完消息但**还没提交 offset** → 宕机 → 重启后重新消费
2. 生产者重试发送 → 写入重复消息

**解决方案：**

```python
import redis
r = redis.Redis(host='localhost', port=6379, db=0)

# 方案 1：业务层幂等（推荐）
# 在消费端用 业务ID + Redis 去重
for tp, messages in records.items():
    for msg in messages:
        biz_id = msg.value.get('order_id')  # 业务唯一 ID
        key = f"msg_consumed:{biz_id}"

        if r.set(key, '1', nx=True, ex=86400):  # nx=True = setnx，ex=24h过期
            # 未消费过，处理
            process_message(msg.value)
        else:
            # 已消费，跳过
            print(f"重复消息，跳过: {biz_id}")

# 方案 2：下游支持幂等（UPSERT）
# MySQL: INSERT ... ON DUPLICATE KEY UPDATE
# ClickHouse: ReplacingMergeTree
```

---

## 9. 性能优化

### 9.1 生产者优化

```python
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',

    # 批量发送（提高吞吐的核心）
    batch_size=16384,           # 批量大小（默认 16KB，调大减少请求数）
    linger_ms=5,                # 等待 5ms 攒一批（默认 0，调大吞吐更高）

    # 压缩（减少网络传输）
    compression_type='lz4',     # lz4 性价比最高
    # 可选: None（默认）, 'gzip'（压缩率高但慢）, 'lz4', 'snappy', 'zstd'

    # 内存调大
    buffer_memory=33554432,     # 32MB 缓冲区（默认）
)
```

### 9.2 消费者优化

```python
consumer = KafkaConsumer(
    'user-events',
    bootstrap_servers='localhost:9092',
    group_id='my-group',

    # 提高消费吞吐
    max_poll_records=500,           # 一次拉更多条
    fetch_min_bytes=1024,           # 至少拉 1KB（减少空请求）
    fetch_max_wait_ms=500,          # 等待 500ms 攒到足够数据

    # 消费起始位置
    auto_offset_reset='earliest',   # 从头开始
    # auto_offset_reset='latest',   # 只消费最新的（默认）
)
```

### 9.3 服务端优化

```properties
# server.properties 核心优化

# 顺序写磁盘
log.dirs=/data1/kafka,/data2/kafka     # 多磁盘目录

# 页面缓存（Kafka 严重依赖 OS 的 Page Cache）
# 建议分配一半内存给 Page Cache

# 网络
num.network.threads=8                   # 网络线程数
num.io.threads=16                        # IO 线程数

# 数据保留
log.retention.hours=168                  # 保留 7 天
log.segment.bytes=1073741824             # 1GB 分段
log.roll.hours=24                        # 或每 24 小时分段

# 副本
num.replica.fetchers=4                   # 副本拉取线程数
```

### 9.4 OS 层面优化

```bash
# 文件句柄数
ulimit -n 65536

# 虚拟内存调优
sysctl -w vm.swappiness=1               # 尽量不用 swap（Kafka 依赖 PageCache）
sysctl -w vm.dirty_ratio=20             # 脏页比例

# 磁盘挂载
mount -o noatime /dev/sdb /data/kafka   # noatime 减少磁盘写
```

---

## 10. 运维管理

### 10.1 查看消费者组

```bash
# 查看所有消费者组
kafka-consumer-groups.sh --bootstrap-server localhost:9092 --list

# 查看指定组的消费进度
kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --group user-event-consumer-group --describe

# 输出示例：
# TOPIC        PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG
# user-events  0          100000          100500          500    ← 积压 500 条
# user-events  1          200000          200000          0      ← 无积压
# user-events  2          150000          150100          100    ← 积压 100 条

# 重置 offset（回到最早消息）
kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --group user-event-consumer-group \
  --topic user-events \
  --reset-offsets --to-earliest --execute

# 重置到最新
kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --group user-event-consumer-group \
  --topic user-events \
  --reset-offsets --to-latest --execute
```

### 10.2 数据迁移与平衡

```bash
# 查看分区分布
kafka-log-dirs.sh --bootstrap-server localhost:9092 \
  --topic-list user-events --describe

# Leader 负载均衡（手动触发）
kafka-leader-election.sh --bootstrap-server localhost:9092 \
  --topic user-events --partition 0 --election-type preferred

# 分区重分配：迁到新 Broker
# 1. 生成重分配计划 JSON
# 2. kafka-reassign-partitions.sh --execute
```

### 10.3 监控与告警

```bash
# 查看 Topic 消息积压
kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --group <group_id> --describe | \
  awk '{sum += $6} END {print "Total LAG:", sum}'

# 查看 Under-Replicated 分区（有副本同步延迟）
kafka-topics.sh --bootstrap-server localhost:9092 --describe --under-replicated-partitions

# 查看不可用的分区（无 Leader）
kafka-topics.sh --bootstrap-server localhost:9092 --describe --unavailable-partitions
```

### 10.4 常用管理操作

```bash
# 动态增加分区（只能增）
kafka-topics.sh --bootstrap-server localhost:9092 \
  --alter --topic user-events --partitions 10

# 修改 Topic 配置
kafka-configs.sh --bootstrap-server localhost:9092 \
  --alter --topic user-events \
  --add-config retention.ms=259200000  # 保留 3 天

# 查看 Topic 当前配置
kafka-configs.sh --bootstrap-server localhost:9092 \
  --describe --topic user-events

# 消息总数查看（工具）
kafka-run-class.sh kafka.tools.GetOffsetShell \
  --broker-list localhost:9092 \
  --topic user-events
```

---

## 11. 监控与排查

### 11.1 常见问题

| 问题 | 现象 | 原因 | 解决方案 |
|------|------|------|---------|
| **消息积压** | LAG 持续增长 | 消费速度 < 生产速度 | 加消费者、增加分区、优化消费逻辑 |
| **消费重复** | 同一消息处理多次 | 提交前宕机 | 业务层幂等 |
| **消息丢失** | 应有消息没收到 | acks=0 或 ISR 不足 | acks=all + 副本 >=3 |
| **Rebalance 风暴** | 频繁重分配 | 消费太慢超过 max.poll.interval | 优化消费逻辑、调大超时时间 |
| **磁盘写满** | Broker 不可用 | 数据没及时过期 | 减小 retention.ms、增加磁盘 |
| **分区倾斜** | 某个分区数据量大 | key 分布不均 | 增加分区、调整分区策略 |

### 11.2 Broker 日志排查

```bash
# 查看 Kafka server.log
tail -f /var/log/kafka/server.log

# 常用关键词搜索
grep "is not in the ISR" server.log    # ISR 副本故障
grep "leader election" server.log      # Leader 重新选举
grep "Error" server.log | tail -20     # 最近错误
grep "INFO.*partition" server.log      # 分区操作日志
```

### 11.3 查看 ISR 状态

```bash
# 哪个 Follower 没有跟上
kafka-topics.sh --bootstrap-server localhost:9092 --describe --topic user-events

# 如果 Isr 列表缺少某个 Broker，说明该副本同步落后或离线
# 检查对应 Broker 的网络、磁盘 IO、数据目录
```

---

## 12. Kafka vs RocketMQ 对比

| 维度 | Kafka | RocketMQ |
|------|-------|----------|
| **出身** | LinkedIn → Apache | 阿里巴巴 → Apache |
| **语言** | Java + Scala | Java |
| **最大吞吐** | 百万 TPS | 十万级 TPS |
| **消息可靠性** | 高（需配置） | **极高**（金融级，默认不丢） |
| **事务消息** | 支持（2.0+） | **原生支持**（分布式事务场景） |
| **顺序消息** | 分区内有序 | **严格全局/分区有序** |
| **定时/延迟消息** | 不支持原生（需插件） | **原生支持** 18 个延迟级别 |
| **消息回溯** | 基于 offset | 基于时间/offset |
| **消息过滤** | 不支持（服务端） | 支持 Tag / SQL 表达式过滤 |
| **消息优先级** | 不支持 | 不支持（Kafka 也没有） |
| **依赖外部** | ZooKeeper（3.3+ 可选 KRaft） | NameServer（轻量，无状态） |
| **运维复杂度** | 中（依赖 ZK/KRaft） | 中低（无外部依赖） |
| **生态** | **极其丰富**（大数据生态事实标准） | 中等（阿里生态完善） |

### 选型速查

```
消息队列选型决策树：

需要极致吞吐量？ → Kafka
  场景：日志收集、大数据管道、流计算

需要金融级事务/延迟消息？ → RocketMQ
  场景：电商订单、分布式事务、定时营销

需要低延迟持久化？ → 两者都行
```

---

## 速查卡片

### 常用命令

```bash
# Topic 管理
kafka-topics.sh --create --bootstrap-server localhost:9092 --topic <name> --partitions 3 --replication-factor 2
kafka-topics.sh --list --bootstrap-server localhost:9092
kafka-topics.sh --describe --bootstrap-server localhost:9092 --topic <name>
kafka-topics.sh --delete --bootstrap-server localhost:9092 --topic <name>

# 生产者
kafka-console-producer.sh --bootstrap-server localhost:9092 --topic <name>

# 消费者
kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic <name> --from-beginning
kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic <name> --max-messages 10

# 消费者组
kafka-consumer-groups.sh --bootstrap-server localhost:9092 --list
kafka-consumer-groups.sh --bootstrap-server localhost:9092 --group <group> --describe
```

### 生产者配置三要素

```python
# 可靠性优先（金融、订单）
producer = KafkaProducer(
    acks='all',
    enable_idempotence=True,
    retries=3,
)

# 吞吐优先（日志、埋点）
producer = KafkaProducer(
    batch_size=65536,        # 64KB
    linger_ms=10,            # 攒 10ms
    compression_type='lz4',
)
```

### 消费者配置要点

```python
# 防止消息丢失
consumer = KafkaConsumer(
    'topic',
    enable_auto_commit=False,       # 手动提交
    auto_offset_reset='earliest',   # 从头开始（无 offset 时）
)

# 处理完成后提交
consumer.commit()
```

### 新手常见错误 Top 5

| # | 错误 | 正确做法 |
|---|------|---------|
| 1 | 启用自动提交后处理失败 → 消息丢失 | 关闭自动提交，手动先处理后提交 |
| 2 | 消费者处理太慢导致 Rebalance 风暴 | 减小 max_poll_records 或调大 max_poll_interval_ms |
| 3 | acks=0 → 消息丢失 | 重要业务用 acks='all' |
| 4 | 分区数过少导致消费者空闲 | 分区数 >= 消费者数 |
| 5 | 分区 Key 集中导致数据倾斜 | 选均匀分布的字段做 Key 或设为 None 轮询 |

---

> **Kafka 是大数据管道之王。理解"分区"就理解了 Kafka 的一切。**
