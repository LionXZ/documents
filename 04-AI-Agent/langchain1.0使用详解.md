# LangChain 完全使用指南
> 基于 LangChain 1.0+ 官方文档整理 | 适合速查 | 通俗易懂  
涵盖：模型接入 → 提示词 → LCEL 链 → RAG → Agent → LangGraph → 生产部署
>

---

## 一、LangChain 概述
**LangChain** 是目前最主流的 LLM（大语言模型）应用开发框架，核心目标是**用最少的代码将 LLM 与外部数据、工具连接起来**。

### 1.1 LangChain 解决什么问题？
| 问题 | LangChain 的解决方案 |
| --- | --- |
| LLM 无法访问最新数据 | **RAG**：检索外部知识库增强回答 |
| LLM 无法执行操作 | **Agent + Tools**：让 LLM 调用搜索、计算、API 等工具 |
| LLM 无状态（不记上下文） | **Memory**：自动管理对话历史 |
| 多个 LLM 调用需编排 | **LCEL + Chain**：用管道符 `|` 串联处理流程 |
| 复杂多步骤工作流 | **LangGraph**：图式状态机编排 |


### 1.2 核心架构
```plain
┌─────────────────────────────────────────────────────┐
│                    LangChain 架构                     │
├─────────────┬──────────────┬────────────┬───────────┤
│  Model I/O  │  Retrieval   │   Agent    │  Memory   │
│  模型调用    │  RAG 检索     │  智能体     │  记忆管理  │
├─────────────┴──────────────┴────────────┴───────────┤
│                  LCEL（链式编排语言）                   │
│              prompt | model | parser                  │
├─────────────────────────────────────────────────────┤
│             LangGraph（图式工作流引擎）                  │
│         StateGraph → Node → Edge → State              │
└─────────────────────────────────────────────────────┘
```

### 1.3 版本说明（重要！）
LangChain 1.0（2025年发布）有重大架构变化：

| 旧写法（已废弃） | 新写法（推荐） |
| --- | --- |
| `LLMChain(prompt, llm)` | `prompt | llm | parser` |
| `initialize_agent(...)` | `create_agent(...)` |
| `ConversationBufferMemory` | LangGraph 内置状态管理 |
| `SequentialChain` | LCEL `|` 管道串联 |
| `AgentExecutor` | `create_agent` 内置执行 |


---

## 二、安装与环境配置
### 2.1 安装
```bash
# 核心框架
pip install langchain

# 各模型供应商的包（按需安装）
pip install langchain-openai       # OpenAI 及兼容接口模型
pip install langchain-deepseek     # DeepSeek
pip install langchain-anthropic    # Claude
pip install langchain-ollama       # 本地 Ollama 模型
pip install langchain-community    # 社区集成（通义千问、智谱等）

# RAG 相关
pip install langchain-chroma       # Chroma 向量数据库
pip install langchain-huggingface  # HuggingFace 嵌入模型

# 环境变量管理
pip install python-dotenv

# LangChain 全家桶（一次性安装常用包）
pip install langchain langchain-openai langchain-community python-dotenv chromadb
```

### 2.2 环境变量配置
在项目根目录创建 `.env` 文件，**绝对不要把 API Key 硬编码在代码中**：

```bash
# .env 文件
# OpenAI
OPENAI_API_KEY=sk-your-key-here
OPENAI_BASE_URL=https://api.openai.com/v1

# DeepSeek
DEEPSEEK_API_KEY=sk-your-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com

# 通义千问（阿里 DashScope）
DASHSCOPE_API_KEY=sk-your-key-here

# 智谱 AI
ZHIPUAI_API_KEY=your-key-here

# Anthropic Claude
ANTHROPIC_API_KEY=sk-your-key-here

# LangSmith 监控（可选）
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2-pt-your-key
LANGCHAIN_PROJECT=my-project
```

```python
# config.py — 加载环境变量
import os
from dotenv import load_dotenv

load_dotenv(override=True)  # override=True 表示 .env 文件中的值覆盖系统环境变量

# 读取各 API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
```

---

## 三、模型接入（Model I/O）
### 3.1 模型调用三件套
每当你用 LangChain 调用 LLM 时，涉及三个核心组件：

```plain
输入文本 → [Prompt Template] → [ChatModel/LLM] → [OutputParser] → 结构化输出
```

以下是最简单的三行调用：

```python
from langchain_openai import ChatOpenAI

# 1. 创建模型实例
llm = ChatOpenAI(
    model="gpt-4o-mini",       # 模型名称
    temperature=0.7,            # 温度参数：0=确定，1=随机，2=非常随机
    max_tokens=500,             # 最大输出 token 数
)

# 2. 调用模型
response = llm.invoke("你好，请介绍一下你自己")

# 3. 获取内容
print(response.content)        # AIMessage 对象的 .content 属性
```

### 3.2 各种模型接入方式
#### （1）ChatOpenAI — OpenAI 及所有兼容接口
这是使用最广泛的接入方式，**任何兼容 OpenAI API 格式的服务都能用**：

```python
from langchain_openai import ChatOpenAI

# 原生 OpenAI
llm = ChatOpenAI(
    model="gpt-4o",
    api_key="sk-xxx",                         # 或读取环境变量
    base_url="https://api.openai.com/v1",
    temperature=0.7,
    max_tokens=2000,
)

# DeepSeek（兼容 OpenAI 接口）
llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com",
)

# 通义千问（兼容 OpenAI 接口）
llm = ChatOpenAI(
    model="qwen-plus",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# 智谱 GLM（兼容 OpenAI 接口）
llm = ChatOpenAI(
    model="glm-4-flash",
    api_key=os.getenv("ZHIPUAI_API_KEY"),
    base_url="https://open.bigmodel.cn/api/paas/v4",
)

# 硅基流动 / OpenRouter 等中转平台（兼容 OpenAI 接口）
llm = ChatOpenAI(
    model="Qwen/Qwen2.5-7B-Instruct",
    api_key="sk-xxx",
    base_url="https://api.siliconflow.cn/v1",
)
```

#### （2）ChatDeepSeek — 深度求索专用
```bash
pip install langchain-deepseek
```

```python
from langchain_deepseek import ChatDeepSeek

llm = ChatDeepSeek(
    model="deepseek-chat",        # 对话模型
    # model="deepseek-reasoner",  # 推理模型（DeepSeek-R1）
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    api_base="https://api.deepseek.com",  # 注意是 api_base，不是 base_url
    temperature=0.7,
)
```

#### （3）ChatAnthropic — Claude
```bash
pip install langchain-anthropic
```

```python
from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(
    model="claude-sonnet-4-6",    # 最新模型
    # model="claude-3-5-haiku-latest",  # 快速轻量模型
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    temperature=0.3,
    max_tokens=4000,
)
```

