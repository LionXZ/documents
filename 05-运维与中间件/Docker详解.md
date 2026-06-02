# Docker 速查手册

> 一份通俗易懂的 Docker 文档，涵盖开发部署中最常用的操作和概念，适合快速查阅和上手。

---

## 目录

- [1. 基础概念](#1-基础概念)
- [2. 安装](#2-安装)
- [3. 镜像操作](#3-镜像操作)
- [4. 容器操作](#4-容器操作)
- [5. Dockerfile](#5-dockerfile)
- [6. Docker Compose](#6-docker-compose)
- [7. 网络](#7-网络)
- [8. 数据卷](#8-数据卷)
- [9. Dockerfile 最佳实践](#9-dockerfile-最佳实践)
- [10. 多阶段构建](#10-多阶段构建)
- [11. 日志管理](#11-日志管理)
- [12. 资源限制](#12-资源限制)
- [13. Django 项目容器化实战](#13-django-项目容器化实战)
- [14. 常用命令速查](#14-常用命令速查)
- [15. 常见问题排查](#15-常见问题排查)

---

## 1. 基础概念

### 什么是 Docker？

Docker 是一个**容器化平台**，把应用及其依赖打包到一个轻量、可移植的容器中，在任何地方运行。

### 核心三要素

```
Dockerfile ──build──→ Image ──run──→ Container
（构建说明书）        （镜像/模板）      （容器/实例）
```

| 概念 | 说明 | 类比 |
|------|------|------|
| **Dockerfile** | 构建镜像的指令文件 | 做菜的菜谱 |
| **镜像（Image）** | 只读的应用模板 | 安装光盘/ISO |
| **容器（Container）** | 从镜像启动的运行实例 | 运行的进程 |
| **仓库（Registry）** | 存放镜像的地方 | GitHub |
| **Docker Compose** | 编排多容器应用 | 启动脚本 |

### Docker vs 虚拟机

```
虚拟机：                    Docker：
┌─────────┐                ┌─────────┐
│  App A  │                │  App A  │
├─────────┤                ├─────────┤
│  Guest OS│  (完整OS)      │ Container│ (共享内核)
├─────────┤                ├─────────┤
│Hypervisor│                │  Docker  │
├─────────┤                ├─────────┤
│  Host OS │                │  Host OS │
├─────────┤                ├─────────┤
│  硬件    │                │  硬件    │
└─────────┘                └─────────┘

启动慢，GB级             启动快，MB级，秒级
```

---

## 2. 安装

### macOS

```bash
brew install --cask docker
# 启动 Docker Desktop 应用
```

### Linux

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com | bash
sudo usermod -aG docker $USER   # 非 root 用户也能用（重新登录生效）

# 启动
sudo systemctl start docker
```

### 验证

```bash
docker --version
docker run hello-world     # 测试容器能否正常启动
```

---

## 3. 镜像操作

```bash
# 搜索镜像
docker search nginx

# 拉取镜像
docker pull nginx:alpine       # nginx 是镜像名, alpine 是标签
docker pull python:3.12-slim

# 查看本地镜像
docker images
docker images -a               # 包括中间层

# 查看镜像详情
docker inspect nginx:alpine

# 查看构建历史
docker history nginx:alpine

# 删除镜像
docker rmi nginx:alpine
docker rmi IMAGE_ID

# 清理无用镜像
docker image prune -a          # 删除所有未使用的镜像

# 给镜像打标签
docker tag SOURCE_IMAGE:TAG TARGET_REGISTRY/NAME:TAG
docker tag myapp:latest myrepo/myapp:v1.0

# 推送镜像到仓库
docker push myrepo/myapp:v1.0

# 导出/导入（离线传输）
docker save -o myapp.tar myapp:latest    # 导出
docker load -i myapp.tar                 # 导入
```

---

## 4. 容器操作

### 生命周期

```bash
# 创建并启动
docker run -d --name mycontainer nginx:alpine

# 常用 run 参数
docker run \
  -d \                    # 后台运行
  --name myapp \          # 命名（不指定则随机名）
  -p 8080:80 \            # 端口映射（主机:容器）
  -v /home/data:/data \   # 挂载卷（主机:容器）
  -e DEBUG=true \         # 环境变量
  --restart always \      # 自动重启策略
  -m 512m \               # 内存限制
  --cpus=1.5 \            # CPU 限制
  myapp:latest             # 镜像

# 查看容器
docker ps                      # 运行中的
docker ps -a                   # 所有（含已停止）

# 停止/启动/重启
docker stop myapp
docker start myapp
docker restart myapp

# 删除
docker rm myapp                # 删除已停止的
docker rm -f myapp             # 强制删除（运行中也删）

# 进入容器
docker exec -it myapp bash     # 打开 shell
docker exec -it myapp sh       # alpine 用 sh

# 查看日志
docker logs myapp
docker logs -f myapp           # 实时追踪（Ctrl+C 退出）
docker logs --tail 100 myapp   # 最后 100 行
docker logs --since 1h myapp   # 最近 1 小时

# 查看容器内进程
docker top myapp

# 查看资源使用
docker stats                   # 所有容器
docker stats myapp             # 指定容器

# 文件拷贝
docker cp myapp:/app/log.txt ./         # 容器→主机
docker cp ./config.json myapp:/app/     # 主机→容器

# 查看容器详情（完整信息）
docker inspect myapp

# 提交容器为镜像
docker commit myapp myapp:debug
```

### 重启策略

| 策略 | 说明 |
|------|------|
| `no` | 不自动重启（默认） |
| `always` | 总是重启（Docker 启动时也会） |
| `unless-stopped` | 除非手动停止，否则重启 |
| `on-failure` | 退出码非 0 时重启 |

---

## 5. Dockerfile

### 基础指令

```dockerfile
# FROM：基础镜像（必须第一条指令）
FROM python:3.12-slim

# LABEL：元信息
LABEL maintainer="zhangsan@example.com"

# WORKDIR：设置工作目录（之后的指令在这里执行）
WORKDIR /app

# COPY：从主机复制文件到镜像
COPY requirements.txt ./
COPY . .

# ADD：类似 COPY，但支持自动解压 tar 和 URL 下载
ADD https://example.com/file.tar.gz /tmp/

# RUN：构建时执行命令（pip install 等）
RUN pip install --no-cache-dir -r requirements.txt

# ENV：环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# ARG：构建参数（docker build --build-arg ENV=prod）
ARG ENV=development

# EXPOSE：声明端口（文档作用，不实际映射端口）
EXPOSE 8000

# USER：切换运行用户
USER appuser

# CMD：容器启动时的默认命令（可以被 docker run 后面的命令覆盖）
CMD ["gunicorn", "myapp.wsgi:application", "--bind", "0.0.0.0:8000"]

# ENTRYPOINT：容器入口点（不会被覆盖，docker run 后面的作为参数追加）
ENTRYPOINT ["python", "manage.py"]
CMD ["runserver", "0.0.0.0:8000"]
```

### CMD vs ENTRYPOINT

```dockerfile
# CMD：默认命令，可被覆盖
CMD ["echo", "hello"]
# docker run myimage echo world  → 输出 world（覆盖了 hello）

# ENTRYPOINT：固定入口，docker run 的参数会追加
ENTRYPOINT ["echo"]
CMD ["hello"]
# docker run myimage world       → 输出 world
# docker run myimage              → 输出 hello（用 CMD 默认值）

# 组合使用：ENTRYPOINT 固定程序，CMD 提供默认参数
```

---

## 6. Docker Compose

### 核心概念

用一个 YAML 文件定义和运行**多容器应用**。一条命令启动所有服务。

```yaml
# docker-compose.yml
version: "3.8"

services:
  web:
    build: .                            # 使用当前目录 Dockerfile
    # image: myapp:latest               # 或直接用镜像
    container_name: django_app
    ports:
      - "8000:8000"
    volumes:
      - .:/app                          # 代码目录挂载（开发用，生产去掉）
      - static_volume:/app/static       # 命名卷
    environment:
      - DEBUG=true
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
    env_file:
      - .env
    depends_on:                         # 启动顺序（不等健康检查）
      - db
      - redis
    restart: unless-stopped
    command: gunicorn myapp.wsgi --bind 0.0.0.0:8000
    networks:
      - app-network

  db:
    image: postgres:16-alpine
    container_name: postgres_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    ports:
      - "5432:5432"                      # 生产环境不建议暴露 DB 端口
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    container_name: redis_cache
    volumes:
      - redis_data:/data
    networks:
      - app-network

  celery:
    build: .
    container_name: celery_worker
    command: celery -A myapp worker -l info
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
    depends_on:
      - db
      - redis
    networks:
      - app-network

  nginx:
    image: nginx:alpine
    container_name: nginx_proxy
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
      - static_volume:/static
    depends_on:
      - web
    networks:
      - app-network

volumes:
  postgres_data:
  redis_data:
  static_volume:

networks:
  app-network:
    driver: bridge
```

### 常用命令

```bash
# 启动所有服务（后台）
docker compose up -d

# 启动并重新构建
docker compose up -d --build

# 启动指定服务
docker compose up -d web db

# 查看运行状态
docker compose ps

# 查看日志
docker compose logs -f        # 所有服务
docker compose logs -f web    # 指定服务

# 进入容器
docker compose exec web bash
docker compose exec db psql -U user -d mydb

# 执行一次性命令
docker compose run --rm web python manage.py migrate

# 停止
docker compose stop

# 停止并删除容器（不删数据卷）
docker compose down

# 停止并删除容器+数据卷（⚠️ 数据也删！）
docker compose down -v

# 重启
docker compose restart

# 查看资源使用
docker compose top
```

---

## 7. 网络

### 网络模式

| 模式 | 说明 |
|------|------|
| `bridge` | 桥接模式（默认），容器间通过 IP 互通 |
| `host` | 共享主机网络栈（性能最好，隔离差） |
| `none` | 无网络 |

```bash
# 查看网络
docker network ls
docker network inspect bridge

# 创建自定义网络
docker network create mynetwork

# 容器加入网络
docker network connect mynetwork myapp

# Compose 中定义的网络
# 同一 Compose 文件中的容器自动在默认网络内互通
# 容器间用服务名访问：http://web:8000
```

---

## 8. 数据卷

```bash
# 查看卷
docker volume ls
docker volume inspect my_volume

# 创建卷
docker volume create my_volume

# 删除卷
docker volume rm my_volume

# 清理无用卷
docker volume prune
```

### 三种挂载方式

```bash
# 1. 命名卷（docker管理，推荐生产用）
docker run -v my_volume:/app/data myapp

# 2. 绑定挂载（主机路径，推荐开发用）
docker run -v /home/user/code:/app myapp

# 3. tmpfs（临时内存挂载，不写磁盘）
docker run --tmpfs /app/cache myapp
```

---

## 9. Dockerfile 最佳实践

```dockerfile
# ❌ 差的写法：层太多，体积大
FROM ubuntu:latest
RUN apt-get update
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN pip install django
COPY . /app

# ✅ 好的写法：合并 RUN，清理缓存，用 slim/alpine
FROM python:3.12-slim

WORKDIR /app

# 先复制依赖文件（利用缓存，代码改了不用重新装包）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 再复制代码
COPY . .

# 创建非 root 用户
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

CMD ["gunicorn", "myapp.wsgi", "--bind", "0.0.0.0:8000"]
```

**核心原则**：

| 原则 | 说明 |
|------|------|
| 选择小基础镜像 | `alpine` 或 `slim` 替代完整版 |
| 合并 RUN 指令 | 减少镜像层数 |
| 利用构建缓存 | 先复制不常变的文件（如 requirements.txt） |
| 用 .dockerignore | 排除 node_modules、.git、__pycache__ |
| 非 root 运行 | USER appuser |
| 多阶段构建 | 编译和运行分离 |

---

## 10. 多阶段构建

```dockerfile
# ===== 构建阶段 =====
FROM python:3.12-slim AS builder

WORKDIR /app
COPY requirements.txt .

# 安装依赖到临时目录
RUN pip install --no-cache-dir --user -r requirements.txt

# ===== 运行阶段 =====
FROM python:3.12-slim

WORKDIR /app

# 从构建阶段复制已安装的包
COPY --from=builder /root/.local /root/.local
COPY . .

# 确保可执行文件在 PATH 中
ENV PATH=/root/.local/bin:$PATH

USER 1000
CMD ["gunicorn", "myapp.wsgi", "--bind", "0.0.0.0:8000"]
```

---

## 11. 日志管理

```bash
# Compose 中配置日志
services:
  web:
    image: myapp
    logging:
      driver: "json-file"
      options:
        max-size: "10m"         # 单个日志文件最大 10MB
        max-file: "3"           # 最多保留 3 个文件
```

---

## 12. 资源限制

```yaml
# Compose 中限制资源
services:
  web:
    image: myapp
    deploy:
      resources:
        limits:
          cpus: "2.0"           # 最多 2 个 CPU
          memory: 512M           # 最多 512MB 内存
        reservations:
          cpus: "0.5"           # 预留 0.5 个 CPU
          memory: 128M           # 预留 128MB 内存
```

---

## 13. Django 项目容器化实战

### 完整项目结构

```
myproject/
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── nginx.conf
├── requirements.txt
├── manage.py
├── myapp/
│   ├── settings.py
│   ├── wsgi.py
│   └── ...
└── static/
```

### Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 代码
COPY . .

# 静态文件
RUN python manage.py collectstatic --noinput

# 非 root 用户
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
CMD ["gunicorn", "myapp.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
```

### .dockerignore

```
__pycache__/
*.pyc
*.pyo
.env
.git/
venv/
.venv/
node_modules/
*.log
media/
staticfiles/
```

### nginx.conf

```nginx
upstream django {
    server web:8000;
}

server {
    listen 80;
    server_name example.com;

    # 静态文件
    location /static/ {
        alias /static/;
        expires 30d;
    }

    # 媒体文件
    location /media/ {
        alias /media/;
    }

    # 转发到 Django
    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### docker-compose.yml（生产版）

```yaml
version: "3.8"

services:
  web:
    build: .
    container_name: django_app
    expose:
      - "8000"
    environment:
      - DJANGO_SETTINGS_MODULE=myapp.settings.production
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
      - REDIS_URL=redis://redis:6379/1
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    networks:
      - app_network

  celery:
    build: .
    command: celery -A myapp worker -l info -c 4
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
      - REDIS_URL=redis://redis:6379/1
    depends_on:
      - db
      - redis
    restart: unless-stopped
    networks:
      - app_network

  celery-beat:
    build: .
    command: celery -A myapp beat -l info
    depends_on:
      - db
      - redis
    restart: unless-stopped
    networks:
      - app_network

  db:
    image: postgres:16-alpine
    container_name: postgres_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d mydb"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    networks:
      - app_network

  redis:
    image: redis:7-alpine
    container_name: redis_cache
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    networks:
      - app_network

  nginx:
    image: nginx:alpine
    container_name: nginx_proxy
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
      - static_volume:/static
      - media_volume:/media
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web
    restart: unless-stopped
    networks:
      - app_network

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:

networks:
  app_network:
    driver: bridge
```

### 启动流程

```bash
# 1. 构建并启动
docker compose up -d --build

# 2. 数据库迁移
docker compose exec web python manage.py migrate

# 3. 创建超级用户
docker compose exec web python manage.py createsuperuser

# 4. 检查状态
docker compose ps
docker compose logs -f
```

---

## 14. 常用命令速查

```bash
# ===== 镜像 =====
docker pull IMAGE:TAG            # 拉取
docker images                    # 查看
docker rmi IMAGE                 # 删除
docker build -t NAME:TAG .       # 构建

# ===== 容器 =====
docker run -d --name NAME -p 8080:80 IMAGE     # 启动
docker ps -a                                    # 查看
docker stop | start | restart NAME              # 启停
docker rm NAME                    # 删除
docker exec -it NAME bash         # 进入
docker logs -f NAME               # 日志
docker cp NAME:/path ./local       # 拷贝

# ===== Compose =====
docker compose up -d               # 启动
docker compose up -d --build       # 构建并启动
docker compose down                # 停止删除
docker compose down -v             # 停止删除+数据卷
docker compose ps                  # 状态
docker compose logs -f             # 日志
docker compose exec SERVICE bash   # 进入
docker compose restart SERVICE     # 重启

# ===== 清理 =====
docker system prune -a             # 清理一切（镜像+容器+网络+构建缓存）
docker image prune -a              # 清理未使用镜像
docker container prune             # 清理停止的容器
docker volume prune                # 清理未使用卷

# ===== 其他 =====
docker stats                       # 资源使用
docker inspect NAME                # 详细信息
docker top NAME                    # 容器进程
```

---

## 15. 常见问题排查

| 问题 | 排查方式 |
|------|---------|
| 容器起不来 | `docker logs NAME` 看日志 |
| 端口冲突 | `docker ps` 检查端口占用 |
| 容器间连不上 | Compose 内用服务名，不要用 IP |
| 磁盘满了 | `docker system df` 查看空间占用 |
| 镜像太大 | 用 alpine/slim 基础镜像 + 多阶段构建 |
| 文件没同步 | 检查 volumes 是否正确挂载 |
| 数据库数据丢失 | 检查是否挂载了数据卷 |

```bash
# 查看磁盘占用
docker system df

# 清理构建缓存
docker builder prune

# 查看容器退出原因
docker inspect NAME --format='{{.State.ExitCode}}'
docker logs --tail 50 NAME
```

---

> **Docker 的核心价值：环境一致性。"在我机器上能跑" 不再是个问题。**
