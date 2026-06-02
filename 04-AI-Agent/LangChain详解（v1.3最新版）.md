# 第 1 章 LangChain 概述

## 什么是 LangChain？

LangChain 是一个用于构建**大语言模型（LLM）应用**的开源框架。它提供了一整套工具和抽象，帮助开发者将 LLM 与外部数据、工具、API 连接起来，构建复杂、可靠的 AI Agent。

:::tips
LangChain 的核心理念：**让 LLM 不仅仅是一个"聊天机器人"，而是一个能思考、能行动、能使用工具的智能体（Agent）。**
:::

### 版本演进

| 版本 | 日期 | 核心变化 |
|------|------|---------|
| 0.x | 2023-2025 | Chain 模式、AgentExecutor |
| **v1.0** | 2025-10 | 废弃 Chain，全面转向 Agent + Middleware 架构 |
| **v1.1** | 2025-11 | Model Profiles、SummarizationMiddleware |
| **v1.2** | 2025-12 | Provider Extras、ProviderStrategy |
| **v1.3** | 2026-05 | stream_events v3、DeltaChannel、CodeInterpreterMiddleware |

> 本书基于 **LangChain v1.3** 编写，覆盖最新 API。

### LangChain 生态三大核心包

```
LangChain 生态
├── langchain          # Agent 框架（create_agent、中间件、工具）
├── langgraph          # 状态图引擎（checkpoint、stream、interrupt）
└── deepagents         # 深度 Agent（文件系统、子代理、沙盒执行）
```

---

# 第 2 章 环境搭建与第一个 Agent

## 安装

```bash
# 核心包
pip install langchain langgraph langchain-core

# 模型提供商
pip install langchain-openai       # OpenAI
pip install langchain-anthropic    # Anthropic
pip install langchain-google-genai # Google Gemini

# Deep Agents（可选）
pip install deepagents

# 开发工具
pip install langgraph-cli          # LangGraph 命令行工具
export LANGSMITH_API_KEY="ls_..."  # 可观测性（推荐）
```

## 第一个 Agent

```python
import os
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent

# 1. 初始化模型
model = init_chat_model(
    "openai:gpt-4o",
    api_key=os.environ["OPENAI_API_KEY"],
    temperature=0.7,
)

# 2. 创建 Agent（最简配置）
agent = create_agent(
    model=model,
    system_prompt="你是一个乐于助人的智能助手。",
)

# 3. 调用
result = agent.invoke({
    "messages": [{"role": "user", "content": "你好，请用一句话介绍自己"}]
})

# 4. 获取回复
print(result["messages"][-1].content)
# 输出：你好！我是一个基于大语言模型的智能助手...
```

### 代码执行流程图

```
create_agent() → 编译成 StateGraph → invoke() → ReAct 循环
                                                    │
                                     ┌──────────────┴──────────────┐
                                     │  思考 → 行动 → 观察 → 再思考  │
                                     └─────────────────────────────┘
```

---

# 第 3 章 create_agent 详解

## 完整参数

`create_agent` 是 LangChain v1.x 创建 Agent 的**唯一推荐入口**。

```python
from langchain.agents import create_agent

agent = create_agent(
    # ========== 核心参数 ==========
    model: str | BaseChatModel,         # 必填：模型或模型字符串
    tools: Sequence[BaseTool] = None,   # 工具列表
    system_prompt: str | SystemMessage = None,  # 系统提示

    # ========== 中间件 ==========
    middleware: Sequence[AgentMiddleware] = (),  # 中间件链

    # ========== 结构化输出 ==========
    response_format: ToolStrategy | ProviderStrategy = None,

    # ========== 状态与上下文 ==========
    state_schema: type[AgentState] = None,   # 自定义状态（TypedDict）
    context_schema: type = None,             # 运行时上下文

    # ========== 持久化 ==========
    checkpointer: Checkpointer = None,       # 短期记忆/对话持久化
    store: BaseStore = None,                 # 长期记忆/跨会话存储

    # ========== 控制 ==========
    interrupt_before: list[str] = None,      # 在这些节点前暂停
    interrupt_after: list[str] = None,       # 在这些节点后暂停
    debug: bool = False,                     # 详细日志
    name: str = None,                        # Agent 名称（建议 snake_case）
    cache: BaseCache = None,                 # 缓存
)
```

