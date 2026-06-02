# Django 5.x 完全使用指南

> 基于 Django 官方文档整理 | 适合速查 | 通俗易懂
> 涵盖：快速入门 → ORM → 视图/模板 → 配置 → Admin → REST Framework → 部署

---

## 一、Django 概述

**Django** 是 Python 最流行的 Web 全栈框架，遵循 **MTV 架构模式**：

| 层级 | 对应 Django 组件 | 职责 |
|------|-----------------|------|
| **M** (Model) | `models.py` | 数据层：定义数据库表结构、操作数据 |
| **T** (Template) | `templates/` 目录 | 表现层：HTML 页面渲染 |
| **V** (View) | `views.py` | 逻辑层：接收请求、处理业务、返回响应 |

完整的请求流程：

```
浏览器请求 → urls.py（路由匹配）→ views.py（业务处理）→ models.py（数据库操作）→ templates（渲染 HTML）→ 返回响应
```

### Django 核心特性

- **ORM 系统**：用 Python 类操作数据库，无需手写 SQL
- **自动 Admin 后台**：根据 Model 自动生成管理界面
- **表单处理**：自动生成表单、数据验证
- **用户认证**：内置用户注册、登录、权限系统
- **中间件机制**：请求/响应的插件式处理
- **缓存框架**：支持 Redis、Memcached 等多种缓存后端
- **安全性**：内置 CSRF 防护、XSS 防护、SQL 注入防护

---

## 二、快速入门

### 2.1 安装 Django

```bash
pip install django

# 查看版本
python -m django --version
```

### 2.2 创建项目

```bash
# 创建项目
django-admin startproject myproject

# 生成的目录结构
myproject/
├── manage.py              # 项目管理入口，所有命令通过它执行
├── myproject/
│   ├── __init__.py
│   ├── settings.py        # 全局配置文件（核心！）
│   ├── urls.py            # 根路由配置
│   ├── asgi.py            # ASGI 异步服务入口
│   └── wsgi.py            # WSGI 同步服务入口
```

### 2.3 启动开发服务器

```bash
cd myproject
python manage.py runserver              # 默认 127.0.0.1:8000
python manage.py runserver 8080         # 指定端口
python manage.py runserver 0.0.0.0:8080 # 允许局域网访问
```

打开浏览器访问 `http://127.0.0.1:8000/`，看到火箭页面即表示成功。

### 2.4 创建应用（App）

Django 项目由多个 **App** 组成，每个 App 负责一个独立功能模块：

```bash
python manage.py startapp blog
```

生成的 App 目录结构：

```
blog/
├── __init__.py
├── admin.py          # Admin 后台注册模型
├── apps.py           # App 配置类
├── models.py         # 数据库模型定义（ORM 核心）
├── views.py          # 视图函数/类
├── urls.py           # 子路由（需手动创建）
├── tests.py          # 单元测试
└── migrations/       # 数据库迁移文件（自动生成）
```

### 2.5 注册 App

在 `settings.py` 中注册 App（必须！否则不会识别模型）：

```python
# myproject/settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # ↓ 添加你的 App
    'blog',
]
```

### 2.6 编写第一个视图

**步骤 1**：在 `blog/views.py` 中编写视图函数：

```python
from django.http import HttpResponse

def index(request):
    """每个视图函数必须接收 request 参数，返回 HttpResponse"""
    return HttpResponse("<h1>Hello Django!</h1>")
```

**步骤 2**：创建 `blog/urls.py` 配置子路由：

```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # name 用于反向解析 URL
]
```

**步骤 3**：在项目根路由 `myproject/urls.py` 中使用 `include` 引入：

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('blog/', include('blog.urls')),  # 将 blog/ 开头的 URL 转发给 blog.urls
]
```

访问 `http://127.0.0.1:8000/blog/` 即可看到 "Hello Django!"

### 2.7 第一个模型（Model）

在 `blog/models.py` 中定义模型：

```python
from django.db import models

class Article(models.Model):
    title = models.CharField(max_length=200, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name='发布时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'blog_articles'        # 自定义表名
        verbose_name = '文章'
        verbose_name_plural = '文章列表'
        ordering = ['-pub_date']           # 默认按发布时间降序

    def __str__(self):
        return self.title
```

然后执行迁移命令：

```bash
python manage.py makemigrations  # 生成迁移文件（记录表结构变化）
python manage.py migrate         # 执行迁移（把变化应用到数据库）
```

---

## 三、核心配置文件 settings.py 详解

### 3.1 完整配置项速查

```python
import os
from pathlib import Path

# ==================== 基础路径 ====================
BASE_DIR = Path(__file__).resolve().parent.parent  # 项目根目录

# ==================== 安全密钥 ====================
SECRET_KEY = 'django-insecure-xxxxxxxxxx'
# 作用：加密签名（session、CSRF Token、密码重置链接等都用它签名）
# 生产环境必须使用强随机字符串，建议用环境变量管理
# 可使用以下命令生成: python -c "import secrets; print(secrets.token_urlsafe(50))"

# ==================== 调试模式 ====================
DEBUG = True
# True: 开发模式（显示详细错误页面、自动重载）
# False: 生产模式（必须设置 ALLOWED_HOSTS）

# ==================== 允许访问的主机 ====================
ALLOWED_HOSTS = ['*']
# DEBUG=False 时，必须设置允许访问的域名/IP，例如：['www.example.com', '192.168.1.100']

# ==================== 应用注册 ====================
INSTALLED_APPS = [
    'django.contrib.admin',          # 后台管理
    'django.contrib.auth',           # 认证系统
    'django.contrib.contenttypes',   # 内容类型框架
    'django.contrib.sessions',       # 会话管理
    'django.contrib.messages',       # 消息框架
    'django.contrib.staticfiles',    # 静态文件管理
    'blog',                          # 你的应用
    'rest_framework',                # DRF（如使用）
]

# ==================== 中间件 ====================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',           # 安全头处理
    'django.contrib.sessions.middleware.SessionMiddleware',    # Session 管理
    'django.middleware.common.CommonMiddleware',               # URL 规范化等
    'django.middleware.csrf.CsrfViewMiddleware',               # CSRF 防护
    'django.contrib.auth.middleware.AuthenticationMiddleware', # 用户认证
    'django.contrib.messages.middleware.MessageMiddleware',    # 消息提示
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # 防点击劫持
]
# ⚠️ 顺序很重要，不可随意调换！

# ==================== 根路由 ====================
ROOT_URLCONF = 'myproject.urls'

# ==================== 模板配置 ====================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # 全局模板目录
        'APP_DIRS': True,                   # 自动搜索每个 App 下的 templates 目录
        'OPTIONS': {
            'context_processors': [         # 模板上下文处理器
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ==================== WSGI/ASGI ====================
WSGI_APPLICATION = 'myproject.wsgi.application'
ASGI_APPLICATION = 'myproject.asgi.application'

# ==================== 数据库配置 ====================
# SQLite（默认，无需额外安装）
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# MySQL 配置（需要 pip install mysqlclient）
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'mydatabase',
#         'USER': 'root',
#         'PASSWORD': 'your_password',
#         'HOST': '127.0.0.1',
#         'PORT': 3306,
#         'OPTIONS': {'charset': 'utf8mb4'},
#     }
# }

# PostgreSQL 配置（需要 pip install psycopg2）
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'mydatabase',
#         'USER': 'mydbuser',
#         'PASSWORD': 'password',
#         'HOST': '127.0.0.1',
#         'PORT': '5432',
#     }
# }

# 多数据库配置
# DATABASES = {
#     'default': { ... },
#     'analytics': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'analytics_db',
#     }
# }
# DATABASE_ROUTERS = ['path.to.AnalyticsRouter']  # 数据库路由

# ==================== 密码验证 ====================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ==================== 国际化 ====================
LANGUAGE_CODE = 'zh-hans'       # 中文
TIME_ZONE = 'Asia/Shanghai'     # 上海时区
USE_I18N = True                 # 启用国际化
USE_TZ = True                   # 使用时区感知的时间

# ==================== 静态文件 ====================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']        # 开发阶段的静态文件目录
STATIC_ROOT = BASE_DIR / 'staticfiles'           # 生产环境收集后的目录（collectstatic 命令使用）

# ==================== 媒体文件（用户上传） ====================
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ==================== 默认主键类型 ====================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==================== 自定义用户模型 ====================
# AUTH_USER_MODEL = 'yourapp.User'  # 替换默认 User 模型时使用

# ==================== 登录/登出跳转 ====================
# LOGIN_URL = '/login/'
# LOGIN_REDIRECT_URL = '/'
# LOGOUT_REDIRECT_URL = '/'

# ==================== 邮件配置 ====================
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.qq.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'xxx@qq.com'
# EMAIL_HOST_PASSWORD = '授权码'

# ==================== 缓存配置（Redis） ====================
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.redis.RedisCache',
#         'LOCATION': 'redis://127.0.0.1:6379/1',
#         'TIMEOUT': 300,
#     }
# }

# ==================== Session 配置 ====================
# SESSION_ENGINE = 'django.contrib.sessions.backends.cache'  # 缓存存储
# SESSION_COOKIE_AGE = 1209600  # 两周（秒）
# SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # 关闭浏览器不失效

# ==================== 日志配置 ====================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
    },
}
```

---

## 四、模型层（Model）— ORM 数据库操作

### 4.1 常用字段类型

| 字段类型 | 参数 | 数据库类型 | 使用场景 |
|---------|------|-----------|---------|
| `CharField` | `max_length=N` | VARCHAR(N) | 短文本（标题、用户名） |
| `TextField` | — | TEXT / LONGTEXT | 长文本（文章内容） |
| `IntegerField` | — | INT | 整数 |
| `BigIntegerField` | — | BIGINT | 大整数 |
| `BooleanField` | — | TINYINT(1) | 布尔值 |
| `DecimalField` | `max_digits`, `decimal_places` | DECIMAL | 金额（精确小数） |
| `FloatField` | — | DOUBLE | 浮点数 |
| `DateField` | `auto_now`, `auto_now_add` | DATE | 日期 |
| `DateTimeField` | `auto_now`, `auto_now_add` | DATETIME | 日期+时间 |
| `TimeField` | — | TIME | 时间 |
| `EmailField` | — | VARCHAR(254) | 邮箱（自带验证） |
| `URLField` | — | VARCHAR(200) | URL |
| `SlugField` | — | VARCHAR(50) | URL友好的短标签 |
| `UUIDField` | — | CHAR(32) | UUID |
| `FileField` | `upload_to` | VARCHAR(100) | 文件上传 |
| `ImageField` | `upload_to`, `height_field`, `width_field` | VARCHAR(100) | 图片上传（需 Pillow） |
| `JSONField` | — | JSON | JSON 数据（MySQL 5.7+/PostgreSQL 9.4+） |

### 4.2 通用字段选项（约束）

