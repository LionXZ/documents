# FastAPI 完全开发指南

> 从 0 到 1，从安装环境到生产部署，每一步都有详细配置和代码示例。零基础可跟着操作。

---

## 目录

- [一、FastAPI 概述](#一fastapi-概述)
- [二、环境准备](#二环境准备)
- [三、创建第一个 FastAPI 项目](#三创建第一个-fastapi-项目)
- [四、路由详解](#四路由详解)
- [五、请求体与数据校验](#五请求体与数据校验)
- [六、响应模型](#六响应模型)
- [七、文件上传](#七文件上传)
- [八、数据库操作](#八数据库操作)
  - [8.1 PyMySQL 原生 SQL](#81-pymysql-原生-sql)
  - [8.2 SQLAlchemy ORM](#82-sqlalchemy-orm)
  - [8.3 SQLModel](#83-sqlmodel)
- [九、用户认证 (JWT)](#九用户认证-jwt)
- [十、依赖注入](#十依赖注入)
- [十一、中间件](#十一中间件)
- [十二、错误处理](#十二错误处理)
- [十三、后台任务](#十三后台任务)
- [十四、流式响应 (SSE)](#十四流式响应-sse)
- [十五、CORS 跨域配置](#十五cors-跨域配置)
- [十六、测试](#十六测试)
- [十七、部署上线](#十七部署上线)

---

## 一、FastAPI 概述

**FastAPI** 是 Python 最快的 Web API 框架。它的设计哲学是：**写最少的代码，得最高的性能。**

### 1.1 架构模式

FastAPI 是纯粹的 API 框架，不包含模板引擎、ORM、表单系统——你需要什么就加什么：

```
客户端请求
    ↓
Uvicorn（ASGI 服务器，接收 HTTP）
    ↓
FastAPI 中间件层（CORS、日志、鉴权）
    ↓
路由匹配（URL → 函数）
    ↓
依赖注入（获取数据库连接、校验用户）
    ↓
业务处理（你的代码）
    ↓
返回 JSON 响应
```

### 1.2 核心特性

- **自动生成 API 文档**：`/docs` 是交互式 Swagger 文档，`/redoc` 是 ReDoc 文档，不需要额外配置
- **Pydantic 数据校验**：定义 Python 类，自动校验 JSON、生成文档
- **依赖注入**：公共逻辑（数据库连接、用户校验）抽成函数，路由声明即获得
- **异步支持**：`async def` 原生支持，性能媲美 Node.js + Go
- **类型安全**：基于 Python 类型提示，编辑器自动补全

### 1.3 与 Django 对比

| | Django | FastAPI |
|------|------|------|
| **类型** | 全栈框架（前后端都管） | API 框架（只管后端接口） |
| **ORM** | 内置 Django ORM | 自己选（SQLAlchemy/SQLModel/原生SQL） |
| **模板** | 内置模板引擎 | 不需要（前后端分离，前端用 Vue/React） |
| **Admin** | 自动生成后台 | 没有（前端写管理页面） |
| **性能** | 一般（同步框架） | 极高（异步，接近 Node.js） |
| **适用** | 内部系统、内容网站、快速原型 | API 服务、微服务、AI Agent 后端 |

---

## 二、环境准备

### 2.1 安装 Python

```bash
# macOS
brew install python@3.14

# Ubuntu
sudo apt install python3.12

# 确认版本 >= 3.10
python3 --version
```

### 2.2 创建项目目录

```bash
mkdir myapi
cd myapi
```

### 2.3 创建虚拟环境

```bash
# 创建 venv
python3 -m venv venv

# 激活（每次开发前都要执行）
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

# 确认 Python 指向 venv
which python
# 应该显示: /xxx/myapi/venv/bin/python
```

### 2.4 安装 FastAPI

```bash
pip install "fastapi[standard]"
```

`[standard]` 会同时安装 Uvicorn（ASGI 服务器）和其他推荐依赖。

> **为什么需要 Uvicorn？** FastAPI 本身是框架（类似 Django），它不监听端口。Uvicorn 是服务器（类似 Nginx），真正接收 HTTP 请求并转给 FastAPI 处理。两者必须一起用。

### 2.5 验证安装

```bash
python -c "import fastapi; print(fastapi.__version__)"
# 输出: 0.136.x
```

---

## 三、创建第一个 FastAPI 项目

### 3.1 最小项目

新建文件 `main.py`：

```python
from fastapi import FastAPI

app = FastAPI(
    title="我的第一个 API",
    version="1.0.0",
    description="一个 FastAPI 示例项目",
)


@app.get("/")
def root():
    return {"message": "Hello FastAPI!"}
```

### 3.2 启动服务

```bash
uvicorn main:app --reload --port 8000
```

| 参数 | 说明 |
|------|------|
| `main` | Python 文件名（`main.py`） |
| `app` | FastAPI 实例变量名 |
| `--reload` | **开发必备**，代码改动自动重启 |
| `--port 8000` | 监听端口 |

打开浏览器：
- `http://localhost:8000` → 你的接口
- `http://localhost:8000/docs` → Swagger 交互文档
- `http://localhost:8000/redoc` → ReDoc 文档

### 3.3 推荐的项目目录结构

```
myapi/
├── venv/                         # 虚拟环境（不提交 Git）
├── .env                          # 环境变量（不提交）
├── requirements.txt              # 依赖清单
├── main.py                       # 应用入口
├── src/
│   ├── __init__.py
│   ├── config.py                 # 配置（数据库连接、JWT 密钥等）
│   ├── database.py               # 数据库连接池
│   ├── models/                   # 数据库模型
│   │   ├── __init__.py
│   │   └── user.py
│   ├── schemas/                  # Pydantic 请求/响应模型
│   │   ├── __init__.py
│   │   └── user.py
│   ├── api/                      # 路由
│   │   ├── __init__.py
│   │   ├── router.py             # 主路由汇总
│   │   └── endpoints/
│   │       ├── __init__.py
│   │       └── user.py           # 用户相关端点
│   ├── services/                 # 业务逻辑
│   │   ├── __init__.py
│   │   └── user_service.py
│   └── utils/                    # 工具函数
│       └── security.py           # JWT 签发/验证
└── tests/                        # 测试
    ├── __init__.py
    └── test_user.py
```

> **为什么要分这么多目录？** 当项目有 10 个接口时，全写在一个 `main.py` 里还凑合。当项目有上百个接口时，不拆目录就是灾难。从一开始就按这个结构建，养成良好的习惯。

---

## 四、路由详解

路由是把 URL 映射到 Python 函数。FastAPI 通过装饰器实现。

### 4.1 HTTP 方法对照

| HTTP 方法 | 装饰器 | 用途 |
|------|------|------|
| GET | `@app.get` | 获取数据（查） |
| POST | `@app.post` | 新增数据（增） |
| PUT | `@app.put` | 全量更新（改全部字段） |
| PATCH | `@app.patch` | 部分更新（改部分字段） |
| DELETE | `@app.delete` | 删除数据（删） |

### 4.2 路径参数

路径参数是 URL 中用 `{}` 包起来的部分，如 `/users/123` 中的 `123`。FastAPI 通过函数参数名接收，并自动做类型转换。

```python
@app.get("/users/{user_id}")
def get_user(user_id: int):               # ← 声明类型为 int
    """
    访问 /users/123  → user_id = 123 (整数)
    访问 /users/abc  → 422 错误（abc 不是 int）
    """
    return {"user_id": user_id, "type": type(user_id).__name__}
```

常用类型：`int`、`str`、`float`、`bool`、`UUID`。

### 4.3 查询参数

URL 中 `?page=1&size=20` 中的 `page` 和 `size` 就是查询参数。不在路径声明，直接在函数参数中写即可——FastAPI 自动识别：URL 模板里有的 → 路径参数，模板里没有的 → 查询参数。

```python
@app.get("/search")
def search(
    q: str,                          # 必填（没有默认值 = 必填）
    page: int = 1,                   # 可选，默认值
    size: int = 20,
    sort: str | None = None,         # 可选，允许不传
    active: bool = True,
):
    return {"q": q, "page": page, "size": size}
```

### 4.4 APIRouter（按模块拆分路由）

当接口越来越多时，把路由按模块拆分到不同文件，用 `APIRouter` 管理：

```python
# src/api/endpoints/user.py
from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.get("/")                     # 实际路径: /users/
def list_users():
    return [{"id": 1, "name": "张三"}]


@router.post("/")                    # 实际路径: /users/
def create_user(name: str, email: str):
    return {"id": 2, "name": name, "email": email}


@router.get("/{user_id}")            # 实际路径: /users/123
def get_user(user_id: int):
    return {"id": user_id}
```

```python
# src/api/router.py — 汇总所有子路由
from fastapi import APIRouter
from src.api.endpoints import user

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(user.router)

# main.py — 挂载到主应用
from fastapi import FastAPI
from src.api.router import api_router

app = FastAPI()
app.include_router(api_router)
```

| 属性 | 说明 |
|------|------|
| `prefix="/users"` | 子路由的公共前缀 |
| `tags=["用户管理"]` | Swagger 文档中的分组名 |

### 4.5 请求体（POST/PUT/PATCH 的 JSON 数据）

GET 请求一般不需要请求体，POST/PUT/PATCH 才需要。用 Pydantic 定义接收的 JSON 结构：

```python
from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    """创建用户的请求体"""
    username: str = Field(min_length=2, max_length=30, description="用户名")
    email: str = Field(pattern=r"^\S+@\S+\.\S+$", description="邮箱")
    password: str = Field(min_length=6, description="密码，至少 6 位")
    age: int | None = Field(default=None, ge=0, le=150, description="年龄可选")


@app.post("/users")
def create_user(user: UserCreate):       # ← 声明类型，FastAPI 自动校验
    # 此时 user 已经是校验后的对象，直接使用
    print(user.username)                  # str
    print(user.email)                     # str，格式已校验
    return {"username": user.username, "email": user.email}
```

**如果客户端传了错误数据会怎样？** 比如 `username` 只有 1 个字符，FastAPI 自动返回 422 状态码和详细的错误信息，你不需要写任何判断。

### 4.6 路由优先级

FastAPI 按代码**定义顺序**匹配路由。更具体的路由要定义在前面：

```python
@app.get("/users/me")           # ← 先定义具体路径
def get_current_user():
    return {"name": "我"}

@app.get("/users/{user_id}")    # ← 再定义通配路径
def get_user(user_id: int):
    return {"id": user_id}

# 请求 /users/me → 匹配第一个（正确）
# 如果把 /users/{user_id} 放前面 → "me" 会被当成 user_id（错误！）
```

---

## 五、请求体与数据校验

Pydantic 是 FastAPI 数据校验的核心。你定义 Python 类，FastAPI 自动：校验 JSON 字段 → 转换类型 → 生成 Swagger 文档。

### 5.1 基础校验

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ProductCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
        description="商品名称",
    )
    price: float = Field(
        gt=0,                                    # 必须大于 0
        description="价格",
    )
    stock: int = Field(
        ge=0,                                    # 大于等于 0
        default=0,                               # 默认值
    )
    tags: list[str] = []
    is_active: bool = True
    published_at: datetime | None = None
```

| Field 参数 | 含义 |
|------|------|
| `min_length` / `max_length` | 字符串长度限制 |
| `gt` / `ge` / `lt` / `le` | 大于 / 大于等于 / 小于 / 小于等于 |
| `pattern` | 正则匹配 |
| `default` | 默认值 |
| `description` | Swagger 文档中的说明 |

### 5.2 自定义校验

Field 不够用时，用 `@field_validator` 写自定义校验逻辑：

```python
from pydantic import field_validator


class UserCreate(BaseModel):
    username: str
    password: str
    password_confirm: str

    @field_validator("username")
    def username_no_space(cls, v: str):
        """用户名不能包含空格"""
        if " " in v:
            raise ValueError("用户名不能包含空格")
        return v.strip()

    @field_validator("password_confirm")
    def passwords_match(cls, v: str, info):
        """两次输入的密码必须一致"""
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("两次输入的密码不一致")
        return v
```

### 5.3 嵌套模型

请求体中的嵌套 JSON 对象，对应嵌套 Pydantic 类：

```python
class Address(BaseModel):
    city: str
    street: str
    zip_code: str

class UserCreate(BaseModel):
    name: str
    addresses: list[Address]    # ← 嵌套数组


# 客户端传:
# {
#   "name": "张三",
#   "addresses": [
#     {"city": "北京", "street": "长安街", "zip_code": "100000"},
#     {"city": "上海", "street": "南京路", "zip_code": "200000"}
#   ]
# }
```

---

## 六、响应模型

### 6.1 控制返回字段

`response_model` 决定客户端收到什么字段。数据库查出来的对象可能有很多字段（密码、内部状态），用 `response_model` 可以只返回想要的部分。

```python
class UserResponse(BaseModel):
    """返回给客户端的用户数据（不含密码）"""
    id: int
    username: str
    email: str

@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate):
    # 数据库返回的对象可能还有 password、is_deleted 等字段
    # response_model 会自动过滤，只返回 id、username、email
    saved_user = save_to_database(user)
    return saved_user
```

### 6.2 排除和包含字段

```python
# 排除密码
@app.get("/users/{id}", response_model=UserCreate, response_model_exclude={"password"})

# 只要这两个字段
@app.get("/users/{id}", response_model=UserCreate, response_model_include={"username", "email"})
```

---

## 七、文件上传

### 7.1 单文件上传

```python
from fastapi import UploadFile, File

@app.post("/upload")
async def upload_file(file: UploadFile = File()):
    # 大文件建议分块读，避免内存溢出
    with open(f"uploads/{file.filename}", "wb") as f:
        while chunk := await file.read(1024 * 1024):  # 每次读 1MB
            f.write(chunk)
    return {
        "filename": file.filename,
        "content_type": file.content_type,
    }
```

### 7.2 多文件上传

```python
@app.post("/upload-multi")
async def upload_files(files: list[UploadFile] = File()):
    result = []
    for file in files:
        content = await file.read()
        result.append({"name": file.filename, "size": len(content)})
    return {"uploaded": result}
```

### 7.3 文件 + 表单混合

```python
@app.post("/profile")
async def create_profile(
    name: str = Form(),              # ← 普通表单字段
    age: int = Form(),
    avatar: UploadFile = File(),     # ← 文件字段
):
    avatar_bytes = await avatar.read()
    return {"name": name, "age": age, "avatar_size": len(avatar_bytes)}
```

---

## 八、数据库操作

FastAPI 不带 ORM，你需要自己选数据库方案。三种主流方式：

| 方案 | 适合场景 | 学习成本 |
|------|------|------|
| PyMySQL 原生 SQL | 复杂查询、报表、有 SQL 基础 | 低 |
| SQLAlchemy ORM | 大型项目、复杂关联 | 中 |
| SQLModel | 新 FastAPI 项目、想要最简写法 | 低 |

### 8.1 PyMySQL 原生 SQL

#### 8.1.1 安装

```bash
pip install pymysql dbutils
```

#### 8.1.2 配置连接池

生产环境**必须**用连接池，否则每次请求新建连接会把 MySQL 打爆。`DBUtils.PooledDB` 是 Python 最成熟的连接池。

```python
# src/database.py
import pymysql
from dbutils.pooled_db import PooledDB
from contextlib import contextmanager
from src.config import settings

# 应用启动时创建一次连接池（全局单例）
POOL = PooledDB(
    creator=pymysql,
    maxconnections=10,       # 最大连接数
    mincached=2,             # 启动时预创建的空闲连接
    blocking=True,           # 连接用完时等待（不报错）
    host=settings.DB_HOST,
    port=settings.DB_PORT,
    user=settings.DB_USER,
    password=settings.DB_PASSWORD,
    database=settings.DB_NAME,
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor,  # 返回字典而非元组
    autocommit=False,        # 手动提交（控制事务）
)


@contextmanager
def get_db():
    """
    获取数据库连接。用 with 语句，自动提交或回滚。

    用法:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT ...")
    """
    conn = POOL.connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
```

| 参数 | 为什么这么设置 |
|------|------|
| `maxconnections=10` | 防连接数爆炸，超出后请求等待 |
| `blocking=True` | 等待好过直接报错 |
| `autocommit=False` | 手动控制：写入多张表要保证一起成功或一起回滚 |
| `cursorclass=DictCursor` | 返回 `{"id": 1, "name": "张三"}` 而非 `(1, "张三")` |

#### 8.1.3 配置类

```python
# src/config.py
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # 数据库
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "mydb")

    # JWT
    JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")
    JWT_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", "72"))


settings = Settings()
```

#### 8.1.4 场景 1：创建用户（INSERT + 防注入）

**需求**：接收用户名和密码，写入数据库。密码用 bcrypt 哈希存储。

```bash
pip install bcrypt
```

```python
# src/api/endpoints/user.py
import bcrypt
from fastapi import APIRouter, HTTPException
from src.database import get_db

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.post("/")
def create_user(username: str, password: str):
    # 密码不能存明文！bcrypt 是单向哈希，即使数据库泄露密码也不可见
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    with get_db() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    "INSERT INTO users (username, password) VALUES (%s, %s)",
                    (username, hashed),       # ← 参数化查询防注入
                )
                return {"id": cur.lastrowid, "username": username}
            except pymysql.IntegrityError:
                raise HTTPException(status_code=400, detail="用户名已存在")
```

> **参数化查询为什么能防注入？** `%s` 不是字符串拼接，是 SQL 参数占位符。PyMySQL 会把 `username` 作为**数据**传给 MySQL，而不是作为**SQL 语句的一部分**。攻击者输入 `'; DROP TABLE users; --` 会被当作普通字符串处理，不会被执行。

#### 8.1.5 场景 2：用户列表 + 搜索 + 分页

**需求**：分页查询用户，支持按用户名搜索。

```python
@router.get("/")
def list_users(
    keyword: str = None,         # 搜索关键词
    page: int = 1,               # 页码
    size: int = 20,              # 每页条数
):
    with get_db() as conn:
        with conn.cursor() as cur:
            # 构建 SQL
            sql = "SELECT id, username, email, created_at FROM users WHERE 1=1"
            params = []

            if keyword:
                sql += " AND username LIKE %s"
                params.append(f"%{keyword}%")

            sql += " ORDER BY id DESC LIMIT %s OFFSET %s"
            params.extend([size, (page - 1) * size])

            cur.execute(sql, params)
            rows = cur.fetchall()

            # 查总数
            count_sql = "SELECT COUNT(*) as total FROM users"
            if keyword:
                count_sql += " WHERE username LIKE %s"
                cur.execute(count_sql, (f"%{keyword}%",))
            else:
                cur.execute(count_sql)
            total = cur.fetchone()["total"]

    return {
        "data": rows,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size,
    }
```

#### 8.1.6 场景 3：订单 + 库存扣减（事务）

**需求**：创建订单需要同时插入订单表、明细表、扣减库存。三步必须全部成功或全部回滚。

```python
@router.post("/orders")
def create_order(user_id: int, items: list[dict]):
    """
    items = [{"product_id": 1, "quantity": 2, "price": 99}, ...]
    """
    with get_db() as conn:
        with conn.cursor() as cur:
            # 1. 插入订单
            cur.execute(
                "INSERT INTO orders (user_id) VALUES (%s)", (user_id,)
            )
            order_id = cur.lastrowid

            # 2. 插入明细
            for item in items:
                cur.execute(
                    "INSERT INTO order_items (order_id, product_id, quantity, price) "
                    "VALUES (%s, %s, %s, %s)",
                    (order_id, item["product_id"], item["quantity"], item["price"]),
                )

            # 3. 扣库存
            for item in items:
                cur.execute(
                    "UPDATE products SET stock = stock - %s WHERE id = %s AND stock >= %s",
                    (item["quantity"], item["product_id"], item["quantity"]),
                )
                if cur.rowcount == 0:
                    raise HTTPException(status_code=400, detail=f"商品 {item['product_id']} 库存不足")

        # with 正常结束 → commit
    # 任何异常 → rollback（连接池自动处理）
    return {"order_id": order_id}
```

---

### 8.2 SQLAlchemy ORM

> ORM（Object-Relational Mapping）把数据库表映射成 Python 类，用操作对象的方式操作数据。不用手写 SQL，换数据库只改连接字符串。

#### 8.2.1 安装

```bash
pip install sqlalchemy alembic pymysql
```

#### 8.2.2 创建引擎和会话工厂

```python
# src/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_engine(
    "mysql+pymysql://root:123456@localhost:3306/mydb?charset=utf8mb4",
    pool_size=10,               # 连接池大小
    max_overflow=20,            # 高峰期额外连接
    pool_recycle=3600,          # 连接超过 1 小时自动重连
    echo=False,                 # True 的话会打印每条 SQL（调试用）
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
```

#### 8.2.3 定义数据模型

```python
# src/models/user.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from src.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(30), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

    articles = relationship("Article", back_populates="author")   # 关联


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, default="")
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.now)

    author = relationship("User", back_populates="articles")
```

#### 8.2.4 获取 Session 的依赖

```python
# src/deps.py
from fastapi import Depends
from sqlalchemy.orm import Session
from src.database import SessionLocal


def get_session():
    """每个请求获取独立的数据库会话，请求结束自动关闭"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
```

#### 8.2.5 完整 CRUD

```python
# src/api/endpoints/article.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from src.deps import get_session
from src.models.user import Article

router = APIRouter(prefix="/articles", tags=["文章管理"])


@router.get("/")
def list_articles(
    status: str = None,
    keyword: str = None,
    page: int = 1,
    size: int = 20,
    session: Session = Depends(get_session),
):
    query = session.query(Article)

    if status:
        query = query.filter(Article.status == status)
    if keyword:
        query = query.filter(
            or_(
                Article.title.like(f"%{keyword}%"),
                Article.content.like(f"%{keyword}%"),
            )
        )

    total = query.count()
    articles = (
        query
        .options(joinedload(Article.author))    # 一次 JOIN 查出作者
        .order_by(Article.id.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    return {
        "data": [{"id": a.id, "title": a.title, "author": a.author.username} for a in articles],
        "total": total,
        "page": page,
    }


@router.post("/")
def create_article(title: str, content: str, author_id: int,
                   session: Session = Depends(get_session)):
    article = Article(title=title, content=content, author_id=author_id)
    session.add(article)
    session.commit()
    session.refresh(article)
    return {"id": article.id, "title": article.title}


@router.put("/{article_id}")
def update_article(article_id: int, title: str = None, content: str = None,
                   session: Session = Depends(get_session)):
    article = session.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    if title is not None:
        article.title = title
    if content is not None:
        article.content = content
    session.commit()
    return {"id": article.id, "title": article.title}


@router.delete("/{article_id}")
def delete_article(article_id: int, session: Session = Depends(get_session)):
    article = session.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    session.delete(article)
    session.commit()
    return {"deleted": article_id}
```

#### 8.2.6 数据库迁移（Alembic）

```bash
# 1. 初始化（一次）
alembic init alembic

# 2. 编辑 alembic/env.py，找到 target_metadata = None，改成：
#    from src.database import Base
#    from src.models import user   # 导入所有模型
#    target_metadata = Base.metadata

# 3. 生成迁移文件
alembic revision --autogenerate -m "init"

# 4. 执行迁移
alembic upgrade head

# 5. 回退
alembic downgrade -1
```

---

### 8.3 SQLModel

`SQLModel` 是 FastAPI 作者做的 ORM，把 SQLAlchemy 和 Pydantic 合并成一个类——定义一次，校验 + ORM 都有了。

```bash
pip install sqlmodel
```

```python
from sqlmodel import SQLModel, Field, Session, create_engine, select
from typing import Optional
from datetime import datetime


class User(SQLModel, table=True):
    """这一个类 = 数据库表定义 + Pydantic 校验 + JSON Schema 文档"""
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, max_length=30)
    email: str = Field(unique=True)
    created_at: datetime = Field(default_factory=datetime.now)


engine = create_engine("mysql+pymysql://root:123456@localhost:3306/mydb?charset=utf8mb4")

# 根据模型自动建表（开发用，生产用 Alembic）
SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


@app.get("/users", response_model=list[User])
def list_users(session: Session = Depends(get_session)):
    return session.exec(select(User)).all()    # ← 直接返回 Pydantic 对象
```

---

## 九、用户认证 (JWT)

JWT（JSON Web Token）是当下最主流的 API 认证方案。核心思想：服务端签发一个加密的 token，客户端每次请求带上，服务端解密验证。

### 9.1 工作原理

```
1. 用户登录 → 服务端校验密码 → 返回一个 JWT token
2. 客户端存下 token
3. 后续请求在 Authorization 头里带上: Bearer <token>
4. 服务端解密 token → 取出 user_id → 执行请求
```

### 9.2 签发 Token

```bash
pip install pyjwt
```

```python
# src/utils/security.py
import jwt
from datetime import datetime, timedelta, timezone
from src.config import settings

ALGORITHM = "HS256"


def create_token(user_id: int) -> str:
    """生成 JWT Token，有效期从配置读取"""
    payload = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRE_HOURS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """解密 Token，无效或过期抛出异常"""
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
```

### 9.3 验证 Token（FastAPI 依赖）

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """从请求头提取 Bearer Token 并验证"""
    try:
        payload = decode_token(credentials.credentials)
        # 这里可以查数据库验证用户是否存在
        return {"user_id": payload["user_id"]}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token 已过期，请重新登录")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token 无效")


# 使用：声明后自动获得当前用户
@app.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return {"user_id": current_user["user_id"]}
```

### 9.4 完整登录流程

```python
import bcrypt
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register")
def register(username: str, email: str, password: str):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    with get_db() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                    (username, email, hashed),
                )
            except pymysql.IntegrityError:
                raise HTTPException(status_code=400, detail="用户名或邮箱已存在")
    return {"id": cur.lastrowid, "username": username}


@router.post("/login")
def login(username: str, password: str):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, password FROM users WHERE username = %s", (username,))
            user = cur.fetchone()

    if not user or not bcrypt.checkpw(password.encode(), user["password"].encode()):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    token = create_token(user["id"])
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    return {"user_id": current_user["user_id"]}
```

---

## 十、依赖注入

`Depends` 是 FastAPI 最强大的功能。任何需要复用的逻辑都可以抽成依赖函数，路由声明即用。

### 10.1 为什么需要依赖注入

```python
# ❌ 每个接口都要重复这段代码
@app.get("/users")
def list_users():
    with get_db() as conn:
        with conn.cursor() as cur:
            return cur.fetchall()

# ✅ 用 Depends 抽成公共逻辑
@app.get("/users")
def list_users(conn=Depends(get_db)):
    with conn.cursor() as cur:
        return cur.fetchall()
```

### 10.2 依赖链

一个依赖可以依赖另一个依赖，形成链式结构：

```python
def get_db():
    """连接数据库"""
    ...

def get_repo(db=Depends(get_db)):
    """获取数据访问层"""
    return UserRepository(db)

def get_current_user(token=Depends(security)):
    """校验登录状态"""
    return decode(token)

@app.post("/orders")
def create_order(
    user=Depends(get_current_user),    # 校验登录
    repo=Depends(get_repo),            # 数据访问
    items: list[OrderItem],            # 请求体
):
    # 函数体里只需要写业务逻辑
    return repo.create_order(user["id"], items)
```

### 10.3 带参数的依赖

```python
def pagination(page: int = 1, size: int = 20):
    return {"skip": (page - 1) * size, "limit": size}

@app.get("/items")
def list_items(pager: dict = Depends(pagination), db=Depends(get_db)):
    return query(db).offset(pager["skip"]).limit(pager["limit"]).all()
```

---

## 十一、中间件

中间件在请求到达路由函数**之前**和**之后**执行，适合横切关注点（日志、计时、鉴权）。

```python
import time
from fastapi import Request


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录每个请求的处理时间"""
    start = time.time()

    response = await call_next(request)      # ← 这里才真正执行路由

    elapsed = time.time() - start
    response.headers["X-Process-Time"] = str(elapsed)

    if elapsed > 1.0:                        # 慢请求告警
        print(f"⚠ 慢请求: {request.method} {request.url.path} ({elapsed:.2f}s)")

    return response
```

---

## 十二、错误处理

### 12.1 手动抛异常

任何时候判断到错误情况，`raise HTTPException` 即可：

```python
from fastapi import HTTPException


@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id < 1:
        raise HTTPException(status_code=400, detail="ID 必须大于 0")

    item = find_in_db(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="商品不存在")

    return item
```

### 12.2 全局异常兜底

```python
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """任何未捕获的异常都返回 500，不暴露内部细节"""
    return JSONResponse(status_code=500, content={"detail": "服务器内部错误"})
```

---

## 十三、后台任务

发邮件、写日志这类操作不需要立即返回结果，用 `BackgroundTasks`：

```python
from fastapi import BackgroundTasks


def send_welcome_email(email: str):
    """连接 SMTP 发送邮件，5 秒完成"""
    time.sleep(5)
    print(f"已发送欢迎邮件给 {email}")


@app.post("/register")
def register(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_welcome_email, email)
    return {"message": "注册成功"}       # ← 立即返回，邮件后台发送
```

---

## 十四、流式响应 (SSE)

AI 对话需要逐字输出，用 `StreamingResponse` + `text/event-stream`：

```python
from fastapi.responses import StreamingResponse
import asyncio
import json


@app.post("/chat/stream")
async def chat_stream(message: str):
    async def generate():
        # 模拟 AI 逐字生成
        words = ["你好", "，", "我是", "AI", "助手"]
        for word in words:
            await asyncio.sleep(0.3)
            yield f"data: {json.dumps(word)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",      # Nginx 不缓冲
        },
    )
```

---

## 十五、CORS 跨域配置

前后端分离时，前端（`localhost:3000`）请求后端（`localhost:8000`）会被浏览器拦截——这就是跨域。

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",          # 开发环境
        "https://your-app.com",           # 生产环境
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

| 参数 | 说明 |
|------|------|
| `allow_origins` | 允许哪些前端域名 |
| `allow_credentials` | 是否允许携带 Cookie/Authorization |
| `allow_methods` | 允许哪些 HTTP 方法 |
| `allow_headers` | 允许哪些请求头 |

---

## 十六、测试

FastAPI 自带 `TestClient`，不需要启动真实服务器就能测。

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_login_success():
    response = client.post("/auth/login", json={"username": "admin", "password": "123456"})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_failure():
    response = client.post("/auth/login", json={"username": "admin", "password": "wrong"})
    assert response.status_code == 401


def test_protected_route():
    # 先登录获取 token
    login_resp = client.post("/auth/login", json={"username": "admin", "password": "123456"})
    token = login_resp.json()["access_token"]

    # 带 token 请求受保护接口
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


def test_validation():
    response = client.post("/users/", json={"username": "a", "password": "12"})
    assert response.status_code == 422    # 用户名太短 + 密码太短
```

运行：

```bash
pip install pytest
pytest tests/ -v
```

---

## 十七、部署上线

### 17.1 生产启动命令

开发时用 `--reload`，生产环境**必须关掉**。

```bash
# 单进程
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1

# 多进程（仅 Linux。macOS/Windows 用 1 个 worker）
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 17.2 Gunicorn + Uvicorn（推荐 Linux 生产方案）

Gunicorn 管理多个 Uvicorn 进程，自动重启崩溃的进程。

```bash
pip install gunicorn

gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

### 17.3 systemd 服务（开机自启 + 崩溃重启）

创建服务文件，让系统自动管理进程：

```ini
# /etc/systemd/system/myapi.service
[Unit]
Description=My FastAPI App
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/myapi
ExecStart=/opt/myapi/venv/bin/gunicorn main:app \
    -w 4 \
    -k uvicorn.workers.UvicornWorker \
    -b 127.0.0.1:8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload       # 加载服务文件
sudo systemctl enable myapi        # 开机自启
sudo systemctl start myapi         # 立即启动
sudo systemctl status myapi        # 查看状态
sudo journalctl -u myapi -f        # 查看日志
```

### 17.4 Nginx 反代

Node 80/443 端口需要 root 权限。用 Nginx 监听 80/443，反向代理到内部 8000 端口：

```nginx
server {
    listen 80;
    server_name api.example.com;

    client_max_body_size 50M;       # 允许上传大文件

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /chat/stream {
        proxy_pass http://127.0.0.1:8000;
        proxy_buffering off;        # SSE 必须关缓冲
        proxy_cache off;
        proxy_read_timeout 300s;    # 长连接超时
    }
}
```

### 17.5 Docker

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# 先复制依赖文件（利用 Docker 缓存层）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 再复制源码
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t myapi .
docker run -d -p 8000:8000 --env-file .env myapi
```

### 17.6 部署检查清单

| 检查项 | 说明 |
|------|------|
| `.env` 已创建且有生产配置 | 数据库密码、JWT_SECRET 用生产值 |
| `--reload` 已移除 | 生产环境不允许热重载 |
| DEBUG=False | 不暴露错误细节 |
| CORS `allow_origins` 改为生产域名 | 不再允许 `*` |
| Nginx 已配置 | 80/443 → 8000 |
| HTTPS 已开启 | Let's Encrypt 免费证书 |
| systemd 已启用 | 崩溃自动重启 |

---

> **来源：**
> - [FastAPI 官方文档](https://fastapi.tiangolo.com/)
> - [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
> - [SQLModel 文档](https://sqlmodel.tiangolo.com/)
> - [Uvicorn 文档](https://www.uvicorn.org/)
> - [Gunicorn 文档](https://docs.gunicorn.org/)