## 返回值：CompiledStateGraph

`create_agent` 返回一个编译后的 LangGraph 图，提供以下方法：

| 方法 | 说明 |
|------|------|
| `invoke(input, config)` | 同步运行，返回最终状态 |
| `ainvoke(input, config)` | 异步运行 |
| `stream(input, config, stream_mode)` | 同步流式运行 |
| `astream(input, config, stream_mode)` | 异步流式运行 |
| `get_state(config)` | 获取当前状态快照 |
| `update_state(config, values)` | 手动更新状态 |

### 调用方式

```python
# 输入格式：字典包含 messages 列表
inputs = {
    "messages": [
        {"role": "user", "content": "帮我查一下北京的天气"}
    ]
}

# 同步调用
result = agent.invoke(inputs)

# 异步调用
result = await agent.ainvoke(inputs)

# 获取最终回复
final_message = result["messages"][-1]
print(final_message.content)
```

---

# 第 4 章 工具（Tools）

## 4.1 @tool 装饰器（推荐）

这是最快速、最简洁的定义方式。

```python
from langchain.tools import tool
from pydantic import BaseModel, Field

# 方式 1：最简单写法（类型注解自动生成 schema）
@tool
def get_weather(location: str) -> str:
    """获取指定城市的天气信息。

    Args:
        location: 城市名称，如 '北京'、'上海'
    """
    weather_data = {
        "北京": "晴，18°C，湿度40%",
        "上海": "多云，22°C，湿度65%",
        "深圳": "阵雨，25°C，湿度80%",
    }
    return weather_data.get(location, f"暂无 {location} 的天气数据")

# 方式 2：带自定义 args_schema
class CalculatorInput(BaseModel):
    a: int = Field(description="第一个数字")
    b: int = Field(description="第二个数字")

@tool(args_schema=CalculatorInput)
def multiply(a: int, b: int) -> int:
    """将两个数字相乘。"""
    return a * b

# 放入 Agent
agent = create_agent(
    model=model,
    tools=[get_weather, multiply],
    system_prompt="你是生活助手，可以查天气、做计算。",
)
```

**工具定义的三个关键要素：**

1. **函数签名**：参数名和类型必须清晰（LLM 据此决定传什么参数）
2. **docstring**：LLM 读取这段文本来理解工具的用途，必须精确
3. **返回值**：必须是字符串（str）

## 4.2 StructuredTool.from_function()

需要同时提供**同步和异步**实现时使用。

```python
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

class SearchInput(BaseModel):
    query: str = Field(description="搜索关键词")
    max_results: int = Field(default=5, description="最大结果数")

def search(query: str, max_results: int = 5) -> str:
    """在知识库中搜索信息。"""
    results = knowledge_base.search(query, limit=max_results)
    return "\n".join([r.title for r in results])

async def asearch(query: str, max_results: int = 5) -> str:
    """异步版本。"""
    results = await knowledge_base.asearch(query, limit=max_results)
    return "\n".join([r.title for r in results])

search_tool = StructuredTool.from_function(
    func=search,
    coroutine=asearch,
    name="search_knowledge_base",
    description="在知识库中搜索信息。",
    args_schema=SearchInput,
)
```

## 4.3 继承 BaseTool（最灵活）

适合有复杂状态、需要注入外部依赖的场景。

```python
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type

class DatabaseQueryInput(BaseModel):
    sql: str = Field(description="只读 SQL 查询语句")

class DatabaseQueryTool(BaseTool):
    name: str = "query_database"
    description: str = "执行只读 SQL 查询。禁止 INSERT/UPDATE/DELETE。"
    args_schema: Type[BaseModel] = DatabaseQueryInput

    db_connection: str = "localhost:3306"  # 可配置属性

    def _run(self, sql: str) -> str:
        # 安全检查：禁止写操作
        forbidden = ["insert", "update", "delete", "drop", "alter"]
        if any(word in sql.lower() for word in forbidden):
            return "错误：只允许只读查询（SELECT）"
        return execute_query(self.db_connection, sql)

    async def _arun(self, sql: str) -> str:
        return self._run(sql)
```