#### （4）ChatOllama — 本地模型
```bash
# 先安装并启动 Ollama
# 官网：https://ollama.com
# 拉取模型：ollama pull qwen3:8b
pip install langchain-ollama
```

```python
from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="qwen3:8b",                         # 使用 ollama list 查看本地可用模型
    base_url="http://localhost:11434",         # Ollama 默认地址
    temperature=0.7,
)
```

#### （5）ChatTongyi — 阿里通义千问专用
```bash
pip install langchain-community dashscope
```

```python
from langchain_community.chat_models import ChatTongyi

llm = ChatTongyi(
    model="qwen-plus",                        # qwen-turbo / qwen-plus / qwen-max
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    temperature=0.7,
)
```

#### （6）LangChain 1.0 统一初始化：`init_chat_model`
```python
from langchain.chat_models import init_chat_model

# 统一方式，只需换 provider 参数即可切换模型供应商
llm = init_chat_model(
    model="deepseek-chat",                    # 模型名
    model_provider="deepseek",                # 供应商：openai / deepseek / anthropic / ollama
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com",
)

# OpenAI
llm = init_chat_model(model="gpt-4o", model_provider="openai")

# 通义千问（兼容接口，provider 用 openai）
llm = init_chat_model(
    model="qwen-plus",
    model_provider="openai",
    api_key=DASHSCOPE_API_KEY,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# Ollama 本地
llm = init_chat_model(
    model="qwen3:8b",
    model_provider="ollama",
    base_url="http://localhost:11434",
)
```

### 3.3 模型参数速查
| 参数 | 说明 | 推荐值 |
| --- | --- | --- |
| `temperature` | 0~2，越高越有创造性 | 代码/翻译用 0.1<sub>0.3，写作/创意用 0.7</sub>1.0 |
| `top_p` | 核采样，只考虑概率前 N% 的词 | 一般 0.9，调此不调 temperature |
| `max_tokens` | 限制最大输出长度 | 按需设置，摘要 200，文章 2000 |
| `frequency_penalty` | 降低重复用词（-2 ~ 2） | 需要多样性时设 0.3~0.5 |
| `presence_penalty` | 鼓励引入新话题（-2 ~ 2） | 需要发散时设 0.3~0.5 |
| `streaming` | 是否开启流式输出 | 聊天场景开启 True |


### 3.4 调用方式对比
```python
# ===== 1. invoke — 同步调用（最常用） =====
response = llm.invoke("你好")
print(response.content)

# ===== 2. ainvoke — 异步调用 =====
import asyncio
async def main():
    response = await llm.ainvoke("你好")
    print(response.content)
asyncio.run(main())

# ===== 3. stream — 流式调用（打字机效果） =====
for chunk in llm.stream("写一首关于春天的诗"):
    print(chunk.content, end="", flush=True)

# ===== 4. batch — 批量调用 =====
responses = llm.batch(["问题1", "问题2", "问题3"])
for r in responses:
    print(r.content)
```

---

## 四、提示词模板（Prompt Templates）
### 4.1 PromptTemplate（纯文本模板）
```python
from langchain_core.prompts import PromptTemplate

# 定义模板
prompt = PromptTemplate.from_template("请用{style}的风格写一篇关于{topic}的短文")

# 填入变量，生成最终提示词
final_prompt = prompt.format(style="幽默", topic="程序员改 Bug")
# 结果："请用幽默的风格写一篇关于程序员改 Bug 的短文"

# 与模型串联使用
chain = prompt | llm
response = chain.invoke({"style": "幽默", "topic": "程序员改 Bug"})
```

### 4.2 ChatPromptTemplate（对话模板，最常用）
```python
from langchain_core.prompts import ChatPromptTemplate

# 方式1：from_messages — 精细控制每条消息的角色
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个{role}，擅长{skill}。"),      # System 消息（设定人设）
    ("user", "请帮我{task}"),                         # User 消息（用户问题）
])

chain = prompt | llm
response = chain.invoke({
    "role": "资深 Python 工程师",
    "skill": "代码审查",
    "task": "检查这段代码是否有安全问题",
})

# 方式2：from_template — 快捷方式（消息全是 user）
prompt = ChatPromptTemplate.from_template("将以下内容翻译成{language}：\n\n{text}")

# 方式3：少样本示例（Few-shot）
from langchain_core.prompts import FewShotChatMessagePromptTemplate

examples = [
    {"input": "今天天气真好", "output": "今天/天气/真好"},
    {"input": "我喜欢吃苹果", "output": "我/喜欢/吃/苹果"},
]
example_prompt = ChatPromptTemplate.from_messages([
    ("user", "{input}"),
    ("assistant", "{output}"),
])
few_shot_prompt = FewShotChatMessagePromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
)
final_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个中文分词工具，对用户输入进行分词"),
    few_shot_prompt,                               # 注入示例
    ("user", "{input}"),
])
```

### 4.3 MessagesPlaceholder（动态插入消息列表）
```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# 用于需要插入对话历史的场景
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个有用的助手"),
    MessagesPlaceholder(variable_name="history"),   # 对话历史插入位（类型：list）
    ("user", "{input}"),
])

# 使用时传入历史消息
chain = prompt | llm
response = chain.invoke({
    "history": [
        HumanMessage(content="我叫小明"),
        AIMessage(content="你好小明！"),
    ],
    "input": "我叫什么名字？",
})
```

### 4.4 PipelinePrompt（组合多个模板）
```python
from langchain_core.prompts import PipelinePromptTemplate, PromptTemplate

# 将多个子模板组合成一个最终模板
full_prompt = PromptTemplate.from_template("{introduction}\n\n{example}\n\n{start}")

introduction_prompt = PromptTemplate.from_template("你是一个{role}")
example_prompt = PromptTemplate.from_template("参考示例：\n{examples}")
start_prompt = PromptTemplate.from_template("现在开始：{input}")

# 组合
pipeline_prompt = PipelinePromptTemplate(
    final_prompt=full_prompt,
    pipeline_prompts=[
        ("introduction", introduction_prompt),
        ("example", example_prompt),
        ("start", start_prompt),
    ]
)
```

---

## 五、输出解析器（Output Parsers）
模型返回的是 `AIMessage` 对象，需要用 Parser 转换成你需要的格式。

### 5.1 StrOutputParser（提取纯文本，最常用）
```python
from langchain_core.output_parsers import StrOutputParser

parser = StrOutputParser()
chain = prompt | llm | parser

# 响应从 AIMessage(content="hello") 变成纯字符串 "hello"
result = chain.invoke({"key": "value"})
print(type(result))  # <class 'str'>
```

