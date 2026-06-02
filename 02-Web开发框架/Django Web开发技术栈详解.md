# Django Web 开发技术栈详解

> Django 后端技术栈全覆盖：DRF、Celery、Channels、缓存、搜索、存储、监控、测试，每个技术附 1-3 个真实场景 + 完整实现代码。

---

## 目录

- [1. DRF — 3 个场景：商品API、订单API、用户注册登录](#1-drf--3-个场景商品api订单api用户注册登录)
- [2. Django Ninja — 场景：高性能API接口](#2-django-ninja--场景高性能api接口)
- [3. Celery — 3 个场景：邮件验证码、Excel导出、图片压缩](#3-celery--3-个场景邮件验证码excel导出图片压缩)
- [4. Channels — 3 个场景：实时通知、在线聊天、数据大屏](#4-channels--3-个场景实时通知在线聊天数据大屏)
- [5. Redis 缓存 — 3 个场景：首页商品缓存、验证码防刷、分布式锁秒杀](#5-redis-缓存--3-个场景首页商品缓存验证码防刷分布式锁秒杀)
- [6. 全文搜索 — 3 个场景：商品搜索、拼音搜索、多条件筛选](#6-全文搜索--3-个场景商品搜索拼音搜索多条件筛选)
- [7. 对象存储 — 3 个场景：头像上传、商品图片、私密文件](#7-对象存储--3-个场景头像上传商品图片私密文件)
- [8. 定时任务 — 3 个场景：日报、清理数据、库存预警](#8-定时任务--3-个场景日报清理数据库存预警)
- [9. 认证与权限 — 3 个场景：JWT登录、RBAC权限、Google OAuth2](#9-认证与权限--3-个场景jwt登录rbac权限google-oauth2)
- [10. 监控 — 3 个场景：异常监控、SQL排查、请求分析](#10-监控--3-个场景异常监控sql排查请求分析)
- [11. 测试 — 3 个场景：模型测试、API测试、异步任务测试](#11-测试--3-个场景模型测试api测试异步任务测试)
- [12. Gunicorn 部署 — 核心配置](#12-gunicorn-部署--核心配置)

---

## 1. DRF — 3 个场景：商品API、订单API、用户注册登录

```bash
pip install djangorestframework django-filter
```

### 场景 1：商品管理 API（列表/详情/搜索/过滤/排序/上下架）

**需求**：后台管理系统需要商品的 CRUD 接口，支持按分类筛选、关键词搜索、价格排序、批量上下架。

```python
# models.py
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

class Product(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

```python
# serializers.py
from rest_framework import serializers
from .models import Product, Category

class ProductListSerializer(serializers.ModelSerializer):
    """列表页：只返回关键字段"""
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'title', 'price', 'stock', 'is_active', 'category_name', 'created_at']

class ProductDetailSerializer(serializers.ModelSerializer):
    """详情页：返回全部字段，含嵌套分类"""
    category = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'

    def get_category(self, obj):
        return {'id': obj.category.id, 'name': obj.category.name, 'slug': obj.category.slug}

class ProductCreateSerializer(serializers.ModelSerializer):
    """创建/更新：只暴露可写字段"""
    class Meta:
        model = Product
        fields = ['title', 'description', 'price', 'stock', 'category']

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("价格必须大于 0")
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("库存不能为负数")
        return value

class BatchToggleSerializer(serializers.Serializer):
    """批量上下架"""
    ids = serializers.ListField(child=serializers.IntegerField())
    is_active = serializers.BooleanField()
```

```python
# views.py
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product
from .serializers import (
    ProductListSerializer,
    ProductDetailSerializer,
    ProductCreateSerializer,
    BatchToggleSerializer,
)

class ProductViewSet(viewsets.ModelViewSet):
    """
    商品管理 API
    GET    /api/products/           — 列表（搜索/过滤/排序）
    POST   /api/products/           — 创建
    GET    /api/products/{id}/      — 详情
    PUT    /api/products/{id}/      — 更新
    DELETE /api/products/{id}/      — 删除
    POST   /api/products/batch_toggle/ — 批量上下架
    GET    /api/products/low_stock/ — 低库存预警
    """
    queryset = Product.objects.select_related('category').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category_id', 'is_active']
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at', 'stock']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return ProductCreateSerializer
        if self.action == 'batch_toggle':
            return BatchToggleSerializer
        return ProductDetailSerializer

    @action(detail=False, methods=['post'], url_path='batch-toggle')
    def batch_toggle(self, request):
        """批量上下架：POST /api/products/batch-toggle/
        {"ids": [1,2,3], "is_active": false}
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        updated = Product.objects.filter(
            id__in=serializer.validated_data['ids']
        ).update(is_active=serializer.validated_data['is_active'])

        return Response({'updated_count': updated})

    @action(detail=False, methods=['get'], url_path='low-stock')
    def low_stock(self, request):
        """低库存预警：GET /api/products/low-stock/?threshold=10"""
        threshold = request.query_params.get('threshold', 10)
        products = self.get_queryset().filter(stock__lte=threshold, is_active=True)
        serializer = ProductListSerializer(products, many=True)
        return Response({
            'count': len(serializer.data),
            'threshold': int(threshold),
            'products': serializer.data,
        })
```

```python
# urls.py
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet

router = DefaultRouter()
router.register('products', ProductViewSet, basename='product')

urlpatterns = [
    path('api/', include(router.urls)),
]
```

---

### 场景 2：订单创建 + 库存扣减（数据库事务 + select_for_update）

**需求**：创建订单时扣减库存，必须保证数据一致性（不能超卖）。

```python
# models.py
from django.db import models, transaction

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', '待支付'),
        ('paid', '已支付'),
        ('shipped', '已发货'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # 下单时快照
```

```python
# serializers.py
class OrderItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, max_value=99)

class CreateOrderSerializer(serializers.Serializer):
    items = OrderItemSerializer(many=True, allow_empty=False)

    def validate_items(self, items):
        """校验所有商品存在且有库存"""
        product_ids = [item['product_id'] for item in items]
        products = Product.objects.filter(id__in=product_ids)

        if len(products) != len(set(product_ids)):
            raise serializers.ValidationError("存在无效的商品ID")

        # 构建库存检查 map
        stock_map = {p.id: p.stock for p in products}
        for item in items:
            if stock_map.get(item['product_id'], 0) < item['quantity']:
                raise serializers.ValidationError(
                    f"商品 {item['product_id']} 库存不足"
                )
        return items
```

```python
# views.py — 核心：事务 + 行锁保证不超卖
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    """创建订单（事务 + 行锁）"""
    serializer = CreateOrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    try:
        with transaction.atomic():
            order = Order.objects.create(user=request.user, total_amount=0)
            total = 0

            for item_data in data['items']:
                # select_for_update：行级锁，防止并发超卖
                product = Product.objects.select_for_update().get(id=item_data['product_id'])

                if product.stock < item_data['quantity']:
                    raise ValueError(f"「{product.title}」库存不足")

                # 扣库存
                product.stock -= item_data['quantity']
                product.save(update_fields=['stock'])

                # 创建订单明细
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item_data['quantity'],
                    price=product.price,
                )
                total += product.price * item_data['quantity']

            order.total_amount = total
            order.save(update_fields=['total_amount'])

        return Response({
            'order_id': order.id,
            'total_amount': str(order.total_amount),
            'item_count': len(data['items']),
            'status': order.status,
        }, status=status.HTTP_201_CREATED)

    except ValueError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
```

---

### 场景 3：用户注册 + 手机验证码

**需求**：用户注册需要手机号 + 验证码，验证码 5 分钟有效，60 秒内不能重复发送。

```python
# serializers.py
from django.contrib.auth import get_user_model
import re, random
from django.core.cache import cache

User = get_user_model()

class SendCodeSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=11)

    def validate_phone(self, value):
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError("手机号格式不正确")

        # 60 秒内不能重复发送
        if cache.get(f'sms:limit:{value}'):
            raise serializers.ValidationError("请60秒后再获取验证码")
        return value

class RegisterSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=11)
    code = serializers.CharField(max_length=6)
    password = serializers.CharField(min_length=6, write_only=True)

    def validate(self, attrs):
        # 验证码校验
        cached_code = cache.get(f'sms:code:{attrs["phone"]}')
        if not cached_code or cached_code != attrs['code']:
            raise serializers.ValidationError({'code': '验证码错误或已过期'})
        return attrs
```

```python
# views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.cache import cache

@api_view(['POST'])
@permission_classes([AllowAny])
def send_sms_code(request):
    """发送手机验证码"""
    serializer = SendCodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    phone = serializer.validated_data['phone']

    code = str(random.randint(100000, 999999))

    # 生产环境调用短信平台API
    # send_sms(phone, f"验证码: {code}, 5分钟内有效")
    print(f"[开发环境] 验证码: {code} → {phone}")

    # 验证码 5 分钟有效
    cache.set(f'sms:code:{phone}', code, 300)
    # 防刷：60 秒限制
    cache.set(f'sms:limit:{phone}', 1, 60)

    return Response({'message': '验证码已发送', 'expire': '5分钟'})

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """用户注册"""
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    # 创建用户
    if User.objects.filter(username=data['phone']).exists():
        return Response({'error': '该手机号已注册'}, status=400)

    user = User.objects.create_user(
        username=data['phone'],
        password=data['password'],
    )

    # 清除验证码
    cache.delete(f'sms:code:{data["phone"]}')
    cache.delete(f'sms:limit:{data["phone"]}')

    # 返回 JWT Token
    refresh = RefreshToken.for_user(user)
    return Response({
        'user_id': user.id,
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    })
```

---

## 2. Django Ninja — 场景：高性能API接口

```bash
pip install django-ninja
```

### 场景：统计看板 API（聚合查询 + 类型安全）

**需求**：后台首页仪表盘需要多个统计接口，要求高性能、自动生成 Swagger 文档。

```python
# api.py
from ninja import NinjaAPI, Schema, Query
from django.db.models import Count, Sum, Q
from datetime import date, timedelta
from typing import List

api = NinjaAPI(title="电商管理后台", version="1.0")

# ===== Schema =====
class DashboardStats(Schema):
    today_orders: int
    today_gmv: float
    total_products: int
    low_stock_products: int
    active_users: int

class SalesTrendItem(Schema):
    date: str
    orders: int
    gmv: float

class TopProductItem(Schema):
    id: int
    title: str
    sales_count: int
    revenue: float

# ===== API =====
@api.get("/dashboard/stats", response=DashboardStats)
def dashboard_stats(request):
    """首页仪表盘核心指标"""
    today = date.today()

    today_orders = Order.objects.filter(created_at__date=today).count()
    today_gmv = Order.objects.filter(
        created_at__date=today, status__in=['paid', 'shipped', 'completed']
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    return {
        'today_orders': today_orders,
        'today_gmv': float(today_gmv),
        'total_products': Product.objects.filter(is_active=True).count(),
        'low_stock_products': Product.objects.filter(stock__lte=10, is_active=True).count(),
        'active_users': User.objects.filter(is_active=True).count(),
    }

@api.get("/dashboard/sales-trend", response=List[SalesTrendItem])
def sales_trend(request, days: int = Query(default=7, ge=1, le=90)):
    """近N天销售趋势"""
    start = date.today() - timedelta(days=days)
    results = []

    for i in range(days):
        d = start + timedelta(days=i)
        day_orders = Order.objects.filter(created_at__date=d).count()
        day_gmv = Order.objects.filter(
            created_at__date=d, status__in=['paid', 'shipped', 'completed']
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        results.append({
            'date': d.isoformat(),
            'orders': day_orders,
            'gmv': float(day_gmv),
        })

    return results

@api.get("/dashboard/top-products", response=List[TopProductItem])
def top_products(request, limit: int = Query(default=10, ge=1, le=50)):
    """热销商品 TOP N"""
    top = OrderItem.objects.values(
        'product_id', 'product__title'
    ).annotate(
        sales_count=Count('id'),
        revenue=Sum('price')
    ).order_by('-sales_count')[:limit]

    return [{
        'id': item['product_id'],
        'title': item['product__title'],
        'sales_count': item['sales_count'],
        'revenue': float(item['revenue']),
    } for item in top]

# urls.py
urlpatterns = [path('api/v2/', api.urls)]
# 访问 /api/v2/docs 查看自动生成的 Swagger 文档
```

---

## 3. Celery — 3 个场景：邮件验证码、Excel导出、图片压缩

```bash
pip install celery redis
```

```python
# celery.py
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
app = Celery('myproject')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# settings.py
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/2'
CELERY_TASK_TIME_LIMIT = 30 * 60
```

### 场景 1：注册成功异步发送欢迎邮件 + 积分赠送

```python
# tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_welcome_email(self, user_id):
    """
    注册成功后发送欢迎邮件。
    bind=True 可以访问 self.retry() 做重试
    max_retries=3：最多重试 3 次
    default_retry_delay=60：每次重试间隔 60 秒
    """
    User = get_user_model()

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        logger.error(f"用户 {user_id} 不存在")
        return

    try:
        send_mail(
            subject='欢迎注册优品商城！',
            message=f'尊敬的 {user.username}：\n\n恭喜您成功注册！\n\n新用户专享 50 积分已到账。',
            from_email='noreply@youpin.com',
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info(f"欢迎邮件已发送: {user.email}")
    except Exception as exc:
        logger.error(f"邮件发送失败 ({user.email}): {exc}")
        self.retry(exc=exc)


@shared_task
def grant_new_user_bonus(user_id):
    """注册送积分（和发邮件并行执行）"""
    from accounts.models import UserProfile

    profile, _ = UserProfile.objects.get_or_create(user_id=user_id)
    profile.points += 50
    profile.save(update_fields=['points'])
    return f"用户 {user_id} 获得 50 积分"
```

```python
# views.py（注册接口中调用）
from .tasks import send_welcome_email, grant_new_user_bonus

@api_view(['POST'])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = User.objects.create_user(...)

    # 异步发送邮件（不阻塞注册请求）
    send_welcome_email.delay(user.id)

    # 异步发积分（和邮件并行）
    grant_new_user_bonus.delay(user.id)

    return Response({'message': '注册成功'})
```

### 场景 2：导出订单报表（生成 Excel + 上传到 OSS + WebSocket 通知）

```python
# tasks.py
import io
from openpyxl import Workbook
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

@shared_task(bind=True, max_retries=2)
def export_orders_to_excel(self, user_id, start_date, end_date, filters=None):
    """
    导出订单数据为 Excel 文件，上传 OSS，通过 WebSocket 通知用户下载。

    适合大数据量导出（比如 10万+ 订单），避免请求超时。
    """
    from orders.models import Order

    # 1. 查询数据（分批处理大数据量）
    queryset = Order.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date,
    ).select_related('user')

    if filters:
        if 'status' in filters:
            queryset = queryset.filter(status=filters['status'])

    # 2. 生成 Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "订单报表"
    ws.append(['订单号', '用户', '金额', '状态', '创建时间'])

    for order in queryset.iterator(chunk_size=1000):  # 分批读取
        ws.append([
            order.id,
            order.user.username,
            float(order.total_amount),
            order.get_status_display(),
            order.created_at.strftime('%Y-%m-%d %H:%M'),
        ])

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    # 3. 上传到对象存储（MinIO/S3/OSS）
    filename = f'reports/orders_{start_date}_{end_date}_用户{user_id}.xlsx'
    path = default_storage.save(filename, ContentFile(buffer.read()))

    # 4. WebSocket 通知用户下载
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'user_{user_id}',
        {
            'type': 'send_notification',
            'message': f'订单报表已生成',
            'data': {
                'type': 'report_ready',
                'file_url': default_storage.url(path),
                'filename': filename,
            },
        },
    )

    return {'file_url': default_storage.url(path)}

# 调用
# export_orders_to_excel.delay(user.id, '2024-01-01', '2024-06-30', {'status': 'paid'})
```

### 场景 3：用户上传头像后异步裁剪 + 生成缩略图

```python
# tasks.py
from PIL import Image
import io, os
from django.core.files.storage import default_storage

@shared_task(bind=True, max_retries=1)
def process_avatar(self, user_id, image_path):
    """
    处理用户头像：裁剪为正方形 → 生成 200x200 缩略图 → 生成 48x48 小图
    原始图在 CPU 密集操作期间不阻塞 Web 请求
    """
    try:
        # 1. 从对象存储读取原图
        file = default_storage.open(image_path, 'rb')
        img = Image.open(file)

        # 2. 裁剪为正方形（取中心区域）
        width, height = img.size
        size = min(width, height)
        left = (width - size) // 2
        top = (height - size) // 2
        img = img.crop((left, top, left + size, top + size))

        # 3. 生成 200x200 缩略图
        img_200 = img.resize((200, 200), Image.LANCZOS)
        buf_200 = io.BytesIO()
        img_200.save(buf_200, 'JPEG', quality=85)
        buf_200.seek(0)

        base, ext = os.path.splitext(image_path)
        path_200 = f'{base}_200x200.jpg'
        default_storage.save(path_200, ContentFile(buf_200.read()))

        # 4. 生成 48x48 小图（用于消息列表头像）
        img_48 = img.resize((48, 48), Image.LANCZOS)
        buf_48 = io.BytesIO()
        img_48.save(buf_48, 'JPEG', quality=80)
        buf_48.seek(0)

        path_48 = f'{base}_48x48.jpg'
        default_storage.save(path_48, ContentFile(buf_48.read()))

        # 5. 更新数据库
        User.objects.filter(id=user_id).update(
            avatar=path_200,
            avatar_thumb=path_48,
        )

        return {'avatar': path_200, 'thumb': path_48}

    except Exception as exc:
        logger.error(f"头像处理失败 user={user_id}: {exc}")
        self.retry(exc=exc)

# 调用（view 中）
@api_view(['POST'])
def upload_avatar(request):
    file = request.FILES['avatar']
    path = default_storage.save(f'avatars/{request.user.id}/raw_{file.name}', file)

    # 响应立即返回，图片异步处理
    process_avatar.delay(request.user.id, path)

    return Response({'message': '头像上传成功，正在处理中...'})
```

---

## 4. Channels — 3 个场景：实时通知、在线聊天、数据大屏

```bash
pip install channels channels-redis daphne
```

```python
# settings.py
INSTALLED_APPS = ['daphne', 'channels', ...]
ASGI_APPLICATION = 'myproject.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {'hosts': [('127.0.0.1', 6379)]},
    },
}
```

```python
# asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from myapp.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AllowedHostsOriginValidator(
        URLRouter(websocket_urlpatterns)
    ),
})
```

### 场景 1：实时通知推送（订单状态变更 → 用户端弹窗）

```python
# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    """用户通知消费者：登录后自动连接，接收服务端推送"""

    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_anonymous:
            await self.close()
            return

        # 加入个人通知组
        self.group_name = f'user_{self.user.id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # 上线通知
        await self.send(text_data=json.dumps({
            'type': 'connected',
            'message': f'通知服务已连接 (用户: {self.user.username})',
        }))

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # 各类通知处理器
    async def order_update(self, event):
        """订单状态变更通知"""
        await self.send(text_data=json.dumps({
            'type': 'order_update',
            'data': event['data'],
        }))

    async def promotion(self, event):
        """促销活动推送"""
        await self.send(text_data=json.dumps({
            'type': 'promotion',
            'data': event['data'],
        }))

    async def send_notification(self, event):
        """通用通知"""
        await self.send(text_data=json.dumps({
            'type': event.get('noti_type', 'info'),
            'message': event['message'],
            'data': event.get('data'),
        }))
```

```python
# routing.py
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/notifications/', consumers.NotificationConsumer.as_asgi()),
]
```

```python
# notify.py — 服务端推送工具函数
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def notify_user(user_id, noti_type, message, data=None):
    """给指定用户发送 WebSocket 通知"""
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'user_{user_id}',
        {
            'type': 'send_notification',
            'noti_type': noti_type,
            'message': message,
            'data': data,
        },
    )

def notify_order_status_changed(order):
    """订单状态变更时通知买家"""
    notify_user(
        order.user_id,
        'order_update',
        f'您的订单 #{order.id} 已{order.get_status_display()}',
        {
            'order_id': order.id,
            'status': order.status,
            'status_display': order.get_status_display(),
        },
    )

# 在订单状态变更的 View/Service 中调用
# notify_order_status_changed(order)
```

### 场景 2：在线客服聊天

```python
# consumers.py
class ChatConsumer(AsyncWebsocketConsumer):
    """客服聊天：支持多房间（order_{order_id}）"""

    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_anonymous:
            await self.close()
            return

        # 从 URL 获取订单号作为聊天房间
        self.order_id = self.scope['url_route']['kwargs']['order_id']
        self.room_name = f'chat_order_{self.order_id}'

        # 校验用户权限（只能进自己的订单聊天）
        order = await self.get_order()
        if not order or (order.user_id != self.user.id and not self.user.is_staff):
            await self.close()
            return

        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def get_order(self):
        from django.db import close_old_connections
        close_old_connections()
        from orders.models import Order
        try:
            return await Order.objects.aget(id=self.order_id)
        except Order.DoesNotExist:
            return None

    async def receive(self, text_data):
        """接收消息 → 存数据库 → 广播给房间所有人"""
        data = json.loads(text_data)

        # 保存消息到数据库
        from orders.models import ChatMessage
        msg = await ChatMessage.objects.acreate(
            order_id=self.order_id,
            sender=self.user,
            content=data['message'],
            msg_type=data.get('type', 'text'),
        )

        # 广播
        await self.channel_layer.group_send(self.room_name, {
            'type': 'chat_message',
            'message': {
                'id': msg.id,
                'sender': self.user.username,
                'sender_id': self.user.id,
                'is_staff': self.user.is_staff,
                'content': data['message'],
                'type': data.get('type', 'text'),
                'created_at': msg.created_at.isoformat(),
            },
        })

    async def chat_message(self, event):
        """广播消息给客户端"""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
        }))

# routing.py
# path('ws/chat/<int:order_id>/', consumers.ChatConsumer.as_asgi()),
```

### 场景 3：实时数据大屏

```python
# consumers.py
class DashboardConsumer(AsyncWebsocketConsumer):
    """
    后台数据大屏：每秒推送最新指标。
    只有管理员可以连接。
    """

    async def connect(self):
        if not self.scope['user'].is_staff:
            await self.close()
            return

        self.group_name = 'dashboard'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def dashboard_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'dashboard_update',
            'data': event['data'],
        }))
```

```python
# Celery Beat 定时推送（每 10 秒）
from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@shared_task
def push_dashboard_data():
    """每 10 秒推送一次实时数据到数据大屏"""
    from django.db.models import Sum, Count
    from django.utils import timezone

    today = timezone.now().date()

    data = {
        'today_orders': Order.objects.filter(created_at__date=today).count(),
        'today_gmv': float(
            Order.objects.filter(
                created_at__date=today,
                status__in=['paid', 'shipped', 'completed']
            ).aggregate(total=Sum('total_amount'))['total'] or 0
        ),
        'pending_orders': Order.objects.filter(status='pending').count(),
        'active_users': User.objects.filter(last_login__date=today).count(),
        'low_stock_count': Product.objects.filter(stock__lte=10, is_active=True).count(),
    }

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'dashboard',
        {'type': 'dashboard_update', 'data': data},
    )
```

---

## 5. Redis 缓存 — 3 个场景：首页商品缓存、验证码防刷、分布式锁秒杀

```bash
pip install django-redis
```

```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {'max_connections': 50},
        },
        'KEY_PREFIX': 'myapp',
    }
}
```

### 场景 1：首页商品缓存（Cache Aside 模式 + 随机过期）

```python
"""需求：首页商品列表访问量极大，需要缓存减轻 DB 压力，同时避免缓存雪崩。"""
import random
from django.core.cache import cache
from products.models import Product

class HomePageService:
    """首页数据服务"""

    CACHE_KEY = 'home:products'
    BASE_TIMEOUT = 300  # 基础 5 分钟

    @classmethod
    def get_home_products(cls):
        """读缓存 → 未命中查 DB → 写缓存（加随机过期防雪崩）"""
        data = cache.get(cls.CACHE_KEY)
        if data is not None:
            return data

        # 查 DB（select_related 减查询次数）
        hot_products = list(Product.objects.filter(
            is_active=True, stock__gt=0
        ).select_related('category').order_by('-created_at')[:50])

        # 写缓存（300~360秒随机过期，避免同时过期导致雪崩）
        timeout = cls.BASE_TIMEOUT + random.randint(0, 60)
        cache.set(cls.CACHE_KEY, hot_products, timeout)

        return hot_products

    @classmethod
    def invalidate_cache(cls):
        """商品变更时删除缓存（下次读时自动重建）"""
        cache.delete(cls.CACHE_KEY)

    @classmethod
    def warmup_cache(cls):
        """定时预热缓存（避免 DB 冷启动）"""
        cls.invalidate_cache()
        cls.get_home_products()

# 商品变更信号自动失效缓存
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver(post_save, sender=Product)
@receiver(post_delete, sender=Product)
def product_changed(sender, instance, **kwargs):
    HomePageService.invalidate_cache()
```

### 场景 2：验证码防刷 + 登录失败限制

```python
"""需求：防止恶意发送验证码和暴力破解登录。"""

from django.core.cache import cache

class RateLimiter:
    """基于 Redis 的速率限制器"""

    @staticmethod
    def check_sms_limit(phone):
        """
        短信验证码防刷：
        - 同手机号 60s 内只能发 1 次
        - 同手机号 1 小时内最多 5 次
        - 同 IP 1 小时内最多 10 次
        """
        # 60s 限制
        if cache.get(f'sms:1min:{phone}'):
            return False, "请 60 秒后再获取验证码"

        # 1 小时限制
        hour_key = f'sms:hour:{phone}'
        count = cache.get(hour_key) or 0
        if count >= 5:
            return False, "今日验证码已达上限，请 1 小时后重试"

        return True, None

    @staticmethod
    def record_sms_sent(phone, ip):
        """记录发送"""
        cache.set(f'sms:1min:{phone}', 1, 60)
        count = cache.get(f'sms:hour:{phone}') or 0
        cache.set(f'sms:hour:{phone}', count + 1, 3600)

        # IP 维度限制
        ip_count = cache.get(f'sms:ip:{ip}') or 0
        cache.set(f'sms:ip:{ip}', ip_count + 1, 3600)

    @staticmethod
    def check_login_limit(ip, username):
        """
        登录失败限制：
        - 同 IP 连续失败 5 次 → 锁定 15 分钟
        - 同账号连续失败 5 次 → 锁定 15 分钟
        """
        ip_fails = cache.get(f'login:ip:{ip}') or 0
        user_fails = cache.get(f'login:user:{username}') or 0

        if ip_fails >= 5:
            return False, "登录太频繁，请 15 分钟后重试"
        if user_fails >= 5:
            return False, "该账号已锁定，请 15 分钟后重试"

        return True, None

    @staticmethod
    def record_login_fail(ip, username):
        cache.set(f'login:ip:{ip}', (cache.get(f'login:ip:{ip}') or 0) + 1, 900)
        cache.set(f'login:user:{username}', (cache.get(f'login:user:{username}') or 0) + 1, 900)

    @staticmethod
    def clear_login_limit(username):
        cache.delete(f'login:user:{username}')

# 在登录 View 中使用
@api_view(['POST'])
def login(request):
    ip = request.META.get('REMOTE_ADDR')
    username = request.data.get('username')

    ok, msg = RateLimiter.check_login_limit(ip, username)
    if not ok:
        return Response({'error': msg}, status=429)

    user = authenticate(username=username, password=request.data.get('password'))
    if not user:
        RateLimiter.record_login_fail(ip, username)
        return Response({'error': '用户名或密码错误'}, status=401)

    RateLimiter.clear_login_limit(username)
    # 返回 Token...
```

### 场景 3：分布式锁 — 四种方案完整实现

**需求**：在多 Gunicorn Worker / 多服务器环境下，保证同一商品同一时间只能被一个用户成功下单（防超卖）。

#### 方案对比一览

| 方案 | 原理 | 可靠性 | 性能 | 适用场景 |
|------|------|--------|------|---------|
| **Redis 分布式锁** | SET NX EX + Lua 释放 | 中 | 高 | 通用，**首选** |
| **select_for_update 行锁** | 数据库行级 X 锁 | 高 | 低 | 小并发、已有事务保护 |
| **乐观锁（版本号）** | WHERE version=旧值 | 中 | 高 | 读多写少、冲突少 |
| **Celery 任务去重锁** | Redis 锁 + Celery 幂等 | 中 | 高 | 异步任务防重 |

---

#### 方案 1：Redis 分布式锁（推荐）

完整实现一个生产级的 Redis 锁，包含 **原子获取、Lua 释放、自动续期、重试机制**：

```python
"""需求：秒杀场景，同一商品同一时间只能有一个用户下单成功。"""
import uuid
import time
import threading
from django.core.cache import cache

class RedisDistributedLock:
    """
    基于 Redis SETNX 的生产级分布式锁。

    核心要点：
    1. SET key token NX EX — 原子获取 + 防死锁
    2. Lua 原子释放 — 只删除自己的锁（防误删）
    3. Watchdog 续期 — 业务执行太久自动续锁
    4. 重试机制 — 获取失败不立即放弃
    """

    def __init__(self, key, expire=30, retry_times=3, retry_delay=0.1):
        self.key = f"lock:{key}"
        self.expire = expire
        self.token = uuid.uuid4().hex
        self.retry_times = retry_times
        self.retry_delay = retry_delay
        self._renew_thread = None
        self._renew_stop = threading.Event()

        # 获取底层 Redis 连接（绕过 Django Cache 抽象）
        from django_redis import get_redis_connection
        self.redis = get_redis_connection("default")

        # Lua 脚本：原子释放（只释放自己的锁）
        self._release_lua = self.redis.register_script("""
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
        """)

        # Lua 脚本：续期
        self._renew_lua = self.redis.register_script("""
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("expire", KEYS[1], ARGV[2])
            else
                return 0
            end
        """)

    # ===== 获取锁 =====
    def acquire(self) -> bool:
        """尝试获取锁，支持重试"""
        for attempt in range(self.retry_times):
            # SET key token NX EX — 原子操作
            if self.redis.set(self.key, self.token, nx=True, ex=self.expire):
                self._start_auto_renew()
                return True
            time.sleep(self.retry_delay)
        return False

    # ===== 释放锁 =====
    def release(self):
        """原子释放锁"""
        self._stop_auto_renew()
        self._release_lua(keys=[self.key], args=[self.token])

    # ===== 自动续期（Watchdog）=====
    def _start_auto_renew(self):
        """启动后台续期线程"""
        interval = max(1, self.expire // 3)

        def _renew():
            while not self._renew_stop.wait(interval):
                result = self._renew_lua(keys=[self.key], args=[self.token, self.expire])
                if not result:
                    break  # 锁已不属于自己，停止续期

        self._renew_thread = threading.Thread(target=_renew, daemon=True)
        self._renew_thread.start()

    def _stop_auto_renew(self):
        self._renew_stop.set()
        if self._renew_thread:
            self._renew_thread.join(timeout=1)

    # ===== 上下文管理器 =====
    def __enter__(self):
        if not self.acquire():
            raise RuntimeError(f"获取锁失败: {self.key}")
        return self

    def __exit__(self, *args):
        self.release()


class SeckillService:
    """秒杀服务 — 使用 Redis 分布式锁"""

    @staticmethod
    def place_seckill_order(user_id: int, product_id: int):
        """秒杀下单（Redis 分布式锁保护）"""
        lock = RedisDistributedLock(f"seckill:product:{product_id}", expire=10)

        # 1. 获取分布式锁
        if not lock.acquire():
            return {'success': False, 'error': '抢购人数太多，请稍后再试'}

        try:
            # 2. 检查 + 扣减（锁内操作）
            with transaction.atomic():
                # select_for_update 双保险：锁内再用行锁
                product = Product.objects.select_for_update().get(id=product_id)

                if product.stock < 1:
                    return {'success': False, 'error': '已售罄'}

                # 检查是否已抢过（同一用户限购 1 件）
                if OrderItem.objects.filter(
                    order__user_id=user_id,
                    product_id=product_id,
                ).exists():
                    return {'success': False, 'error': '每人限购 1 件'}

                # 扣库存
                product.stock -= 1
                product.save(update_fields=['stock'])

                # 创建订单
                order = Order.objects.create(
                    user_id=user_id,
                    total_amount=product.seckill_price,
                )
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=1,
                    price=product.seckill_price,
                )

            return {
                'success': True,
                'order_id': order.id,
                'price': float(product.seckill_price),
            }

        finally:
            lock.release()  # 无论成功失败，释放锁

    @staticmethod
    def place_seckill_order_with_retry(user_id: int, product_id: int, max_retries: int = 3):
        """带重试的秒杀（应对瞬时高并发）"""
        for attempt in range(max_retries):
            result = SeckillService.place_seckill_order(user_id, product_id)
            if result['success']:
                return result
            if result['error'] == '已售罄':
                return result  # 库存没了，不必重试
            time.sleep(0.05)  # 换锁失败，等 50ms 重试
        return {'success': False, 'error': '系统繁忙，请稍后再试'}
```

---

#### 方案 2：select_for_update 行级锁（数据库悲观锁）

适合**并发不高**或需要配合数据库事务的场景：

```python
from django.db import transaction
from django.db.models import F

class SeckillWithDBLock:
    """秒杀 — select_for_update 行级锁"""

    @staticmethod
    def place_order(user_id: int, product_id: int):
        """
        select_for_update 原理：
        - SELECT ... FOR UPDATE = 对查询到的行加 X 锁
        - 其他事务的 SELECT ... FOR UPDATE 会阻塞
        - 事务提交后释放锁
        """
        try:
            with transaction.atomic():
                # ⚠️ 关键：select_for_update 在 transaction.atomic() 内才生效
                product = Product.objects.select_for_update().get(id=product_id)

                if product.stock < 1:
                    return {'success': False, 'error': '已售罄'}

                # 直接 update（不需要再 save，利用 F 表达式原子扣减）
                Product.objects.filter(
                    id=product_id, stock__gte=1
                ).update(stock=F('stock') - 1)

                order = Order.objects.create(user_id=user_id, total_amount=100)
                OrderItem.objects.create(order=order, product_id=product_id, quantity=1, price=100)

            return {'success': True, 'order_id': order.id}

        except Product.DoesNotExist:
            return {'success': False, 'error': '商品不存在'}

    # 对比：不加锁的后果
    @staticmethod
    def place_order_unsafe(user_id: int, product_id: int):
        """❌ 不安全：先读后写，并发时会超卖"""
        product = Product.objects.get(id=product_id)

        if product.stock < 1:
            return {'success': False, 'error': '已售罄'}

        # ⚠️ 竞态窗口：多个线程可能同时读到 stock >= 1
        product.stock -= 1
        product.save()

        # 结果：可能超卖！
        return {'success': True}
```

**select_for_update 注意事项：**

```python
# ✅ 正确：在 transaction.atomic() 上下文中使用
with transaction.atomic():
    obj = Product.objects.select_for_update().get(id=1)

# ❌ 错误：在事务外使用（FOR UPDATE 立刻释放，等同于没锁）
obj = Product.objects.select_for_update().get(id=1)

# ✅ 正确：只锁需要的行（WHERE 条件走索引）
Product.objects.select_for_update().filter(id__in=[1, 2, 3])

# ❌ 错误：没有索引的 WHERE（会导致全表锁！）
Product.objects.select_for_update().filter(name='iPhone')
# 如果 name 列没有索引 → 全表扫描 → 锁全表
```

---

#### 方案 3：乐观锁（版本号 / 时间戳）

**不阻塞，冲突时重试**，适合读多写少的场景：

```python
from django.db.models import F

class SeckillWithOptimisticLock:
    """秒杀 — 乐观锁（版本号机制）"""

    @staticmethod
    def place_order(user_id: int, product_id: int, max_retries: int = 5):
        """
        乐观锁流程：
        1. 读取当前版本号
        2. UPDATE WHERE version=旧值（原子操作）
        3. 如果 affected_rows = 0 → 被抢先了 → 重试
        """
        for attempt in range(max_retries):
            # 读取当前数据和版本号
            product = Product.objects.get(id=product_id)
            if product.stock < 1:
                return {'success': False, 'error': '已售罄'}

            # 原子更新：只有 version 匹配才执行
            affected = Product.objects.filter(
                id=product_id,
                version=product.version,  # ⚠️ 关键：带上旧版本号
                stock__gte=1,
            ).update(
                stock=F('stock') - 1,
                version=F('version') + 1,  # 版本号 +1
            )

            if affected > 0:
                # 成功
                order = Order.objects.create(user_id=user_id, total_amount=100)
                return {'success': True, 'order_id': order.id}

            # affected = 0 → 被其他请求抢先了，重试
            # 可以加短暂随机等待，减少冲突
            time.sleep(0.01 * random.randint(1, 5))

        return {'success': False, 'error': '系统繁忙，请稍后重试'}
```

**Model 定义：**

```python
class Product(models.Model):
    title = models.CharField(max_length=200)
    stock = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    version = models.IntegerField(default=0)  # 乐观锁版本号
```

---

#### 方案 4：Celery 任务去重锁（防止任务重复执行）

```python
from celery import shared_task
from django_redis import get_redis_connection

@shared_task(bind=True)
def process_refund(self, order_id):
    """退款处理 — 防止同一订单被多个 worker 重复处理"""
    redis = get_redis_connection("default")
    lock_key = f"task:refund:{order_id}"
    lock_token = uuid.uuid4().hex

    # 尝试获取分布式锁
    if not redis.set(lock_key, lock_token, nx=True, ex=300):
        return f"退款任务已在执行中，跳过: {order_id}"

    try:
        # 执行退款逻辑
        with transaction.atomic():
            order = Order.objects.select_for_update().get(id=order_id)
            if order.status != 'paid':
                return f"订单状态不是已支付，无法退款"

            # 退款...
            order.status = 'refunded'
            order.save()

            # 恢复库存
            for item in order.items.all():
                Product.objects.filter(id=item.product_id).update(
                    stock=F('stock') + item.quantity
                )

        return f"退款成功: {order_id}"

    except Exception as e:
        logger.error(f"退款失败 {order_id}: {e}")
        raise

    finally:
        # Lua 原子释放锁
        script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        redis.eval(script, 1, lock_key, lock_token)
```

---

#### 四种方案选型总结

```
                        并发抢单/任务去重
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
       有 Redis？      只用数据库？     需事务保障？
            │               │               │
            ▼               ▼               ▼
    ┌──────────────┐ ┌──────────┐ ┌──────────────┐
    │Redis分布式锁  │ │ 乐观锁    │ │select_for   │
    │(首选，高性能) │ │(版本号)   │ │update 行锁   │
    └──────────────┘ └──────────┘ └──────────────┘
            │               │               │
    适用：高并发抢购  适用：个人资料修改 适用：余额扣减
          秒杀活动       库存非热点数据   订单状态变更

选型口诀：
- 高并发 → Redis 分布式锁
- 有事务 → select_for_update 行锁
- 低冲突 → 乐观锁（版本号）
- 异步任务 → Redis 锁 + 任务幂等
```

---

## 6. 全文搜索 — 3 个场景：商品搜索、拼音搜索、多条件筛选

```bash
docker run -d --name meilisearch -p 7700:7700 \
  -v meili_data:/meili_data \
  getmeili/meilisearch:v1.10 meilisearch --master-key=masterKey

pip install meilisearch
```

### 场景 1：商品搜索引擎（分词 + 容错 + 高亮）

```python
# search.py
import meilisearch

client = meilisearch.Client('http://localhost:7700', 'masterKey')

def build_product_index():
    """初始化商品搜索索引"""
    index = client.index('products')

    index.update_settings({
        'searchableAttributes': ['title', 'description', 'brand', 'category_name'],
        'filterableAttributes': [
            'category_id', 'price', 'brand', 'is_active', 'tags'
        ],
        'sortableAttributes': ['price', 'created_at', 'sales_count'],
        'typoTolerance': {'enabled': True, 'minWordSizeForTypos': {'oneTypo': 4, 'twoTypos': 8}},
        'pagination': {'maxTotalHits': 10000},
        'faceting': {'maxValuesPerFacet': 100},
    })

def sync_product_to_index(product):
    """同步单个商品到索引"""
    doc = {
        'id': str(product.id),  # Meilisearch 要求字符串 ID
        'title': product.title,
        'description': product.description,
        'price': float(product.price),
        'stock': product.stock,
        'brand': product.brand or '',
        'category_id': product.category_id,
        'category_name': product.category.name,
        'is_active': product.is_active,
        'tags': product.tags_list(),
        'sales_count': product.sales_count,
        'created_at': product.created_at.timestamp(),
    }
    client.index('products').add_documents([doc])

def search_products(query, filters=None, sort=None, page=1, page_size=20):
    """
    搜索商品（支持过滤 + 排序 + 分页）
    """
    search_params = {
        'limit': page_size,
        'offset': (page - 1) * page_size,
        'attributesToHighlight': ['title', 'description'],
        'highlightPreTag': '<em>',
        'highlightPostTag': '</em>',
    }

    # 过滤
    if filters:
        filter_list = []
        if 'category_id' in filters:
            filter_list.append(f'category_id = {filters["category_id"]}')
        if 'min_price' in filters:
            filter_list.append(f'price >= {filters["min_price"]}')
        if 'max_price' in filters:
            filter_list.append(f'price <= {filters["max_price"]}')
        if 'brand' in filters:
            filter_list.append(f'brand = "{filters["brand"]}"')
        if filter_list:
            search_params['filter'] = ' AND '.join(filter_list)

    # 排序
    if sort:
        search_params['sort'] = [sort]

    result = client.index('products').search(query, search_params)

    return {
        'total': result['estimatedTotalHits'],
        'page': page,
        'page_size': page_size,
        'items': [{
            'id': hit['id'],
            'title': hit.get('_formatted', {}).get('title', hit['title']),
            'description': hit.get('_formatted', {}).get('description', hit['description'])[:200],
            'price': hit['price'],
            'brand': hit['brand'],
        } for hit in result['hits']],
    }
```

### 场景 2：拼音搜索（支持用户用拼音搜中文商品）

```python
from pypinyin import lazy_pinyin

def add_pinyin_field(product):
    """为商品标题生成拼音字段"""
    title_pinyin = ''.join(lazy_pinyin(product.title))
    title_pinyin_first = ''.join([p[0] for p in lazy_pinyin(product.title)])
    return f'{product.title} {title_pinyin} {title_pinyin_first}'

def sync_product_with_pinyin(product):
    """同步含拼音的索引"""
    doc = {
        'id': str(product.id),
        'title': product.title,
        'description': product.description,
        'title_pinyin': add_pinyin_field(product),  # 搜索时 match 这个字段
        'price': float(product.price),
        'category_name': product.category.name,
    }
    client.index('products').add_documents([doc])

# 搜索时：search_products("shouji") 能搜到"手机"
```

### 场景 3：搜索结果 + 分类/品牌/价格聚合（类似电商筛选侧栏）

```python
# search.py
def search_with_facets(query, filters=None):
    """搜索结果 + 筛选条件聚合（分类分布、品牌分布、价格区间）"""

    search_params = {
        'limit': 20,
        'filter': filters,
        'facets': ['category_name', 'brand', 'price'],
    }

    result = client.index('products').search(query, search_params)

    return {
        'total': result['estimatedTotalHits'],
        'items': result['hits'],
        # 筛选面（供前端渲染筛选侧栏）
        'facets': {
            'categories': result.get('facetDistribution', {}).get('category_name', {}),
            'brands': result.get('facetDistribution', {}).get('brand', {}),
        },
        # 价格分布
        'price_ranges': [
            {'label': '0-50元', 'min': 0, 'max': 50},
            {'label': '50-100元', 'min': 50, 'max': 100},
            {'label': '100-200元', 'min': 100, 'max': 200},
            {'label': '200元以上', 'min': 200, 'max': None},
        ],
    }
```

```python
# Django 信号自动同步索引
from django.db.models.signals import post_save, post_delete

@receiver(post_save, sender=Product)
def sync_on_save(sender, instance, **kwargs):
    if instance.is_active:
        sync_product_with_pinyin(instance)
    else:
        client.index('products').delete_document(str(instance.id))

@receiver(post_delete, sender=Product)
def delete_from_index(sender, instance, **kwargs):
    client.index('products').delete_document(str(instance.id))
```

---

## 7. 对象存储 — 3 个场景：头像上传、商品图片、私密文件

```bash
pip install django-storages boto3

# 本地 MinIO
docker run -d --name minio -p 9000:9000 -p 9001:9001 \
  -e MINIO_ROOT_USER=admin -e MINIO_ROOT_PASSWORD=password123 \
  minio/minio server /data --console-address ":9001"
```

```python
# settings.py
INSTALLED_APPS += ['storages']

STORAGES = {
    'default': {
        'BACKEND': 'storages.backends.s3.S3Storage',
        'OPTIONS': {'bucket_name': 'myapp'},
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}

AWS_S3_ENDPOINT_URL = os.getenv('S3_ENDPOINT', 'http://127.0.0.1:9000')
AWS_ACCESS_KEY_ID = os.getenv('S3_ACCESS_KEY', 'admin')
AWS_SECRET_ACCESS_KEY = os.getenv('S3_SECRET_KEY', 'password123')
AWS_S3_REGION_NAME = 'us-east-1'
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_DEFAULT_ACL = 'public-read'
AWS_QUERYSTRING_EXPIRE = 3600  # 预签名 URL 过期时间
```

### 场景 1：用户头像上传 + 自动生成缩略图

```python
# models.py
class UserProfile(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/%Y/%m/', blank=True)
    avatar_thumb = models.ImageField(upload_to='avatars/%Y/%m/thumbs/', blank=True)

# views.py
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_avatar(request):
    """上传头像 → 存 MinIO → Celery 异步处理缩略图"""
    file = request.FILES.get('avatar')
    if not file:
        return Response({'error': '请选择图片'}, status=400)

    if file.size > 5 * 1024 * 1024:
        return Response({'error': '图片不能超过 5MB'}, status=400)

    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    # 直接上传到 MinIO
    profile.avatar = file
    profile.save()

    # 异步压缩 + 生成缩略图
    process_avatar.delay(request.user.id)

    return Response({
        'avatar_url': request.build_absolute_uri(profile.avatar.url),
        'message': '上传成功，正在处理中',
    })
```

### 场景 2：商品图片批量上传 + 排序

```python
# models.py
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/%Y/%m/')
    sort_order = models.IntegerField(default=0)
    is_main = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

# views.py
@api_view(['POST'])
def upload_product_images(request, product_id):
    """批量上传商品图片（最多 9 张）"""
    product = get_object_or_404(Product, id=product_id)
    files = request.FILES.getlist('images')

    if len(files) > 9:
        return Response({'error': '最多 9 张图片'}, status=400)

    images = []
    for i, file in enumerate(files):
        obj = ProductImage.objects.create(
            product=product,
            image=file,
            sort_order=i,
            is_main=(i == 0 and not product.images.exists()),  # 第一张设为主图
        )
        images.append({
            'id': obj.id,
            'url': request.build_absolute_uri(obj.image.url),
            'sort_order': obj.sort_order,
            'is_main': obj.is_main,
        })

    return Response({'images': images, 'count': len(images)}, status=201)

@api_view(['POST'])
def reorder_product_images(request, product_id):
    """调整图片排序"""
    product = get_object_or_404(Product, id=product_id)
    image_ids = request.data.get('image_ids', [])  # [3, 1, 2]

    for order, img_id in enumerate(image_ids):
        ProductImage.objects.filter(id=img_id, product=product).update(sort_order=order)

    return Response({'message': '排序已更新'})
```

### 场景 3：私有文件 + 预签名 URL（订单发票/合同下载）

```python
"""需求：发票等私密文件不能公开访问，需要生成有时效的临时下载链接。"""
import boto3
from django.conf import settings

class PrivateFileService:
    """私有文件服务"""

    @staticmethod
    def generate_download_url(file_key, expire_seconds=600):
        """生成预签名 URL（10 分钟有效）"""
        s3 = boto3.client(
            's3',
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )

        url = s3.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                'Key': file_key,
                'ResponseContentDisposition': f'attachment; filename="{file_key.split("/")[-1]}"',
            },
            ExpiresIn=expire_seconds,
        )
        return url

    @staticmethod
    def upload_private_file(file_obj, path):
        """上传私有文件（不设公开权限）"""
        from django.core.files.storage import default_storage
        saved_path = default_storage.save(
            path, file_obj,
            # 覆盖 ACL 为私有
        )
        return saved_path


# views.py — 发票下载
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_invoice(request, order_id):
    """下载订单发票（私有文件，生成临时链接）"""
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if not order.invoice_file:
        return Response({'error': '发票尚未生成'}, status=404)

    url = PrivateFileService.generate_download_url(order.invoice_file, expire_seconds=300)

    return Response({'download_url': url, 'expire_in': 300})
```

---

## 8. 定时任务 — 3 个场景：日报、清理数据、库存预警

```python
# settings.py
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'daily-report': {
        'task': 'reports.tasks.send_daily_report',
        'schedule': crontab(hour=9, minute=0),
    },
    'clean-expired-data': {
        'task': 'maintenance.tasks.clean_expired_data',
        'schedule': crontab(hour=3, minute=0),  # 凌晨低峰
    },
    'check-low-stock': {
        'task': 'products.tasks.check_low_stock_and_alert',
        'schedule': crontab(minute='*/30'),  # 每 30 分钟
    },
}
```

### 场景 1：每日销售日报（邮件 + 站内信）

```python
# reports/tasks.py
from celery import shared_task
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta

@shared_task
def send_daily_report():
    """每天 9:00 发送昨日销售日报给所有管理员"""
    yesterday = timezone.now().date() - timedelta(days=1)

    # 统计数据
    from orders.models import Order
    from django.db.models import Sum, Count, Q

    paid_orders = Order.objects.filter(
        created_at__date=yesterday,
        status__in=['paid', 'shipped', 'completed'],
    )

    stats = {
        'date': yesterday,
        'total_orders': paid_orders.count(),
        'total_gmv': float(paid_orders.aggregate(t=Sum('total_amount'))['t'] or 0),
        'new_users': User.objects.filter(date_joined__date=yesterday).count(),
        'top_products': list(
            OrderItem.objects.filter(order__in=paid_orders)
            .values('product__title')
            .annotate(cnt=Count('id'))
            .order_by('-cnt')[:5]
        ),
    }

    # 渲染 HTML 邮件
    html_content = render_to_string('reports/daily_email.html', stats)

    # 发送给管理员
    admins = User.objects.filter(is_staff=True, is_active=True)
    for admin in admins:
        try:
            email = EmailMessage(
                subject=f'📊 销售日报 {yesterday}',
                body=html_content,
                from_email='noreply@youpin.com',
                to=[admin.email],
            )
            email.content_subtype = 'html'
            email.send()
        except Exception as e:
            logger.error(f"发送日报失败 {admin.email}: {e}")

    return stats
```

### 场景 2：清理过期数据（验证码、临时文件、已取消订单）

```python
# maintenance/tasks.py
from celery import shared_task
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta

@shared_task
def clean_expired_data():
    """凌晨 3:00 自动清理过期数据"""
    results = {}

    # 1. 清理 24 小时前已取消的订单（释放库存号等）
    from orders.models import Order
    cutoff = timezone.now() - timedelta(hours=24)
    deleted, _ = Order.objects.filter(
        status='cancelled', updated_at__lt=cutoff
    ).delete()
    results['cancelled_orders'] = deleted

    # 2. 清理 7 天前的临时导出文件
    from django.core.files.storage import default_storage
    old_files = default_storage.listdir('reports/')[1]
    for f in old_files:
        # 检查文件时间...
        pass
    results['old_files_deleted'] = len(old_files)

    # 3. 清理过期的 Redis 会话
    # Redis 自带 TTL 过期，不需额外处理

    logger.info(f"数据清理完成: {results}")
    return results
```

### 场景 3：库存预警 + 自动创建采购建议

```python
# products/tasks.py
from celery import shared_task
from django.core.mail import send_mail

@shared_task
def check_low_stock_and_alert():
    """每 30 分钟检查库存，低于安全线的自动告警 + 生成采购建议"""
    from products.models import Product

    low_stock = Product.objects.filter(
        is_active=True,
        stock__lte=models.F('safety_stock')  # 低于安全库存
    )

    if not low_stock.exists():
        return {'alert': False, 'count': 0}

    # 按供应商分组
    by_supplier = {}
    for p in low_stock:
        by_supplier.setdefault(p.supplier_id, []).append({
            'product_id': p.id,
            'title': p.title,
            'stock': p.stock,
            'safety_stock': p.safety_stock,
            'suggested_order': p.safety_stock * 2 - p.stock,
        })

    # 给每个供应商发采购建议邮件
    for supplier_id, products in by_supplier.items():
        supplier = Supplier.objects.get(id=supplier_id)

        product_list = "\n".join(
            f"- {p['title']}: 库存 {p['stock']}, "
            f"安全线 {p['safety_stock']}, "
            f"建议采购 {p['suggested_order']} 件"
            for p in products
        )

        send_mail(
            subject=f'📦 库存预警：{len(products)} 个商品需要补货',
            message=f'{supplier.name}：\n\n以下商品库存低于安全线：\n\n{product_list}',
            from_email='noreply@youpin.com',
            recipient_list=[supplier.email],
        )

    # 同时通知内部运营
    send_mail(
        subject=f'⚠️ 库存预警：{low_stock.count()} 个商品需要关注',
        message=f'已自动通知 {len(by_supplier)} 个供应商补货',
        from_email='noreply@youpin.com',
        recipient_list=['ops@youpin.com'],
    )

    return {
        'alert': True,
        'low_stock_count': low_stock.count(),
        'suppliers_notified': len(by_supplier),
    }
```

---

## 9. 认证与权限 — 3 个场景：JWT登录、RBAC权限、Google OAuth2

```bash
pip install djangorestframework-simplejwt django-allauth
```

### 场景 1：JWT 登录 + 刷新 + 登出（黑名单）

```python
# settings.py
from datetime import timedelta

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,        # 每次刷新同时换新 refresh token
    'BLACKLIST_AFTER_ROTATION': True,     # 旧 refresh token 进黑名单
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```

```python
# views.py
from rest_framework_simplejwt.tokens import RefreshToken, OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """登录 → 返回 access + refresh token"""
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)
    if not user:
        return Response({'error': '用户名或密码错误'}, status=401)

    refresh = RefreshToken.for_user(user)

    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': {
            'id': user.id,
            'username': user.username,
            'is_staff': user.is_staff,
        },
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """登出 → 将当前 refresh token 加入黑名单"""
    try:
        refresh_token = request.data['refresh']
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': '已登出'})
    except TokenError:
        return Response({'error': '无效的 Token'}, status=400)

@api_view(['POST'])
def refresh_token_view(request):
    """刷新 access token"""
    try:
        refresh = RefreshToken(request.data['refresh'])
        return Response({'access': str(refresh.access_token)})
    except TokenError:
        return Response({'error': 'Token 已过期或无效'}, status=401)

# urls.py
urlpatterns += [
    path('api/auth/login/', login_view),
    path('api/auth/logout/', logout_view),
    path('api/auth/refresh/', refresh_token_view),
]
```

### 场景 2：RBAC 权限控制（管理员/运营/普通用户）

```python
# permissions.py
from rest_framework.permissions import BasePermission

class IsAdminUser(BasePermission):
    """仅超级管理员"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff

class IsOwnerOrAdmin(BasePermission):
    """资源所有者 或 管理员"""
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.user == request.user

class HasPermission(BasePermission):
    """基于 Django Permission 的细粒度控制"""

    def __init__(self, codename):
        self.codename = codename

    def has_permission(self, request, view):
        return request.user.has_perm(f'app.{self.codename}')

class CanManageProducts(BasePermission):
    """可以管理商品（编辑/上下架/删除）"""
    def has_permission(self, request, view):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        if request.user.is_staff:
            return True
        return request.user.has_perm('products.change_product')

# views.py — 使用
class ProductViewSet(viewsets.ModelViewSet):

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy', 'batch_toggle'):
            return [CanManageProducts()]
        return [IsAuthenticated()]
```

```python
# 用 Django 内置 Group + Permission 管理角色
from django.contrib.auth.models import Group, Permission

# 创建运营组
operations, _ = Group.objects.get_or_create(name='运营人员')
operations.permissions.add(
    Permission.objects.get(codename='change_product'),
    Permission.objects.get(codename='view_order'),
    Permission.objects.get(codename='change_order'),
)

# 创建只读组
readonly, _ = Group.objects.get_or_create(name='只读用户')
readonly.permissions.add(
    Permission.objects.get(codename='view_product'),
    Permission.objects.get(codename='view_order'),
)
```

### 场景 3：Google OAuth2 第三方登录

```python
# settings.py
INSTALLED_APPS += [
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': os.getenv('GOOGLE_CLIENT_ID'),
            'secret': os.getenv('GOOGLE_CLIENT_SECRET'),
        },
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    }
}

# urls.py
urlpatterns += [path('accounts/', include('allauth.urls'))]

# 前端访问 /accounts/google/login/ 发起 Google OAuth2 登录
# 回调 /accounts/google/login/callback/ 自动处理
```

---

## 10. 监控 — 3 个场景：异常监控、SQL排查、请求分析

### 场景 1：Sentry 异常监控（所有未捕获异常自动上报）

```bash
pip install sentry-sdk
```

```python
# settings.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.redis import RedisIntegration

if not DEBUG:
    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN'),
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
            RedisIntegration(),
        ],
        traces_sample_rate=0.2,      # 20% 请求记录完整调用链
        profiles_sample_rate=0.1,    # 10% 请求做性能剖析
        environment=os.getenv('ENV', 'production'),
        release=os.getenv('APP_VERSION', '1.0.0'),
        send_default_pii=False,      # 不发送用户个人信息
    )
```

**效果**：所有 500 错误自动上报 Sentry，附带完整的请求上下文、数据库查询、调用栈，支持邮件/钉钉/飞书通知。

### 场景 2：django-debug-toolbar 排查 SQL 查询

```bash
pip install django-debug-toolbar
```

```python
# settings.py（仅开发环境）
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
    INTERNAL_IPS = ['127.0.0.1']
```

**使用**：打开任意页面，右侧出现工具栏，点击可见：
- **SQL**：本请求执行了哪些查询、每条耗时、有无重复查询
- **Cache**：缓存命中/未命中次数
- **Templates**：模板渲染耗时
- **Signals**：触发了哪些 Django 信号

**实际排查案例**：
- `product_list` 页面执行了 51 条 SQL → 发现是 N+1 问题 → 加上 `select_related('category')` → 降到 2 条
- `order_detail` 页面重复查了 5 次相同数据 → 加视图缓存 → 首次外不再查 DB

### 场景 3：django-silk 请求分析和性能瓶颈定位

```bash
pip install django-silk
```

```python
# settings.py
INSTALLED_APPS += ['silk']
MIDDLEWARE.insert(0, 'silk.middleware.SilkyMiddleware')

# 生产环境建议：只对部分请求启用
SILKY_PYTHON_PROFILER = True    # 开启 Python profiler
SILKY_MAX_REQUEST_BODY_SIZE = 1024 * 1024  # 1MB
SILKY_MAX_RESPONSE_BODY_SIZE = 1024 * 1024

# urls.py
urlpatterns += [path('silk/', include('silk.urls'))]
```

**使用**：访问 `/silk/` 查看所有请求记录，每个请求包含：
- 请求体/响应体
- 所有 SQL 查询和耗时
- 代码级别的 cProfile 火焰图
- 可对比两次请求的性能差异

---

## 11. 测试 — 3 个场景：模型测试、API测试、异步任务测试

```bash
pip install pytest pytest-django pytest-cov factory-boy
```

```ini
# pytest.ini
[pytest]
DJANGO_SETTINGS_MODULE = myproject.settings
python_files = test_*.py
addopts = --cov=. --cov-report=html --cov-report=term-missing -v
```

### 场景 1：模型测试 + 工厂数据

```python
# tests/conftest.py — 全局 Fixtures
import pytest
from django.contrib.auth import get_user_model
import factory
from products.models import Product, Category

class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category
    name = factory.Sequence(lambda n: f'分类{n}')
    slug = factory.Sequence(lambda n: f'category-{n}')

class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product
    title = factory.Sequence(lambda n: f'商品{n}')
    price = 99.00
    stock = 100
    category = factory.SubFactory(CategoryFactory)

@pytest.fixture
def user():
    return get_user_model().objects.create_user(username='test', password='test123')

@pytest.fixture
def admin_user():
    return get_user_model().objects.create_superuser(username='admin', password='admin123')

@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()

@pytest.fixture
def product():
    return ProductFactory()
```

```python
# tests/test_models.py
import pytest

@pytest.mark.django_db
class TestProductModel:

    def test_create_product(self, product):
        assert product.title == '商品0'
        assert product.price == 99.00
        assert product.stock == 100
        assert product.is_active is True

    def test_price_cannot_be_negative(self):
        """价格不能为负"""
        with pytest.raises(Exception):
            ProductFactory(price=-1)

    def test_stock_decrease(self, product):
        """库存扣减"""
        product.stock -= 5
        product.save()
        product.refresh_from_db()
        assert product.stock == 95

    def test_category_cascade_delete(self, product):
        """删除分类时级联删除商品"""
        category_id = product.category_id
        Category.objects.get(id=category_id).delete()
        assert not Product.objects.filter(id=product.id).exists()
```

### 场景 2：API 接口测试

```python
# tests/test_api.py
import pytest
from rest_framework import status

@pytest.mark.django_db
class TestProductAPI:

    def test_list_products(self, api_client, product):
        """GET /api/products/ 返回商品列表"""
        response = api_client.get('/api/products/')
        assert response.status_code == 200
        assert response.data['count'] >= 1

    def test_create_product_authenticated(self, api_client, admin_user):
        """认证用户可创建商品"""
        api_client.force_authenticate(user=admin_user)
        category = CategoryFactory()
        response = api_client.post('/api/products/', {
            'title': '新商品', 'price': 50, 'stock': 20,
            'category': category.id,
        })
        assert response.status_code == 201

    def test_create_product_unauthenticated(self, api_client):
        """未认证用户不能创建"""
        response = api_client.post('/api/products/', {'title': '商品'})
        assert response.status_code == 401

    def test_search_products(self, api_client):
        """搜索商品"""
        ProductFactory(title='Python高级编程')
        ProductFactory(title='Django教程')
        ProductFactory(title='Java入门')

        response = api_client.get('/api/products/?search=Python')
        assert response.status_code == 200
        assert response.data['count'] == 1
        assert 'Python' in response.data['results'][0]['title']

    def test_filter_by_category(self, api_client):
        """按分类过滤"""
        cat_a, cat_b = CategoryFactory(), CategoryFactory()
        ProductFactory.create_batch(3, category=cat_a)
        ProductFactory.create_batch(2, category=cat_b)

        response = api_client.get(f'/api/products/?category_id={cat_a.id}')
        assert response.data['count'] == 3

    def test_low_stock_endpoint(self, api_client):
        """低库存预警接口"""
        ProductFactory(title='缺货商品', stock=3)
        ProductFactory(title='库存充足', stock=50)

        response = api_client.get('/api/products/low-stock/?threshold=5')
        assert response.status_code == 200
        assert response.data['count'] == 1
        assert '缺货商品' in response.data['products'][0]['title']

    def test_create_order_with_transaction(self, api_client, user):
        """创建订单 + 库存扣减"""
        api_client.force_authenticate(user=user)
        product = ProductFactory(stock=10)

        response = api_client.post('/api/orders/', {
            'items': [{'product_id': product.id, 'quantity': 3}],
        }, format='json')
        assert response.status_code == 201

        # 验证库存被扣减
        product.refresh_from_db()
        assert product.stock == 7

    def test_order_fails_when_oversell(self, api_client, user):
        """库存不足时订单创建失败"""
        api_client.force_authenticate(user=user)
        product = ProductFactory(stock=2)

        response = api_client.post('/api/orders/', {
            'items': [{'product_id': product.id, 'quantity': 5}],
        }, format='json')
        assert response.status_code == 400

        # 库存不应被扣
        product.refresh_from_db()
        assert product.stock == 2
```

### 场景 3：Celery 异步任务测试

```python
# tests/test_tasks.py
import pytest
from django.core.cache import cache
from celery.contrib.testing.worker import start_worker

@pytest.mark.django_db(transaction=True)
class TestCeleryTasks:

    def test_send_welcome_email_task(self, celery_app, celery_worker):
        """测试欢迎邮件任务"""
        from accounts.tasks import send_welcome_email
        user = get_user_model().objects.create_user(
            username='test', email='test@example.com'
        )

        result = send_welcome_email.delay(user.id)
        result.get(timeout=10)  # 等待任务完成
        assert result.successful()

    def test_grant_bonus_task(self, celery_app, celery_worker):
        """测试积分赠送任务"""
        from accounts.tasks import grant_new_user_bonus
        user = get_user_model().objects.create_user(username='test')

        result = grant_new_user_bonus.delay(user.id)
        result.get(timeout=10)

        user.userprofile.refresh_from_db()
        assert user.userprofile.points == 50

    def test_redis_lock_seckill(self):
        """测试分布式锁"""
        lock = RedisLock('test:seckill', expire=5)

        # 第一次获取成功
        assert lock.acquire() is True

        # 第二次获取失败（锁被占用）
        lock2 = RedisLock('test:seckill', expire=5, retry_times=1)
        assert lock2.acquire() is False

        # 释放后重新获取成功
        lock.release()
        lock3 = RedisLock('test:seckill', expire=5)
        assert lock3.acquire() is True
        lock3.release()

    def test_rate_limiter_sms(self):
        """测试短信验证码防刷"""
        phone = '13800138000'

        # 可以发送
        ok, msg = RateLimiter.check_sms_limit(phone)
        assert ok is True

        RateLimiter.record_sms_sent(phone, '127.0.0.1')

        # 60 秒内不能重复发送
        ok, msg = RateLimiter.check_sms_limit(phone)
        assert ok is False
        assert '60 秒' in msg

    def test_cache_aside_pattern(self):
        """测试 Cache Aside 缓存模式"""
        # 第一次读 DB
        products = HomePageService.get_home_products()
        assert len(products) >= 0

        # 缓存命中
        assert cache.get(HomePageService.CACHE_KEY) is not None

        # 更新商品后缓存失效
        product = ProductFactory()
        assert cache.get(HomePageService.CACHE_KEY) is None

        # 下次读时重建缓存
        products2 = HomePageService.get_home_products()
        assert cache.get(HomePageService.CACHE_KEY) is not None
```

---

## 12. Gunicorn 部署 — 核心配置

```bash
pip install gunicorn
```

```bash
#!/bin/bash
# start.sh — 生产环境启动脚本

gunicorn myproject.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --worker-class sync \
  --threads 2 \
  --timeout 30 \
  --max-requests 1000 \
  --max-requests-jitter 50 \
  --keep-alive 5 \
  --access-logfile /var/log/gunicorn/access.log \
  --error-logfile /var/log/gunicorn/error.log \
  --log-level info \
  --preload \
  --daemon
```

- `--workers 4`：CPU 核数 × 2 + 1
- `--max-requests 1000`：每个 worker 处理 1000 个请求后自动重启（防内存泄漏）
- `--preload`：预加载应用（fork 前加载，共享内存，节省资源）

---

> **Django 后端技术栈核心原则：DRF 做 API、Celery 做异步、Redis 做缓存+锁、Channels 做实时推送、Meilisearch 做搜索、MinIO 做存储、Sentry 做监控、pytest 做测试、Gunicorn + Nginx 做部署。**
