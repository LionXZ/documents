# AI Agent 全流程开发指南：从 0 到 1 使用 LangChain v1.3

> 以一个**"AI 智能编程助手"**项目为主线，完整覆盖环境搭建 → 工具开发 → RAG 检索 → Agent 构建 → MCP 集成 → 测试评估 → 生产部署的全流程。

---

## 目录

- [第 1 章 项目概述与需求分析](#第-1-章-项目概述与需求分析)
- [第 2 章 环境搭建](#第-2-章-环境搭建)
- [第 3 章 项目工程结构](#第-3-章-项目工程结构)
- [第 4 章 配置管理](#第-4-章-配置管理)
- [第 5 章 模型层封装](#第-5-章-模型层封装)
- [第 6 章 工具开发](#第-6-章-工具开发)
- [第 7 章 RAG 检索增强生成](#第-7-章-rag-检索增强生成)
- [第 8 章 记忆系统](#第-8-章-记忆系统)
- [第 9 章 中间件体系](#第-9-章-中间件体系)
- [第 10 章 Agent 组装](#第-10-章-agent-组装)
- [第 11 章 MCP 工具集成](#第-11-章-mcp-工具集成)
- [第 12 章 流式输出与 API 服务](#第-12-章-流式输出与-api-服务)
- [第 13 章 测试与评估](#第-13-章-测试与评估)
- [第 14 章 生产部署](#第-14-章-生产部署)
- [第 15 章 可观测性](#第-15-章-可观测性)
- [第 16 章 完整项目代码汇总](#第-16-章-完整项目代码汇总)

---

# 第 1 章 项目概述与需求分析

## 1.1 项目定义

构建一个 **"AI 编程助手"（DevAssistant）**，帮助开发者在日常工作中：

- 回答编程问题（基于知识库 RAG）
- 分析代码文件并给出审查建议
- 搜索互联网上的技术文档
- 执行简单的代码生成和重构
- 记住用户的编程偏好和技术栈

## 1.2 功能需求

| 功能 | 技术方案 | 优先级 |
|------|---------|--------|
| 编程知识问答 | RAG + 向量数据库 | P0 |
| 代码文件分析 | Filesystem 工具 | P0 |
| 互联网搜索 | Tavily Search API | P1 |
| 代码审查 | 结构化输出 + 自定义工具 | P1 |
| 用户偏好记忆 | LangGraph Store（长期记忆） | P2 |
| 对话历史 | Checkpointer（短期记忆） | P0 |
| 上下文压缩 | SummarizationMiddleware | P2 |
| 流式输出 | astream_events | P0 |
| MCP 外部工具 | MCP Client | P1 |

## 1.3 技术栈选型

| 技术 | 选型 | 原因 |
|------|------|------|
| 框架 | LangChain v1.3 + LangGraph v1.2 | 最新 Agent 架构 |
| 模型 | GPT-4o（主力）+ GPT-4o-mini（摘要/路由） | 性能+成本平衡 |
| 向量数据库 | ChromaDB | 轻量开源，开发友好 |
| 嵌入模型 | text-embedding-3-small | OpenAI 生态，性价比高 |
| 搜索 API | Tavily Search | LangChain 原生支持 |
| Web 框架 | FastAPI | 高性能异步 |
| 持久化 | SQLite（checkpoint） + ChromaDB（向量） | 单机部署 |
| 可观测性 | LangSmith | 官方推荐 |

## 1.4 AI Agent 六大核心组件

```
┌──────────────────────────────────────────────────┐
│                    AI Agent                       │
│                                                  │
│  ┌─────────┐  ┌─────────┐  ┌─────────────────┐  │
│  │ 大模型   │  │ 记忆    │  │ 工具 (Tools)    │  │
│  │ (LLM)   │  │ (Memory) │  │ 搜索/代码/API   │  │
│  └────┬────┘  └────┬────┘  └───────┬─────────┘  │
│       │            │               │            │
│  ┌────┴────┐  ┌────┴────┐  ┌──────┴──────────┐  │
│  │ 规划    │  │ 行动    │  │ 协作           │  │
│  │ReAct    │  │ToolCall │  │ SubAgents       │  │
│  └─────────┘  └─────────┘  └─────────────────┘  │
└──────────────────────────────────────────────────┘
```

---

# 第 2 章 环境搭建

## 2.1 Python 环境

```bash
# 确认 Python 版本（需要 3.10+）
python --version

# 创建虚拟环境
python -m venv venv
source venv/bin/activate   # macOS/Linux
# venv\Scripts\activate    # Windows

# 升级 pip
pip install --upgrade pip
```

## 2.2 安装核心依赖

```bash
# ===== 核心框架 =====
pip install langchain==1.3.0
pip install langgraph==1.2.0
pip install langchain-core==1.4.0

# ===== 模型提供商 =====
pip install langchain-openai      # OpenAI（GPT-4o 等）

# ===== Web 框架 =====
pip install fastapi uvicorn

# ===== 向量数据库 =====
pip install chromadb

# ===== 文档处理 =====
pip install pypdf langchain-text-splitters
pip install tiktoken              # Token 计数

# ===== 搜索 =====
pip install tavily-python

# ===== MCP =====
pip install langchain-mcp-adapters

# ===== 持久化 =====
pip install langgraph-checkpoint-sqlite

# ===== 可观测性 =====
pip install langsmith

# ===== 工具库 =====
pip install python-dotenv httpx
```

## 2.3 环境变量配置

```bash
# .env 文件
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxxxxxx
LANGSMITH_API_KEY=ls_xxxxxxxxxxxxxxxxxxxx

# LangSmith 配置
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=dev-assistant
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
```

```bash
# 验证环境
python -c "
from langchain.agents import create_agent
from langgraph.graph import StateGraph
print('LangChain 环境搭建成功！')
"
```

## 2.4 目录结构初始化

```bash
mkdir -p dev-assistant
cd dev-assistant

# 创建目录
mkdir -p src/{config,models,tools,rag,memory,middleware,agent,api,utils}
mkdir -p data/documents    # RAG 文档
mkdir -p tests
mkdir -p evaluations

# 创建空文件
touch src/__init__.py
touch src/config/__init__.py src/config/settings.py
touch src/models/__init__.py src/models/chat_model.py
touch src/tools/__init__.py src/tools/code_tools.py src/tools/web_tools.py
touch src/rag/__init__.py src/rag/loader.py src/rag/retriever.py
touch src/memory/__init__.py src/memory/checkpointer.py src/memory/store.py
touch src/middleware/__init__.py src/middleware/custom.py
touch src/agent/__init__.py src/agent/assistant.py
touch src/api/__init__.py src/api/server.py src/api/routes.py
touch src/utils/__init__.py src/utils/logger.py
touch src/app.py
```

---

# 第 3 章 项目工程结构

最终的完整项目结构：

```
dev-assistant/
├── .env                          # 环境变量（不提交 Git）
├── .env.example                  # 环境变量模板
├── .gitignore
├── requirements.txt
├── README.md
│
├── data/                         # 数据目录
│   └── documents/                # RAG 原始文档
│       ├── python-guide.md
│       ├── go-best-practices.md
│       └── design-patterns.pdf
│
├── src/                          # 源代码
│   ├── __init__.py
│   │
│   ├── config/                   # 配置层
│   │   ├── __init__.py
│   │   └── settings.py           # 全局配置（加载 .env）
│   │
│   ├── models/                   # 模型层
│   │   ├── __init__.py
│   │   └── chat_model.py         # 模型初始化和 profile
│   │
│   ├── tools/                    # 工具层
│   │   ├── __init__.py
│   │   ├── code_tools.py         # 代码分析工具
│   │   ├── web_tools.py          # 搜索工具
│   │   └── registry.py           # 工具注册中心
│   │
│   ├── rag/                      # RAG 层
│   │   ├── __init__.py
│   │   ├── loader.py             # 文档加载
│   │   ├── splitter.py           # 文档切分
│   │   ├── embedder.py           # 向量嵌入
│   │   └── retriever.py          # 检索器
│   │
│   ├── memory/                   # 记忆层
│   │   ├── __init__.py
│   │   ├── checkpointer.py       # 短期记忆
│   │   └── store.py              # 长期记忆
│   │
│   ├── middleware/               # 中间件层
│   │   ├── __init__.py
│   │   └── custom.py             # 自定义中间件
│   │
│   ├── agent/                    # Agent 层
│   │   ├── __init__.py
│   │   └── assistant.py          # Agent 组装入口
│   │
│   ├── api/                      # API 层
│   │   ├── __init__.py
│   │   ├── server.py             # FastAPI 服务
│   │   ├── routes.py             # 路由定义
│   │   └── schemas.py            # 请求/响应模型
│   │
│   ├── utils/                    # 工具层
│   │   ├── __init__.py
│   │   └── logger.py             # 日志工具
│   │
│   └── app.py                    # 应用入口
│
├── tests/                        # 测试
│   ├── __init__.py
│   ├── test_tools.py
│   ├── test_rag.py
│   └── test_agent.py
│
└── evaluations/                   # 评估
    └── test_dataset.json
```

---

# 第 4 章 配置管理

## 4.1 全局配置

```python
# src/config/settings.py
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env
load_dotenv()

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()

class Settings:
    """全局配置"""

    # ===== 项目 =====
    PROJECT_NAME: str = "DevAssistant"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # ===== OpenAI =====
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    OPENAI_MODEL_MINI: str = os.getenv("OPENAI_MODEL_MINI", "gpt-4o-mini")
    OPENAI_EMBEDDING_MODEL: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

    # ===== 搜索 API =====
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")

    # ===== 向量数据库 =====
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", str(PROJECT_ROOT / "data" / "chroma"))

    # ===== SQLite Checkpointer =====
    SQLITE_DB_PATH: str = os.getenv("SQLITE_DB_PATH", str(PROJECT_ROOT / "data" / "checkpoints.db"))

    # ===== LangSmith =====
    LANGSMITH_API_KEY: str = os.getenv("LANGSMITH_API_KEY", "")
    LANGSMITH_PROJECT: str = os.getenv("LANGSMITH_PROJECT", "dev-assistant")
    LANGSMITH_TRACING: bool = os.getenv("LANGSMITH_TRACING", "true").lower() == "true"

    # ===== Agent =====
    MAX_MODEL_RETRIES: int = int(os.getenv("MAX_MODEL_RETRIES", "3"))
    MAX_TOOL_RETRIES: int = int(os.getenv("MAX_TOOL_RETRIES", "2"))
    SUMMARIZATION_TRIGGER_FRACTION: float = float(os.getenv("SUMMARIZATION_TRIGGER_FRACTION", "0.8"))

    # ===== API =====
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))


# 单例
settings = Settings()
```

```python
# .env.example（提交到 Git，不含真实密钥）
OPENAI_API_KEY=sk-your-key-here
TAVILY_API_KEY=tvly-your-key-here
LANGSMITH_API_KEY=ls-your-key-here
DEBUG=false
```

---

# 第 5 章 模型层封装

## 5.1 模型初始化

```python
# src/models/chat_model.py
import os
from langchain.chat_models import init_chat_model
from src.config.settings import settings

def get_main_model(temperature: float = 0.7):
    """主力模型：用于推理和回答"""
    return init_chat_model(
        model=f"openai:{settings.OPENAI_MODEL}",
        api_key=settings.OPENAI_API_KEY or None,
        temperature=temperature,
        max_tokens=4096,
    )

def get_mini_model(temperature: float = 0.3):
    """轻量模型：用于摘要、路由等辅助任务"""
    return init_chat_model(
        model=f"openai:{settings.OPENAI_MODEL_MINI}",
        api_key=settings.OPENAI_API_KEY or None,
        temperature=temperature,
        max_tokens=2048,
    )

# 使用示例
if __name__ == "__main__":
    model = get_main_model()
    print(f"主力模型: {model.model_name}")
    print(f"最大输入 token: {model.profile.max_input_tokens}")
    print(f"支持结构化输出: {model.profile.supports_structured_output}")
    print(f"支持函数调用: {model.profile.supports_function_calling}")
```

---

# 第 6 章 工具开发

## 6.1 代码分析工具

```python
# src/tools/code_tools.py
import os
import glob
from pathlib import Path
from langchain.tools import tool
from pydantic import BaseModel, Field
from typing import List, Optional


class ReadFileInput(BaseModel):
    """读取文件的参数"""
    filepath: str = Field(description="文件路径（绝对路径或相对路径）")
    start_line: Optional[int] = Field(default=None, description="起始行号（可选，从1开始）")
    end_line: Optional[int] = Field(default=None, description="结束行号（可选，包含此行）")


@tool(args_schema=ReadFileInput)
def read_code_file(filepath: str, start_line: Optional[int] = None, end_line: Optional[int] = None) -> str:
    """读取代码文件内容。支持指定行号范围。

    Args:
        filepath: 文件路径
        start_line: 可选，起始行号
        end_line: 可选，结束行号
    """
    try:
        path = Path(filepath)
        if not path.exists():
            return f"错误：文件不存在 - {filepath}"

        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if start_line is None:
            start_line = 1
        if end_line is None:
            end_line = len(lines)

        selected = lines[start_line - 1:end_line]
        result = "".join(selected)

        if len(result) > 8000:
            result = result[:8000] + "\n\n... (文件过长，已截断)"

        return result

    except Exception as e:
        return f"读取文件失败：{str(e)}"


class ListFilesInput(BaseModel):
    """列出文件的参数"""
    directory: str = Field(description="目录路径")
    pattern: str = Field(default="*", description="文件匹配模式，如 '*.py', '*.go'")


@tool(args_schema=ListFilesInput)
def list_code_files(directory: str, pattern: str = "*") -> str:
    """列出指定目录下的代码文件。支持通配符过滤。

    Args:
        directory: 目录路径
        pattern: 文件匹配模式，如 '*.py'
    """
    try:
        path = Path(directory)
        if not path.exists():
            return f"错误：目录不存在 - {directory}"

        if not path.is_dir():
            return f"错误：不是目录 - {directory}"

        files = list(path.rglob(pattern))
        # 排除常见非代码目录
        exclude_dirs = {"node_modules", "__pycache__", ".git", "venv", ".venv", "dist", "build"}
        files = [f for f in files if not any(ex in f.parts for ex in exclude_dirs)]

        if not files:
            return f"目录 {directory} 中没有匹配 {pattern} 的文件"

        result = []
        for f in sorted(files)[:50]:  # 最多 50 个
            size = f.stat().st_size
            result.append(f"  {f.relative_to(path)}  ({_format_size(size)})")

        return f"找到 {len(result)} 个文件:\n" + "\n".join(result)

    except Exception as e:
        return f"列出文件失败：{str(e)}"


@tool
def count_code_lines(filepath: str) -> str:
    """统计代码文件的行数、注释行数、空行数。

    Args:
        filepath: 文件路径
    """
    try:
        path = Path(filepath)
        if not path.exists():
            return f"错误：文件不存在 - {filepath}"

        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        total = len(lines)
        empty = sum(1 for l in lines if l.strip() == "")
        comment = sum(1 for l in lines if l.strip().startswith(("#", "//", "--")))
        code = total - empty - comment

        return f"""
文件: {path.name}
总行数: {total}
代码行: {code} ({code/total*100:.1f}%)
注释行: {comment} ({comment/total*100:.1f}%)
空行: {empty} ({empty/total*100:.1f}%)
"""

    except Exception as e:
        return f"统计失败：{str(e)}"


def _format_size(size_bytes: int) -> str:
    """格式化文件大小"""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f}TB"
```

## 6.2 网络搜索工具

```python
# src/tools/web_tools.py
from langchain.tools import tool
from pydantic import BaseModel, Field
from typing import Optional

# 如果安装了 tavily
try:
    from tavily import TavilyClient
    from src.config.settings import settings
    _tavily = TavilyClient(api_key=settings.TAVILY_API_KEY) if settings.TAVILY_API_KEY else None
except ImportError:
    _tavily = None


class SearchInput(BaseModel):
    """搜索参数"""
    query: str = Field(description="搜索关键词")
    max_results: int = Field(default=5, description="最大结果数")


@tool(args_schema=SearchInput)
def web_search(query: str, max_results: int = 5) -> str:
    """在互联网上搜索技术文档和编程资料。

    Args:
        query: 搜索关键词
        max_results: 最大返回结果数
    """
    if _tavily is None:
        return "搜索服务未配置（缺少 TAVILY_API_KEY）"

    try:
        response = _tavily.search(
            query=query,
            max_results=max_results,
            search_depth="advanced",
            include_domains=["github.com", "stackoverflow.com", "docs.python.org", "go.dev"],
        )

        if not response.get("results"):
            return f"未找到关于 '{query}' 的相关结果"

        results = []
        for i, result in enumerate(response["results"], 1):
            title = result.get("title", "无标题")
            url = result.get("url", "")
            content = result.get("content", "")[:300]
            results.append(f"{i}. {title}\n   链接: {url}\n   摘要: {content}\n")

        return "\n".join(results)

    except Exception as e:
        return f"搜索失败：{str(e)}"
```

## 6.3 工具注册中心

```python
# src/tools/registry.py
from typing import List
from langchain_core.tools import BaseTool
from src.tools.code_tools import read_code_file, list_code_files, count_code_lines
from src.tools.web_tools import web_search


class ToolRegistry:
    """工具注册中心：统一管理所有工具"""

    _instance = None
    _tools: List[BaseTool] = []

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._register_defaults()
        return cls._instance

    def _register_defaults(self):
        """注册默认工具"""
        self._tools = [
            read_code_file,
            list_code_files,
            count_code_lines,
            web_search,
        ]

    def get_all_tools(self) -> List[BaseTool]:
        """获取所有已注册的工具"""
        return self._tools

    def add_tool(self, tool: BaseTool):
        """动态注册新工具"""
        self._tools.append(tool)

    def get_tool_by_name(self, name: str) -> BaseTool:
        """按名称获取工具"""
        for tool in self._tools:
            if tool.name == name:
                return tool
        raise ValueError(f"工具 '{name}' 未注册")


# 单例
tool_registry = ToolRegistry()
```

---

# 第 7 章 RAG 检索增强生成

## 7.1 文档加载器

```python
# src/rag/loader.py
from pathlib import Path
from typing import List
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    UnstructuredMarkdownLoader,
)
from langchain_core.documents import Document


class DocumentLoader:
    """多格式文档加载器"""

    LOADERS = {
        ".txt": TextLoader,
        ".md": UnstructuredMarkdownLoader,
        ".pdf": PyPDFLoader,
    }

    @classmethod
    def load_directory(cls, directory: str) -> List[Document]:
        """加载目录下所有支持的文档"""
        path = Path(directory)
        all_docs = []

        for file_path in path.rglob("*"):
            if file_path.suffix in cls.LOADERS:
                loader_cls = cls.LOADERS[file_path.suffix]
                try:
                    loader = loader_cls(str(file_path))
                    docs = loader.load()
                    # 添加来源元数据
                    for doc in docs:
                        doc.metadata["source"] = str(file_path.relative_to(path))
                    all_docs.extend(docs)
                    print(f"  ✓ 已加载: {file_path.name}")
                except Exception as e:
                    print(f"  ✗ 加载失败 {file_path.name}: {e}")

        return all_docs

    @classmethod
    def load_file(cls, filepath: str) -> List[Document]:
        """加载单个文件"""
        path = Path(filepath)
        if path.suffix not in cls.LOADERS:
            raise ValueError(f"不支持的文件格式: {path.suffix}")
        loader = cls.LOADERS[path.suffix](str(path))
        return loader.load()
```

## 7.2 文档切分器

```python
# src/rag/splitter.py
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


class DocumentSplitter:
    """智能文档切分"""

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: List[str] = None,
    ):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators or [
                "\n\n",     # 段落
                "\n",       # 行
                ". ",       # 句子
                " ",        # 单词
                "",         # 字符
            ],
            length_function=len,
        )

    def split(self, documents: List[Document]) -> List[Document]:
        """切分文档"""
        chunks = self.splitter.split_documents(documents)
        print(f"  ✓ 切分完成: {len(documents)} 个文档 → {len(chunks)} 个片段")
        return chunks
```

## 7.3 向量嵌入与检索器

```python
# src/rag/embedder.py
from langchain_openai import OpenAIEmbeddings
from src.config.settings import settings


def get_embeddings():
    """获取嵌入模型"""
    return OpenAIEmbeddings(
        model=settings.OPENAI_EMBEDDING_MODEL,
        api_key=settings.OPENAI_API_KEY or None,
    )
```

```python
# src/rag/retriever.py
from typing import List, Optional
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from src.rag.loader import DocumentLoader
from src.rag.splitter import DocumentSplitter
from src.rag.embedder import get_embeddings
from src.config.settings import settings


class RAGRetriever:
    """RAG 检索器：加载 → 切分 → 嵌入 → 检索"""

    def __init__(self):
        self.embeddings = get_embeddings()
        self.vector_store: Optional[Chroma] = None

    def build_index(self, documents_dir: str = None, force_rebuild: bool = False):
        """构建向量索引"""
        if documents_dir is None:
            from src.config.settings import PROJECT_ROOT
            documents_dir = str(PROJECT_ROOT / "data" / "documents")

        print(f"\n>>> 构建 RAG 索引: {documents_dir}")

        # 1. 加载文档
        print("1. 加载文档...")
        docs = DocumentLoader.load_directory(documents_dir)
        if not docs:
            print("  ⚠ 未找到任何文档，跳过索引构建")
            return
        print(f"  总计: {len(docs)} 个文档")

        # 2. 切分
        print("2. 切分文档...")
        splitter = DocumentSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split(docs)

        # 3. 构建向量存储
        print("3. 构建向量索引...")
        self.vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=settings.CHROMA_PERSIST_DIR,
            collection_name="dev_docs",
        )
        print(f"  ✓ 索引构建完成，存储于: {settings.CHROMA_PERSIST_DIR}")

    def load_index(self):
        """加载已有索引"""
        import os
        if os.path.exists(settings.CHROMA_PERSIST_DIR):
            self.vector_store = Chroma(
                persist_directory=settings.CHROMA_PERSIST_DIR,
                embedding_function=self.embeddings,
                collection_name="dev_docs",
            )
            print(f"  ✓ 已加载索引: {self.vector_store._collection.count()} 个向量")
            return True
        return False

    def as_retriever(self, k: int = 5) -> BaseRetriever:
        """返回 LangChain 检索器"""
        if self.vector_store is None:
            raise RuntimeError("请先调用 build_index() 或 load_index()")
        return self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k},
        )

    def search(self, query: str, k: int = 5) -> List[Document]:
        """搜索相关文档"""
        if self.vector_store is None:
            raise RuntimeError("请先调用 build_index() 或 load_index()")
        return self.vector_store.similarity_search(query, k=k)


# 单例
rag_retriever = RAGRetriever()
```

## 7.4 创建 RAG 工具

```python
# 将检索器包装为 Agent 可用的工具
from langchain.tools import tool
from src.rag.retriever import rag_retriever


@tool
def search_knowledge_base(query: str) -> str:
    """在编程知识库中搜索答案。用于查找编程语言用法、最佳实践、设计模式等技术内容。

    Args:
        query: 搜索关键词或问题，如 'Python 装饰器的用法'、'Go的错误处理最佳实践'
    """
    try:
        docs = rag_retriever.search(query, k=4)

        if not docs:
            return f"知识库中未找到关于 '{query}' 的相关内容"

        results = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "未知来源")
            content = doc.page_content[:500]
            results.append(f"[{i}] 来源: {source}\n{content}\n")

        return "\n".join(results)

    except Exception as e:
        return f"知识库搜索失败：{str(e)}"
```

---

# 第 8 章 记忆系统

## 8.1 短期记忆（Checkpointer）

```python
# src/memory/checkpointer.py
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.memory import MemorySaver
from src.config.settings import settings


def get_checkpointer():
    """获取 Checkpointer"""
    if settings.DEBUG:
        # 开发环境：内存（重启丢失）
        return MemorySaver()
    else:
        # 生产环境：SQLite 持久化
        return SqliteSaver.from_conn_string(settings.SQLITE_DB_PATH)


# 使用示例
# checkpointer = get_checkpointer()
# config = {"configurable": {"thread_id": "user-001"}}
```

## 8.2 长期记忆（Store）

```python
# src/memory/store.py
from langgraph.store.memory import InMemoryStore
from typing import Optional, Dict, Any


class UserMemoryStore:
    """基于 LangGraph Store 的长期记忆管理"""

    def __init__(self):
        self.store = InMemoryStore()

    def save_user_preference(self, user_id: str, key: str, value: Any):
        """保存用户偏好"""
        self.store.put(
            ["users", user_id, "preferences", key],
            value,
        )

    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """获取用户所有偏好"""
        results = self.store.search(["users", user_id, "preferences"])
        return {item.key.split("/")[-1]: item.value for item in results}

    def save_conversation_summary(self, user_id: str, thread_id: str, summary: str):
        """保存对话摘要（用于跨会话记忆）"""
        import time
        self.store.put(
            ["users", user_id, "conversations", thread_id],
            {
                "summary": summary,
                "timestamp": time.time(),
            },
        )

    def get_recent_conversations(self, user_id: str, limit: int = 5):
        """获取最近的对话摘要"""
        items = self.store.search(["users", user_id, "conversations"])
        items.sort(key=lambda x: x.value.get("timestamp", 0), reverse=True)
        return items[:limit]


# 单例
user_memory = UserMemoryStore()
```

---

# 第 9 章 中间件体系

## 9.1 用户偏好注入中间件

```python
# src/middleware/custom.py
from langchain.agents.middleware import AgentMiddleware
from langchain.agents.middleware.types import AgentState
from langchain_core.messages import SystemMessage
from src.memory.store import user_memory


class UserPreferenceMiddleware(AgentMiddleware):
    """将用户偏好注入到系统消息中"""

    def __init__(self, user_id: str):
        super().__init__()
        self.user_id = user_id

    def before_agent(self, state: AgentState, runtime) -> dict | None:
        prefs = user_memory.get_user_preferences(self.user_id)

        if prefs:
            pref_lines = ["\n用户偏好设置："]
            for k, v in prefs.items():
                pref_lines.append(f"- {k}: {v}")

            # 在消息列表开头添加偏好信息
            pref_msg = SystemMessage(content="\n".join(pref_lines))
            state["messages"].insert(0, pref_msg)

        return None  # 不修改状态，继续执行
```

## 9.2 性能监控中间件

```python
import time
import logging
from langchain.agents.middleware import AgentMiddleware
from langchain.agents.middleware.types import AgentState

logger = logging.getLogger(__name__)


class PerformanceMonitorMiddleware(AgentMiddleware):
    """记录每次模型调用和工具调用的耗时"""

    def __init__(self):
        super().__init__()
        self.model_calls = []
        self.tool_calls = []

    async def wrap_model_call(self, request, handler):
        start = time.time()
        response = await handler(request)
        elapsed = time.time() - start

        self.model_calls.append({
            "model": request.model_name,
            "time": elapsed,
            "tokens": getattr(response, "usage_metadata", {}),
        })

        logger.info(f"模型调用: {request.model_name}, 耗时: {elapsed:.2f}s")

        return response

    async def wrap_tool_call(self, request, handler):
        start = time.time()
        response = await handler(request)
        elapsed = time.time() - start

        self.tool_calls.append({
            "tool": request.tool_call.get("name", "unknown"),
            "time": elapsed,
        })

        logger.info(f"工具调用: {request.tool_call.get('name')}, 耗时: {elapsed:.2f}s")

        return response

    def after_agent(self, state: AgentState, runtime) -> dict | None:
        total_model_time = sum(c["time"] for c in self.model_calls)
        total_tool_time = sum(c["time"] for c in self.tool_calls)

        logger.info(
            f"Agent 执行完毕: "
            f"模型调用 {len(self.model_calls)} 次 ({total_model_time:.2f}s), "
            f"工具调用 {len(self.tool_calls)} 次 ({total_tool_time:.2f}s)"
        )
        return None
```

---

# 第 10 章 Agent 组装

这是整个项目的核心——把所有组件组装成一个完整的 Agent。

```python
# src/agent/assistant.py
from typing import Optional, AsyncIterator, Dict, Any
from langchain.agents import create_agent
from langchain.agents.middleware import (
    SummarizationMiddleware,
    ModelRetryMiddleware,
)
from langchain_core.messages import HumanMessage

from src.config.settings import settings
from src.models.chat_model import get_main_model, get_mini_model
from src.tools.registry import tool_registry
from src.tools.rag_tool import search_knowledge_base
from src.memory.checkpointer import get_checkpointer
from src.memory.store import user_memory
from src.middleware.custom import UserPreferenceMiddleware
from src.rag.retriever import rag_retriever


class DevAssistantAgent:
    """AI 编程助手 Agent"""

    def __init__(self):
        self.agent = None
        self._initialized = False

    async def initialize(self):
        """初始化 Agent（异步加载向量索引等）"""
        if self._initialized:
            return

        print("\n>>> 初始化 DevAssistant Agent...")

        # 1. 准备 RAG 检索器
        print("1. 加载知识库索引...")
        if not rag_retriever.load_index():
            print("  索引不存在，正在构建...")
            rag_retriever.build_index()

        # 2. 注册 RAG 工具
        tool_registry.add_tool(search_knowledge_base)

        # 3. 获取所有工具
        tools = tool_registry.get_all_tools()
        print(f"2. 已注册 {len(tools)} 个工具:")
        for tool in tools:
            print(f"   - {tool.name}: {tool.description[:50]}...")

        # 4. 组装 Agent
        print("3. 组装 Agent...")
        self.agent = create_agent(
            # ===== 模型 =====
            model=get_main_model(temperature=0.7),

            # ===== 工具 =====
            tools=tools,

            # ===== 系统提示 =====
            system_prompt="""你是 DevAssistant，一个专业的 AI 编程助手。你的职责是：

1. **回答编程问题**：优先使用知识库搜索（search_knowledge_base）查找答案
2. **分析代码**：使用 read_code_file 读取代码并给出分析和建议
3. **搜索技术资料**：使用 web_search 查找最新的技术文档
4. **项目导航**：使用 list_code_files 了解项目结构

工作原则：
- 用中文回答，代码示例保持英文
- 回答包含可运行的代码示例
- 不确定时先搜索知识库，不要猜测
- 代码审查时按：bug > 性能 > 安全 > 可维护性 的优先级
- 每个建议都要说明原因""",

            # ===== 中间件 =====
            middleware=[
                SummarizationMiddleware(
                    model=get_mini_model(),
                    trigger={"fraction": settings.SUMMARIZATION_TRIGGER_FRACTION},
                    keep={"messages": 15},
                ),
                ModelRetryMiddleware(
                    max_retries=settings.MAX_MODEL_RETRIES,
                    backoff_factor=2.0,
                    initial_delay=1.0,
                ),
            ],

            # ===== 持久化 =====
            checkpointer=get_checkpointer(),

            # ===== 配置 =====
            name="dev_assistant",
            debug=settings.DEBUG,
        )

        self._initialized = True
        print("  ✓ Agent 初始化完成\n")

    async def chat(
        self,
        message: str,
        thread_id: str = "default",
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """同步对话"""
        await self.initialize()

        config = {"configurable": {"thread_id": thread_id}}

        # 如果有用户偏好，临时添加偏好中间件
        middleware = []
        if user_id:
            middleware.append(UserPreferenceMiddleware(user_id))

        result = await self.agent.ainvoke(
            {"messages": [{"role": "user", "content": message}]},
            config,
        )

        # 提取回复
        response = result["messages"][-1]
        return {
            "content": response.content,
            "thread_id": thread_id,
            "message_count": len(result["messages"]),
        }

    async def chat_stream(
        self,
        message: str,
        thread_id: str = "default",
    ) -> AsyncIterator[str]:
        """流式对话"""
        await self.initialize()

        config = {"configurable": {"thread_id": thread_id}}

        async for event in self.agent.astream_events(
            {"messages": [{"role": "user", "content": message}]},
            config,
            version="v2",
        ):
            kind = event["event"]

            # 逐 token 输出
            if kind == "on_chat_model_stream":
                content = event["data"]["chunk"].content
                if content:
                    yield content

            # 工具调用事件
            elif kind == "on_tool_start":
                yield f"\n\n🔧 **[调用工具: {event['name']}]**\n"

            elif kind == "on_tool_end":
                output = str(event["data"]["output"])[:200]
                yield f"\n📋 **[工具返回: {output}...]**\n\n"


# 全局单例
assistant = DevAssistantAgent()
```

---

# 第 11 章 MCP 工具集成

## 11.1 MCP 客户端

```python
# src/tools/mcp_tools.py
"""
MCP (Model Context Protocol) 工具集成

MCP 是一种标准化的工具协议，让 LangChain Agent 可以
无缝使用外部 MCP 服务器提供的工具。
"""
from langchain_mcp_adapters.client import MultiServerMCPClient
from typing import List
from langchain_core.tools import BaseTool


class MCPToolManager:
    """MCP 工具管理器"""

    def __init__(self):
        self.client = None
        self._tools: List[BaseTool] = []

    async def connect_stdio_server(self, name: str, command: str, args: List[str]):
        """连接 stdio 模式的 MCP 服务器"""
        if self.client is None:
            self.client = MultiServerMCPClient({})

        await self.client.connect_to_server(
            name,
            {
                "transport": "stdio",
                "command": command,
                "args": args,
            },
        )

    async def connect_http_server(self, name: str, url: str):
        """连接 HTTP 模式的 MCP 服务器"""
        if self.client is None:
            self.client = MultiServerMCPClient({})

        await self.client.connect_to_server(
            name,
            {
                "transport": "streamable_http",
                "url": url,
            },
        )

    async def load_tools(self) -> List[BaseTool]:
        """加载所有 MCP 服务器的工具"""
        if self.client:
            self._tools = await self.client.get_tools()
        return self._tools

    async def close(self):
        """关闭所有连接"""
        if self.client:
            await self.client.close()


# 使用示例
"""
# 连接数学计算 MCP 服务器
mcp_manager = MCPToolManager()
await mcp_manager.connect_stdio_server(
    name="math",
    command="python",
    args=["math_server.py"],
)
mcp_tools = await mcp_manager.load_tools()
"""
```

---

# 第 12 章 流式输出与 API 服务

## 12.1 请求/响应模型

```python
# src/api/schemas.py
from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    """对话请求"""
    message: str = Field(description="用户消息")
    thread_id: str = Field(default="default", description="会话 ID（用于多轮对话）")
    user_id: Optional[str] = Field(default=None, description="用户 ID（用于个性化）")


class ChatResponse(BaseModel):
    """对话响应"""
    content: str = Field(description="回复内容")
    thread_id: str = Field(description="会话 ID")
    message_count: int = Field(description="当前会话消息数")


class HealthResponse(BaseModel):
    """健康检查"""
    status: str
    version: str
    tools_count: int
```

## 12.2 FastAPI 服务

```python
# src/api/routes.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from src.api.schemas import ChatRequest, ChatResponse, HealthResponse
from src.agent.assistant import assistant
from src.config.settings import settings
from src.tools.registry import tool_registry

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    return HealthResponse(
        status="ok",
        version=settings.VERSION,
        tools_count=len(tool_registry.get_all_tools()),
    )

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """同步对话"""
    try:
        result = await assistant.chat(
            message=request.message,
            thread_id=request.thread_id,
            user_id=request.user_id,
        )
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """流式对话"""
    async def generate():
        try:
            async for chunk in assistant.chat_stream(
                message=request.message,
                thread_id=request.thread_id,
            ):
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
```

## 12.3 应用入口

```python
# src/api/server.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.api.routes import router
from src.agent.assistant import assistant
from src.config.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期事件"""
    # 启动时
    print(f"\n{'='*50}")
    print(f"  {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"  API: http://{settings.API_HOST}:{settings.API_PORT}")
    print(f"  Docs: http://{settings.API_HOST}:{settings.API_PORT}/docs")
    print(f"{'='*50}\n")

    await assistant.initialize()

    yield

    # 关闭时
    print("\n  shutting down...\n")


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="AI 编程助手 Agent - 基于 LangChain v1.3",
        lifespan=lifespan,
    )

    # CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由
    app.include_router(router, prefix="/api/v1")

    return app


app = create_app()
```

```python
# src/app.py
import uvicorn
from src.api.server import app
from src.config.settings import settings

if __name__ == "__main__":
    uvicorn.run(
        "src.api.server:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
    )
```

## 12.4 启动与调用

```bash
# 启动服务
python -m src.app

# 测试健康检查
curl http://localhost:8000/api/v1/health

# 同步对话
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "帮我解释一下 Python 装饰器的原理",
    "thread_id": "user-001"
  }'

# 流式对话
curl -X POST http://localhost:8000/api/v1/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "分析一下 src/tools/code_tools.py 这个文件的代码质量",
    "thread_id": "user-001"
  }'
```

---

# 第 13 章 测试与评估

## 13.1 工具单元测试

```python
# tests/test_tools.py
import pytest
from src.tools.code_tools import read_code_file, list_code_files


def test_read_code_file_exists():
    """测试读取存在的文件"""
    result = read_code_file.invoke({"filepath": "src/tools/code_tools.py"})
    assert "错误" not in result
    assert len(result) > 0


def test_read_code_file_not_exists():
    """测试读取不存在的文件"""
    result = read_code_file.invoke({"filepath": "/nonexistent/file.py"})
    assert "错误" in result


def test_list_code_files():
    """测试列出文件"""
    result = list_code_files.invoke({"directory": "src", "pattern": "*.py"})
    assert "错误" not in result
    assert ".py" in result
```

## 13.2 Agent 集成测试

```python
# tests/test_agent.py
import pytest
import asyncio
from src.agent.assistant import assistant


@pytest.mark.asyncio
async def test_agent_basic_chat():
    """测试 Agent 基本对话"""
    await assistant.initialize()

    result = await assistant.chat(
        message="你好，请用一句话介绍自己",
        thread_id="test-basic-001",
    )

    assert result["content"]
    assert result["thread_id"] == "test-basic-001"
    assert result["message_count"] > 0


@pytest.mark.asyncio
async def test_agent_multi_turn():
    """测试多轮对话"""
    await assistant.initialize()
    thread_id = "test-multi-001"

    # 第一轮：告诉 Agent 偏好
    await assistant.chat(
        message="我偏好使用 TypeScript",
        thread_id=thread_id,
        user_id="test-user",
    )

    # 第二轮：Agent 应记住偏好
    result = await assistant.chat(
        message="推荐一个 Web 框架",
        thread_id=thread_id,
        user_id="test-user",
    )

    assert result["content"]
    assert result["message_count"] > 2  # 累积消息
```

## 13.3 评估数据集

```json
[
    {
        "query": "Python 中如何处理文件？",
        "expected_tools": ["search_knowledge_base"],
        "expected_keywords": ["open", "with", "read", "write"]
    },
    {
        "query": "分析 src/main.py 的代码",
        "expected_tools": ["read_code_file"],
        "expected_keywords": ["代码", "建议"]
    },
    {
        "query": "Go 语言的错误处理最佳实践是什么？",
        "expected_tools": ["search_knowledge_base"],
        "expected_keywords": ["error", "if err", "fmt.Errorf"]
    }
]
```

```python
# evaluations/evaluate.py
"""Agent 评估脚本"""
import json
import time
from src.agent.assistant import assistant


async def run_evaluation(test_dataset_path: str):
    """运行评估"""
    with open(test_dataset_path) as f:
        test_cases = json.load(f)

    results = []
    for i, case in enumerate(test_cases):
        print(f"\n评估 [{i+1}/{len(test_cases)}]: {case['query'][:50]}...")

        start = time.time()
        result = await assistant.chat(
            message=case["query"],
            thread_id=f"eval-{i}",
        )
        elapsed = time.time() - start

        # 检查关键词
        content_lower = result["content"].lower()
        keyword_hits = [
            kw for kw in case["expected_keywords"]
            if kw.lower() in content_lower
        ]

        score = len(keyword_hits) / len(case["expected_keywords"])
        results.append({
            "query": case["query"],
            "score": score,
            "keyword_hits": keyword_hits,
            "time": elapsed,
        })

        print(f"  得分: {score:.0%}, 命中关键词: {keyword_hits}, 耗时: {elapsed:.2f}s")

    # 汇总
    avg_score = sum(r["score"] for r in results) / len(results)
    avg_time = sum(r["time"] for r in results) / len(results)
    print(f"\n{'='*50}")
    print(f"评估完成: {len(results)} 个用例")
    print(f"平均得分: {avg_score:.1%}")
    print(f"平均耗时: {avg_time:.2f}s")
    print(f"{'='*50}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_evaluation("evaluations/test_dataset.json"))
```

---

# 第 14 章 生产部署

## 14.1 Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制源代码
COPY src/ src/
COPY data/ data/

# 创建非 root 用户
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# 暴露端口
EXPOSE 8000

# 启动
CMD ["python", "-m", "src.app"]
```

## 14.2 docker-compose.yml

```yaml
version: "3.8"

services:
  dev-assistant:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - TAVILY_API_KEY=${TAVILY_API_KEY}
      - LANGSMITH_API_KEY=${LANGSMITH_API_KEY}
      - DEBUG=false
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## 14.3 生产 Checklist

| 类别 | 检查项 | 说明 |
|------|--------|------|
| 安全 | API Key 不硬编码 | 用环境变量或密钥管理服务 |
| 安全 | 输出内容审核 | 添加 PIIMiddleware 过滤敏感信息 |
| 安全 | RBAC 权限控制 | 不同用户不同工具权限 |
| 安全 | 请求频率限制 | 防止滥用（可用 FastAPI middleware） |
| 可靠性 | 熔断降级 | 主模型故障时自动切换 |
| 可靠性 | 指数退避重试 | ModelRetryMiddleware |
| 可靠性 | 健康检查 | /health 端点 |
| 性能 | 嵌入缓存 | 缓存高频搜索结果 |
| 性能 | 连接池 | 数据库和 HTTP 客户端连接池 |
| 性能 | 异步 | 全链路 async |
| 可观测性 | LangSmith | 全链路追踪 |
| 可观测性 | 结构化日志 | JSON 格式日志，方便 ELK 采集 |
| 可观测性 | 关键指标 | 响应时间、成功率、Token 消耗 |
| 运维 | Docker 部署 | 容器化，资源隔离 |
| 运维 | 优雅关闭 | 处理 SIGTERM 信号 |

---

# 第 15 章 可观测性

## 15.1 LangSmith 集成

```python
# 设置环境变量即可自动集成
# LANGSMITH_API_KEY=ls_...
# LANGSMITH_TRACING=true
# LANGSMITH_PROJECT=dev-assistant

# LangSmith 会自动追踪：
# - 每次 Agent 调用
# - 每次 LLM 调用（输入/输出/耗时/token）
# - 每次工具调用
# - Agent 执行轨迹图
```

## 15.2 自定义日志

```python
# src/utils/logger.py
import logging
import json
import sys
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """JSON 格式日志（方便 Log 采集）"""

    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info and record.exc_info[0]:
            log_entry["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "extra_data"):
            log_entry.update(record.extra_data)

        return json.dumps(log_entry, ensure_ascii=False)


def setup_logger(name: str = "dev-assistant", level: str = "INFO"):
    """设置 Logger"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level))

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)

    return logger


logger = setup_logger()
```

---

# 第 16 章 完整项目代码汇总

## 启动流程

```bash
# 1. 克隆/创建项目
cd dev-assistant

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 填入真实密钥

# 5. 准备知识库文档
# 将 Markdown/PDF 文件放入 data/documents/

# 6. 构建 RAG 索引
python -c "
import asyncio
from src.rag.retriever import rag_retriever
rag_retriever.build_index()
"

# 7. 运行测试
pytest tests/ -v

# 8. 启动服务
python -m src.app

# 9. 打开 API 文档
# http://localhost:8000/docs
```

## requirements.txt

```
langchain==1.3.0
langgraph==1.2.0
langchain-core==1.4.0
langchain-openai>=0.3.0
langchain-community>=0.3.0
langchain-text-splitters>=0.3.0
langchain-chroma>=0.2.0
langchain-mcp-adapters>=0.2.0
langgraph-checkpoint-sqlite>=2.0.0
fastapi>=0.115.0
uvicorn[standard]>=0.32.0
pydantic>=2.0.0
python-dotenv>=1.0.0
tiktoken>=0.8.0
chromadb>=0.5.0
tavily-python>=0.5.0
langsmith>=0.3.0
httpx>=0.28.0
pypdf>=5.0.0
pytest>=8.0.0
pytest-asyncio>=0.24.0
```

## .gitignore

```
# 环境
venv/
.env
__pycache__/
*.pyc
.idea/
.vscode/

# 数据
data/chroma/
data/checkpoints.db
logs/

# 系统
.DS_Store
*.egg-info/
dist/
build/
```

---

## 架构总览图

```
┌─────────────────────────────────────────────────────────────┐
│                       API 服务层                            │
│   FastAPI (routes.py) → /chat, /chat/stream, /health       │
├─────────────────────────────────────────────────────────────┤
│                      Agent 核心层                           │
│   create_agent → model + tools + middleware + checkpointer  │
├──────────────┬──────────────┬──────────────┬───────────────┤
│   工具层      │   RAG 层     │   记忆层     │   中间件层    │
│ code_tools   │ loader       │ checkpointer │ summarization │
│ web_tools    │ splitter     │ store        │ retry         │
│ MCP tools    │ retriever    │              │ preference    │
├──────────────┴──────────────┴──────────────┴───────────────┤
│                      模型抽象层                             │
│   init_chat_model → model.profile (自描述能力)              │
├─────────────────────────────────────────────────────────────┤
│                      基础设施层                             │
│   ChromaDB (向量)  SQLite (checkpoint)  Tavily (搜索)      │
└─────────────────────────────────────────────────────────────┘
```

---

> **本指南覆盖了使用 LangChain v1.3 从零构建 AI Agent 的全流程：环境搭建 → 工程结构 → 模型封装 → 工具开发 → RAG 检索 → 记忆系统 → 中间件 → Agent 组装 → MCP 集成 → API 服务 → 测试评估 → 生产部署。所有代码可直接运行，基于 2026 年 5 月最新版 LangChain v1.3。**

> 来源：
> - [LangChain 官方文档](https://docs.langchain.com/oss/python/overview)
> - [LangGraph 官方文档](https://docs.langchain.com/oss/python/langgraph)
> - [Deep Agents GitHub](https://github.com/langchain-ai/deepagents)
> - [MCP 协议规范](https://modelcontextprotocol.io)