### 5.2 JsonOutputParser（JSON 格式输出）
```python
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

# 定义你想要的输出结构
class Person(BaseModel):
    name: str = Field(description="人物姓名")
    age: int = Field(description="年龄")

parser = JsonOutputParser(pydantic_object=Person)

# 把格式说明注入到提示词中
prompt = ChatPromptTemplate.from_template(
    "提取人物信息为 JSON 格式。\n{format_instructions}\n\n文本：{text}"
)

chain = prompt.partial(format_instructions=parser.get_format_instructions()) | llm | parser

result = chain.invoke({"text": "张三今年25岁，是一名软件工程师"})
print(result)  # {'name': '张三', 'age': 25}
```

### 5.3 PydanticOutputParser（Pydantic 模型输出）
```python
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List

class ArticleSummary(BaseModel):
    title: str = Field(description="文章标题")
    keywords: List[str] = Field(description="关键词列表，3-5个")
    summary: str = Field(description="100字以内的摘要")

parser = PydanticOutputParser(pydantic_object=ArticleSummary)

prompt = ChatPromptTemplate.from_template(
    "分析以下文章：\n{format_instructions}\n\n文章内容：{content}"
)
chain = prompt.partial(
    format_instructions=parser.get_format_instructions()
) | llm | parser

result = chain.invoke({"content": "今天 OpenAI 发布了 GPT-5..."})
print(result.title)      # "OpenAI 发布 GPT-5"
print(result.keywords)    # ['GPT-5', 'OpenAI', 'AI', '大模型']
```

### 5.4 CommaSeparatedListOutputParser（逗号分隔列表）
```python
from langchain_core.output_parsers import CommaSeparatedListOutputParser

parser = CommaSeparatedListOutputParser()
prompt = ChatPromptTemplate.from_template(
    "列出5个关于{topic}的{format_instructions}"
)
chain = prompt.partial(
    format_instructions=parser.get_format_instructions()
) | llm | parser

result = chain.invoke({"topic": "机器学习"})
print(result)  # ['深度学习', '自然语言处理', '计算机视觉', '强化学习', '迁移学习']
```

---

## 六、LCEL 链式编排（核心！）
**LCEL（LangChain Expression Language）** 是 LangChain 1.0 最重要的概念。用管道符 `|` 将组件串联，数据从左向右流动。

### 6.1 基础链条
```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

# 定义各组件
prompt = ChatPromptTemplate.from_template("将以下内容翻译成{language}：\n\n{text}")
llm = ChatOpenAI(model="gpt-4o-mini")
parser = StrOutputParser()

# 链式串联（核心语法！）
chain = prompt | llm | parser

# 数据流：dict → prompt（渲染模板）→ llm（生成 AIMessage）→ parser（提取字符串）
result = chain.invoke({"language": "日语", "text": "今天天气真好"})
print(result)  # "今日は天気がとても良いですね"
```

### 6.2 RunnablePassthrough（透传数据）
```python
from langchain_core.runnables import RunnablePassthrough

# 场景：需要把用户输入透传给多个模板占位符
chain = (
    {"topic": RunnablePassthrough(), "count": RunnablePassthrough()}
    | ChatPromptTemplate.from_template("关于{topic}，列出{count}个要点")
    | llm
    | parser
)
result = chain.invoke("Python")
# RunnablePassthrough() 把输入值 "Python" 原样传入 topic 和 count
```

### 6.3 使用函数预处理数据
```python
# 用 RunnableLambda 包装自定义函数
from langchain_core.runnables import RunnableLambda

def extract_and_format(input_dict):
    """预处理：提取长文本的前200字作为摘要"""
    text = input_dict["long_text"]
    return {"summary": text[:200], "full_text": text}

chain = (
    RunnableLambda(extract_and_format)        # 先预处理
    | prompt                                   # 再渲染模板
    | llm                                      # 调用模型
    | parser                                   # 解析输出
)
```

### 6.4 RunnableParallel（并行执行）
```python
from langchain_core.runnables import RunnableParallel

# 同时执行多个任务，互不阻塞
# 场景：对同一段文本同时做摘要和关键词提取
summary_chain = summary_prompt | llm | parser
keyword_chain = keyword_prompt | llm | parser

parallel_chain = RunnableParallel(
    summary=summary_chain,                     # 分支1：摘要
    keywords=keyword_chain,                    # 分支2：关键词
)
result = parallel_chain.invoke({"text": "很长的文章..."})
print(result["summary"])    # 摘要结果
print(result["keywords"])   # 关键词结果
```

### 6.5 RunnableBranch（条件路由）
```python
from langchain_core.runnables import RunnableBranch

# 根据条件选择不同的处理链
branch = RunnableBranch(
    # (条件函数, 对应的链)
    (lambda x: "数学" in x["topic"], math_chain),      # 数学问题走 math_chain
    (lambda x: "编程" in x["topic"], coding_chain),     # 编程问题走 coding_chain
    default_chain,  # 其他问题走默认链
)

full_chain = {"topic": RunnablePassthrough()} | branch
```

### 6.6 配置运行时参数
```python
# 使用 configurable_fields 让参数可配置
from langchain_core.runnables import ConfigurableField

configurable_llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
).configurable_fields(
    temperature=ConfigurableField(
        id="temperature",
        name="Temperature",
        description="控制输出的随机性",
    )
)

chain = prompt | configurable_llm | parser

# 调用时动态调整参数
result = chain.with_config(
    configurable={"temperature": 0.1}  # 这次调用使用低温度
).invoke({"input": "写一段代码"})
```

---

## 七、文档加载与文本分割
### 7.1 文档加载器（Document Loaders）
```python
# ===== 加载 PDF =====
# pip install pypdf
from langchain_community.document_loaders import PyPDFLoader
loader = PyPDFLoader("document.pdf")
pages = loader.load()           # 返回 List[Document]，每页一个
page = pages[0]
print(page.page_content)        # 页面文本内容
print(page.metadata)            # {'source': 'document.pdf', 'page': 1}

# ===== 加载纯文本 =====
from langchain_community.document_loaders import TextLoader
loader = TextLoader("knowledge.txt", encoding="utf-8")

# ===== 加载网页内容 =====
# pip install beautifulsoup4
from langchain_community.document_loaders import WebBaseLoader
loader = WebBaseLoader("https://docs.python.org/3/")
docs = loader.load()

# ===== 批量加载目录 =====
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import TextLoader
loader = DirectoryLoader("./docs/", glob="**/*.txt", loader_cls=TextLoader)
docs = loader.load()

# ===== 加载 CSV =====
from langchain_community.document_loaders import CSVLoader
loader = CSVLoader("data.csv", encoding="utf-8")
```

**常用 Document Loader 一览：**