## 4.4 三种方式对比

| 方式 | 适用场景 | 复杂度 |
|------|---------|--------|
| `@tool` 装饰器 | 简单函数，快速原型 | 低 |
| `StructuredTool.from_function()` | 需要 sync + async | 中 |
| 继承 `BaseTool` | 复杂逻辑、外部依赖注入 | 高 |

---

# 第 5 章 中间件体系

中间件是 LangChain v1.x 的**核心扩展机制**，让你在不修改 Agent 核心循环的情况下注入自定义逻辑。

## 5.1 中间件概念

```
Agent 执行流程：
  before_agent → [before_model → model → after_model → wrap_tool_call]* → after_agent
                └──────────────── 循环 ────────────────┘
```

**两类钩子：**

| 类型 | 钩子 | 触发时机 |
|------|------|---------|
| 节点式 | `before_agent` | Agent 调用开始（仅一次） |
| 节点式 | `before_model` | 每次模型调用前 |
| 节点式 | `after_model` | 每次模型响应后 |
| 节点式 | `after_agent` | Agent 调用结束（仅一次） |
| 包装式 | `wrap_model_call` | 包裹每次模型调用 |
| 包装式 | `wrap_tool_call` | 包裹每次工具调用 |

**执行顺序（洋葱模型）**：`middleware=[m1, m2, m3]`
- `before_*`：正序 m1→m2→m3
- `after_*`：逆序 m3→m2→m1
- `wrap_*`：嵌套执行

:::color4
**编排原则：安全 > 业务 > 成本 > 监控**。安全检查永远排在最前面。
:::

## 5.2 内置中间件速查

| 中间件 | 功能 | 分类 |
|--------|------|------|
| `SummarizationMiddleware` | 上下文超长时自动总结历史 | 上下文管理 |
| `ContextEditingMiddleware` | 修剪/清除工具调用历史 | 上下文管理 |
| `AnthropicPromptCachingMiddleware` | Anthropic 缓存优化 | 上下文管理 |
| `ModelRetryMiddleware` | LLM 调用指数退避重试 | 容错 |
| `ToolRetryMiddleware` | 工具调用指数退避重试 | 容错 |
| `ModelFallbackMiddleware` | 主模型故障时切换备用模型 | 容错 |
| `PIIMiddleware` | PII 检测和脱敏 | 安全 |
| `ToolCallLimitMiddleware` | 限制工具调用次数 | 安全 |
| `ModelCallLimitMiddleware` | 限制模型调用次数 | 安全 |
| `HumanInTheLoopMiddleware` | 关键操作人工审批 | 人机协同 |
| `TodoListMiddleware` | 任务规划和进度跟踪 | 规划 |
| `LLMToolSelectorMiddleware` | 用小模型预选工具 | 成本优化 |

## 5.3 SummarizationMiddleware（上下文压缩）

长对话 Agent 核心中间件，v1.1 起生产可用。

```python
from langchain.agents.middleware import SummarizationMiddleware

agent = create_agent(
    model="openai:gpt-4o",
    tools=[search_tool, db_tool],
    middleware=[
        SummarizationMiddleware(
            model="openai:gpt-4o-mini",     # 用小模型做摘要，省钱
            trigger={"fraction": 0.8},        # 达到模型窗口 80% 时触发
            keep={"messages": 20},            # 保留最近 20 条完整消息
        ),
    ],
)
```

**触发条件**支持灵活组合：

| 方式 | 示例 | 说明 |
|------|------|------|
| Token 阈值 | `{"tokens": 80000}` | 固定触发线 |
| 容量比例 | `{"fraction": 0.8}` | 基于 model.profile 自动计算 |
| 消息计数 | `{"messages": 50}` | 超过 N 条时触发 |

实际效果（社区报告）：Token 消耗 **-58%**，响应速度 **+40%**。

## 5.4 HumanInTheLoopMiddleware（人工审批）

```python
from langchain.agents.middleware import HumanInTheLoopMiddleware

agent = create_agent(
    model=model,
    tools=[send_email, transfer_money],
    middleware=[
        HumanInTheLoopMiddleware(
            # 这些工具调用需要人工审批
            interrupt_on=["send_email", "transfer_money"],
        ),
    ],
)
```