| 选项 | 说明 | 示例 |
|------|------|------|
| `null=True` | 数据库层面允许 NULL | `models.CharField(null=True)` |
| `blank=True` | 表单验证允许为空 | `models.CharField(blank=True)` |
| `default=值` | 设置默认值 | `models.IntegerField(default=0)` |
| `unique=True` | 值唯一约束 | `models.EmailField(unique=True)` |
| `primary_key=True` | 自定义主键（不设置则自动创建 id） | `models.CharField(primary_key=True)` |
| `db_index=True` | 创建数据库索引 | `models.CharField(db_index=True)` |
| `choices=列表` | 限定可选值范围 | `models.CharField(choices=[('M','男'),('F','女')])` |
| `verbose_name='名称'` | Admin 后台显示的字段名 | `models.CharField(verbose_name='标题')` |
| `editable=False` | 不在 Admin 显示，不可编辑 | `models.DateTimeField(editable=False)` |
| `help_text='提示'` | Admin 表单中的帮助文本 | `models.CharField(help_text='请输入真实姓名')` |
| `validators=[...]` | 自定义验证器 | `models.CharField(validators=[validate_xxx])` |
| `error_messages={}` | 自定义错误信息 | `models.CharField(error_messages={'blank':'必填'})` |

### 4.3 自动时间字段

```python
class Article(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    # ↑ 首次创建时自动设为当前时间（不可更新）

    updated_at = models.DateTimeField(auto_now=True)
    # ↑ 每次 save() 时自动更新为当前时间
```

### 4.4 关系字段

```python
class Author(models.Model):
    name = models.CharField(max_length=50)

class Publisher(models.Model):
    name = models.CharField(max_length=100)

class Book(models.Model):
    title = models.CharField(max_length=200)

    # ========== 一对多（ForeignKey） ==========
    # 外键默认关联到主表的主键（id）
    # on_delete 必填！决定主表删除时子表的行为
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.CASCADE,    # 级联删除：出版社删了，书也删
        related_name='books',        # 反向查询名：publisher.books.all()
        related_query_name='book',   # 反向过滤名：Publisher.objects.filter(book__title='xxx')
    )

    # ========== 多对多（ManyToManyField） ==========
    # Django 自动创建中间表
    authors = models.ManyToManyField(
        Author,
        related_name='books',
    )

    # ========== 一对一（OneToOneField） ==========
    # detail = models.OneToOneField(BookDetail, on_delete=models.CASCADE)
```

**on_delete 参数必填选项：**

| 选项 | 行为 |
|------|------|
| `models.CASCADE` | 级联删除：主表删除，从表也删除 |
| `models.PROTECT` | 保护：有关联数据时禁止删除主表（抛出 ProtectedError） |
| `models.SET_NULL` | 置空：主表删除，外键字段设为 NULL（需 null=True） |
| `models.SET_DEFAULT` | 设默认值：主表删除，外键字段设为默认值（需设 default） |
| `models.SET(值/函数)` | 设为指定值或函数返回值 |
| `models.DO_NOTHING` | 什么都不做（可能导致数据库完整性错误） |

### 4.5 Meta 内部类（模型元数据）

```python
class Article(models.Model):
    title = models.CharField(max_length=200)

    class Meta:
        # ---------- 表名 ----------
        db_table = 'my_custom_table_name'   # 自定义数据库表名

        # ---------- 排序 ----------
        ordering = ['-pub_date']            # 默认排序（- 表示降序）
        ordering = ['-pub_date', 'title']   # 多字段排序

        # ---------- Admin显示名 ----------
        verbose_name = '文章'               # 单数
        verbose_name_plural = '文章列表'    # 复数

        # ---------- 约束 ----------
        unique_together = ['title', 'author']  # 联合唯一（旧方式）
        constraints = [                        # 联合唯一（新方式，推荐）
            models.UniqueConstraint(fields=['title', 'author'], name='unique_title_author')
        ]

        # ---------- 索引 ----------
        indexes = [
            models.Index(fields=['title']),                        # 单字段索引
            models.Index(fields=['title', '-pub_date'], name='idx_title_date'),  # 联合索引
        ]

        # ---------- 权限 ----------
        permissions = [
            ('can_publish', '可以发布文章'),
        ]

        # ---------- 抽象基类/代理 ----------
        abstract = True   # 抽象类：不创建数据表，只供子类继承字段
        # proxy = True    # 代理模型：不创建新表，只改变 Python 行为

        # ---------- 其他 ----------
        # get_latest_by = 'pub_date'   # latest()/earliest() 默认字段
        # default_related_name = 'articles'   # 默认反向关系名
```

### 4.6 模型方法

```python
class Article(models.Model):
    title = models.CharField(max_length=200)

    def __str__(self):
        """返回对象的字符串表示（Admin 显示用）"""
        return self.title

    def get_absolute_url(self):
        """获取对象的规范 URL（Admin "查看"按钮用）"""
        from django.urls import reverse
        return reverse('article-detail', args=[str(self.id)])

    def save(self, *args, **kwargs):
        """重写保存方法（在保存前后做额外处理）"""
        # 保存前的自定义逻辑
        super().save(*args, **kwargs)
        # 保存后的自定义逻辑

    def delete(self, *args, **kwargs):
        """重写删除方法"""
        super().delete(*args, **kwargs)
```

### 4.7 自定义模型管理器（Manager）

```python
class PublishedManager(models.Manager):
    """只返回已发布的文章"""
    def get_queryset(self):
        return super().get_queryset().filter(status='published')

class Article(models.Model):
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('published', '已发布'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    objects = models.Manager()            # 默认管理器（始终保留第一个）
    published = PublishedManager()        # 自定义管理器

# 使用
Article.objects.all()        # 返回所有文章
Article.published.all()      # 只返回已发布文章
```

### 4.8 数据库迁移完整命令

```bash
# 生成迁移文件（检测 models.py 变化）
python manage.py makemigrations
python manage.py makemigrations blog    # 只生成指定 app 的迁移

# 查看迁移对应的 SQL（不执行，仅预览）
python manage.py sqlmigrate blog 0001

# 执行迁移到数据库
python manage.py migrate

# 查看所有迁移状态
python manage.py showmigrations

# 回滚到指定迁移（一般不推荐）
python manage.py migrate blog 0001      # 回退到 0001

# 重置迁移（终极方案，谨慎使用）
# 1. 删除所有迁移文件（保留 __init__.py）
# 2. 删除数据库中的 django_migrations 表
# 3. python manage.py makemigrations
# 4. python manage.py migrate --fake-initial

# 从已有数据库反向生成模型
python manage.py inspectdb > models.py

# 进入数据库终端
python manage.py dbshell
```

---

## 五、ORM 查询操作大全

### 5.1 创建数据（Create）— 4 种方式

```python
from blog.models import Article

# 方式1：实例化后 save()
article = Article(title='标题1', content='内容1')
article.save()

# 方式2：create() 一步完成（无需调 save()）
Article.objects.create(title='标题2', content='内容2')

# 方式3：get_or_create（已存在则获取，不存在则创建）
# 返回 (对象, 是否新建) 元组
article, created = Article.objects.get_or_create(
    title='标题3',                   # 查找条件
    defaults={'content': '默认内容'} # 新建时使用的其他字段
)

# 方式4：bulk_create 批量创建（只需1条SQL，高效！）
articles = [
    Article(title=f'标题{i}', content=f'内容{i}')
    for i in range(100)
]
Article.objects.bulk_create(articles)
```

### 5.2 查询数据（Read）

#### 5.2.1 基础查询方法

| 方法 | 返回值类型 | 说明 |
|------|-----------|------|
| `all()` | QuerySet | 获取所有记录 |
| `get(**kwargs)` | 单个对象 | 获取唯一记录（多了或少了都抛异常） |
| `filter(**kwargs)` | QuerySet | 条件过滤，返回所有匹配项 |
| `exclude(**kwargs)` | QuerySet | 排除匹配条件的记录 |
| `first()` | 对象/None | 返回第一条，无则 None |
| `last()` | 对象/None | 返回最后一条，无则 None |
| `order_by(*fields)` | QuerySet | 排序（`-field` 降序） |
| `count()` | int | 计数（比 len(queryset) 高效） |
| `exists()` | bool | 判断是否有匹配数据 |
| `distinct()` | QuerySet | 去重 |
| `values(*fields)` | QuerySet 字典 | 返回字典列表，只查指定字段 |
| `values_list(*fields)` | QuerySet 元组 | 返回元组列表 |
| `values_list(*fields, flat=True)` | QuerySet | 返回单个字段值的列表 |
| `defer(*fields)` | QuerySet | 延迟加载指定字段（用于大字段） |
| `only(*fields)` | QuerySet | 只加载指定字段 |
| `select_related(*fk)` | QuerySet | JOIN 预加载外键（一对一/多对一） |
| `prefetch_related(*m2m)` | QuerySet | 批量预加载多对多/反向一对多 |

```python
# ---------- 基础用法示例 ----------

# all() — 全表查询
articles = Article.objects.all()

# get() — 查一条（唯一）
article = Article.objects.get(id=1)
article = Article.objects.get(title='Python教程')  # 找不到 → DoesNotExist；找到多条 → MultipleObjectsReturned

# filter() — 条件过滤（返回 QuerySet，可链式调用）
articles = Article.objects.filter(status='published')

# exclude() — 排除
articles = Article.objects.exclude(status='archived')

# order_by() — 排序
articles = Article.objects.order_by('-pub_date')     # 降序
articles = Article.objects.order_by('title', '-id')  # 多字段排序

# values() — 返回字典（只查指定列）
articles = Article.objects.values('id', 'title')
# 结果：[{'id': 1, 'title': '标题1'}, {'id': 2, 'title': '标题2'}]

# values_list() — 返回元组
articles = Article.objects.values_list('id', 'title')
# 结果：[(1, '标题1'), (2, '标题2')]

# values_list(flat=True) — 单字段值列表
titles = Article.objects.values_list('title', flat=True)
# 结果：['标题1', '标题2']

# count() / exists()
count = Article.objects.filter(status='published').count()
has_data = Article.objects.filter(status='draft').exists()
```

#### 5.2.2 字段查询条件（Field Lookups）— 双下划线魔法

语法：`字段名__查询条件=值`

| 查询条件 | SQL 等价 | 示例 |
|---------|---------|------|
| `exact`/`iexact` | `=` / `LIKE`(不区分大小写) | `filter(name__exact='Python')` |
| `contains`/`icontains` | `LIKE '%值%'` | `filter(title__contains='Django')` |
| `startswith`/`istartswith` | `LIKE '值%'` | `filter(title__startswith='Python')` |
| `endswith`/`iendswith` | `LIKE '%值'` | `filter(file__endswith='.pdf')` |
| `in` | `IN (...)` | `filter(id__in=[1, 2, 3])` |
| `gt` / `gte` | `>` / `>=` | `filter(price__gt=50)` |
| `lt` / `lte` | `<` / `<=` | `filter(price__lte=100)` |
| `range` | `BETWEEN` | `filter(price__range=(10, 50))` |
| `isnull` | `IS NULL` / `IS NOT NULL` | `filter(desc__isnull=True)` |
| `year` / `month` / `day` | `EXTRACT(...)` | `filter(pub_date__year=2025)` |
| `week` / `week_day` | `EXTRACT(...)` | `filter(pub_date__week_day=1)` — 周日=1 |
| `regex` / `iregex` | `REGEXP` | `filter(title__regex=r'^[Dd]jango')` |

**跨关系查询（双下划线穿透关联表）：**