| Loader | 安装 | 用途 |
| --- | --- | --- |
| `PyPDFLoader` | `pypdf` | PDF 文件 |
| `TextLoader` | 内置 | 纯文本 |
| `CSVLoader` | 内置 | CSV 文件 |
| `UnstructuredMarkdownLoader` | `unstructured` | Markdown |
| `WebBaseLoader` | `beautifulsoup4` | 网页抓取 |
| `DirectoryLoader` | 内置 | 批量加载目录 |


### 7.2 文本分割器（Text Splitters）
**核心概念**：LLM 上下文窗口有限，需要把长文档切成小块（chunk）。

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 最推荐的分割器：按语义分隔符递归切割
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,              # 每块最大字符数
    chunk_overlap=200,            # 块之间重叠 200 字符（保持语义连贯，非常重要！）
    separators=[                  # 优先级从高到低的语义分隔符
        "\n\n",                    # 优先在段落之间切割
        "\n",                     # 其次在行之间
        "。",                      # 中文句号
        "！",                      # 中文感叹号
        "？",                      # 中文问号
        ".",                       # 英文句号
        " ",                       # 最后才是空格
        "",                        # 实在不行就硬切
    ],
    length_function=len,          # 长度计算函数
)

# 切割文本
chunks = text_splitter.split_text(long_text)

# 切割文档对象
chunks = text_splitter.split_documents(documents)

# 结果查看
for chunk in chunks[:3]:
    print(f"长度: {len(chunk.page_content)}, 内容: {chunk.page_content[:100]}...")
```

**其他分割器：**

| 分割器 | 适用场景 |
| --- | --- |
| `RecursiveCharacterTextSplitter` | **通用首选**：按语义分隔符递归切割 |
| `CharacterTextSplitter` | 简单按字符数切割 |
| `MarkdownHeaderTextSplitter` | Markdown 按标题层级切割 |
| `TokenTextSplitter` | 按 token 数切割（需 `tiktoken`） |
| `PythonCodeTextSplitter` | Python 代码（按函数/类边界） |


**chunk_size 和 chunk_overlap 选值建议：**

| 场景 | chunk_size | chunk_overlap |
| --- | --- | --- |
| 短问答/FAQ | 200~500 | 50~100 |
| 通用文档问答 | 800~1200 | 150~200 |
| 长文档深度分析 | 1500~2000 | 200~400 |


---

## 八、Embeddings（向量嵌入）
Embedding 的作用：**把文本转换成数学向量**。语义相近的文本，向量距离也近。

### 8.1 各种 Embedding 模型
```python
# ===== OpenAI Embedding（云端付费） =====
from langchain_openai import OpenAIEmbeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
# model: text-embedding-3-small（便宜）/ text-embedding-3-large（效果好）

# ===== 通义千问 Embedding =====
from langchain_community.embeddings import DashScopeEmbeddings
embeddings = DashScopeEmbeddings(
    model="text-embedding-v3",            # v1 / v2 / v3
    dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
)

# ===== HuggingFace 开源模型（本地免费） =====
# pip install langchain-huggingface sentence-transformers
from langchain_huggingface import HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-zh-v1.5",  # 中文推荐（BGE 系列）
    # model_name="sentence-transformers/all-MiniLM-L6-v2",  # 英文推荐
    model_kwargs={'device': 'cpu'},        # 'cpu' 或 'cuda'
    encode_kwargs={'normalize_embeddings': True},
)

# ===== Ollama 本地 Embedding =====
from langchain_ollama import OllamaEmbeddings
embeddings = OllamaEmbeddings(
    model="nomic-embed-text",             # 先 ollama pull nomic-embed-text
    base_url="http://localhost:11434",
)
```

### 8.2 文本转向量
```python
# 单条文本
vector = embeddings.embed_query("你好世界")
print(len(vector))  # 1536（OpenAI）/ 768（BGE）/ 其他

# 批量文本
vectors = embeddings.embed_documents(["文本1", "文本2", "文本3"])
print(len(vectors))  # 3
```

---

## 九、向量数据库（Vector Store）
### 9.1 Chroma（推荐！最易上手）
```python
# pip install langchain-chroma

from langchain_chroma import Chroma

# ===== 创建向量库 + 存储 =====
vectorstore = Chroma.from_documents(
    documents=chunks,                         # 文本块
    embedding=embeddings,                     # 嵌入模型
    persist_directory="./chroma_db",          # 持久化目录
)

# ===== 加载已有向量库 =====
vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings,
)

# ===== 相似度检索 =====
docs = vectorstore.similarity_search("什么是机器学习？", k=4)  # k=返回条数

# 遍历结果
for doc in docs:
    print(f"来源: {doc.metadata}")
    print(f"内容: {doc.page_content[:100]}...\n")

# ===== 带元数据过滤的检索 =====
docs = vectorstore.similarity_search(
    "技术文章",
    k=3,
    filter={"source": "manual.pdf", "page": {"$gte": 10}}  # 只查 manual.pdf 的第10页之后
)

# ===== 返回相似度分数 =====
docs_with_scores = vectorstore.similarity_search_with_relevance_scores("查询内容", k=5)
for doc, score in docs_with_scores:
    print(f"分数: {score:.3f}, 内容: {doc.page_content[:50]}...")

# ===== MMR 检索（最大边际相关性，结果更多样化） =====
docs = vectorstore.max_marginal_relevance_search(
    "查询内容",
    k=4,
    fetch_k=20,        # 先取20条候选，再从中挑4条最多样的
    lambda_mult=0.5,   # 0=最大化多样性，1=最大化相似度
)

# ===== 转为检索器 =====
retriever = vectorstore.as_retriever(
    search_type="similarity",          # "similarity" / "mmr" / "similarity_score_threshold"
    search_kwargs={"k": 5},
)
docs = retriever.invoke("查询内容")
```

### 9.2 FAISS（高性能）
```python
# pip install faiss-cpu  （或 faiss-gpu）

from langchain_community.vectorstores import FAISS

# 创建
vectorstore = FAISS.from_documents(chunks, embeddings)

# 保存到磁盘
vectorstore.save_local("faiss_index/")

# 从磁盘加载
vectorstore = FAISS.load_local(
    "faiss_index/",
    embeddings,
    allow_dangerous_deserialization=True,  # ⚠️ 只加载自己创建的文件
)