## 5.5 ModelRetryMiddleware（自动重试）

```python
from langchain.agents.middleware import ModelRetryMiddleware

agent = create_agent(
    model=model,
    middleware=[
        ModelRetryMiddleware(
            max_retries=3,
            backoff_factor=2.0,     # 指数退避：1s → 2s → 4s
            initial_delay=1.0,
        ),
    ],
)
```

## 5.6 自定义中间件

```python
from langchain.agents.middleware import AgentMiddleware, before_model
from langchain.agents.middleware.types import AgentState
from langchain_core.messages import AIMessage

# 方式 1：装饰器（简单场景）
@before_model(can_jump_to=["end"])
def check_message_limit(state: AgentState, runtime) -> dict | None:
    """超过 50 条消息时终止对话"""
    if len(state["messages"]) >= 50:
        return {
            "messages": [AIMessage(content="对话已达上限。")],
            "jump_to": "end",
        }
    return None  # 返回 None 表示不干预

# 方式 2：类（复杂场景）
class MessageLimitMiddleware(AgentMiddleware):
    def __init__(self, max_messages: int = 50):
        super().__init__()
        self.max_messages = max_messages

    def before_model(self, state: AgentState, runtime) -> dict | None:
        if len(state["messages"]) >= self.max_messages:
            return {
                "messages": [AIMessage(content="对话已达上限。")],
                "jump_to": "end",
            }
        return None
```

---

# 第 6 章 Model Profiles 与 ProviderStrategy

## 6.1 Model Profiles