```python
# 查询"出版社名为'人民社'的书"
Book.objects.filter(publisher__name='人民社')

# 查询"作者名字包含'张'的书"
Book.objects.filter(authors__name__icontains='张')

# 多层级穿透
Book.objects.filter(publisher__city__name='北京')
```

#### 5.2.3 Q 对象 — 复杂条件查询（OR / NOT）

```python
from django.db.models import Q

# AND（逗号分隔，这是默认行为）
Article.objects.filter(price__gt=50, status='published')

# OR（Q 对象的管道符 |）
Article.objects.filter(Q(price__lt=30) | Q(price__gt=100))

# NOT（Q 对象的波浪符 ~）
Article.objects.filter(~Q(title__icontains='广告'))

# 嵌套组合（OR 条件 + AND 条件）
Article.objects.filter(
    Q(price__lt=50) | Q(status='featured'),  # OR 条件
    is_active=True                            # AND 条件
)
# SQL: WHERE (price < 50 OR status = 'featured') AND is_active = True

# 动态构建查询条件
conditions = Q()
if keyword:
    conditions &= Q(title__icontains=keyword)
if min_price:
    conditions &= Q(price__gte=min_price)
articles = Article.objects.filter(conditions)
```

#### 5.2.4 F 对象 — 字段间比较 + 原子更新

```python
from django.db.models import F

# 字段间比较（查询阅读量 > 点赞量的文章）
Article.objects.filter(read_count__gt=F('like_count'))

# 原子更新（避免竞态条件，直接在数据库层面计算）
Article.objects.filter(id=1).update(read_count=F('read_count') + 1)
# SQL: UPDATE article SET read_count = read_count + 1 WHERE id = 1
```

#### 5.2.5 聚合查询

```python
from django.db.models import Count, Sum, Avg, Max, Min, StdDev, Variance

# aggregate() — 全表聚合，返回字典
result = Article.objects.aggregate(
    total=Count('id'),
    avg_price=Avg('price'),
    max_price=Max('price'),
    min_price=Min('price'),
)
# {'total': 50, 'avg_price': 35.5, 'max_price': 99.0, 'min_price': 9.9}

# annotate() — 分组聚合（等价 GROUP BY），每个对象附加聚合值
from django.db.models import Count
authors = Author.objects.annotate(book_count=Count('books'))
for author in authors:
    print(author.name, author.book_count)

# 复杂分组：统计每个分类下已发布文章数
categories = Category.objects.annotate(
    pub_count=Count('article', filter=Q(article__status='published'))
)
```

### 5.3 更新数据（Update）— 3 种方式

```python
# 方式1：获取对象 → 修改属性 → save()（修改所有字段）
article = Article.objects.get(id=1)
article.title = '新标题'
article.save()  # 更新所有字段

# 方式2：save(update_fields=[...]) — 只更新指定字段（更高效）
article = Article.objects.get(id=1)
article.title = '新标题'
article.save(update_fields=['title'])  # 只更新 title 字段

# 方式3：QuerySet 批量 update() — 只发1条 SQL，不触发 save() 信号
Article.objects.filter(status='draft').update(status='published')
Article.objects.filter(id__in=[1,2,3]).update(publisher_id=5)

# update_or_create — 有则更新，无则创建
article, created = Article.objects.update_or_create(
    id=1,                      # 查找条件
    defaults={                 # 更新/创建的字段
        'title': '新标题',
        'content': '新内容',
    }
)
```

### 5.4 删除数据（Delete）

```python
# 删除单个
article = Article.objects.get(id=1)
article.delete()

# 批量删除（返回被删除数量及类型统计）
count_info = Article.objects.filter(status='archived').delete()
# count_info: (15, {'blog.Article': 15})

# ⚠️ 慎用：删除所有数据
# Article.objects.all().delete()
```

### 5.5 QuerySet 核心特性

| 特性 | 说明 |
|------|------|
| **惰性求值** | 创建 QuerySet 不触发数据库查询，只在遍历/切片/序列化时才执行 |
| **缓存机制** | 首次求值后缓存结果，后续使用直接读缓存 |
| **链式调用** | `filter().exclude().order_by().annotate()` 无限链式 |
| **切片** | `qs[:10]` → LIMIT 10；`qs[10:20]` → OFFSET 10 LIMIT 10；不支持负索引 |

```python
# 惰性求值示例
qs = Article.objects.filter(status='published')  # 此时还没查数据库
qs = qs.filter(price__gt=50)                     # 仍没查
result = list(qs)                                 # 此时才真正执行 SQL

# 查看 QuerySet 对应的 SQL（调试神器）
print(Article.objects.filter(title__icontains='python').query)

# 查看所有已执行的 SQL
from django.db import connection
print(connection.queries)  # 需要在 DEBUG=True 下
```

### 5.6 关联查询优化

```python
# ❌ N+1 问题：循环外键访问导致每次循环都查一次数据库
books = Book.objects.all()
for book in books:
    print(book.publisher.name)  # 每次循环都执行一条 SQL 查 publisher

# ✅ select_related：JOIN 方式预加载外键（一对一/多对一）
books = Book.objects.select_related('publisher').all()
for book in books:
    print(book.publisher.name)  # 不再额外查询

# ✅ prefetch_related：批量方式预加载多对多/反向一对多
authors = Author.objects.prefetch_related('books').all()
for author in authors:
    # author.books.all() 不再额外查询
    print(author.name, author.books.count())

# 多层预加载
books = Book.objects.select_related('publisher__city').prefetch_related('authors')
```

---

## 六、视图层（View）

### 6.1 函数视图（FBV）

```python
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, Http404
from .models import Article

def article_list(request):
    """文章列表"""
    articles = Article.objects.filter(status='published')
    return render(request, 'blog/list.html', {'articles': articles})

def article_detail(request, article_id):
    """文章详情（自动处理 404）"""
    article = get_object_or_404(Article, id=article_id, status='published')
    return render(request, 'blog/detail.html', {'article': article})

def article_create(request):
    """创建文章"""
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        if title and content:
            Article.objects.create(title=title, content=content)
            return redirect('article-list')  # 重定向到列表页
    return render(request, 'blog/create.html')

def api_articles(request):
    """返回 JSON 数据"""
    articles = Article.objects.values('id', 'title', 'pub_date')
    return JsonResponse({'data': list(articles)})
```

**常用快捷函数：**

| 函数 | 说明 |
|------|------|
| `render(request, template, context)` | 渲染模板并返回 HttpResponse |
| `redirect(to)` | 重定向（可传 URL、视图名、模型对象） |
| `get_object_or_404(Model, **kwargs)` | 查对象，找不到自动抛出 404 |
| `get_list_or_404(Model, **kwargs)` | 查列表，空列表也 404 |
| `JsonResponse(data)` | 返回 JSON 响应 |

### 6.2 类视图（CBV）— 内置通用视图

Django 提供了一套内置类视图，大幅减少重复代码：

| 类视图 | 用途 | 关键属性 |
|--------|------|---------|
| `View` | 所有 CBV 的基类 | 重写 `get()`, `post()` 等 |
| `TemplateView` | 渲染模板 | `template_name`, `get_context_data()` |
| `RedirectView` | 重定向 | `url`, `pattern_name` |
| `ListView` | 对象列表 | `model`, `template_name`, `context_object_name`, `paginate_by`, `queryset` |
| `DetailView` | 对象详情 | `model`, `template_name`, `context_object_name`, `pk_url_kwarg` |
| `CreateView` | 创建对象 | `model`, `form_class`, `fields`, `template_name`, `success_url` |
| `UpdateView` | 更新对象 | 同 CreateView |
| `DeleteView` | 删除对象 | 同 CreateView（会显示确认页） |

```python
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Article

class ArticleListView(ListView):
    model = Article
    template_name = 'blog/article_list.html'
    context_object_name = 'articles'
    paginate_by = 20                        # 每页20条，自动分页
    queryset = Article.objects.filter(status='published')  # 自定义查询集
    ordering = ['-pub_date']               # 排序

class ArticleDetailView(DetailView):
    model = Article
    template_name = 'blog/article_detail.html'
    context_object_name = 'article'

class ArticleCreateView(CreateView):
    model = Article
    template_name = 'blog/article_form.html'
    fields = ['title', 'content', 'status']  # 允许编辑的字段
    success_url = reverse_lazy('article-list')

class ArticleUpdateView(UpdateView):
    model = Article
    template_name = 'blog/article_form.html'
    fields = ['title', 'content', 'status']
    success_url = reverse_lazy('article-list')

class ArticleDeleteView(DeleteView):
    model = Article
    template_name = 'blog/article_confirm_delete.html'
    success_url = reverse_lazy('article-list')
```

**URL 配置：**

```python
urlpatterns = [
    path('', ArticleListView.as_view(), name='article-list'),
    path('<int:pk>/', ArticleDetailView.as_view(), name='article-detail'),
    path('create/', ArticleCreateView.as_view(), name='article-create'),
    path('<int:pk>/edit/', ArticleUpdateView.as_view(), name='article-edit'),
    path('<int:pk>/delete/', ArticleDeleteView.as_view(), name='article-delete'),
]
```

### 6.3 request 对象常用属性

| 属性 | 说明 |
|------|------|
| `request.method` | 请求方法（GET/POST/PUT/DELETE 等） |
| `request.GET` | GET 参数（类字典对象 `QueryDict`） |
| `request.POST` | POST 表单数据 |
| `request.FILES` | 上传文件 |
| `request.user` | 当前登录用户（未登录为 AnonymousUser） |
| `request.session` | Session 会话 |
| `request.path` | 当前请求路径（不含域名） |
| `request.get_full_path()` | 含查询参数的完整路径 |
| `request.META` | HTTP 头部等信息（如 `REMOTE_ADDR`） |
| `request.body` | 原始请求体（bytes） |
| `request.is_ajax()` | 是否 Ajax 请求 |
| `request.is_secure()` | 是否 HTTPS |
| `request.COOKIES` | Cookie 字典 |

---

## 七、URL 路由配置

### 7.1 path() 基础用法

```python
from django.urls import path, include, re_path

urlpatterns = [
    # 精确匹配
    path('articles/', views.article_list),

    # 路径参数（<>）
    path('articles/<int:article_id>/', views.article_detail),
    # int 是转换器类型，article_id 是传给视图的参数名

    # 子路由（include）
    path('blog/', include('blog.urls')),

    # 正则匹配（re_path）
    re_path(r'^articles/(?P<year>[0-9]{4})/$', views.year_archive),
]
```

**内置路径转换器类型：**

| 转换器 | 匹配内容 | 示例 |
|--------|---------|------|
| `str` | 非空字符串（不含 `/`） | `<str:name>` |
| `int` | 零或正整数 | `<int:pk>` |
| `slug` | 由字母/数字/连字符/下划线组成的字符串 | `<slug:slug>` |
| `uuid` | UUID 格式 | `<uuid:id>` |
| `path` | 非空字符串（含 `/`） | `<path:filepath>` |

### 7.2 自定义路径转换器

```python
# converters.py
class YearConverter:
    regex = '[0-9]{4}'          # 匹配4位数字

    def to_python(self, value):
        return int(value)        # 转换为 Python 类型

    def to_url(self, value):
        return str(value)        # 反向解析时转换为 URL 字符串

# urls.py
from django.urls import register_converter, path
register_converter(YearConverter, 'yyyy')

urlpatterns = [
    path('articles/<yyyy:year>/', views.year_archive),
]
```