# 检索（用法同 Chroma）
docs = vectorstore.similarity_search("查询内容", k=4)
```

### 9.3 向量数据库选型对比
| 特性 | Chroma | FAISS | Milvus | Pinecone |
| --- | --- | --- | --- | --- |
| 部署方式 | 本地 pip 安装 | 本地 pip 安装 | 需部署服务 | SaaS 云服务 |
| 持久化 | ✅ 内置 | ✅ save_local | ✅ 自动 | ✅ 云端 |
| 元数据过滤 | ✅ 完善 | ❌ 基础 | ✅ 完善 | ✅ 完善 |
| 规模 | 小~中 | 大 | 超大 | 大 |
| 上手难度 | ⭐ 简单 | ⭐⭐ 中等 | ⭐⭐⭐ | ⭐ 简单 |
| 费用 | 免费 | 免费 | 免费/开源 | 付费 |
| **适合场景** | 开发测试、中小项目 | 高性能本地部署 | 企业级生产 | 快速上线 |


---

## 十、RAG（检索增强生成）完整实战
**RAG = 检索 + 生成**：先从知识库检索相关内容，再让 LLM 基于这些内容回答问题，解决 LLM 不知道私有知识、"幻觉"编造信息的问题。

### 10.1 基础 RAG 流程
```python
# 完整 RAG 流程：文档 → 分块 → 向量化 → 检索 → 生成答案
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# 步骤1: 加载文档
loader = PyPDFLoader("knowledge_base.pdf")
documents = loader.load()

# 步骤2: 分割文本
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)
chunks = text_splitter.split_documents(documents)

# 步骤3: 向量化 + 存储
vectorstore = Chroma.from_documents(
    chunks,
    OpenAIEmbeddings(model="text-embedding-3-small"),
    persist_directory="./rag_db",
)

# 步骤4: 创建检索器
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

# 步骤5: 定义 RAG 提示词模板
template = """你是一个专业的知识问答助手。请仅根据以下参考内容回答问题。
如果参考内容中没有相关信息，请如实说"我不确定"。
不要编造任何信息。

参考内容：
{context}

用户问题：{question}

回答："""

prompt = ChatPromptTemplate.from_template(template)

# 步骤6: 构建 RAG 链
def format_docs(docs):
    """将检索到的文档拼接成一个上下文字符串"""
    return "\n\n".join(f"来源：{doc.metadata.get('source', '未知')}\n{doc.page_content}" for doc in docs)

rag_chain = (
    {
        "context": retriever | format_docs,       # 检索 + 格式化上下文
        "question": RunnablePassthrough(),         # 原样传入用户问题
    }
    | prompt                                       # 填入提示词模板
    | ChatOpenAI(model="gpt-4o-mini")              # 调用 LLM
    | StrOutputParser()                            # 提取纯文本
)

# 步骤7: 提问！
answer = rag_chain.invoke("公司的年假政策是什么？")
print(answer)
```

### 10.2 带对话历史的 RAG
```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage

# 带对话历史的 RAG 提示词
contextual_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个问答助手。根据以下参考内容回答问题：\n\n{context}"),
    MessagesPlaceholder(variable_name="chat_history"),  # 对话历史
    ("user", "{question}"),
])

# 每次调用时传入历史
def ask_with_history(question, chat_history):
    docs = retriever.invoke(question)
    context = format_docs(docs)
    return llm.invoke(contextual_prompt.format(
        context=context,
        chat_history=chat_history,
        question=question,
    ))

# 使用
history = []
while True:
    question = input("你: ")
    response = ask_with_history(question, history)
    print(f"AI: {response.content}")
    # 更新历史
    history.append(HumanMessage(content=question))
    history.append(response)
```

### 10.3 高级检索策略
```python
# ===== 1. 自查询检索器（SelfQueryRetriever） =====
# LLM 自动从用户问题中提取过滤条件
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo

# 定义元数据字段
metadata_field_info = [
    AttributeInfo(name="source", description="文档来源", type="string"),
    AttributeInfo(name="date", description="文档日期", type="string"),
    AttributeInfo(name="category", description="文档分类", type="string"),
]

retriever = SelfQueryRetriever.from_llm(
    llm=llm,
    vectorstore=vectorstore,
    document_contents="技术文档集合",
    metadata_field_info=metadata_field_info,
)
# 用户问："2024年的Python相关文档" → LLM自动生成过滤条件 {date: "2024", category: "Python"}


# ===== 2. 混合检索（EnsembleRetriever） =====
# 同时用 BM25（关键词匹配）+ 语义检索（向量相似度）
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever

bm25_retriever = BM25Retriever.from_documents(chunks)
bm25_retriever.k = 5

semantic_retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

# 混合检索：取两种结果加权合并
hybrid_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, semantic_retriever],
    weights=[0.3, 0.7],       # BM25 占 30%，语义检索占 70%
)


# ===== 3. 上下文压缩检索器（ContextualCompressionRetriever） =====
# 先检索，再用 LLM 筛选出真正相关的内容（只保留有用片段，去掉噪音）
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

compressor = LLMChainExtractor.from_llm(llm)  # LLM 对每个候选片段打相关分
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=vectorstore.as_retriever(search_kwargs={"k": 10}),
)
# 先取 10 条检索结果，再用 LLM 压缩过滤，只保留真正相关的
```

### 10.4 RAG 性能优化清单
| 优化点 | 方案 |
| --- | --- |
| **检索不准** | 调整 chunk_size / chunk_overlap；用混合检索（BM25+语义） |
| **检索到无关内容** | 用 `ContextualCompressionRetriever` 二次过滤 |
| **答案质量差** | 优化提示词模板；用 `refine` 链而非 `stuff` 链 |
| **速度慢** | 减小 chunk_size；使用更快的 Embedding 模型 |
| **中文效果差** | 使用 BGE 中文 Embedding 模型；调整分隔符包含中文标点 |
| **历史理解差** | 加入对话历史到提示词中 |


---

## 十一、消息历史与记忆（Memory）
### 11.1 消息类型
```python
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage

# 四种消息类型
HumanMessage(content="用户说的话")          # 用户消息
AIMessage(content="AI 的回复")              # AI 回复
SystemMessage(content="系统指令/人设")       # 系统指令
ToolMessage(content="工具返回结果",          # 工具调用结果
             tool_call_id="call_xxx")
```

### 11.2 使用列表管理对话历史（最简单）
```python
# 维护一个消息列表作为历史
messages = [
    SystemMessage(content="你是专业的技术顾问"),
]

while True:
    user_input = input("你: ")
    messages.append(HumanMessage(content=user_input))

    response = llm.invoke(messages)
    messages.append(response)              # AIMessage 本身可追加

    print(f"AI: {response.content}")

    if len(messages) > 20:                 # 保持最近10轮对话
        messages = messages[:1] + messages[-20:]
```

### 11.3 ChatMessageHistory（自动管理）
```python
from langchain_community.chat_message_histories import ChatMessageHistory

# 创建历史管理器
history = ChatMessageHistory()
history.add_user_message("你好")
history.add_ai_message("你好！有什么可以帮你的？")
history.add_user_message("Python 怎么做异步编程？")

