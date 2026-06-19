# TypeScript LangChain Agent 开发详解

> 基于 **LangChain.js v1.x + LangGraph.js v1.x**，对照 Python 版 LangChain v1.3，提供完整的 TypeScript Agent 开发指南。

---

## 目录

- [第 1 章 LangChain.js 概述](#第-1-章-langchainjs-概述)
- [第 2 章 环境搭建与第一个 Agent](#第-2-章-环境搭建与第一个-agent)
- [第 3 章 createAgent 详解](#第-3-章-createagent-详解)
- [第 4 章 工具（Tools）](#第-4-章-工具tools)
- [第 5 章 中间件体系](#第-5-章-中间件体系)
- [第 6 章 结构化输出](#第-6-章-结构化输出)
- [第 7 章 LangGraph 核心](#第-7-章-langgraph-核心)
- [第 8 章 流式输出](#第-8-章-流式输出)
- [第 9 章 记忆系统](#第-9-章-记忆系统)
- [第 10 章 RAG 检索增强生成](#第-10-章-rag-检索增强生成)
- [第 11 章 MCP 工具集成](#第-11-章-mcp-工具集成)
- [第 12 章 项目实战：AI 编程助手 Agent](#第-12-章-项目实战ai-编程助手-agent)
- [第 13 章 速查卡片](#第-13-章-速查卡片)

---

# 第 1 章 LangChain.js 概述

## 什么是 LangChain.js？

LangChain.js 是 LangChain 官方提供的 **JavaScript/TypeScript SDK**，与 Python 版同步维护，用于构建大语言模型（LLM）驱动的应用程序和 AI Agent。

:::tips
LangChain.js 的核心理念与 Python 版一致：**让 LLM 不仅仅是一个"聊天机器人"，而是一个能思考、能行动、能使用工具的智能体（Agent）。**
:::

## Python 版 vs TypeScript 版对照

| 维度 | Python 版 | TypeScript 版 |
|------|-----------|---------------|
| 核心包 | `langchain` | `langchain` (npm) |
| 图引擎 | `langgraph` | `@langchain/langgraph` |
| Agent 入口 | `create_agent()` | `createAgent()` |
| 工具定义 | `@tool` 装饰器 | `tool()` 函数 + Zod |
| 结构体定义 | Pydantic BaseModel | Zod Schema |
| 中间件 | `AgentMiddleware` 类 | `createMiddleware()` 函数式 API |
| 模型入口 | `init_chat_model()` | `initChatModel()` 或直接实例化 |
| 检查点 | `MemorySaver` / `SqliteSaver` | `MemorySaver` / `PostgresSaver` |
| Deep Agents | `deepagents` 包 | `deepagentsjs` 包（开发中） |

## LangChain.js 核心包

```
LangChain.js 生态
├── langchain               # Agent 框架（createAgent、中间件、工具）
├── @langchain/core         # 核心抽象（Runnable、消息、回调等）
├── @langchain/langgraph    # 状态图引擎（StateGraph、Checkpointer、Stream）
├── @langchain/openai       # OpenAI 集成
├── @langchain/anthropic    # Anthropic Claude 集成
├── @langchain/community    # 社区维护的集成（向量数据库、文档加载器等）
└── deepagentsjs            # 深度 Agent（开发中）
```

## 安装

```bash
# 核心包
npm install langchain @langchain/core @langchain/langgraph

# 模型提供商（按需选择）
npm install @langchain/openai       # OpenAI
npm install @langchain/anthropic    # Anthropic Claude
npm install @langchain/google-genai # Google Gemini

# 工具库
npm install zod                     # Schema 定义（必装）

# 可观测性（推荐）
export LANGSMITH_API_KEY="ls_..."   # LangSmith 追踪
export LANGSMITH_TRACING=true
```

---

# 第 2 章 环境搭建与第一个 Agent

## 2.1 Node.js 环境要求

```bash
# 确认 Node.js 版本（需要 20+）
node --version  # 应 >= 20.0.0

# 确认 npm 版本
npm --version
```

## 2.2 项目初始化

```bash
# 创建项目
mkdir my-agent-app && cd my-agent-app
npm init -y

# 安装依赖
npm install langchain @langchain/core @langchain/openai zod
npm install -D typescript @types/node tsx

# 初始化 TypeScript 配置
npx tsc --init --target ES2022 --module nodenext --moduleResolution nodenext
```

## 2.3 第一个 Agent

```typescript
// src/first-agent.ts
import { createAgent } from "langchain";
import { z } from "zod";

// 1. 创建 Agent（最简配置）
const agent = createAgent({
  model: "openai:gpt-4o",                      // 模型字符串，自动解析
  systemPrompt: "你是一个乐于助人的智能助手。",
});

// 2. 调用
const result = await agent.invoke({
  messages: [{ role: "user", content: "你好，请用一句话介绍自己" }],
});

// 3. 获取回复
const lastMsg = result.messages[result.messages.length - 1];
console.log(lastMsg.content);
// 输出：你好！我是一个基于大语言模型的智能助手...
```

### 代码执行流程图

```
createAgent() → 编译成 LangGraph StateGraph → invoke() → ReAct 循环
                                                          │
                                          ┌───────────────┴───────────────┐
                                          │  思考 → 行动 → 观察 → 再思考    │
                                          └───────────────────────────────┘
```

---

# 第 3 章 createAgent 详解

`createAgent` 是 LangChain.js v1.x 创建 Agent 的**唯一推荐入口**。

## 3.1 完整参数

```typescript
import { createAgent, type CreateAgentParams } from "langchain";

const agent = createAgent({
  // ========== 核心参数 ==========
  model: "openai:gpt-4o",                   // 必填：模型字符串或 BaseChatModel 实例
  tools: [myTool1, myTool2],                // 工具数组
  systemPrompt: "你是一个专业的助手。",       // 系统提示词

  // ========== 结构化输出 ==========
  responseFormat: MyZodSchema,              // Zod Schema，控制输出格式

  // ========== 中间件 ==========
  middleware: [
    summarizationMiddleware({              // 上下文压缩
      model: "openai:gpt-4o-mini",
      trigger: { tokens: 4000 },
      keep: { messages: 20 },
    }),
    modelRetryMiddleware({ maxRetries: 3 }), // 自动重试
  ],

  // ========== 持久化 ==========
  checkpointer: new MemorySaver(),          // 短期记忆/对话持久化
  store: new InMemoryStore(),               // 长期记忆/跨会话存储

  // ========== 其他 ==========
  name: "my-agent",                         // Agent 名称
  version: "v2",                            // 工具执行模式（默认 "v2"）
});
```

## 3.2 返回值：ReactAgent

`createAgent` 返回 `ReactAgent` 实例（底层是编译后的 LangGraph `CompiledStateGraph`）：

| 方法 | 说明 |
|------|------|
| `invoke(input, config?)` | 运行 Agent，返回最终状态 |
| `stream(input, streamMode?)` | 流式运行 |
| `streamEvents(input, options?)` | v3 事件流（推荐，类型安全） |
| `getState(config)` | 获取当前状态快照 |

### 调用方式

```typescript
// ===== 基础调用 =====
const result = await agent.invoke({
  messages: [{ role: "user", content: "帮我查一下北京的天气" }],
});

// 获取最终回复
const lastMsg = result.messages[result.messages.length - 1];
console.log(lastMsg.content);

// ===== 带 thread_id 的调用（持久化会话） =====
const config = { configurable: { thread_id: "user-session-001" } };

// 第一轮
await agent.invoke({
  messages: [{ role: "user", content: "我叫张三" }],
}, config);

// 第二轮——Agent 记住了名字
const result2 = await agent.invoke({
  messages: [{ role: "user", content: "我叫什么名字？" }],
}, config);
// 回复："你叫张三"
```

---

# 第 4 章 工具（Tools）

## 4.1 `tool()` 函数（推荐）

TypeScript 版使用 `tool()` 函数 + Zod schema，这是最快速、最简洁的定义方式。

```typescript
import { tool } from "langchain";
import { z } from "zod";

// ===== 方式 1：基础写法 =====
const getWeather = tool(
  async ({ city }: { city: string }) => {
    const weatherData: Record<string, string> = {
      "北京": "晴，18°C，湿度40%",
      "上海": "多云，22°C，湿度65%",
      "深圳": "阵雨，25°C，湿度80%",
    };
    return weatherData[city] ?? `暂无 ${city} 的天气数据`;
  },
  {
    name: "get_weather",
    description: "获取指定城市的天气信息",
    schema: z.object({
      city: z.string().describe("城市名称，如'北京'、'上海'"),
    }),
  }
);

// ===== 方式 2：复杂 schema =====
const calculator = tool(
  async ({ operation, a, b }) => {
    switch (operation) {
      case "add": return `${a + b}`;
      case "subtract": return `${a - b}`;
      case "multiply": return `${a * b}`;
      case "divide":
        if (b === 0) return "错误：除数不能为0";
        return `${a / b}`;
    }
  },
  {
    name: "calculator",
    description: "执行基本数学运算",
    schema: z.object({
      operation: z.enum(["add", "subtract", "multiply", "divide"])
        .describe("运算类型"),
      a: z.number().describe("第一个数字"),
      b: z.number().describe("第二个数字"),
    }),
  }
);

// ===== 放入 Agent =====
const agent = createAgent({
  model: "openai:gpt-4o",
  tools: [getWeather, calculator],
  systemPrompt: "你是生活助手，可以查天气、做计算。",
});
```

**工具定义的三个关键要素：**

1. **Zod Schema**：定义参数名、类型和描述（LLM 据此决定传什么参数）
2. **description**：LLM 读取这段文本来理解工具的用途，必须精确
3. **返回值**：必须是字符串（string）

## 4.2 ToolRuntime（获取 Agent 运行时上下文）

工具函数第二个参数可以获取运行时上下文：

```typescript
import { tool, type ToolRuntime } from "langchain";
import { z } from "zod";

const getUserPreference = tool(
  async (
    { key }: { key: string },
    runtime: ToolRuntime<MyState, MyContext>
  ) => {
    // 访问 Agent 状态
    const state = runtime.state;

    // 访问运行时上下文
    const userId = runtime.context?.userId;

    // 访问长期存储
    const prefs = await runtime.store?.get(["users", userId, "preferences"]);

    return `偏好 ${key}: ${prefs?.[key] ?? "未设置"}`;
  },
  {
    name: "get_user_preference",
    description: "获取用户偏好设置",
    schema: z.object({
      key: z.string().describe("偏好键名"),
    }),
  }
);
```

## 4.3 继承 BaseTool（复杂场景）

适合有复杂状态、需要注入外部依赖的场景。

```typescript
import { BaseTool } from "@langchain/core/tools";
import { z } from "zod";

const databaseQuerySchema = z.object({
  sql: z.string().describe("只读 SQL 查询语句"),
});

class DatabaseQueryTool extends BaseTool<typeof databaseQuerySchema> {
  name = "query_database";
  description = "执行只读 SQL 查询。禁止 INSERT/UPDATE/DELETE。";
  schema = databaseQuerySchema;

  private dbConnection: string;

  constructor(dbConnection: string) {
    super();
    this.dbConnection = dbConnection;
  }

  async _call({ sql }: z.infer<typeof databaseQuerySchema>): Promise<string> {
    // 安全检查：禁止写操作
    const forbidden = ["insert", "update", "delete", "drop", "alter"];
    if (forbidden.some(word => sql.toLowerCase().includes(word))) {
      return "错误：只允许只读查询（SELECT）";
    }
    return executeQuery(this.dbConnection, sql);
  }
}

async function executeQuery(conn: string, sql: string): Promise<string> {
  // 实际数据库查询逻辑
  return `查询结果: ...`;
}
```

## 4.4 工具定义三种方式对比

| 方式 | 适用场景 | 复杂度 |
|------|---------|--------|
| `tool()` 函数 | 简单函数，快速原型 | 低 |
| `tool()` + ToolRuntime | 需要访问状态/存储/上下文 | 中 |
| 继承 `BaseTool` | 复杂逻辑、外部依赖注入 | 高 |

---

# 第 5 章 中间件体系

中间件是 LangChain.js v1.x 的**核心扩展机制**，让你在不修改 Agent 核心循环的情况下注入自定义逻辑。

## 5.1 中间件概念

```
Agent 执行流程：
  beforeAgent → [beforeModel → model → afterModel → wrapToolCall]* → afterAgent
               └────────────────── 循环 ──────────────────┘
```

**钩子类型：**

| 类型 | 钩子 | 触发时机 |
|------|------|---------|
| 节点式 | `beforeAgent` | Agent 调用开始（仅一次） |
| 节点式 | `beforeModel` | 每次模型调用前 |
| 节点式 | `afterModel` | 每次模型响应后 |
| 节点式 | `afterAgent` | Agent 调用结束（仅一次） |

**执行顺序（洋葱模型）**：`middleware=[m1, m2, m3]`
- `before*`：正序 m1 → m2 → m3
- `after*`：逆序 m3 → m2 → m1

:::color4
**编排原则：安全 > 业务 > 成本 > 监控**。安全检查永远排在最前面。
:::

## 5.2 内置中间件速查

| 中间件 | 功能 | 分类 |
|--------|------|------|
| `summarizationMiddleware` | 上下文超长时自动总结历史 | 上下文管理 |
| `contextEditingMiddleware` | 修剪/清除工具调用历史 | 上下文管理 |
| `modelRetryMiddleware` | LLM 调用指数退避重试 | 容错 |
| `toolRetryMiddleware` | 工具调用指数退避重试 | 容错 |
| `modelFallbackMiddleware` | 主模型故障时切换备用模型 | 容错 |
| `piiRedactionMiddleware` | PII 检测和脱敏 | 安全 |
| `toolCallLimitMiddleware` | 限制工具调用次数 | 安全 |
| `modelCallLimitMiddleware` | 限制模型调用次数 | 安全 |
| `humanInTheLoopMiddleware` | 关键操作人工审批 | 人机协同 |
| `todoListMiddleware` | 任务规划和进度跟踪 | 规划 |

## 5.3 summarizationMiddleware（上下文压缩）

长对话 Agent 核心中间件。

```typescript
import { createAgent, summarizationMiddleware } from "langchain";

const agent = createAgent({
  model: "openai:gpt-4o",
  tools: [searchTool, dbTool],
  middleware: [
    summarizationMiddleware({
      model: "openai:gpt-4o-mini",         // 用小模型做摘要，省钱
      trigger: { tokens: 4000 },            // 达到 4000 token 时触发
      keep: { messages: 20 },               // 保留最近 20 条完整消息
      maxSummaryTokens: 500,                // 摘要最大 token 数
    }),
  ],
});
```

**触发条件**支持灵活组合：

| 方式 | 示例 | 说明 |
|------|------|------|
| Token 阈值 | `{ tokens: 4000 }` | 固定触发线 |
| 比例触发 | `{ fraction: 0.8 }` | 达到模型窗口 80% 时触发 |
| 消息计数 | `{ messages: 50 }` | 超过 N 条时触发 |

## 5.4 modelRetryMiddleware（自动重试）

```typescript
import { createAgent, modelRetryMiddleware } from "langchain";

const agent = createAgent({
  model: "openai:gpt-4o",
  middleware: [
    modelRetryMiddleware({
      maxRetries: 3,
      backoffFactor: 2.0,          // 指数退避：1s → 2s → 4s
      initialDelayMs: 1000,
      onFailure: "error",          // "continue" | "error" | 自定义函数
    }),
  ],
});
```

## 5.5 humanInTheLoopMiddleware（人工审批）

```typescript
import { createAgent, humanInTheLoopMiddleware } from "langchain";

const agent = createAgent({
  model: "openai:gpt-4o",
  tools: [sendEmail, transferMoney],
  middleware: [
    humanInTheLoopMiddleware({
      interruptOn: ["send_email", "transfer_money"],   // 这些工具需要人工审批
    }),
  ],
});

// 运行并处理中断
const stream = await agent.stream(inputs, config);
for await (const chunk of stream) {
  if (chunk.__interrupt__) {
    console.log("需要人工审批：", chunk.__interrupt__);
    // 人工审查后...
  }
}
```

## 5.6 自定义中间件

```typescript
import { createMiddleware, type MiddlewareState } from "langchain";

// 方式 1：createMiddleware（推荐）
const messageLimitMiddleware = createMiddleware({
  name: "MessageLimitMiddleware",
  beforeModel: (state) => {
    if (state.messages.length >= 50) {
      return {
        messages: [{
          role: "assistant",
          content: "对话已达上限，请开始新的会话。",
        }],
        jumpTo: "end",
      };
    }
    return null;   // 返回 null 表示不干预
  },
});

// 方式 2：类（复杂场景）
import { AgentMiddleware } from "langchain";

class LoggingMiddleware extends AgentMiddleware {
  constructor(private logFn: (msg: string) => void = console.log) {
    super();
  }

  beforeModel(state: MiddlewareState) {
    this.logFn(`[beforeModel] 消息数: ${state.messages.length}`);
    return null;
  }

  afterModel(state: MiddlewareState) {
    const lastMsg = state.messages[state.messages.length - 1];
    this.logFn(`[afterModel] 模型响应: ${lastMsg.content?.slice(0, 100)}...`);
    return null;
  }
}

// 使用
const agent = createAgent({
  model: "openai:gpt-4o",
  tools: [myTool],
  middleware: [
    messageLimitMiddleware,
    new LoggingMiddleware(),
  ],
});
```

---

# 第 6 章 结构化输出

## 6.1 responseFormat（Zod Schema）

让 Agent 输出遵循特定结构。

```typescript
import { createAgent } from "langchain";
import { z } from "zod";

// 1. 定义输出 Schema
const WeatherReport = z.object({
  city: z.string().describe("城市名称"),
  temperature: z.number().describe("当前温度（摄氏度）"),
  condition: z.string().describe("天气状况，如'晴'、'多云'、'雨'"),
  suggestion: z.string().describe("出行建议"),
});

// 2. 创建带结构化输出的 Agent
const agent = createAgent({
  model: "openai:gpt-4o",
  tools: [getWeather],
  responseFormat: WeatherReport,
});

// 3. 调用
const result = await agent.invoke({
  messages: [{ role: "user", content: "北京今天天气怎么样？" }],
});

// 4. 获取结构化响应
const report = result.structuredResponse;
console.log(`${report.city}：${report.condition}，${report.temperature}°C`);
console.log(`建议：${report.suggestion}`);
```

## 6.2 providerStrategy vs toolStrategy

```typescript
import { createAgent, providerStrategy, toolStrategy } from "langchain";
import { z } from "zod";

const UserInfo = z.object({
  name: z.string(),
  age: z.number(),
  email: z.string(),
});

// 方式 1：ProviderStrategy — 使用模型原生结构化输出能力（更可靠，推荐）
const agent1 = createAgent({
  model: "openai:gpt-4o",
  responseFormat: providerStrategy(UserInfo),
});

// 方式 2：ToolStrategy — 通过工具调用实现（兼容性更好，兜底方案）
const agent2 = createAgent({
  model: "anthropic:claude-sonnet-4-6",
  responseFormat: toolStrategy(UserInfo),
});

// 方式 3：直接传 Zod Schema，框架自动选择最佳策略（最常用）
const agent3 = createAgent({
  model: "openai:gpt-4o",
  responseFormat: UserInfo,   // 自动：OpenAI → native，Anthropic → tool_use
});
```

## 6.3 withStructuredOutput（非 Agent 场景）

不在 Agent 中，直接让模型输出结构化数据：

```typescript
import { ChatOpenAI } from "@langchain/openai";
import { z } from "zod";

const model = new ChatOpenAI({ model: "gpt-4o", temperature: 0 });

const Joke = z.object({
  setup: z.string().describe("笑话的铺垫"),
  punchline: z.string().describe("笑话的笑点"),
  rating: z.number().min(1).max(10).describe("好笑程度 1-10"),
});

const structuredModel = model.withStructuredOutput(Joke);

const result = await structuredModel.invoke("讲一个程序员笑话");
console.log(result);
// { setup: "为什么程序员分不清万圣节和圣诞节？", punchline: "因为 Oct 31 == Dec 25", rating: 7 }
```

---

# 第 7 章 LangGraph 核心

LangGraph 是 LangChain 的底层引擎，用**状态图**来描述 Agent 的执行流程。`createAgent` 底层也使用它。

## 7.1 StateGraph 基础

```typescript
import { StateGraph, MessagesValue, START, END } from "@langchain/langgraph";
import { ChatOpenAI } from "@langchain/openai";
import * as z from "zod";

// 1. 定义状态（使用 StateSchema）
const AgentState = z.object({
  messages: MessagesValue,      // MessagesValue 自带 add_messages reducer
  currentStep: z.string(),      // 覆盖模式
});

type State = z.infer<typeof AgentState>;

// 2. 定义节点函数
const model = new ChatOpenAI({ model: "gpt-4o" });

async function callModel(state: State): Promise<Partial<State>> {
  const response = await model.invoke(state.messages);
  return {
    messages: [response],
    currentStep: "done",
  };
}

// 3. 构建图
const builder = new StateGraph(AgentState)
  .addNode("call_model", callModel)
  .addEdge(START, "call_model")
  .addEdge("call_model", END);

// 4. 编译
const graph = builder.compile();
```

## 7.2 条件路由

```typescript
import { StateGraph, MessagesValue, START, END } from "@langchain/langgraph";

const builder = new StateGraph(State)
  .addNode("router", router)
  .addNode("thinker", thinker)
  .addNode("tool_executor", toolExecutor)
  .addEdge(START, "router")
  .addConditionalEdges("router", (state) => {
    // 根据状态决定下一步
    if (state.currentStep === "think") return "thinker";
    if (state.currentStep === "act") return "tool_executor";
    return END;
  })
  .addEdge("thinker", END)
  .addEdge("tool_executor", "router");    // 工具执行后回到路由，形成循环

const graph = builder.compile();
```

## 7.3 Checkpointer（持久化）

```typescript
import { MemorySaver } from "@langchain/langgraph";

// 编译时挂载 checkpointer
const graph = builder.compile({ checkpointer: new MemorySaver() });

const config = { configurable: { thread_id: "session-001" } };

// 运行（每一步自动保存状态）
const result = await graph.invoke(
  { messages: [{ role: "user", content: "你好" }] },
  config
);

// 获取当前状态
const state = graph.getState(config);
console.log(state.values);   // 状态数据
console.log(state.next);     // 即将执行的节点

// 时间旅行——查看所有历史 checkpoint
const history = [];
for await (const checkpoint of graph.getStateHistory(config)) {
  history.push(checkpoint);
  console.log(`Step: ${checkpoint.values}`);
}

// 从最近 checkpoint 继续
const result2 = await graph.invoke(null, config);  // null = 恢复
```

**Checkpointer 选择：**

| 后端 | 场景 | 安装 |
|------|------|------|
| `MemorySaver` | 开发/测试 | 内置 `@langchain/langgraph` |
| `PostgresSaver` | 生产（多实例） | `@langchain/langgraph-checkpoint-postgres` |
| `SqliteSaver` | 生产（单机） | `@langchain/langgraph-checkpoint` |
| `MongoDBSaver` | 生产（MongoDB） | `@langchain/langgraph-checkpoint-mongodb` |

### 生产环境 PostgreSQL Checkpointer 示例

```typescript
import { PostgresSaver } from "@langchain/langgraph-checkpoint-postgres";

const DB_URI = "postgresql://postgres:postgres@localhost:5432/postgres?sslmode=disable";
const checkpointer = PostgresSaver.fromConnString(DB_URI);
await checkpointer.setup();   // 首次运行建表

const graph = builder.compile({ checkpointer });
```

## 7.4 Human-in-the-Loop（中断与恢复）

```typescript
// 在关键节点前中断
const graph = builder.compile({
  checkpointer: new MemorySaver(),
  interruptBefore: ["send_notification", "execute_payment"],
});

// 运行到中断点
const stream = await graph.stream(inputs, config);
for await (const chunk of stream) {
  console.log(chunk);
  // 如果遇到中断，stream 会暂停，chunk 包含 __interrupt__ 信息
}

// 人工审查后批准：更新状态
graph.updateState(config, { humanApproved: true });

// 恢复执行
const stream2 = await graph.stream(null, config);
for await (const chunk of stream2) {
  console.log(chunk);
}
```

---

# 第 8 章 流式输出

## 8.1 stream() 基础

```typescript
// 基础流式
const stream = await agent.stream(
  { messages: [{ role: "user", content: "讲个笑话" }] },
  { streamMode: "values" }       // 每次输出完整状态
);

for await (const chunk of stream) {
  const lastMsg = chunk.messages[chunk.messages.length - 1];
  console.log(lastMsg.content);
}
```

**streamMode 对比：**

| 模式 | 说明 |
|------|------|
| `"values"` | 每步的完整状态 |
| `"updates"` | 每步的增量变更 |
| `"messages"` | LLM token 级别输出（逐字打字效果） |

## 8.2 streamEvents v3（推荐，类型安全）

LangChain v1.3+ 推荐使用 `streamEvents` + `version: "v3"`，提供结构化的类型投影：

```typescript
// ===== 基本 streaming =====
const stream = await agent.streamEvents(
  { messages: [{ role: "user", content: "今天深圳天气怎么样？" }] },
  { version: "v3" }
);

// 实时输出文本 token
for await (const message of stream.messages) {
  for await (const delta of message.text) {
    process.stdout.write(delta);   // 逐字效果
  }
}

// 获取最终状态
const finalState = await stream.output;
```

## 8.3 完整事件流（调试利器）

```typescript
const stream = await agent.streamEvents(
  { messages: [{ role: "user", content: "搜索 LangGraph 最新文档并总结" }] },
  { version: "v3" }
);

// 并行监听多个投影
await Promise.all([
  // 1. 文本流式输出
  (async () => {
    for await (const message of stream.messages) {
      for await (const delta of message.text) {
        process.stdout.write(delta);
      }
    }
  })(),

  // 2. 工具调用链路
  (async () => {
    for await (const call of stream.toolCalls) {
      console.log(`\n🔧 调用工具 [${call.name}]:`, call.input);
      try {
        const output = await call.output;
        console.log(`🔧 工具返回: ${output?.slice(0, 200)}`);
      } catch (err) {
        console.error(`🔧 工具出错:`, call.error);
      }
    }
  })(),

  // 3. Token 用量统计（每个 LLM 调用完成后）
  (async () => {
    for await (const message of stream.messages) {
      const usage = await message.usage;
      if (usage) {
        console.log(`\nToken: input=${usage.input_tokens}, output=${usage.output_tokens}`);
      }
    }
  })(),
]);
```

## 8.4 streamEvents v3 投影速查

| 投影 | 用途 |
|------|------|
| `stream.messages` | 模型消息流（每次 LLM 调用一个） |
| `message.text` | 文本 token 增量（实时逐字输出） |
| `message.reasoning` | 推理内容（o1、DeepSeek-R1 等推理模型） |
| `message.toolCalls` | 工具调用参数 chunk 和最终调用 |
| `message.output` | 模型调用完成后的最终消息对象 |
| `message.usage` | Token 用量元数据 |
| `stream.values` | Agent 状态快照 |
| `stream.output` | 最终 Agent 状态 |
| `stream.toolCalls` | 完整工具执行生命周期（input/output/error） |
| `stream.subgraphs` | 嵌套子 Agent 运行 |

---

# 第 9 章 记忆系统

## 9.1 Checkpointer（短期记忆）

单次会话内的对话持久化。

```typescript
import { createAgent } from "langchain";
import { MemorySaver } from "@langchain/langgraph";

const agent = createAgent({
  model: "openai:gpt-4o",
  tools: [myTool],
  checkpointer: new MemorySaver(),       // 短期记忆
});

// ===== 使用 thread_id 区分会话 =====
const config = { configurable: { thread_id: "user-001" } };

// 第一轮对话
await agent.invoke({
  messages: [{ role: "user", content: "我叫张三，我喜欢编程" }],
}, config);

// 第二轮对话 —— Agent 记住了名字和偏好
const result = await agent.invoke({
  messages: [{ role: "user", content: "我叫什么名？我喜欢什么？" }],
}, config);
const reply = result.messages[result.messages.length - 1].content;
// 回复："你叫张三，喜欢编程"
```

## 9.2 Store（长期记忆）

跨会话、跨用户的持久化信息。

```typescript
import { createAgent } from "langchain";
import { MemorySaver } from "@langchain/langgraph";
import { InMemoryStore } from "@langchain/langgraph";

const store = new InMemoryStore();

const agent = createAgent({
  model: "openai:gpt-4o",
  tools: [myTool],
  checkpointer: new MemorySaver(),
  store,                                 // 长期记忆
});

// 在中间件中读写长期记忆
import { createMiddleware } from "langchain";

const personalMemoryMiddleware = createMiddleware({
  name: "PersonalMemoryMiddleware",
  async beforeModel(state, runtime) {
    const userId = runtime.context?.userId ?? "default";
    // 读取用户偏好
    const prefs = await runtime.store?.get(["users", userId, "preferences"]);

    if (prefs) {
      // 注入到系统提示
      const systemMsg = {
        role: "system" as const,
        content: `该用户偏好：${JSON.stringify(prefs)}`,
      };
      return { messages: [systemMsg] };
    }
    return null;
  },
  async afterAgent(state, runtime) {
    const userId = runtime.context?.userId ?? "default";
    // 从对话中提取并保存信息
    await runtime.store?.put(
      ["users", userId, "preferences"],
      { language: "Chinese", expertise: "TypeScript" }
    );
  },
});
```

## 9.3 生产环境持久化（PostgreSQL）

```typescript
import { PostgresSaver } from "@langchain/langgraph-checkpoint-postgres";
import { PostgresStore } from "@langchain/langgraph-checkpoint-postgres/store";

const DB_URI = "postgresql://user:password@localhost:5432/langgraph";

// 短期记忆
const checkpointer = PostgresSaver.fromConnString(DB_URI);
await checkpointer.setup();

// 长期记忆
const store = new PostgresStore({ connectionString: DB_URI });
await store.setup();

// 使用
const agent = createAgent({
  model: "openai:gpt-4o",
  tools: [myTool],
  checkpointer,
  store,
});
```

---

# 第 10 章 RAG 检索增强生成

## 10.1 文档加载与分割

```typescript
import { RecursiveCharacterTextSplitter } from "@langchain/textsplitters";
import { CheerioWebBaseLoader } from "@langchain/community/document_loaders/web/cheerio";

// 加载文档
const loader = new CheerioWebBaseLoader("https://docs.langchain.com/");
const docs = await loader.load();

// 分割文档
const splitter = new RecursiveCharacterTextSplitter({
  chunkSize: 1000,
  chunkOverlap: 200,
});
const splits = await splitter.splitDocuments(docs);
console.log(`分割为 ${splits.length} 个块`);
```

## 10.2 向量存储与检索

```typescript
import { OpenAIEmbeddings } from "@langchain/openai";
import { MemoryVectorStore } from "@langchain/classic/vectorstores/memory";

// 创建向量存储
const vectorStore = await MemoryVectorStore.fromDocuments(
  splits,
  new OpenAIEmbeddings({ model: "text-embedding-3-small" })
);

// 创建检索器
const retriever = vectorStore.asRetriever({ k: 5 });

// 检索
const results = await retriever.invoke("LangGraph 怎么用？");
console.log(results.map(r => r.pageContent).join("\n---\n"));
```

## 10.3 RAG Agent（将检索器包装为工具）

```typescript
import { createAgent } from "langchain";
import { z } from "zod";

// 将检索器包装为可被 Agent 调用的工具
const searchKnowledgeBase = tool(
  async ({ query }: { query: string }) => {
    const docs = await retriever.invoke(query);
    if (docs.length === 0) return "未找到相关内容。";
    return docs
      .map((doc, i) => `[${i + 1}] ${doc.pageContent}\n来源：${doc.metadata.source ?? "未知"}`)
      .join("\n\n");
  },
  {
    name: "search_knowledge_base",
    description: "在知识库中搜索技术文档和信息。",
    schema: z.object({
      query: z.string().describe("搜索查询语句"),
    }),
  }
);

// 创建 RAG Agent
const agent = createAgent({
  model: "openai:gpt-4o",
  tools: [searchKnowledgeBase],
  systemPrompt: `你是一个基于知识库的问答助手。
当用户问技术问题时，请先使用 search_knowledge_base 工具检索知识库。
基于检索到的内容回答问题，如果知识库中没有相关信息，请如实告知。`,
});

// 使用
const result = await agent.invoke({
  messages: [{ role: "user", content: "LangChain 的 createAgent 怎么用？" }],
});
```

## 10.4 使用 Chroma 向量数据库（生产环境）

```typescript
import { Chroma } from "@langchain/community/vectorstores/chroma";
import { OpenAIEmbeddings } from "@langchain/openai";

// 连接 Chroma
const vectorStore = await Chroma.fromDocuments(
  splits,
  new OpenAIEmbeddings({ model: "text-embedding-3-small" }),
  {
    collectionName: "my-knowledge-base",
    url: "http://localhost:8000",      // Chroma 服务地址
  }
);

const retriever = vectorStore.asRetriever({ k: 5 });
```

---

# 第 11 章 MCP 工具集成

MCP（Model Context Protocol）允许 Agent 动态发现和调用外部工具。

## 11.1 MCP Client

```typescript
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

// 1. 创建 MCP 客户端
const transport = new StdioClientTransport({
  command: "node",
  args: ["./my-mcp-server.js"],
});

const client = new Client({
  name: "my-agent-client",
  version: "1.0.0",
});

await client.connect(transport);

// 2. 列出可用工具
const toolsResult = await client.listTools();
console.log("MCP 工具:", toolsResult.tools.map(t => t.name));

// 3. 将 MCP 工具转换为 LangChain 工具
// （具体转换方式取决于 MCP SDK 版本，核心是将工具列表转成 tool() 格式）
```

---

# 第 12 章 项目实战：AI 编程助手 Agent

一个完整的实战案例，展示各项特性的组合使用。

## 12.1 项目结构

```
my-dev-assistant/
├── src/
│   ├── agent.ts          # Agent 主入口
│   ├── tools/
│   │   ├── file-tools.ts # 文件操作工具
│   │   └── search-tools.ts # 搜索工具
│   ├── middleware/
│   │   └── logging.ts    # 自定义中间件
│   ├── rag/
│   │   ├── loader.ts     # 文档加载
│   │   └── retriever.ts  # 检索器
│   └── index.ts          # 启动文件
├── .env
├── tsconfig.json
└── package.json
```

## 12.2 工具定义

```typescript
// src/tools/file-tools.ts
import { tool } from "langchain";
import { z } from "zod";
import * as fs from "node:fs/promises";

export const readCodeFile = tool(
  async ({ filepath }: { filepath: string }) => {
    try {
      return await fs.readFile(filepath, "utf-8");
    } catch (err) {
      return `错误：无法读取文件 ${filepath} —— ${err}`;
    }
  },
  {
    name: "read_code_file",
    description: "读取指定路径的代码文件内容",
    schema: z.object({
      filepath: z.string().describe("文件的绝对路径"),
    }),
  }
);

export const listFiles = tool(
  async ({ dirPath }: { dirPath: string }) => {
    const files = await fs.readdir(dirPath);
    return files.join("\n");
  },
  {
    name: "list_files",
    description: "列出目录内容",
    schema: z.object({
      dirPath: z.string().describe("目录的绝对路径"),
    }),
  }
);
```

```typescript
// src/tools/search-tools.ts
import { tool } from "langchain";
import { z } from "zod";

// 模拟知识库
const bestPractices: Record<string, string> = {
  "错误处理": "1. 永远不要忽略 error 返回值\n2. 使用 error cause 链式包装\n3. 只在顶层处理 error",
  "并发编程": "1. 优先使用 Promise.all 并行\n2. 使用 AbortController 控制超时\n3. 避免 Promise 泄漏",
  "设计模式": "1. 工厂模式解耦创建逻辑\n2. 策略模式替代 if-else\n3. 观察者模式处理事件驱动",
};

export const searchBestPractices = tool(
  async ({ topic }: { topic: string }) => {
    const key = Object.keys(bestPractices).find(k => k.includes(topic));
    return key
      ? `关于"${key}"的最佳实践：\n${bestPractices[key]}`
      : `未找到关于"${topic}"的最佳实践`;
  },
  {
    name: "search_best_practices",
    description: "搜索某个编程主题的最佳实践和常见反模式",
    schema: z.object({
      topic: z.string().describe("搜索主题，如'错误处理'、'并发编程'"),
    }),
  }
);
```

## 12.3 Agent 组装

```typescript
// src/agent.ts
import { createAgent } from "langchain";
import {
  summarizationMiddleware,
  modelRetryMiddleware,
  humanInTheLoopMiddleware,
} from "langchain";
import { MemorySaver } from "@langchain/langgraph";
import { z } from "zod";
import { readCodeFile, listFiles } from "./tools/file-tools.js";
import { searchBestPractices } from "./tools/search-tools.js";

// 1. 定义结构化输出
const ReviewResult = z.object({
  file: z.string().describe("审查的文件名"),
  score: z.number().min(1).max(10).describe("代码质量评分 1-10"),
  issues: z.array(z.string()).describe("发现的问题列表"),
  suggestions: z.array(z.string()).describe("改进建议列表"),
});

// 2. 创建 Agent
export const devAssistant = createAgent({
  model: "openai:gpt-4o",

  tools: [readCodeFile, listFiles, searchBestPractices],

  systemPrompt: `你是资深代码审查专家。审查代码时关注：
1. 潜在 bug 和错误处理
2. 性能问题
3. 安全漏洞
4. 代码可维护性
请用中文给出审查结果。`,

  responseFormat: ReviewResult,

  middleware: [
    // 上下文压缩
    summarizationMiddleware({
      model: "openai:gpt-4o-mini",
      trigger: { fraction: 0.7 },
      keep: { messages: 10 },
    }),
    // 自动重试
    modelRetryMiddleware({ maxRetries: 2 }),
    // 文件读取需人工审批
    humanInTheLoopMiddleware({
      interruptOn: ["read_code_file"],
    }),
  ],

  checkpointer: new MemorySaver(),
  name: "dev-assistant",
});
```

## 12.4 启动入口

```typescript
// src/index.ts
import { devAssistant } from "./agent.js";

async function reviewFile(filepath: string, sessionId: string) {
  const config = { configurable: { thread_id: sessionId } };

  const result = await devAssistant.invoke({
    messages: [{
      role: "user",
      content: `请审查文件 ${filepath}，并给出评分和改进建议。`,
    }],
  }, config);

  const review = result.structuredResponse;

  console.log(`\n===== 审查报告：${review.file} =====`);
  console.log(`评分：${review.score}/10`);

  console.log("\n发现的问题：");
  for (const issue of review.issues) {
    console.log(`  - ${issue}`);
  }

  console.log("\n改进建议：");
  for (const sug of review.suggestions) {
    console.log(`  - ${sug}`);
  }

  return review;
}

// 带流式输出的版本
async function reviewFileWithStream(filepath: string, sessionId: string) {
  const config = { configurable: { thread_id: sessionId } };

  const stream = await devAssistant.streamEvents({
    messages: [{
      role: "user",
      content: `请审查文件 ${filepath}，并给出评分和改进建议。`,
    }],
  }, { version: "v3", ...config });

  // 实时输出文本
  for await (const message of stream.messages) {
    for await (const delta of message.text) {
      process.stdout.write(delta);
    }
  }

  // 获取最终结构化结果
  const finalState = await stream.output;
  return finalState.structuredResponse;
}

// 运行
if (require.main === module) {
  reviewFile("./src/agent.ts", "session-001");
}
```

## 12.5 完整 package.json

```json
{
  "name": "dev-assistant",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "tsx src/index.ts",
    "build": "tsc",
    "start": "node dist/index.js"
  },
  "dependencies": {
    "@langchain/core": "^1.0.0",
    "@langchain/openai": "^1.0.0",
    "@langchain/langgraph": "^1.0.0",
    "langchain": "^1.0.0",
    "zod": "^3.25.0"
  },
  "devDependencies": {
    "@types/node": "^22.0.0",
    "typescript": "^5.7.0",
    "tsx": "^4.0.0"
  }
}
```

---

# 第 13 章 速查卡片

## createAgent 模板

```typescript
import { createAgent } from "langchain";
import { MemorySaver } from "@langchain/langgraph";
import { z } from "zod";

const agent = createAgent({
  model: "openai:gpt-4o",                 // 模型
  tools: [myTool1, myTool2],              // 工具列表
  systemPrompt: "你是一个专业的...",       // 系统提示
  middleware: [
    summarizationMiddleware({             // 上下文压缩
      model: "openai:gpt-4o-mini",
      trigger: { fraction: 0.8 },
    }),
    modelRetryMiddleware({ maxRetries: 2 }), // 自动重试
  ],
  responseFormat: MyZodSchema,            // 结构化输出（可选）
  checkpointer: new MemorySaver(),        // 短期记忆（可选）
});

const result = await agent.invoke({
  messages: [{ role: "user", content: "..." }],
});
```

## 工具定义模板

```typescript
import { tool } from "langchain";
import { z } from "zod";

// 最简单写法
const myTool = tool(
  async ({ param }: { param: string }) => {
    /** 工具实现 */
    return `结果: ${param}`;
  },
  {
    name: "my_tool",
    description: "工具描述——LLM 会读这段文本来理解工具",
    schema: z.object({
      param: z.string().describe("参数说明"),
    }),
  }
);
```

## 中间件速查

| 需求 | 中间件 |
|------|--------|
| 长对话压缩 | `summarizationMiddleware` |
| 自动重试 | `modelRetryMiddleware` |
| 人工审批 | `humanInTheLoopMiddleware` |
| 成本控制 | `modelCallLimitMiddleware` |
| 隐私保护 | `piiRedactionMiddleware` |
| 多模型切换 | `modelFallbackMiddleware` |
| 任务规划 | `todoListMiddleware` |

## Python ↔ TypeScript 常用 API 对照

| 功能 | Python | TypeScript |
|------|--------|------------|
| 创建 Agent | `create_agent()` | `createAgent()` |
| 定义工具 | `@tool` | `tool()` + Zod |
| 结构体定义 | `BaseModel` | `z.object()` |
| 模型初始化 | `init_chat_model()` | `initChatModel()` 或 `new ChatOpenAI()` |
| 系统提示 | `system_prompt="..."` | `systemPrompt="..."` |
| 结构化输出 | `response_format=MyModel` | `responseFormat: MyZodSchema` |
| 检查点 | `checkpointer=MemorySaver()` | `checkpointer: new MemorySaver()` |
| 状态图 | `StateGraph(AgentState)` | `new StateGraph(AgentState)` |
| 同步调用 | `.invoke()` | `.invoke()` |
| 流式调用 | `.astream()` | `.streamEvents()` (v3) |
| 结构化输出获取 | `result["structured_response"]` | `result.structuredResponse` |

## 常见问题 Top 5

| 问题 | 原因 | 解决 |
|------|------|------|
| Agent 输出不符合预期格式 | 未使用结构化输出 | 加 `responseFormat: MyZodSchema` |
| 长对话突然"失忆" | 超过模型窗口 | 加 `summarizationMiddleware` |
| 工具调用一直失败 | 参数描述不清晰 | 检查 Zod schema 中的 `.describe()` |
| 返回 "I don't know" | 缺少对应工具 | 添加能解决问题的工具 |
| 并发场景状态丢失 | 未配置 checkpointer | 传 `checkpointer: new MemorySaver()` |

---

> **LangChain.js v1.x 核心理念：与 Python 版保持一致的设计哲学，提供类型安全的 Agent 开发体验。**
>
> 来源：
> - [LangChain.js 官方文档](https://docs.langchain.com/oss/javascript/overview)
> - [LangGraph.js 文档](https://docs.langchain.com/oss/javascript/langgraph/overview)
> - [createAgent 参考文档](https://reference.langchain.com/javascript/langchain/browser/createAgent)
> - [LangChain.js GitHub](https://github.com/langchain-ai/langchainjs)