### 7.3 URL 命名与反向解析

```python
# urls.py — 给每个 URL 起个名字
urlpatterns = [
    path('articles/', views.article_list, name='article-list'),
    path('articles/<int:pk>/', views.article_detail, name='article-detail'),
]

# views.py — 通过名称反向获取 URL
from django.urls import reverse

url = reverse('article-detail', args=[1])          # → /articles/1/
url = reverse('article-detail', kwargs={'pk': 1})  # → /articles/1/
url = reverse('article-list')                       # → /articles/

# 模板中反向获取 URL
# {% url 'article-detail' article.id %}
# {% url 'article-list' %}
```

### 7.4 命名空间

```python
# blog/urls.py
app_name = 'blog'  # ← 设置命名空间

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:pk>/', views.detail, name='detail'),
]

# 使用时带命名空间前缀
reverse('blog:index')           # 在 Python 中
# {% url 'blog:detail' pk=1 %}  # 在模板中
```

---

## 八、模板层（Template）

### 8.1 模板配置

```python
# settings.py
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # 全局模板目录（优先级最高）
        'APP_DIRS': True,                   # 是否搜索每个 app 的 templates/ 目录
        'OPTIONS': {
            'context_processors': [         # 上下文处理器（向所有模板注入变量）
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',  # → 模板中可用 {{ user }}
                'django.contrib.messages.context_processors.messages',  # → {{ messages }}
            ],
        },
    },
]
```

### 8.2 模板语法速查

```djangotemplate
{# ========== 变量输出 ========== #}
{{ variable }}
{{ article.title }}
{{ article.pub_date|date:"Y-m-d H:i:s" }}   {# 日期格式化 #}
{{ content|truncatechars:100 }}              {# 截断字符 #}
{{ content|safe }}                            {# 不转义 HTML #}
{{ price|floatformat:2 }}                     {# 保留两位小数 #}
{{ value|default:"默认值" }}                  {# 默认值 #}

{# ========== 标签 ========== #}

{# if 条件判断 #}
{% if user.is_authenticated %}
    <p>欢迎，{{ user.username }}</p>
{% elif user.is_staff %}
    <p>管理员</p>
{% else %}
    <p>请登录</p>
{% endif %}

{# for 循环 #}
{% for article in articles %}
    <h2>{{ article.title }}</h2>
    {{ forloop.counter }}     {# 当前循环序号（从1开始） #}
    {{ forloop.counter0 }}    {# 当前循环序号（从0开始） #}
    {{ forloop.first }}       {# 是否是第一项 #}
    {{ forloop.last }}        {# 是否是最后一项 #}
{% empty %}
    <p>暂无数据</p>
{% endfor %}

{# URL 反向解析 #}
{% url 'blog:detail' article.id %}
{% url 'blog:index' %}

{# 静态文件引用 #}
{% load static %}
<link rel="stylesheet" href="{% static 'css/style.css' %}">
<img src="{% static 'images/logo.png' %}">

{# 媒体文件引用 #}
<img src="{{ user.avatar.url }}">

{# include 包含子模板 #}
{% include 'partials/header.html' %}

{# csrf_token（POST 表单必须） #}
<form method="post">
    {% csrf_token %}
    ...
</form>

{# 模板注释（不会出现在渲染的 HTML 中） #}
{# 这是注释 #}

{# with 定义临时变量 #}
{% with total=articles|length %}
    {{ total }}
{% endwith %}

{# block/extends 模板继承 #}
{% extends 'base.html' %}
{% block title %}页面标题{% endblock %}
{% block content %}
    {{ block.super }}  {# 保留父模板此 block 的内容 #}
    <p>子模板内容</p>
{% endblock %}
```

### 8.3 常用过滤器一览

| 过滤器 | 说明 | 示例 |
|--------|------|------|
| `date:"Y-m-d"` | 日期格式化 | `{{ obj.pub_date\|date:"Y-m-d" }}` |
| `truncatechars:N` | 截取 N 个字符 | `{{ text\|truncatechars:50 }}` |
| `truncatewords:N` | 截取 N 个单词 | `{{ text\|truncatewords:20 }}` |
| `safe` | 不转义 HTML 标签 | `{{ content\|safe }}` |
| `default:"值"` | 变量为空时的默认值 | `{{ value\|default:"-" }}` |
| `length` | 返回列表/字符串长度 | `{{ articles\|length }}` |
| `floatformat:N` | 保留 N 位小数 | `{{ price\|floatformat:2 }}` |
| `add:N` | 加法 | `{{ count\|add:1 }}` |
| `lower` / `upper` | 大小写转换 | `{{ name\|upper }}` |
| `title` | 首字母大写 | `{{ name\|title }}` |
| `join:"分隔符"` | 列表拼接 | `{{ tags\|join:", " }}` |
| `yesno:"是,否,未知"` | 布尔值格式化 | `{{ active\|yesno:"激活,禁用" }}` |
| `pluralize` | 复数形式 | `{{ count }} 条留言{{ count\|pluralize }}` |
| `slugify` | 转换为 URL 友好格式 | `{{ title\|slugify }}` |

### 8.4 模板继承

```djangotemplate
{# ========== base.html（父模板） ========== #}
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}默认标题{% endblock %}</title>
    {% block extra_head %}{% endblock %}
</head>
<body>
    <header>{% block header %}{% endblock %}</header>
    <main>
        {% block content %}
            <p>默认内容</p>
        {% endblock %}
    </main>
    <footer>{% block footer %}{% endblock %}</footer>
    {% block extra_js %}{% endblock %}
</body>
</html>

{# ========== article_list.html（子模板） ========== #}
{% extends 'base.html' %}

{% block title %}文章列表{% endblock %}

{% block content %}
    <h1>文章列表</h1>
    {% for article in articles %}
        <h2><a href="{% url 'article-detail' article.id %}">{{ article.title }}</a></h2>
        <p>{{ article.content|truncatechars:200 }}</p>
    {% empty %}
        <p>暂无文章</p>
    {% endfor %}

    {# 分页 #}
    {% if is_paginated %}
        <div class="pagination">
            {% if page_obj.has_previous %}
                <a href="?page={{ page_obj.previous_page_number }}">上一页</a>
            {% endif %}
            <span>第 {{ page_obj.number }} / {{ page_obj.paginator.num_pages }} 页</span>
            {% if page_obj.has_next %}
                <a href="?page={{ page_obj.next_page_number }}">下一页</a>
            {% endif %}
        </div>
    {% endif %}
{% endblock %}
```

---

## 九、表单（Form）

### 9.1 普通表单（forms.Form）

```python
from django import forms
import re

class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        label='姓名',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入姓名'})
    )
    email = forms.EmailField(label='邮箱', required=True)
    message = forms.CharField(label='留言', widget=forms.Textarea(attrs={'rows': 5}))

    # 自定义字段验证（方法名格式：clean_字段名）
    def clean_name(self):
        name = self.cleaned_data['name']
        if len(name) < 2:
            raise forms.ValidationError('姓名至少2个字符')
        return name

    # 跨字段验证
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        if email and 'test.com' in email:
            raise forms.ValidationError('测试邮箱不允许')
        return cleaned_data
```

### 9.2 模型表单（forms.ModelForm）— 推荐

```python
from django.forms import ModelForm
from .models import Article

class ArticleForm(ModelForm):
    class Meta:
        model = Article
        fields = '__all__'             # 所有字段
        # fields = ['title', 'content']  # 只包含指定字段
        # exclude = ['author']           # 排除指定字段
        widgets = {                    # 自定义控件样式
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'pub_date': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {                     # 自定义标签
            'title': '文章标题',
        }
        help_texts = {                 # 帮助文本
            'title': '请输入一个吸引人的标题',
        }
        error_messages = {             # 自定义错误信息
            'title': {'required': '标题不能为空'},
        }
```

### 9.3 视图中使用表单

```python
from django.shortcuts import render, redirect
from .forms import ArticleForm

def article_create(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)  # 有文件上传时必须传 request.FILES
        if form.is_valid():
            article = form.save()  # ModelForm 的 save() 直接保存到数据库
            return redirect('article-detail', pk=article.id)
    else:
        form = ArticleForm()

    return render(request, 'blog/article_form.html', {'form': form})

def article_edit(request, pk):
    article = Article.objects.get(pk=pk)
    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)  # 传入 instance 表示更新
        if form.is_valid():
            form.save()
            return redirect('article-detail', pk=article.id)
    else:
        form = ArticleForm(instance=article)  # 初始值从已有对象填充

    return render(request, 'blog/article_form.html', {'form': form})
```

### 9.4 模板中渲染表单

```djangotemplate
<form method="post" enctype="multipart/form-data">
    {% csrf_token %}

    {# 方式1：自动渲染（最简洁，但样式不可控） #}
    {{ form.as_p }}

    {# 方式2：逐个字段渲染（推荐，样式可控） #}
    {% for field in form %}
        <div class="form-group">
            {{ field.label_tag }}
            {{ field }}
            {% if field.help_text %}
                <small class="help-text">{{ field.help_text }}</small>
            {% endif %}
            {% if field.errors %}
                <div class="error">{{ field.errors }}</div>
            {% endif %}
        </div>
    {% endfor %}

    <button type="submit">提交</button>
</form>
```

---

## 十、Admin 管理后台

### 10.1 注册模型到 Admin

```python
# blog/admin.py
from django.contrib import admin
from .models import Article, Author, Publisher

# 方式1：简单注册（使用默认配置）
admin.site.register(Author)

# 方式2：使用装饰器注册（推荐）
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    pass

# 方式3：register() 方法
class PublisherAdmin(admin.ModelAdmin):
    pass
admin.site.register(Publisher, PublisherAdmin)
```

### 10.2 ModelAdmin 配置项大全

```python
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    # ========== 列表页配置 ==========
    list_display = ('title', 'author', 'status', 'pub_date', 'view_count')
    # ↑ 列表页展示的字段，支持模型字段和方法

    list_display_links = ('title',)        # 哪些列可点击进入编辑页
    list_editable = ('status',)            # 哪些列可在列表页直接编辑
    list_filter = ('status', 'pub_date')   # 右侧快速筛选
    search_fields = ('title', 'content')   # 搜索框（模糊搜索）
    date_hierarchy = 'pub_date'            # 按日期层级导航
    ordering = ('-pub_date',)              # 默认排序
    list_per_page = 30                     # 每页显示条数（默认100）
    list_select_related = ('author',)      # 预加载关联（解决N+1）
    actions = ['make_published']           # 自定义批量操作

    # ========== 编辑页配置 ==========
    fields = ('title', 'content', 'status')            # 只显示这些字段（顺序可控）
    exclude = ('created_at', 'updated_at')             # 排除这些字段
    readonly_fields = ('created_at', 'updated_at')     # 只读字段
    save_as = True                         # "另存为新对象"功能
    save_on_top = True                     # 顶部也显示保存按钮

    # 字段分组显示
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'content')
        }),
        ('状态信息', {
            'fields': ('status', 'author', 'pub_date'),
            'classes': ('collapse',),      # 默认折叠此分组
        }),
    )

    # ========== 自定义批量操作 ==========
    @admin.action(description='批量发布所选文章')
    def make_published(self, request, queryset):
        updated = queryset.update(status='published')
        self.message_user(request, f'成功发布了 {updated} 篇文章')

    # ========== 自定义列表显示字段 ==========
    @admin.display(description='标题长度')
    def title_length(self, obj):
        return len(obj.title)
```