# 查看历史
for msg in history.messages:
    print(f"{msg.type}: {msg.content}")
```

### 11.4 带总结的长对话记忆
当对话变得很长时，自动对早期内容做摘要压缩：

```python
from langchain.memory import ConversationSummaryMemory

memory = ConversationSummaryMemory(
    llm=llm,
    max_token_limit=200,            # 摘要保留的字数上限
    return_messages=True,
)

# 保存对话
memory.save_context(
    {"input": "我叫张三，是一名 Python 工程师"},
    {"output": "你好张三！有什么 Python 问题需要帮助？"}
)

# 之后的调用会自动携带历史摘要
print(memory.load_memory_variables({})["history"])
# → "The human introduces himself as Zhang San, a Python engineer..."
```

---

## 十二、工具定义（Tools）
Tool 是让 LLM 执行具体操作（搜索、计算、API 调用等）的桥梁。LLM 决定"该调哪个工具、传什么参数"，Tool 执行并返回结果。

### 12.1 @tool 装饰器（最推荐）
```python
from langchain.tools import tool
from langchain_core.tools import ToolRuntime
import requests
import math

# ===== 基础工具 =====
@tool
def search_web(query: str) -> str:
    """搜索互联网获取实时信息。当需要最新资讯时使用。"""
    # 函数名 → 工具名称
    # Docstring → 工具描述（LLM 据此判断何时调用此工具）
    # 类型提示 → 参数 Schema（LLM 据此生成正确的参数）
    return f"搜索结果：关于'{query}'的信息..."

# ===== 带默认参数的工具 =====
@tool
def calculator(expression: str) -> str:
    """执行数学计算。例如用户要求计算 123*456 时使用。"""
    try:
        result = eval(expression)  # 实际生产请用更安全的方式
        return f"计算结果：{expression} = {result}"
    except Exception as e:
        return f"计算出错：{e}"

# ===== 调用外部 API 的工具 =====
@tool
def get_weather(city: str) -> str:
    """查询指定城市的实时天气。参数 city 为城市中文名称。"""
    # 实际项目中调用天气 API
    api_url = f"https://api.weather.com/v1/current?city={city}"
    response = requests.get(api_url)
    return response.json()["summary"]


# ===== 使用 Pydantic 定义复杂参数的工具 =====
from pydantic import BaseModel, Field
from typing import Literal

class DatabaseSearchInput(BaseModel):
    """数据库搜索的参数模型"""
    table: str = Field(description="要查询的表名")
    field: str = Field(description="要查询的字段名")
    condition: str = Field(default="", description="过滤条件，如 age>25")
    limit: int = Field(default=10, description="返回条数上限")

@tool(args_schema=DatabaseSearchInput)
def search_database(table: str, field: str, condition: str = "", limit: int = 10) -> str:
    """搜索数据库中的记录"""
    # 实际项目中执行数据库查询
    return f"从表 {table} 查询字段 {field}，条件 {condition}，返回 {limit} 条"
```

### 12.2 通过 Tool 对象定义
```python
from langchain_core.tools import Tool

# 适合简单函数或 lambda
tools = [
    Tool(
        name="UpperCase",               # 工具名称
        func=lambda x: x.upper(),       # 执行函数
        description="将文本转换为大写",   # 工具描述（重要！）
    ),
]
```

### 12.3 StructuredTool（更灵活的参数定义）
```python
from langchain_core.tools import StructuredTool

def multiply(a: int, b: int) -> int:
    """将两个整数相乘"""
    return a * b

calc_tool = StructuredTool.from_function(
    func=multiply,
    name="multiply",
    description="将两个整数相乘。参数 a 和 b 为整数。",
)
```

---

## 十三、Agent 智能体
**Agent = LLM + Tools**。LLM 自主决定"什么时候调用哪个工具、传什么参数"，看到工具结果后再决定"是继续调其他工具，还是给出最终回答"。

### 13.1 create_agent（LangChain 1.0 推荐）
```python
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

# 准备工作：定义工具
@tool
def web_search(query: str) -> str:
    """搜索互联网，获取最新信息"""
    return f"关于'{query}'的搜索结果：..."

@tool
def get_current_time() -> str:
    """获取当前的日期和时间"""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 创建 Agent
agent = create_agent(
    model=ChatOpenAI(model="gpt-4o"),
    tools=[web_search, get_current_time],
    system_prompt="你是一个有帮助的助手。遇到不确定的信息时请使用搜索工具。",
)

# 调用 Agent
result = agent.invoke({
    "messages": [
        {"role": "user", "content": "今天的日期是什么？另外帮我搜索一下今天的科技新闻"}
    ]
})

# 获取最终回答
print(result["messages"][-1].content)
```

### 13.2 create_agent 常用参数
| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| `model` | LLM 模型实例 | 必填 |
| `tools` | 工具列表 | `[]` |
| `system_prompt` | 系统提示词 | `None` |
| `max_iterations` | 最大迭代次数（防止死循环） | 25 |
| `middleware` | 中间件列表（在模型调用前后插入逻辑） | `[]` |
| `checkpointer` | 检查点保存器（用于记忆跨轮次状态） | `None` |
| `interrupt_before` | 在执行哪些节点前暂停（人工介入） | `[]` |
| `interrupt_after` | 在执行哪些节点后暂停（人工介入） | `[]` |


### 13.3 Agent + 记忆（跨轮次对话）
```python
from langgraph.checkpoint.memory import MemorySaver

# 创建带记忆的 Agent
agent = create_agent(
    model=llm,
    tools=[web_search, calculator],
    system_prompt="你是一个专业的助手",
    checkpointer=MemorySaver(),          # 使用内存检查点保存器
)

# 使用 thread_id 区分不同的对话
config = {"configurable": {"thread_id": "user-001"}}

# 第一轮
result = agent.invoke(
    {"messages": [{"role": "user", "content": "我叫张三"}]},
    config=config,
)

# 第二轮（同一 thread_id，能记住上一轮的内容）
result = agent.invoke(
    {"messages": [{"role": "user", "content": "我叫什么名字？"}]},
    config=config,
)
print(result["messages"][-1].content)  # → "你叫张三"
```

### 13.4 Agent 中间件
中间件可以拦截 Agent 的每一次模型调用，做日志记录、权限检查等：

```python
from langchain.agents.middleware import AgentMiddleware

class LoggingMiddleware(AgentMiddleware):
    """在每次 LLM 调用前后打印日志"""

    def before_model(self, state, runtime):
        print(f"[即将调用模型] 当前消息数: {len(state['messages'])}")
        return None  # 返回 None 表示不修改状态，继续执行

    def after_model(self, state, runtime):
        print(f"[模型调用完成] 返回消息数: {len(state['messages'])}")
        return None

