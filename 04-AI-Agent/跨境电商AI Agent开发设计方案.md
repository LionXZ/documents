# 跨境电商 AI Agent 开发设计方案

> 全流程智能化：自动选品 → 内容优化 → 一键上架 → 运营监控 → 数据统计 → 策略建议

---

## 目录

- [第 1 章 项目概述](#第-1-章-项目概述)
- [第 2 章 技术架构](#第-2-章-技术架构)
- [第 3 章 数据层设计](#第-3-章-数据层设计)
- [第 4 章 AI Agent 体系设计](#第-4-章-ai-agent-体系设计)
- [第 5 章 选品 Agent](#第-5-章-选品-agent)
- [第 6 章 优化 Agent](#第-6-章-优化-agent)
- [第 7 章 上架 Agent](#第-7-章-上架-agent)
- [第 8 章 监控 Agent](#第-8-章-监控-agent)
- [第 9 章 统计 Agent](#第-9-章-统计-agent)
- [第 10 章 策略 Agent](#第-10-章-策略-agent)
- [第 11 章 平台集成层（MCP）](#第-11-章-平台集成层mcp)
- [第 12 章 总控编排 Agent](#第-12-章-总控编排-agent)
- [第 13 章 前端仪表盘](#第-13-章-前端仪表盘)
- [第 14 章 部署与运维](#第-14-章-部署与运维)
- **第 15 章 项目路线图](#第-15-章-项目路线图)
- [第 16 章 可行度分析与新手方案](#第-16-章-可行度分析与新手方案)

---

# 第 1 章 项目概述

## 1.1 业务背景

跨境电商卖家面临的核心痛点：

| 痛点 | 现状 | AI 解决方案 |
|------|------|------------|
| 选品难 | 人工刷平台、跟卖、凭经验 | 多源数据聚合 + 趋势预测模型 |
| 优化慢 | 翻译不地道、关键词靠猜 | LLM 生成本地化标题/描述 |
| 上架繁 | 多平台重复填写 | API 自动上架 + 模板映射 |
| 监控累 | 多店铺切换查看 | 统一仪表盘 + 异常告警 |
| 分析弱 | Excel 手动统计 | 自动报表 + AI 解读 |
| 决策盲 | 凭感觉调整策略 | 数据驱动建议 + A/B 实验 |

## 1.2 系统目标

构建一个覆盖**全链路**的 AI Agent 系统：

```
┌──────────────────────────────────────────────────────────┐
│                    跨境AI运营大脑                          │
│                                                          │
│  选品 ──→ 优化 ──→ 上架 ──→ 监控 ──→ 统计 ──→ 建议      │
│   ↑                                                    │
│   └──────────── 数据反馈闭环 ──────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

## 1.3 支持平台

| 平台 | 站点 | 优先级 |
|------|------|--------|
| TikTok Shop | 泰国、越南、菲律宾、马来西亚、印尼、英国、美国 | P0 |
| Shopee | 泰国、巴西、菲律宾、越南、马来西亚 | P0 |
| Lazada | 泰国、菲律宾 | P1 |
| Amazon | 美国 | P2 |

---

# 第 2 章 技术架构

## 2.1 整体架构图

```
┌──────────────────────────────────────────────────────────────────┐
│                         前端仪表盘 (Vite + React SPA)              │
│         选品看板 │ 商品管理 │ 运营监控 │ 数据报表 │ AI助手         │
├──────────────────────────────────────────────────────────────────┤
│                         API 网关 (Kong / Nginx)                   │
├──────────────────────────────────────────────────────────────────┤
│                     后端服务层 (FastAPI 微服务)                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │ 选品服务  │ │ 商品服务  │ │ 上架服务  │ │ 数据服务  │           │
│  │ Product  │ │ Content  │ │ Listing  │ │Analytics │           │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘           │
├───────┼────────────┼────────────┼────────────┼──────────────────┤
│       │            │            │            │                   │
│  ┌────┴────────────┴────────────┴────────────┴─────┐            │
│  │              AI Agent 编排层 (LangGraph)          │            │
│  │                                                  │            │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐   │            │
│  │  │选品    │ │优化    │ │上架    │ │监控    │   │            │
│  │  │Agent   │ │Agent   │ │Agent   │ │Agent   │   │            │
│  │  └───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘   │            │
│  │  ┌───┴────┐ ┌───┴────┐     │     ┌───┴────┐   │            │
│  │  │统计    │ │策略    │     │     │总控编排 │   │            │
│  │  │Agent   │ │Agent   │◄────┘     │Orch    │   │            │
│  │  └────────┘ └────────┘           └────────┘   │            │
│  └──────────────────────┬───────────────────────┘            │
├─────────────────────────┼────────────────────────────────────┤
│                         │                                     │
│  ┌──────────────────────┴───────────────────────┐            │
│  │          MCP 工具层 (平台 API 封装)            │            │
│  │  TikTokShopTool │ ShopeeTool │ WebSearchTool  │            │
│  └──────────────────────┬───────────────────────┘            │
├─────────────────────────┼────────────────────────────────────┤
│                         │                                     │
│  ┌──────────┐  ┌────────┴─────┐  ┌──────────┐               │
│  │PostgreSQL│  │    Redis     │  │ ChromaDB  │               │
│  │ 业务数据  │  │  缓存/队列    │  │ 向量检索   │               │
│  └──────────┘  └──────────────┘  └──────────┘               │
│                                                              │
│  ┌──────────┐  ┌──────────────┐  ┌──────────┐               │
│  │RabbitMQ  │  │   MinIO/S3   │  │ LangSmith │               │
│  │ 异步任务  │  │  图片/文件    │  │  可观测性  │               │
│  └──────────┘  └──────────────┘  └──────────┘               │
└──────────────────────────────────────────────────────────────────┘
```

## 2.2 技术栈明细

| 层级 | 技术 | 版本 | 说明 |
|------|------|------|------|
| **Agent 框架** | LangChain | 1.3+ | Agent 编排 |
| **状态引擎** | LangGraph | 1.2+ | 工作流状态管理 |
| **后端** | Python FastAPI | 0.115+ | 高性能异步 API |
| **前端** | Vite + React 19 | 19+ | SPA 管理后台（内部工具，无需SSR） |
| **数据库** | PostgreSQL | 16+ | 业务数据 |
| **缓存** | Redis | 7+ | 热数据 + 限流 |
| **向量库** | ChromaDB | 0.5+ | 商品相似度检索 |
| **消息队列** | RabbitMQ | 3.13+ | 异步任务调度 |
| **对象存储** | MinIO / S3 | - | 商品图片 |
| **LLM** | GPT-4o + GPT-4o-mini | - | OpenAI API |
| **可观测性** | LangSmith | - | Agent 追踪 |
| **容器** | Docker + K8s | - | 部署编排 |
| **CI/CD** | GitHub Actions | - | 自动部署 |

## 2.3 服务划分

```
services/
├── api-gateway/          # API 网关（Kong/Nginx）
├── product-service/      # 选品服务
│   ├── api/              # REST API
│   ├── agent/            # 选品 Agent
│   ├── crawler/          # 数据采集
│   └── models/           # 数据模型
├── content-service/      # 内容优化服务
│   ├── api/
│   ├── agent/            # 优化 Agent
│   └── templates/        # 文案模板
├── listing-service/      # 上架服务
│   ├── api/
│   ├── agent/            # 上架 Agent
│   ├── adapters/         # 平台适配器
│   └── scheduler/        # 定时上架
├── monitoring-service/   # 监控服务
│   ├── api/
│   ├── agent/            # 监控 Agent
│   └── alerting/         # 告警规则
├── analytics-service/    # 分析服务
│   ├── api/
│   ├── agent/            # 统计 + 策略 Agent
│   └── reports/          # 报表模板
├── orchestration-service/# 编排服务
│   ├── agent/            # 总控编排 Agent
│   └── workflows/        # 工作流定义
├── mcp-service/          # MCP 工具服务
│   ├── tiktok/           # TikTok Shop 工具
│   ├── shopee/           # Shopee 工具
│   └── common/           # 通用工具（搜索、翻译等）
└── shared/               # 共享库
    ├── models/           # 公共数据模型
    ├── utils/            # 工具函数
    └── config/           # 全局配置
```

---

# 第 3 章 数据层设计

## 3.1 核心表结构

### 3.1.1 商品数据

```sql
-- 商品主表
CREATE TABLE products (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    external_id     VARCHAR(100),               -- 平台商品ID
    platform        VARCHAR(20) NOT NULL,       -- tiktok_shop, shopee, lazada
    site            VARCHAR(10) NOT NULL,       -- TH, VN, PH, BR, US
    shop_id         UUID REFERENCES shops(id),

    -- 基础信息
    title           VARCHAR(500) NOT NULL,
    description     TEXT,
    category_id     UUID REFERENCES categories(id),
    brand           VARCHAR(200),
    price           DECIMAL(12,2),
    currency        VARCHAR(3) DEFAULT 'THB',
    stock           INT DEFAULT 0,

    -- 媒体
    main_image      VARCHAR(500),
    images          JSONB DEFAULT '[]',         -- ["url1", "url2"]
    video_url       VARCHAR(500),

    -- SKU
    skus            JSONB DEFAULT '[]',         -- [{sku, price, stock, attrs}]

    -- 状态
    status          VARCHAR(20) DEFAULT 'draft', -- draft, active, paused, deleted
    listing_time    TIMESTAMPTZ,
    source          VARCHAR(20) DEFAULT 'manual', -- manual, ai, crawler

    -- 优化记录
    optimization_log JSONB DEFAULT '[]',        -- [{time, field, old, new, source}]

    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_products_platform ON products(platform, site);
CREATE INDEX idx_products_status ON products(status, shop_id);
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_created ON products(created_at DESC);
```

```sql
-- 选品池表（待分析商品）
CREATE TABLE product_pool (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source          VARCHAR(50) NOT NULL,        -- crawler, manual, supplier_api
    source_url      VARCHAR(1000),
    platform        VARCHAR(20),
    site            VARCHAR(10),

    title           VARCHAR(500),
    description     TEXT,
    price           DECIMAL(12,2),
    images          JSONB DEFAULT '[]',

    -- AI 分析结果
    ai_score        DECIMAL(5,2),               -- 综合评分 0-100
    ai_tags         JSONB DEFAULT '[]',          -- AI 标签
    ai_category     VARCHAR(100),               -- AI 分类
    ai_analysis     TEXT,                        -- 分析报告

    -- 状态
    status          VARCHAR(20) DEFAULT 'pending', -- pending, analyzing, selected, rejected
    selected_at     TIMESTAMPTZ,

    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_pool_score ON product_pool(ai_score DESC, status);
```

```sql
-- 销售数据表
CREATE TABLE sales_data (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id      UUID REFERENCES products(id),
    platform        VARCHAR(20),
    site            VARCHAR(10),
    date            DATE NOT NULL,

    -- 指标
    orders          INT DEFAULT 0,
    gmv             DECIMAL(14,2) DEFAULT 0,     -- 成交额
    units_sold      INT DEFAULT 0,
    impressions     INT DEFAULT 0,
    clicks          INT DEFAULT 0,
    ctr             DECIMAL(6,4) DEFAULT 0,      -- 点击率
    conversion_rate DECIMAL(6,4) DEFAULT 0,       -- 转化率

    -- 成本
    ad_spend        DECIMAL(12,2) DEFAULT 0,     -- 广告花费
    shipping_cost   DECIMAL(12,2) DEFAULT 0,     -- 物流成本
    platform_fee    DECIMAL(12,2) DEFAULT 0,     -- 平台佣金

    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(product_id, platform, site, date)
);

CREATE INDEX idx_sales_date ON sales_data(date DESC, platform, site);
```

```sql
-- 店铺表
CREATE TABLE shops (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(200) NOT NULL,
    platform        VARCHAR(20) NOT NULL,
    site            VARCHAR(10) NOT NULL,
    shop_id_external VARCHAR(100),               -- 平台店铺ID

    -- API 凭证（加密存储）
    api_credentials JSONB DEFAULT '{}',

    status          VARCHAR(20) DEFAULT 'active',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

```sql
-- 告警规则表
CREATE TABLE alert_rules (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(200) NOT NULL,
    shop_id         UUID REFERENCES shops(id),
    product_id      UUID REFERENCES products(id),  -- NULL = 全店

    metric          VARCHAR(50) NOT NULL,        -- 指标名
    condition       VARCHAR(10) NOT NULL,         -- >, <, =, >=, <=
    threshold       DECIMAL(14,2) NOT NULL,

    severity        VARCHAR(10) DEFAULT 'warning', -- info, warning, critical
    enabled         BOOLEAN DEFAULT true,
    notify_channels JSONB DEFAULT '["email"]',    -- email, slack, webhook

    created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

## 3.2 数据流设计

```
外部数据源                    数据采集层                  数据存储层
──────────                  ──────────                ──────────
TikTok Shop API ──┐
Shopee API ───────┤
Lazada API ───────┼──→ MCP Tools ──→ ETL Pipeline ──→ PostgreSQL
供应商 API ───────┤                │                     │
1688/拼多多 ──────┘                │                     ├─ 业务数据
                                  │                     │
爬虫数据 ───────────→ Crawler ────┘                     ├─ 销售数据
                                                         │
                                  ┌─────────────────────┤
                                  │                     │
用户交互层 ←── Agent 分析 ←── 数据服务层 ←──────────────┘
                                  │
                                  ├─ Redis（热数据缓存）
                                  └─ ChromaDB（向量嵌入）
```

## 3.3 缓存策略

| 数据类型 | 缓存介质 | TTL | 刷新策略 |
|---------|---------|-----|---------|
| 类目树 | Redis | 1 天 | 定时刷新 |
| 热搜关键词 | Redis | 1 小时 | 定时刷新 |
| 店铺基础信息 | Redis | 30 分钟 | 访问时刷新 |
| 商品详情 | Redis | 10 分钟 | 变更时主动失效 |
| 选品评分结果 | Redis | 1 天 | 新选品时更新 |
| AI 分析报告 | PostgreSQL | 永久 | 版本管理 |
| API 限流计数 | Redis | 窗口期 | 自动过期 |
| 向量嵌入 | ChromaDB | 永久 | 商品变更时更新 |

---

# 第 4 章 AI Agent 体系设计

## 4.1 Agent 总览

```
                        ┌──────────────────┐
                        │   总控编排 Agent   │
                        │  (Orchestrator)   │
                        └────────┬─────────┘
            ┌───────────────────┼───────────────────┐
            │                   │                   │
    ┌───────┴───────┐  ┌───────┴───────┐  ┌───────┴───────┐
    │  选品 Agent    │  │  优化 Agent    │  │  上架 Agent    │
    │  (Selection)   │  │(Optimization)  │  │  (Listing)    │
    └───────────────┘  └───────────────┘  └───────────────┘
            │                   │                   │
    ┌───────┴───────┐  ┌───────┴───────┐
    │  监控 Agent    │  │  统计 Agent    │
    │ (Monitoring)  │  │  (Analytics)  │
    └───────────────┘  └───────────────┘
            │                   │
            └─────────┬─────────┘
              ┌───────┴───────┐
              │  策略 Agent    │
              │  (Strategy)   │
              └───────────────┘
```

## 4.2 Agent 职责矩阵

| Agent | 触发方式 | 执行频率 | 核心能力 |
|-------|---------|---------|---------|
| 选品 Agent | 定时 + 手动 | 每日 | 多源数据采集、趋势分析、评分排序 |
| 优化 Agent | 选品后 + 手动 | 按需 | 标题/描述生成、关键词优化、图片优化 |
| 上架 Agent | 优化后 + 定时 | 按需 | 多平台发布、SKU映射、定时上架 |
| 监控 Agent | 定时 | 每小时 | 指标采集、异常检测、告警推送 |
| 统计 Agent | 定时 + 手动 | 每日 | 报表生成、数据可视化、AI 解读 |
| 策略 Agent | 事件触发 + 手动 | 按需 | 定价建议、库存建议、投放建议 |

## 4.3 通用 Agent 架构

每个 Agent 共享相同的结构模式：

```python
# 通用 Agent 模板
from langchain.agents import create_agent
from langgraph.checkpoint.sqlite import SqliteSaver

class BaseEcommerceAgent:
    """跨境电商 Agent 基类"""

    def __init__(self, name: str, model, tools, system_prompt, middleware=None):
        self.name = name
        self.agent = create_agent(
            model=model,
            tools=tools,
            system_prompt=system_prompt,
            middleware=middleware or [],
            checkpointer=SqliteSaver.from_conn_string("checkpoints.db"),
            name=name,
        )

    async def execute(self, task: str, context: dict = None) -> dict:
        """执行 Agent 任务"""
        messages = [{"role": "user", "content": task}]
        if context:
            messages.insert(0, {
                "role": "system",
                "content": f"当前上下文: {json.dumps(context, ensure_ascii=False)}"
            })
        result = await self.agent.ainvoke({"messages": messages})
        return self._parse_result(result)

    def _parse_result(self, result: dict) -> dict:
        """解析 Agent 输出为结构化结果"""
        # 子类重写
        return result
```

## 4.4 编排模式

采用**主从编排模式**：

```
总控 Agent (Orchestrator)
  │
  ├── 接收用户意图 → 路由到子 Agent
  │   意图: "选品"  → 选品 Agent
  │   意图: "优化"  → 优化 Agent
  │   意图: "上架"  → 上架 Agent
  │
  ├── 工作流编排 → 串联子 Agent
  │   选品 → 优化 → 审批 → 上架 → 监控
  │
  └── 定时调度 → Cron 触发
      每日 6:00  → 选品 Agent
      每小时    → 监控 Agent
      每日 9:00  → 统计 Agent
```

---

# 第 5 章 选品 Agent

## 5.1 设计目标

从海量商品中筛选出**高潜力爆款商品**，输出评分排序和理由。

## 5.2 选品策略模型

```
选品评分 = 市场热度 × 0.35 + 竞争程度 × 0.25 + 利润空间 × 0.25 + 趋势系数 × 0.15
         ──────────   ──────────   ──────────   ──────────
           需求端        供给端        财务端        时间端
```

### 数据源

| 数据维度 | 数据源 | 获取方式 |
|---------|--------|---------|
| 平台热销榜 | TikTok Shop / Shopee 榜单 | API + 爬虫 |
| 搜索趋势 | 平台搜索热词 | API |
| 竞品分析 | 同类目 Top100 商品 | API |
| 社交媒体 | TikTok / Instagram 话题 | API + 爬虫 |
| 1688 供货 | 1688 商品库 | API |
| 行业报告 | 公开数据 | WebSearch |

## 5.3 Agent 实现

```python
# product-service/agent/selection_agent.py
from langchain.agents import create_agent
from langchain.tools import tool
from pydantic import BaseModel, Field
from typing import List, Optional
import json


# ===== 选品工具集 =====

@tool
def fetch_hot_products(platform: str, site: str, category: str, limit: int = 50) -> str:
    """获取平台热销榜商品。

    Args:
        platform: 平台名 (tiktok_shop, shopee, lazada)
        site: 站点代码 (TH, VN, PH, BR)
        category: 类目名称
        limit: 返回数量
    """
    # 调用 MCP 工具获取平台数据
    # ...
    return json.dumps({"count": 50, "products": [...]}, ensure_ascii=False)


@tool
def search_trends(keyword: str, site: str) -> str:
    """搜索关键词的趋势数据（搜索量变化、热度指数）。

    Args:
        keyword: 搜索关键词
        site: 站点代码
    """
    return json.dumps({
        "keyword": keyword,
        "trend_score": 85,
        "growth_rate": "+23%",
        "search_volume": 15000,
    }, ensure_ascii=False)


@tool
def analyze_competition(product_title: str, category: str, site: str) -> str:
    """分析指定品类的竞争程度。

    Args:
        product_title: 商品标题
        category: 类目
        site: 站点
    """
    return json.dumps({
        "competition_level": "中等",
        "top_seller_count": 45,
        "avg_price": 299,
        "avg_reviews": 120,
        "market_gap_score": 72,
    }, ensure_ascii=False)


@tool
def calculate_profit_margin(supplier_price: float, platform: str, site: str) -> str:
    """计算利润率。

    Args:
        supplier_price: 供货价（人民币）
        platform: 目标平台
        site: 目标站点
    """
    exchange_rates = {"THB": 4.9, "VND": 3450, "PHP": 7.6, "BRL": 0.7}
    fees = {"tiktok_shop": 0.05, "shopee": 0.06, "lazada": 0.05}

    rate = exchange_rates.get(site.upper(), 1)
    platform_fee = fees.get(platform, 0.05)
    shipping_per_unit = 15  # 估算单件物流成本

    selling_price = supplier_price * rate * 1.8  # 1.8倍定价系数
    cost = supplier_price * rate + shipping_per_unit + selling_price * platform_fee
    profit = selling_price - cost
    margin = profit / selling_price * 100

    return json.dumps({
        "selling_price": round(selling_price, 2),
        "cost": round(cost, 2),
        "profit": round(profit, 2),
        "margin": round(margin, 1),
        "verdict": "良好" if margin > 25 else "一般" if margin > 15 else "偏低",
    }, ensure_ascii=False)


@tool
def search_supplier_products(keyword: str, min_price: float = 0, max_price: float = 200) -> str:
    """在 1688/供应商库中搜索货源。

    Args:
        keyword: 搜索关键词
        min_price: 最低价
        max_price: 最高价
    """
    return json.dumps({
        "total_results": 120,
        "avg_price": 25.5,
        "price_range": [8, 85],
        "suppliers": [
            {"name": "义乌A厂", "price": 22.0, "moq": 50},
            {"name": "广州B厂", "price": 18.5, "moq": 100},
        ],
    }, ensure_ascii=False)


@tool
def check_platform_restrictions(product_type: str, site: str) -> str:
    """检查平台对该品类的限制（是否需要资质、禁售等）。

    Args:
        product_type: 商品类型
        site: 目标站点
    """
    restrictions = {
        "电子": "需要CE/FCC认证",
        "化妆品": "需要FDA/MSDS备案",
        "食品": "需要进口许可",
        "服装": "无特殊限制",
        "家居": "无特殊限制",
    }
    return json.dumps({
        "restricted": product_type in ["电子", "化妆品", "食品"],
        "requirements": restrictions.get(product_type, "需人工确认"),
    }, ensure_ascii=False)


# ===== 选品 Agent 组装 =====

SELECTION_SYSTEM_PROMPT = """你是专业的跨境电商选品分析师，负责为 {site} 站点筛选高潜商品。

工作流程：
1. 分析目标市场的热销趋势（fetch_hot_products, search_trends）
2. 在供应商库中匹配货源（search_supplier_products）
3. 计算利润率（calculate_profit_margin）
4. 分析竞争程度（analyze_competition）
5. 检查平台限制（check_platform_restrictions）
6. 输出综合评分和选品建议

评分标准（满分100）：
- 市场需求度（0-35分）：搜索量、增长率、话题热度
- 竞争友好度（0-25分）：卖家数、头部集中度、差异化空间
- 利润空间（0-25分）：毛利率、物流成本、平台佣金
- 趋势潜力（0-15分）：增长趋势、季节性、可持续性

输出格式（JSON）：
{
    "recommendations": [
        {
            "title": "商品标题建议",
            "category": "类目",
            "supplier_price": 供货价,
            "suggested_price": 建议售价,
            "margin": 利润率,
            "score": 综合评分,
            "scores_detail": {"market": 28, "competition": 20, "profit": 22, "trend": 12},
            "reason": "推荐理由（3句话以内）",
            "risk": "风险提示",
            "keywords": ["关键词1", "关键词2"],
            "supplier_link": "货源链接"
        }
    ],
    "market_summary": "市场概况总结",
    "top_trends": ["趋势1", "趋势2"]
}
"""


def create_selection_agent(model):
    """创建选品 Agent"""
    return create_agent(
        model=model,
        tools=[
            fetch_hot_products,
            search_trends,
            analyze_competition,
            calculate_profit_margin,
            search_supplier_products,
            check_platform_restrictions,
        ],
        system_prompt=SELECTION_SYSTEM_PROMPT,
        middleware=[
            ModelRetryMiddleware(max_retries=2),
        ],
        name="selection_agent",
    )
```

## 5.4 执行流程

```
选品请求（类目 + 站点）
    │
    ├──→ fetch_hot_products       # 获取平台热销
    ├──→ search_trends            # 搜索趋势
    │
    ├──→ 筛选 Top 20 候选商品
    │
    ├──→ search_supplier_products # 匹配货源
    ├──→ calculate_profit_margin   # 算利润
    ├──→ analyze_competition       # 竞争分析
    ├──→ check_platform_restrictions # 合规检查
    │
    └──→ LLM 综合评分 → 输出推荐列表
```

---

# 第 6 章 优化 Agent

## 6.1 设计目标

将选定的商品进行**本地化内容优化**，生成符合各平台各站点风格的标题、描述和关键词。

## 6.2 优化维度

| 维度 | 内容 | AI 能力 |
|------|------|---------|
| 标题优化 | 多语言本地化标题 | LLM 生成 + SEO关键词嵌入 |
| 描述优化 | 卖点提炼 + 规格详情 | LLM 结构化生成 |
| 关键词 | 热搜词 + 长尾词 | 平台搜索词API + 向量检索 |
| 图片优化 | 主图 + 详情图 | 图片翻译 + 尺寸适配（可选 DALL-E） |
| 定价策略 | 竞争定价 + 促销价 | 竞品价格分析 |

## 6.3 Agent 实现

```python
# content-service/agent/optimization_agent.py
from langchain.agents import create_agent
from langchain.tools import tool
import json


# ===== 优化工具集 =====

@tool
def get_site_style_guide(site: str, platform: str) -> str:
    """获取目标站点的文案风格指南（标题长度限制、禁用词、本地化特点）。

    Args:
        site: 站点代码 (TH, VN, PH, BR)
        platform: 平台名
    """
    guides = {
        "TH": {
            "language": "泰语",
            "style": "亲切友好，多用 'ค่ะ/ครับ' 敬语，可以适当使用流行语",
            "title_max_chars": 255,
            "title_format": "关键词 + 卖点 + 促销信息",
            "taboo_words": ["第一", "最好", "100%"],
            "popular_emoji": ["✨", "🔥", "💯", "🚀"],
        },
        "VN": {
            "language": "越南语",
            "style": "简洁直接，强调性价比和质量认证",
            "title_max_chars": 255,
            "title_format": "品牌或特征 + 产品名 + 型号/规格 + 优惠",
            "popular_emoji": ["⚡", "💎", "🎯"],
        },
        "BR": {
            "language": "葡萄牙语（巴西）",
            "style": "热情奔放，多用感叹号和 emoji，强调 parcelamento（分期付款）",
            "title_max_chars": 255,
            "title_format": "Marca + Produto + Especificação + Promoção",
            "popular_emoji": ["⚡", "🔥", "🏆", "💸"],
        },
    }
    return json.dumps(guides.get(site, guides["TH"]), ensure_ascii=False)


@tool
def get_hot_keywords(category: str, site: str, limit: int = 20) -> str:
    """获取目标站点类目下的热搜关键词和长尾词。

    Args:
        category: 商品类目
        site: 站点代码
        limit: 返回数量
    """
    return json.dumps({
        "hot_keywords": [
            {"keyword": "เสื้อผ้าแฟชั่น", "search_volume": 50000, "competition": "高"},
            {"keyword": "ชุดเดรส", "search_volume": 35000, "competition": "中"},
        ],
        "long_tail_keywords": [
            "เสื้อผ้าผู้หญิง 2024 เทรนด์ใหม่",
            "เดรสยาว สไตล์เกาหลี",
        ],
    }, ensure_ascii=False)


@tool
def analyze_competitor_listings(product_category: str, site: str, limit: int = 10) -> str:
    """分析同类目 Top 商品标题的关键词和结构。

    Args:
        product_category: 类目
        site: 站点
        limit: Top N
    """
    return json.dumps({
        "common_patterns": [
            "60% 标题以品类关键词开头",
            "80% 包含促销标签如 [ถูกมาก]",
            "45% 使用 emoji",
        ],
        "top_keywords_used": ["แฟชั่น", "ใหม่", "สวย", "คุณภาพ", "ลดราคา"],
        "avg_title_length": 120,
    }, ensure_ascii=False)


@tool
def translate_and_localize(
    text: str, target_language: str, site: str, style: str = "ecommerce"
) -> str:
    """翻译并本地化文案（使用 LLM 实现高质量本地化）。

    Args:
        text: 原始文本（中文）
        target_language: 目标语言 (th, vi, pt, en)
        site: 站点
        style: 文案风格 (ecommerce=电商, casual=口语, formal=正式)
    """
    # 实际调用 LLM 做翻译 + 本地化
    return json.dumps({
        "original": text,
        "translated": "【本地化后的文案】",
        "back_translation": "【回译中文验证】",
    }, ensure_ascii=False)


@tool
def generate_product_images(
    product_title: str, product_features: str, site: str, count: int = 5
) -> str:
    """生成商品图片（主图/详情图/营销图），可选调用 DALL-E 或使用模板。

    Args:
        product_title: 商品标题
        product_features: 商品卖点
        site: 目标站点
        count: 生成数量
    """
    return json.dumps({
        "images": [
            {"type": "main", "url": "https://cdn.example.com/main_001.jpg", "size": "800x800"},
            {"type": "detail", "url": "https://cdn.example.com/detail_001.jpg", "size": "800x1200"},
        ]
    }, ensure_ascii=False)


# ===== 优化 Agent 组装 =====

OPTIMIZATION_SYSTEM_PROMPT = """你是跨境电商内容优化专家，负责为 {site} 站点的商品生成本地化文案。

工作流程：
1. 获取目标站点的文案风格指南（get_site_style_guide）
2. 分析热搜关键词（get_hot_keywords）
3. 分析竞品文案（analyze_competitor_listings）
4. 生成本地化标题（translate_and_localize）
5. 生成商品描述
6. 输出优化后的完整文案

标题要求：
- 包含核心热搜关键词（前35个字符内）
- 符合平台字数限制
- 突出差异化卖点
- 避免禁用词

描述要求：
- 前3行是精华卖点（用户只能看到前3行）
- 结构化展示规格参数
- 包含促销和物流信息
- 使用本地化表达方式

输出格式（JSON）：
{
    "title": "优化后的标题",
    "description": "优化后的描述",
    "keywords": ["关键词列表"],
    "key_selling_points": ["卖点1", "卖点2", "卖点3"],
    "hashtags": ["#标签1", "#标签2"],
    "localization_notes": "本地化说明"
}
"""


def create_optimization_agent(model):
    return create_agent(
        model=model,
        tools=[
            get_site_style_guide,
            get_hot_keywords,
            analyze_competitor_listings,
            translate_and_localize,
            generate_product_images,
        ],
        system_prompt=OPTIMIZATION_SYSTEM_PROMPT,
        name="optimization_agent",
    )
```

## 6.4 SEO关键词策略

```
关键词金字塔：
         ┌─────────────┐
         │  核心大词 1-2个 │  ← 搜索量最大，竞争最激烈
         │  如: ชุดเดรส   │
         ├─────────────┤
         │  精准词 3-5个  │  ← 核心流量
         │  เดรสยาวสไตล์  │
         ├─────────────┤
         │  长尾词 5-10个 │  ← 转化率最高
         │  ชุดเดรสยาว     │
         │  ราคาถูก        │
         └─────────────┘
```

---

# 第 7 章 上架 Agent

## 7.1 设计目标

将优化后的商品**自动推送到各平台**，处理不同平台的字段映射和审核规则。

## 7.2 上架流程

```
商品已优化 ──→ 选择目标店铺 ──→ 字段映射 ──→ 预检 ──→ 上架
                                            │
                                     ┌──────┴──────┐
                                     │  平台审核     │
                                     │  成功 / 失败  │
                                     └─────────────┘
```

## 7.3 Agent 实现

```python
# listing-service/agent/listing_agent.py
from langchain.agents import create_agent
from langchain.tools import tool
import json
from datetime import datetime, timedelta
from typing import Optional


@tool
def map_to_platform(product_data: str, platform: str, site: str) -> str:
    """将通用商品数据映射为目标平台的字段格式。

    Args:
        product_data: 商品数据 JSON
        platform: 目标平台 (tiktok_shop, shopee, lazada)
        site: 目标站点
    """
    # 平台字段映射逻辑
    product = json.loads(product_data)

    if platform == "tiktok_shop":
        mapped = {
            "product_name": product["title"][:255],
            "description": product["description"],
            "category_id": product.get("category_id"),
            "images": [{"url": img} for img in product.get("images", [])],
            "skus": [],
            "package_weight": product.get("weight", 200),
            "package_dimensions": product.get("dimensions", {"length": 10, "width": 10, "height": 5}),
        }
    elif platform == "shopee":
        mapped = {
            "item_name": product["title"][:120],
            "description": product["description"][:3000],
            "category_id": product.get("category_id"),
            "images": product.get("images", []),
            "variations": [],
            "weight": product.get("weight", 0.2),
            "logistics": [],
        }
    else:
        mapped = {}

    return json.dumps(mapped, ensure_ascii=False)


@tool
def pre_check_listing(listing_data: str, platform: str, site: str) -> str:
    """上架前预检：检查必填字段、图片规格、违规词等。

    Args:
        listing_data: 映射后的商品数据
        platform: 平台
        site: 站点
    """
    data = json.loads(listing_data)
    issues = []

    # 检查标题长度
    title_field = "product_name" if platform == "tiktok_shop" else "item_name"
    max_len = 255 if platform == "tiktok_shop" else 120
    if len(data.get(title_field, "")) > max_len:
        issues.append(f"标题超过{max_len}字符限制")

    # 检查图片数量
    min_images = 3 if platform == "tiktok_shop" else 1
    images = data.get("images", [])
    if len(images) < min_images:
        issues.append(f"图片至少{min_images}张")

    # 检查图片规格
    for img in images:
        if img.get("size", 0) < 500 * 1024:
            issues.append("图片小于500KB，可能被压缩")

    # 检查违禁词
    taboo_words = ["第一", "最好", "唯一", "绝对", "100%正品"]
    for word in taboo_words:
        if word in str(data):
            issues.append(f"包含违禁词: {word}")

    return json.dumps({
        "passed": len(issues) == 0,
        "issues": issues,
        "warnings": [],
    }, ensure_ascii=False)


@tool
def publish_listing(
    listing_data: str,
    platform: str,
    site: str,
    shop_id: str,
    schedule_time: Optional[str] = None,
) -> str:
    """将商品发布到目标平台。

    Args:
        listing_data: 映射后的商品数据
        platform: 平台
        site: 站点
        shop_id: 店铺ID
        schedule_time: 定时发布时间（ISO格式），不填则立即发布
    """
    # 调用平台 API
    return json.dumps({
        "success": True,
        "platform_product_id": "123456789",
        "status": "pending_review" if platform == "tiktok_shop" else "active",
        "published_at": schedule_time or datetime.now().isoformat(),
        "review_estimated": "24小时内（TikTok Shop 审核）",
    }, ensure_ascii=False)


@tool
def check_listing_status(platform_product_id: str, platform: str) -> str:
    """查询上架审核状态。

    Args:
        platform_product_id: 平台商品ID
        platform: 平台
    """
    return json.dumps({
        "product_id": platform_product_id,
        "status": "active",
        "review_result": "approved",
        "rejection_reason": None,
    }, ensure_ascii=False)


# ===== 上架 Agent =====

LISTING_SYSTEM_PROMPT = """你是跨境电商上架专家，负责将商品发布到各平台。

工作流程：
1. 将商品数据映射为目标平台格式（map_to_platform）
2. 上架前预检（pre_check_listing）
3. 如果有问题，修复后重新预检
4. 确认无误后发布（publish_listing）
5. 返回上架结果

重要规则：
- TikTok Shop 图片至少 3 张，主图 800x800 以上
- Shopee 标题不超过 120 字符
- 违禁词绝对不能出现
- 定时上架避开平台审核繁忙时段
*/

def create_listing_agent(model):
    return create_agent(
        model=model,
        tools=[
            map_to_platform,
            pre_check_listing,
            publish_listing,
            check_listing_status,
        ],
        system_prompt=LISTING_SYSTEM_PROMPT,
        middleware=[
            HumanInTheLoopMiddleware(
                interrupt_on=["publish_listing"],  # 发布前需人工确认
            ),
        ],
        name="listing_agent",
    )
```

---

# 第 8 章 监控 Agent

## 8.1 设计目标

实时监控多店铺的**核心运营指标**，异常时自动告警。

## 8.2 监控指标体系

```
监控维度
├── 流量指标
│   ├── 曝光量 (Impressions)
│   ├── 点击量 (Clicks)
│   ├── 点击率 (CTR)
│   └── 访客数 (Visitors)
├── 转化指标
│   ├── 订单量 (Orders)
│   ├── 转化率 (CVR)
│   ├── GMV (成交额)
│   └── 客单价 (AOV)
├── 服务指标
│   ├── 好评率 (Rating)
│   ├── 差评数 (Negative Reviews)
│   ├── 退货率 (Return Rate)
│   └── 客服响应时间
├── 商品指标
│   ├── 库存水位 (Stock Level)
│   ├── 价格竞争力 (Price Index)
│   └── 排名变化 (Rank Change)
└── 广告指标
    ├── 广告花费 (Ad Spend)
    ├── 投产比 (ROAS)
    └── 获客成本 (CAC)
```

## 8.3 Agent 实现

```python
# monitoring-service/agent/monitoring_agent.py
from langchain.agents import create_agent
from langchain.tools import tool
import json
from datetime import datetime, timedelta


@tool
def collect_metrics(shop_id: str, platform: str, site: str, metrics: str) -> str:
    """采集店铺核心指标。

    Args:
        shop_id: 店铺ID
        platform: 平台
        site: 站点
        metrics: 指标列表（逗号分隔），如 'orders,gmv,ctr,cvr'
    """
    return json.dumps({
        "shop_id": shop_id,
        "time": datetime.now().isoformat(),
        "metrics": {
            "orders": {"value": 156, "change": "+12%", "status": "normal"},
            "gmv": {"value": 45600, "change": "+8%", "status": "normal"},
            "ctr": {"value": 3.2, "change": "-0.5%", "status": "normal"},
            "cvr": {"value": 5.1, "change": "-1.2%", "status": "warning"},
            "stock_low": {"value": 3, "change": "-80%", "status": "critical"},
        },
    }, ensure_ascii=False)


@tool
def check_alerts(shop_id: str) -> str:
    """检查是否有触发告警。

    Args:
        shop_id: 店铺ID
    """
    return json.dumps({
        "alerts": [
            {
                "severity": "critical",
                "rule": "库存低于安全线",
                "detail": "商品 SKU-001 库存仅剩 3 件",
                "suggested_action": "立即补货或暂停推广",
            },
            {
                "severity": "warning",
                "rule": "转化率下降",
                "detail": "店铺 CVR 从 6.3% 降至 5.1%",
                "suggested_action": "检查商品页面和竞品动态",
            },
        ],
    }, ensure_ascii=False)


@tool
def analyze_reviews(product_id: str, platform: str, limit: int = 50) -> str:
    """分析商品评论，提取用户反馈的关键信息。

    Args:
        product_id: 商品ID
        platform: 平台
        limit: 分析评论数
    """
    return json.dumps({
        "summary": "用户总体满意，但尺码偏小是高频反馈",
        "sentiment": {"positive": 72, "neutral": 18, "negative": 10},
        "top_positive": ["质量好", "物流快", "物超所值"],
        "top_negative": ["尺码偏小", "颜色有偏差"],
        "action_items": ["更新尺码表说明", "补充实物图"],
    }, ensure_ascii=False)


@tool
def send_alert(shop_id: str, severity: str, title: str, detail: str, channels: str) -> str:
    """发送告警通知。

    Args:
        shop_id: 店铺ID
        severity: 严重级别 (critical, warning, info)
        title: 告警标题
        detail: 告警详情
        channels: 通知渠道（逗号分隔），如 'email,slack'
    """
    # 实际调用通知服务
    return json.dumps({"sent": True, "channels": channels.split(",")})


MONITORING_SYSTEM_PROMPT = """你是跨境电商运营监控专家，负责7x24小时监控店铺健康度。

工作流程：
1. 定时采集核心指标（collect_metrics）
2. 检查告警规则（check_alerts）
3. 如果有告警，分析严重程度并发送通知（send_alert）
4. 分析差评和用户反馈（analyze_reviews）
5. 输出监控日报

告警阈值（参考）：
- CTR 下降超过 20% → warning
- CVR 下降超过 10% → warning
- 库存低于 5 → critical
- 差评连续 3 条以上 → critical
- GMV 下降超过 30% → critical
*/

def create_monitoring_agent(model):
    return create_agent(
        model=model,
        tools=[
            collect_metrics,
            check_alerts,
            analyze_reviews,
            send_alert,
        ],
        system_prompt=MONITORING_SYSTEM_PROMPT,
        name="monitoring_agent",
    )
```

---

# 第 9 章 统计 Agent

## 9.1 设计目标

自动生成**日报/周报/月报**，提供可视化数据和 AI 解读。

## 9.2 报表体系

| 报表类型 | 频率 | 内容 |
|---------|------|------|
| 日报 | 每日 9:00 | 昨日核心指标、异常商品、行动建议 |
| 周报 | 每周一 | 趋势对比、品类分析、竞品动态 |
| 月报 | 每月 1 日 | 全月经营分析、利润报表、下月规划 |
| 专项报告 | 按需 | 选品分析、广告ROI分析、促销复盘 |

## 9.3 Agent 实现

```python
# analytics-service/agent/analytics_agent.py
from langchain.agents import create_agent
from langchain.tools import tool
import json
from datetime import datetime, timedelta


@tool
def query_sales_data(shop_id: str, platform: str, site: str,
                     start_date: str, end_date: str, group_by: str = "day") -> str:
    """查询销售数据并按维度聚合。

    Args:
        shop_id: 店铺ID
        platform: 平台
        site: 站点
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
        group_by: 聚合维度 (day, week, month, product, category)
    """
    return json.dumps({
        "period": f"{start_date} ~ {end_date}",
        "summary": {
            "total_gmv": 320000,
            "total_orders": 1200,
            "aov": 266.67,
            "gmv_growth": "+15.2%",
            "order_growth": "+12.8%",
        },
        "daily_trend": [
            {"date": "2024-06-01", "gmv": 45000, "orders": 168},
            {"date": "2024-06-02", "gmv": 42000, "orders": 155},
        ],
    }, ensure_ascii=False)


@tool
def query_product_ranking(shop_id: str, platform: str, site: str,
                          top_n: int = 20, sort_by: str = "gmv") -> str:
    """查询商品排行榜。

    Args:
        shop_id: 店铺ID
        platform: 平台
        site: 站点
        top_n: Top N
        sort_by: 排序指标 (gmv, orders, conversion_rate)
    """
    return json.dumps({
        "top_products": [
            {"rank": 1, "title": "夏季连衣裙", "gmv": 85000, "orders": 320, "margin": 35.2},
            {"rank": 2, "title": "防晒衣", "gmv": 62000, "orders": 280, "margin": 42.1},
        ]
    }, ensure_ascii=False)


@tool
def calculate_profit_report(shop_id: str, start_date: str, end_date: str) -> str:
    """计算利润报表。

    Args:
        shop_id: 店铺ID
        start_date: 开始日期
        end_date: 结束日期
    """
    return json.dumps({
        "revenue": {"gmv": 320000, "refunds": 8500, "net_revenue": 311500},
        "costs": {
            "product_cost": 128000,
            "shipping": 32000,
            "platform_fee": 15000,
            "ad_spend": 25000,
            "other": 5000,
            "total": 205000,
        },
        "profit": {
            "gross_profit": 106500,
            "gross_margin": 34.2,
            "net_profit": 98500,
            "net_margin": 31.6,
        },
    }, ensure_ascii=False)


STATISTICS_SYSTEM_PROMPT = """你是跨境电商数据分析专家，负责生成经营报表和AI解读。

工作流程：
1. 查询销售数据（query_sales_data）
2. 查询商品排名（query_product_ranking）
3. 计算利润报表（calculate_profit_report）
4. 生成自然语言的 AI 解读

报告模板：
# 📊 {shop_name} 经营日报

## 核心指标
| 指标 | 昨日 | 环比 | 7日均值 | 状态 |
|------|------|------|---------|------|
| GMV  | ...  | ...  | ...     | ...  |
| 订单 | ...  | ...  | ...     | ...  |
...

## Top 5 商品
...

## AI 解读
...

## 行动建议
...
*/

def create_analytics_agent(model):
    return create_agent(
        model=model,
        tools=[
            query_sales_data,
            query_product_ranking,
            calculate_profit_report,
        ],
        system_prompt=STATISTICS_SYSTEM_PROMPT,
        name="analytics_agent",
    )
```

---

# 第 10 章 策略 Agent

## 10.1 设计目标

基于**监控数据 + 统计结果 + 市场趋势**，给出可执行的运营建议。

## 10.2 策略决策模型

```
输入层                        分析层                      输出层
────────                    ────────                    ────────
监控数据 ─┐              ┌─ 定价策略模型 ──→ 建议调价方案
统计报表 ─┤              ├─ 库存策略模型 ──→ 补货 / 清仓建议
竞品数据 ─┼──→ 策略Agent ─┼─ 推广策略模型 ──→ 广告优化建议
市场趋势 ─┤              ├─ 选品策略模型 ──→ 上新 / 下架建议
用户反馈 ─┘              └─ 风险预警模型 ──→ 风险规避建议
```

## 10.3 Agent 实现

```python
# analytics-service/agent/strategy_agent.py
from langchain.agents import create_agent
from langchain.tools import tool
import json


@tool
def analyze_price_position(product_id: str, platform: str, site: str) -> str:
    """分析商品价格在同类目中的位置和竞争力。

    Args:
        product_id: 商品ID
        platform: 平台
        site: 站点
    """
    return json.dumps({
        "our_price": 299,
        "market_avg": 320,
        "market_median": 310,
        "price_position": "偏低",  # 偏低/合理/偏高
        "competitors": [
            {"title": "竞品A", "price": 350, "sales_rank": 1},
            {"title": "竞品B", "price": 280, "sales_rank": 3},
        ],
        "suggestion": "可提价至 320（仍低于均值），预计 margin +7%",
    }, ensure_ascii=False)


@tool
def analyze_inventory_health(shop_id: str) -> str:
    """分析库存健康度。

    Args:
        shop_id: 店铺ID
    """
    return json.dumps({
        "healthy": 45,
        "low_stock": 8,       # 需要补货
        "overstock": 12,       # 需要清仓
        "recommendations": [
            {
                "product": "连衣裙-S",
                "action": "紧急补货",
                "reason": "库存仅剩 3 件，日销 5 件",
                "suggested_order": 200,
            },
            {
                "product": "冬季外套-XL",
                "action": "清仓促销",
                "reason": "库存积压 120 件，季末贬值风险",
                "suggested_discount": "30% off",
            },
        ],
    }, ensure_ascii=False)


@tool
def optimize_ad_campaign(product_id: str, platform: str, budget: float) -> str:
    """分析广告投放效果并给出优化建议。

    Args:
        product_id: 商品ID
        platform: 平台
        budget: 广告预算
    """
    return json.dumps({
        "current_roas": 3.2,
        "avg_roas": 4.5,
        "waste_keywords": ["宽松连衣裙", "大码连衣裙"],
        "potential_keywords": ["夏季新款", "度假裙"],
        "suggestion": "暂停2个低效词，新增2个高潜词，预计ROAS提升至4.0+",
    }, ensure_ascii=False)


STRATEGY_SYSTEM_PROMPT = """你是跨境电商运营策略专家，基于数据给出可执行的运营建议。

工作流程：
1. 分析价格竞争力（analyze_price_position）
2. 分析库存健康度（analyze_inventory_health）
3. 优化广告投放（optimize_ad_campaign）
4. 综合给出策略建议

建议输出格式：
## 📋 运营策略建议

### 定价调整
- [商品名] 当前XX元 → 建议XX元，原因：...

### 库存管理
- [商品名] 立即补货XX件，原因：...
- [商品名] 清仓促销，建议折扣XX，原因：...

### 广告优化
- 暂停关键词：[...]
- 新增关键词：[...]
- 预算调整：XX → XX

### 风险提示
- ...
*/

def create_strategy_agent(model):
    return create_agent(
        model=model,
        tools=[
            analyze_price_position,
            analyze_inventory_health,
            optimize_ad_campaign,
        ],
        system_prompt=STRATEGY_SYSTEM_PROMPT,
        name="strategy_agent",
    )
```

---

# 第 11 章 平台集成层（MCP）

## 11.1 设计思路

使用 **MCP (Model Context Protocol)** 将各电商平台 API 封装为标准化工具，让 Agent 可以透明地调用任何平台的接口。

## 11.2 MCP 工具架构

```
                    ┌──────────────────┐
                    │   Agent (主机)    │
                    │  调用工具, 路由   │
                    └────────┬─────────┘
                             │
                    ┌────────┴─────────┐
                    │  MCP Client      │
                    │  管理连接, 发现工具 │
                    └────────┬─────────┘
           ┌────────────────┼────────────────┐
           │                │                │
    ┌──────┴──────┐ ┌──────┴──────┐ ┌──────┴──────┐
    │ TikTok Shop  │ │   Shopee    │ │  通用工具   │
    │ MCP Server   │ │ MCP Server  │ │ MCP Server  │
    └──────────────┘ └──────────────┘ └──────────────┘
```

## 11.3 平台工具清单

### TikTok Shop MCP Server

```
工具列表:
├── tiktok_get_shop_info()        → 获取店铺信息
├── tiktok_upload_product()        → 上传商品
├── tiktok_update_product()        → 更新商品
├── tiktok_get_products()          → 商品列表
├── tiktok_get_orders()            → 订单列表
├── tiktok_get_sales_data()        → 销售数据
├── tiktok_get_reviews()           → 商品评价
├── tiktok_get_categories()        → 类目树
├── tiktok_search_products()       → 搜索商品
├── tiktok_get_hot_keywords()      → 热搜词
└── tiktok_update_stock()          → 更新库存
```

### Shopee MCP Server

```
工具列表:
├── shopee_get_shop_info()
├── shopee_upload_item()
├── shopee_update_item()
├── shopee_get_items()
├── shopee_get_orders()
├── shopee_get_sales_data()
├── shopee_get_reviews()
├── shopee_get_categories()
├── shopee_search_items()
├── shopee_get_hot_keywords()
└── shopee_update_stock()
```

### 通用工具 MCP Server

```
工具列表:
├── web_search()                   → 互联网搜索
├── translate()                    → 翻译
├── image_generate()               → AI 图片生成
├── image_remove_bg()              → 图片去背景
├── calculate_shipping()           → 物流费计算
├── exchange_rate()                → 实时汇率
└── crawl_webpage()                → 网页抓取
```

## 11.4 MCP 集成代码

```python
# mcp-service/client.py
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from typing import List
from langchain_core.tools import BaseTool


class EcommerceMCPClient:
    """跨境电商 MCP 客户端"""

    def __init__(self):
        self.client = MultiServerMCPClient({})
        self._connected = False

    async def connect_all_servers(self):
        """连接所有平台 MCP 服务器"""

        # TikTok Shop - 不同站点
        for site in ["TH", "VN", "PH", "MY", "ID"]:
            await self.client.connect_to_server(
                f"tiktok_{site.lower()}",
                {
                    "transport": "streamable_http",
                    "url": f"http://mcp-tiktok:8080/{site.lower()}",
                },
            )

        # Shopee - 不同站点
        for site in ["TH", "BR", "VN"]:
            await self.client.connect_to_server(
                f"shopee_{site.lower()}",
                {
                    "transport": "streamable_http",
                    "url": f"http://mcp-shopee:8080/{site.lower()}",
                },
            )

        # 通用工具
        await self.client.connect_to_server(
            "common",
            {
                "transport": "streamable_http",
                "url": "http://mcp-common:8080/",
            },
        )

        self._connected = True

    async def get_all_tools(self) -> List[BaseTool]:
        """获取所有平台工具"""
        if not self._connected:
            await self.connect_all_servers()
        return await self.client.get_tools()

    async def get_tools_for_platform(self, platform: str, site: str) -> List[BaseTool]:
        """获取指定平台工具"""
        all_tools = await self.get_all_tools()

        prefix = f"{platform}_{site.lower()}"
        return [t for t in all_tools if t.name.startswith(prefix)]
```

---

# 第 12 章 总控编排 Agent

## 12.1 设计思路

总控 Agent 是系统的"大脑"，负责：

1. **意图识别**：理解用户要做什么（选品/优化/上架/监控/统计）
2. **任务路由**：将任务分发给对应的子 Agent
3. **工作流编排**：串联多步骤业务流程
4. **结果汇总**：收集各子 Agent 的结果并汇总呈现

## 12.2 完整工作流

```python
# orchestration-service/agent/orchestrator.py
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from typing import TypedDict, Annotated, List, Optional
from langchain_core.messages import BaseMessage
import json


# ===== 状态定义 =====
class OrchestratorState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    intent: str                          # 用户意图
    context: dict                        # 全局上下文
    selection_results: Optional[str]     # 选品结果
    optimization_results: Optional[str]  # 优化结果
    listing_results: Optional[str]       # 上架结果
    monitoring_results: Optional[str]    # 监控结果
    analytics_results: Optional[str]     # 统计结果
    strategy_results: Optional[str]      # 策略结果
    final_response: Optional[str]        # 最终回复


# ===== 主工作流 =====
def build_orchestration_graph(model):
    """构建总控编排工作流"""

    builder = StateGraph(OrchestratorState)

    # 添加节点
    builder.add_node("understand_intent", understand_intent_node)
    builder.add_node("run_selection", make_run_agent_node("selection", model))
    builder.add_node("run_optimization", make_run_agent_node("optimization", model))
    builder.add_node("run_listing", make_run_agent_node("listing", model))
    builder.add_node("run_monitoring", make_run_agent_node("monitoring", model))
    builder.add_node("run_analytics", make_run_agent_node("analytics", model))
    builder.add_node("run_strategy", make_run_agent_node("strategy", model))
    builder.add_node("aggregate_response", aggregate_response_node)

    # 添加边
    builder.add_edge(START, "understand_intent")

    # 条件路由：根据意图分发
    builder.add_conditional_edges(
        "understand_intent",
        route_by_intent,
        {
            "selection": "run_selection",
            "optimization": "run_optimization",
            "listing": "run_listing",
            "monitoring": "run_monitoring",
            "analytics": "run_analytics",
            "strategy": "run_strategy",
            "workflow": "run_selection",  # 全流程
            "unknown": "aggregate_response",
        },
    )

    # 工作流串联（全流程模式）
    builder.add_edge("run_selection", "run_optimization")
    builder.add_edge("run_optimization", "run_listing")
    builder.add_edge("run_listing", "aggregate_response")

    # 其他节点直接到汇总
    builder.add_edge("run_monitoring", "aggregate_response")
    builder.add_edge("run_analytics", "aggregate_response")
    builder.add_edge("run_strategy", "aggregate_response")

    builder.add_edge("aggregate_response", END)

    return builder.compile()


# ===== 节点函数 =====
async def understand_intent_node(state: OrchestratorState) -> dict:
    """意图识别节点"""
    last_msg = state["messages"][-1].content.lower()

    intent_map = {
        "选品": "selection", "找品": "selection", "选款": "selection",
        "优化": "optimization", "改标题": "optimization", "写文案": "optimization",
        "上架": "listing", "发布": "listing", "上新": "listing",
        "监控": "monitoring", "数据": "analytics", "统计": "analytics",
        "报表": "analytics", "周报": "analytics", "日报": "analytics",
        "策略": "strategy", "建议": "strategy", "怎么做": "strategy",
        "全流程": "workflow", "一键": "workflow",
    }

    for keyword, intent in intent_map.items():
        if keyword in last_msg:
            return {"intent": intent}

    return {"intent": "unknown"}


def route_by_intent(state: OrchestratorState) -> str:
    """路由函数"""
    return state["intent"]


def make_run_agent_node(agent_name: str, model):
    """创建执行子 Agent 的节点"""

    async def run_agent_node(state: OrchestratorState) -> dict:
        context = {
            "selection_results": state.get("selection_results"),
            "optimization_results": state.get("optimization_results"),
            "listing_results": state.get("listing_results"),
        }

        # 根据 agent_name 创建对应的 Agent 并执行
        agent = _get_agent_by_name(agent_name, model)
        last_msg = state["messages"][-1].content
        result = await agent.ainvoke({
            "messages": [{"role": "user", "content": last_msg}],
        })

        key = f"{agent_name}_results"
        return {
            key: result["messages"][-1].content,
            "messages": result["messages"],
        }

    return run_agent_node


async def aggregate_response_node(state: OrchestratorState) -> dict:
    """汇总所有结果"""
    parts = []

    if state.get("selection_results"):
        parts.append(f"## 选品结果\n{state['selection_results']}")
    if state.get("optimization_results"):
        parts.append(f"## 优化结果\n{state['optimization_results']}")
    if state.get("listing_results"):
        parts.append(f"## 上架结果\n{state['listing_results']}")
    if state.get("monitoring_results"):
        parts.append(f"## 监控结果\n{state['monitoring_results']}")
    if state.get("analytics_results"):
        parts.append(f"## 统计分析\n{state['analytics_results']}")
    if state.get("strategy_results"):
        parts.append(f"## 策略建议\n{state['strategy_results']}")

    return {"final_response": "\n\n".join(parts) if parts else "请告诉我你需要什么帮助？"}


# ===== 定时调度 =====
class OrchestratorScheduler:
    """定时任务调度"""

    async def daily_selection_task(self):
        """每日选品任务（早上6点）"""
        model = init_chat_model("openai:gpt-4o")
        agent = create_selection_agent(model)

        result = await agent.ainvoke({
            "messages": [{
                "role": "user",
                "content": "分析 TH 站点服装类目，推荐 10 个本周潜力商品。"
            }],
        })
        return result

    async def hourly_monitoring_task(self):
        """每小时监控任务"""
        # 采集所有店铺指标，检查告警
        pass

    async def daily_report_task(self):
        """每日报表（早上9点）"""
        model = init_chat_model("openai:gpt-4o")
        agent = create_analytics_agent(model)

        # 为每个店铺生成日报
        pass
```

## 12.3 用户对话示例

```
用户: 帮我找一下泰国站防晒衣的爆款

总控Agent:
  → 意图: selection
  → 选品Agent: fetch_hot_products + search_trends + analyze_competition
  → 输出: Top 10 推荐商品列表（含评分、利润、风险）

用户: 第 3 个看着不错，帮我优化一下文案

总控Agent:
  → 意图: optimization
  → 优化Agent: get_site_style_guide + get_hot_keywords + translate_and_localize
  → 输出: 泰语标题 3 个版本 + 本地化描述

用户: 优化没问题，上架到我的 TT 泰国店

总控Agent:
  → 意图: listing
  → 上架Agent: map_to_platform + pre_check_listing + publish_listing
  → 输出: 上架成功，商品ID 123456，等待平台审核

用户: 一周了，帮我看看卖的怎么样

总控Agent:
  → 意图: analytics → strategy
  → 统计Agent: 生成周报
  → 策略Agent: 根据周报数据给出优化建议
  → 输出: 周报 + 建议调价到320铢 + 新增关键词
```

---

# 第 13 章 前端仪表盘

## 13.1 技术选型

| 技术 | 用途 |
|------|------|
| Vite 6 | 构建工具（极速 HMR，零配置） |
| React 19 | UI 框架 |
| React Router 7 | 客户端路由（SPA） |
| Tailwind CSS | 样式 |
| Tremor / shadcn/ui | 图表组件库 |
| SWR | 数据获取和缓存 |
| Zustand | 状态管理 |
| SSE | 实时数据推送 |

> 为什么不用 Next.js：这是**内部管理工具**而非对外独立站，不需要 SSR/SEO。SPA 部署更简单（一个静态 dist 目录），首屏加载由 Vite code-split 优化即可。

## 13.2 页面结构

```
仪表盘页面结构
├── /dashboard                 # 总览首页
│   ├── 今日核心指标卡片
│   │   [GMV] [订单] [利润率] [ROAS]
│   ├── 销售趋势图（7天折线）
│   ├── Top 商品排行榜
│   └── 告警面板
│
├── /products                  # 商品管理
│   ├── 商品列表（筛选/排序/搜索）
│   ├── 商品详情（含 AI 分析）
│   └── 批量操作（优化/上架）
│
├── /selection                 # 选品中心
│   ├── 选品池列表
│   ├── AI 评分详情
│   └── 选品对比
│
├── /content                   # 内容优化
│   ├── 优化任务列表
│   ├── 文案编辑器（AI 辅助）
│   └── 图片优化
│
├── /listing                   # 上架管理
│   ├── 上架队列
│   ├── 上架记录
│   └── 定时上架
│
├── /monitoring                # 运营监控
│   ├── 实时指标面板
│   ├── 告警规则配置
│   └── 告警历史
│
├── /reports                   # 数据报表
│   ├── 日报/周报/月报
│   ├── 利润报表
│   └── 自定义报表
│
├── /strategy                   # 策略建议
│   ├── AI 策略建议列表
│   ├── 定价分析
│   └── 库存建议
│
└── /settings                  # 设置
    ├── 店铺管理
    ├── API 凭证
    └── 用户偏好
```

## 13.3 AI 对话侧边栏

每个页面右下角悬浮一个**AI 助手对话框**，支持：

```
┌─────────────────────────┐
│  🤖 AI 运营助手          │
│                         │
│  你可以问我:             │
│  "本周销量最好的3个品"    │
│  "帮我分析一下转化率下降"  │
│  "防晒衣现在该补货吗"     │
│                         │
│  [输入框________________] │
└─────────────────────────┘
```

---

# 第 14 章 部署与运维

## 14.1 容器化部署

```yaml
# docker-compose.yml (生产精简版)
version: "3.8"

services:
  # API 网关
  gateway:
    image: nginx:alpine
    ports: ["80:80", "443:443"]
    volumes: ["./nginx.conf:/etc/nginx/nginx.conf"]

  # 前端（SPA 静态部署，nginx 直接托管）
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    volumes: ["./frontend/dist:/usr/share/nginx/html"]

  # 核心服务
  product-service:
    build: ./services/product-service
    environment: &env
      DATABASE_URL: postgresql://user:pass@postgres:5432/ecommerce
      REDIS_URL: redis://redis:6379
      OPENAI_API_KEY: ${OPENAI_API_KEY}

  content-service:
    build: ./services/content-service
    environment: *env

  listing-service:
    build: ./services/listing-service
    environment: *env

  monitoring-service:
    build: ./services/monitoring-service
    environment: *env

  analytics-service:
    build: ./services/analytics-service
    environment: *env

  orchestration-service:
    build: ./services/orchestration-service
    environment: *env

  # MCP 服务
  mcp-tiktok:
    build: ./services/mcp-tiktok
    environment: *env

  mcp-shopee:
    build: ./services/mcp-shopee
    environment: *env

  # 数据层
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: ecommerce
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes: ["./data/postgres:/var/lib/postgresql/data"]

  redis:
    image: redis:7-alpine
    volumes: ["./data/redis:/data"]

  rabbitmq:
    image: rabbitmq:3-management-alpine
    ports: ["5672:5672", "15672:15672"]
```

## 14.2 监控告警

| 层面 | 工具 | 监控内容 |
|------|------|---------|
| 基础设施 | Prometheus + Grafana | CPU、内存、网络、磁盘 |
| 应用 | OpenTelemetry | 请求延迟、错误率 |
| Agent | LangSmith | Agent 轨迹、Token 消耗 |
| 业务 | 自建指标 | GMV、订单量、上架成功率 |
| 告警 | AlertManager | 多渠道通知 |

## 14.3 安全设计

| 层面 | 措施 |
|------|------|
| API 认证 | JWT + API Key |
| 平台凭证 | 加密存储（AES-256） |
| 数据传输 | HTTPS |
| 输入校验 | Pydantic 严格校验 |
| 频率限制 | Redis 令牌桶 |
| 权限控制 | RBAC（管理员/运营/只读） |
| 审计日志 | 所有操作可追溯 |

---

# 第 15 章 项目路线图

## MVP 阶段（4周）

| 周次 | 任务 | 产出 |
|------|------|------|
| W1 | 技术架构搭建、数据库设计、FastAPI 骨架 | 可运行框架 |
| W2 | 选品 Agent + 优化 Agent 核心功能 | 选品+优化可用 |
| W3 | 上架 Agent + MCP 平台对接（TikTok Shop TH） | 单平台跑通 |
| W4 | 监控 Agent + 前端仪表盘 MVP | 可演示 MVP |

## 增长阶段（6周）

| 周次 | 任务 |
|------|------|
| W5-6 | 统计 Agent + 策略 Agent |
| W7-8 | 多平台扩展（Shopee TH/BR） |
| W9-10 | 前端完整功能 + AI 对话 |

## 成熟阶段（持续）

- A/B 实验框架
- 自动选品 → 自动上架全自动化
- 知识图谱（商品关联推荐）
- 多店铺协同管理
- 移动端 App

---

# 第 16 章 可行度分析与新手方案

## 16.1 平台 API 准入门槛

### 现实情况：新手小白基本拿不到 API

| 平台 | API 开放程度 | 准入门槛 | 新手可行性 |
|------|------------|---------|-----------|
| **TikTok Shop** | 开放平台（需审批） | 企业认证 + 店铺运营 60 天以上 + 订单量达标 + ISV 认证 | 几乎不可能 |
| **Shopee** | 开放平台 | 企业认证 + 店铺活跃 + API 调用权限审批 | 几乎不可能 |
| **Lazada** | 开放平台 | 企业认证 + 技术审核 | 几乎不可能 |
| **Amazon** | SP-API | 专业卖家账号 + IAM 配置 + 开发资质 | 极低 |

:::info
各平台 API 本质上是为 **ISV（独立软件开发商）和成熟服务商**设计的，不是给小卖家用的。新手个人卖家或小团队，账户类型、GMV、运营时长等都不满足条件。
:::

## 16.2 三种可行方案对比

基于"新手小白能实际落地"的约束，有 3 条路线：

```
方案                      核心技术              能做什么                    适合谁
─────────────────────────────────────────────────────────────────────────────
A. 浏览器自动化     Playwright/Puppeteer    操作任何网页（1688选品、      新手 ✅
                   + OCR + 视觉AI           ERP后台、平台商家后台）

B. ERP 对接         主流ERP（店小秘/芒果/     批量上品、订单管理、          已有ERP的卖家 ✅
                   马帮）的本地操作           库存同步

C. CSV 批量导入     平台商家后台的            批量上架新商品                 所有新手 ✅
                   CSV/Excel导入功能
```

**推荐**：三个方案不互斥，而是**互补组合**：

```
方案 C（CSV导入上架）
    +
方案 A（浏览器自动化做选品采集 + 监控）
    +
方案 B（如果已用ERP，自动化操作ERP）
```

## 16.3 推荐方案：以浏览器自动化为核心的新手架构

### 架构重设计

```
                         ┌─────────────────────┐
                         │   AI Agent 决策层    │
                         │  (分析/选品/策略)     │
                         │  保持不变 ✅          │
                         └─────────┬───────────┘
                                   │
                 ┌─────────────────┼─────────────────┐
                 │                 │                 │
        ┌────────┴──────┐  ┌──────┴──────┐  ┌──────┴──────┐
        │  选品执行层    │  │  上架执行层  │  │  监控执行层  │
        │  Playwright   │  │   CSV导出   │  │  Playwright │
        │  操作浏览器    │  │   + 导入    │  │  采集数据    │
        └───────────────┘  └─────────────┘  └─────────────┘
                 │                 │                 │
        ┌────────┴──────┐  ┌──────┴──────┐  ┌──────┴──────┐
        │ 1688           │  │  本地CSV    │  │ 平台商家后台  │
        │ 淘宝           │  │  文件中转   │  │ 登录抓数据   │
        │ 拼多多          │  │            │  │              │
        │ 抖音/小红书      │  │ ERP批量导入  │  │              │
        └───────────────┘  └─────────────┘  └─────────────┘
```

**核心变化**：把原来的"API 调用"替换为"浏览器自动化操作"。

### 执行层代码差异

```python
# ❌ 原方案：API 调用（需要开发者资质，新手行不通）
result = tiktok_api.upload_product(product_data)

# ✅ 新方案：浏览器自动化操作
# 方式 1：操作平台商家后台直接填表单
# 方式 2：生成 CSV → 用户登录后台手动导入
# 方式 3：操作已安装的 ERP（如店小秘）批量上品
```

## 16.4 方案 A：浏览器自动化（核心工具）

### 选品数据采集

```python
# 不用 API，用 Playwright 操作浏览器采集数据

@tool
async def crawl_1688_products(keyword: str, max_pages: int = 3) -> str:
    """从1688采集商品数据（模拟真实用户浏览）。

    Args:
        keyword: 搜索关键词
        max_pages: 爬取页数
    """
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # headless=False 更不易被检测
        page = await browser.new_page()

        # 模拟真实用户行为
        await page.goto("https://www.1688.com/")
        await page.wait_for_timeout(random.randint(1000, 3000))

        # 搜索
        await page.fill('input[name="keywords"]', keyword)
        await page.click('button[type="submit"]')
        await page.wait_for_timeout(random.randint(2000, 4000))

        products = []
        for p in range(max_pages):
            # 提取商品信息
            items = await page.query_selector_all('.product-item')
            for item in items:
                title = await item.query_selector('.title')
                price = await item.query_selector('.price')

                if title and price:
                    products.append({
                        "title": await title.text_content(),
                        "price": await price.text_content(),
                    })

            # 翻页（随机延迟，反反爬）
            if p < max_pages - 1:
                next_btn = await page.query_selector('.next-page')
                if next_btn:
                    await next_btn.click()
                    await page.wait_for_timeout(random.randint(2000, 5000))

        await browser.close()
        return json.dumps({"total": len(products), "products": products}, ensure_ascii=False)


@tool
async def crawl_platform_trends(platform: str, site: str, keyword: str) -> str:
    """从 TikTok Shop/Shopee 平台抓取热销数据（浏览器访问前台）。

    Args:
        platform: 平台
        site: 站点
        keyword: 关键词
    """
    # 用 Playwright 访问平台前台页面（买家端，不需要登录）
    # 抓取搜索结果中的销量排名、价格区间等
    # ...
```

### CSV 生成 + 批量上架

```python
# 代替 API 上架：生成 CSV → 用户登录平台后台批量导入

@tool
async def generate_listing_csv(products: str, platform: str, site: str) -> str:
    """生成符合平台格式的批量上架 CSV 文件。

    Args:
        products: 商品数据（JSON）
        platform: 目标平台
        site: 站点
    """
    import csv
    from pathlib import Path

    data = json.loads(products)
    output_dir = Path.home() / "Desktop" / "listings"
    output_dir.mkdir(exist_ok=True)

    filepath = output_dir / f"{platform}_{site}_批量上架{datetime.now():%Y%m%d_%H%M}.csv"

    if platform == "tiktok_shop":
        fieldnames = [
            "product_name", "category_id", "brand", "price",
            "stock", "description", "main_image_url", "image_urls",
            "package_weight", "package_length", "package_width", "package_height",
            "sku_id", "sku_price", "sku_stock"
        ]

        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for product in data.get("products", []):
                writer.writerow({
                    "product_name": product["title"],
                    "category_id": product.get("category_id", ""),
                    "price": product["price"],
                    "stock": 100,
                    "description": product.get("description", ""),
                    "main_image_url": product.get("main_image", ""),
                    "image_urls": ",".join(product.get("images", [])),
                    "package_weight": 200,
                    "package_length": 10, "package_width": 10, "package_height": 5,
                })

    elif platform == "shopee":
        fieldnames = [
            "item_name", "category_id", "price", "stock",
            "description", "weight", "images", "logistics"
        ]
        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for product in data.get("products", []):
                writer.writerow({...})

    return json.dumps({
        "filepath": str(filepath),
        "count": len(data.get("products", [])),
        "instruction": f"请登录 {platform} {site} 站点商家后台 → 商品管理 → 批量导入 → 选择文件 {filepath.name}",
    }, ensure_ascii=False)
```

### 运营数据监控（浏览器方案）

```python
# 用浏览器登录商家后台采集数据（代替 API 拉取）

@tool
async def collect_shop_data_via_browser(
    shop_id: str, platform: str, site: str, session_file: str
) -> str:
    """通过浏览器登录商家后台采集运营数据。

    Args:
        shop_id: 店铺ID
        platform: 平台
        site: 站点
        session_file: 浏览器会话文件路径（保存登录态，避免每次重新登录）
    """
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        # 使用持久化浏览器上下文（保留登录 Cookie）
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=f"./browser_data/{shop_id}",
            headless=False,
        )
        page = await browser.new_page()

        # 访问商家后台
        if platform == "tiktok_shop":
            await page.goto(f"https://seller.tiktokglobalshop.com/")
        elif platform == "shopee":
            await page.goto(f"https://seller.shopee.co.th/")

        # 等待用户手动登录（第一次）或自动恢复会话
        await page.wait_for_selector(".dashboard-metrics", timeout=60000)

        # 抓取核心指标
        metrics = {}

        # GMV
        gmv_elem = await page.query_selector(".gmv-value")
        if gmv_elem:
            metrics["gmv"] = await gmv_elem.text_content()

        # 订单数
        orders_elem = await page.query_selector(".orders-value")
        if orders_elem:
            metrics["orders"] = await orders_elem.text_content()

        await browser.close()
        return json.dumps(metrics, ensure_ascii=False)
```

## 16.5 方案 B：ERP 对接（如果有 ERP）

国内跨境电商最常用的 ERP 工具：

| ERP | 特色 | 支持平台 | 是否可自动化 |
|-----|------|---------|------------|
| **店小秘** | 最主流，免费版可用 | TT/Shopee/Lazada/Amazon | 可操作 Web 版 |
| **芒果店长** | 老牌，功能全 | TT/Shopee/Lazada | 可操作 Web 版 |
| **马帮 ERP** | 仓储管理强 | 全平台 | 可操作 Web 版 |
| **通途 ERP** | 刊登功能 | 多平台 | 可操作 Web 版 |

```python
# ERP 自动化工具：操作 ERP 的 Web 界面进行批量上品

@tool
async def erp_bulk_listing(
    erp_name: str,          # "dianxiaomi" | "mango" | "tongtool"
    csv_filepath: str,
    erp_account: str,       # ERP 登录账号（从配置读取）
) -> str:
    """通过浏览器自动化操作 ERP 批量上架。

    Args:
        erp_name: ERP名称
        csv_filepath: 上架CSV文件路径
        erp_account: ERP账号
    """
    # 不同 ERP 的操作流程
    erp_flows = {
        "dianxiaomi": [
            ("navigate", "https://www.dianxiaomi.com/"),
            ("login", erp_account),
            ("click", "商品管理"),
            ("click", "批量刊登"),
            ("upload_file", csv_filepath),
            ("click", "开始导入"),
        ],
        "mango": [
            ("navigate", "https://www.mangoerp.com/"),
            ("login", erp_account),
            ("click", "产品"),
            ("click", "批量上传"),
            ("upload_file", csv_filepath),
        ],
    }

    flow = erp_flows.get(erp_name)
    if not flow:
        return json.dumps({"error": f"不支持的ERP: {erp_name}"})

    # 用 Playwright 按流程操作...
    return json.dumps({"status": "success", "erp": erp_name})
```

## 16.6 方案 C：CSV 直出（零门槛兜底方案）

这是**任何新手都能立即使用**的方式：

```
AI 生成商品文案 → 导出为 CSV 文件 → 用户登录平台后台 → 手动导入
                                                         ↓
                                                  TikTok Shop: 商品 → 批量工具 → 批量上传
                                                  Shopee: 商品 → 新增商品 → 批量上传
```

**优点**：
- 零技术门槛，不需要任何 API 或浏览器自动化
- 平台原生支持 CSV/Excel 导入，不会触发风控
- AI 做最值钱的部分（选品决策 + 文案生成），人做简单的点击操作

**缺点**：
- 上架环节仍需要人工操作（从下载 CSV 到导入约 2-5 分钟/批次）

## 16.7 新手方案总结

```
                     AI 决策层（不变）
                     ├── 选品分析
                     ├── 文案优化
                     ├── 策略建议
                     └── 数据解读
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
    选品数据来源          上架执行方式         运营数据监控
          │                 │                 │
  ┌───────┴───────┐  ┌─────┴─────┐  ┌───────┴───────┐
  │ 浏览器自动采集  │  │ CSV文件导出│  │ 浏览器模拟登录  │
  │ 1688/淘宝/拼多多│  │ → 手动导入 │  │ 抓取后台数据    │
  │                │  │ (零门槛)  │  │                │
  │ TikTok买家端浏览│  │          │  │ 或用ERP自动推送 │
  └───────────────┘  └───────────┘  └───────────────┘
         ↑                ↑                ↑
    风险：反爬检测      风险：最低        风险：登录态维护
    对策：慢速/轮换IP   对策：无需        对策：持久化session
```

## 16.8 迭代建议

```
第1阶段（零门槛启动）
  → AI 决策层就绪
  → 输出 CSV 文件
  → 人工导入上架
  → 数据手动录入或截图给 AI 分析

第2阶段（加入浏览器自动化）
  → Playwright 采集选品数据
  → 自动生成上架 CSV
  → 仍手动导入（安全第一）

第3阶段（自动化上架 + 监控）
  → 浏览器自动登录平台操作
  → 或对接 ERP 自动上架
  → 自动采集运营数据

第4阶段（API 化，未来）
  → 店铺做大后有 API 权限了
  → 切换到 API 方案
  → 实现全自动化
```

---

> **核心结论**：对于新手小白卖家，**平台 API 方案不可行**。推荐以 **AI 决策层保持不变 + 浏览器自动化 + CSV 文件** 为执行层的混合方案，从人工辅助逐步过渡到半自动化，最终在有 API 权限后实现全自动化。

---

> **本文档覆盖跨境电商 AI Agent 从技术架构到全流程业务模块的完整设计方案，可作为实际项目开发的起点参考文档。**

> 来源：
> - [LangChain 官方文档](https://docs.langchain.com)
> - [LangGraph 官方文档](https://docs.langchain.com/oss/python/langgraph)
> - [MCP 协议规范](https://modelcontextprotocol.io)
> - [TikTok Shop API](https://developers.tiktok-shops.com)
> - [Shopee Open Platform](https://open.shopee.com)