### 10.3 外键/多对多字段优化

```python
class ArticleAdmin(admin.ModelAdmin):
    # 外键字段优化（数据量大时避免下拉框）
    raw_id_fields = ('author', 'publisher')
    autocomplete_fields = ('author',)     # 带搜索的自动补全（需在关联 ModelAdmin 中定义 search_fields）

    # 多对多字段选择器方向
    filter_horizontal = ('tags', 'categories')   # 水平方向（左右两栏）
    filter_vertical = ('authors',)               # 垂直方向

    # 内联编辑关联表
    # inlines = [CommentInline]

# 内联编辑示例
class CommentInline(admin.TabularInline):   # 或 admin.StackedInline
    model = Comment
    extra = 1              # 默认显示的空行数
    fields = ('author', 'content')
    readonly_fields = ('created_at',)
```

### 10.4 Admin 全局定制

```python
# admin.py
admin.site.site_header = '我的网站管理系统'    # 顶部标题
admin.site.site_title = '管理后台'             # 浏览器标签标题
admin.site.index_title = '功能导航'            # 首页标题
```

---

## 十一、用户认证系统（Auth）

### 11.1 用户操作

```python
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

# 创建用户
user = User.objects.create_user(
    username='zhangsan',
    email='zhangsan@example.com',
    password='securepass123'
)

# 创建超级用户（或用命令：python manage.py createsuperuser）
User.objects.create_superuser(username='admin', email='admin@example.com', password='admin123')

# 校验登录
user = authenticate(request, username='zhangsan', password='securepass123')
if user is not None:
    login(request, user)   # 将用户写入 session
    # 之后 request.user 就是当前用户
else:
    # 用户名或密码错误

# 判断是否登录
if request.user.is_authenticated:
    print(f'当前用户：{request.user.username}')

# 检查密码
request.user.check_password('old_password')

# 修改密码
request.user.set_password('new_secure_password')
request.user.save()  # 必须 save

# 退出登录
logout(request)
# 注意：logout 后 request.user 变为 AnonymousUser
```

### 11.2 登录保护

```python
# 函数视图 — 装饰器
from django.contrib.auth.decorators import login_required

@login_required(login_url='/login/')  # 未登录跳转到 /login/
def protected_view(request):
    return HttpResponse('此页面需要登录')

# 类视图 — Mixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

class ProtectedListView(LoginRequiredMixin, ListView):
    login_url = '/login/'
    model = Article
```

### 11.3 扩展自定义用户模型（推荐在项目开始时做）

```python
# models.py
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """扩展默认 User，添加手机号、头像等字段"""
    phone = models.CharField(max_length=11, blank=True, verbose_name='手机号')
    avatar = models.ImageField(upload_to='avatars/', blank=True, verbose_name='头像')
    bio = models.TextField(blank=True, verbose_name='个人简介')

    class Meta:
        db_table = 'users'

# settings.py — 必须在首次 migrate 前配置！
AUTH_USER_MODEL = 'yourapp.User'

# 之后所有地方都用 settings.AUTH_USER_MODEL 引用用户模型
from django.conf import settings
from django.contrib.auth import get_user_model
User = get_user_model()  # 推荐方式
```

---

## 十二、中间件（Middleware）

### 12.1 内置中间件顺序与职责

```
请求进入
    ↓
1. SecurityMiddleware          — 安全请求头、HTTPS重定向
2. SessionMiddleware           — Session 管理
3. CommonMiddleware            — URL 规范化（斜杠追加、禁止User-Agent）
4. CsrfViewMiddleware          — CSRF Token 验证
5. AuthenticationMiddleware    — 将用户绑定到 request.user
6. MessageMiddleware           — 消息框架（flash message）
7. XFrameOptionsMiddleware     — 防点击劫持
    ↓
视图函数/类
    ↓
响应阶段反向执行（7 → 1）
```

### 12.2 自定义中间件

```python
# blog/middleware.py
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden
import time

class RequestTimingMiddleware(MiddlewareMixin):
    """记录每个请求的处理时间"""

    def process_request(self, request):
        request._start_time = time.time()
        # 返回 None 继续处理，返回 HttpResponse 直接返回

    def process_response(self, request, response):
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            response['X-Request-Duration'] = f'{duration:.3f}s'
        return response  # process_response 必须返回 response


class IPBlacklistMiddleware(MiddlewareMixin):
    """IP 黑名单中间件"""
    BLACKLIST = ['192.168.1.100']

    def process_request(self, request):
        ip = request.META.get('REMOTE_ADDR')
        if ip in self.BLACKLIST:
            return HttpResponseForbidden('您的 IP 已被禁止访问')
```

注册中间件：

```python
# settings.py
MIDDLEWARE = [
    # ... 默认中间件 ...
    'blog.middleware.RequestTimingMiddleware',
    'blog.middleware.IPBlacklistMiddleware',
]
```

---

## 十三、信号（Signals）

### 13.1 Django 内置信号一览

| 信号 | 触发时机 | 参数 |
|------|---------|------|
| `pre_init` | Model `__init__()` 开始前 | sender, args, kwargs |
| `post_init` | Model `__init__()` 完成后 | sender, instance |
| `pre_save` | Model `save()` 开始前 | sender, instance, raw, using |
| `post_save` | Model `save()` 完成后 | sender, instance, created, raw, using |
| `pre_delete` | Model `delete()` 开始前 | sender, instance, using |
| `post_delete` | Model `delete()` 完成后 | sender, instance, using |
| `m2m_changed` | ManyToManyField 变更时 | sender, instance, action, pk_set |
| `request_started` | HTTP 请求开始时 | sender, environ |
| `request_finished` | HTTP 请求结束时 | sender |
| `pre_migrate` | `migrate` 命令开始前 | sender, app_config, verbosity, plan |
| `post_migrate` | `migrate` 命令完成后 | sender, app_config, verbosity, plan |

### 13.2 使用信号

```python
# blog/signals.py
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Article

# 方式1：装饰器注册（推荐）
@receiver(post_save, sender=Article)
def article_post_save(sender, instance, created, **kwargs):
    if created:
        print(f'新文章创建了：{instance.title}')
        # 发送通知邮件
        # send_mail(f'新文章：{instance.title}', '', 'noreply@example.com', ['admin@example.com'])

# 方式2：手动连接
def article_pre_save_handler(sender, instance, **kwargs):
    print(f'文章即将保存：{instance.title}')

pre_save.connect(article_pre_save_handler, sender=Article)
```

在 App 配置中导入信号文件，确保信号被注册：

```python
# blog/apps.py
from django.apps import AppConfig

class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'

    def ready(self):
        import blog.signals  # 导入信号
```

---

## 十四、缓存（Cache）

### 14.1 缓存后端配置

```python
# ========== Redis（推荐） ==========
# pip install django-redis
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'TIMEOUT': 300,                  # 默认过期时间（秒）
        'KEY_PREFIX': 'myproject-',      # key 前缀（避免冲突）
        'OPTIONS': {
            'MAX_ENTRIES': 1000,         # 最大条目数
        },
    }
}

# ========== 本地内存（开发用） ==========
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# ========== 文件缓存 ==========
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/django_cache',
    }
}

# ========== 数据库缓存 ==========
# 先执行：python manage.py createcachetable
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'my_cache_table',
    }
}
```

### 14.2 缓存使用方式

```python
# ========== 方式1：手动操作缓存 API ==========
from django.core.cache import cache

cache.set('key', 'value', timeout=60)     # 设置，60秒过期
value = cache.get('key')                  # 获取
value = cache.get('key', 'default')       # 获取（带默认值）
cache.get_or_set('key', 'computed', 60)   # 获取或设置
cache.set_many({'k1': 'v1', 'k2': 'v2'})  # 批量设置
cache.get_many(['k1', 'k2'])              # 批量获取
cache.delete('key')                       # 删除
cache.clear()                             # 清空所有
cache.incr('counter')                     # 自增
cache.decr('counter')                     # 自减

# ========== 方式2：视图级别缓存 ==========
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # 缓存 15 分钟
def my_view(request):
    # 第一次请求执行此处逻辑，后续直接返回缓存
    return render(request, 'my_template.html')
```

---

## 十五、执行原生 SQL

### 15.1 raw() 方法 — 执行 SELECT 返回模型实例

```python
# 基本用法
for article in Article.objects.raw('SELECT * FROM blog_article'):
    print(article.title)

# 参数化查询（防 SQL 注入）
Article.objects.raw(
    'SELECT * FROM blog_article WHERE title LIKE %s',
    ['%Django%']
)

# 添加自定义字段到结果
articles = Article.objects.raw(
    "SELECT *, DATE_FORMAT(pub_date, '%%Y-%%m') AS pub_month FROM blog_article"
)
for a in articles:
    print(a.pub_month)  # 自定义字段

# ⚠️ raw() 只能执行 SELECT！INSERT/UPDATE/DELETE 必须用 cursor
```

### 15.2 connection.cursor() — 执行任意 SQL（最灵活）

```python
from django.db import connection

# ========== 执行查询 ==========
with connection.cursor() as cursor:
    cursor.execute("SELECT id, title FROM blog_article WHERE status = %s", ['published'])
    rows = cursor.fetchall()   # 返回元组列表：[(1, '标题1'), (2, '标题2')]
    row = cursor.fetchone()    # 返回单行：(1, '标题1')

# ========== 转换为字典列表（带字段名） ==========
def dictfetchall(cursor):
    """将 cursor 结果转为字典列表"""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

with connection.cursor() as cursor:
    cursor.execute("SELECT id, title FROM blog_article LIMIT 10")
    results = dictfetchall(cursor)
# 结果: [{'id': 1, 'title': '标题1'}, {'id': 2, 'title': '标题2'}]

# ========== 执行 INSERT/UPDATE/DELETE ==========
with connection.cursor() as cursor:
    cursor.execute("INSERT INTO blog_article (title, content) VALUES (%s, %s)",
                   ['新文章', '内容'])
    cursor.execute("UPDATE blog_article SET status = %s WHERE id = %s",
                   ['published', 1])
    cursor.execute("DELETE FROM blog_article WHERE status = %s", ['archived'])

# ========== 执行 DDL（创建索引、修改表结构等） ==========
with connection.cursor() as cursor:
    cursor.execute("CREATE INDEX idx_title ON blog_article(title)")
```

### 15.3 多数据库

```python
from django.db import connections

with connections['analytics'].cursor() as cursor:
    cursor.execute("SELECT * FROM analytics_table")
    rows = cursor.fetchall()
```

### 15.4 ORM 扩展：extra()（不推荐，了解即可）

```python
# extra() 已不推荐使用，但可能在老项目中遇到
Article.objects.extra(
    where=["status = %s"],
    params=['published']
)
# 官方建议用 raw() 或 cursor() 代替
```

---

## 十六、文件上传

### 16.1 配置