agent = create_agent(
    model=llm,
    tools=tools,
    middleware=[LoggingMiddleware()],
)
```

### 13.5 Agent 传统写法（兼容旧版本）
```python
# 仅在维护旧项目时需要了解
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub

# 拉取 ReAct 提示词模板
prompt = hub.pull("hwchase17/react")

# 创建 ReAct Agent
agent = create_react_agent(llm, tools, prompt)

# 用 AgentExecutor 包裹执行
executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,              # 打印执行过程
    max_iterations=10,         # 最大迭代次数
    handle_parsing_errors=True, # 自动处理格式解析错误
)

result = executor.invoke({"input": "搜索最新 AI 新闻"})
print(result["output"])
```

---

## 十四、LangGraph 状态图（进阶）
LangGraph 底层全部是 LangGraph 的 `StateGraph`（状态图）。理解状态图，才能真正理解 Agent 的运行机制。

### 14.1 核心概念
一个 LangGraph 应用由四个要素构成：

| 概念 | 说明 |
| --- | --- |
| **State（状态）** | 全局共享的数据字典，贯穿所有节点 |
| **Node（节点）** | 处理单元，接收 State → 执行逻辑 → 返回 State 的增量 |
| **Edge（边）** | 连接规则：静态边（固定流向）/ 条件边（动态路由） |
| **Graph（图）** | 将 Node 和 Edge 组合在一起，编译成可执行的应用 |


### 14.2 构建自定义 StateGraph
```python
from typing import TypedDict, Annotated, Literal
import operator
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage

# ===== 步骤1：定义状态结构 =====
class AgentState(TypedDict):
    """所有节点共享的状态"""
    messages: Annotated[list, operator.add]  # Annotated + operator.add = 追加而非覆盖
    current_step: str                         # 当前步骤名（条件路由时用）

# ===== 步骤2：定义节点函数 =====
def call_model(state: AgentState) -> dict:
    """节点：调用 LLM"""
    llm = ChatOpenAI(model="gpt-4o-mini")
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

def human_approval(state: AgentState) -> dict:
    """节点：人工审批（模拟）"""
    last_message = state["messages"][-1]
    print(f"--- 需要审批的消息：{last_message.content[:100]} ---")
    approved = input("批准? (y/n): ")
    if approved.lower() == "y":
        return {"messages": [AIMessage(content="已批准")]}
    return {"messages": [AIMessage(content="审批未通过，请修改")]}

# ===== 步骤3：定义条件路由函数 =====
def should_continue(state: AgentState) -> Literal["approval", END]:
    """根据 LLM 的响应决定下一步"""
    last_message = state["messages"][-1]
    if "需要审批" in last_message.content:
        return "approval"   # 流转到审批节点
    return END              # 结束

# ===== 步骤4：构建图 =====
workflow = StateGraph(AgentState)

# 注册节点
workflow.add_node("model", call_model)
workflow.add_node("approval", human_approval)

# 注册边
workflow.add_edge(START, "model")          # 入口 → model 节点

# 条件边：从 model 节点出发，根据条件决定去 approval 还是 END
workflow.add_conditional_edges(
    "model",                                # 从哪个节点出发
    should_continue,                        # 条件函数
    {
        "approval": "approval",             # 如果返回 "approval" → 去 approval 节点
        END: END,                           # 如果返回 END → 结束
    }
)

workflow.add_edge("approval", END)          # 审批完成后结束

# ===== 步骤5：编译并运行 =====
app = workflow.compile()

result = app.invoke({
    "messages": [HumanMessage(content="我想请假三天，需要审批")]
})

# 打印全流程消息
for msg in result["messages"]:
    print(f"[{msg.type}]: {msg.content}")
```

### 14.3 Agent 的 ReAct 循环模型
标准 Agent 就是一个 ReAct 循环：**思考 → 行动 → 观察 → 再思考**，直到给出最终答案：

```plain
                    ┌──────────────────────┐
                    │       Agent 节点      │
                    │  （LLM 决定调哪个工具）│
                    └───────┬──────────────┘
                            │
                    ┌───────▼──────────────┐
                    │   条件路由判断         │
                    │  有 tool_calls?       │
                    └───┬─────────────┬────┘
                        │ YES         │ NO
                ┌───────▼──────┐    ┌▼────┐
                │  Tools 节点   │    │ END │
                │（执行工具调用）│    └─────┘
                └───────┬──────┘
                        │
                        └────→ 回到 Agent 节点（循环）
```

### 14.4 带检查点的跨轮次记忆
```python
from langgraph.checkpoint.memory import MemorySaver

# 创建检查点保存器
memory = MemorySaver()

# 编译时传入检查点
app = workflow.compile(checkpointer=memory)

# 使用 thread_id 隔离不同对话
config = {"configurable": {"thread_id": "conversation-1"}}

# 第一轮对话
app.invoke({"messages": [HumanMessage(content="我叫王五")]}, config=config)

# 第二轮对话（自动加载之前的检查点，状态延续）
result = app.invoke(
    {"messages": [HumanMessage(content="我叫什么名字？")]},
    config=config
)

# 查看对话状态历史
states = list(app.get_state_history(config))
for state in states:
    print(f"步骤: {state.next}")

# 查看当前完整状态
current_state = app.get_state(config)
print(current_state.values["messages"])
```

### 14.5 子图（Subgraph）嵌套
```python
# 将一个已编译的 Graph 作为另一个 Graph 的节点
from langgraph.graph import StateGraph

# 定义子图
subgraph = StateGraph(SomeState)
# ... 构建子图逻辑 ...
compiled_subgraph = subgraph.compile()

# 将子图作为节点嵌入父图
parent = StateGraph(ParentState)
parent.add_node("sub_process", compiled_subgraph)  # 子图作为一个节点！
parent.add_edge(START, "sub_process")
parent.add_edge("sub_process", END)

app = parent.compile()
```

---

## 十五、回调机制（Callbacks）
### 15.1 回调事件类型
| 事件 | 触发时机 |
| --- | --- |
| `on_llm_start` | LLM 调用开始前 |
| `on_llm_new_token` | 流式输出时每生成一个 token |
| `on_llm_end` | LLM 调用完成 |
| `on_llm_error` | LLM 调用出错 |
| `on_chain_start` | Chain 开始执行 |
| `on_chain_end` | Chain 执行结束 |
| `on_tool_start` | 工具开始执行 |
| `on_tool_end` | 工具执行完成 |
| `on_tool_error` | 工具执行出错 |
| `on_retriever_start` | 检索器开始 |
| `on_retriever_end` | 检索器完成 |


### 15.2 自定义回调处理器
```python
# callbacks.py
import time
from langchain.callbacks.base import BaseCallbackHandler

