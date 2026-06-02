# LangChain OSS Python 版本演进总结（v1.0 → v1.3）

> 从 2025年10月 v1.0 发布到 2026年5月 v1.3，半年内 3 个大版本迭代。

---

## 目录

- [1. 版本演进时间线](#1-版本演进时间线)
- [2. v1.0.0 — 里程碑发布](#2-v100--里程碑发布)
- [3. v1.1.0 — Model Profiles + 上下文压缩](#3-v110--model-profiles--上下文压缩)
- [4. v1.2.0 — Provider Extras + 严格结构化输出](#4-v120--provider-extras--严格结构化输出)
- [5. v1.3.0 联合发布 — 三大核心突破](#5-v130-联合发布--三大核心突破)
- [6. langgraph v1.2.0 — 企业级可靠性](#6-langgraph-v120--企业级可靠性)
- [7. deepagents v0.6.0 — Agent 会写代码了](#7-deepagents-v060--agent-会写代码了)
- [8. 架构全景图](#8-架构全景图)
- [9. 中间件体系速查](#9-中间件体系速查)
- [10. 版本升级迁移要点](#10-版本升级迁移要点)

---

## 1. 版本演进时间线

| 日期 | 包 | 版本 | 核心主题 |
|------|-----|------|---------|
| 2025-10-20 | langchain + langgraph | **v1.0.0** | 里程碑发布，Agent 框架定型 |
| 2025-11-25 | langchain | **v1.1.0** | Model Profiles、SummarizationMiddleware |
| 2025-12-08 | langchain-google-genai | **v4.0.0** | 统一 Google Generative AI SDK |
| 2025-12-15 | langchain | **v1.2.0** | `create_agent` Provider Extras、ProviderStrategy |
| 2026-02-10 | deepagents | **v0.4.0** | 新沙盒包、OpenAI Responses API 默认 |
| 2026-03-10 | langgraph | **v1.1.0** | 类型安全 streaming v2、Pydantic 强制转换 |
| 2026-04-07 | deepagents | **v0.5.0** | 异步子代理、多模态文件读取 |
| 2026-05-12 | langchain | **v1.3.0** | stream_events v3 协议 |
| 2026-05-12 | langgraph | **v1.2.0** | **DeltaChannel**、超时控制、优雅关闭 |
| 2026-05-12 | deepagents | **v0.6.0** | **CodeInterpreterMiddleware** + QuickJS |

---

## 2. v1.0.0 — 里程碑发布

**日期**：2025-10-20

`langchain` 和 `langgraph` 同时发布 1.0，标志 LangChain Agent 框架进入稳定期。

### 核心变化

+ **废弃旧的 Chain 设计模式**，全面转向 **Agent + Middleware** 架构
+ `create_agent` 成为创建 Agent 的唯一推荐入口（`AgentExecutor` 被移除）
+ 中间件体系确立（3 类：Task Adaptation、Flow Control、Guardrails）

```
# v1.0 之前（旧 Chain 模式，已废弃）
from langchain.chains import LLMChain
chain = LLMChain(llm=model, prompt=prompt)

# v1.0 之后（Agent + Middleware）
from langchain.agents import create_agent
agent = create_agent(
    model="openai:gpt-4o",
    tools=[...],
    middleware=[...],
)
```

---

## 3. v1.1.0 — Model Profiles + 上下文压缩

**日期**：2025-11-25

### 3.1 Model Profiles（新增）

Chat 模型现在暴露 `.profile` 属性（数据源自 [models.dev](https://models.dev)），声明式描述模型能力。

```python
from langchain.chat_models import init_chat_model

model = init_chat_model("openai:gpt-4o")

# 模型自描述能力
model.profile.max_input_tokens              # 最大上下文窗口
model.profile.supports_structured_output    # 是否支持原生结构化输出
model.profile.supports_function_calling     # 是否支持工具/函数调用
model.profile.supports_json_mode            # 是否支持 JSON 模式
model.profile.supports_reasoning            # 是否支持推理/思考
```

**为什么重要**：中间件和 `ProviderStrategy` 可基于 profile 自动决策，不再需要手写 `if provider == "openai"` 这类分支逻辑。

### 3.2 SummarizationMiddleware（重大增强）

长对话 Agent 的**上下文压缩**中间件，v1.1 达到生产可用级别。

```python
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware

agent = create_agent(
    model="openai:gpt-4o",
    tools=[search_tool, db_tool],
    middleware=[
        SummarizationMiddleware(
            model="openai:gpt-4o-mini",    # 用小模型做摘要（省钱）
            trigger={"fraction": 0.8},       # 达 80% 容量自动触发
            keep={"messages": 20},           # 保留最近 20 条完整消息
        ),
    ],
)
```

**触发条件**支持灵活组合：

| 触发方式 | 示例 | 说明 |
|---------|------|------|
| `{"tokens": 80000}` | 达到 8 万 token 时触发 | 固定阈值 |
| `{"fraction": 0.8}` | 达模型窗口的 80% 时触发 | 基于 profile 自动计算 |
| `{"messages": 50}` | 超过 50 条消息时触发 | 消息计数 |
| AND/OR 组合 | `{"fraction": 0.7, "messages": 30}` | 条件组合 |

**保留策略**同样灵活：

```python
SummarizationMiddleware(
    model="openai:gpt-4o-mini",
    trigger={"fraction": 0.8},
    keep={"tokens": 20000},     # 保留最近 2 万 token
    # 或
    keep={"messages": 20},      # 保留最近 20 条
    # 或
    keep={"fraction": 0.3},     # 保留窗口的 30%
)
```

**实际效果**（社区报告）：

| 指标 | 改善 |
|------|------|
| Token 消耗 | **-58%** |
| 响应速度 | **+40%** |
| 信息保留率 | **>90%** |
| 月成本 | **-58%** |

### 3.3 ModelRetryMiddleware（新增）

内置指数退避重试，对不可靠的模型调用自动重试。

```python
from langchain.agents.middleware import ModelRetryMiddleware

agent = create_agent(
    model="openai:gpt-4o",
    middleware=[
        ModelRetryMiddleware(
            max_retries=3,
            backoff_factor=2.0,   # 指数退避倍数
            initial_delay=1.0,    # 初始延迟（秒）
        ),
    ],
)
```

### 3.4 SystemMessage 支持

`create_agent` 的 `system_prompt` 现在可以直接传入 `SystemMessage` 对象：

```python
from langchain_core.messages import SystemMessage

agent = create_agent(
    model="openai:gpt-4o",
    system_prompt=SystemMessage(content="你是专业的数据分析师..."),
)
```

---

## 4. v1.2.0 — Provider Extras + 严格结构化输出

**日期**：2025-12-15

### 4.1 create_agent 的 Provider Extras

v1.2 最重要的功能——为不同模型提供商传递其特有参数，同时保持代码跨提供商通用。

```python
agent = create_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[...],

    # extras — 按 provider 传递特有配置
    extras={
        # Anthropic 特有：思考模式 + computer use
        "anthropic": {
            "thinking": {
                "type": "enabled",
                "budget_tokens": 2000,
            },
            "computer_use": True,
        },
        # OpenAI 特有：推理强度
        "openai": {
            "reasoning_effort": "high",
        },
        # Google 特有
        "google": {
            "safety_settings": [...],
        },
    },
)

# 如果模型切换到 openai:gpt-4o，代码不用改，
# extras["openai"] 的参数自动生效
```

### 4.2 ProviderStrategy 严格 Schema 遵循

`response_format` 通过 `ProviderStrategy` 确保模型严格遵循指定 schema：

```python
from pydantic import BaseModel

class ExtractedInfo(BaseModel):
    name: str
    age: int
    email: str

agent = create_agent(
    model="openai:gpt-4o",
    response_format=ExtractedInfo,
    # ProviderStrategy 自动选择最佳实现方式：
    # OpenAI → native structured outputs
    # Anthropic → tool_use + constrained decoding
    # 其他 → JSON mode + retry
)
```

---

## 5. v1.3.0 联合发布 — 三大核心突破

**日期**：2026-05-12

同一天发布了 langchain v1.3.0、langgraph v1.2.0、deepagents v0.6.0。

### 5.1 stream_events v3 协议

以 **content-block** 为中心的流式协议，取代旧的逐 token 方案。

```python
# v3 提供类型化的分通道投影
async for event in graph.astream_events(..., version="v3"):
    match event:
        case {"event": "run.values"}:
            # 状态更新
            print(event["data"])
        case {"event": "run.messages"}:
            # ChatModelStream — 含 text、reasoning、tool_calls、usage
            msg = event["data"]
        case {"event": "run.lifecycle"}:
            # 节点生命周期事件
            pass
        case {"event": "run.subgraphs"}:
            # 子图事件
            pass
```

**v1/v2 保持不变**，向后兼容。v3 的核心改进：

| 特性 | v1/v2 | v3 |
|------|-------|-----|
| 粒度 | token 级别 | content-block 级别 |
| 类型安全 | 弱 | 强（TypedDict） |
| 子图事件 | 平铺 | 层级投影 |
| reasoning 内容 | 混在 text 中 | 独立通道 |

---

## 6. langgraph v1.2.0 — 企业级可靠性

### 6.1 DeltaChannel — 存储革命

解决长时间运行 Agent 的**存储膨胀**问题。

**问题**：传统方式每一步都写完整快照（如包含 200 条消息的完整列表），N 步 → O(N²) 存储。

**方案**：DeltaChannel 只写**增量**，每 K 步写一次全量快照。

| 指标 | 旧方案（全量快照） | DeltaChannel | 改善 |
|------|-------------------|-------------|------|
| 200 轮对话存储 | 5.3 GB | 129 MB | **减少 41 倍** |
| 增长模式 | O(N²) | O(N) | 适用于长时间会话 |

```python
from langgraph.channels.delta import DeltaChannel
from langgraph.graph.message import add_messages

class MyAgentState(TypedDict):
    messages: Annotated[list, DeltaChannel(
        reducer=add_messages,        # 合并函数
        snapshot_frequency=50,       # 每 50 步写一次全量快照
    )]
```

**原理**：

```
写入时：
  Step 1: [msg1]                          → 增量写入
  Step 2: [msg2]                          → 增量写入
  ...
  Step 50: [msg1...msg50]                 → 全量快照
  Step 51: [msg51]                        → 增量写入

恢复时：
  检查点 → 回溯到最近全量快照 → 重放最多 K 步增量 → 恢复完整状态
```

deepagents v0.6 中的 `messages` 和 `files` 字段默认启用 DeltaChannel，无需配置。

### 6.2 Per-Node Timeout

控制单个节点执行时长。

```python
from langgraph.types import TimeoutPolicy

# 硬超时：绝对时间限制
TimeoutPolicy(run_timeout=120)    # 超过 120 秒直接中断

# 空闲超时：无进度则中断
TimeoutPolicy(idle_timeout=30)    # 30 秒无产出则中断

# 组合使用
TimeoutPolicy(run_timeout=120, idle_timeout=30)
```

**心跳机制**：节点可 yield `{}` 来重置 idle 超时，不写入状态。

```python
async def long_running_node(state):
    for chunk in stream_data():
        process(chunk)
        yield {}  # 告知系统"我还在工作"
    return {"status": "done"}
```

### 6.3 Node-Level Error Handler

所有重试耗尽后执行的恢复函数，支持 **Saga/补偿模式**。

```python
from langgraph.errors import NodeError
from langgraph.types import Command, RetryPolicy

def compensate_on_failure(state: State, error: NodeError) -> Command:
    return Command(
        update={"status": f"已补偿: {error.error}"},
        goto="finalize",
    )

builder.add_node(
    "charge_payment",
    charge_payment,                          # 主逻辑
    retry_policy=RetryPolicy(max_attempts=3),  # 重试 3 次
    error_handler=compensate_on_failure,       # 都失败后执行补偿
)
```

### 6.4 Graceful Shutdown

优雅中断并保存可恢复的 checkpoint。

```python
from langgraph.runtime import RunControl
from langgraph.errors import GraphDrained

control = RunControl()

# 发送中断信号
control.request_drain("需要紧急维护")

try:
    result = graph.invoke(inputs, config, control=control)
except GraphDrained as e:
    # 当前 superstep 完成后已保存 checkpoint
    # 稍后从相同 config 恢复
    result = graph.invoke(None, config)
```

---

## 7. deepagents v0.6.0 — Agent 会写代码了

### 7.1 CodeInterpreterMiddleware

在 Agent 循环中嵌入 **QuickJS 沙盒解释器**，让 Agent 能用代码组合工具，无需多次 LLM 往返。

```python
from deepagents import create_deep_agent
from langchain_quickjs import CodeInterpreterMiddleware

agent = create_deep_agent(
    model="claude-sonnet-4-6",
    middleware=[
        CodeInterpreterMiddleware(
            timeout=10,                # 每次 eval 超时
            memory_limit=128 * 1024 * 1024,  # 128 MiB 内存限制
        ),
    ],
)
# 注意：必须使用 ainvoke（PTC 桥接注册为异步函数）
result = await agent.ainvoke({
    "messages": [{"role": "user", "content": "分析这 3 个搜索结果并总结"}]
})
```

### 7.2 编程式工具调用（PTC）

暴露给解释器的工具可直接在 JavaScript REPL 中调用。

```javascript
// Agent 在沙盒中批量并行调用工具，无需多次 LLM 往返
const results = await Promise.all([
    tools.searchWeb({ query: "langchain v1.3" }),
    tools.searchWeb({ query: "delta channel langgraph" }),
    tools.searchWeb({ query: "deepagents v0.6" }),
]);

// 在沙盒中过滤、转换、聚合结果
const relevant = results
    .flatMap(r => r.items)
    .filter(item => item.date > "2026-01-01");

// 调用 summarization 工具处理聚合结果
await tools.summarize({ text: JSON.stringify(relevant) });

// 只有最终结果返回给 LLM，中间过程不消耗 token
```

**PTC 启用方式**：

```python
# 显式白名单
CodeInterpreterMiddleware(ptc=["search_web", "summarize"])

# 传入工具对象
CodeInterpreterMiddleware(ptc=[search_web_tool, summarize_tool])
```

### 7.3 沙盒安全

| 安全特性 | 默认值 | 说明 |
|---------|--------|------|
| `timeout` | 5 秒 | 每次 eval 超时限制 |
| `memory_limit` | 64 MiB | 跨上下文共享内存上限 |
| `max_ptc_calls` | 256 | 每次 eval 的 PTC 桥接调用上限 |
| `capture_console` | True | 捕获 console.log/warn/error |
| 文件系统 | 无 | 无 fs 访问 |
| 网络 | 无 | 无 fetch/require |
| 进程 | 无 | 无 process 对象 |

### 7.4 效果

早期测试中，CodeInterpreterMiddleware 在特定任务上：

- Token 消耗降低 **35%**
- 工具调用并行度提升（批量并发 vs 逐次串行）
- 复杂多步任务成功率提升

---

## 8. 架构全景图

```
create_agent (入口)
    │
    ├── model: ChatModel
    │   ├── .profile (自描述能力)
    │   │   ├── max_input_tokens
    │   │   ├── supports_structured_output
    │   │   ├── supports_function_calling
    │   │   └── supports_json_mode
    │   └── ProviderStrategy (自动选择最佳能力)
    │
    ├── tools: list[BaseTool]
    │   └── extras: {provider: {key: value}}  (v1.2)
    │
    └── middleware: list[Middleware]  (核心扩展机制)
        │
        ├── 上下文管理
        │   ├── SummarizationMiddleware (v1.1 增强)
        │   ├── ContextEditingMiddleware
        │   └── AnthropicPromptCachingMiddleware
        │
        ├── 重试容错
        │   ├── ModelRetryMiddleware (v1.1 新增)
        │   ├── ToolRetryMiddleware
        │   └── ModelFallbackMiddleware
        │
        ├── 安全护栏
        │   ├── PIIMiddleware
        │   ├── ToolCallLimitMiddleware
        │   ├── ModelCallLimitMiddleware
        │   └── Content Moderation (OpenAI)
        │
        ├── 人工介入
        │   └── HumanInTheLoopMiddleware
        │
        └── 代码执行 (deepagents)
            ├── CodeInterpreterMiddleware (v0.6) → QuickJS 沙盒
            ├── langchain-modal → Serverless 容器
            ├── langchain-daytona → 远程开发环境
            └── langchain-runloop → API 管理沙盒
```

---

## 9. 中间件体系速查

| 分类 | 中间件 | 用途 | 引入版本 |
|------|--------|------|---------|
| 上下文 | SummarizationMiddleware | 长对话自动压缩 | v1.1 |
| 上下文 | ContextEditingMiddleware | 拦截并编辑上下文 | v1.1 |
| 上下文 | AnthropicPromptCachingMiddleware | Anthropic 缓存优化 | v1.0 |
| 容错 | ModelRetryMiddleware | LLM 调用指数退避重试 | v1.1 |
| 容错 | ToolRetryMiddleware | 工具调用重试 | v1.0 |
| 容错 | ModelFallbackMiddleware | 模型降级切换 | v1.0 |
| 安全 | PIIMiddleware | PII 检测和脱敏 | v1.0 |
| 安全 | ToolCallLimitMiddleware | 限制工具调用次数 | v1.0 |
| 安全 | ModelCallLimitMiddleware | 限制模型调用次数 | v1.0 |
| 安全 | Content Moderation | OpenAI 内容审核 | v1.1 |
| 人机交互 | HumanInTheLoopMiddleware | 关键操作人工审批 | v1.0 |
| 规划 | TodoListMiddleware | 任务规划和跟踪 | v1.0 |
| 代码 | CodeInterpreterMiddleware | QuickJS 沙盒代码执行 | deepagents v0.6 |

---

## 10. 版本升级迁移要点

### 从 v1.0 升级到 v1.1

```bash
pip install -U langchain>=1.1.0 langgraph>=1.0.0
```

+ Model profiles 自动可用，无需代码改动
+ 如需 SummarizationMiddleware，添加中间件配置即可
+ SystemMessage 可以替代字符串 system_prompt

### 从 v1.1 升级到 v1.2

```bash
pip install -U langchain>=1.2.0
```

+ `create_agent` 新增 `extras` 参数，可按 provider 传递特有配置
+ `response_format` 启用 `ProviderStrategy` 确保严格 schema 遵循

### 从 v1.2 升级到 v1.3

```bash
pip install -U langchain>=1.3.0 langgraph>=1.2.0
```

+ 可选：在 langgraph 中为长时间 Agent 启用 DeltaChannel
+ 可选：为 langgraph 节点添加 TimeoutPolicy
+ streaming 用户可渐进迁移到 `version="v3"`（v1/v2 不变）
+ deepagents 用户可添加 CodeInterpreterMiddleware

---

> **LangChain 演进主线**：让 Agent **更省 Token**、**跑得更久**、**用更少存储**、**自己写代码组合工具**。

> 来源：
> - [LangChain Official Changelog](https://docs.langchain.com/oss/python/releases/changelog)
> - [DeltaChannel 技术博客](https://www.langchain.com/blog/delta-channels-evolving-agent-runtime)
> - [Deep Agents v0.6 公告](https://www.langchain.com/blog/deep-agents-0-6)
> - [Code Interpreter 技术博客](https://www.langchain.com/blog/give-your-agents-an-interpreter)
> - [LangChain v1.1 公告](https://changelog.langchain.com/announcements/langchain-1-1)