```python
# settings.py
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# urls.py（主路由文件）
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ... 你的路由 ...
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# ⚠️ 仅开发环境用！生产环境由 Nginx/Apache 处理媒体文件
```

### 16.2 模型定义

```python
class Document(models.Model):
    title = models.CharField(max_length=100)
    file = models.FileField(
        upload_to='documents/%Y/%m/',  # 按年月分子目录存储
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])],
        max_length=100,
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Profile(models.Model):
    avatar = models.ImageField(
        upload_to='avatars/%Y/%m/',
        default='avatars/default.png',
        height_field='avatar_height',
        width_field='avatar_width',
    )
    avatar_height = models.IntegerField(default=0)
    avatar_width = models.IntegerField(default=0)
```

### 16.3 视图接收文件

```python
# 表单定义
class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'file']

# 视图处理
def upload_file(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)  # ← 必须传 request.FILES
        if form.is_valid():
            doc = form.save()
            return redirect('success')
    else:
        form = DocumentForm()
    return render(request, 'upload.html', {'form': form})
```

### 16.4 模板

```djangotemplate
<form method="post" enctype="multipart/form-data">  <!-- enctype 必须！ -->
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">上传</button>
</form>

<!-- 显示已上传的文件 -->
{% if document.file %}
    <a href="{{ document.file.url }}" download>下载</a>
    <img src="{{ profile.avatar.url }}" alt="头像">
{% endif %}
```

---

## 十七、Django REST Framework（DRF）

### 17.1 安装与配置

```bash
pip install djangorestframework
pip install django-filter      # 过滤支持（可选）
```

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'rest_framework',
]

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    # 'EXCEPTION_HANDLER': 'myapp.exceptions.custom_exception_handler',
}
```

### 17.2 Serializer（序列化器）

```python
from rest_framework import serializers
from .models import Article, Author

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name']
        # fields = '__all__'
        # exclude = ['created_at']
        read_only_fields = ['id']

class ArticleSerializer(serializers.ModelSerializer):
    # 嵌套序列化：展示作者详情而非仅 ID
    author = AuthorSerializer(read_only=True)
    # 只接受 author_id 写入
    author_id = serializers.IntegerField(write_only=True)

    # 自定义只读字段
    word_count = serializers.SerializerMethodField()

    def get_word_count(self, obj):
        return len(obj.content)

    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'author', 'author_id',
                  'status', 'pub_date', 'word_count']
        read_only_fields = ['pub_date']

    # 自定义验证
    def validate_title(self, value):
        if len(value) < 2:
            raise serializers.ValidationError('标题不能少于2个字符')
        return value

    def validate(self, data):
        """跨字段验证"""
        if data.get('status') == 'published' and not data.get('content'):
            raise serializers.ValidationError('发布文章必须有内容')
        return data
```

### 17.3 ViewSet + Router（推荐方案，代码最少）

```python
# views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Article
from .serializers import ArticleSerializer

class ArticleViewSet(viewsets.ModelViewSet):
    """
    自动提供 list / create / retrieve / update / partial_update / destroy
    """
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """按需过滤（根据请求参数）"""
        qs = super().get_queryset()
        status = self.request.query_params.get('status')
        if status:
            qs = qs.filter(status=status)
        return qs

    def perform_create(self, serializer):
        """创建时自动设置作者为当前用户"""
        serializer.save(author=self.request.user)
```

```python
# urls.py
from rest_framework.routers import DefaultRouter
from .views import ArticleViewSet

router = DefaultRouter()
router.register(r'articles', ArticleViewSet, basename='article')

urlpatterns = [
    path('api/', include(router.urls)),
]
```

**自动生成的路由：**
| 方法 | URL | 操作 |
|------|-----|------|
| GET | `/api/articles/` | 列表 |
| POST | `/api/articles/` | 创建 |
| GET | `/api/articles/{id}/` | 详情 |
| PUT | `/api/articles/{id}/` | 完整更新 |
| PATCH | `/api/articles/{id}/` | 部分更新 |
| DELETE | `/api/articles/{id}/` | 删除 |

### 17.4 APIView（灵活但代码较多）

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

class ArticleAPIView(APIView):
    def get(self, request):
        articles = Article.objects.all()
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ArticleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ArticleDetailAPIView(APIView):
    def get(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        serializer = ArticleSerializer(article)
        return Response(serializer.data)

    def put(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        serializer = ArticleSerializer(article, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        article.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
```

### 17.5 分页、过滤、搜索

```python
# 基于 DjangoFilterBackend 的过滤
# pip install django-filter

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'author']                       # ?status=published&author=1
    search_fields = ['title', 'content']                          # ?search=Python
    ordering_fields = ['pub_date', 'view_count']                  # ?ordering=-pub_date
```

---

## 十八、manage.py 命令大全

### 18.1 常用命令速查

| 命令 | 说明 |
|------|------|
| `python manage.py runserver` | 启动开发服务器 |
| `python manage.py startapp <名称>` | 创建新 App |
| `python manage.py makemigrations` | 生成迁移文件 |
| `python manage.py migrate` | 执行数据库迁移 |
| `python manage.py createsuperuser` | 创建超级管理员 |
| `python manage.py shell` | 打开 Django 交互式 shell |
| `python manage.py dbshell` | 打开数据库交互终端 |
| `python manage.py test` | 运行测试 |
| `python manage.py collectstatic` | 收集静态文件（生产环境用） |
| `python manage.py check` | 检查项目完整性问题 |
| `python manage.py help` | 列出所有可用命令 |

### 18.2 全部命令

```bash
# 数据库
python manage.py makemigrations        # 生成迁移文件
python manage.py migrate               # 执行迁移
python manage.py showmigrations        # 查看迁移状态（[x] 已执行，[ ] 未执行）
python manage.py sqlmigrate app 0001   # 查看迁移对应的 SQL
python manage.py flush                 # 清空数据库数据（保留表结构）
python manage.py dbshell               # 数据库命令行
python manage.py inspectdb             # 反向生成 Model（从已有数据库）
python manage.py inspectdb > models.py # 输出到文件

# 用户
python manage.py createsuperuser       # 创建超级用户
python manage.py changepassword 用户名  # 修改密码
python manage.py clearsessions         # 清除过期 session

# 数据导入/导出
python manage.py dumpdata app.Model > data.json  # 导出数据为 JSON
python manage.py dumpdata --indent 2 app > data.json  # 格式化导出
python manage.py loaddata data.json    # 导入数据

# 静态文件
python manage.py collectstatic         # 收集所有静态文件到一个目录
python manage.py findstatic css/style.css  # 查找静态文件路径

# 测试/检查
python manage.py test                  # 运行所有测试
python manage.py test app.tests        # 运行指定模块测试
python manage.py test app.tests.TestCase.test_method  # 运行指定测试方法
python manage.py check                 # 检查项目完整性
python manage.py check --deploy        # 生产环境安全检查
python manage.py diffsettings          # 显示配置与默认值的差异

# 交互
python manage.py shell                 # Django shell（推荐用 shell_plus：pip install django-extensions）
python manage.py shell -c "from blog.models import Article; print(Article.objects.count())"

# 国际化
python manage.py makemessages -l zh_Hans  # 提取翻译字符串
python manage.py compilemessages          # 编译翻译文件

# 邮件测试
python manage.py sendtestemail admin@example.com

# 缓存
python manage.py createcachetable       # 创建数据库缓存表

# 其他
python manage.py help                   # 命令列表
python manage.py version                # 查看 Django 版本
python manage.py show_urls              # 列出所有 URL（需要 django-extensions）
python manage.py runserver_plus         # 增强版开发服务器（django-extensions）
python manage.py runscript my_script    # 运行脚本（django-extensions）
```

### 18.3 开发工作流

```bash
# 1. 创建项目
django-admin startproject myproject
cd myproject

# 2. 创建 App
python manage.py startapp blog

# 3. 修改 models.py → 迁移
python manage.py makemigrations
python manage.py migrate

# 4. 创建管理员
python manage.py createsuperuser

# 5. 开发中循环
# 修改代码 → 浏览器刷新（开发服务器自动重载）
python manage.py runserver

# 6. 运行测试
python manage.py test

# 7. 调试
python manage.py shell    # 交互式测试 ORM 查询等

# 8. 生产部署前
python manage.py check --deploy
python manage.py collectstatic
```

---

## 十九、常用代码片段速查

### 项目结构最佳实践

```
myproject/
├── manage.py
├── requirements.txt          # pip freeze > requirements.txt
├── myproject/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/                     # 所有 App 放一起（可选）
│   ├── blog/
│   ├── users/
│   └── api/
├── static/                   # 全局静态文件
│   ├── css/
│   ├── js/
│   └── images/
├── media/                    # 用户上传文件
├── templates/                # 全局模板
│   ├── base.html
│   └── includes/
└── .env                      # 环境变量（不入 Git）
```

### 常见问题排查

```python
# 1. 查看 ORM 生成的 SQL（调试神器）
print(Article.objects.filter(status='published').query)

# 2. 查看所有已执行的 SQL
from django.db import connection, reset_queries
from django.conf import settings
if settings.DEBUG:
    print(len(connection.queries))
    for q in connection.queries:
        print(q['sql'], q['time'])
    reset_queries()  # 清空查询记录

# 3. 获取对象的原始字段值
article = Article.objects.get(id=1)
article.title = '新标题'
article.get_deferred_fields()  # 哪些字段未加载
Article.objects.get(id=1).__dict__  # 所有字段值字典

# 4. 强制刷新对象（从数据库重新加载）
article.refresh_from_db()

# 5. 对比两个对象的值
article1 = Article.objects.get(id=1)
article2 = Article.objects.get(id=2)
# diff = {k: (v, getattr(article2, k)) for k, v in article1.__dict__.items() if k != '_state'}
```

### 常用 pip 包推荐

```bash
# 核心依赖
pip install django

# 数据库
pip install mysqlclient        # MySQL
pip install psycopg2-binary    # PostgreSQL
pip install django-redis       # Redis缓存

# REST API
pip install djangorestframework
pip install django-filter      # DRF 过滤
pip install django-cors-headers  # 跨域 CORS

# 调试和开发
pip install django-extensions  # shell_plus、show_urls 等实用命令
pip install django-debug-toolbar  # 调试工具栏

# 认证
pip install djangorestframework-simplejwt  # JWT 认证

# 生产部署
pip install gunicorn           # WSGI 服务器
pip install uvicorn            # ASGI 服务器
```

### 安全注意事项清单

| 项目 | 说明 |
|------|------|
| `SECRET_KEY` | 生产环境必须强随机，不准放代码仓库，用环境变量 |
| `DEBUG = False` | 生产环境必须关闭，否则错误页面会暴露代码细节 |
| `ALLOWED_HOSTS` | 生产必须设置正确的域名，不可是 `['*']` |
| CSRF | POST 表单必须加 `{% csrf_token %}` |
| SQL 注入 | 使用 ORM 或 参数化查询，绝对不要拼字符串 |
| XSS | 模板默认转义 HTML，如需渲染 HTML 用 `safe` 但要确保内容可信 |
| 文件上传 | 限制文件类型和大小，不在 URL 中暴露文件路径 |
| 密码 | 始终用 `create_user()` 而非 `User(username='xxx', password='明文的密码')` |
| HTTPS | 生产环境必须开启 HTTPS，设置 `SECURE_SSL_REDIRECT = True` 等安全头 |
| 数据库 | 不用默认 SQLite 数据库密码，生产数据库用强密码 |