class CostTrackerCallback(BaseCallbackHandler):
    """追踪 API 调用成本和耗时"""

    def __init__(self):
        self.total_tokens = 0
        self.total_cost = 0
        self.start_time = None

    def on_llm_start(self, serialized, prompts, **kwargs):
        self.start_time = time.time()
        print(f"[LLM 开始] 发送了 {len(prompts)} 条提示")

    def on_llm_end(self, response, **kwargs):
        elapsed = time.time() - self.start_time
        # 从响应中提取 token 用量
        usage = response.llm_output.get("token_usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        self.total_tokens += prompt_tokens + completion_tokens

        print(f"[LLM 完成] 耗时 {elapsed:.2f}s | "
              f"输入 {prompt_tokens} tokens | 输出 {completion_tokens} tokens")

    def on_llm_error(self, error, **kwargs):
        print(f"[LLM 错误] {error}")

    def on_tool_start(self, serialized, input_str, **kwargs):
        tool_name = serialized.get("name", "unknown")
        print(f"[工具调用] {tool_name}: {input_str}")

    def on_tool_end(self, output, **kwargs):
        print(f"[工具返回] {output}")


# 使用
callback = CostTrackerCallback()
chain = prompt | llm | parser
result = chain.invoke(
    {"input": "写一首诗"},
    config={"callbacks": [callback]},  # 通过 config 传入回调
)
```

---

## 十六、流式输出（Streaming）
### 16.1 基础流式输出
```python
# ===== 同步流式 =====
llm = ChatOpenAI(model="gpt-4o-mini", streaming=True)

for chunk in llm.stream("写一篇关于AI未来的短文"):
    print(chunk.content, end="", flush=True)  # 逐 token 打印

# ===== 异步流式 =====
import asyncio

async def stream_response():
    llm = ChatOpenAI(model="gpt-4o-mini", streaming=True)
    async for chunk in llm.astream("介绍量子计算"):
        print(chunk.content, end="", flush=True)

asyncio.run(stream_response())

# ===== Chain 流式 =====
chain = prompt | llm | parser
for chunk in chain.stream({"input": "写一首诗"}):  # StrOutputParser 也支持流式
    print(chunk, end="", flush=True)
    # 注意：经过 parser 后，chunk 是字符串而非 AIMessageChunk
```

### 16.2 FastAPI + 流式输出
```python
# app.py
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

app = FastAPI()

async def generate_response(question: str):
    """生成流式响应的生成器函数"""
    prompt = ChatPromptTemplate.from_template("{question}")
    llm = ChatOpenAI(model="gpt-4o-mini", streaming=True)
    chain = prompt | llm

    async for chunk in chain.astream({"question": question}):
        yield chunk.content

@app.post("/chat")
async def chat(question: str):
    return StreamingResponse(
        generate_response(question),
        media_type="text/event-stream",
    )
```

---

## 十七、LangSmith 监控与调试
LangSmith 是 LangChain 官方的可观测性平台，用于记录、调试、评估 LLM 应用。

### 17.1 快速接入
```python
# 设置环境变量（或写在 .env 文件中）
# LANGCHAIN_TRACING_V2=true
# LANGCHAIN_API_KEY=lsv2-pt-your-api-key
# LANGCHAIN_PROJECT=my-project-name

# Python 代码中无需额外操作，所有 LangChain 调用会自动被追踪

# 执行任何 LangChain 操作即可在 LangSmith 后台看到追踪记录
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o-mini")
response = llm.invoke("你好")
# → 登录 https://smith.langchain.com 查看完整调用链
```

### 17.2 用户反馈收集
```python
from langsmith import Client

client = Client()

def save_feedback(run_id: str, score: int, comment: str = ""):
    """保存用户反馈到 LangSmith"""
    client.create_feedback(
        run_id,
        key="user_feedback",
        score=score,            # 1.0 好评，0.0 差评
        comment=comment,        # 可选评语
    )

# 在用户反馈逻辑中使用
# 例如：用户点了"赞"
# save_feedback(run_id, 1.0, "回答很准确")
```

---

## 十八、常用代码片段速查
### 18.1 最简单的 LLM 调用
```python
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o-mini")
print(llm.invoke("你好").content)
```

### 18.2 简单翻译链
```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

chain = (
    ChatPromptTemplate.from_template("将以下内容翻译成{target_lang}：\n{text}")
    | ChatOpenAI(model="gpt-4o-mini")
    | StrOutputParser()
)
print(chain.invoke({"target_lang": "英文", "text": "今天天气真好"}))
```

### 18.3 RAG 一句话代码框架
```python
rag = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
```

### 18.4 创建带工具的 Agent
```python
from langchain.agents import create_agent

agent = create_agent(
    model=ChatOpenAI(model="gpt-4o"),
    tools=[my_tool1, my_tool2],
    system_prompt="你是一个有用的助手",
)
agent.invoke({"messages": [{"role": "user", "content": "帮我..."}]})
```

### 18.5 常用 pip 安装命令
```bash
# 快速开始全家桶
pip install langchain langchain-openai langchain-community python-dotenv

# RAG
pip install chromadb langchain-chroma tiktoken

# 文档处理
pip install pypdf beautifulsoup4 lxml unstructured

# Agent + 工具
pip install langgraph

# 监控
pip install langsmith

# Web 服务
pip install fastapi uvicorn sse-starlette
```

### 18.6 开发工作流
```plain
1. 在 .env 配置 API Key
2. 创建模型实例: llm = ChatOpenAI(model="gpt-4o-mini")
3. 写提示词模板: prompt = ChatPromptTemplate.from_template(...)
4. 串联链: chain = prompt | llm | StrOutputParser()
5. 测试: chain.invoke({...})
6. 加入工具: @tool 定义 → create_agent
7. 加入检索: 加载文档 → 分块 → 向量化 → retriever
8. 上线: FastAPI + StreamingResponse
```

### 18.7 常见错误排查
```python
# 1. 查看链的实际运行过程（调试神器）
import langchain
langchain.debug = True
chain.invoke({"input": "test"})
langchain.debug = False

# 2. 查看模型实际收到的提示词
prompt = ChatPromptTemplate.from_template("{input}")
formatted = prompt.format(input="测试")
print(formatted)

# 3. 查看检索到的文档
docs = retriever.invoke("查询内容")
for i, doc in enumerate(docs):
    print(f"[{i}] 来源: {doc.metadata}, 内容: {doc.page_content[:100]}...")
```

---

> **参考来源**：[LangChain 官方文档](https://python.langchain.com/) | [LangGraph 文档](https://langchain-ai.github.io/langgraph/)  
**适用版本**：LangChain 1.0+ / LangGraph 0.2+  
**最后更新**：2026-05
>

