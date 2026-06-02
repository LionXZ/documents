# Nginx 速查手册

> 一份通俗易懂的 Nginx 文档，涵盖 Web 服务、反向代理、负载均衡等核心场景，适合快速查阅和上手。

---

## 目录

- [1. 基础概念](#1-基础概念)
- [2. 安装与启停](#2-安装与启停)
- [3. 配置文件结构](#3-配置文件结构)
- [4. 虚拟主机](#4-虚拟主机)
- [5. 静态文件服务](#5-静态文件服务)
- [6. 反向代理](#6-反向代理)
- [7. 负载均衡](#7-负载均衡)
- [8. HTTPS 配置](#8-https-配置)
- [9. 重定向与重写](#9-重定向与重写)
- [10. 缓存配置](#10-缓存配置)
- [11. 限流与安全](#11-限流与安全)
- [12. WebSocket 代理](#12-websocket-代理)
- [13. 日志管理](#13-日志管理)
- [14. Django 项目完整配置](#14-django-项目完整配置)
- [15. 常用命令速查](#15-常用命令速查)

---

## 1. 基础概念

### Nginx 是什么？

Nginx 是一个**高性能的 HTTP 服务器和反向代理服务器**。它最大的特点是**高并发、低内存、稳定**。

### 核心用途

| 场景 | 说明 |
|------|------|
| **静态文件服务** | 直接返回 HTML/CSS/JS/图片（比 Django 快几十倍） |
| **反向代理** | 把请求转发给后端应用（Django/Flask/FastAPI） |
| **负载均衡** | 把流量分发给多个后端实例 |
| **HTTPS 终端** | SSL/TLS 加密，证书管理 |
| **缓存** | 缓存静态资源和代理结果 |
| **限流** | 控制访问频率 |
| **WebSocket 代理** | 代理 WebSocket 连接 |

### Nginx 在 Django 项目中的位置

```
浏览器 → Nginx (80/443) → Gunicorn (8000) → Django
              │
              └── 静态文件直接返回（/static/, /media/）
```

---

## 2. 安装与启停

### macOS

```bash
brew install nginx
brew services start nginx
```

### Linux

```bash
sudo apt install nginx     # Ubuntu/Debian
sudo systemctl start nginx
sudo systemctl enable nginx  # 开机自启
```

### Docker

```bash
docker run -d --name nginx -p 80:80 -v ./nginx.conf:/etc/nginx/conf.d/default.conf nginx:alpine
```

### 常用管理命令

```bash
# 启动 / 停止 / 重启
sudo systemctl start nginx
sudo systemctl stop nginx
sudo systemctl restart nginx

# 重载配置（不停服！）
sudo nginx -s reload
sudo systemctl reload nginx

# 测试配置文件语法
sudo nginx -t

# 查看版本和编译参数
nginx -V
```

### 关键目录

```
/etc/nginx/
├── nginx.conf                      # 主配置
├── conf.d/                         # 虚拟主机配置目录（推荐放这里）
│   └── default.conf
├── sites-available/                # 可用站点（Ubuntu 风格）
├── sites-enabled/                  # 已启用站点（符号链接）
└── ssl/                            # SSL 证书目录
```

---

## 3. 配置文件结构

```nginx
# /etc/nginx/nginx.conf — 主配置文件

# ===== 全局块 =====
user nginx;                         # worker 进程运行用户
worker_processes auto;              # worker 数（auto=自动匹配 CPU 核数）
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

# ===== events 块 =====
events {
    worker_connections 1024;        # 每个 worker 最大连接数
    use epoll;                      # Linux 用 epoll（高并发关键）
}

# ===== http 块 =====
http {
    include /etc/nginx/mime.types;  # MIME 类型映射
    default_type application/octet-stream;

    # 日志格式
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    # 性能优化
    sendfile on;                     # 高效文件传输
    tcp_nopush on;                   # 合并发送
    tcp_nodelay on;                  # 实时发送
    keepalive_timeout 65;

    # 客户端请求限制
    client_max_body_size 10M;        # 最大请求体（上传文件大小）
    client_body_timeout 12;
    client_header_timeout 12;

    # Gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml;
    gzip_min_length 1000;

    # ===== 虚拟主机配置（从 conf.d 目录加载）=====
    include /etc/nginx/conf.d/*.conf;
}
```

---

## 4. 虚拟主机

### 基于域名的虚拟主机

```nginx
# /etc/nginx/conf.d/example.com.conf
server {
    listen 80;
    server_name example.com www.example.com;

    root /var/www/example.com;
    index index.html;
}
```

### 基于端口的虚拟主机

```nginx
server {
    listen 8080;
    server_name _;    # _ 表示匹配所有域名
    root /var/www/app;
}
```

---

## 5. 静态文件服务

```nginx
server {
    listen 80;
    server_name static.example.com;

    root /var/www;

    # 静态文件
    location /static/ {
        # root 实际路径 = root + location = /var/www/static/
        # 或直接 alias
        alias /home/user/project/staticfiles/;
        expires 30d;                         # 浏览器缓存 30 天
        add_header Cache-Control "public, immutable";
    }

    # 媒体文件
    location /media/ {
        alias /home/user/project/media/;
        expires 7d;
    }

    # 禁止访问隐藏文件
    location ~ /\. {
        deny all;
    }
}
```

---

## 6. 反向代理

将请求转发给后端应用服务器。

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
}
```

### 不同路径转发到不同服务

```nginx
server {
    listen 80;
    server_name example.com;

    # / 转发到 Django
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # /api/ 转发到 FastAPI
    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
    }

    # /admin/ 转发到 Django Admin（可做 IP 白名单）
    location /admin/ {
        allow 192.168.1.0/24;
        deny all;
        proxy_pass http://127.0.0.1:8000;
    }

    # 静态文件直接返回
    location /static/ {
        alias /app/staticfiles/;
        expires 30d;
    }
}
```

### 常用代理头

| 头 | 含义 |
|----|------|
| `Host` | 原始请求域名 |
| `X-Real-IP` | 客户端真实 IP |
| `X-Forwarded-For` | 代理链 |
| `X-Forwarded-Proto` | 原始协议（http/https） |
| `X-Forwarded-Host` | 原始 Host |

---

## 7. 负载均衡

### 轮询（默认）

```nginx
upstream django_cluster {
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}

server {
    listen 80;
    location / {
        proxy_pass http://django_cluster;
    }
}
```

### 加权轮询

```nginx
upstream django_cluster {
    server 127.0.0.1:8001 weight=3;   # 承担 50% 流量
    server 127.0.0.1:8002 weight=2;   # 承担 33%
    server 127.0.0.1:8003 weight=1;   # 承担 17%
}
```

### IP 哈希（会话保持）

```nginx
upstream django_cluster {
    ip_hash;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}
# 同一客户端 IP 始终路由到同一台后端
```

### 后端健康检查

```nginx
upstream django_cluster {
    server 127.0.0.1:8001 max_fails=3 fail_timeout=30s;
    server 127.0.0.1:8002 max_fails=3 fail_timeout=30s;
    server 127.0.0.1:8003 down;    # 标记为下线
    # backup：备用，其他都挂了才用
    server 127.0.0.1:8004 backup;
}
```

---

## 8. HTTPS 配置

### 基本配置

```nginx
server {
    listen 443 ssl http2;
    server_name example.com;

    ssl_certificate /etc/nginx/ssl/example.com.pem;
    ssl_certificate_key /etc/nginx/ssl/example.com.key;

    # 安全配置（推荐）
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    location / {
        proxy_pass http://127.0.0.1:8000;
    }
}

# HTTP 自动跳转 HTTPS
server {
    listen 80;
    server_name example.com;
    return 301 https://$host$request_uri;
}
```

### Let's Encrypt 免费证书（Certbot）

```bash
# 安装 certbot
sudo apt install certbot python3-certbot-nginx

# 自动获取并配置 Nginx
sudo certbot --nginx -d example.com -d www.example.com

# 仅获取证书
sudo certbot certonly --nginx -d example.com

# 自动续期（certbot 默认已加 cron 任务）
sudo certbot renew --dry-run
```

---

## 9. 重定向与重写

```nginx
# 永久重定向（301）
server {
    listen 80;
    server_name old.example.com;
    return 301 https://new.example.com$request_uri;
}

# 按路径重定向
location /old-blog {
    return 301 /new-blog;
}

# 重写 URL（内部重写，浏览器地址栏不变）
location /api {
    rewrite ^/api/(.*)$ /$1 break;     # /api/users → /users
    proxy_pass http://127.0.0.1:8000;
}

# 去掉路径前缀
location /api/ {
    rewrite ^/api/(.*) /$1 break;
    proxy_pass http://127.0.0.1:8000;
}

# www 跳转非 www
server {
    listen 80;
    server_name www.example.com;
    return 301 https://example.com$request_uri;
}
```

---

## 10. 缓存配置

### 静态文件缓存

```nginx
# 浏览器缓存
location ~* \.(jpg|jpeg|png|gif|ico|css|js|woff2?)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}

# HTML 不缓存
location ~* \.html$ {
    expires -1;
    add_header Cache-Control "no-cache";
}
```

### 代理缓存

```nginx
# 定义缓存区
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m max_size=1g inactive=60m;

server {
    location / {
        proxy_cache my_cache;
        proxy_cache_key "$scheme$request_method$host$request_uri";
        proxy_cache_valid 200 302 10m;      # 200/302 缓存 10 分钟
        proxy_cache_valid 404 1m;           # 404 缓存 1 分钟
        proxy_cache_bypass $http_cache_control;  # 请求头可跳过缓存
        add_header X-Cache-Status $upstream_cache_status;  # HIT/MISS 头

        proxy_pass http://127.0.0.1:8000;
    }
}
```

---

## 11. 限流与安全

### 请求频率限制

```nginx
# 定义限速区（按 IP，10MB 约 16 万个 IP）
limit_req_zone $binary_remote_addr zone=req_limit:10m rate=10r/s;

server {
    location /api/ {
        limit_req zone=req_limit burst=20 nodelay;  # 突发 20 个，超了立即 503
        proxy_pass http://127.0.0.1:8000;
    }
}
```

### 连接数限制

```nginx
limit_conn_zone $binary_remote_addr zone=conn_limit:10m;

server {
    location / {
        limit_conn conn_limit 10;  # 每个 IP 最多 10 个并发连接
        proxy_pass http://127.0.0.1:8000;
    }
}
```

### 安全头

```nginx
server {
    # 隐藏 Nginx 版本
    server_tokens off;

    # XSS 防护
    add_header X-XSS-Protection "1; mode=block";
    # 禁止 MIME 嗅探
    add_header X-Content-Type-Options "nosniff";
    # 防止点击劫持
    add_header X-Frame-Options "SAMEORIGIN";

    # 内容安全策略
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' cdn.example.com";

    location / {
        proxy_pass http://127.0.0.1:8000;
    }
}
```

### IP 黑白名单

```nginx
server {
    # 后台管理只允许内网访问
    location /admin/ {
        allow 192.168.1.0/24;     # 内网
        allow 10.0.0.0/8;         # VPN
        deny all;
        proxy_pass http://127.0.0.1:8000;
    }
}
```

---

## 12. WebSocket 代理

Django Channels 等实时通信场景。

```nginx
server {
    listen 80;
    server_name example.com;

    location /ws/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 86400;     # WebSocket 长连接不过期
    }
}
```

---

## 13. 日志管理

### 访问日志格式

```nginx
http {
    log_format detailed '$remote_addr - $remote_user [$time_local] '
                        '"$request" $status $body_bytes_sent '
                        '"$http_referer" "$http_user_agent" '
                        'rt=$request_time uct="$upstream_connect_time" '
                        'uht="$upstream_header_time" urt="$upstream_response_time"';

    access_log /var/log/nginx/access.log detailed;
}
```

### 按日切割日志

```bash
# 用 logrotate 自动切割（通常自带）
# /etc/logrotate.d/nginx
/var/log/nginx/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 640 nginx adm
    sharedscripts
    postrotate
        [ -f /var/run/nginx.pid ] && kill -USR1 $(cat /var/run/nginx.pid)
    endscript
}
```

---

## 14. Django 项目完整配置

```nginx
# /etc/nginx/conf.d/django.conf

upstream django_app {
    server 127.0.0.1:8000;
    # 多实例时取消注释
    # server 127.0.0.1:8001;
    # server 127.0.0.1:8002;
}

server {
    listen 80;
    server_name example.com www.example.com;

    # 上传文件大小限制
    client_max_body_size 20M;

    # Gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
    gzip_min_length 1000;

    # ===== 静态文件 =====
    location /static/ {
        alias /home/user/project/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /home/user/project/media/;
        expires 7d;
    }

    # ===== 网站图标 =====
    location /favicon.ico {
        alias /home/user/project/staticfiles/favicon.ico;
        expires 30d;
    }

    # ===== Django Admin =====
    location /admin/ {
        # 安全：仅内网可访问
        allow 192.168.1.0/24;
        deny all;

        proxy_pass http://django_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # ===== Django 应用 =====
    location / {
        proxy_pass http://django_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;

        # 超时配置
        proxy_connect_timeout 60s;
        proxy_read_timeout 60s;
        proxy_send_timeout 60s;

        # 缓冲
        proxy_buffering off;                     # Django 流式响应需要关闭
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }

    # ===== WebSocket（Channels）=====
    location /ws/ {
        proxy_pass http://django_app;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 86400;
    }

    # ===== 安全 =====
    # 禁止访问隐藏文件
    location ~ /\. {
        deny all;
    }

    # 禁止直接访问 Python 文件
    location ~ \.py$ {
        return 404;
    }

    # ===== 自定义错误页 =====
    error_page 404 /404.html;
    error_page 500 502 503 504 /50x.html;

    location = /50x.html {
        root /usr/share/nginx/html;
    }
}

# HTTPS 重定向（有证书时使用）
# server {
#     listen 80;
#     server_name example.com;
#     return 301 https://$host$request_uri;
# }
#
# server {
#     listen 443 ssl http2;
#     server_name example.com;
#     ssl_certificate /etc/nginx/ssl/example.com.pem;
#     ssl_certificate_key /etc/nginx/ssl/example.com.key;
#     include /etc/nginx/conf.d/django.conf;  # 复用 location 配置
# }
```

---

## 15. 常用命令速查

```bash
# 测试配置
nginx -t

# 重载（不停服）
nginx -s reload
systemctl reload nginx

# 重启
systemctl restart nginx

# 查看日志
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# 查看编译参数
nginx -V

# 按访问量统计 IP
awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -10

# 统计状态码分布
awk '{print $9}' /var/log/nginx/access.log | sort | uniq -c | sort -rn

# 统计最慢的请求
awk '{print $NF,$0}' /var/log/nginx/access.log | sort -rn | head -10
```

---

### 关键指令速查

```nginx
# 静态文件
location /static/ { alias /path/; expires 30d; }

# 反向代理
location / { proxy_pass http://127.0.0.1:8000; proxy_set_header Host $host; }

# 负载均衡
upstream backend { server 127.0.0.1:8001; server 127.0.0.1:8002; }

# HTTPS 重定向
return 301 https://$host$request_uri;

# WebSocket
proxy_http_version 1.1; proxy_set_header Upgrade $http_upgrade; proxy_set_header Connection "upgrade";

# 限流
limit_req rate=10r/s;

# IP 白名单
allow 192.168.1.0/24; deny all;
```

---

> **Nginx 的核心价值：高性能的反向代理层。Django 前面的 Nginx 就像餐厅门口的接待员——处理静态文件、分流请求、缓冲保护后端。**
