# FastAPI 速查手册

> 一份 Python 代码驱动的 FastAPI 文档，覆盖从入门到生产部署的常用场景，适合快速查阅和实战。

---

## 目录

- [1. 安装与启动](#1-安装与启动)
- [2. 基础路由](#2-基础路由)
- [3. 路径参数](#3-路径参数)
- [4. 查询参数](#4-查询参数)
- [5. 请求体 (Pydantic)](#5-请求体-pydantic)
- [6. 响应模型](#6-响应模型)
- [7. 表单与文件上传](#7-表单与文件上传)
- [8. 中间件](#8-中间件)
- [9. 依赖注入](#9-依赖注入)
- [10. JWT 认证](#10-jwt-认证)
- [11. 后台任务](#11-后台任务)
- [12. 流式响应 (SSE)](#12-流式响应-sse)
- [13. WebSocket](#13-websocket)
- [14. 错误处理](#14-错误处理)
- [15. CORS 配置](#15-cors-配置)
- [16. 生命周期事件](#16-生命周期事件)
- [17. 测试](#17-测试)
- [18. 部署](#18-部署)

---

## 1. 安装与启动

### 1.1 安装

```bash
pip install fastapi uvicorn[standard]
```

### 1.2 最小应用

```python
# main.py
from fastapi import FastAPI

app = FastAPI(title="My API", version="1.0.0")


@app.get("/")
def root():
    return {"message": "Hello World"}
```

### 1.3 启动

```bash
uvicorn main:app --reload --port 8000
# main = 文件名, app = FastAPI 实例名
```

打开 `http://localhost:8000/docs` 查看自动生成的 Swagger 文档。

---

## 2. 基础路由

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/items")
def get_items():
    return [{"id": 1, "name": "Item A"}]


@app.post("/items")
def create_item():
    return {"message": "创建成功"}


@app.put("/items/{item_id}")
def update_item(item_id: int):
    return {"message": f"更新 {item_id}"}


@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    return {"message": f"删除 {item_id}"}


@app.patch("/items/{item_id}")
def patch_item(item_id: int):
    return {"message": f"部分更新 {item_id}"}


@app.head("/health")
def health_check():
    return {}  # 只返回 header, 无 body


@app.options("/items")
def items_options():
    return {"methods": ["GET", "POST"]}
```

### 路由前缀

```python
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["items"])


@router.get("/items")
def list_items():
    return [{"name": "A"}]


@router.post("/items")
def create_item():
    return {"ok": True}


# 挂载到主应用
app.include_router(router)
```

---

## 3. 路径参数

```python
@app.get("/users/{user_id}")
def get_user(user_id: int):           # 自动类型转换
    return {"user_id": user_id}


@app.get("/files/{file_path:path}")   # 匹配 /files/home/foo.txt
def read_file(file_path: str):
    return {"path": file_path}


# 枚举约束
from enum import Enum

class Color(str, Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"

@app.get("/colors/{color}")
def get_color(color: Color):
    return {"color": color.value}
```

---

## 4. 查询参数

```python
from typing import Optional

@app.get("/search")
def search(
    q: str,                         # 必填
    page: int = 1,                  # 可选，默认值
    size: int = 10,
    sort: Optional[str] = None,     # 可选，允许 None
    active: bool = True,
    tags: list[str] = [],           # ?tags=a&tags=b → ["a", "b"]
):
    return {"q": q, "page": page, "size": size}
```

```bash
curl "http://localhost:8000/search?q=python&page=2&tags=a&tags=b"
```

---

## 5. 请求体 (Pydantic)

```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100, description="商品名称")
    price: float = Field(gt=0, description="价格")
    tags: list[str] = []
    is_active: bool = True

    # 自定义校验
    @field_validator("price")
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("价格必须大于 0")
        return round(v, 2)

    # 示例值 (Swagger 显示)
    model_config = {
        "json_schema_extra": {
            "example": {"name": "Python书", "price": 59.9, "tags": ["编程"]}
        }
    }


class ItemResponse(BaseModel):
    id: int
    name: str
    price: float
    created_at: datetime


# 使用
@app.post("/items", response_model=ItemResponse, status_code=201)
def create_item(item: ItemCreate):
    # item 已经被校验和转换
    return {
        "id": 1,
        "name": item.name,
        "price": item.price,
        "created_at": datetime.now(),
    }
```

### 嵌套模型

```python
class Address(BaseModel):
    city: str
    street: str


class UserCreate(BaseModel):
    name: str
    addresses: list[Address]  # 嵌套数组


# 请求体示例:
# {
#   "name": "张三",
#   "addresses": [
#     {"city": "北京", "street": "长安街"},
#     {"city": "上海", "street": "南京路"}
#   ]
# }
```

---

## 6. 响应模型

```python
@app.get("/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: int):
    # 返回的数据会被自动过滤，只保留 response_model 定义的字段
    return {"id": item_id, "name": "xxx", "price": 99, "internal": "secret"}


# 排除某些字段
@app.get("/users/{user_id}", response_model=UserCreate, response_model_exclude={"password"})
def get_user(user_id: int):
    ...


# 只包含某些字段
@app.get("/users/{user_id}", response_model=UserCreate, response_model_include={"name", "email"})
def get_user(user_id: int):
    ...


# 联合返回类型
from typing import Union

@app.get("/result", response_model=Union[ItemResponse, dict])
def get_result(flag: bool):
    if flag:
        return ItemResponse(id=1, name="A", price=10, created_at=datetime.now())
    return {"msg": "not found"}
```

---

## 7. 表单与文件上传

### 7.1 表单

```python
from fastapi import Form

@app.post("/login")
def login(username: str = Form(), password: str = Form()):
    return {"username": username}
```

### 7.2 单文件上传

```python
from fastapi import UploadFile, File

@app.post("/upload")
async def upload_file(file: UploadFile = File()):
    content = await file.read()
    with open(f"uploads/{file.filename}", "wb") as f:
        f.write(content)
    return {
        "filename": file.filename,
        "size": len(content),
        "content_type": file.content_type,
    }
```

### 7.3 多文件上传

```python
from typing import List

@app.post("/upload-multi")
async def upload_files(files: List[UploadFile] = File()):
    results = []
    for file in files:
        content = await file.read()
        results.append({"filename": file.filename, "size": len(content)})
    return {"files": results}
```

### 7.4 文件 + 表单混合

```python
@app.post("/profile")
async def create_profile(
    name: str = Form(),
    age: int = Form(),
    avatar: UploadFile = File(),
):
    avatar_content = await avatar.read()
    return {"name": name, "age": age, "avatar_size": len(avatar_content)}
```

---

## 8. 中间件

```python
import time
from fastapi import Request

# 8.1 计时中间件
@app.middleware("http")
async def add_process_time(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    response.headers["X-Process-Time"] = str(time.time() - start)
    return response


# 8.2 自定义中间件类
from starlette.middleware.base import BaseHTTPMiddleware

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 请求前
        token = request.headers.get("Authorization")
        if not token:
            request.state.user = None

        response = await call_next(request)

        # 响应后
        response.headers["X-Powered-By"] = "FastAPI"
        return response


app.add_middleware(AuthMiddleware)
```

---

## 9. 依赖注入

```python
from fastapi import Depends

# 9.1 简单依赖
def get_db():
    db = create_connection()
    try:
        yield db
    finally:
        db.close()


@app.get("/items")
def list_items(db=Depends(get_db)):
    return db.query("SELECT * FROM items")


# 9.2 带参数的依赖
def pagination(page: int = 1, size: int = 10):
    return {"page": page, "size": size, "offset": (page - 1) * size}


@app.get("/articles")
def list_articles(pager: dict = Depends(pagination)):
    return pager


# 9.3 子依赖 (依赖链)
def get_db():
    ...

def get_repo(db=Depends(get_db)):
    return UserRepository(db)


@app.post("/users")
def create_user(user_data: UserCreate, repo=Depends(get_repo)):
    return repo.create(user_data)


# 9.4 全局依赖 (所有路由自动注入)
from fastapi import Security

# app = FastAPI(dependencies=[Depends(verify_token)])  # 方式1
```

---

## 10. JWT 认证

```python
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

SECRET = "your-secret-key"
ALGORITHM = "HS256"
security = HTTPBearer()


def create_token(user_id: int) -> str:
    return jwt.encode(
        {
            "user_id": user_id,
            "exp": datetime.now(timezone.utc) + timedelta(hours=72),
        },
        SECRET,
        algorithm=ALGORITHM,
    )


def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET, algorithms=[ALGORITHM])


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    try:
        payload = decode_token(credentials.credentials)
        return {"user_id": payload["user_id"]}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token 已过期")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token 无效")


# 使用认证依赖
@app.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return {"user_id": current_user["user_id"]}


@app.post("/login")
def login(username: str, password: str):
    # 校验用户...
    token = create_token(user_id=1)
    return {"access_token": token, "token_type": "bearer"}
```

---

## 11. 后台任务

```python
from fastapi import BackgroundTasks


def send_email(to: str, subject: str):
    # 耗时操作，不阻塞响应
    import time
    time.sleep(3)
    print(f"邮件已发送给 {to}")


@app.post("/register")
def register(email: str, background_tasks: BackgroundTasks):
    # 注册逻辑...
    background_tasks.add_task(send_email, email, "欢迎注册")
    return {"message": "注册成功，邮件稍后发送"}


# 多个后台任务
background_tasks.add_task(send_email, email, "欢迎")
background_tasks.add_task(send_notification, user_id)
```

---

## 12. 流式响应 (SSE)

```python
from fastapi.responses import StreamingResponse
import asyncio
import json


async def generate_numbers():
    for i in range(10):
        await asyncio.sleep(0.5)
        yield f"data: {json.dumps({'num': i})}\n\n"
    yield "data: [DONE]\n\n"


@app.get("/stream")
def stream_numbers():
    return StreamingResponse(
        generate_numbers(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # 禁用 Nginx 缓冲
        },
    )


# 流式对话 (类似 ChatGPT)
@app.post("/chat/stream")
async def chat_stream(message: str):
    async def generate():
        try:
            async for chunk in call_llm_stream(message):
                yield f"data: {json.dumps(chunk)}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
```

---

## 13. WebSocket

```python
from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active_connections.append(ws)

    def disconnect(self, ws: WebSocket):
        self.active_connections.remove(ws)

    async def broadcast(self, message: str):
        for ws in self.active_connections:
            await ws.send_text(message)


manager = ConnectionManager()


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(ws: WebSocket, client_id: str):
    await manager.connect(ws)
    try:
        while True:
            data = await ws.receive_text()
            await manager.broadcast(f"Client {client_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(ws)
        await manager.broadcast(f"Client {client_id} 离开了")
```

---

## 14. 错误处理

```python
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


# 14.1 抛异常
@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id < 1:
        raise HTTPException(status_code=404, detail="商品不存在")
    return {"id": item_id}


# 14.2 自定义异常处理器
class BusinessException(Exception):
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code


@app.exception_handler(BusinessException)
async def business_exception_handler(request, exc: BusinessException):
    return JSONResponse(
        status_code=exc.code,
        content={"detail": exc.message, "error_code": exc.code},
    )


# 14.3 覆盖默认校验异常
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "detail": "参数校验失败",
            "errors": exc.errors(),
        },
    )


# 14.4 全局 500 兜底
@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "服务器内部错误"},
    )


# 使用自定义异常
@app.get("/danger")
def dangerous():
    raise BusinessException("余额不足", code=402)
```

---

## 15. CORS 配置

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://myapp.com"],
    allow_credentials=True,
    allow_methods=["*"],              # GET, POST, PUT, DELETE...
    allow_headers=["*"],              # Content-Type, Authorization...
    expose_headers=["X-Process-Time"],
    max_age=3600,                     # 预检缓存时间
)
```

---

## 16. 生命周期事件

```python
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时
    print("服务启动中...")
    await init_database()
    await load_models()

    yield  # ← 服务运行中

    # 关闭时
    print("服务关闭中...")
    await close_database()


app = FastAPI(lifespan=lifespan)
```

---

## 17. 测试

```python
from fastapi.testclient import TestClient

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


def test_create_item():
    response = client.post("/items", json={"name": "Test", "price": 99})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test"


def test_with_auth():
    # 带认证头的测试
    response = client.get(
        "/me",
        headers={"Authorization": "Bearer test-token"},
    )
    assert response.status_code == 200


def test_not_found():
    response = client.get("/items/99999")
    assert response.status_code == 404


def test_validation_error():
    response = client.post("/items", json={"name": "", "price": -1})
    assert response.status_code == 422
```

运行：

```bash
pytest test_main.py -v
```

---

## 18. 部署

### 18.1 Uvicorn 生产命令

```bash
uvicorn main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \           # 多进程 (Linux)
  --log-level info \
  --no-access-log          # 关闭访问日志 (Nginx 处理)
```

### 18.2 Gunicorn + Uvicorn (推荐 Linux)

```bash
pip install gunicorn

gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

### 18.3 systemd 服务

```ini
# /etc/systemd/system/myapp.service
[Unit]
Description=My FastAPI App
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/myapp
ExecStart=/opt/myapp/venv/bin/gunicorn main:app \
    -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000
Restart=always
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable myapp
sudo systemctl start myapp
```

### 18.4 Nginx 反代

```nginx
server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # SSE 长连接
    location /api/v1/chat/stream {
        proxy_pass http://127.0.0.1:8000;
        proxy_buffering off;
        proxy_cache off;
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding off;
    }
}
```

### 18.5 Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/

EXPOSE 8000

CMD ["uvicorn", "src.api.server:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 18.6 Docker Compose

```yaml
version: "3.8"
services:
  api:
    build: .
    ports: ["8000:8000"]
    env_file: .env
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports: ["80:80"]
    volumes: [./nginx.conf:/etc/nginx/conf.d/default.conf]
    depends_on: [api]
```

---

> **来源：** [FastAPI 官方文档](https://fastapi.tiangolo.com/)