v1.1 起，Chat Model 暴露 `.profile` 属性（数据源自 [models.dev](https://models.dev)），声明式描述模型能力。

```python
from langchain.chat_models import init_chat_model

model = init_chat_model("openai:gpt-4o")

# 模型自描述
print(model.profile.max_input_tokens)              # 128000
print(model.profile.supports_structured_output)    # True
print(model.profile.supports_function_calling)     # True
print(model.profile.supports_json_mode)            # True
print(model.profile.supports_reasoning)            # False
```

**为什么重要**：中间件和 `ProviderStrategy` 基于 profile 自动决策，不再手写 `if provider == "openai"`。

## 6.2 Provider Extras（v1.2）

为不同模型提供商传递其**特有参数**，同时保持代码跨提供商通用。

```python
agent = create_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[...],

    extras={
        # Anthropic 特有功能
        "anthropic": {
            "thinking": {
                "type": "enabled",
                "budget_tokens": 2000,
            },
        },
        # OpenAI 特有功能
        "openai": {
            "reasoning_effort": "high",
        },
    },
)

# 切换到 OpenAI 模型时，代码不用改！
# extras["openai"] 的参数自动生效
```

## 6.3 ProviderStrategy（严格结构化输出）

```python
from pydantic import BaseModel

class UserInfo(BaseModel):
    name: str
    age: int
    email: str

agent = create_agent(
    model=model,
    response_format=UserInfo,  # 自动选择最佳实现方式
    # ProviderStrategy 内部：
    #   OpenAI   → native structured outputs
    #   Anthropic → tool_use + constrained decoding
    #   其他      → JSON mode + retry
)
```

---

# 第 7 章 LangGraph 核心

LangGraph 是 LangChain 的底层引擎，用**状态图**来描述 Agent 的执行流程。

## 7.1 StateGraph 基础

```python
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

# 1. 定义状态
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]  # 追加模式
    current_step: str                                      # 覆盖模式

# 2. 定义节点函数
def router(state: AgentState) -> AgentState:
    """路由节点"""
    last_msg = state["messages"][-1]
    return {"current_step": "thinking"}

def thinker(state: AgentState) -> AgentState:
    """思考节点"""
    # 调用 LLM...
    return {"current_step": "done"}

# 3. 构建图
builder = StateGraph(AgentState)
builder.add_node("router", router)
builder.add_node("thinker", thinker)

builder.add_edge(START, "router")
builder.add_conditional_edges(
    "router",
    lambda s: "thinker" if s["current_step"] == "thinking" else END,
)
builder.add_edge("thinker", END)

# 4. 编译
graph = builder.compile()
```

## 7.2 Checkpoint（持久化）

```python
from langgraph.checkpoint.memory import MemorySaver

# 编译时挂载 checkpointer
graph = builder.compile(checkpointer=MemorySaver())

config = {"configurable": {"thread_id": "session-001"}}

# 运行（每一步自动保存状态）
result = graph.invoke({"messages": [{"role": "user", "content": "你好"}]}, config)

# 获取当前状态
state = graph.get_state(config)
print(state.values)   # 状态数据
print(state.next)     # 即将执行的节点

# 时间旅行——查看所有历史 checkpoint
history = list(graph.get_state_history(config))
for checkpoint in history:
    print(f"Step {checkpoint.metadata['step']}: {checkpoint.values}")

# 从最近 checkpoint 继续
result = graph.invoke(None, config)  # None = 恢复
```

**Checkpointer 选择：**

| 后端 | 场景 | 安装 |
|------|------|------|
| `MemorySaver` | 开发/测试 | 内置 |
| `SqliteSaver` | 单机生产 | `pip install langgraph-checkpoint-sqlite` |
| `PostgresSaver` | 多实例生产 | `pip install langgraph-checkpoint-postgres` |

## 7.3 Human-in-the-Loop（中断与恢复）

```python
# 在关键节点前中断
graph = builder.compile(
    checkpointer=MemorySaver(),
    interrupt_before=["send_notification", "execute_payment"],
)

# 运行到中断点
for event in graph.stream(inputs, config, stream_mode="updates"):
    print(event)

# 人工审查后批准
graph.update_state(config, {"human_approved": True})

# 恢复执行
for event in graph.stream(None, config, stream_mode="updates"):
    print(event)
```

## 7.4 DeltaChannel（存储革命，v1.2）

长时间 Agent 的**存储膨胀**解决方案。传统 checkpoint 每步写完整快照，DeltaChannel 只写**增量**。

| 指标 | 旧方案 | DeltaChannel | 改善 |
|------|--------|-------------|------|
| 200 轮编码 Agent 存储 | 5.3 GB | 129 MB | **减少 41 倍** |
| 增长模式 | O(N²) | O(N) | 适用于长时间会话 |

```python
from langgraph.channels.delta import DeltaChannel
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list, DeltaChannel(
        reducer=add_messages,       # 合并函数
        snapshot_frequency=50,      # 每 50 步写一次全量快照
    )]
```

## 7.5 Per-Node Timeout（v1.2）

```python
from langgraph.types import TimeoutPolicy

# 硬超时：120 秒绝对限制
TimeoutPolicy(run_timeout=120)

# 空闲超时：30 秒无产出则中断
TimeoutPolicy(idle_timeout=30)

# 组合
TimeoutPolicy(run_timeout=120, idle_timeout=30)
```

**心跳保活**：节点可 yield `{}` 来重置 idle 超时。

```python
async def long_running_node(state):
    for chunk in stream_large_data():
        process(chunk)
        yield {}  # "我还在工作"
    return {"status": "done"}
```

---

# 第 8 章 流式输出

## 8.1 stream() 模式

```python
# 基本流式
for chunk in agent.stream(
    {"messages": [{"role": "user", "content": "讲个笑话"}]},
    stream_mode="values",      # 每步的完整状态
):
    last_msg = chunk["messages"][-1]
    print(last_msg.content)

# 多种模式对比
# "values"   — 每步的完整状态
# "updates"  — 每步的增量变更
# "messages" — LLM token 级别输出（逐字打字效果）
```

## 8.2 stream_events（调试利器）

```python
# 观察 Agent 内部每一步发生了什么
for event in agent.stream_events(input_messages, version="v2"):
    if event["event"] == "on_chat_model_start":
        print(f"\n>>> 调用模型，输入: {event['data']['input']['messages'][-1].content[:50]}...")

    elif event["event"] == "on_chat_model_end":
        usage = event['data']['output'].usage_metadata
        print(f">>> 模型返回: {event['data']['output'].content[:100]}...")
        print(f">>> Token 使用: input={usage['input_tokens']}, output={usage['output_tokens']}")

    elif event["event"] == "on_tool_start":
        print(f"\n🔧 调用工具 [{event['name']}]: {event['data']['input']}")

    elif event["event"] == "on_tool_end":
        output = event['data']['output']
        print(f"🔧 工具返回: {str(output)[:200]}")
```

**v3 版本**（langchain v1.3）提供类型化的分通道投影：

```python
async for event in graph.astream_events(..., version="v3"):
    # run.values     → 状态更新通道
    # run.messages   → ChatModelStream（含 text/reasoning/tool_calls/usage）
    # run.lifecycle  → 节点生命周期通道
    # run.subgraphs  → 子图事件通道
```

---

# 第 9 章 Deep Agents

Deep Agents 是 LangChain 的"电池全装"Agent，内置文件系统、子代理、沙盒执行等能力。

## 9.1 create_deep_agent

```python
from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model

# 最简 Agent
agent = create_deep_agent()
result = agent.invoke({
    "messages": [{"role": "user", "content": "研究 LangGraph 并写一篇总结"}]
})

# 完整配置
agent = create_deep_agent(
    model=init_chat_model("openai:gpt-4o"),
    tools=[my_custom_tool],
    system_prompt="你是专业的研究助手。",
    memory=["AGENTS.md"],               # 加载记忆文件
    skills=["./src/skills"],            # 加载技能目录
    subagents=[my_subagent],            # 子代理
)
```

## 9.2 内置工具（开箱即用）

| 工具类别 | 具体工具 |
|---------|---------|
| 规划 | `write_todos` — 任务拆解和进度跟踪 |
| 文件系统 | `ls`、`read_file`、`write_file`、`edit_file`、`glob`、`grep` |
| Shell | `execute` — 执行 shell 命令（需 sandbox） |
| 子代理 | `task` — 委托子任务给独立代理 |
| 压缩 | `compact_conversation` — 对话总结（通过 SummarizationToolMiddleware） |

## 9.3 Backend（文件系统后端）

```python
from deepagents.backends import (
    FilesystemBackend,
    StateBackend,
    StoreBackend,
    CompositeBackend,
)

# 1. 本地文件系统
agent = create_deep_agent(
    backend=FilesystemBackend(root_dir="./workspace", virtual_mode=True)
)

# 2. 内存（默认，会话结束消失）
agent = create_deep_agent()  # 等同于 backend=StateBackend()

# 3. 持久化存储（跨会话）
from langgraph.store.memory import InMemoryStore
agent = create_deep_agent(
    backend=StoreBackend(),
    store=InMemoryStore(),
)

# 4. 混合路由：不同路径用不同后端
def make_backend(rt):
    return CompositeBackend(
        default=StateBackend(rt),          # 默认内存
        routes={"/memories/": StoreBackend(rt)},  # /memories/ 持久化
    )
agent = create_deep_agent(backend=make_backend, store=InMemoryStore())
```

## 9.4 CodeInterpreterMiddleware（v0.6 新增）

在 Agent 循环中嵌入 **QuickJS 沙盒解释器**，让 Agent 能用代码组合工具。

```python
from deepagents import create_deep_agent
from langchain_quickjs import CodeInterpreterMiddleware

agent = create_deep_agent(
    model="claude-sonnet-4-6",
    middleware=[
        CodeInterpreterMiddleware(
            timeout=10,                          # 每次 eval 超时（秒）
            memory_limit=128 * 1024 * 1024,      # 128 MiB 内存限制
            ptc=["search_web", "summarize"],      # 允许 PTC 的工具
        ),
    ],
)

# 必须用 ainvoke（PTC 桥接是异步的）
result = await agent.ainvoke({
    "messages": [{"role": "user", "content": "搜索 LangChain DeltaChannel 并总结"}]
})
```

**编程式工具调用（PTC）**：Agent 在沙盒中并行调用工具，无需多次 LLM 往返：

```javascript
// Agent 在沙盒中写并行调用
const results = await Promise.all([
    tools.searchWeb({ query: "langgraph delta channel" }),
    tools.searchWeb({ query: "deepagents code interpreter" }),
]);
await tools.summarize({ text: JSON.stringify(results) });
// 只有最终结果返回给 LLM，中间过程不消耗 token
```

---

# 第 10 章 结构化输出

## 10.1 response_format

让 Agent 输出遵循特定结构（Pydantic 模型）。

```python
from pydantic import BaseModel, Field
from langchain.agents import create_agent

class WeatherReport(BaseModel):
    """天气报告"""
    city: str = Field(description="城市名称")
    temperature: float = Field(description="当前温度（摄氏度）")
    condition: str = Field(description="天气状况，如'晴'、'多云'、'雨'")
    suggestion: str = Field(description="出行建议")

agent = create_agent(
    model=model,
    tools=[get_weather],
    response_format=WeatherReport,
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "北京今天天气怎么样？"}]
})

# 结构化响应在 result["structured_response"] 中
report = result["structured_response"]
print(f"{report.city}：{report.condition}，{report.temperature}°C")
print(f"建议：{report.suggestion}")
```

## 10.2 ToolStrategy vs ProviderStrategy

```python
from langchain.agents.middleware.types import ToolStrategy, ProviderStrategy

# ToolStrategy：通过工具调用实现结构化输出（兼容性好）
ToolStrategy()

# ProviderStrategy：使用模型原生能力（更可靠，需 profile 支持）
ProviderStrategy()
```

---

# 第 11 章 记忆系统

## 11.1 Checkpointer（短期记忆）

单次会话内的对话持久化。

```python
from langgraph.checkpoint.memory import MemorySaver

agent = create_agent(
    model=model,
    tools=[...],
    checkpointer=MemorySaver(),
)

config = {"configurable": {"thread_id": "user-001"}}

# 第一轮对话
agent.invoke({"messages": [{"role": "user", "content": "我叫张三"}]}, config)

# 第二轮对话 —— Agent 记住了名字
agent.invoke({"messages": [{"role": "user", "content": "我叫什么名？"}]}, config)
# 回复："你叫张三"
```

## 11.2 Store（长期记忆）

跨会话、跨用户的持久化信息。

```python
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()

agent = create_agent(
    model=model,
    store=store,
)

# 在中间件中读写长期记忆
class PersonalMemoryMiddleware(AgentMiddleware):
    def before_model(self, state, runtime):
        user_id = runtime.user_id

        # 读取用户偏好
        prefs = runtime.store.get(["users", user_id, "preferences"])

        if prefs:
            # 注入到系统消息
            system_msg = f"用户偏好：{prefs}"
            ...

    def after_agent(self, state, runtime):
        # 从对话中提取并保存信息
        runtime.store.put(["users", user_id, "preferences"], extracted_info)
```

---

# 第 12 章 项目实战：批量代码审查 Agent

一个完整的实战案例，展示 v1.3 各项特性的组合使用。

```python
import os
from pydantic import BaseModel, Field
from typing import List
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.tools import tool
from langchain.agents.middleware import (
    SummarizationMiddleware,
    ModelRetryMiddleware,
    HumanInTheLoopMiddleware,
)
from langgraph.checkpoint.memory import MemorySaver


# ===== 1. 定义输出结构 =====
class ReviewResult(BaseModel):
    """代码审查结果"""
    file: str = Field(description="审查的文件名")
    score: int = Field(description="评分 1-10")
    issues: List[str] = Field(description="发现的问题列表")
    suggestions: List[str] = Field(description="改进建议")


# ===== 2. 定义工具 =====
@tool
def read_code_file(filepath: str) -> str:
    """读取指定路径的代码文件内容。
    Args:
        filepath: 文件的绝对路径
    """
    with open(filepath, "r") as f:
        return f.read()


@tool
def search_best_practices(topic: str) -> str:
    """搜索某个主题的最佳实践和常见反模式。
    Args:
        topic: 搜索主题，如 '错误处理'、'并发编程'
    """
    knowledge = {
        "错误处理": "Go 最佳实践：1. 永远不要忽略 error 返回值 2. 使用 %w 包装错误 3. 只在顶层处理 error",
        "并发编程": "最佳实践：1. 用 channel 而非共享内存 2. 用 context 控制超时 3. 避免 goroutine 泄漏",
    }
    return knowledge.get(topic, f"未找到关于 '{topic}' 的最佳实践")


# ===== 3. 创建 Agent =====
agent = create_agent(
    model=init_chat_model("openai:gpt-4o", temperature=0.2),
    tools=[read_code_file, search_best_practices],
    system_prompt="""你是资深代码审查专家。审查代码时关注：
1. 潜在 bug 和错误处理
2. 性能问题
3. 安全漏洞
4. 代码可维护性
请用中文给出审查结果。""",
    response_format=ReviewResult,
    middleware=[
        SummarizationMiddleware(
            model="openai:gpt-4o-mini",
            trigger={"fraction": 0.7},
            keep={"messages": 10},
        ),
        ModelRetryMiddleware(max_retries=2),
        HumanInTheLoopMiddleware(interrupt_on=["read_code_file"]),
    ],
    checkpointer=MemorySaver(),
)


# ===== 4. 运行 =====
def review_file(filepath: str, session_id: str):
    config = {"configurable": {"thread_id": session_id}}

    result = agent.invoke({
        "messages": [{
            "role": "user",
            "content": f"请审查文件 {filepath}，并给出评分和改进建议。"
        }]
    }, config)

    review = result["structured_response"]
    print(f"\n===== 审查报告：{review.file} =====")
    print(f"评分：{review.score}/10")

    print("\n发现的问题：")
    for issue in review.issues:
        print(f"  - {issue}")

    print("\n改进建议：")
    for sug in review.suggestions:
        print(f"  - {sug}")

    return review


if __name__ == "__main__":
    review_file("./src/user_service.go", "session-001")
```

---

# 第 13 章 速查卡片

## create_agent 模板

```python
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import MemorySaver

agent = create_agent(
    model=init_chat_model("openai:gpt-4o"),
    tools=[my_tool_1, my_tool_2],
    system_prompt="你是一个专业的...",
    middleware=[
        SummarizationMiddleware(model="openai:gpt-4o-mini", trigger={"fraction": 0.8}),
        ModelRetryMiddleware(max_retries=2),
    ],
    response_format=MyOutputSchema,  # 可选
    checkpointer=MemorySaver(),       # 可选
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "..."}]
})
```

## 工具定义模板

```python
from langchain.tools import tool
from pydantic import BaseModel, Field

# 最简单
@tool
def my_tool(param: str) -> str:
    """工具描述——LLM 会读这段文本来理解工具。
    Args:
        param: 参数说明
    """
    return f"结果: {param}"

# 放入 agent: create_agent(model=model, tools=[my_tool])
```

## 中间件速查

| 需求 | 中间件 |
|------|--------|
| 长对话压缩 | `SummarizationMiddleware` |
| 自动重试 | `ModelRetryMiddleware` |
| 人工审批 | `HumanInTheLoopMiddleware` |
| 成本控制 | `ModelCallLimitMiddleware` |
| 隐私保护 | `PIIMiddleware` |
| 多模型切换 | `ModelFallbackMiddleware` |
| 任务规划 | `TodoListMiddleware` |

## 常见问题 Top 5

| 问题 | 原因 | 解决 |
|------|------|------|
| Agent 输出不符合预期格式 | 未使用结构化输出 | 加 `response_format=MySchema` |
| 长对话突然"失忆" | 超过模型窗口 | 加 `SummarizationMiddleware` |
| 工具调用一直失败 | 参数描述不清晰 | 检查工具 docstring + args_schema |
| 返回 "I don't know" | 缺少对应工具 | 添加能解决问题的工具 |
| 并发场景状态丢失 | 未配置 checkpointer | 编译时传 `checkpointer=MemorySaver()` |

---

> **LangChain v1.3 核心哲学：让 Agent 更省 Token、跑得更久、用更少存储、自己写代码组合工具。**

> 来源：
> - [LangChain 官方文档](https://docs.langchain.com/oss/python/overview)
> - [LangGraph 官方文档](https://docs.langchain.com/oss/python/langgraph/streaming)
> - [Deep Agents GitHub](https://github.com/langchain-ai/deepagents)
> - [DeltaChannel 技术博客](https://www.langchain.com/blog/delta-channels-evolving-agent-runtime)
> - [Deep Agents v0.6 公告](https://www.langchain.com/blog/deep-agents-0-6)