---

## 二十、实战示例：完整 CRUD

### 20.1 Model 定义

```python
# blog/models.py
from django.db import models
from django.urls import reverse

class Category(models.Model):
    """文章分类"""
    name = models.CharField(max_length=50, unique=True, verbose_name='分类名称')
    slug = models.SlugField(max_length=60, unique=True, verbose_name='URL 别名')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '文章分类'
        verbose_name_plural = '文章分类'
        ordering = ['name']  # 按名称排序

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """获取分类的规范 URL（Admin 中"查看"按钮使用）"""
        return reverse('category-detail', kwargs={'slug': self.slug})


class Article(models.Model):
    """文章模型 — 完整示例"""
    # 状态选项常量定义
    STATUS_DRAFT = 'draft'
    STATUS_PUBLISHED = 'published'
    STATUS_ARCHIVED = 'archived'
    STATUS_CHOICES = [
        (STATUS_DRAFT, '草稿'),
        (STATUS_PUBLISHED, '已发布'),
        (STATUS_ARCHIVED, '已归档'),
    ]

    title = models.CharField(max_length=200, verbose_name='标题')
    slug = models.SlugField(max_length=250, unique=True, verbose_name='URL 别名')
    content = models.TextField(verbose_name='正文内容')
    excerpt = models.TextField(blank=True, verbose_name='摘要')

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default=STATUS_DRAFT, verbose_name='状态'
    )

    category = models.ForeignKey(
        Category, on_delete=models.CASCADE,   # 分类删除时，文章级联删除
        related_name='articles',              # 反向查询：category.articles.all()
        verbose_name='所属分类'
    )

    cover_image = models.ImageField(
        upload_to='covers/%Y/%m/',            # 上传到 media/covers/2025/01/ 目录
        blank=True, null=True, verbose_name='封面图'
    )

    view_count = models.PositiveIntegerField(default=0, verbose_name='阅读量')
    is_featured = models.BooleanField(default=False, verbose_name='是否推荐')

    # auto_now_add: 创建时自动设置时间（之后不可更新）
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    # auto_now: 每次 save() 时自动更新为当前时间
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'articles'  # 自定义数据库表名
        ordering = ['-created_at']  # 默认按创建时间降序排列
        verbose_name = '文章'
        verbose_name_plural = '文章'
        indexes = [
            models.Index(fields=['status', '-created_at']),  # 联合索引：加速按状态+时间筛选
            models.Index(fields=['slug']),                   # slug 索引：加速 URL 查找
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """文章的规范 URL（redirect 和 Admin "查看"按钮会调用）"""
        return reverse('blog:article-detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        """保存前自动从标题生成 slug（如果 slug 为空）"""
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
```

### 20.2 Form 表单定义

```python
# blog/forms.py
from django import forms
from .models import Article

class ArticleForm(forms.ModelForm):
    """文章表单 — 用于创建和编辑，ModelForm 自动根据模型生成字段"""

    class Meta:
        model = Article
        fields = ['title', 'slug', 'content', 'excerpt',
                  'status', 'category', 'cover_image', 'is_featured']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',          # CSS 类（Bootstrap 样式）
                'placeholder': '请输入文章标题',
                'autofocus': True,                # 页面加载后自动获取焦点
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '留空则自动从标题生成',
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 15,
                'placeholder': '请输入文章正文...',
            }),
            'excerpt': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '文章摘要（可选，留空则自动截取正文前200字）',
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'cover_image': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {'title': '文章标题', 'content': '正文内容', 'excerpt': '摘要'}
        help_texts = {
            'slug': 'URL 中的标识符，由字母、数字、连字符组成',
        }

    def clean_title(self):
        """自定义字段校验：标题至少需要2个字符"""
        title = self.cleaned_data['title']
        if len(title.strip()) < 2:
            raise forms.ValidationError('标题至少需要2个字符')
        return title

    def clean(self):
        """跨字段校验：已发布的文章必须有正文内容"""
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        content = cleaned_data.get('content')
        if status == 'published' and not content:
            raise forms.ValidationError('已发布的文章不能没有正文内容！')
        return cleaned_data
```

### 20.3 View 视图（带错误处理、日志、分页）

```python
# blog/views.py
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import F, Q, Count
from django.db import DatabaseError
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import Http404
from .models import Article, Category
from .forms import ArticleForm

logger = logging.getLogger('blog')


def article_list(request):
    """
    文章列表页
    - 支持分类过滤（URL参数 ?category=slug）
    - 支持搜索（URL参数 ?q=关键词）
    - 只显示已发布的文章
    - 支持分页（URL参数 ?page=页码）
    """
    # 基础查询：只查已发布文章，用 select_related 预加载分类（避免 N+1 查询）
    article_qs = Article.objects.filter(status='published').select_related('category')

    # 按分类过滤（如果 URL 中传了 category 参数）
    category_slug = request.GET.get('category')
    if category_slug:
        article_qs = article_qs.filter(category__slug=category_slug)

    # 按关键词搜索（搜索标题和内容）
    search_query = request.GET.get('q')
    if search_query:
        article_qs = article_qs.filter(
            Q(title__icontains=search_query) | Q(content__icontains=search_query)
        )

    # 分页：每页10条
    paginator = Paginator(article_qs, 10)
    page = request.GET.get('page', 1)
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)       # 页码不是整数，跳转到第1页
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)  # 页码超出范围，跳转到最后一页

    # 获取全部分类及文章数（只显示有已发布文章的分类）
    categories = Category.objects.annotate(
        article_count=Count('articles', filter=Q(articles__status='published'))
    ).filter(article_count__gt=0)

    context = {
        'articles': articles,                # 当前页的文章对象
        'categories': categories,            # 全部分类（含文章计数）
        'current_category': category_slug,   # 当前选中的分类
        'search_query': search_query,        # 当前搜索关键词
        'is_paginated': articles.has_other_pages(),  # 是否需要显示分页导航
    }
    return render(request, 'blog/article_list.html', context)


def article_detail(request, slug):
    """文章详情页 — 阅读量原子+1"""
    article = get_object_or_404(
        Article.objects.select_related('category'),  # 预加载分类信息
        slug=slug, status='published'                # 非已发布状态也返回404
    )

    # 用 F 对象原子更新阅读量（避免并发竞态条件）
    # SQL: UPDATE articles SET view_count = view_count + 1 WHERE id = xxx
    Article.objects.filter(pk=article.pk).update(view_count=F('view_count') + 1)
    article.refresh_from_db()  # 从数据库重新加载，获取最新的 view_count

    # 获取相关文章（同分类下其他文章，最多5条）
    related_articles = Article.objects.filter(
        category=article.category, status='published'
    ).exclude(pk=article.pk)[:5]

    logger.info(f'查看文章: id={article.pk}, title={article.title}')  # 记录日志

    return render(request, 'blog/article_detail.html', {
        'article': article,
        'related_articles': related_articles,
    })


@login_required(login_url='/accounts/login/')  # 未登录用户重定向到登录页
def article_create(request):
    """
    创建文章
    - GET 请求：显示空表单
    - POST 请求：校验并保存
    """
    if request.method == 'POST':
        # POST 请求需要同时传递 POST 数据和上传的文件
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save()       # ModelForm.save() 直接保存到数据库
            logger.info(f'文章已创建: id={article.pk}')
            return redirect(article)    # redirect 可接收模型对象（自动调用 get_absolute_url）
        # is_valid() 失败时，form 中包含错误信息，下面继续渲染
    else:
        form = ArticleForm()  # GET 请求：显示空表单

    return render(request, 'blog/article_form.html', {
        'form': form,
        'action': '创建',  # 告诉模板当前是创建模式
    })


@login_required(login_url='/accounts/login/')
def article_edit(request, slug):
    """
    编辑文章
    - 传入 instance 参数，form 会自动用已有对象的数据填充表单
    """
    article = get_object_or_404(Article, slug=slug)
    if request.method == 'POST':
        # instance=article 表示更新已有对象而非新建
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            logger.info(f'文章已更新: id={article.pk}')
            return redirect(article)
    else:
        form = ArticleForm(instance=article)  # 用已有数据填充表单

    return render(request, 'blog/article_form.html', {
        'form': form,
        'article': article,
        'action': '编辑',
    })


@login_required(login_url='/accounts/login/')
def article_delete(request, slug):
    """删除文章 — 要求 POST 确认（防止误删和 CSRF 攻击）"""
    article = get_object_or_404(Article, slug=slug)
    if request.method == 'POST':
        article.delete()
        logger.info(f'文章已删除: slug={slug}')
        return redirect('blog:article-list')
    # GET 请求时显示确认页面
    return render(request, 'blog/article_confirm_delete.html', {'article': article})
```

### 20.4 URL 路由配置

```python
# blog/urls.py
from django.urls import path
from . import views

app_name = 'blog'  # 设置命名空间，使用时: {% url 'blog:xxx' %}

urlpatterns = [
    # 文章列表页：/blog/
    path('', views.article_list, name='article-list'),
    # 文章详情页：/blog/article/hello-world/
    path('article/<slug:slug>/', views.article_detail, name='article-detail'),
    # 创建文章：/blog/create/
    path('create/', views.article_create, name='article-create'),
    # 编辑文章：/blog/article/hello-world/edit/
    path('article/<slug:slug>/edit/', views.article_edit, name='article-edit'),
    # 删除文章：/blog/article/hello-world/delete/
    path('article/<slug:slug>/delete/', views.article_delete, name='article-delete'),
    # 分类文章列表：/blog/category/python/
    path('category/<slug:slug>/', views.article_list, name='category-detail'),
]
```

### 20.5 模板

