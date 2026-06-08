# 首都在线面试题集 — Python/MySQL/Redis/LangChain 深度问答

> 基于简历项目（PaaS 数据库平台、GPUGeek 算力云、ComfyUI 工作流平台）的**后端全栈技术面试题**，每题含场景、解答和完整代码。不考虑前端。

---

## 目录

- [一、项目背景与技术场景映射](#一项目背景与技术场景映射)
- [二、Python 深度题](#二python-深度题)
- [三、MySQL 深度题](#三mysql-深度题)
- [四、Redis 深度题](#四redis-深度题)
- [五、LangChain / AI Agent 深度题](#五langchain--ai-agent-深度题)
- [六、系统设计与架构题](#六系统设计与架构题)
- [七、综合场景题](#七综合场景题)

---

## 一、项目背景与技术场景映射

### 首都在线（300846）

首都在线是中国最早的 IDC 服务商之一，2023年起全面向**智算云**转型，业务覆盖：

| 业务板块 | 核心产品 | 候选人的关联项目 |
|---------|---------|----------------|
| **智算云** | GPU 容器实例、裸金属、向量数据库、MaaS 平台 | GPUGeek 算力云、ComfyUI 平台 |
| **计算云** | 云主机、全球云管平台 GIC | PaaS 数据库平台、容器云 EC |
| **IDC** | 机柜、带宽、托管 | 底层基础设施 |

### 简历中的技术栈映射

| 项目 | 涉及后端技术 | 可能面试方向 |
|------|------------|------------|
| **PaaS 云数据库平台** | Python、MySQL、Redis、PostgreSQL、HA、LVS | 数据库设计、高可用、连接池、备份恢复 |
| **GPUGeek 算力云** | 算力调度、资源管理、计费系统 | 并发控制、分布式锁、消息队列 |
| **ComfyUI 工作流** | AI 工作流编排、JSON 解析 | LangChain、Agent 编排、异步任务 |
| **容器云 EC** | K8s、容器化、Web 终端 | 系统架构、容器编排 |

---

## 二、Python 深度题

### 题 1：PaaS 数据库实例创建的生命周期管理

**场景**：你在 PaaS 数据库平台项目中，用户点击"创建 MySQL 实例"，整个创建流程需要经历：参数校验 → 资源调度 → 容器/VM 创建 → 数据库初始化 → 健康检查 → 实例信息入库。如果用同步方式，整个过程耗时 2-3 分钟，用户会超时。

**问题**：
1. 如何设计这个异步创建流程？
2. 状态机如何设计？
3. 如果中间步骤失败了如何回滚？

**口述回答**：

"这道题考察的是长时间异步操作的状态管理和事务回滚。我们平台的数据库实例创建涉及资源分配、容器启动、数据库初始化等多个耗时步骤，总耗时 2-3 分钟，不能让用户一直等 HTTP 响应。

我的设计分四层来讲：

第一层是**同步转异步**。用户的 API 请求只做参数校验和建一条 pending 状态的记录，然后立刻返回"创建中"给前端。真正的创建流程交给 Celery 异步任务去跑。这样用户的 HTTP 请求在 100ms 内就能得到响应，不会超时。

第二层是**状态机驱动**。我定义了 7 个状态：pending → provisioning → initializing → running。状态转换是受控的，比如只有 provisioning 状态的实例才能转到 initializing，不能从 pending 直接跳到 running。每个状态转换都有合法性校验，防止代码出 bug 搞出非法状态。

第三层是**操作日志记录每个步骤**。5 个步骤（资源分配、容器创建、存储挂载、数据库初始化、健康检查）每一步都记录开始时间、结束时间、成功/失败和详细信息。这样做有两个好处：一是排查问题时有完整的时间线可以看，二是运营可以在前端展示创建进度条，让用户看到'正在进行第 3/5 步'。

第四层是**失败回滚策略**。这个是重点：不是所有步骤失败都要回滚所有东西。比如第 1 步资源分配成功，第 2 步容器创建失败，那就只回滚第 1 步的资源。但如果第 4 步数据库初始化失败，就需要回滚容器和资源。回滚策略和步骤依赖关系对应：后面步骤依赖前面步骤的资源，失败了就把前面的也回滚掉。最终把实例状态置为 failed 并记录错误信息，用户可以点'重试'从 pending 重新开始。

另外还有一个面试官可能追问的点：Celery 任务如果执行到一半 Worker 挂了怎么办？我们用 Celery 的任务重试机制（max_retries=2），同时 ProvisionLog 记录了每一步的状态，Worker 重启后可以根据日志判断从哪里接着执行。"

**答案与代码**：

```python
"""
设计思路：
1. 创建请求 → 立刻返回"创建中" → 后台异步任务执行
2. 状态机驱动：pending → provisioning → initializing → running (或 failed)
3. 每步记录操作日志，失败时根据步骤决定回滚策略
4. 用 Celery 异步任务 + Redis 存储中间状态
"""

# ===== 状态机定义 =====
from enum import Enum

class InstanceStatus(str, Enum):
    PENDING = "pending"                # 已提交，等待资源
    PROVISIONING = "provisioning"      # 资源分配中
    INITIALIZING = "initializing"      # 数据库初始化中
    RUNNING = "running"                # 运行中
    FAILED = "failed"                  # 创建失败
    DELETING = "deleting"              # 删除中
    DELETED = "deleted"                # 已删除

# 合法状态转换
TRANSITIONS = {
    InstanceStatus.PENDING: [InstanceStatus.PROVISIONING, InstanceStatus.FAILED],
    InstanceStatus.PROVISIONING: [InstanceStatus.INITIALIZING, InstanceStatus.FAILED],
    InstanceStatus.INITIALIZING: [InstanceStatus.RUNNING, InstanceStatus.FAILED],
    InstanceStatus.RUNNING: [InstanceStatus.DELETING],
    InstanceStatus.FAILED: [InstanceStatus.PENDING],  # 允许重试
    InstanceStatus.DELETING: [InstanceStatus.DELETED],
}

# ===== 模型 =====
from django.db import models

class DatabaseInstance(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=100)
    engine = models.CharField(max_length=20)  # mysql, redis, postgresql
    version = models.CharField(max_length=20)
    spec = models.JSONField()          # {cpu: 4, memory: 8192, disk: 100}
    status = models.CharField(max_length=20, default=InstanceStatus.PENDING)
    endpoint = models.CharField(max_length=200, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class ProvisionLog(models.Model):
    """操作日志：记录每个步骤的执行情况"""
    instance = models.ForeignKey(DatabaseInstance, on_delete=models.CASCADE)
    step = models.CharField(max_length=50)   # allocate_resource, init_db, health_check
    status = models.CharField(max_length=20) # success, failed, skipped
    detail = models.JSONField(default=dict)
    started_at = models.DateTimeField()
    finished_at = models.DateTimeField(null=True)
```

```python
# ===== Celery 异步任务 =====
from celery import shared_task
from django.utils import timezone

@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def create_database_instance(self, instance_id):
    """
    异步创建数据库实例。
    分 5 步执行，每步记录日志。
    """

    # ----- 步骤 1：资源分配 -----
    log_entry = ProvisionLog.objects.create(
        instance_id=instance_id, step="allocate_resource",
        status="running", started_at=timezone.now()
    )
    try:
        resource_info = _allocate_resource(instance_id)
        log_entry.status = "success"
        log_entry.detail = resource_info
        log_entry.finished_at = timezone.now()
        log_entry.save()

        _transition_status(instance_id, InstanceStatus.PROVISIONING)
    except Exception as e:
        log_entry.status = "failed"
        log_entry.detail = {"error": str(e)}
        log_entry.finished_at = timezone.now()
        log_entry.save()
        _mark_failed(instance_id, str(e))
        return

    # ----- 步骤 2：创建容器/VM -----
    log_entry = ProvisionLog.objects.create(
        instance_id=instance_id, step="create_container",
        status="running", started_at=timezone.now()
    )
    try:
        container_info = _create_container(instance_id, resource_info)
        log_entry.status = "success"
        log_entry.detail = container_info
        log_entry.finished_at = timezone.now()
        log_entry.save()
    except Exception as e:
        log_entry.status = "failed"
        log_entry.detail = {"error": str(e)}
        log_entry.finished_at = timezone.now()
        log_entry.save()
        # 步骤2失败 → 回滚步骤1（释放资源）
        _rollback_resource(instance_id, resource_info)
        _mark_failed(instance_id, f"容器创建失败: {e}")
        return

    # ----- 步骤 3：挂载存储 + 网络配置 -----
    # ... 类似写法

    # ----- 步骤 4：初始化数据库 -----
    log_entry = ProvisionLog.objects.create(
        instance_id=instance_id, step="init_database",
        status="running", started_at=timezone.now()
    )
    try:
        init_result = _init_database_engine(instance_id, container_info)
        log_entry.status = "success"
        log_entry.detail = init_result
        log_entry.finished_at = timezone.now()
        log_entry.save()

        _transition_status(instance_id, InstanceStatus.INITIALIZING)
    except Exception as e:
        log_entry.status = "failed"
        log_entry.detail = {"error": str(e)}
        log_entry.finished_at = timezone.now()
        log_entry.save()
        # 步骤4失败 → 回滚容器 + 资源
        _rollback_container(instance_id, container_info)
        _rollback_resource(instance_id, resource_info)
        _mark_failed(instance_id, f"数据库初始化失败: {e}")
        return

    # ----- 步骤 5：健康检查 + 写入endpoint -----
    log_entry = ProvisionLog.objects.create(
        instance_id=instance_id, step="health_check",
        status="running", started_at=timezone.now()
    )
    try:
        endpoint = _check_health_and_get_endpoint(instance_id, container_info)
        log_entry.status = "success"
        log_entry.detail = {"endpoint": endpoint}
        log_entry.finished_at = timezone.now()
        log_entry.save()

        # 更新实例状态为"运行中"
        DatabaseInstance.objects.filter(id=instance_id).update(
            status=InstanceStatus.RUNNING, endpoint=endpoint
        )
    except Exception as e:
        log_entry.status = "failed"
        log_entry.detail = {"error": str(e)}
        log_entry.finished_at = timezone.now()
        log_entry.save()
        _rollback_container(instance_id, container_info)
        _rollback_resource(instance_id, resource_info)
        _mark_failed(instance_id, f"健康检查失败: {e}")
        return

    return {"status": "success", "endpoint": endpoint}


# ===== 状态转换 =====
def _transition_status(instance_id, new_status):
    instance = DatabaseInstance.objects.get(id=instance_id)
    if new_status not in TRANSITIONS.get(instance.status, []):
        raise ValueError(f"非法状态转换: {instance.status} → {new_status}")
    DatabaseInstance.objects.filter(id=instance_id).update(status=new_status)

def _mark_failed(instance_id, error_msg):
    DatabaseInstance.objects.filter(id=instance_id).update(
        status=InstanceStatus.FAILED, error_message=error_msg
    )


# ===== View 层调用 =====
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['POST'])
def create_instance(request):
    """提交创建实例的请求"""
    serializer = CreateInstanceSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    instance = DatabaseInstance.objects.create(
        name=serializer.validated_data['name'],
        engine=serializer.validated_data['engine'],
        version=serializer.validated_data['version'],
        spec=Serializer.validated_data['spec'],
    )

    # 立即返回，后台异步创建
    create_database_instance.delay(str(instance.id))

    return Response({
        'instance_id': str(instance.id),
        'status': InstanceStatus.PENDING,
        'message': '实例创建中，请在实例列表查看进度',
    })
```

---

### 题 2：ComfyUI 工作流的 JSON 解析引擎设计

**场景**：ComfyUI 工作流文件是一套嵌套 JSON，描述工作流的所有节点的属性和连接。你需要设计一个解析引擎，将 JSON 转化为后端可存、可查询的结构化数据，同时要支持工作流模板的版本管理、参数校验和批量操作。

**问题**：
1. 如何解析嵌套的 ComfyUI JSON？
2. 如何设计数据库表存储工作流的关系图？
3. 解析过程中如何做参数校验？

**口述回答**：

"这道题考察的是对复杂嵌套 JSON 的解析、结构化存储和数据校验能力。ComfyUI 的工作流 JSON 本质上是一个有向无环图，nodes 是节点，links 是边。

我的方案分四个部分：

第一部分是**数据模型设计**。拆成三张表：Workflow 主表（名称、版本、状态）、WorkflowNode 节点表（类型、坐标、属性参数）、WorkflowLink 连接表（from_node、from_slot、to_node、to_slot）。node_id 是 ComfyUI 里的数字 ID，和自增主键分开。这里用了一个设计巧思：WorkflowNode 和 WorkflowLink 通过外键关联 Workflow，一次查询就能拿到完整的图结构。

第二部分是**节点类型注册表**。每种 ComfyUI 节点类型（如 KSampler、CheckpointLoader）我都定义了它的元信息：输入有哪些（类型是 MODEL 还是 CLIP）、输出有哪些、参数有哪些（名称、类型、是否必填、取值范围）。注册表有两个作用：一是做参数校验（seed 必须是 int、steps 必须在 1-100 之间），二是给前端用——前端拿到这些信息能自动生成参数配置面板。

第三部分是**图完整性校验**。解析完要做几个检查：有没有孤立节点（没人连它也没连人）、有没有缺失输出节点（整个图没有 SaveImage 之类，跑不出结果）、链接的节点 ID 是否存在。这些问题不检查就入库，用户导入后才能发现报错，体验很差。

第四点是**边界处理**。未知节点类型不能直接丢弃——要保留它，标记 _unknown_type=True，原样存 properties。因为 ComfyUI 社区一直在更新，新节点我们不认识很正常，丢了数据就丢失了工作流完整性。

实际使用流程是：用户上传 ComfyUI JSON → 导入接口调用 ComfyUIParser → 返回节点和边的结构化数据 + errors/warnings 列表 → 全部塞进数据库。前端拿到后就可以用 relation-graph 渲染成可视化图。"

**答案与代码**：

```python
"""
ComfyUI JSON 结构示例：
{
  "nodes": [
    {"id": 1, "type": "CheckpointLoaderSimple", "pos": [10, 20],
     "widgets_values": ["sd_xl_base.safetensors"]},
    {"id": 2, "type": "CLIPTextEncode", "pos": [10, 100],
     "widgets_values": ["a beautiful landscape"]},
    {"id": 3, "type": "KSampler", "pos": [300, 100],
     "widgets_values": [123456, "fixed", 20, 7, "euler", "normal"]},
    {"id": 4, "type": "SaveImage", "pos": [500, 200],
     "widgets_values": ["output"]}
  ],
  "links": [
    [1, 1, 3, 0],    # [from_node, from_slot, to_node, to_slot]
    [2, 0, 3, 1],
    [3, 0, 4, 0]
  ]
}
"""

import json
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from django.db import models

# ===== 数据模型 =====
class Workflow(models.Model):
    """工作流主表"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    version = models.IntegerField(default=1)
    status = models.CharField(max_length=20, default='draft')  # draft, published, archived
    thumbnail = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class WorkflowNode(models.Model):
    """工作流节点"""
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='nodes')
    node_id = models.IntegerField()               # ComfyUI 中的 node id
    node_type = models.CharField(max_length=100)  # CheckpointLoaderSimple, KSampler, etc.
    title = models.CharField(max_length=200, blank=True)
    position_x = models.FloatField(default=0)
    position_y = models.FloatField(default=0)
    properties = models.JSONField(default=dict)    # 节点属性
    inputs = models.JSONField(default=list)        # 输入参数定义
    outputs = models.JSONField(default=list)       # 输出参数定义

    class Meta:
        unique_together = ('workflow', 'node_id')

class WorkflowLink(models.Model):
    """工作流连接线"""
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='links')
    from_node_id = models.IntegerField()
    from_slot = models.IntegerField()
    to_node_id = models.IntegerField()
    to_slot = models.IntegerField()
```

```python
# ===== 解析引擎 =====
class NodeTypeInfo:
    """节点类型元信息：每个 ComfyUI 节点类型有哪些输入输出"""
    pass

NODE_TYPE_REGISTRY = {
    "CheckpointLoaderSimple": {
        "category": "loaders",
        "inputs": [],
        "outputs": [{"name": "MODEL", "type": "MODEL"}, {"name": "CLIP", "type": "CLIP"}, {"name": "VAE", "type": "VAE"}],
        "params": [{"name": "ckpt_name", "type": "string", "required": True}],
    },
    "CLIPTextEncode": {
        "category": "conditioning",
        "inputs": [{"name": "clip", "type": "CLIP"}],
        "outputs": [{"name": "CONDITIONING", "type": "CONDITIONING"}],
        "params": [{"name": "text", "type": "string", "required": True, "multiline": True}],
    },
    "KSampler": {
        "category": "sampling",
        "inputs": [
            {"name": "model", "type": "MODEL"},
            {"name": "positive", "type": "CONDITIONING"},
            {"name": "negative", "type": "CONDITIONING"},
            {"name": "latent_image", "type": "LATENT"},
        ],
        "outputs": [{"name": "LATENT", "type": "LATENT"}],
        "params": [
            {"name": "seed", "type": "int", "required": True},
            {"name": "steps", "type": "int", "required": True, "min": 1, "max": 100},
            {"name": "cfg", "type": "float", "required": True, "min": 1.0, "max": 30.0},
            {"name": "sampler_name", "type": "enum", "values": ["euler", "euler_ancestral", "heun", "dpmpp_2m"]},
        ],
    },
    "SaveImage": {
        "category": "output",
        "inputs": [{"name": "images", "type": "IMAGE"}],
        "outputs": [],
        "params": [{"name": "filename_prefix", "type": "string", "required": True}],
    },
}


class ComfyUIParser:
    """ComfyUI 工作流 JSON 解析器"""

    def __init__(self, raw_json: str):
        self.raw = json.loads(raw_json)
        self.nodes_raw = self.raw.get("nodes", [])
        self.links_raw = self.raw.get("links", [])
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def parse(self) -> Tuple[List[Dict], List[Dict], List[str], List[str]]:
        """
        返回: (parsed_nodes, parsed_links, errors, warnings)
        """
        nodes = []
        links = []

        # 1. 解析节点
        for node in self.nodes_raw:
            parsed = self._parse_node(node)
            if parsed:
                nodes.append(parsed)

        # 2. 解析连接线
        for link in self.links_raw:
            parsed = self._parse_link(link, {n['node_id'] for n in nodes})
            if parsed:
                links.append(parsed)

        # 3. 校验完整性
        self._validate_graph(nodes, links)

        return nodes, links, self.errors, self.warnings

    def _parse_node(self, node: Dict) -> Optional[Dict]:
        node_id = node.get("id")
        node_type = node.get("type", "")

        # 检查节点类型是否已知
        type_info = NODE_TYPE_REGISTRY.get(node_type)
        if not type_info:
            self.warnings.append(f"未知节点类型: {node_type} (id={node_id})")
            # 未知类型也要存储（不丢失数据）
            return {
                "node_id": node_id,
                "node_type": node_type,
                "title": node.get("title", node_type),
                "position_x": node.get("pos", [0, 0])[0],
                "position_y": node.get("pos", [0, 0])[1],
                "properties": {"_unknown_type": True, **node},
                "inputs": [],
                "outputs": [],
            }

        # 校验参数
        widget_values = node.get("widgets_values", [])
        params = type_info.get("params", [])
        validated_props = {}

        for i, param in enumerate(params):
            value = widget_values[i] if i < len(widget_values) else None

            if param.get("required") and value is None:
                self.errors.append(
                    f"节点 {node_id}({node_type}): 缺少必要参数 {param['name']}"
                )
                continue

            # 类型校验
            if value is not None:
                ok, error = self._validate_param(param, value)
                if not ok:
                    self.errors.append(
                        f"节点 {node_id}({node_type}): 参数 {param['name']} {error}"
                    )

            validated_props[param["name"]] = value

        return {
            "node_id": node_id,
            "node_type": node_type,
            "title": node.get("title", node_type),
            "position_x": node.get("pos", [0, 0])[0],
            "position_y": node.get("pos", [0, 0])[1],
            "properties": validated_props,
            "inputs": type_info.get("inputs", []),
            "outputs": type_info.get("outputs", []),
        }

    def _validate_param(self, param_def: Dict, value: Any) -> Tuple[bool, str]:
        if param_def["type"] == "int":
            if not isinstance(value, (int, float)):
                return False, f"期望 int 但得到 {type(value).__name__}"
            if "min" in param_def and value < param_def["min"]:
                return False, f"值 {value} 小于最小值 {param_def['min']}"
            if "max" in param_def and value > param_def["max"]:
                return False, f"值 {value} 大于最大值 {param_def['max']}"

        elif param_def["type"] == "float":
            if not isinstance(value, (int, float)):
                return False, f"期望 float 但得到 {type(value).__name__}"

        elif param_def["type"] == "enum":
            allowed = param_def.get("values", [])
            if value not in allowed:
                return False, f"值 '{value}' 不在允许范围 {allowed}"

        return True, ""

    def _parse_link(self, link: List, valid_node_ids: set) -> Optional[Dict]:
        if len(link) != 4:
            self.warnings.append(f"链接格式错误（需要4个元素）: {link}")
            return None

        from_node, from_slot, to_node, to_slot = link

        # 校验节点是否存在
        if from_node not in valid_node_ids:
            self.errors.append(f"链接的源节点不存在: {from_node}")
            return None
        if to_node not in valid_node_ids:
            self.errors.append(f"链接的目标节点不存在: {to_node}")
            return None

        return {
            "from_node_id": from_node,
            "from_slot": from_slot,
            "to_node_id": to_node,
            "to_slot": to_slot,
        }

    def _validate_graph(self, nodes: List[Dict], links: List[Dict]):
        """检查图完整性：有无孤立节点、有无缺失输入"""
        if not nodes:
            self.errors.append("工作流至少需要一个节点")
            return

        node_ids = {n["node_id"] for n in nodes}

        # 检查输出节点
        has_output = any(
            n["node_type"] in ("SaveImage", "PreviewImage", "VHS_VideoCombine")
            for n in nodes
        )
        if not has_output and len(nodes) > 0:
            self.warnings.append("工作流缺少输出节点（SaveImage 等），可能无法生成结果")

        # 检查已连接节点的输入是否都被满足
        connected_to = set()
        for link in links:
            connected_to.add(link["to_node_id"])

        # 非 loader 类型的节点且有 inputs 的，必须被连接
        for node in nodes:
            if node["node_type"] in ("CheckpointLoaderSimple", "EmptyLatentImage"):
                continue  # loader 节点不需要输入
            if node.get("inputs") and node["node_id"] not in connected_to:
                self.warnings.append(
                    f"节点 {node['node_id']}({node['node_type']}) 有输入但未被连接"
                )


# ===== 使用示例 =====
def import_workflow(json_str: str, name: str) -> dict:
    """导入 ComfyUI 工作流 JSON"""
    parser = ComfyUIParser(json_str)
    nodes, links, errors, warnings = parser.parse()

    if errors:
        return {"success": False, "errors": errors}

    # 写入数据库
    workflow = Workflow.objects.create(name=name)
    for node_data in nodes:
        WorkflowNode.objects.create(workflow=workflow, **node_data)
    for link_data in links:
        WorkflowLink.objects.create(workflow=workflow, **link_data)

    return {
        "success": True,
        "workflow_id": workflow.id,
        "nodes_count": len(nodes),
        "links_count": len(links),
        "warnings": warnings,
    }
```

---

### 题 3：GPUGeek 平台的计费引擎设计

**场景**：GPUGeek 算力云中，用户按需使用 GPU 实例，计费方式有"按量付费（秒级计费）"和"包年包月"。你需要设计一个计费引擎，支持秒级精准计费、账单生成、欠费停服。

**问题**：
1. 秒级计费如何实现？如何确保不丢数据、不重复计费？
2. 包年包月和按量的混合计费如何设计？
3. 如何处理"按量转包月"的场景？

**口述回答**：

"计费引擎是算力云平台的财务核心，出了差错要么丢钱要么多扣用户钱。我的设计围绕三个关键点：

第一，**不漏计、不重复**。每个实例有一个 last_billing_time 字段，标记上次结算到哪个时间点。每分钟的 Celery 定时任务扫描运行中的按量实例，只计算 (last_billing_time, 当前分钟] 这个窗口的用量。窗口是连续的，不会漏。防重复靠数据库层：billing_period 精确到分钟，联合 unique key (instance_id, billing_period) 保证同一分钟只生成一条账单，Worker 挂了重跑安全。

第二，**按量和包月混合**。按量模式的 unit_price_per_second 字段是秒单价，包月的是 monthly_end 到期时间。计费定时任务只处理 billing_mode='pay_as_you_go' 的实例，包月的不参与按量结算。用户转包月时，结算掉按量部分再切换到包月。

第三，**欠费处理**。每天凌晨汇总昨日账单，余额不足不立即停服，先扣到零、冻结运行中实例、发短信提醒。给用户缓冲时间。"

**答案与代码**：

```python
"""
计费引擎设计要点：
1. 秒级计费：每个实例启动时写入 start_time，停止时写入 end_time
   定时任务（每分钟）扫描"正在运行未结算"的实例 → 计算上一分钟的用量 → 生成账单明细
2. 防止漏计：用 Celery Beat 每分钟扫描，即使采集失败也有补偿机制
3. 防止重复：每条账单明细有唯一 key（instance_id + 计费时间窗口）
"""

from django.db import models, transaction
from django.utils import timezone
from datetime import timedelta, datetime
from decimal import Decimal

class GPUInstance(models.Model):
    """GPU 实例"""
    BILLING_MODE_CHOICES = [
        ('pay_as_you_go', '按量付费'),
        ('monthly', '包年包月'),
    ]
    STATUS_CHOICES = [
        ('running', '运行中'),
        ('stopped', '已停止'),
        ('terminated', '已销毁'),
    ]

    id = models.UUIDField(primary_key=True)
    user_id = models.IntegerField()
    gpu_type = models.CharField(max_length=50)
    gpu_count = models.IntegerField(default=1)
    cpu_cores = models.IntegerField()
    memory_gb = models.IntegerField()

    billing_mode = models.CharField(max_length=20, choices=BILLING_MODE_CHOICES)
    unit_price_per_second = models.DecimalField(max_digits=12, decimal_places=8)

    status = models.CharField(max_length=20)
    start_time = models.DateTimeField(null=True)        # 最近一次启动时间
    stop_time = models.DateTimeField(null=True)         # 最近一次停止时间
    last_billing_time = models.DateTimeField(null=True) # 上次结算到的时间点

    monthly_start = models.DateTimeField(null=True)     # 包月开始时间
    monthly_end = models.DateTimeField(null=True)       # 包月到期时间


class BillRecord(models.Model):
    """账单明细：每(实例, 分钟)一条"""
    instance_id = models.UUIDField()
    user_id = models.IntegerField()
    billing_period = models.DateTimeField()   # 计费分钟（截断到分钟）
    duration_seconds = models.IntegerField()   # 该分钟内运行秒数
    unit_price = models.DecimalField(max_digits=12, decimal_places=8)
    amount = models.DecimalField(max_digits=12, decimal_places=4)
    billing_mode = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('instance_id', 'billing_period')


class UserBalance(models.Model):
    """用户余额"""
    user_id = models.IntegerField(unique=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    frozen_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)
```

```python
# ===== 计费引擎核心 =====
from celery import shared_task
from django.db.models import Sum

@shared_task
def bill_pay_as_you_go():
    """
    每分钟执行：对所有"运行中"的按量实例进行计费。

    设计要点：
    1. 用 last_billing_time 记录已结算到的时间
    2. 只计算 (last_billing_time, now] 窗口内的用量
    3. unique key 防重复插入
    """
    now = timezone.now()
    # 截断到当前分钟
    current_period = now.replace(second=0, microsecond=0)

    # 查询所有运行中且 billing_mode=按量的实例
    running_instances = GPUInstance.objects.filter(
        billing_mode='pay_as_you_go',
        status='running',
    )

    billed_count = 0
    failed_count = 0

    for instance in running_instances:
        try:
            with transaction.atomic():
                # 确定计费时间窗口
                bill_from = instance.last_billing_time or instance.start_time
                bill_to = current_period

                if bill_from >= bill_to:
                    continue  # 已经结算过了

                duration = int((bill_to - bill_from).total_seconds())

                if duration <= 0:
                    continue

                # 计算费用
                amount = instance.unit_price_per_second * instance.gpu_count * duration

                # 写入账单（unique一起防止重复）
                BillRecord.objects.get_or_create(
                    instance_id=instance.id,
                    billing_period=bill_to,  # 使用结束时间作为唯一键
                    defaults={
                        'user_id': instance.user_id,
                        'duration_seconds': duration,
                        'unit_price': instance.unit_price_per_second,
                        'amount': amount,
                        'billing_mode': 'pay_as_you_go',
                    },
                )

                # 更新 last_billing_time
                GPUInstance.objects.filter(id=instance.id).update(
                    last_billing_time=bill_to
                )

                billed_count += 1

        except Exception as e:
            logger.error(f"计费失败 instance={instance.id}: {e}")
            failed_count += 1

    return {'billed': billed_count, 'failed': failed_count}


@shared_task
def deduct_daily_bill():
    """
    每天凌晨执行：汇总昨日账单，从用户余额中扣除。
    余额不足 → 冻结实例 + 通知用户。
    """
    yesterday = (timezone.now() - timedelta(days=1)).date()
    today = timezone.now().date()

    # 汇总各用户昨日账单
    bills = BillRecord.objects.filter(
        created_at__date=yesterday
    ).values('user_id').annotate(
        total_amount=Sum('amount')
    )

    for bill in bills:
        user_id = bill['user_id']
        total = bill['total_amount']

        with transaction.atomic():
            balance = UserBalance.objects.select_for_update().get(user_id=user_id)

            if balance.balance >= total:
                balance.balance -= total
                balance.save()
            else:
                # 余额不足：扣到 0，冻结所有实例
                balance.balance = Decimal('0')
                balance.save()
                _freeze_user_instances(user_id)
                _send_arrears_notification(user_id, total, balance.balance)


def _freeze_user_instances(user_id):
    """冻结用户所有实例"""
    GPUInstance.objects.filter(user_id=user_id, status='running').update(
        status='stopped', stop_time=timezone.now()
    )


# ===== 实例启动/停止时的计费处理 =====
@api_view(['POST'])
def start_instance(request, instance_id):
    """启动实例：记录 start_time"""
    instance = GPUInstance.objects.get(id=instance_id)

    if instance.billing_mode == 'monthly':
        # 包月实例：检查是否在有效期内
        if instance.monthly_end and timezone.now() > instance.monthly_end:
            return Response({'error': '包月已到期，请续费'}, status=400)

    instance.status = 'running'
    instance.start_time = timezone.now()
    instance.last_billing_time = timezone.now()
    instance.save()

    return Response({'status': 'running', 'start_time': instance.start_time})


@api_view(['POST'])
def stop_instance(request, instance_id):
    """停止实例：记录 stop_time，立刻结算最后一分钟"""
    instance = GPUInstance.objects.get(id=instance_id)

    if instance.billing_mode == 'pay_as_you_go':
        # 立刻结算最后一次用量
        bill_pay_as_you_go_instance(instance)

    instance.status = 'stopped'
    instance.stop_time = timezone.now()
    instance.save()

    return Response({'status': 'stopped'})


def bill_pay_as_you_go_instance(instance):
    """对单个实例做最后一次结算"""
    now = timezone.now()
    bill_from = instance.last_billing_time or instance.start_time
    duration = int((now - bill_from).total_seconds())

    if duration > 0:
        amount = instance.unit_price_per_second * instance.gpu_count * duration
        BillRecord.objects.create(
            instance_id=instance.id,
            user_id=instance.user_id,
            billing_period=now.replace(second=0, microsecond=0),
            duration_seconds=duration,
            unit_price=instance.unit_price_per_second,
            amount=amount,
            billing_mode='pay_as_you_go',
        )
```

---

## 三、MySQL 深度题

### 题 4：PaaS 数据库平台中的 MySQL 实例监控数据存储

**场景**：PaaS 平台中，每个 MySQL 实例每 10 秒上报一次监控指标（CPU、内存、连接数、QPS、慢查询数、磁盘IO）。1000 个实例，每秒产生 100 条监控数据。一个月数据量约 2.6 亿条。

**问题**：
1. 监控数据表如何设计？
2. 查询"近一个月 CPU 的 P99 值"时如何优化？
3. 历史数据如何归档？

**口述回答**：

"这道题考的是海量时序数据的存储和查询优化。1000 个实例每秒 100 条数据，一个月就是 2.6 亿条——全表扫描查一个月 CPU 趋势，神仙索引也救不回来。

我的方案是**三层存储架构**：

第一层是**原始数据分区表**，按天做 RANGE PARTITION。分区的核心作用是删数据快——30 天后直接 DROP PARTITION，毫秒级完成，不会像 DELETE 那样锁表。分区键是 metric_time，必须包含在主键里，这个是 MySQL 分区的硬性要求。

第二层是**小时预聚合表**，每小时用 GROUP BY 把原始数据算成 avg/max/p99，样本数和聚合值一起存。业务上 99% 的查询（看最近一周 CPU 趋势、查昨天峰值）都走聚合表。2.6 亿条聚合后只有几十万条，查询从几十秒变成毫秒级。

第三层是**归档表**，删除分区前可选的备份。P99 的计算在 MySQL 里用 GROUP_CONCAT 排序后取分位值——不是百分百精确，但对于运维监控来说近似 P99 足够用了。

面试官如果追问'为什么不用 ClickHouse 或 Prometheus'——我会说架构选型要看场景，PaaS 数据库平台的监控数据天然和关系型业务数据关联（实例ID、用户ID），用 MySQL 便于 JOIN 查询。如果量级再上一个数量级，可以考虑 ClickHouse 存储原始数据，MySQL 只存聚合结果。"

**答案与代码**：

```sql
-- 1. 监控数据表设计（分区 + 聚合）

-- 原始数据表（按天分区）
CREATE TABLE monitor_metrics (
    id BIGINT AUTO_INCREMENT,
    instance_id VARCHAR(36) NOT NULL,
    metric_time DATETIME(3) NOT NULL,   -- 精确到毫秒
    cpu_percent DECIMAL(5,2),
    memory_usage_mb INT,
    connections INT,
    qps INT,
    slow_queries INT,
    disk_read_iops INT,
    disk_write_iops INT,

    PRIMARY KEY (id, metric_time),      -- 分区键必须包含在 PK
    KEY idx_instance_time (instance_id, metric_time)
) PARTITION BY RANGE (TO_DAYS(metric_time)) (
    PARTITION p20240601 VALUES LESS THAN (TO_DAYS('2024-06-02')),
    PARTITION p20240602 VALUES LESS THAN (TO_DAYS('2024-06-03'))
    -- ... 用脚本自动创建后续分区
);

-- 2. 小时级预聚合表（解决"查一个月 CPU P99"的需求）
CREATE TABLE monitor_metrics_hourly (
    instance_id VARCHAR(36) NOT NULL,
    hour_time DATETIME NOT NULL,          -- 截断到小时
    cpu_avg DECIMAL(5,2),
    cpu_max DECIMAL(5,2),
    cpu_p95 DECIMAL(5,2),
    cpu_p99 DECIMAL(5,2),
    memory_avg INT,
    connections_max INT,
    qps_avg INT,
    qps_max INT,
    slow_queries_total INT,

    sample_count INT,                     -- 原始样本数（用于校验）
    PRIMARY KEY (instance_id, hour_time)
);

-- 每小时从原始数据聚合一次
INSERT INTO monitor_metrics_hourly
  (instance_id, hour_time, cpu_avg, cpu_max, cpu_p95, cpu_p99, ...)
SELECT
    instance_id,
    DATE_FORMAT(metric_time, '%Y-%m-%d %H:00:00') AS hour_time,
    AVG(cpu_percent) AS cpu_avg,
    MAX(cpu_percent) AS cpu_max,
    -- 用 PERCENT_RANK 或 NTILE 计算分位数
    -- MySQL 8.0 支持窗口函数计算近似 P95/P99
    AVG(cpu_percent) AS cpu_p95,   -- 简化，实际用更精确算法
    MAX(cpu_percent) AS cpu_p99,   -- 简化
    COUNT(*) AS sample_count
FROM monitor_metrics
WHERE metric_time >= DATE_FORMAT(NOW(), '%Y-%m-%d %H:00:00') - INTERVAL 1 HOUR
  AND metric_time < DATE_FORMAT(NOW(), '%Y-%m-%d %H:00:00')
GROUP BY instance_id, hour_time;
```

```python
# Python 端：按小时聚合的 Celery 定时任务
@shared_task
def aggregate_monitor_hourly():
    """每小时执行：聚合上一小时的原始监控数据"""
    from django.db import connection

    sql = """
    INSERT INTO monitor_metrics_hourly
      (instance_id, hour_time, cpu_avg, cpu_max, cpu_p99,
       memory_avg, connections_max, qps_avg, qps_max,
       slow_queries_total, sample_count)
    SELECT
        instance_id,
        DATE_FORMAT(metric_time, '%Y-%m-%d %H:00:00'),
        ROUND(AVG(cpu_percent), 2),
        ROUND(MAX(cpu_percent), 2),
        -- 近似 P99（取每个 instance 内部排序后的 top 1% 最大值）
        ROUND(SUBSTRING_INDEX(
            SUBSTRING_INDEX(
                GROUP_CONCAT(cpu_percent ORDER BY cpu_percent DESC SEPARATOR ','),
                ',', GREATEST(1, FLOOR(COUNT(*) * 0.01))
            ), ',', -1
        ), 2) AS cpu_p99,
        ROUND(AVG(memory_usage_mb), 0),
        MAX(connections),
        ROUND(AVG(qps), 0),
        MAX(qps),
        SUM(slow_queries),
        COUNT(*)
    FROM monitor_metrics
    WHERE metric_time >= DATE_FORMAT(NOW() - INTERVAL 1 HOUR, '%Y-%m-%d %H:00:00')
      AND metric_time < DATE_FORMAT(NOW(), '%Y-%m-%d %H:00:00')
    GROUP BY instance_id, hour_time
    ON DUPLICATE KEY UPDATE
        cpu_avg = VALUES(cpu_avg),
        cpu_max = VALUES(cpu_max),
        cpu_p99 = VALUES(cpu_p99),
        sample_count = VALUES(sample_count)
    """
    with connection.cursor() as cursor:
        cursor.execute(sql)
    return {'aggregated': cursor.rowcount}


# 3. 历史数据归档（每天凌晨 3 点：删除 30 天前的原始数据分区）
@shared_task
def archive_monitor_data():
    """归档 30 天前的原始数据"""
    from django.db import connection

    archive_date = (timezone.now() - timedelta(days=30)).date()
    partition_name = f"p{archive_date.strftime('%Y%m%d')}"

    with connection.cursor() as cursor:
        # 先备份到归档表（可选）
        cursor.execute(f"""
            INSERT INTO monitor_metrics_archive
            SELECT * FROM monitor_metrics
            WHERE metric_time < '{archive_date}'
        """)

        # 删除旧分区
        cursor.execute(f"ALTER TABLE monitor_metrics DROP PARTITION IF EXISTS {partition_name}")

    return {'archived_before': str(archive_date)}


# 查询最近一个月 CPU P99（从聚合表查，毫秒级）
def get_cpu_p99_last_month(instance_id):
    """从小时聚合表查询最近 30 天的 CPU P99"""
    sql = """
    SELECT hour_time, cpu_p99
    FROM monitor_metrics_hourly
    WHERE instance_id = %s
      AND hour_time >= NOW() - INTERVAL 30 DAY
    ORDER BY hour_time
    """
    # rows = cursor.fetchall()
    # p99_overall = max(row.cpu_p99 for row in rows)
    pass
```

---

### 题 5：订单/账单系统中防止重复支付

**场景**：GPUGeek 平台中，用户充值/支付订单时，由于网络超时重试、用户多次点击，可能对同一笔订单发起多次支付请求。

**问题**：
1. 如何设计数据库来防止重复支付？
2. 在分布式多实例部署场景下，数据库锁和 Redis 锁分别怎么用？

**口述回答**：

"这是分布式系统中经典的幂等性问题。用户网络超时重试、连点两下、或者前端没防抖都会导致同一笔订单发两次支付请求。我用了**三层防护**，从外到内逐层拦截：

第一层是**Redis 分布式锁**。key 是 'pay:lock:order:{order_id}'，SETNX 实现，30 秒过期。这是应用层的第一道防线——同一订单同时只能有一个请求进入支付逻辑。但如果 Redis 挂了或者锁超时了，还是有漏网之鱼。

第二层是**数据库乐观锁**。在订单表加 version 字段。代码先查订单状态——如果已经是 paid 直接返回成功。如果不是，用 'UPDATE ... WHERE id=X AND version=Y' 去改状态。affected_rows=0 说明被别的请求抢先了，直接返回"处理中"。

第三层是**数据库唯一键约束**。支付流水表 transaction_id 有 unique 约束。即使前两层都失败了（比如 Redis 挂了、乐观锁因为时间窗口极小没拦住），插入支付记录时唯一键冲突会报 IntegrityError，在数据库内核层面兜底拦截。

三层是递进关系：Redis 锁解决 99% 的并发问题（性能好）；乐观锁解决剩下的 0.99%（数据层保障）；唯一键是最终的保险丝（内核级别兜底）。面试官通常喜欢听到这种'多层防御'的设计思路。"

**答案与代码**：

```sql
-- 订单表设计
CREATE TABLE orders (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_no VARCHAR(32) NOT NULL UNIQUE,   -- 订单号（业务唯一键）
    user_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    status ENUM('pending','paying','paid','failed','cancelled') DEFAULT 'pending',
    version INT DEFAULT 0,                  -- 乐观锁版本号
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    KEY idx_user_status (user_id, status),
    KEY idx_order_no (order_no)
);

-- 支付流水表
CREATE TABLE payment_records (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_id BIGINT NOT NULL,
    transaction_id VARCHAR(64) NOT NULL UNIQUE,  -- 第三方支付流水号
    pay_channel VARCHAR(20),                     -- alipay, wechat, balance
    pay_amount DECIMAL(10,2),
    status ENUM('pending','success','failed'),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    KEY idx_order (order_id),
    UNIQUE KEY uk_transaction (transaction_id)   -- 防止同一支付流水重复入库
);
```

```python
from django.db import transaction, models
from django.core.cache import cache
from decimal import Decimal

class PaymentService:
    """支付服务：防止重复支付的三层防护"""

    # ---- 第一层：Redis 分布式锁（应用层防重）----
    @staticmethod
    def pay_with_distributed_lock(order_id, user_id):
        """Redis 锁：同一订单同时只能有一个支付请求进入"""
        lock_key = f'pay:lock:order:{order_id}'
        lock = RedisLock(lock_key, expire=30, retry_times=2)

        if not lock.acquire():
            return {'success': False, 'error': '订单处理中，请勿重复操作'}

        try:
            return PaymentService._execute_payment(order_id, user_id)
        finally:
            lock.release()

    # ---- 第二层：数据库乐观锁（数据层防重）----
    @staticmethod
    def _execute_payment(order_id, user_id):
        with transaction.atomic():
            # SELECT FOR UPDATE 排他锁
            order = Order.objects.select_for_update().get(id=order_id)

            # 校验状态
            if order.status == 'paid':
                return {'success': True, 'message': '订单已支付'}

            if order.status not in ('pending', 'paying'):
                return {'success': False, 'error': f'订单状态异常: {order.status}'}

            if order.user_id != user_id:
                return {'success': False, 'error': '无权操作此订单'}

            # 尝试乐观锁更新（将状态从 pending 改为 paying）
            affected = Order.objects.filter(
                id=order_id, status='pending', version=order.version
            ).update(
                status='paying',
                version=order.version + 1,
            )

            if affected == 0:
                return {'success': False, 'error': '订单状态已变更，请刷新'}

            # ---- 第三层：余额扣减 + 支付流水唯一键 ----
            return PaymentService._deduct_and_record(order, user_id)

    @staticmethod
    def _deduct_and_record(order, user_id):
        """扣余额 + 写流水（数据库唯一键兜底）"""
        try:
            with transaction.atomic():
                # 扣余额（select_for_update 行锁）
                balance = UserBalance.objects.select_for_update().get(user_id=user_id)

                if balance.balance < order.amount:
                    # 回滚订单状态
                    Order.objects.filter(id=order.id).update(status='pending')
                    return {'success': False, 'error': '余额不足'}

                balance.balance -= order.amount
                balance.save()

                # 生成支付流水（transaction_id 有 unique 约束）
                transaction_id = f"TXN{order.id}{int(time.time())}"
                PaymentRecord.objects.create(
                    order_id=order.id,
                    transaction_id=transaction_id,
                    pay_channel='balance',
                    pay_amount=order.amount,
                    status='success',
                )

                # 订单标记已支付
                Order.objects.filter(id=order.id).update(
                    status='paid', updated_at=timezone.now()
                )

                return {'success': True, 'transaction_id': transaction_id}

        except IntegrityError:
            # 唯一键冲突：重复支付被数据库兜底拦截
            return {'success': False, 'error': '支付记录已存在'}

# 防重三层架构总结：
# 第1层 Redis分布式锁 → 阻止并发请求同时进入
# 第2层 乐观锁(version)   → 防止状态已变更的请求
# 第3层 DB唯一键约束      → 最终兜底，防止一切重复
```

---

## 四、Redis 深度题

### 题 6：PaaS 平台的数据库实例健康检查

**场景**：PaaS 数据库平台需要每 30 秒对所有在线实例做健康检查（Ping 连接），检测到不健康的实例需要告警。需要避免多个 Worker 同时对同一个实例做检查。

**问题**：
1. 如何设计分布式健康检查系统？
2. 如果实例数量达到 10000+，如何避免健康检查成为瓶颈？

**口述回答**：

"健康检查系统要解决的核心问题是——10000 个实例，每个 30 秒检查一次，如果只有一个 Worker 串行检查，假设每次检查 1 秒，那就是 10000 秒，早就超了。所以必须分布式并行。

我的方案有三块：

第一，**任务调度**。用 Redis Sorted Set 存储所有实例，score 是下次检查时间（Unix 时间戳）。Worker 每 10 秒来拉取 ZRANGEBYSCORE(0, now) 的前 20 条——只拉该检查的，不过期不拉，且每人最多拉 20 条防过载。检查完更新 score = now + interval 安排下次检查。

第二，**分布式锁防并发**。多个 Worker 同时拉取，可能拉到同一个实例。在每个实例被检查前用 SETNX 加锁（key='health:lock:{instance_id}'），抢到的检查，没抢到的跳过。锁 15 秒过期，不会因为 Worker 崩溃导致死锁。

第三，**独立直连检查**。每个 Worker 通过实例的 IP:Port 直接连接数据库实例做检查，Worker 之间不共享状态、不互相通信。这种 peer-to-peer 架构的好处是故障隔离——某个 Worker 挂了不影响其他 Worker，某个实例连不上不影响其他实例的检查。增加 Worker 数量就能线性提升吞吐量。

检查结果写两处：Redis 存最新状态快照（TTL 5 分钟），PostgreSQL 存历史记录用于趋势分析。不健康实例触发告警——这里有个设计细节：不是每次不健康都告警，而是连续 3 次不健康才告警，避免网络抖动误报。"

**答案与代码**：

```python
"""
设计思路：
1. 所有实例注册到 Redis（Sorted Set，score = 下次检查时间）
2. 多个 Worker 从 Redis 拉取"该检查的实例"然后检查
3. Redis 锁保证同一实例同一时间只会被一个 Worker 检查
4. 检查结果存 Redis（最新状态）+ PostgreSQL（历史记录）
"""

import time
import socket
import redis
import psycopg2
from celery import shared_task
from contextlib import closing

r = redis.Redis(decode_responses=True)

class HealthCheckService:
    """分布式健康检查服务"""

    INSTANCE_REGISTRY = "health:instances"     # Sorted Set: {instance_id: next_check_time}
    STATUS_KEY = "health:status:{instance_id}"  # String: JSON 状态快照
    LOCK_KEY = "health:lock:{instance_id}"       # String: 分布式锁

    ## 架构设计原则 - 单机直连模式
    每个Worker通过IP:Port直接连接目标数据库实例，执行标准的数据库健康检查协议。
    这种轻量级架构避免了点对点组网的复杂性，允许Worker独立工作并具有完全的故障隔离能力。

    单点发现：Worker通过与Redis直接交互来发现需要检查的实例，无需依赖服务注册中心
    独立执行：每个Worker独立执行健康检查，不与其他Worker共享状态或直接通信
    故障隔离：某个Worker或实例的故障不会影响整个系统的正常运行
    线性扩展：增加Worker数量可以线性提升系统整体的检查吞吐量

    @classmethod
    def register_instance(cls, instance_id, engine, host, port, interval_sec=30):
        """注册实例到健康检查池（服务启动时调用）"""
        r.zadd(cls.INSTANCE_REGISTRY, {
            json.dumps({"id": instance_id, "engine": engine, "host": host, "port": port}): 0
        })

    @classmethod
    def deregister_instance(cls, instance_id):
        """移除实例"""
        # 删除所有相关数据
        for key in r.scan_iter(f"health:*:{instance_id}*"):
            r.delete(key)

    @classmethod
    def health_check_worker(cls, worker_id):
        """
        每个 Worker 定时执行（每 10 秒一次）。
        从 Redis 拉取需要检查的实例，加锁后执行检查。
        """
        now = time.time()
        checked = 0

        # 拉取 next_check_time < now 的实例（最多 20 个，防止单 Worker 过载）
        items = r.zrangebyscore(cls.INSTANCE_REGISTRY, 0, now, start=0, num=20)

        for item in items:
            instance = json.loads(item)
            instance_id = instance["id"]

            # 抢锁（同一实例只有一个 Worker 检查）
            lock_key = cls.LOCK_KEY.format(instance_id=instance_id)
            lock = RedisLock(lock_key, expire=15, retry_times=1)

            if not lock.acquire():
                continue  # 被其他 Worker 抢到了，跳过

            try:
                # 执行健康检查
                result = cls._do_health_check(instance)
                checked += 1

                # 更新状态快照
                r.setex(
                    cls.STATUS_KEY.format(instance_id=instance_id),
                    300,  # 5 分钟过期
                    json.dumps(result),
                )

                # 如果不健康 → 记录到 DB + 发送告警
                if not result["healthy"]:
                    cls._record_unhealthy(instance, result)
                    cls._send_alert(instance, result)

            finally:
                lock.release()

            # 安排下次检查（now + interval）
            r.zadd(cls.INSTANCE_REGISTRY, {
                item: now + instance.get("interval_sec", 30)
            })

        return {"worker": worker_id, "checked": checked}

    @classmethod
    def _do_health_check(cls, instance):
        """实际执行健康检查"""
        start = time.time()

        try:
            if instance["engine"] == "mysql":
                conn = psycopg2.connect(  # 实际用 pymysql/mysql-connector
                    host=instance["host"],
                    port=instance["port"],
                    connect_timeout=5,
                )
                with closing(conn):
                    with closing(conn.cursor()) as cur:
                        cur.execute("SELECT 1")
                        cur.fetchone()
                result = {"healthy": True, "latency_ms": (time.time() - start) * 1000}

            elif instance["engine"] == "redis":
                r2 = redis.Redis(
                    host=instance["host"],
                    port=instance["port"],
                    socket_connect_timeout=5,
                )
                r2.ping()
                r2.close()
                result = {"healthy": True, "latency_ms": (time.time() - start) * 1000}

            else:
                # PostgreSQL
                sock = socket.socket()
                sock.settimeout(5)
                sock.connect((instance["host"], instance["port"]))
                sock.close()
                result = {"healthy": True, "latency_ms": (time.time() - start) * 1000}

        except Exception as e:
            result = {
                "healthy": False,
                "error": str(e)[:200],
                "latency_ms": (time.time() - start) * 1000,
            }

        result["checked_at"] = time.time()
        return result
```

---

### 题 7：GPUGeek 平台实时 GPU 库存缓存

**场景**：GPUGeek 平台首页需要展示各区域 GPU 的实时库存（可用数量）。GPU 资源状态变化频繁（用户租用/释放），需要高实时性（< 2 秒延迟）。

**问题**：
1. 如何设计缓存来满足高并发低延迟？
2. 如何保证缓存和数据库的一致性？

**口述回答**：

"GPU 库存是高频读写的热点数据——首页展示、创建实例时校验可用数量都会访问。直接用 MySQL 查的话 QPS 上不去。我的方案是 Redis 做缓存层 + DB 做持久层。

读操作：全走 Redis Hash，key='gpu:inventory'，field 是 'region:gpu_type'，value 是可用数量。一次 HGETALL 拿到全量库存，毫秒级。

写操作（分配 GPU）：**先更新 DB，再更新 Redis**，用 Lua 脚本保证 Redis 端的原子性。Lua 脚本的逻辑是先 HGET 当前值，判断库存是否足够，够的话 HINCRBY 减 count，不够的话返回 -2。为什么用 Lua？因为如果先 HGET 再 HINCRBY 中间被别的请求插入，就会超卖，Lua 在 Redis 是单线程执行的，天然原子。

一致性保障：分配 GPU 走 DB 事务（select_for_update），DB 提交成功才执行 Lua 减 Redis。但如果 DB 成功、Redis 执行失败（比如 Redis 挂了重连），就会出现 DB 扣了而 Redis 没扣——多扣用户钱的严重 bug。所以 Lua 脚本返回 -2 时触发一个 **fallback 机制**：从 DB 全量重建 Redis 缓存。这种事务性补偿不是自动的，需要手动或定时触发。

还有个兜底：定时任务每 5 分钟从 DB 全量刷新一次 Redis，保证最终一致性。代码里还有一个细节——分配 GPU 时要先更新 last_billing_time 为当前时刻再入库，这属于业务逻辑和缓存操作的边界处理。"

**答案与代码**：

```python
"""
设计：
1. Redis Hash 存 GPU 库存（按区域 + GPU 型号）
2. 实例创建/释放时：先更新 DB，再更新 Redis
3. 缓存预热 + 定时刷新兜底
"""

class GPUInventoryService:
    """GPU 库存服务"""

    INVENTORY_KEY = "gpu:inventory"  # Hash: {region:gpu_type: available_count}

    @classmethod
    def get_available_gpus(cls, region=None, gpu_type=None):
        """查询可用 GPU（直接从 Redis 读，毫秒级）"""
        all_data = r.hgetall(cls.INVENTORY_KEY)

        results = []
        for key, count in all_data.items():
            reg, gpu = key.split(":", 1)
            if region and reg != region:
                continue
            if gpu_type and gpu != gpu_type:
                continue
            results.append({
                "region": reg,
                "gpu_type": gpu,
                "available": int(count),
            })
        return results

    @classmethod
    def allocate_gpu(cls, region, gpu_type, count=1):
        """
        分配 GPU（创建实例时调用）。

        先 DB 再 Redis：DB 成功 → Redis 减库存
        用 Lua 脚本保证 Redis 减库存的原子性
        """
        # 1. DB 扣库存（用 select_for_update 行锁）
        with transaction.atomic():
            inventory = Inventory.objects.select_for_update().get(
                region=region, gpu_type=gpu_type
            )
            if inventory.available < count:
                raise ValueError(f"{region} {gpu_type} 库存不足")
            inventory.available -= count
            inventory.save()

        # 2. Redis 扣库存（Lua 原子操作）
        lua_script = """
        local key = KEYS[1]
        local field = ARGV[1]
        local count = tonumber(ARGV[2])

        local current = redis.call('HGET', key, field)
        if not current then
            return -1  -- 字段不存在
        end

        current = tonumber(current)
        if current < count then
            return -2  -- 库存不足
        end

        redis.call('HINCRBY', key, field, -count)
        return current - count
        """
        new_count = r.eval(
            lua_script, 1, cls.INVENTORY_KEY,
            f"{region}:{gpu_type}", count
        )

        if new_count == -2:
            # Redis 和 DB 不一致！触发补偿刷新
            cls.refresh_inventory_from_db()
            raise ValueError("库存异常，请刷新重试")

        return new_count

    @classmethod
    def refresh_inventory_from_db(cls):
        """从 DB 全量刷新 Redis 缓存（兜底机制）"""
        from django.db.models import Sum

        # 按区域+GPU型号聚合
        inventories = Inventory.objects.values('region', 'gpu_type').annotate(
            total=Sum('available')
        )

        pipe = r.pipeline()
        pipe.delete(cls.INVENTORY_KEY)

        for inv in inventories:
            pipe.hset(cls.INVENTORY_KEY, f"{inv['region']}:{inv['gpu_type']}", inv['total'])

        pipe.execute()
```

---

## 五、LangChain / AI Agent 深度题

### 题 8：为 PaaS 数据库平台设计 AI 运维助手 Agent

**场景**：PaaS 数据库平台需要集成一个 AI 运维助手，用户可以用自然语言查询自己的实例状态、慢查询分析、扩容建议。例如用户问"昨天 CPU 最高的实例是哪个？帮我分析慢查询"。

**问题**：
1. 如何设计这个 Agent？需要哪些 Tool？
2. 如何保证 Agent 不会执行危险操作（如 DROP DATABASE）？
3. 如何在 Agent 中集成公司内部的 API？

**口述回答**：

"这是 LangChain Agent 的典型落地场景。以数据库运维助手为例，核心思路是把公司内部的 API 能力封装成 Agent 可以调用的 Tool，然后 LLM 自己决策什么时候调用哪个 Tool。

我的 Agent 有 5 个 Tool：查用户实例列表、查性能指标、分析慢查询、给出扩容建议、搜索内部知识库。每个 Tool 就是加个 @tool 装饰器的普通 Python 函数，函数签名加上类型注解和 docstring，LangChain 自动把函数签名转成 OpenAI function calling 的 schema——LLM 读 docstring 理解工具用途，根据参数类型决定传什么参数。

安全是重点。这个 Agent 只有**只读能力**——查实例、看监控、分析慢查询。绝对不能让它执行 DROP TABLE 或重启实例。保障分三层：第一，不注册任何写操作的 Tool（不写就不存在误操作的可能）。第二，ToolCallLimitMiddleware 限制最多 10 次工具调用，防止 Agent 死循环无限调 tool 烧 Token。第三，ModelRetryMiddleware 只重试 2 次避免雪崩。

Agent 和用户系统的对接：thread_id 绑定用户 ID，config = {'configurable': {'thread_id': str(user_id)}} 传给 Agent。Checkpointer 自动保存对话历史，用户下次问'刚才那个实例的扩容建议呢'，Agent 有上下文能继续。

还有一个我实际验证过的经验：SummarizationMiddleware 对长对话非常关键。运维排查可能要反复问好几轮，消息历史很容易超过模型上下文窗口，不加总结中间件 Agent 会'失忆'——加上后Token 消耗降 58%。

公司内部 API 的集成方式就是通过 Tool 的 @tool 装饰器直接调用 Django ORM 或 API 函数，和其他工具写法一样。"

**答案与代码**：

```python
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langchain.agents.middleware import (
    HumanInTheLoopMiddleware,
    SummarizationMiddleware,
    ModelRetryMiddleware,
    ToolCallLimitMiddleware,
)
from datetime import datetime, timedelta


# ===== 1. 定义 Agent 工具 =====

@tool
def query_user_instances(user_id: int) -> str:
    """查询用户拥有的所有数据库实例。

    Args:
        user_id: 用户ID
    """
    instances = DatabaseInstance.objects.filter(user_id=user_id)
    if not instances:
        return "您当前没有数据库实例"

    result = "您的数据库实例列表：\n"
    for inst in instances:
        result += (
            f"- ID: {inst.id}, 名称: {inst.name}, 引擎: {inst.engine} {inst.version}, "
            f"状态: {inst.status}, 配置: {inst.spec.get('cpu')}C{inst.spec.get('memory')}G\n"
        )
    return result


@tool
def get_instance_metrics(instance_id: str, hours: int = 24) -> str:
    """查询指定数据库实例的性能指标（CPU、内存、QPS、慢查询）。

    Args:
        instance_id: 实例ID
        hours: 最近多少小时（默认24小时）
    """
    since = datetime.now() - timedelta(hours=hours)

    metrics = MonitorMetricsHourly.objects.filter(
        instance_id=instance_id, hour_time__gte=since
    ).order_by('-hour_time')

    if not metrics:
        return f"实例 {instance_id} 在最近 {hours} 小时内暂无监控数据"

    # 计算摘要
    cpu_max = max(m.cpu_max for m in metrics)
    cpu_avg = sum(m.cpu_avg for m in metrics) / len(metrics)
    qps_max = max(m.qps_max for m in metrics)
    slow_total = sum(m.slow_queries_total for m in metrics)

    return f"""
实例 {instance_id} 最近 {hours} 小时性能摘要：
- CPU: 平均 {cpu_avg:.1f}%, 峰值 {cpu_max:.1f}%
- QPS: 峰值 {qps_max}
- 慢查询: 总计 {slow_total} 条
- 连接数峰值: {max(m.connections_max for m in metrics)}
"""


@tool
def analyze_slow_queries(instance_id: str, limit: int = 10) -> str:
    """分析数据库实例的慢查询日志，返回最耗时的 SQL 和优化建议。

    Args:
        instance_id: 实例ID
        limit: 分析前 N 条慢查询
    """
    # 从监控系统/慢查询日志中拉取
    slow_logs = SlowQueryLog.objects.filter(
        instance_id=instance_id
    ).order_by('-query_time')[:limit]

    if not slow_logs:
        return f"实例 {instance_id} 最近没有慢查询记录"

    result = f"实例 {instance_id} 的 Top {limit} 慢查询：\n"
    for i, log in enumerate(slow_logs, 1):
        result += (
            f"{i}. 耗时 {log.query_time:.2f}s | "
            f"扫描行数: {log.rows_examined} | "
            f"SQL: {log.sql_text[:150]}\n"
        )

    return result


@tool
def get_scaling_recommendation(instance_id: str) -> str:
    """根据性能指标给出扩容建议。

    Args:
        instance_id: 实例ID
    """
    # 获取最近 7 天数据
    metrics = MonitorMetricsHourly.objects.filter(
        instance_id=instance_id,
        hour_time__gte=datetime.now() - timedelta(days=7),
    )

    if not metrics:
        return "暂无足够数据给出建议"

    cpu_p99 = sorted(m.cpu_max for m in metrics)[int(len(metrics) * 0.99)]

    suggestions = []
    if cpu_p99 > 80:
        suggestions.append("CPU 使用率 P99 超过 80%，建议增加 CPU 核心数")
    if cpu_p99 > 50:
        suggestions.append("CPU 使用率较高，可考虑开启读写分离")

    avg_mem = sum(m.memory_avg for m in metrics) / len(metrics)
    max_mem = max(m.memory_avg for m in metrics)

    instance = DatabaseInstance.objects.get(id=instance_id)
    spec = instance.spec or {}
    mem_limit = spec.get('memory', 0)

    if mem_limit and max_mem > mem_limit * 0.8:
        suggestions.append(f"内存使用率超过 80%（峰值 {max_mem}MB / {mem_limit}MB），建议扩容内存")

    if not suggestions:
        suggestions.append(f"当前配置合理，CPU P99={cpu_p99:.1f}%")

    return "扩容建议：\n" + "\n".join(f"- {s}" for s in suggestions)


@tool
def search_knowledge_base(query: str) -> str:
    """在公司内部的数据库运维知识库中搜索解决方案。

    Args:
        query: 搜索关键词，如 'MySQL 主从延迟', 'Redis OOM 处理'
    """
    from src.rag.retriever import rag_retriever

    docs = rag_retriever.search(query, k=3)
    if not docs:
        return f"知识库中未找到关于 '{query}' 的内容"

    results = []
    for i, doc in enumerate(docs, 1):
        results.append(f"[{i}] {doc.page_content[:300]}")
    return "\n".join(results)


# ===== 2. 创建 Agent（带安全护栏） =====

OPS_AGENT_PROMPT = """你是首都在线数据库运维助手。职责：
1. 帮助用户查询实例信息和性能指标
2. 分析慢查询并给出优化建议
3. 根据历史数据给出扩容建议
4. 在知识库中搜索解决方案

安全规则：
- 你只能执行只读查询，不能修改变更任何实例配置
- 不能删除、重启、变更实例
- 不确定时建议用户联系运维团队
- 所有回答使用中文
"""

def create_ops_agent():
    """创建数据库运维 Agent"""
    model = init_chat_model("openai:gpt-4o", temperature=0.3)

    agent = create_agent(
        model=model,
        tools=[
            query_user_instances,
            get_instance_metrics,
            analyze_slow_queries,
            get_scaling_recommendation,
            search_knowledge_base,
        ],
        system_prompt=OPS_AGENT_PROMPT,
        middleware=[
            # 1. 上下文压缩（长对话不丢信息）
            SummarizationMiddleware(
                model=init_chat_model("openai:gpt-4o-mini"),
                trigger={"fraction": 0.7},
                keep={"messages": 10},
            ),
            # 2. 重试（模型调用失败自动重试 2 次）
            ModelRetryMiddleware(max_retries=2, backoff_factor=2.0),
            # 3. 工具调用次数限制（防止死循环）
            ToolCallLimitMiddleware(max_calls=10),
        ],
        name="database_ops_agent",
    )
    return agent


# ===== 3. API 接入 =====

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

ops_agent = create_ops_agent()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
async def chat_with_ops_agent(request):
    """与 AI 运维助手对话"""
    message = request.data.get('message', '')
    thread_id = request.data.get('thread_id', str(request.user.id))

    config = {"configurable": {"thread_id": thread_id}}

    result = await ops_agent.ainvoke(
        {"messages": [
            {"role": "system", "content": f"当前用户ID: {request.user.id}"},
            {"role": "user", "content": message},
        ]},
        config,
    )

    return Response({
        "reply": result["messages"][-1].content,
        "thread_id": thread_id,
    })
```

---

### 题 9：ComfyUI 平台中 AI 工作流自动推荐

**场景**：在 ComfyUI 工作流管理平台中，用户上传/创建了大量工作流。你希望实现一个智能推荐功能：根据用户当前的操作意图（如"生成真实风格的人像"），推荐合适的开源工作流模板，并自动从 Civitai 等社区搜索相关模型。

**问题**：
1. 如何用 RAG + 向量检索实现工作流推荐？
2. 如何设计工具让 Agent 能调用外部 API（如 Civitai）？

**口述回答**：

"这是 RAG + Agent 组合的典型应用。工作流推荐本质上是一个语义匹配问题：用户说'我想生成写实风格的人像'，系统需要从成千上万个工作流模板中找到最匹配的。

核心流程分三步：

第一步的**向量化**。把每个工作流模板的元信息（名称、描述、包含的节点类型、标签）拼成一段文本，用 OpenAI text-embedding-3-small 转成向量存 ChromaDB。这个 embedding 模型的维度是 1536，搜索效果对中英文都支持得不错。

第二步的**语义检索**。用户输入意图比如'生成动漫风格图片'，同样做 embedding，然后 similarity_search 在 ChromaDB 里找余弦距离最近的 K 个模板。这里有一个实际踩过的坑：纯向量搜索有时候会召回语义相近但实际不匹配的结果。更稳健的做法是 BM25 + 向量混合搜索 + Rerank 重排序，但这个场景数据量不大，纯向量就够用。

第三步的**Agent 串联**。用户意图除了触发工作流搜索，还会触发 Civitai 模型搜索——这两个搜索是独立的，Agent 可以并行调用两个 Tool 然后汇总结果。用户最终看到的是'推荐这 3 个工作流模板 + 你可以用这几个 Civitai 模型'的完整回答。

外部 API 集成如 Civitai 没什么特殊的——httpx 异步 HTTP 请求封装成 async Tool，LangChain Agent 天然支持异步 Tool。注意加超时和异常处理，外部 API 可能挂。"

**答案与代码**：

```python
"""
设计：
1. 所有工作流模板预先 Embedding → 存 ChromaDB
2. 用户输入意图 → 向量检索最相似的工作流
3. Agent = LLM 推理 + 向量检索 Tool + Civitai API Tool
"""
from langchain.tools import tool
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.documents import Document
import httpx

# ===== 工作流向量索引 =====
def build_workflow_index():
    """构建工作流模板向量索引"""
    workflows = Workflow.objects.filter(status='published')

    docs = []
    for wf in workflows:
        # 将工作流的元信息拼接为文本
        text = f"工作流名称: {wf.name}\n描述: {wf.description}\n"
        text += f"包含节点: {', '.join(wf.nodes.values_list('node_type', flat=True))}\n"
        text += f"标签: {wf.tags}\n"
        docs.append(Document(
            page_content=text,
            metadata={"workflow_id": wf.id, "name": wf.name},
        ))

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = Chroma.from_documents(
        docs, embeddings,
        persist_directory="./workflow_embeddings",
    )
    return vectorstore


vectorstore = build_workflow_index()


# ===== Agent 工具 =====
@tool
def search_workflows(intent: str, k: int = 5) -> str:
    """根据用户意图搜索匹配的 ComfyUI 工作流模板。

    Args:
        intent: 用户意图描述，如 '生成写实人像'、'动漫风格图片'、'图像超分放大'
        k: 返回前 K 个结果
    """
    results = vectorstore.similarity_search_with_score(intent, k=k)

    if not results:
        return "没有找到匹配的工作流模板"

    output = "推荐的工作流模板：\n"
    for i, (doc, score) in enumerate(results, 1):
        meta = doc.metadata
        output += f"{i}. [{meta['name']}] (相似度: {score:.2f})\n"
        output += f"   描述: {doc.page_content[:200]}\n\n"
    return output


@tool
async def search_civitai_models(query: str, model_type: str = "checkpoint", limit: int = 5) -> str:
    """在 Civitai 上搜索 AI 模型。

    Args:
        query: 搜索关键词
        model_type: 模型类型 (checkpoint, lora, textual_inversion, vae)
        limit: 返回数量
    """
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://civitai.com/api/v1/models",
            params={"query": query, "type": model_type, "limit": limit, "sort": "Highest Rated"},
            timeout=10,
        )
        data = resp.json()

    items = data.get("items", [])
    if not items:
        return f"Civitai 上没有找到 '{query}' 相关的 {model_type} 模型"

    result = f"Civitai 上关于 '{query}' 的推荐模型：\n"
    for i, item in enumerate(items, 1):
        stats = item.get("stats", {})
        result += (
            f"{i}. {item['name']}\n"
            f"   下载: {stats.get('downloadCount', 0)}, "
            f"评分: {stats.get('rating', 0):.1f}, "
            f"类型: {item['type']}\n"
            f"   链接: https://civitai.com/models/{item['id']}\n\n"
        )
    return result


@tool
def download_and_import_workflow(workflow_id: int, user_id: int) -> str:
    """将推荐的工作流模板导入到用户的工作区。

    Args:
        workflow_id: 工作流模板ID
        user_id: 用户ID
    """
    template = Workflow.objects.get(id=workflow_id)

    # 克隆工作流
    new_wf = Workflow.objects.create(
        name=f"{template.name} (导入)",
        description=template.description,
        user_id=user_id,
        status='draft',
    )

    # 克隆节点
    for node in template.nodes.all():
        WorkflowNode.objects.create(
            workflow=new_wf,
            node_id=node.node_id,
            node_type=node.node_type,
            position_x=node.position_x,
            position_y=node.position_y,
            properties=node.properties,
        )

    # 克隆连接线
    for link in template.links.all():
        WorkflowLink.objects.create(workflow=new_wf, **link)

    return f"工作流 '{template.name}' 已导入到您的工作区（ID: {new_wf.id}），包含 {template.nodes.count()} 个节点"
```

---

## 六、系统设计与架构题

### 题 10：设计 GPUGeek 平台的算力调度系统

**场景**：GPUGeek 平台中，用户提交 GPU 任务（训练/推理），需要调度到可用的 GPU 节点上。全球多个区域都有 GPU 集群。

**问题**：
1. 调度算法如何设计？
2. 如何处理"优先级"（付费用户优先）？
3. 超时任务如何处理？

**口述回答**：

"算力调度是一个资源分配问题。全球多个区域有 GPU 集群，用户提交任务后需要调度到最合适的 GPU 节点上。我设计的架构是三层调度。

第一层**全局调度器**：接收用户任务请求，根据 GPU 型号、数量、区域偏好选择最优集群。比如用户需要 8 张 A100 且偏好新加坡，全局调度器先看新加坡集群有没有资源，没有再降级到其他区域。这是粗粒度的路由决策。

第二层**本地调度器**：管理单个集群内的 GPU 资源池，维护一个优先级队列。具体实现用 Redis Sorted Set——score = 结合优先级和入队时间的复合值。优先级高的排在前面，同优先级按 FIFO。高优先级可抢占低优先级——这个'可抢占'不是说直接 kill 低优任务，而是新任务入队时插到低优前面。

第三层**节点执行器**：在具体 GPU 节点上启动容器、挂载存储、配置网络、监控资源。

优先级设计上用了 4 级枚举（LOW/NORMAL/HIGH/URGENT）。Redis Sorted Set 按 score 升序排列，所以 score 要写成负的优先级值——priority 越高的任务 score 越小，排前面。复合 score = -(priority * 10^10 + timestamp)，保证'同优先级 FIFO，不同优先级按优先级排'。

超时处理用单独的扫描任务：每 30 秒扫描所有运行中的任务，计算 now - start_time，超过 timeout 的强制终止。终止前先发 WebSocket 通知用户'任务超时即将终止'，给 30 秒缓冲。"

**答案**：

```python
"""
调度系统设计（三层）：

第 1 层：全局调度器 (Global Scheduler)
  - 接收任务请求
  - 根据任务需求（GPU型号、数量、区域偏好）选择最优集群
  - 将任务下发到对应集群的本地调度器

第 2 层：本地调度器 (Local Scheduler)
  - 管理单个集群内的 GPU 资源池
  - 维护等待队列（按优先级 + FIFO 排序）
  - 分配具体 GPU 节点

第 3 层：节点执行器 (Node Executor)
  - 在具体 GPU 节点上启动容器
  - 监控资源使用和任务状态
  - 执行超时处理

调度策略：
1. 优先分配同一集群的 GPU（跨集群通信延迟高）
2. 碎片整理：尽量把 GPU 分配给能填满单机的任务
3. 优先级队列：付费用户 > 试用用户，高优先级可抢占低优先级
"""
```

```python
import heapq
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class TaskPriority(int, Enum):
    LOW = 0      # 试用用户
    NORMAL = 1   # 普通用户
    HIGH = 2     # 付费用户
    URGENT = 3   # VIP/管理员


@dataclass(order=True)
class GPUTask:
    priority: int  # 优先级的负数（heapq 是最小堆，优先级高的排在前面）
    enqueue_time: float
    task_id: str = field(compare=False)
    user_id: int = field(compare=False)
    gpu_type: str = field(compare=False)
    gpu_count: int = field(compare=False)
    region: str = field(compare=False)
    image: str = field(compare=False)
    command: str = field(compare=False)
    timeout: int = field(compare=False, default=3600)  # 超时时间（秒）


class GPUScheduler:
    """GPU 任务调度器（基于 Redis 的优先级队列 + 分布式锁）"""

    TASK_QUEUE_KEY = "gpu:task_queue:{region}:{gpu_type}"

    def __init__(self):
        self.r = redis.Redis(decode_responses=True)

    def submit_task(self, task: GPUTask) -> str:
        """提交任务到等待队列"""
        # 按区域 + GPU型号 路由到不同队列
        queue_key = self.TASK_QUEUE_KEY.format(
            region=task.region, gpu_type=task.gpu_type
        )

        # Redis Sorted Set 实现优先级队列
        # score = 优先级分数（priority越大越优先，但zset按score升序，所以用负数）
        score = -(task.priority * 10**10 + int(time.time() * 1000))
        self.r.zadd(queue_key, {task.task_id: score})

        # 任务详情存 Hash
        self.r.hset(f"gpu:task:{task.task_id}", mapping=task.__dict__)

        return task.task_id

    def schedule(self, region: str, gpu_type: str, available_count: int) -> List[str]:
        """调度：将等待队列中的任务分配到可用 GPU"""
        queue_key = self.TASK_QUEUE_KEY.format(region=region, gpu_type=gpu_type)

        # 从优先级队列中弹出前 N 个任务
        # 原子操作：ZPOPMIN
        task_ids = self.r.zpopmin(queue_key, count=available_count)

        scheduled = []
        for task_id, _ in task_ids:
            task_data = self.r.hgetall(f"gpu:task:{task_id}")
            if task_data:
                scheduled.append(task_id)
                # 分配 GPU → 创建实例 → 通知用户
                self._allocate_gpu(task_data)

        return scheduled

    def handle_timeout(self):
        """扫描超时任务并自动终止"""
        now = time.time()

        # 扫描所有运行中的任务
        for task_id in self.r.scan_iter("gpu:task:*"):
            task = self.r.hgetall(task_id)

            if task and now - float(task["start_time"]) > task["timeout"]:
                # 超时：强制终止
                self._terminate_task(task_id)
```

---

## 七、综合场景题

### 题 11：PaaS 平台数据库实例的自动备份策略

**场景**：PaaS 数据库平台需要为 MySQL/Redis/PostgreSQL 实例提供自动备份功能。支持全量备份（每天）和增量备份（每小时），备份文件存到 MinIO。

**问题**：
1. 如何设计备份任务调度？
2. 备份失败如何重试和告警？
3. 如何保证备份和恢复的一致性（特别是 MySQL 的 mysqldump 锁问题）？

**口述回答**：

"备份看似简单，实则有很多坑。一个数据库平台的可信度，很大程度取决于备份恢复能力——用户数据丢了是不可接受的。

我的备份策略分两个层次：全量备份每天一次（凌晨 2-6 点），增量备份每小时（binlog）。备份文件存 MinIO，命名规则是 '{instance_id}/{backup_type}/{timestamp}.{format}'。

调度上有个重点：**错峰执行**。如果 1000 个实例同时在凌晨 2 点开始备份，磁盘 IO 会被打爆。我用 Celery Beat 触发调度任务，把实例按创建时间排序后每个间隔 5 分钟加一个随机偏移（0-120 秒），把备份平摊到 4 个小时窗口内。实例级别用 Redis 分布式锁防止同一实例被两个 Worker 同时备份。

MySQL 备份的核心问题是一致性——备份过程中有写入怎么办？答案是 `mysqldump --single-transaction`。这个参数启动一个 REPEATABLE READ 的事务，基于 MVCC 快照导出整个数据库——期间 DML 操作完全不受影响，因为 mysqldump 读的是快照，实际写入走的是当前数据。但有前提：存储引擎必须是 InnoDB 且没有执行 DDL。还有一个 `--quick` 参数，让 mysqldump 逐行读取而不是全部加载到内存——对大表这是致命的，没有它 10GB 的表会把备份进程 OOM。

恢复验证也是设计重点——备份不是目的，能恢复才是。定期随机抽取实例做恢复演练：从 MinIO 拉备份文件 → 创建临时实例 → 恢复 → 抽样校验数据 → 记录结果 → 销毁临时实例。校验和 SHA256 在每个备份完成后计算并存库，恢复时对比。

备份失败的重试交给 Celery 的 max_retries + 指数退避。连续失败需要人工介入的发告警——比如 3 次全量备份都失败，说明可能是实例本身有问题或者 MinIO 连接挂了。"

**答案与代码**：

```python
"""
备份策略：
- 全量备份：每天凌晨 2:00 - 6:00 之间（与实例所在时区错峰）
- 增量备份：每小时（MySQL binlog, Redis RDB）
- 备份文件命名：{instance_id}/{backup_type}/{timestamp}.{format}

调度设计：
- 避免所有实例同时备份（错峰执行，随机偏移）
- 备份任务由 Celery Beat 触发 + Celery Worker 执行
- 备份前加实例级分布式锁
- 备份结果存 MinIO + 记录到 DB
"""

from datetime import timedelta, datetime
import random

class BackupType(str, Enum):
    FULL = "full"
    INCREMENTAL = "incremental"


class BackupRecord(models.Model):
    instance_id = models.UUIDField()
    backup_type = models.CharField(max_length=20)
    file_path = models.CharField(max_length=500)     # MinIO 路径
    file_size = models.BigIntegerField()
    status = models.CharField(max_length=20)          # running, success, failed
    started_at = models.DateTimeField()
    finished_at = models.DateTimeField(null=True)
    error_message = models.TextField(blank=True)
    checksum = models.CharField(max_length=64, blank=True)  # SHA256


@shared_task(bind=True, max_retries=2, default_retry_delay=300)
def backup_instance(self, instance_id: str, backup_type: str):
    """备份单个实例"""

    instance = DatabaseInstance.objects.get(id=instance_id)
    lock_key = f"backup:lock:{instance_id}"

    # 1. 加锁：防止同时有多个备份任务
    if not r.set(lock_key, "1", nx=True, ex=600):
        logger.info(f"实例 {instance_id} 正在备份中，跳过")
        return

    try:
        if instance.engine == "mysql":
            result = _backup_mysql(instance, backup_type)
        elif instance.engine == "redis":
            result = _backup_redis(instance, backup_type)
        elif instance.engine == "postgresql":
            result = _backup_postgresql(instance, backup_type)
        else:
            raise ValueError(f"不支持的引擎: {instance.engine}")

        # 记录备份
        BackupRecord.objects.create(
            instance_id=instance_id,
            backup_type=backup_type,
            status='success',
            file_path=result['path'],
            file_size=result['size'],
            started_at=result['started'],
            finished_at=result['finished'],
            checksum=result['checksum'],
        )

        # 清理过期备份
        _cleanup_old_backups(instance_id)

    except Exception as e:
        BackupRecord.objects.create(
            instance_id=instance_id,
            backup_type=backup_type,
            status='failed',
            error_message=str(e)[:500],
        )
        self.retry(exc=e)
    finally:
        r.delete(lock_key)


def _backup_mysql(instance, backup_type):
    """
    MySQL 备份（mysqldump）。

    --single-transaction：InnoDB 一致性备份（不加锁，不阻塞写入）
    --quick：逐行导出（大表不OOM）
    --routines --triggers：包含存储过程和触发器
    """
    import subprocess, hashlib, tempfile

    host = instance.endpoint.split(":")[0]
    port = instance.endpoint.split(":")[1] if ":" in instance.endpoint else "3306"

    started = datetime.now()
    filepath = tempfile.mktemp(suffix=".sql.gz")

    if backup_type == BackupType.FULL:
        cmd = [
            "mysqldump",
            f"--host={host}", f"--port={port}",
            "-u", instance.master_user,
            f"-p{instance.master_password}",
            "--single-transaction",
            "--quick",
            "--routines",
            "--triggers",
            "--all-databases",
        ]
        # 管道到 gzip 并输出到文件
        with open(filepath, "wb") as f:
            p1 = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            p2 = subprocess.Popen(["gzip"], stdin=p1.stdout, stdout=f)
            p1.stdout.close()
            p2.communicate()

    elif backup_type == BackupType.INCREMENTAL:
        # 增量备份 = 备份 binlog
        cmd = f"mysqlbinlog --read-from-remote-server --host={host} --port={port} ..."

    finished = datetime.now()

    # 计算校验和
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        while True:
            data = f.read(65536)
            if not data:
                break
            sha.update(data)

    # 上传到 MinIO
    minio_path = f"{instance.id}/{backup_type}/{started.strftime('%Y%m%d%H%M%S')}.sql.gz"
    upload_to_minio(filepath, minio_path)

    file_size = os.path.getsize(filepath)
    os.remove(filepath)

    return {
        "path": minio_path,
        "size": file_size,
        "started": started,
        "finished": finished,
        "checksum": sha.hexdigest(),
    }


# 备份调度：错峰执行
@shared_task
def schedule_full_backups():
    """每天凌晨，为所有实例安排全量备份（错峰执行）"""
    instances = DatabaseInstance.objects.filter(
        status='running',
        auto_backup=True,
    )

    base_time = datetime.now().replace(hour=2, minute=0)

    for i, inst in enumerate(instances):
        # 每个实例间隔 5 分钟，避免 I/O 集中
        delay = i * 300 + random.randint(0, 120)
        backup_instance.apply_async(
            args=[str(inst.id), BackupType.FULL],
            eta=base_time + timedelta(seconds=delay),
        )

    return {'scheduled': len(instances)}
```

---

## 面试题总表

| 题号 | 方向 | 场景来源 | 难度 | 核心考点 |
|------|------|---------|------|---------|
| 1 | Python | PaaS 数据库平台 | ⭐⭐⭐⭐⭐ | 状态机、Celery 异步、事务回滚 |
| 2 | Python | ComfyUI 平台 | ⭐⭐⭐⭐ | JSON 解析、参数校验、图结构存储 |
| 3 | Python | GPUGeek 平台 | ⭐⭐⭐⭐⭐ | 秒级计费、分布式事务、防重复 |
| 4 | MySQL | PaaS 数据库平台 | ⭐⭐⭐⭐ | 分区表、聚合优化、数据归档 |
| 5 | MySQL+Redis | GPUGeek 平台 | ⭐⭐⭐⭐⭐ | 三层防重、乐观锁+行锁+分布式锁 |
| 6 | Redis | PaaS 数据库平台 | ⭐⭐⭐⭐ | 分布式健康检查、Sorted Set 调度 |
| 7 | Redis | GPUGeek 平台 | ⭐⭐⭐⭐ | Lua 原子操作、缓存一致性 |
| 8 | LangChain | PaaS 数据库平台 | ⭐⭐⭐⭐⭐ | Agent 设计、Tool 开发、安全护栏 |
| 9 | LangChain | ComfyUI 平台 | ⭐⭐⭐⭐ | RAG 向量检索、外部 API 集成 |
| 10 | 架构 | GPUGeek 平台 | ⭐⭐⭐⭐⭐ | 算力调度、优先级队列、超时处理 |
| 11 | 综合 | PaaS 数据库平台 | ⭐⭐⭐⭐⭐ | MySQL备份、mysqldump 一致性、MinIO |

---

> **面试策略建议**：每道题先从"场景理解"入手 → 说设计思路 → 再给关键代码 → 最后补充边界情况。技术负责人很看重**从场景到方案的完整思维链路**。

---

# 十二、首都在线 CloudOS 云管理平台

> 项目背景：首都在线（CapitalOnline）CloudOS 公有云管理平台，Python Django + DRF 微服务架构。三个核心服务分工协作——ecs-service（执行层）、ecs-business（运维层）、gic-business（用户控制台层），共享 MySQL / Redis / Kafka 基础设施。

---

## Q1: 介绍 CloudOS 三个服务的分层架构

**场景理解：**

首都在线是一个公有云平台（对标阿里云/腾讯云）。终端用户在网页上买云主机、挂云盘，背后是三层微服务：

```
用户浏览器 → gic-business → ecs-service → 虚拟化层
运维管理台 → ecs-business → ecs-service → 虚拟化层
```

- **gic-business（用户控制台）**：给终端用户用的，管自己的云主机/云盘/镜像/快照
- **ecs-business（运维管理台）**：给内部运维用的，管物理机/Pod/集群/库存
- **ecs-service（核心执行层）**：真正执行云资源操作的服务，对接虚拟化层

**设计思路：**

三层分工人为做了"读写分离"——gic-business 和 ecs-business 只能读和发起请求，所有写的操作最终都在 ecs-service 里执行。这样保证了：

1. 状态一致性——云资源状态变更只在一个地方发生
2. 审计可追踪——所有变更操作统一经过 ecs-service
3. 解耦——用户层改需求不影响运维层，运维层加功能不干扰用户层

**面试话术：**

> "我们当时是 Django + DRF 微服务架构，三个服务通过 HTTP 内部调用串联。最底层 ecs-service 是唯一能碰虚拟化的服务，上面两层是它的'客户端'。gic-business 面向终端用户，ecs-business 面向运维。最大的设计决策是**把执行和展示彻底分开**——业务层只做校验和编排，真正执行全在 service 层，保证了状态一致性。"

---

## Q2: EBS 云盘模块——从用户点击到云盘挂载全链路

> 这是我主要负责的核心模块。EBS（Elastic Block Storage）是云盘——用户可以创建一块云盘，然后挂载到自己的云主机上。

**场景理解：**

用户登录控制台 → 点击"挂载云盘" → 选云盘 + 目标 ECS → 确认。背后经过两层服务：

```
GIC 前端 → gic-business (View→Backend→HTTP Client) → ecs-service (事件→Spooler→虚拟化)
```

### 2.1 gic-business 层：EbsView 的真实代码

用户控制台的 API 在 `gic-business/apps/api/views/ebs.py`，真实代码长这样：

```python
# gic-business/apps/api/views/ebs.py — 真实源码
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from apps.api.serializers.ebs import (
    DiskMountSerializer, DiskCreateSerializer, DiskExpansionSerializer,
    BatchOperateDiskBaseSerializer, GetCloudDiskListSerializer, ...
)
from apps.api.backend.ebs_service import EbsOperateService, DiskService, EbsDataService


class EbsView(GenericViewSet):

    @action(methods=['POST'], url_path='mount', detail=False,
            serializer_class=DiskMountSerializer)
    @login_required
    @response
    def mount(self, req, data):
        """云盘挂载"""
        op = EbsOperateService(data)
        res = op.api_mount_ebs(data)
        return res

    @action(methods=['POST'], url_path='unmount', detail=False,
            serializer_class=BatchOperateDiskBaseSerializer)
    @login_required
    @response
    def unmount(self, req, data):
        """云盘卸载"""
        op = EbsOperateService(data)
        res = op.api_unmount_ebs(data)
        return res

    @action(methods=['POST'], url_path='expansion', detail=False,
            serializer_class=DiskExpansionSerializer)
    @login_required
    @response
    def expansion(self, req, data):
        """云盘扩容"""
        op = EbsOperateService(data)
        res = op.api_expansion_ebs(data)
        return res

    @action(methods=['POST'], url_path='create_disk', detail=False,
            serializer_class=DiskCreateSerializer)
    @login_required
    @response
    def create_disk(self, req, data):
        """云盘创建"""
        op = EbsOperateService(data)
        res = op.api_create_ebs(data)
        return res
```

View 层的设计非常简单——**每个 action 只有三行**：创建 Service 实例 → 调 Backend 方法 → 返回结果。参数校验由 `@response` 装饰器结合 DRF 的 Serializer 自动完成，不需要在 View 里写。

### 2.2 gic-business Backend 层：真实的业务逻辑

`gic-business/apps/api/backend/ebs_service.py` 是真正的业务逻辑层：

```python
# gic-business/apps/api/backend/ebs_service.py — 真实源码
from utils.request_service import EbsServiceRequest

class EbsOperateService(BasicService):

    @catch_business_exception('云盘挂载')
    def api_mount_ebs(self, data):
        logger.info('云盘挂载参数：{}'.format(data))

        # 1. 权限校验：检查 ECS 和云盘是否属于当前用户
        ecs_id = data['ecs_id']
        disk_ids = data['disk_ids']
        self.check_customer_ecs([ecs_id])
        self.check_customer_disks(disk_ids)
        self.check_disks_is_follow_delete(disk_ids, data.get('is_follow_delete', False))

        # 2. 组装参数
        params = {
            'customer_id': self.customer_id,
            'ecs_id': ecs_id,
            'disk_ids': disk_ids,
            'is_follow_delete': data.get('is_follow_delete', False),
            'op_user': self.op_user,
            'op_source': self.op_source,
            'host_id': data.get('host_id', ''),
            'product_source': data.get('product_source', '')
        }

        # 3. 调下游 HTTP 客户端 → ecs-service
        res_data = EbsServiceRequest.disk_mount_info(params)
        return BusinessReturn(ReturnCodeMsg.SUCCESS, '云盘挂载成功！', res_data)

    @catch_business_exception('云盘扩容')
    def api_expansion_ebs(self, data):
        logger.info('云盘扩容参数：{}'.format(data))
        params = {
            'customer_id': self.customer_id,
            'expansion_info': data.get('expansion_info'),
            'billing_info': data.get('billing_info'),
            'op_user': self.op_user,
            'op_source': self.op_source,
            'az_id': data.get('az_id')
        }
        res_data = EbsServiceRequest.disk_expansion_info(params)
        return BusinessReturn(ReturnCodeMsg.SUCCESS, '云盘扩容成功！', res_data)
```

### 2.3 HTTP 客户端层：EbsServiceRequest

`gic-business/utils/request_service.py` 封装了对下游 ecs-service（也叫 ebs-service）的 HTTP 调用：

```python
# 真实源码 — 所有 EBS 相关 API 的 HTTP 端点定义
class EbsServiceRequest(BusinessRequest):
    EBS_SERVICE_URL = settings.EBS_SERVICE_URL

    # 每个操作对应一个下游 URL
    DISK_MOUNT_URL    = urljoin(EBS_SERVICE_URL, '/ebs_service/v1/ebs/mount/')
    DISK_UNMOUNT_URL  = urljoin(EBS_SERVICE_URL, '/ebs_service/v1/ebs/unmount/')
    DISK_CREATE_URL   = urljoin(EBS_SERVICE_URL, '/ebs_service/v1/ebs/api_create_disk/')
    DISK_UPDATE_URL   = urljoin(EBS_SERVICE_URL, '/ebs_service/v1/ebs/expansion/')
    DISK_DESTROY_URL  = urljoin(EBS_SERVICE_URL, '/ebs_service/v1/ebs/destroy_disk/')
    EBS_PRICE_URL     = urljoin(EBS_SERVICE_URL, '/ebs_service/v1/ebs_data/get_ebs_price/')
    DISK_LIMIT_URL    = urljoin(EBS_SERVICE_URL, '/ebs_service/v1/ebs/get_disk_limit/')
    # ... 30+ 个端点

    @classmethod
    def disk_mount_info(cls, param):
        return cls.post(cls.DISK_MOUNT_URL, param)

    @classmethod
    def disk_unmount_info(cls, param):
        return cls.post(cls.DISK_UNMOUNT_URL, param)

    @classmethod
    def disk_create_ebs(cls, param):
        return cls.post(cls.DISK_CREATE_URL, param)

    @classmethod
    def disk_expansion_info(cls, param):
        return cls.post(cls.DISK_UPDATE_URL, param)
```

### 2.4 ecs-service 层：DiskEventSet 事件处理

请求到达 ecs-service 后，`spool_service/event_service/ebs_event_service.py` 的 `DiskEventSet.common_init_ebs_event()` 负责拆解事件为子任务：

```python
# ecs-service/spool_service/event_service/ebs_event_service.py — 真实源码
class DiskEventSet(object):

    @classmethod
    def common_init_ebs_event(cls, event):
        event_type = event.event_type               # 事件类型（挂载/卸载/扩容/删除）
        event_param = event.event_param             # 请求参数
        disk_ids = event_param['disk_ids']          # 云盘ID列表
        customer_id = event.customer_id

        disk_queryset = CloudOsDisk.objects.select_related('az__region', 'ecs_goods').filter(
            disk_id__in=disk_ids, is_valid=True)

        for disk in disk_queryset:
            resource_id = disk.disk_id
            region_id = disk.az.region_id           # 从关联表获取 region
            az_code = disk.az.az_code
            disk_type = disk.ecs_goods.feature.lower()  # SSD / HDD

            global_context = {
                'customer_id': customer_id,
                'volume_info': [{
                    'uuid': resource_id,
                    'disk_type': disk_type
                }]
            }

            # ===== 根据事件类型设置不同的上下文 =====
            if event_type == EbsEventType.MOUNT_DISK:
                # 挂载：需要 ecs_id + attach_flag + order
                ecs_id = event_param['ecs_id']
                global_context['instance_id'] = ecs_id
                global_context['volume_info'][0]['attach_flag'] = EbsAttachFlagType.ATTACH
                global_context['volume_info'][0]['order'] = order

            elif event_type == EbsEventType.UNMOUNT_DISK:
                # 卸载：从 disk 对象上取已挂载的 ecs_id
                ecs_id = disk.ecs_id
                global_context['instance_id'] = ecs_id
                global_context['volume_info'][0]['attach_flag'] = EbsAttachFlagType.UNLOAD

            elif event_type == EbsEventType.UPDATE_DISK:
                # 扩容：传入新大小 + iops + 带宽
                expansion_config = event_param['disk_expanded_info'][resource_id]
                global_context['volume_info'][0]['size'] = expansion_config['size']
                global_context['volume_info'][0]['iops'] = expansion_config.get('iops', 0)
                global_context['volume_info'][0]['band_mbps'] = expansion_config.get('storage', 0)

            elif event_type == EbsEventType.DELETE_DISK:
                # 逻辑删除：如果已挂载，先卸载再删
                if disk.ecs_id and recycling_info:
                    global_context['instance_id'] = disk.ecs_id
                    global_context['volume_info'][0]['attach_flag'] = EbsAttachFlagType.UNLOAD
                    maintask_name = EVENT_MAIN_TASK_DICT[EbsEventType.DETACH_DELETE_DISK]

            # 生成 Task 对象，写入 CloudOsTask 表
            task_param = gen_task_param(maintask_name, ResourceType.EBS, resource_id,
                                        region_id, az_code, customer_id, global_context)
            task_id = create_uuid()
            ebs_task = gen_task_instance(task_id, resource_id, az_id, customer_id, now,
                                         event, event_type, task_param, EcsCloudType.EBS)
            ebs_task_list.append(ebs_task)
```

### 2.5 EbsTaskSet — 任务执行与失败回滚

任务生成后，由 `spool_service/task_service/ebs_task_service.py` 的 `EbsTaskSet` 负责执行，继承自 `CommonTaskSet`：

```python
# ecs-service/spool_service/task_service/ebs_task_service.py — 真实源码
class EbsTaskSet(CommonTaskSet):

    @staticmethod
    def mount_disk_success(ebs_task):
        """挂载成功后：更新 disk 状态 + 更新订单"""
        event_param = ebs_task.event.event_param
        ecs_id = event_param['ecs_id']
        disk_id = ebs_task.cloud_id
        disk = CloudOsDisk.objects.get(disk_id=disk_id, is_valid=True)
        # ... 状态更新 ...

    def common_op_ebs_error(self, ebs_task):
        """失败处理：回滚 disk 状态"""
        disk_id = ebs_task.cloud_id
        task_type = ebs_task.task_type
        with transaction.atomic():
            kwargs = {'update_time': datetime.datetime.now()}
            if task_type == EbsEventType.MOUNT_DISK:
                kwargs['ecs_id'] = ''                # 清空挂载的ECS
                kwargs['status'] = DiskResourceStatus.WAITING    # 回滚为"待挂载"
            elif task_type == EbsEventType.UNMOUNT_DISK:
                kwargs['status'] = DiskResourceStatus.RUNNING    # 回滚为"使用中"
            else:
                kwargs['status'] = DiskResourceStatus.ERROR      # 标记为错误
            CloudOsDisk.objects.filter(disk_id=disk_id, is_valid=True).update(**kwargs)
```

**面试话术：**

> "EBS 云盘模块我负责了完整的三层实现。gic-business 层是用户控制台后端——`EbsView` 用 DRF 的 `GenericViewSet` + `@action` 装饰器定义了 20+ 个端点，参数校验走 Serializer，业务逻辑在 `EbsOperateService` 里（先校验权限→再调 HTTP 客户端→返回结果）。HTTP 客户端 `EbsServiceRequest` 封装了 30+ 个下游 API，通过 `settings.EBS_SERVICE_URL` 配置目标地址。最底层 ecs-service 用 `DiskEventSet` 把每个操作拆成子任务链——比如挂载操作需要传 `instance_id`（目标 ECS）+ `attach_flag`（挂载/卸载标识）+ `order`（多盘挂载顺序）。任务框架支持自动失败回滚：挂载失败就把 `ecs_id` 清空、状态回滚到 `WAITING`。"



---

## Q3: 云盘挂载/卸载的完整流程与权限校验

**场景理解：**

用户在控制台把一块云盘挂载到云主机。这个操作涉及 `gic-business` 层的权限校验 + `ecs-service` 层的事件拆分和异步执行。

### 3.1 gic-business Backend 层：权限校验

真实源码在 `gic-business/apps/api/backend/ebs_service.py`，关键校验逻辑：

```python
# gic-business/apps/api/backend/ebs_service.py — 真实源码
class EbsOperateService(BasicService):

    def do_mount_disk(self, data):
        ecs_id = data['ecs_id']
        disk_ids = data['disk_ids']
        host_id = data.get('host_id', '')
        is_follow_delete = data.get('is_follow_delete', False)

        # === 权限校验（继承自 BasicService 的方法）===
        if not host_id:
            self.check_customer_ecs([ecs_id])          # ECS 是否属于当前用户
        self.check_customer_disks(disk_ids)             # 云盘是否属于当前用户
        self.check_disks_is_follow_delete(disk_ids, is_follow_delete)  # 随删属性校验

        # === 组装参数传给 ecs-service ===
        params = {
            'customer_id': self.customer_id,
            'ecs_id': ecs_id,
            'disk_ids': disk_ids,
            'is_follow_delete': is_follow_delete,
            'op_user': self.op_user,
            'op_source': self.op_source,
            'host_id': host_id,
            'product_source': data.get('product_source', '')
        }
        res_data = EbsServiceRequest.disk_mount_info(params)
        return res_data
```

三层校验逻辑：
- `check_customer_ecs()` — 查 `CloudOsEcs` 表确认这台 ECS 的 `customer_id` 匹配当前用户
- `check_customer_disks()` — 查 `CloudOsDisk` 表确认这些云盘的 `customer_id` 匹配当前用户
- `check_disks_is_follow_delete()` — 校验云盘是否设置了"随 ECS 删除"

### 3.2 ecs-service 层：挂载事件拆分

挂载操作在 `DiskEventSet.common_init_ebs_event()` 中的处理：

```python
# ecs-service — 真实源码
if event_type == EbsEventType.MOUNT_DISK:  # 挂载云盘
    ecs_id = event_param['ecs_id']
    global_context['instance_id'] = ecs_id
    global_context['volume_info'][0]['attach_flag'] = EbsAttachFlagType.ATTACH   # 挂载标记
    global_context['volume_info'][0]['order'] = order     # 多盘挂载顺序
    disk_type = disk.ecs_goods.feature
    global_context['volume_info'][0]['disk_type'] = disk_type   # 磁盘类型(SSD/HDD)

if event_type == EbsEventType.UNMOUNT_DISK:  # 卸载云盘
    ecs_id = disk.ecs_id                                   # 从 disk 记录上取
    global_context['instance_id'] = ecs_id
    global_context['volume_info'][0]['attach_flag'] = EbsAttachFlagType.UNLOAD  # 卸载标记
```

### 3.3 失败自动回滚

```python
# ecs-service/spool_service/task_service/ebs_task_service.py — 真实源码
def common_op_ebs_error(self, ebs_task):
    """失败回滚磁盘状态"""
    disk_id = ebs_task.cloud_id
    task_type = ebs_task.task_type

    with transaction.atomic():
        kwargs = {'update_time': datetime.datetime.now()}

        if task_type == EbsEventType.MOUNT_DISK:
            kwargs['ecs_id'] = ''                           # 清空挂载关系
            kwargs['status'] = DiskResourceStatus.WAITING   # → "待挂载"
        elif task_type == EbsEventType.UNMOUNT_DISK:
            kwargs['status'] = DiskResourceStatus.RUNNING   # → "使用中"
        else:
            kwargs['status'] = DiskResourceStatus.ERROR     # → "错误"

        CloudOsDisk.objects.filter(disk_id=disk_id, is_valid=True).update(**kwargs)
```

**面试话术：**

> "挂载前的校验集中在 `BasicService` 的 check 方法族里——`check_customer_ecs` 验证 ECS 归属、`check_customer_disks` 验证云盘归属。校验通过后，gic-business 通过 `EbsServiceRequest.disk_mount_info()` 把请求发给 ecs-service。ecs-service 在 `DiskEventSet` 里根据事件类型 `MOUNT_DISK` 给 `volume_info` 打上 `attach_flag=ATTACH` 标记和 `order` 顺序。失败回滚由 `common_op_ebs_error` 统一处理——`with transaction.atomic()` 保护，挂载失败就清空 `ecs_id`，状态回滚到 `WAITING`。"



---

## Q4: 云盘扩容的特殊处理

**场景理解：**

云盘扩容和创建/挂载不同——扩容可以在线进行（云盘正挂载着也能扩容，不需要先卸载）。但扩容后需要通知 ECS 重新识别磁盘大小。

```python
# 扩容流程
def expansion_ebs(data):
    # 1. 校验
    disk = get_disk_info(data["disk_id"])
    if disk["status"] not in ["available", "in-use"]:
        raise BusinessError("当前云盘状态不可扩容")

    new_size = data["new_size"]
    if new_size <= disk["storage_space"]:
        raise BusinessError("新容量必须大于当前容量")

    # 2. 价格计算（扩容只是变更了容量，按新的配置重新计费）
    price = calculate_price(
        disk_type=disk["disk_feature"],
        new_size=new_size,
        region=disk["region"]
    )

    # 3. 异步执行扩容
    event = create_expansion_event(disk, new_size)

    # 4. 如果云盘正在挂载中，扩容完成后通知 ECS 重新扫描磁盘
    if disk["status"] == "in-use":
        ecs_id = disk["attached_to"]
        # 扩容完成后，ECS 需要 re-scan 磁盘才能识别新大小
        add_post_hook(event, "notify_ecs_rescan", ecs_id)

    return {"event_id": event.id, "price": price}
```

**面试话术：**

> "云盘扩容有两类——容量扩容和性能调整。容量扩容改动 `volume_info[0]['size']`；IOPS/Mbps 性能调整走 `CHANGE_IOPS_MBPS` 事件，可以单独调 IOPS、带宽，或两者一起调。扩容都是在线操作，不需要先卸载。本地盘扩容和云盘扩容走不同的 task 类型（`UPDATE_DISK` vs `UPDATE_LOCAL_DISK`），因为本地盘直接挂在宿主机上。"

---

## Q5: 云盘库存与运维管理

**场景理解：**

ecs-business 是运维管理台，负责物理机磁盘库存管理和云盘运维操作。运维人员可以查看每个物理机还有多少磁盘容量、管理存储池、调整 IOPS/Mbps。

### 5.1 ecs-business 的 EbsView（运维视角，27 个端点）

```python
# ecs-business/apps/api/views/ebs.py — 真实源码（运维管理台）
class EbsView(GenericViewSet):

    # ===== 云盘 CRUD（运维侧）=====
    @action(methods=['POST'], url_path='create_disk', ...)
    def create_disk(self, req, data):
        op = EbsOperateService(data['customer_id'], req.user.username, OpSource.CLOUD_OP)
        res = op.api_create_ebs(data)
        return res

    @action(methods=['POST'], url_path='delete', ...)       # 逻辑删除
    @action(methods=['POST'], url_path='destroy_disk', ...) # 物理销毁
    @action(methods=['POST'], url_path='recover', ...)      # 恢复

    # ===== 库存与容量管理 =====
    @action(methods=['GET'], url_path='disk_info', ...)     # 云盘规格
    @action(methods=['POST'], url_path='get_disk_limit', ...)    # 云盘余量
    @action(methods=['GET'], url_path='get_pool_info', ...)      # 存储池售卖率
    @action(methods=['POST'], url_path='handle_pool_info', ...)  # 设置售卖状态
    @action(methods=['GET'], url_path='search_pool_add_rate', ...) # 30天售卖率

    # ===== 性能调整 =====
    @action(methods=['POST'], url_path='change_iops_mbps', ...)   # IOPS/Mbps调整
    @action(methods=['POST'], url_path='iops_mbps_record', ...)   # 操作记录
    @action(methods=['GET'], url_path='get_iops_mbps_limit', ...) # IOPS/Mbps限制
```

### 5.2 EbsServiceRequest 的下游调用（真实端点列表）

```python
# ecs-business/utils/request_service.py — 真实源码
class EbsServiceRequest(BusinessRequest):
    EBS_SERVICE_URL = settings.EBS_SERVICE_URL

    # 向下游 ebs-service 发起的 HTTP 端点（部分）
    DISK_MOUNT_URL       = '/ebs_service/v1/ebs/mount/'
    DISK_UNMOUNT_URL     = '/ebs_service/v1/ebs/unmount/'
    DISK_CREATE_URL      = '/ebs_service/v1/ebs/api_create_disk/'
    DISK_UPDATE_URL      = '/ebs_service/v1/ebs/expansion/'
    DISK_LIMIT_URL       = '/ebs_service/v1/ebs/get_disk_limit/'
    EBS_PRICE_URL        = '/ebs_service/v1/ebs_data/get_ebs_price/'
    DISK_LIST_URL        = '/ebs_service/v1/ebs_data/disk_list/'
    EBS_QUOTA_URL        = '/ebs_service/v1/ebs_data/check_ebs_quota/'
    SNAPSHOT_CREATE_URL  = '/ebs_service/v1/snapshot/api_create_snapshot/'
    SNAPSHOT_PRICE_URL   = '/ebs_service/v1/snapshot_data/get_snapshot_price/'
    # ... 30+ 个端点

    # 所有请求走同一个基类方法
    @classmethod
    def req(cls, url, method, param):
        res_data = cls.request(url, method, **param)
        if res_data.get('code') == 'Success':
            return res_data['data']
        else:
            raise BusinessException(res_data, extra_msg=res_data.get('message', ''))

    @classmethod
    def disk_mount_info(cls, param):   return cls.post(cls.DISK_MOUNT_URL, param)
    @classmethod
    def disk_create_ebs(cls, param):   return cls.post(cls.DISK_CREATE_URL, param)
    @classmethod
    def disk_expansion_info(cls, param): return cls.post(cls.DISK_UPDATE_URL, param)
```

**面试话术：**

> "运维侧 EBS 比用户侧多了库存管理、存储池管控、IOPS/Mbps 调整等端点。`EbsServiceRequest` 封装了 30+ 个下游 HTTP 端点，所有请求走统一的 `req()` 基类方法——成功检查 `code == 'Success'` 后返回 `data`，失败抛 `BusinessException`。存储池管理包括查看 30 天售卖率、设置售卖阈值、禁售操作等。"

---

## Q6: EBS 操作失败回滚与最终一致性

**场景理解：**

云盘操作是异步的——任务生成后写入 `CloudOsTask` 表，Spooler 轮询执行。如果中间失败，必须正确回滚磁盘状态。

### 6.1 失败回滚（真实源码）

```python
# ecs-service/spool_service/task_service/ebs_task_service.py — 真实源码
class EbsTaskSet(CommonTaskSet):

    def common_op_ebs_error(self, ebs_task):
        disk_id = ebs_task.cloud_id
        task_type = ebs_task.task_type
        event = ebs_task.event
        event_param = event.event_param

        with transaction.atomic():
            kwargs = {'update_time': datetime.datetime.now()}

            # 挂载失败 → 清空ECS关联，状态→待挂载
            if task_type == EbsEventType.MOUNT_DISK:
                kwargs['ecs_id'] = ''
                kwargs['status'] = DiskResourceStatus.WAITING

            # 卸载失败 → 状态→使用中
            elif task_type == EbsEventType.UNMOUNT_DISK:
                kwargs['status'] = DiskResourceStatus.RUNNING

            # 其他操作失败 → 状态→错误
            else:
                kwargs['status'] = DiskResourceStatus.ERROR

            CloudOsDisk.objects.filter(disk_id=disk_id, is_valid=True).update(**kwargs)

            # 检查是否需要回收处理
            CommonTaskSet.check_recycling(disk_id, ebs_task.task_param, CallBackTaskStatus.FAILED)

            # 回调ECS状态
            if event_param.get('ecs_disk_dict', {}):
                EbsTaskSet.callback_ecs_status(ebs_task)
```

### 6.2 事件→任务链

```python
# ecs-service/spool_service/event_service/ebs_event_service.py
# 删除云盘时连带删除关联快照
if event_type == EbsEventType.DELETE_DISK:
    if is_delete_not_infinite:
        # 找出关联的非无限快照，为每个快照生成删除任务
        snapshot_objs = CloudOsSnapshot.objects.filter(disk_id=disk.disk_id, is_valid=1, is_infinite=False)
        for snapshot in snapshot_objs:
            snapshot_task = cls.create_delete_snapshot_task(
                snapshot, region_id, az_code, customer_id, az_id, now, event)
            ebs_task_list.append(snapshot_task)

# 销毁云盘时：force 标记 + 删除所有快照
if event_type == EbsEventType.DESTROY_DISK:
    global_context['force'] = 1
    snapshot_objs = CloudOsSnapshot.objects.filter(disk_id__in=disk.disk_id, is_valid=1)
    for snapshot in snapshot_objs:
        snapshot_task = cls.create_delete_snapshot_task(...)
        ebs_task_list.append(snapshot_task)
```

**面试话术：**

> "一致性保证有两层。一是**事务保护**——`with transaction.atomic()` 包裹状态回滚，失败时磁盘状态恢复为操作前的值（挂载失败清 `ecs_id`，卸载失败恢复为 `RUNNING`）。二是**关联资源清理**——删除云盘时连带删除关联的快照链。每个快照生成独立的子任务，和主任务一起写入任务列表，保证云资源的级别一致。"

---

## Q7: URL Rewrite 中间件——多云盘供应商路由

**场景理解：**

ecs-business 负责物理机磁盘库存的管理和维护。运维人员可以查看每个物理机还有多少磁盘空间可以分配给云盘。

```python
# ecs-business/ebs_service.py（运维视角）
class EbsOperateService:
    def get_disk_inventory(self, host_id):
        """查某个物理机的磁盘库存"""
        # 1. 调虚拟化层获取物理磁盘总容量和已用量
        host_info = compute_admin.get_host_disk(host_id)

        # 2. 调 ebs-service 获取该物理机上已分配的云盘列表
        allocated_disks = ebs_request.get_disk_list(host_id=host_id)

        # 3. 计算可用容量
        total = host_info["total_capacity"]
        used = sum(d["storage_space"] for d in allocated_disks)
        available = total - used

        return {
            "host_id": host_id,
            "total": total,
            "used": used,
            "available": available,
            "disk_count": len(allocated_disks),
        }

    def get_ebs_price(self, data):
        """云盘价格查询——按磁盘类型、容量、计费方式"""
        # 磁盘类型: SSD(1) / SATA(0)
        # 计费方式: 按量付费(0) / 包年包月(1)
        order_data = {
            "goods_id": data["ebs_goods_id"],      # 商品的 SKU ID
            "disk_feature": data["disk_feature"],   # SSD/HDD
            "storage_space": data["storage_space"], # 容量
            "billing_method": data["billing_method"],
            "region": data["region"],
        }
        return order_service.calculate_price(order_data)
```

**面试话术：**

> "库存管理是运维视角的核心功能。运维人员需要知道每个物理机上还有多少磁盘容量可分配。库存统计需要调两个数据源——虚拟化层查物理磁盘总量，ebs-service 查已分配的云盘列表，差额就是可用容量。价格计算走 order-service 微服务，按照磁盘类型（SSD/HDD）、容量大小、计费方式三个维度定价。"

---

## Q6: 如何保证云盘操作的最终一致性

**场景理解：**

用户创建云盘 → Spooler 异步执行 → 中间可能失败（虚拟化层超时、网络抖动）。怎么保证用户看到的云盘状态是准确的？

**设计思路：**

```
1. 事件表（CloudOsEvent）记录所有操作
2. 每个事件 → 拆成多个子任务
3. 子任务可重试（不在界面上显示失败，后台重试 3 次）
4. 全部子任务成功 → 事件状态 = completed
5. 任一子任务最终失败 → 事件状态 = failed, 云盘状态回滚为 error
```

```python
# 最终一致性保证
class EventHandler:
    MAX_RETRY = 3

    def execute_task(self, task):
        for attempt in range(1, self.MAX_RETRY + 1):
            try:
                result = task.execute()
                if result.success:
                    return result
            except Exception as e:
                if attempt == self.MAX_RETRY:
                    # 最终失败：回滚云盘状态
                    disk = Disk.objects.get(id=task.disk_id)
                    disk.status = "error"
                    disk.status_message = f"操作失败(已重试{self.MAX_RETRY}次): {e}"
                    disk.save()
                    raise
                time.sleep(2 ** attempt)  # 指数退避
```

**面试话术：**

> "云盘是用户的核心资产，状态必须可靠。我们通过事件表 + 子任务重试来保证最终一致性——每个操作都记录在事件表里，子任务失败后指数退避重试 3 次。如果还是失败，云盘状态标记为 error，用户可以在控制台看到'操作失败'并重新发起。关键是**状态对用户透明**——是 processing 就是 processing，是 error 就是 error，不会出现'在后台卡住了用户不知道'的情况。"

---

## Q7: URL Rewrite 中间件——多云盘供应商路由

**场景理解：**

gic-business 有两套 API：`apps/api/views/ebs.py`（单云 CDS）和 `apps/multi_api/views/multi_ebs.py`（多云）。中间件根据 region 自动 URL 重写，对前端透明。

### 7.1 中间件 + 多套 API 架构

```
用户请求 /gic_business/v1/ebs/create_disk/
    ↓ URLRewriteMiddleware
    │ region 在 MULTI_CLOUD_REGIONS?
    │ YES → 重写为 /multi_gic_business/v1/ebs/create_disk/
    │       路由到 apps/multi_api/views/multi_ebs.py
    │ NO  → 保持原 URL
    │       路由到 apps/api/views/ebs.py
```

### 7.2 gic-business 的三套 API 体系

```python
# gic-business 同时维护三套 EBS API：

# 1. 单云 API — apps/api/views/ebs.py（EbsView, 35+ 端点）
# 2. 多云 API — apps/multi_api/views/ （multi_ebs.py 等，调用第三方云 SDK）
# 3. OpenAPI — apps/api/views/ebs_open_api.py（对外标准API, action分发）
# 4. Internal API — apps/api/views/ebs_internal_api.py（内部产品调用）
```

### 7.3 代码图谱中的依赖关系

从 `cloud-os-ecs-business-代码图谱.md` 可以看到：

```mermaid
EbsView → EbsOperateService → EbsServiceRequest → cos-ebs-service (下游)
                                                      ├── mount
                                                      ├── unmount
                                                      ├── create_disk
                                                      ├── expansion
                                                      └── disk_list
```

`EbsServiceRequest` 的 `EBS_SERVICE_URL` 在 settings 中配置，通过修改配置可以指向不同的下游服务。

**面试话术：**

> "gic-business 同时维护三套 EBS API——单云 CDS 的 `apps/api/views/ebs.py`（35+ 端点）、多云的 `apps/multi_api/views/`（调用第三方云 SDK）、OpenAPI 网关的 `ebs_open_api.py`（action 分发）。URL Rewrite 中间件在请求到达 View 层之前根据 region 决定路由到哪套 API。`EbsServiceRequest` 封装了 30+ 个下游端点，所有请求走统一的 `req()` 基类——成功检查 `code == 'Success'`，失败抛 `BusinessException`。"

---

---

## Q8: uWSGI Spooler 异步任务引擎是怎么工作的？

**场景理解：**

创建云主机、挂载云盘这些操作从几秒到几分钟不等，不能阻塞 HTTP 请求。Celery 需要额外的 RabbitMQ + Worker 进程，运维成本高。团队选了 uWSGI Spooler——uWSGI 自带的异步任务机制，零额外依赖。

**核心流程：**

```
HTTP请求 → View → 写入CloudOsEvent → 返回event_id
                                          ↓
                              Spool Consumer (轮询)
                                          ↓
                              拆分子任务 → CloudOsTask
                                          ↓
                              调虚拟化层 compute-admin
                                          ↓
                              轮询结果 → 更新状态 → 回调计费
```

**真实源码：**

```python
# ecs-service/spool_service/spool_consumer.py — 真实源码
# 核心入口：uWSGI @spool 装饰器 → EventCenter.event_route()

@spool
def spool_task(args):
    """uWSGI Spooler 入口——每次轮询调用这个函数"""
    request_id = create_uuid()
    event_id = args['event_id']
    event_type = args['event_type']
    close_old_connections()              # 关闭旧的数据库连接
    EventCenter(event_type, event_id, request_id).event_route()


class EventCenter(object):
    RC = RedisHelper()                   # Redis 客户端（用于分布式锁）

    def event_route(self):
        """事件路由——Spooler 的核心调度逻辑"""
        # 1. 时间检查：事件是否到了处理时机
        if not self._check_time(self.event):
            spool_task.spool(event_id=self.event_id, event_type=self.event_type)
            return

        flag = False
        try:
            # === 2. Redis 分布式锁：防止同一事件被重复处理 ===
            flag = self.RC.set_nx_key(self.event_id, self.event_type)
            if not flag:
                logger.info('事件<{}>获取锁失败, 已有相同事件在执行'.format(self.event_id))
                return
            self.RC.set_expire(self.event_id, 180)   # 锁 180 秒过期

            # 3. 状态路由
            if self.event.status == EcsTaskStatus.INIT:
                if CloudOsTask.objects.filter(event_id=self.event_id).exists():
                    # 已有子任务 → 检查子任务状态
                    continue_flag = self._check_task_status()
                else:
                    # 无子任务 → 根据事件类型创建子任务
                    try:
                        if self.event_supplier == CloudSupplierType.CDS:
                            continue_flag = self._common_init_event(
                                self._event_handle_route(self.event.event_type))
                        else:
                            continue_flag = self._common_init_event(
                                self._multi_cloud_event_handle_route(self.event.event_type),
                                supplier=self.event_supplier)
                    except Exception as e:
                        logger.exception('事件初始化失败event_id:{}'.format(self.event_id))
                        continue_flag = True

            elif self.event.status == EcsTaskStatus.DOING:
                # 事件进行中 → 轮询子任务状态
                continue_flag = self._check_task_status()
            else:
                continue_flag = False

        except Exception as e:
            continue_flag = True
        finally:
            # 4. 释放 Redis 锁
            if flag and self.RC.get_key(self.event_id):
                self.RC.delete_key([self.event_id])

        # 5. 未完成 → 重新注册到 Spooler 等待下次执行
        if continue_flag:
            time.sleep(5)
            spool_task.spool(event_id=self.event_id, event_type=self.event_type)
```

任务状态汇总逻辑：

```python
# spool_consumer.py — 事件状态 = 子任务状态的汇总
def _gen_event_task(self):
    ecs_task_status_list = CloudOsTask.objects.filter(
        event_id=self.event_id).values_list('status', flat=True)

    all_finish_flag = True
    part_success_flag = False
    part_fail_flag = False

    for task_status in ecs_task_status_list:
        if task_status in EcsTaskStatus.DOING_STATUS_SET:
            all_finish_flag = False
            break
        elif task_status == EcsTaskStatus.SUCCESS:
            part_success_flag = True
        elif task_status == EcsTaskStatus.FAILED:
            part_fail_flag = True

    if all_finish_flag:
        if part_fail_flag:
            if not part_success_flag:
                event_status = EcsTaskStatus.FAILED        # 全部失败
            else:
                event_status = EcsTaskStatus.PART_FAIL     # 部分失败
        else:
            event_status = EcsTaskStatus.SUCCESS            # 全部成功
    else:
        event_status = EcsTaskStatus.DOING                 # 进行中
    return event_status
```

**面试话术：**

> "Spooler 的工作原理是**事件表 + 子任务表 + Redis 锁**的组合。`@spool` 装饰器是 uWSGI 自带的——把函数注册为 Spooler 任务，uWSGI 进程池里有专门的 Spooler 线程轮询执行。`EventCenter.event_route()` 是核心调度器：先检查时间间隔（处理间隔至少 5 秒避免底层接口压力过大），然后 `Redis.set_nx_key(event_id)` 获取分布式锁防止同一事件被多个 Spooler 线程并发处理，再根据事件状态路由——INIT 创建子任务、DOING 轮询子任务进度、完成则关锁。`_gen_event_task()` 把子任务状态汇总为事件状态——全部成功→SUCCESS、部分失败→PART_FAIL、全部失败→FAILED、有进行中→DOING。"

---

## Q9: OpenAPI 网关——action 分发模式

**场景理解：**

首都在线对外暴露标准 API 给客户（类似于 AWS API），客户通过一个统一的入口 URL，用 `Action` 参数指定想要的操作。

gic-business 的 `apps/api/views/ebs_open_api.py` 负责 EBS 相关的 OpenAPI 网关。

**面试话术：**

> "OpenAPI 网关的核心是**action 分发模式**。所有外部 API 请求打到同一个 URL，通过请求参数中的 `Action` 字段路由到对应处理函数。gic-business 的 OpenAPI 覆盖了 ECS、EBS、快照、镜像四大领域，30+ 种 action。网关层做了统一的签名验证——防止请求被篡改和重放。和 AWS API 的设计理念一致：客户用 `CreateDisk` 而不是 `POST /api/v1/disks`。"

---

## Q10: 超大模块管理——单文件 571KB 的 ecs_service.py

**场景理解：**

ecs-service 的核心文件 `ecs_service.py` 有 **571KB**，是整个项目最庞大的文件，包含了 ECS 创建/删除/启停/迁移/驱散等全部逻辑。

**面试话术：**

> "571KB 的单文件是历史遗留问题——项目初期为了快速交付，所有 ECS 逻辑写在一个 backend 文件里。虽然不符合'小而美'的设计原则，但在当时的场景下有它的合理性：ECS 的操作之间高度耦合，拆文件会导致循环引用。我的态度是——不追求完美架构，追求可交付。如果团队决定重构，我的方案是按操作域拆：create_ecs.py、migrate_ecs.py、power_ecs.py，每个 100-200KB，接口不变。"

---

## Q11: 多数据库路由——4 个 MySQL 如何管理？

**场景理解：**

三个服务共享 4 个 MySQL 数据库：

| 数据库 | 用途 |
|------|------|
| cloud_os | 核心业务数据（ECS、云盘、主机、事件、任务） |
| cdscp | 客户配置数据（用户、计费） |
| ucenter | 用户中心（SSO 认证 token） |
| nas | NAS 存储相关 |

**Django 多数据库配置：**

```python
# settings.py
DATABASES = {
    'default': {  # cloud_os 是默认库
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'cloud_os',
    },
    'cdscp': {
        'NAME': 'cdscp',
    },
    'ucenter': {
        'NAME': 'ucenter',
    },
    'nas': {
        'NAME': 'nas',
    },
}

# ORM 使用 —— 每个 Model 的 Meta 指定数据库
class CloudOsDisk(models.Model):
    class Meta:
        app_label = 'cloud_os'
        db_table = 'cloud_os_disk'

class CustomerUser(models.Model):
    class Meta:
        app_label = 'cdscp'
        db_table = 'cdscp_customer_user'

# 跨库查询时手动指定 using
users = CustomerUser.objects.using('cdscp').filter(is_valid=True)
```

**面试话术：**

> "4 个库是历史演进的结果——cloud_os 是业务核心库，cdscp 和 ucenter 是公司级共享服务（客户数据、SSO），nas 是存储域专属。Django 多数据库通过 Model 的 `Meta.app_label` + `using()` 方法路由。跨库 JOIN 在 Django ORM 中不可行——如果业务需要跨库关联，只能在应用层做两次查询后在 Python 里 join。"

---

## Q12: Kafka 状态同步——消费虚拟化层上报

**场景理解：**

虚拟化层（compute-admin）的物理机和虚拟机状态变更后，通过 Kafka 上报。ecs-service 的 `KafkaConsumerHelper` 消费消息后直接更新 MySQL，不经过 Spooler 管道（因为是单向状态同步，不是用户触发的操作）。

**真实源码：**

```python
# ecs-service/utils/kafka_kit.py — 真实源码
from kafka import KafkaConsumer, TopicPartition

class KafkaConsumerHelper(object):
    def __init__(self, bootstrap_servers, group_id):
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.op_user = 'kakfa_sync'              # 系统用户标识
        self.instance_type_list = ['vm', 'host']  # 同步两种资源类型
        self.status_map = {
            'RUNNING':  EcsResourceStatus.RUNNING,
            'SHUTDOWN': EcsResourceStatus.SHUTDOWN,
            'OFF':      HostPowerStatus.SHUTDOWN,
            'ON':       HostPowerStatus.RUNNING
        }

    def get_event_data(self, topic, partition):
        """消费指定 topic 的指定 partition"""
        logger.info('开始消费数据：topic：{}，partition：{}'.format(topic, partition))
        local_consumer = KafkaConsumer(
            group_id=self.group_id,
            bootstrap_servers=self.bootstrap_servers,
            consumer_timeout_ms=5000)
        tp = TopicPartition(topic, partition)
        local_consumer.assign([tp])

        for msg in local_consumer:
            data = eval(msg.value.decode('utf-8'))
            instance_type = data.get('instance_type')  # 'vm' or 'host'
            event_info = data.get('event_info', {})
            instance_id = data.get('instance_id')
            timestamp = int(str(data.get('timestamp'))[:10])

            # ===== 时间戳校验：防止旧消息覆盖新状态 =====
            message_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))

            if instance_type == 'vm':
                # 查该VM的最新任务更新时间
                final_task_obj = CloudOsTask.objects.filter(
                    cloud_id=instance_id).order_by('-id').first()
                if message_time < str(final_task_obj.update_time):
                    logger.info('消息时间早于最新任务更新时间，跳过')  # 防止旧消息覆盖
                    continue

                # 直接更新 ECS 状态
                CloudOsEcs.objects.filter(
                    ecs_id=instance_id,
                    status__in=EcsResourceStatus.BEFORE_KAFKA_SYNC_STATUS_LIST
                ).update(status=power_status)

                # 同步修复挂载盘状态（处于 error 的盘恢复为 running）
                CloudOsDisk.objects.filter(
                    ecs_id=ecs_ins_id, is_valid=True,
                    status=DiskResourceStatus.ERROR
                ).update(status=DiskResourceStatus.RUNNING)

            else:  # host——物理机
                machine_status = event_info.get('machine_status')
                # 电源+机器状态组合校验
                if status in self.pass_power_status_list and \
                   machine_status in self.pass_machine_status_list:
                    CloudOsHost.objects.filter(
                        host_id=instance_id, is_valid=True,
                        update_time__lt=message_time
                    ).exclude(
                        machine_status__in=[HostMachineStatus.OFF_SHELVES,
                                            HostMachineStatus.ONLINE_MAINTENANCE]
                    ).update(power_status=power_status, machine_status=machine_status)
```

**面试话术：**

> "Kafka Consumer 是独立的后台线程，直接消费虚拟化层上报的状态变更消息。关键设计有两个——**时间戳校验**防止旧消息覆盖新状态（比对新消息时间和 `CloudOsTask.update_time`），**状态过滤**只更新特定状态范围内的资源（`BEFORE_KAFKA_SYNC_STATUS_LIST`）。和 Spooler 的区别是：Kafka 是**源端被动上报**，不需要拆分任务链，直接写 MySQL；Spooler 是**用户主动操作**，需要事件→任务→轮询→回调的四步流程。"

---

## Q13: Redis 的使用场景（真实代码）

**场景理解：**

三个服务共享 Redis Cluster。真实源码在 `utils/redis_kit.py`——基于 `rediscluster.StrictRedisCluster`。

**真实源码：**

```python
# ecs-service/utils/redis_kit.py — 真实源码
from rediscluster import StrictRedisCluster as rc

class RedisHelper(object):
    DEFAULT_EXPIRE_TIME = 300  # 默认过期 5 分钟
    MAX_COMMANDS = 10          # Pipeline 批量上限

    def __init__(self):
        self.redis_nodes = settings.REDIS_CLUSTER_NODES
        self.password = getattr(settings, 'REDIS_CLUSTER_PASSWORD', None)
        self.r = rc(startup_nodes=self.redis_nodes,
                     decode_responses=True, password=self.password)

    # === 基础 K-V ===
    def set_key(self, key, value, expire=DEFAULT_EXPIRE_TIME):
        self.r.set(key, value, ex=expire)

    def get_key(self, key):
        return self.r.get(key)

    # === JSON 缓存 ===
    def set_json_key(self, key, value, expire=DEFAULT_EXPIRE_TIME):
        self.r.set(key, json.dumps(value), ex=expire)

    def get_json_key(self, key):
        value = self.get_key(key)
        return json.loads(value) if value else value

    # === Pipeline 批量操作 ===
    def pipe_set_key(self, data, expire=DEFAULT_EXPIRE_TIME):
        """批量 SET——一次网络往返写多个 key"""
        r_pipe = self.r.pipeline()
        for key, value in data.items():
            r_pipe.set(key, json.dumps(value) if isinstance(value, dict) else value, ex=expire)
        r_pipe.execute()

    def pipe_get_json_key(self, keys=[]):
        """批量 GET——一次网络往返读多个 key"""
        records = {}
        r_pipe = self.r.pipeline()
        for index, key in enumerate(keys):
            r_pipe.get(key)
        for (k, v) in zip(keys, r_pipe.execute()):
            records[k] = json.loads(v) if v else v
        return records

    # === 分布式锁（SETNX）===
    def set_nx_key(self, key, value):
        """SETNX——键不存在才写，用于分布式锁"""
        return self.r.setnx(key, value)

    def set_expire(self, key, time=DEFAULT_EXPIRE_TIME):
        self.r.expire(key, time)

    def delete_key(self, names):
        return self.r.delete(*names)
```

**三个实际使用场景：**

| 场景 | 方法 | 代码位置 |
|------|------|------|
| **分布式锁** | `RC.set_nx_key(event_id, event_type)` + `set_expire(event_id, 180)` | `spool_consumer.py:540` |
| **热点缓存** | `set_json_key(key, value)` / `get_json_key(key)` | 用户信息、机房配置 |
| **批量查询** | `pipe_get_json_key(keys)` | 一次查多个资源的状态 |

**面试话术：**

> "Redis 在三处核心使用。最关键是**分布式锁**——Spooler 的 `event_route()` 用 `SETNX(event_id)` 防止同一事件被多个 Spooler 线程并发处理，180 秒自动过期防死锁。**热点缓存**用 `set_json_key/get_json_key` 存用户信息和机房配置，5 分钟过期，减少 MySQL 查询。**Pipeline 批量**用于一次查询多个 key——`pipe_get_json_key` 把多次 GET 合并成一次网络往返，避免循环 RTT。Redis 是集群模式（`rediscluster.StrictRedisCluster`），配置节点列表在 `settings.REDIS_CLUSTER_NODES`。"

---

## Q14: 审计日志的设计

**场景理解：**

ecs-business 负责运维审计——每一项运维操作（主机上线/下架/维护，云盘批量删除等）都记录到 `CloudOsOperationList` 表。

```python
# ecs-business/apps/api/backend/ebs_service.py — 真实源码
def set_operation(self, disk_ids, content, status, operation_type=OperationType.CHANGE, under_msg={}, fail_reason=''):
    """批量记录运维操作日志"""
    operation_list = []
    disk_objs = CloudOsDisk.objects.select_related('az').filter(
        disk_id__in=disk_ids).values('disk_id', 'name', 'az__az_id')

    for disk in disk_objs:
        operation_list.append(CloudOsOperationList(
            operation_id=create_uuid(),
            cloud_type=LogType.DISK,
            cloud_id=disk['disk_id'],
            content=content,                          # 操作内容
            response=fail_reason + under_msg[disk_id] if under_msg else fail_reason,
            status=status,                             # 成功/失败
            op_user=self.op_user,                      # 操作人
            operation_type=operation_type,             # 操作类型
            cloud_name=disk['name'],
            az_id=disk['az__az_id']
        ))

    CloudOsOperationList.objects.bulk_create(operation_list)
```

**面试话术：**

> "审计日志的核心是**不可删除**和**完整记录**。`CloudOsOperationList` 表只有 INSERT 没有 UPDATE/DELETE。每个操作记录包含操作人(`op_user`)、操作内容、操作结果、失败原因。`bulk_create` 批量写入提高性能。审计日志还要关联到具体云资源——方便排查'这块云盘什么时候被谁删了'。运维侧所有危险操作（批量删除、物理销毁）都强制记录。"

---

## Q15: SSO 认证 + 权限校验（真实代码）

**场景理解：**

两个面向用户的业务服务（gic-business、ecs-business）使用 SSO Token 认证，纯内部调用的 ecs-service 不做认证。两个服务的 Auth 实现略有不同，但核心流程一致。

### 15.1 gic-business 的 @login_required（用户侧）

```python
# gic-business/apps/auth.py — 真实源码
from utils.request_service import UserCenterRequest
from utils.redis_kit import RedisHelper

def login_required(func):
    """GIC 用户控制台的登录验证装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        req = args[1]
        # === 1. 从三个位置提取 Token ===
        token = (req.GET.get('token')                         # URL 参数
                 or req.headers.get(settings.OSS_TOKEN_HEADER_NAME)  # Header
                 or req.COOKIES.get(settings.OSS_TOKEN_COOKIE_NAME)) # Cookie

        if not token:
            return get_redirect_login_res()     # 401 + SSO 重定向URL

        # === 2. 调 UserCenter 验证 Token ===
        try:
            res = UserCenterRequest.get_user_info(headers={'Access-Token': token})
        except BusinessException:
            return get_redirect_login_res()

        # === 3. 提取用户信息注入到请求参数 ===
        user_data = res['user']
        customer_data = res['customer']
        kwargs.setdefault('data', {})
        kwargs['data']['customer_id'] = customer_data['id']
        kwargs['data']['user_id'] = user_data['acct_user_id']
        kwargs['data']['user_name'] = user_data['username']
        kwargs['data']['main_user_id'] = CustomerUser.get_main_user_id(customer_data['id'])
        kwargs['data']['user_ip'] = get_user_ip_by_request(req)
        kwargs['data']['customer_source'] = customer_data.get('customer_source', '')

        return func(*args, **kwargs)
    return wrapper
```

### 15.2 ecs-business 的 TokenAuthBackend（运维侧）

```python
# ecs-business/apps/auth.py — 真实源码
from django.contrib.auth.backends import ModelBackend

class TokenAuthBackend(ModelBackend):
    """Django 自定义认证后端——根据 SSO Token 验证运维用户"""

    def authenticate(self, token=None, **kwargs):
        usr = login_ucenter_user(token)   # 调 ucenter 验证 Token
        return usr if usr else None

    def get_user(self, user_id):
        return User.objects.get(pk=user_id)

def get_user_with_token(token):
    """调 SSO 服务获取用户信息"""
    response = requests.get(
        urljoin(settings.GET_USER_INFO, 'currentInfo'),
        headers={
            'Accept': 'application/json',
            'Access-Token': token,
        }
    )
    if response.status_code != 200:
        return {}
    return response.json()
```

### 15.3 在 View 层的使用

```python
# ecs-business/apps/api/views/ebs.py — 真实源码
class EbsView(GenericViewSet):

    @login_required         # ← gic-business 装饰器
    @response
    def mount(self, req, data):
        op = EbsOperateService(
            data['customer_id'],     # 装饰器注入的客户ID
            req.user.username,        # SSO Token 解析出的用户名
        )
        res = op.api_mount_ebs(data)
        return res

    @login_required
    @response
    def create_disk(self, req, data):
        op = EbsOperateService(
            data['customer_id'],
            req.user.username,
            OpSource.CLOUD_OP          # 运维操作标识
        )
        res = op.api_create_ebs(data)
        return res
```

**面试话术：**

> "认证分两层——`@login_required` 装饰器负责身份认证（是谁），Backend 层的 `check_customer_ecs/check_customer_disks` 负责资源授权（有没有权限操作这个资源）。Token 从三个地方取（URL参数/Header/Cookie），优先级从高到低。验证走 `UserCenterRequest.get_user_info()` 调 SSO 服务，返回用户信息和客户信息。验证成功后把 `customer_id`、`user_name` 等注入到 `kwargs['data']`，后续 Backend 层直接用。ecs-service 不做认证——它是纯内部服务，外部请求由 gic-business/ecs-business 校验后才转发过来。"

---

> 持续更新中 | 最后更新 2026-06-08