```djangotemplate
{# templates/blog/base.html — 基础父模板 #}
{% load static %}
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>{% block title %}我的博客{% endblock %}</title>
    <link rel="stylesheet" href="{% static 'css/style.css' %}">
    {% block extra_head %}{% endblock %}
</head>
<body>
    <header>
        <nav>
            <a href="{% url 'blog:article-list' %}">首页</a>
            {% if user.is_authenticated %}
                <a href="{% url 'blog:article-create' %}">写文章</a>
                <span>你好，{{ user.username }}</span>
                <a href="/accounts/logout/">退出</a>
            {% else %}
                <a href="/accounts/login/">登录</a>
            {% endif %}
        </nav>
    </header>

    <main>{% block content %}{% endblock %}</main>

    <footer><p>&copy; 2025 我的博客</p></footer>
</body>
</html>


{# templates/blog/article_list.html — 文章列表页（继承 base.html） #}
{% extends 'blog/base.html' %}

{% block title %}文章列表{% endblock %}

{% block content %}
    <h1>文章列表</h1>

    {# 搜索表单 #}
    <form method="get">
        <!-- 保留 category 参数，避免搜索时丢失分类过滤 -->
        {% if current_category %}
            <input type="hidden" name="category" value="{{ current_category }}">
        {% endif %}
        <input type="text" name="q" value="{{ search_query|default:'' }}" placeholder="搜索文章...">
        <button type="submit">搜索</button>
    </form>

    {# 分类导航 #}
    <nav>
        <a href="{% url 'blog:article-list' %}" {% if not current_category %}class="active"{% endif %}>全部</a>
        {% for cat in categories %}
            <a href="{% url 'blog:category-detail' cat.slug %}"
               {% if current_category == cat.slug %}class="active"{% endif %}>
                {{ cat.name }}（{{ cat.article_count }}）
            </a>
        {% endfor %}
    </nav>

    {# 文章列表 #}
    {% for article in articles %}
        <article>
            <h2><a href="{% url 'blog:article-detail' article.slug %}">{{ article.title }}</a></h2>
            <div class="meta">
                <span>{{ article.category.name }}</span>
                <span>{{ article.created_at|date:"Y-m-d" }}</span>
                <span>{{ article.view_count }} 次阅读</span>
            </div>
            <!-- excerpt 为空时，截取 content 前200个字符作为摘要 -->
            <p>{{ article.excerpt|default:article.content|truncatechars:200 }}</p>
        </article>
    {% empty %}
        <p>暂无文章</p>
    {% endfor %}

    {# 分页导航 #}
    {% if is_paginated %}
        <div class="pagination">
            {% if articles.has_previous %}
                <a href="?page={{ articles.previous_page_number }}{% if search_query %}&q={{ search_query }}{% endif %}">上一页</a>
            {% endif %}
            <span>第 {{ articles.number }} 页 / 共 {{ articles.paginator.num_pages }} 页</span>
            {% if articles.has_next %}
                <a href="?page={{ articles.next_page_number }}{% if search_query %}&q={{ search_query }}{% endif %}">下一页</a>
            {% endif %}
        </div>
    {% endif %}
{% endblock %}


{# templates/blog/article_form.html — 创建/编辑文章表单 #}
{% extends 'blog/base.html' %}

{% block title %}{{ action }}文章{% endblock %}

{% block content %}
    <h1>{{ action }}文章</h1>

    {# enctype="multipart/form-data" 不可省略！否则文件无法上传 #}
    <form method="post" enctype="multipart/form-data" novalidate>
        {% csrf_token %}

        {% for field in form %}
            <div class="form-group {% if field.errors %}has-error{% endif %}">
                <label for="{{ field.id_for_label }}">
                    {{ field.label }}
                    {% if field.field.required %}<span class="required">*</span>{% endif %}
                </label>

                {{ field }}

                {% if field.help_text %}
                    <small class="help-text">{{ field.help_text }}</small>
                {% endif %}

                {# 逐个显示该字段的校验错误 #}
                {% for error in field.errors %}
                    <div class="error-text">{{ error }}</div>
                {% endfor %}
            </div>
        {% endfor %}

        {# 显示非字段错误（跨字段验证失败时） #}
        {% for error in form.non_field_errors %}
            <div class="alert alert-danger">{{ error }}</div>
        {% endfor %}

        <button type="submit" class="btn btn-primary">保存</button>
        <a href="{% url 'blog:article-list' %}" class="btn btn-secondary">取消</a>
    </form>
{% endblock %}
```

### 20.6 Admin 后台注册

```python
# blog/admin.py
from django.contrib import admin
from .models import Article, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')    # 列表页展示的列
    search_fields = ('name',)                         # 允许搜索的字段
    prepopulated_fields = {'slug': ('name',)}         # 输入 name 时自动填充 slug


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    # ===== 列表页 =====
    list_display = ('title', 'category', 'status', 'is_featured',
                    'view_count', 'created_at')
    list_filter = ('status', 'is_featured', 'category', 'created_at')
    search_fields = ('title', 'content')              # 搜索标题和内容
    list_editable = ('status', 'is_featured')         # 列表页可直接编辑
    list_per_page = 30                                # 每页显示30条
    date_hierarchy = 'created_at'                     # 按日期层级导航
    ordering = ('-created_at',)                       # 默认排序

    # ===== 编辑页 =====
    prepopulated_fields = {'slug': ('title',)}        # 输入标题时自动填充 slug
    readonly_fields = ('view_count', 'created_at', 'updated_at')  # 只读字段
    save_on_top = True                                # 表单顶部也显示保存按钮

    # 字段分组显示
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'slug', 'content', 'excerpt', 'cover_image')
        }),
        ('分类与状态', {
            'fields': ('category', 'status', 'is_featured')
        }),
        ('统计数据', {
            'fields': ('view_count', 'created_at', 'updated_at'),
            'classes': ('collapse',),                 # 默认折叠，点击展开
        }),
    )
```

---

## 二十一、高级技巧

### 21.1 数据库事务（原子操作）

```python
from django.db import transaction, DatabaseError

# ===== 方式1：装饰器 =====
@transaction.atomic
def transfer_money(from_account_id, to_account_id, amount):
    """
    转账操作：两个账户的更新要么都成功，要么都回滚。
    一旦函数内任何地方抛出异常，所有数据库操作自动回滚。
    """
    # select_for_update() 锁定这两行数据，防止并发修改
    from_account = Account.objects.select_for_update().get(id=from_account_id)
    to_account = Account.objects.select_for_update().get(id=to_account_id)

    if from_account.balance < amount:
        raise ValueError('余额不足！')  # 抛出异常 → 自动回滚

    from_account.balance -= amount
    from_account.save()

    to_account.balance += amount
    to_account.save()
    # 函数正常结束 → 自动提交数据库事务

# ===== 方式2：上下文管理器 =====
def batch_update_articles(article_ids, new_status):
    """批量更新文章状态：任意一条失败，全部回滚"""
    try:
        with transaction.atomic():
            for aid in article_ids:
                article = Article.objects.get(id=aid)
                article.status = new_status
                article.save()
            # 全部保存成功后才提交
    except DatabaseError as e:
        # 任何一条出错，with 块内的所有修改全部回滚
        print(f'批量更新失败，已全部回滚：{e}')

# ===== 保存点（嵌套事务） =====
@transaction.atomic
def complex_operation():
    """外层事务：部分子操作失败不影响主流程"""
    # 主操作先执行...
    try:
        with transaction.atomic():
            # 子操作（独立的保存点）
            # 如果子操作失败，只回滚子操作，外层继续
            do_something_risky()
    except ValueError:
        pass  # 子操作失败，外层主操作不受影响
```

### 21.2 日志配置与错误处理

```python
# settings.py — 日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # 不禁用已有的 logger
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'level': 'INFO',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs/django.log',     # 日志文件路径
            'maxBytes': 1024 * 1024 * 10,                  # 单个文件最大 10MB
            'backupCount': 5,                              # 保留5个备份
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {                                # Django 自身日志
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,                    # 不向上级传递（避免重复输出）
        },
        'blog': {                                  # 自定义应用日志
            'handlers': ['console', 'file'],
            'level': 'DEBUG',                      # 开发时用 DEBUG，生产改 INFO
            'propagate': False,
        },
    },
}
```

```python
# views.py — 在视图中使用日志
import logging
from django.shortcuts import get_object_or_404
from django.db import DatabaseError
from django.http import Http404
from .models import Article

logger = logging.getLogger('blog')  # 获取名为 'blog' 的 logger

def safe_article_detail(request, slug):
    """文章详情 — 带错误处理和日志"""
    try:
        article = Article.objects.select_related('category').get(
            slug=slug, status='published'
        )
    except Article.DoesNotExist:
        logger.warning(f'文章不存在或未发布: slug={slug}')
        raise Http404('文章不存在')  # 抛出 404 异常，Django 会渲染 404 页面
    except DatabaseError as e:
        # exc_info=True 会输出完整的堆栈信息
        logger.error(f'数据库查询失败: {e}', exc_info=True)
        return render(request, '500.html', status=500)

    # 原子更新阅读量
    try:
        Article.objects.filter(pk=article.pk).update(
            view_count=F('view_count') + 1
        )
    except Exception as e:
        logger.error(f'更新阅读量失败: article_id={article.pk}, error={e}')

    article.refresh_from_db()
    return render(request, 'blog/article_detail.html', {'article': article})
```

### 21.3 自定义管理命令

```python
"""
创建自定义命令的目录结构（必须严格遵循）:
blog/
    management/
        __init__.py
        commands/
            __init__.py
            publish_scheduled.py   ← 命令文件

使用方式:
python manage.py publish_scheduled
python manage.py publish_scheduled --dry-run    # 只预览，不实际修改
python manage.py publish_scheduled --count 10   # 只处理10篇
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from blog.models import Article


class Command(BaseCommand):
    help = '将到期的定时文章自动发布'  # python manage.py help 中显示的帮助文字

    def add_arguments(self, parser):
        """定义命令的额外参数"""
        parser.add_argument(
            '--dry-run',
            action='store_true',  # 布尔开关，传了就是 True
            help='只预览将要发布的文章，不实际修改数据库',
        )
        parser.add_argument(
            '--count',
            type=int,
            default=50,
            help='最多处理的文章数量，默认50篇',
        )

    def handle(self, *args, **options):
        """命令的实际执行逻辑"""
        dry_run = options['dry_run']
        max_count = options['count']
        now = timezone.now()

        # 查询所有到期的定时文章
        articles = Article.objects.filter(
            status='scheduled',
            scheduled_time__lte=now  # 发布时间 <= 当前时间
        )[:max_count]

        count = articles.count()
        if count == 0:
            self.stdout.write(self.style.SUCCESS('没有需要发布的文章'))
            # style.SUCCESS = 绿色文字
            return

        # 输出待处理的文章列表
        self.stdout.write(f'共 {count} 篇文章待发布：')
        for art in articles:
            self.stdout.write(f'  - [{art.pk}] {art.title}')

        if dry_run:
            self.stdout.write(self.style.WARNING('--dry-run 模式，未实际修改数据'))
            # style.WARNING = 黄色文字
            return

        # 批量更新状态为已发布
        updated = articles.update(status='published', published_at=now)
        self.stdout.write(self.style.SUCCESS(f'成功发布 {updated} 篇文章'))
        # style.ERROR = 红色文字（用于错误提示）
```

### 21.4 上下文处理器（为所有模板注入全局变量）

```python
# blog/context_processors.py
from .models import Category

def global_info(request):
    """
    为所有模板注入全局变量，避免在每个视图中重复传递。
    在 settings.py 的 TEMPLATES -> OPTIONS -> context_processors 中注册后生效：
    'blog.context_processors.global_info'
    """
    return {
        'global_categories': Category.objects.all(),  # 所有模板可用
        'site_name': '我的博客',
    }

# settings.py 注册方式:
# TEMPLATES = [{
#     'OPTIONS': {
#         'context_processors': [
#             'django.template.context_processors.debug',
#             'django.template.context_processors.request',
#             'django.contrib.auth.context_processors.auth',
#             'django.contrib.messages.context_processors.messages',
#             'blog.context_processors.global_info',   # ← 注册这里
#         ],
#     },
# }]
# 模板中直接用: {{ site_name }} / {% for cat in global_categories %}
```

---

> **参考来源**：[Django 官方文档](https://docs.djangoproject.com/zh-hans/5.1/) | [Django REST Framework](https://www.django-rest-framework.org/)
> **适用版本**：Django 4.x / 5.x
> **最后更新**：2026-05
