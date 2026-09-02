# NestJS 完整指南

> NestJS 是一个用于构建高效、可扩展 Node.js 服务端应用的框架。它使用渐进式 JavaScript，内建并完全支持 TypeScript（但仍允许开发者使用纯 JavaScript 编码），并结合了 OOP（面向对象编程）、FP（函数式编程）和 FRP（函数响应式编程）的元素。

---

## 目录

1. [概述](#1-概述)
2. [安装与项目初始化](#2-安装与项目初始化)
3. [核心概念：Controller、Module、Provider](#3-核心概念controllermoduleprovider)
4. [路由与请求处理](#4-路由与请求处理)
5. [Provider 与依赖注入详解](#5-provider-与依赖注入详解)
6. [Module 模块系统](#6-module-模块系统)
7. [中间件 Middleware](#7-中间件-middleware)
8. [异常过滤器 Exception Filter](#8-异常过滤器-exception-filter)
9. [管道 Pipe](#9-管道-pipe)
10. [守卫 Guard](#10-守卫-guard)
11. [拦截器 Interceptor](#11-拦截器-interceptor)
12. [自定义装饰器](#12-自定义装饰器)
13. [数据库集成 TypeORM](#13-数据库集成-typeorm)
14. [配置管理](#14-配置管理)
15. [文件上传](#15-文件上传)
16. [任务调度](#16-任务调度)
17. [WebSocket](#17-websocket)
18. [GraphQL](#18-graphql)
19. [性能优化](#19-性能优化)
20. [单元测试与 E2E 测试](#20-单元测试与-e2e-测试)

---

## 1. 概述

### 1.1 NestJS 是什么？

**一句话**：NestJS 是 Node.js 的后端框架，它用"类 + 装饰器"的写法来组织代码，底层跑的是 Express（默认）或 Fastify。

如果把 Express 比作"毛坯房"——你需要自己决定怎么组织路由、怎么管理数据库连接、怎么做参数校验，那么 NestJS 就是"精装修房"——它规定了一套固定的组织方式，你只要按照它的规则来写，就能自动获得路由解析、参数校验、依赖注入、异常处理等一系列能力。

### 1.2 为什么要用 NestJS？

| 场景 | Express 做法 | NestJS 做法 |
|------|-------------|------------|
| 路由管理 | 一个文件所有路由，或自己拆 | `@Controller('users')` 声明式拆分为控制器 |
| 参数验证 | 写 `if` 判断或引入 joi | `@Body() dto` + `class-validator` 装饰器自动验证 |
| 权限检查 | 每个路由里写 `if (!req.user)` | `@UseGuards(AuthGuard)` 声明式守卫 |
| 依赖管理 | `require()` 到处引入 | 构造函数注入，IoC 容器自动管理 |
| 测试 | 需要 mock `require()` | 用 `Test.createTestingModule` 替换 Provider |

**总结**：项目越大，NestJS 的架构约束带来的收益越明显——它让团队所有成员用同一种方式组织代码，新人接手模块时能立刻理解其结构。

### 1.3 核心设计思想

NestJS 借鉴了 **Angular** 的架构理念，核心围绕三个概念：

1. **模块化（Module）**：用 `@Module()` 装饰器将功能拆分为独立模块，每个模块包含自己的 controller、service、imports、exports。应用就是一棵模块树。
2. **依赖注入（DI）**：不需要手动 `new` 对象，而是在类的构造函数中声明"我需要什么"，由 NestJS 的 IoC 容器负责创建对象并注入依赖。这让你可以轻松替换实现（比如测试时注入 Mock 而非真实数据库连接）。
3. **装饰器（Decorator）**：用 `@Get()`、`@Post()`、`@Body()` 等声明式语法描述路由行为，而不是写 `router.get()` 式的命令式调用。

### 1.4 核心架构图

```text
┌───────────────────────────────────────────────────────┐
│                    AppModule (根模块)                    │
│                                                         │
│   imports: [UserModule, ProductModule, ...]             │
│                                                         │
│   ┌───────────── UserModule ───────────────┐            │
│   │                                          │           │
│   │  controllers: [UserController]          │           │
│   │  providers:   [UserService]             │           │
│   │  imports:     [DatabaseModule]          │           │
│   │  exports:     [UserService]             │           │
│   │                                          │           │
│   │  ┌──────────────────────────────────┐   │           │
│   │  │  Middleware → Guard → Interceptor │  │           │
│   │  │  → Pipe → Controller → Service   │  │           │
│   │  │  → 响应 → ExceptionFilter        │  │           │
│   │  └──────────────────────────────────┘   │           │
│   └─────────────────────────────────────────┘           │
└───────────────────────────────────────────────────────┘
```

### 1.5 请求生命周期（每条请求的完整路径）

```text
客户端发请求
  │
  ▼
① Middleware（中间件）
  作用：请求进入后第一个处理。常用于日志记录、CORS、请求解析等。
  可以访问原始 req/res 对象，调用 next() 放行或直接返回响应。
  │
  ▼
② Guard（守卫）
  作用：决定"能不能访问"。用于认证（登录检查）和授权（角色/权限检查）。
  返回 true 放行，返回 false 返回 403 Forbidden。
  │
  ▼
③ Interceptor（拦截器）- 前置阶段
  作用：在方法执行前做预处理。用于日志、缓存命中返回、请求超时控制。
  │
  ▼
④ Pipe（管道）
  作用：对参数做转换和验证。将 string "1" 转成 number 1，检查必填字段。
  验证失败直接抛异常。
  │
  ▼
⑤ Controller（控制器）
  作用：路由处理器，接收请求参数，调用 Service，返回响应。
  这一步才是你的业务逻辑代码。
  │
  ▼
⑥ Service（服务）
  由 Controller 调用的业务逻辑层，与数据库交互等。
  │
  ▼
⑦ Interceptor（拦截器）- 后置阶段
  作用：对返回值做统一包装。例如统一加 { code: 200, data: ... } 外壳。
  │
  ▼
⑧ ExceptionFilter（异常过滤器）
  作用：捕获未处理的异常。将异常转为统一的错误响应格式。
  只有在上述流程任何一步抛出异常时才会执行。
  │
  ▼
响应返回给客户端
```

**关键理解**：这 8 个步骤中，只有 ⑤Controller 和 ⑥Service 是你写的业务代码，其余都是框架提供的"横切关注点"（cross-cutting concern），它们像洋葱皮一样层层包裹你的业务逻辑，让你不用在每个接口里重复写日志、验证、权限检查这些胶水代码。

---

## 2. 安装与项目初始化

### 2.1 TypeScript 方式（推荐）

**为什么用 TS**：NestJS 的装饰器、依赖注入等特性与 TypeScript 深度集成——在 TS 中可以利用类型元数据自动推导依赖类型，而 JS 需要手动 `@Inject()` 声明。此外，TS 的接口和泛型让你可以定义 DTO、实体类型，获得编译期类型检查。

```bash
# 全局安装 CLI（只需执行一次）
npm i -g @nestjs/cli

# 创建新项目
nest new my-project

# CLI 会询问你选择包管理器（npm/yarn/pnpm），然后自动安装依赖
```

**`nest new` 帮你做了什么**：
1. 创建目录结构（src/、test/）
2. 生成 tsconfig.json（TS 编译配置）
3. 生成 package.json 和 .eslintrc.js
4. 生成入口文件 main.ts 和 app.module.ts
5. 安装 @nestjs/core、@nestjs/common 等核心依赖

### 2.2 项目目录结构（逐层解释）

```text
my-project/
├── src/
│   ├── main.ts                 # 入口：创建 NestApp 实例并监听端口
│   ├── app.module.ts           # 根模块：应用启动时加载的第一个模块
│   ├── app.controller.ts       # 根控制器：处理 http://localhost:3000/ 的请求
│   ├── app.service.ts          # 根服务：根控制器调用的业务逻辑
│   └── app.controller.spec.ts  # 根控制器单元测试
├── test/
│   ├── app.e2e-spec.ts         # E2E 端到端测试
│   └── jest-e2e.json           # E2E 测试的 Jest 配置
├── nest-cli.json               # NestJS CLI 配置
├── tsconfig.json               # TypeScript 编译配置
├── tsconfig.build.json         # 生产构建时的 TS 配置
└── package.json
```

**目录设计理念**：NestJS 遵循"约定优于配置"原则。`src/` 下通常按功能模块（如 `users/`、`products/`）组织，每个模块内部包含 `.controller.ts`、`.service.ts`、`.module.ts`——这样当你要修改"用户"功能时，所有相关文件都在 `src/users/` 目录下。

### 2.3 入口文件 main.ts 逐行解析

```typescript
import { NestFactory } from '@nestjs/core';
// NestFactory 是核心工厂类，负责创建 Nest 应用实例

import { AppModule } from './app.module';
// 根模块——应用从这里启动，像一棵树的根

async function bootstrap() {
  // bootstrap 函数必须用 async，因为 NestFactory.create 返回 Promise

  const app = await NestFactory.create(AppModule);
  // create() 做了几件事：
  // 1. 扫描 AppModule 及其 imports 的模块树
  // 2. 解析所有 Controller 和 Provider 的依赖关系
  // 3. 创建 Express（或 Fastify）HTTP 服务器
  // 4. 将所有路由注册到 HTTP 服务器
  // 返回的 app 实例可以调用 useGlobalPipes、useGlobalFilters 等配置全局功能

  await app.listen(3000);
  // 启动 HTTP 服务器，监听 3000 端口
  // listen 返回 Promise，成功后服务器开始接收请求

  console.log('应用运行在 http://localhost:3000');
}
bootstrap(); // 调用启动函数
```

**常见扩展点**：在 `create()` 之后、`listen()` 之前，你可以：

```typescript
const app = await NestFactory.create(AppModule);

// 1. 设置全局前缀（所有路由前加 /api）
//    例如 @Controller('users') → /api/users
app.setGlobalPrefix('api');

// 2. 注册全局管道（对所有请求的参数做验证和转换）
app.useGlobalPipes(new ValidationPipe());

// 3. 注册全局异常过滤器（统一错误返回格式）
app.useGlobalFilters(new AllExceptionsFilter());

// 4. 启用 CORS（允许跨域请求）
app.enableCors({ origin: ['https://my-frontend.com'] });

// 5. 启用 Gzip 压缩（减小响应体积）
const compression = require('compression');
app.use(compression());

await app.listen(3000);
```

---

## 3. 核心概念：Controller、Module、Provider

这三个概念是 NestJS 的"铁三角"——每个功能模块都由它们组成。

### 3.1 什么是 Controller（控制器）？

**一句话**：控制器就是"接线员"——它接收 HTTP 请求，把参数传给 Service，再把 Service 返回的结果作为 HTTP 响应返回。

**在生命周期中的位置**：请求经过 Middleware → Guard → Interceptor → Pipe 后到达 Controller。Controller 不处理业务逻辑（交给 Service），只做路由归类和请求/响应的格式转换。

**@Controller() 装饰器做了什么？**
当你写 `@Controller('cats')` 时，NestJS 会在底层 Express 上注册 `router.get('/cats', handler)` 等路由。如果你传空字符串 `@Controller()`，它使用类名推断（如 `CatsController` → `/cats`），但一般显式传参更清晰。

**TypeScript：**

```typescript
// cats.controller.ts
import { Controller, Get, Post, Req } from '@nestjs/common';
import { Request } from 'express';

@Controller('cats')  // ← 所有方法的路由都以 /cats 开头
export class CatsController {

  @Get()              // ← GET /cats
  findAll(@Req() request: Request): string {
    return '获取所有猫咪';
  }

  @Post()             // ← POST /cats
  create(): string {
    return '创建一只猫咪';
  }
}
```

**Controller 的最佳实践**：
- 一个 Controller 只负责一个资源类型（RESTful 单一职责）
- Controller 保持薄——不要写 if/else 业务逻辑，全交给 Service
- 不要用 `@Res()` 手动调用 `res.json()` —— 拦截器和异常过滤器会失效

### 3.2 什么是 Provider / Service（服务）？

**一句话**：Service 是"干活的工人"——Controller 接单，Service 干活。

Provider 是 NestJS 中更宽泛的概念：只要是被 `@Injectable()` 标记、能被 IoC 容器管理的类，都是 Provider。Service 是其中最常见的类型。

**`@Injectable()` 装饰器做了什么？**
它告诉 NestJS："这个类可以由 IoC 容器管理"。当你注册并使用时，NestJS 会记住它的元数据（包括构造函数参数的类型），从而在需要时自动实例化并注入依赖。

**TypeScript：**

```typescript
// cats.service.ts
import { Injectable } from '@nestjs/common';

// 定义数据类型
export interface Cat {
  name: string;
  age: number;
  breed: string;
}

@Injectable() // ← 标记：这个类可以被注入
export class CatsService {
  private readonly cats: Cat[] = []; // 用内存数组模拟数据库

  // 创建一只猫
  create(cat: Cat): void {
    this.cats.push(cat);
  }

  // 查询所有猫
  findAll(): Cat[] {
    return this.cats;
  }

  // 按名称查找
  findOne(name: string): Cat | undefined {
    return this.cats.find((cat) => cat.name === name);
  }
}
```

**Service 的最佳实践**：
- Service 不接触 `req`/`res` 对象——它只关心业务数据和逻辑
- Service 通过构造函数注入其他 Service 或 Repository，形成依赖链
- 如果 ServiceA 和 ServiceB 互相引用会导致循环依赖，此时用 `forwardRef(() => ...)` 延迟解析

### 3.3 什么是 Module（模块）？

**一句话**：Module 是"集装箱"——把 Controller 和 Provider 打包在一起，并声明导入了哪些外部模块、对外提供了哪些 Provider。

**@Module() 的四个属性**：

| 属性 | 说明 |
|------|------|
| `controllers` | 注册该模块的控制器。Client 的 HTTP 请求只能到达注册的 Controller |
| `providers` | 注册该模块的 Provider（通常是 Service）。只在本模块范围内可用 |
| `imports` | 导入其他模块。导入后即可使用其 `exports` 中暴露的 Provider |
| `exports` | 将 Provider 暴露出去，供其他导入本模块的模块使用 |

**TypeScript：**

```typescript
// cats.module.ts
import { Module } from '@nestjs/common';
import { CatsController } from './cats.controller';
import { CatsService } from './cats.service';

@Module({
  controllers: [CatsController],  // 注册控制器
  providers: [CatsService],        // 注册服务（模块内部可用）
  exports: [CatsService],          // 导出服务（其他模块可注入）
})
export class CatsModule {}
```

**为什么需要 Module？** 假设你有两个功能：用户管理（UserModule）和订单管理（OrderModule）。订单模块需要查询用户信息——如果不拆分模块，你就得在订单模块里直接 `require` 用户数据库连接，耦合严重。通过模块化，OrderModule 只需 `imports: [UserModule]`，然后构造函数注入 UserService 即可，无需关心 UserService 内部使用了什么数据库、什么 ORM。

### 3.4 三者的协作流程（以一个完整的请求为例）

```text
GET /cats/Tom 请求到达
  │
  ▼
CatsController.findAll(@Param('name') name)
  │  Controller 不做业务逻辑，直接调用 Service
  │
  ├─→ this.catsService.findOne('Tom')
  │     Service 执行查找逻辑
  │     ← 返回 { name: 'Tom', age: 3, breed: 'Persian' }
  │
  ▼
Controller 把 Service 返回的对象直接 return
  │
  ▼
NestJS 自动序列化为 JSON：{"name":"Tom","age":3,"breed":"Persian"}
  返回给客户端
```

### 3.5 把三者串联到 AppModule

**TypeScript：**

```typescript
// app.module.ts
import { Module } from '@nestjs/common';
import { CatsModule } from './cats/cats.module';

@Module({
  imports: [CatsModule], // 导入 Cats 功能模块
  // 根模块本身通常不定义 controllers 和 providers
  // 它们分散在各个子模块中
})
export class AppModule {}
```

---

## 4. 路由与请求处理

### 4.1 HTTP 方法装饰器概述

NestJS 用装饰器将 HTTP 方法映射到控制器方法，而不是用 `router.get('/path', handler)` 这种命令式写法。

| 装饰器 | 对应 HTTP 方法 | 使用场景 |
|--------|---------------|---------|
| `@Get()` | GET | 读取资源 |
| `@Post()` | POST | 创建资源 |
| `@Put()` | PUT | 完整更新资源 |
| `@Delete()` | DELETE | 删除资源 |
| `@Patch()` | PATCH | 部分更新资源 |
| `@Options()` | OPTIONS | CORS 预检请求 |
| `@Head()` | HEAD | 只获取响应头（不获取 body） |
| `@All()` | 所有方法 | 代理/转发所有请求 |

### 4.2 路由参数获取详解

NestJS 提供了专门的参数装饰器从 HTTP 请求的不同位置提取数据。每种装饰器对应请求的一个部分：

| 装饰器 | 从请求的哪里取值 | 等价原生写法 |
|--------|----------------|------------|
| `@Param('id')` | 路由参数 `/users/:id` | `req.params.id` |
| `@Query('page')` | 查询参数 `?page=1` | `req.query.page` |
| `@Body()` | 请求体（JSON） | `req.body` |
| `@Headers('key')` | 指定请求头 | `req.headers['key']` |
| `@Ip()` | 客户端 IP 地址 | `req.ip` |
| `@HostParam()` | 域名中的参数 `:domain.example.com` | `req.hostname` |
| `@Req()` | 原生请求对象（不推荐） | `req` |
| `@Res()` | 原生响应对象（不推荐） | `res` |
| `@Session()` | Session 对象 | `req.session` |

### 4.3 完整示例：各种参数获取方式

**TypeScript：**

```typescript
import {
  Controller, Get, Post, Param, Query, Body, Headers, Ip, HostParam,
} from '@nestjs/common';

@Controller('users')
export class UsersController {

  // ========== 路径参数 ==========
  // GET /users/42
  // 从 URL 路径中提取 :id 的值
  @Get(':id')
  findOne(@Param('id') id: string): string {
    // id 是 string "42" —— 如需 number，结合 ParseIntPipe 使用
    return `查询用户 ID=${id}`;
  }

  // GET /users/42/posts/7 —— 多路径参数
  @Get(':userId/posts/:postId')
  findPost(
    @Param() params: { userId: string; postId: string }
  ): string {
    // @Param() 不传参 → 拿到所有路径参数的 key-value 对象
    return `用户 ${params.userId} 的文章 ${params.postId}`;
  }

  // ========== 查询参数 ==========
  // GET /users?page=1&limit=10
  @Get()
  findAll(
    @Query('page') page: number,
    @Query('limit') limit: number,
  ): string {
    // 注意：查询参数默认为 string，page 实际上是 "1"，不是 1
    // 如需转为 number，参见后文 Pipe 章节
    return `查询第 ${page} 页，每页 ${limit} 条`;
  }

  // GET /users/search?keyword=nest&sort=desc
  // 拿到所有查询参数（用于条件搜索）
  @Get('search')
  search(@Query() query: Record<string, any>): string {
    return `搜索条件：${JSON.stringify(query)}`;
    // 输出: 搜索条件：{"keyword":"nest","sort":"desc"}
  }

  // ========== 请求体 ==========
  // POST /users  + JSON body: {"name":"John","age":25}
  @Post()
  create(@Body() createUserDto: any): string {
    return `创建用户：${JSON.stringify(createUserDto)}`;
  }

  // POST /users/create-simple
  // 只取 body 中特定字段（不用的字段自动忽略）
  @Post('create-simple')
  createSimple(
    @Body('name') name: string,
    @Body('age') age: number,
  ): string {
    return `创建用户：${name}，年龄：${age}`;
  }

  // ========== 请求头 ==========
  // 读取认证 token 和客户端 IP
  @Get('auth')
  auth(
    @Headers('authorization') token: string,
    @Ip() ip: string,
  ): string {
    return `Token: ${token}, IP: ${ip}`;
    // token: "Bearer eyJhbGciOiJIUzI1NiIs..."
    // ip: "127.0.0.1"
  }

  // ========== 子域名参数（HostParam） ==========
  // 如果域名是 account.example.com
  @Get('tenant')
  getTenant(@HostParam('subdomain') subdomain: string): string {
    return `当前租户子域名：${subdomain}`;
  }
}
```

### 4.4 路由通配符与正则匹配

路由路径可以包含通配符和正则表达式：

```typescript
// 通配符：GET /users/anything → 被此方法处理
// 注意：只匹配一级路径，不匹配 /users/a/b
@Get('*')
wildcard(): string {
  return '通配符 — 所有未匹配到特定路径的请求都到此';
}

// 正则限制：只匹配字母组成的 name，匹配 /users/abc，不匹配 /users/123
@Get(':name([a-z]+)')
byName(@Param('name') name: string): string {
  return `只接受字母名称：${name}`;
}
```

**场景**：正则匹配常用于 ID 格式验证，比如只接受数字 ID，防止 `/users/profile` 被 `/users/:id` 错误匹配。

### 4.5 状态码与响应头 —— 4 种控制方式

**方式 1：@HttpCode() 设置状态码（最常用，推荐）**

默认情况下，`@Get()` 返回 200，`@Post()` 返回 201，`@Delete()` 返回 200。你可以用 `@HttpCode()` 覆盖：

```typescript
@Get('created')
@HttpCode(201)          // 虽然 GET 通常返回 200，但我们强制设为 201
created(): string {
  return '资源创建成功';
}

@Post('no-content')
@HttpCode(204)          // POST 默认 201，改为 204（创建成功但无响应体）
noContent(): void {
  // 返回 void → HTTP 响应体为空
}
```

**方式 2：@Header() 设置响应头**

```typescript
@Get('cache')
@Header('Cache-Control', 'public, max-age=3600')  // 浏览器缓存 1 小时
@Header('X-Custom-Header', 'custom-value')
cached(): string {
  return '这条响应带缓存头';
}
```

**方式 3：@Res() 手动控制（陷阱模式）**

当你用 `@Res()` 获取原生 Express 响应对象并手动调用 `res.json()` 时，NestJS 的拦截器、异常过滤器、`@HttpCode` 等**全部失效**——因为你绕过了框架的响应处理管道。

```typescript
// ❌ 不推荐：拦截器和异常过滤器失效
@Get('manual')
manual(@Res() res: Response): void {
  res.status(200).json({ data: '手动响应' });
}
```

**方式 4：@Res({ passthrough: true }) 混合模式（推荐）**

设置 `passthrough: true` 后，你可以手动设状态码/响应头，但**响应体仍由 NestJS 自动处理**——拦截器和异常过滤器继续生效。

```typescript
// ✅ 推荐：既能手动设状态码，又保留框架能力
@Get('passthrough')
passthrough(@Res({ passthrough: true }) res: Response): object {
  res.status(202);           // 设状态码 202
  res.set('X-Custom', 'v');  // 设自定义头
  return { message: '状态码是 202，但响应体正常由框架处理' };
}
```

**各个方式的对比**：

| 方式 | 状态码 | 响应头 | 拦截器 | 异常过滤器 | 推荐场景 |
|------|-------|--------|--------|-----------|---------|
| `@HttpCode()` | ✅ | ❌ | ✅ | ✅ | 仅需改状态码 |
| `@Header()` | ❌ | ✅ | ✅ | ✅ | 仅需加响应头 |
| `@Res()` 直接 | ✅ | ✅ | ❌ | ❌ | 极特殊（如流式响应） |
| `passthrough` | ✅ | ✅ | ✅ | ✅ | **推荐** |

---

## 5. Provider 与依赖注入详解

### 5.1 什么是依赖注入（DI）？—— 用大白话理解

**不用 DI 的写法**（紧耦合）：

```typescript
// ❌ 没有依赖注入：UserService 自己管理 LoggerService
class UserService {
  private logger = new LoggerService();  // 硬编码依赖
  createUser(data) {
    this.logger.log('创建用户');
    // ...
  }
}
```

**问题**：
- 你想把 LoggerService 换成 CloudLoggerService？要改 UserService 的源码。
- 你写单元测试时想用 MockLoggerService（不打印日志）？做不到。
- LoggerService 本身需要 ConfigService？你在 UserService 里也要关心它的依赖链。

**用 DI 后**（松耦合）：

```typescript
// ✅ 依赖注入：UserService 声明"我需要一个 LoggerService"
class UserService {
  constructor(private logger: LoggerService) {}
  // NestJS 框架负责创建 LoggerService 实例并传给 UserService
}
```

UserService 只管声明"我需要什么"，NestJS 的 IoC 容器负责"创建并传递"。换实现时只需改注册配置，代码一行不动。

### 5.2 IoC 容器的运作原理

NestJS 在启动时会做以下事情：

```text
① 扫描所有 Module 的 providers 数组
② 对每个 Provider，分析其构造函数的参数类型（通过 TypeScript 的类型元数据或 @Inject() 手动声明）
③ 构建依赖图（类似 DAG 有向无环图）
④ 按依赖顺序创建实例：先创建无依赖的（如 ConfigService），再创建依赖 ConfigService 的
⑤ 将所有实例放入容器（默认单例，全局一份）
⑥ Controller 方法被调用时，从容器取出对应的 Service 注入
```

**默认作用域**：所有 Provider 默认是 **Singleton（单例）**，应用只创建一个实例，所有请求共享。你也可以改为 Request 作用域（每个请求一个新实例）或 Transient 作用域（每次注入一个新实例），后文详述。

### 5.3 @Injectable() 装饰器

**作用**：`@Injectable()` 标记这个类可以被 NestJS IoC 容器管理。只有被标记的类，才能在其他类的构造函数中被注入。

```typescript
import { Injectable } from '@nestjs/common';

@Injectable()
export class LoggerService {
  log(message: string): void {
    console.log(`[${new Date().toISOString()}] ${message}`);
  }
}
```

**不标记的后果**：如果忘记写 `@Injectable()`，NestJS 注入时会抛异常，因为缺少元数据。

### 5.4 构造函数注入（最常用）

**TypeScript：**

```typescript
// logger.service.ts
import { Injectable } from '@nestjs/common';

@Injectable()
export class LoggerService {
  log(message: string): void {
    console.log(`[LOG] ${new Date().toISOString()} - ${message}`);
  }
}

// user.service.ts
import { Injectable } from '@nestjs/common';
import { LoggerService } from './logger.service';

@Injectable()
export class UserService {
  // TypeScript 类型标注让 NestJS 自动知道注入 logger: LoggerService
  constructor(private readonly logger: LoggerService) {}

  createUser(data: any): void {
    this.logger.log(`创建用户: ${JSON.stringify(data)}`);
    // ...
  }
}
```

```typescript
// user.module.ts
import { Module } from '@nestjs/common';
import { UserService } from './user.service';
import { LoggerService } from './logger.service';

@Module({
  providers: [UserService, LoggerService], // 两者都注册
})
export class UserModule {}
```

**TS 中不需要手动 `@Inject()`**：因为 NestJS 通过 TypeScript 编译器的 `emitDecoratorMetadata` 选项，能在运行时读取构造函数的参数类型（LoggerService），从而自动找到对应的 Provider。

> **注意**：在 TypeScript 中，NestJS 通过 `emitDecoratorMetadata` 编译选项在运行时读取构造函数参数的类型元数据，从而自动找到对应的 Provider。如果你不使用 TypeScript，需要用 `@Inject()` 手动声明注入目标。

### 5.5 属性注入（@Inject 装饰器）

当构造函数注入不方便时（如基类中需要注入的依赖不确定），使用属性注入：

**TypeScript：**

```typescript
import { Injectable, Inject } from '@nestjs/common';

@Injectable()
export class PaymentService {
  // 用 @Inject() 直接注入属性，不需要构造函数参数
  @Inject('STRIPE_CONFIG')
  private readonly stripeConfig: { apiKey: string };

  @Inject(LoggerService)
  private readonly logger: LoggerService;

  processPayment(amount: number): string {
    this.logger.log(`处理支付: ¥${amount}`);
    return `使用密钥 ${this.stripeConfig.apiKey} 处理支付 ¥${amount}`;
  }
}
```

**场景**：属性注入适合 JS 代码（因为 JS 没有类型元数据），也适合 TS 中的继承场景——当子类构造函数不同但需要相同依赖时。

### 5.6 四种 Provider 定义方式

在 Module 中注册 Provider 时，除了简写（直接放类名），还有 3 种完整写法：

**类型 1：`useClass` —— 动态选择实现类**

使用场景：开发环境用真实的 Stripe 支付，测试环境用 Mock。

```typescript
// 定义接口（TS 中可以用抽象类）
abstract class PaymentProcessor {
  abstract pay(amount: number): string;
}

class StripeProcessor extends PaymentProcessor {
  pay(amount: number): string { return `Stripe: ¥${amount}`; }
}

class MockProcessor extends PaymentProcessor {
  pay(amount: number): string { return `Mock: ¥${amount}`; }
}

// 在 Module 中根据环境选择
const isProd = process.env.NODE_ENV === 'production';

@Module({
  providers: [
    {
      provide: PaymentProcessor,            // 注入 Token
      useClass: isProd ? StripeProcessor : MockProcessor, // 运行时的类
    },
  ],
})
export class PaymentModule {}
```

**效果**：控制器中注入 `PaymentProcessor`，但实际运行时获取的是 StripeProcessor 或 MockProcessor 实例。切换实现只需改注册代码，不碰业务代码。

**类型 2：`useValue` —— 注入固定值/配置对象**

使用场景：配置文件、第三方库实例（如 Redis 客户端）。

```typescript
@Module({
  providers: [
    {
      provide: 'APP_CONFIG',  // 字符串 Token
      useValue: {
        appName: 'MyNestApp',
        version: '1.0.0',
        adminEmail: 'admin@example.com',
      },
    },
    {
      provide: 'REDIS_CLIENT',
      useValue: require('ioredis').default.createClient({
        host: 'localhost',
        port: 6379,
      }),
    },
  ],
})
export class ConfigModule {}
```

**使用处**：`constructor(@Inject('APP_CONFIG') private config: any) {}`

**类型 3：`useFactory` —— 工厂函数动态创建**

使用场景：创建实例前需要读取其他配置，或需要异步初始化。

```typescript
@Module({
  providers: [
    {
      provide: 'DATABASE_CONNECTION',
      useFactory: async (config: any, logger: LoggerService) => {
        // 在工厂内做异步操作（连接数据库等）
        logger.log('正在连接数据库...');
        const connection = await createConnection({
          host: config.dbHost,
          port: config.dbPort,
        });
        logger.log('数据库连接成功');
        return connection;
      },
      inject: ['APP_CONFIG', LoggerService], // 注入依赖到工厂参数
    },
  ],
})
export class DatabaseModule {}
```

**工厂函数参数顺序**：`inject` 数组中的 Token 按顺序对应 `useFactory` 函数的参数。

**类型 4：标准 Provider（简写，最常用）**

```typescript
// 简写形式 —— 等价于 { provide: CatsService, useClass: CatsService }
providers: [CatsService],
```

### 5.7 作用域：Singleton / Request / Transient

默认所有 Provider 是 **单例（Singleton）**——应用整个生命周期只创建 1 个实例，所有请求共享。这性能最好，但在某些场景下需要隔离：

```typescript
import { Injectable, Scope } from '@nestjs/common';

// 请求作用域：每个 HTTP 请求创建一个新实例
// 场景：需要访问请求级别的数据（如当前用户 ID）
@Injectable({ scope: Scope.REQUEST })
export class RequestContextService {
  // 每个请求有自己的实例，实例间不共享状态
  currentUserId: number;
}

// 瞬态作用域：每次注入都创建新实例
// 极少使用，通常用单例
@Injectable({ scope: Scope.TRANSIENT })
export class TransientService {}
```

**作用域影响**：如果 Controller 是 Request 作用域，那么它依赖的所有 Service 也会自动变为 Request 作用域（级联效应）。这会影响性能，非必要时不要用。

### 5.8 循环依赖的处理

当 A 依赖 B，B 也依赖 A 时，NestJS 无法决定先创建谁。解决方案是 `forwardRef()`：

```typescript
// a.service.ts
@Injectable()
export class AService {
  constructor(
    @Inject(forwardRef(() => BService)) private bService: BService,
  ) {}
}

// b.service.ts
@Injectable()
export class BService {
  constructor(
    @Inject(forwardRef(() => AService)) private aService: AService,
  ) {}
}

// module 中也要用 forwardRef
@Module({
  imports: [forwardRef(() => BModule)],
  exports: [AService],
})
export class AModule {}
```

**什么情况下会出现循环依赖**？
- 两个 Service 互相调用对方的方法（如 UserService 需要 OrderService 统计用户的订单数，OrderService 需要 UserService 获取订单的买家信息）
- 这是**设计问题的信号**——考虑是否能引入第三个 Service 打破循环

---

## 6. Module 模块系统

### 6.1 为什么需要模块？

**无模块的问题**：在一个 `app.module.ts` 中注册所有 Controller 和 Provider，当应用达到 50+ 个 Service 时，`providers` 数组将超过上百行，依赖关系难以理清。

**模块化后**：按功能拆分，每个模块自包含其依赖和暴露：

```text
AppModule (根)
├── UserModule
│   ├── controllers: [UserController]
│   ├── providers:   [UserService]
│   ├── exports:     [UserService]    ← 暴露给其他模块
│   └── imports:     [DatabaseModule] ← 需要数据库
├── ProductModule
│   ├── controllers: [ProductController]
│   ├── providers:   [ProductService]
│   └── imports:     [UserModule]     ← 可以注入 UserService
└── DatabaseModule
    ├── providers: [DatabaseProvider]
    └── exports:   [DatabaseProvider]
```

### 6.2 @Module() 四个属性详解

```typescript
@Module({
  // controllers: 该模块的 Controller。请求路由到这个模块时，由这些 Controller 处理
  controllers: [CatsController],

  // providers: 该模块的 Provider（Service/Repository/Factory 等）。
  // 注册到 IoC 容器，只有本模块的 Controller 和 Provider 能注入
  providers: [CatsService],

  // imports: 导入其他模块，使用它们的 exports 中暴露的 Provider
  imports: [SharedModule, TypeOrmModule.forFeature([Cat])],

  // exports: 将本模块的 Provider 暴露出去。只有 exports 中的 Provider 才能被其他模块注入
  exports: [CatsService],
})
export class CatsModule {}
```

### 6.3 共享模块与模块封装

NestJS 模块默认是 **封装的**——模块内的 Provider 对外不可见，只有明确放到 `exports` 中才对外暴露。这样设计是为了防止其他模块意外依赖你的内部实现细节。

**TypeScript：**

```typescript
// shared.module.ts —— 共享模块
import { Module } from '@nestjs/common';
import { LoggerService } from './logger.service';
import { CryptoService } from './crypto.service';

@Module({
  providers: [LoggerService, CryptoService],
  exports: [LoggerService],  // 只导出 LoggerService
  // CryptoService 是模块内部使用的，对外不可见
})
export class SharedModule {}
```

```typescript
// user.module.ts —— 消费模块
import { Module } from '@nestjs/common';
import { SharedModule } from '../shared/shared.module';
import { UserService } from './user.service';

@Module({
  imports: [SharedModule],  // 导入后，可以注入 LoggerService
  providers: [UserService], // 但 CryptoService 无法注入
  // UserService 的构造函数中写 constructor(private logger: LoggerService) 即可
})
export class UserModule {}
```

### 6.4 全局模块 `@Global()`

当你某个模块（如配置模块、工具模块）需要被几乎所有模块引入时，可以标记为全局——其他模块**无需在 imports 中声明**即可注入其 exports 中的 Provider。

**TypeScript：**

```typescript
// config.module.ts
import { Module, Global } from '@nestjs/common';

@Global()
@Module({
  providers: [
    {
      provide: 'APP_CONFIG',
      useValue: {
        port: 3000,
        database: { host: 'localhost', port: 5432 },
      },
    },
  ],
  exports: ['APP_CONFIG'],
})
export class ConfigModule {}
```

```typescript
// 其他任意模块中，无需 imports ConfigModule：
import { Injectable, Inject } from '@nestjs/common';

@Injectable()
export class AppService {
  constructor(@Inject('APP_CONFIG') private config: any) {}
  // config.port → 3000
}
```

**注意**：`@Global()` 虽然方便，但不可滥用。最佳实践是只对 ConfigModule、DatabaseModule 这类基础设施模块使用。

### 6.5 动态模块 —— 传入配置参数

当模块需要接受外部参数来调整行为时（比如连接哪个数据库），使用动态模块。

**TypeScript：**

```typescript
// database.module.ts
import { Module, DynamicModule } from '@nestjs/common';

export interface DatabaseOptions {
  host: string;
  port: number;
  username: string;
  password: string;
}

@Module({})  // 空的 —— 静态定义留空
export class DatabaseModule {
  // static register() 返回一个动态模块定义
  static register(options: DatabaseOptions): DynamicModule {
    return {
      module: DatabaseModule,
      providers: [
        {
          provide: 'DATABASE_OPTIONS',
          useValue: options,  // 把传入的配置作为 Provider
        },
        {
          provide: 'DB_CONNECTION',
          useFactory: (opts: DatabaseOptions) => {
            // 模拟数据库连接
            console.log(`连接数据库：${opts.host}:${opts.port}`);
            return { connected: true, host: opts.host };
          },
          inject: ['DATABASE_OPTIONS'],
        },
      ],
      exports: ['DB_CONNECTION'],
    };
  }

  // registerAsync 用于异步获取配置（如从 ConfigService 读取）
  static registerAsync(options: {
    useFactory: (...args: any[]) => Promise<DatabaseOptions> | DatabaseOptions;
    inject: any[];
  }): DynamicModule {
    return {
      module: DatabaseModule,
      providers: [
        {
          provide: 'DATABASE_OPTIONS',
          useFactory: options.useFactory,
          inject: options.inject,
        },
        {
          provide: 'DB_CONNECTION',
          useFactory: (opts: DatabaseOptions) => ({
            connected: true,
            host: opts.host,
          }),
          inject: ['DATABASE_OPTIONS'],
        },
      ],
      exports: ['DB_CONNECTION'],
    };
  }
}
```

```typescript
// 在 AppModule 中使用：
@Module({
  imports: [
    // 方式 1：静态参数
    DatabaseModule.register({
      host: 'localhost',
      port: 5432,
      username: 'admin',
      password: 'secret',
    }),

    // 方式 2：从环境变量读取（需要先加载 ConfigModule）
    DatabaseModule.registerAsync({
      inject: [ConfigService],
      useFactory: (config: ConfigService) => ({
        host: config.get('DB_HOST'),
        port: config.get('DB_PORT'),
        username: config.get('DB_USERNAME'),
        password: config.get('DB_PASSWORD'),
      }),
    }),
  ],
})
export class AppModule {}
```

**`register()` vs `forRoot()` vs `forFeature()`**：NestJS 生态中，命名约定：
- `register()` — 每次调用创建独立配置，通常给"消费者模块"用的
- `forRoot()` — 在根模块调用一次，配置全局共享，通常给"基础设施模块"用的
- `forFeature()` — TypeORM 专用，注册实体到指定模块

### 6.6 模块重新导出

一个模块可以导入另一个模块，然后直接重新导出——上层模块不需要知道中间模块的存在。

```typescript
// common.module.ts —— 聚合模块，把多个基础模块打包
@Module({
  imports: [LoggerModule, TemplateModule, ValidationModule],
  exports: [LoggerModule, TemplateModule, ValidationModule],
})
export class CommonModule {}

// 业务模块只需要导入 CommonModule 即可使用 LoggerService 等
@Module({
  imports: [CommonModule],  // 一行导入，获得三个模块的能力
})
export class OrderModule {}
```

这个模式在大型项目中非常实用，可以避免每个业务模块的 imports 列表长达 10+ 行。

---

（未完，接第二部分）

---

## 7. 中间件 Middleware

### 7.1 中间件是什么？（大白话解释）

**一句话**：中间件是请求进入 NestJS 后**第一个经过的处理层**，它在 Guard 和 Pipe 之前执行，可以直接操作原生的 Express `req`/`res` 对象。

**中间件在生命周期中的位置**：

```text
Request → ①Middleware → ②Guard → ③Interceptor(Before) → ④Pipe
→ ⑤Controller → ⑥Service → ... → Response
```

**中间件和 Guard / Interceptor 的区别**：
- **Middleware**：可以访问原始 `req`/`res`，类似 Express 中间件。用 `next()` 控制流程。
- **Guard**：只做"能不能访问"的判断，返回 true/false，不操作响应。
- **Interceptor**：可以操作方法调用的结果（返回值），但不能修改原始 `req`。

### 7.2 中间件的核心原理

中间件实现 `NestMiddleware` 接口，在 `use(req, res, next)` 方法中处理逻辑。你可以：
1. 在请求处理**前**做操作（记录日志、解析 cookie）
2. 调用 `next()` 放行
3. 在 `res.on('finish')` 回调中做响应后的操作（统计耗时）
4. 直接返回响应（如 IP 黑名单直接 res.status(403).end()）

### 7.3 类中间件（完整示例）

**TypeScript：**

```typescript
import { Injectable, NestMiddleware } from '@nestjs/common';
import { Request, Response, NextFunction } from 'express';

@Injectable()
export class LoggerMiddleware implements NestMiddleware {
  use(req: Request, res: Response, next: NextFunction): void {
    const { method, originalUrl } = req;
    const startTime = Date.now();

    // 打印请求信息
    console.log(`[${method}] ${originalUrl} - 开始处理`);

    // 监听响应完成事件（当 HTTP 响应发送完毕时触发）
    res.on('finish', () => {
      const duration = Date.now() - startTime;
      const statusCode = res.statusCode;

      // 根据状态码用不同日志级别
      if (statusCode >= 400) {
        console.error(`[${method}] ${originalUrl} - ${statusCode} - ${duration}ms ⚠️`);
      } else {
        console.log(`[${method}] ${originalUrl} - ${statusCode} - ${duration}ms ✅`);
      }
    });

    next(); // 必须调用，否则请求会挂起
  }
}
```

### 7.4 函数中间件（无依赖时的轻量方案）

如果中间件不需要注入其他 Service，可以写成一个简单函数——不需要 `@Injectable()`：

**TypeScript：**

```typescript
import { Request, Response, NextFunction } from 'express';

export function corsMiddleware(req: Request, res: Response, next: NextFunction): void {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (req.method === 'OPTIONS') {
    res.sendStatus(200);  // 预检请求直接响应，不继续处理
  } else {
    next();
  }
}
```

**什么时候用函数中间件 vs 类中间件**：
- 函数中间件：不需要依赖注入时（纯功能，如 CORS、helmet）
- 类中间件：需要通过构造函数注入其他 Service 时（如日志中间件需要 LoggerService）

### 7.5 在模块中配置中间件范围

中间件不像 Guard/Interceptor 那样可以用 `@UseGuards()` 装饰器挂在 Controller 上，而是**在 Module 中通过 `configure()` 方法声明其作用范围**。

**TypeScript：**

```typescript
import {
  Module,
  MiddlewareConsumer,
  NestModule,
  RequestMethod,
} from '@nestjs/common';
import { LoggerMiddleware } from './logger.middleware';
import { CorsMiddleware } from './cors.middleware';
import { CatsController } from './cats.controller';

@Module({
  controllers: [CatsController],
})
export class CatsModule implements NestModule {
  configure(consumer: MiddlewareConsumer): void {
    consumer
      // .apply() 应用一个或多个中间件
      .apply(LoggerMiddleware, CorsMiddleware)

      // 只对特定路由生效
      .forRoutes('cats');  // 等价于所有 /cats/* 路由

    // 也可以多次 configure，精确控制不同路径用不同中间件
    consumer
      .apply(LoggerMiddleware)

      // exclude 排除某些路由
      .exclude(
        { path: 'cats/health', method: RequestMethod.GET },  // 健康检查不需要日志
        { path: 'cats/metrics', method: RequestMethod.ALL },
      )

      // forRoutes 指定作用范围
      .forRoutes(
        { path: 'cats/create', method: RequestMethod.POST },  // 仅 POST
        { path: 'cats/*', method: RequestMethod.GET },        // 仅 GET
        CatsController,  // 直接传 Controller 类 → 该控制器所有路由
      );
  }
}
```

### 7.6 全局中间件（main.ts 中注册）

全局中间件**只能是函数式**（不是类中间件），通过 `app.use()` 注册：

```typescript
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import * as helmet from 'helmet';
import * as rateLimit from 'express-rate-limit';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // 安全头中间件（第三方）
  app.use(helmet());

  // 请求限流
  app.use(
    rateLimit({
      windowMs: 15 * 60 * 1000,  // 15 分钟窗口
      max: 100,                    // 窗口内最多 100 次请求
    }),
  );

  // 自定义全局函数中间件
  app.use((req, res, next) => {
    const userAgent = req.headers['user-agent'] || 'unknown';
    (req as any).userAgent = userAgent;
    next();
  });

  await app.listen(3000);
}
bootstrap();
```

### 7.7 中间件常见使用场景

| 场景 | 中间件示例 |
|------|---------|
| 日志记录 | 记录每个请求的方法、路径、耗时、状态码 |
| CORS | 设置允许跨域的头和预检响应 |
| 安全头 | helmet（防 XSS、点击劫持等） |
| 限流 | express-rate-limit |
| 请求体解析 | `express.json()`、`express.urlencoded()` |
| Cookie/Session 解析 | `cookie-parser`、`express-session` |
| IP 黑名单 | 检查 `req.ip`，匹配到黑名单直接返回 403 |
| 请求 ID 注入 | 每个请求生成 UUID，挂到 `req` 上便于日志追踪 |

### 7.8 中间件的注意事项

1. **必须调用 `next()`**：忘记调用会导致请求永久挂起（除非你直接 `res.end()` 了）。
2. **能解析原始 body**：中间件在请求体被 pipe/controller 处理之前执行，可以在此阶段对原始数据做处理。
3. **不能注入到 Controller**：中间件是整个模块级别的，无法像 `@UseGuards()` 那样挂在单个路由方法上。如果某个中间件只需要对单个方法生效，用 `{ path, method }` 精确指定。
4. **与 Interceptor 的选择**：如果你需要访问返回值（而不是原始请求），应该用 Interceptor 而不是 Middleware。

---

## 8. 异常过滤器 Exception Filter

### 8.1 异常过滤器是什么？

**一句话**：异常过滤器是"最后一道防线"——当 Controller 或 Service 中任何地方抛出异常时，过滤器捕获它，转换为格式化的 HTTP 响应发给客户端。

**为什么需要**：没加过滤器时，NestJS 默认返回的异常格式是 `{ statusCode: 400, message: '...' }`。如果你的前端需要统一格式 `{ code: 400, msg: '...', path: '/...' }`，就需要自定义过滤器来转换。

### 8.2 NestJS 内置的异常类

NestJS 提供了一系列 `HttpException` 的子类，对应各个 HTTP 状态码。抛出这些异常时，框架自动返回正确的状态码：

| 异常类 | 状态码 | 何时抛出 |
|--------|--------|---------|
| `BadRequestException` | 400 | 请求参数错误（通过 Pipe 自动抛） |
| `UnauthorizedException` | 401 | 未登录或 token 无效 |
| `ForbiddenException` | 403 | 已登录但无权限 |
| `NotFoundException` | 404 | 资源不存在 |
| `ConflictException` | 409 | 资源冲突（如重复创建） |
| `PayloadTooLargeException` | 413 | 请求体过大 |
| `TooManyRequestsException` | 429 | 请求过于频繁 |
| `InternalServerErrorException` | 500 | 服务器内部错误 |
| `BadGatewayException` | 502 | 上游服务异常 |
| `ServiceUnavailableException` | 503 | 服务暂时不可用 |

### 8.3 基础用法：抛出和自定义异常信息

```typescript
// 方式 1：只传错误消息
throw new NotFoundException(`用户 #${id} 不存在`);
// 响应: { "statusCode": 404, "message": "用户 #99 不存在" }

// 方式 2：传自定义响应格式
throw new BadRequestException({
  code: 400,
  error: 'VALIDATION_FAILED',
  message: '邮箱格式不正确',
  field: 'email',
  value: 'not-an-email',
});
// 响应: { "statusCode": 400, "message": { ...上面那个对象 } }

// 方式 3：传消息 + 描述（第二个参数）
throw new UnauthorizedException(
  '请先登录',
  'TOKEN_EXPIRED',  // 描述字段，在 error 属性中返回
);
// 响应: { "statusCode": 401, "message": "请先登录", "error": "TOKEN_EXPIRED" }
```

### 8.4 自定义异常过滤器（统一响应格式）

**TypeScript：**

```typescript
import {
  ExceptionFilter,
  Catch,
  ArgumentsHost,
  HttpException,
  HttpStatus,
} from '@nestjs/common';
import { Request, Response } from 'express';

// @Catch(HttpException) → 只捕获 HttpException 及其子类
// @Catch()              → 捕获所有异常（包括非 HTTP 异常）
@Catch(HttpException)
export class HttpExceptionFilter implements ExceptionFilter {

  catch(exception: HttpException, host: ArgumentsHost): void {
    // === 第 1 步：获取上下文 ===
    // host.switchToHttp() 将通用执行上下文转为 HTTP 上下文
    // （因为 NestJS 也支持 WebSocket、RPC 等，所以需要 switch）
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();
    const request = ctx.getRequest<Request>();

    // === 第 2 步：获取异常信息 ===
    const status = exception.getStatus();
    const exceptionResponse = exception.getResponse();

    // getResponse() 可能返回字符串或对象
    let message: string;
    if (typeof exceptionResponse === 'string') {
      message = exceptionResponse;
    } else {
      message = (exceptionResponse as any).message || exception.message;
    }

    // === 第 3 步：构造统一格式的响应 ===
    response.status(status).json({
      code: status,
      message: Array.isArray(message) ? message.join('; ') : message, // ValidationPipe 可能返回数组
      path: request.url,
      method: request.method,
      timestamp: new Date().toISOString(),
    });
  }
}
```

### 8.5 捕获所有异常的过滤器

`@Catch()` 不传参数可以捕获**一切异常**——包括 `throw new Error('数据库挂了')` 这种不是 HttpException 的错误：

```typescript
@Catch()  // ← 不传参 = 捕获所有
export class AllExceptionsFilter implements ExceptionFilter {
  catch(exception: unknown, host: ArgumentsHost): void {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();

    let status = HttpStatus.INTERNAL_SERVER_ERROR;
    let message = '服务器内部错误';

    if (exception instanceof HttpException) {
      status = exception.getStatus();
      message = exception.message;
    } else if (exception instanceof Error) {
      // 普通 JS Error，如 TypeError、ReferenceError
      message = exception.message;
      // 生产环境不应该暴露内部错误堆栈给客户端
      // 这里可以记录到日志系统
      console.error('未捕获异常:', exception);
    }

    response.status(status).json({
      code: status,
      message,
      timestamp: new Date().toISOString(),
    });
  }
}
```

### 8.6 过滤器的三种作用域

```typescript
// ===== 1. 方法级别：只对这一个路由方法生效 =====
@Controller('users')
export class UsersController {
  @Get()
  @UseFilters(CustomExceptionFilter)  // 只影响 findAll()
  findAll() { /* ... */ }
}

// ===== 2. 控制器级别：对这个 Controller 的所有方法生效 =====
@Controller('users')
@UseFilters(CustomExceptionFilter)    // 影响所有方法
export class UsersController {
  @Get()
  findAll() { /* ... */ }

  @Post()
  create() { /* ... */ }
}

// ===== 3. 全局级别：对所有 Controller 生效 =====
// main.ts
const app = await NestFactory.create(AppModule);
app.useGlobalFilters(new AllExceptionsFilter());
```

**通过 DI 注册全局过滤器**（需要注入依赖时用这种方式）：

```typescript
// app.module.ts
import { Module } from '@nestjs/common';
import { APP_FILTER } from '@nestjs/core';

@Module({
  providers: [
    {
      provide: APP_FILTER,
      useClass: AllExceptionsFilter, // 这样 AllExceptionsFilter 就能注入其他依赖了
    },
  ],
})
export class AppModule {}
```

### 8.7 ArgumentsHost 详解

`ArgumentsHost` 是 NestJS 中横跨不同执行上下文的抽象。当你写一个异常过滤器时，你不仅可能在处理 HTTP 请求，也可能在处理 WebSocket 或 RPC 调用的异常。

```typescript
catch(exception: unknown, host: ArgumentsHost) {
  // 方式 1：switchToHttp() → 获取 HTTP 上下文
  const httpCtx = host.switchToHttp();
  const request = httpCtx.getRequest<Request>();  // 类型安全的 Express Request
  const response = httpCtx.getResponse<Response>();
  const next = httpCtx.getNext<NextFunction>();

  // 方式 2：switchToWs() → 获取 WebSocket 上下文
  // const wsCtx = host.switchToWs();
  // const client = wsCtx.getClient();

  // 方式 3：switchToRpc() → 获取 RPC 上下文
  // const rpcCtx = host.switchToRpc();

  // 方式 4：getArgs() → 获取原始参数数组 [req, res, next]
  const [req, res, nxt] = host.getArgs();
}
```

### 8.8 异常过滤器最佳实践

1. **生产环境不暴露堆栈信息**：`exception.stack` 只写到日志系统，不要返回给前端。
2. **区分开发/生产行为**：开发时返回详细错误便于调试，生产时返回简洁消息。

```typescript
const isProduction = process.env.NODE_ENV === 'production';

response.status(status).json({
  code: status,
  message,
  ...(isProduction ? {} : { stack: exception.stack }), // 开发环境返回堆栈
});
```

3. **多个过滤器叠加**：可以用 `@UseFilters(Filter1, Filter2)` 叠加，从近到远依次执行（类似 try-catch 的嵌套）。
4. **过滤器不吞异常**：如果某个过滤器只捕获特定异常，其他异常会继续向上冒泡（到全局过滤器）。

---

## 9. 管道 Pipe

### 9.1 管道是什么？

**一句话**：管道对 Controller 方法的**参数**做两件事——**转换**（把字符串 "1" 变成数字 1）和**验证**（检查参数是否符合规则，不符合就抛异常）。

**管道在请求生命周期中的位置**：

```text
Guard 通过 → Interceptor(Before) → ④Pipe → Controller 方法被调用
```

管道在 Controller 方法执行**紧前**工作——参数到达方法之前已经完成了转换和验证。

**管道与中间件的区别**：
- 中间件处理**原始请求**（req/res），不知道你具体要哪些参数
- 管道只关心**方法的参数**（@Body、@Query、@Param 等），有明确的类型信息

### 9.2 内置管道一览

| 管道 | 输入 | 输出 | 失败时抛出 |
|------|------|------|---------|
| `ParseIntPipe` | `"42"` | `42` | `BadRequestException` |
| `ParseFloatPipe` | `"3.14"` | `3.14` | `BadRequestException` |
| `ParseBoolPipe` | `"true"` | `true` | `BadRequestException` |
| `ParseArrayPipe` | `"1,2,3"` | `[1, 2, 3]` | `BadRequestException` |
| `ParseUUIDPipe` | `"550e8..."` | 验证通过返回原值 | `BadRequestException` |
| `DefaultValuePipe` | 无参数时 | 返回默认值 | 无 |
| `ValidationPipe` | 任意对象 | 经过 class-validator 验证的对象 | `BadRequestException` |

### 9.3 内置管道的使用方式

**TypeScript：**

```typescript
import { Controller, Get, Post, Param, Query, Body, ParseIntPipe, DefaultValuePipe, ParseUUIDPipe } from '@nestjs/common';

@Controller('orders')
export class OrdersController {

  // ===== ParseIntPipe：路径参数通常默认为字符串，用此管道自动转整数 =====
  // GET /orders/42  → id = 42 (number)
  // GET /orders/abc → 自动返回 400 "Validation failed (numeric string is expected)"
  @Get(':id')
  findOne(@Param('id', ParseIntPipe) id: number): string {
    // id 是真正的 number 类型，typeof id === 'number' → true
    return `订单 #${id}`;
  }

  // ===== 自定义错误状态码和消息 =====
  // 给管道传 options 对象，定制异常消息
  @Get('v2/:id')
  findOneV2(
    @Param('id', new ParseIntPipe({
      errorHttpStatusCode: 422,  // 默认 400，改为 422
      exceptionFactory: (error) => {
        // 完全自定义错误响应
        return new BadRequestException('订单 ID 必须是有效的整数');
      },
    }))
    id: number,
  ): string {
    return `订单 v2 #${id}`;
  }

  // ===== DefaultValuePipe：查询参数未传时使用默认值 =====
  // GET /orders → page=1, limit=10
  // GET /orders?page=2&limit=20 → page=2, limit=20
  @Get()
  findAll(
    @Query('page', new DefaultValuePipe(1), ParseIntPipe) page: number,
    @Query('limit', new DefaultValuePipe(10), ParseIntPipe) limit: number,
  ): string {
    // 管道从左到右执行：
    // ① DefaultValuePipe: 如果 page 未传，赋值为 1
    // ② ParseIntPipe: 把 "1" 转成 number 1
    return `第 ${page} 页，每页 ${limit} 条`;
  }

  // ===== ParseUUIDPipe：验证 v4 UUID 格式 =====
  // GET /orders/uuid/550e8400-e29b-41d4-a716-446655440000 → 通过
  // GET /orders/uuid/not-a-uuid → 自动返回 400
  @Get('uuid/:uuid')
  findByUuid(@Param('uuid', ParseUUIDPipe) uuid: string): string {
    return `UUID: ${uuid}`;
  }

  // ===== ParseArrayPipe：Body 中解析数组 =====
  // POST /orders/batch  Body: { "ids": [1, 2, 3] }
  @Post('batch')
  createBatch(
    @Body('ids', ParseArrayPipe) ids: number[],
  ): string {
    return `批量处理 ${ids.length} 个订单`;
  }
}
```

### 9.4 ValidationPipe 详解（最重要的管道）

ValidationPipe 是最常用的管道，它配合 `class-validator` 和 `class-transformer` 实现**声明式验证**。

**安装**：

```bash
npm i class-validator class-transformer
```

**TypeScript：**

```typescript
// ===== 步骤 1：定义 DTO（Data Transfer Object）=====
// create-user.dto.ts
import {
  IsString, IsEmail, IsInt, Min, Max, IsOptional,
  MinLength, MaxLength, IsNotEmpty, IsEnum,
} from 'class-validator';

export enum UserRole {
  ADMIN = 'admin',
  USER = 'user',
  GUEST = 'guest',
}

export class CreateUserDto {
  @IsString({ message: '用户名必须是字符串' })
  @IsNotEmpty({ message: '用户名不能为空' })
  @MinLength(2, { message: '用户名至少 2 个字符' })
  @MaxLength(50, { message: '用户名最多 50 个字符' })
  username: string;

  @IsEmail({}, { message: '邮箱格式不正确' })
  email: string;

  @IsInt({ message: '年龄必须是整数' })
  @Min(0, { message: '年龄不能小于 0' })
  @Max(150, { message: '年龄不能大于 150' })
  age: number;

  @IsOptional()  // 可选字段
  @IsString()
  @MaxLength(100, { message: '昵称最多 100 字符' })
  nickname?: string;

  @IsEnum(UserRole, { message: '角色必须是 admin/user/guest 之一' })
  role: UserRole = UserRole.USER;  // 默认值
}

// ===== 步骤 2：在 Controller 中使用 =====
// users.controller.ts
import { Controller, Post, Body, UsePipes, ValidationPipe } from '@nestjs/common';
import { CreateUserDto } from './dto/create-user.dto';

@Controller('users')
export class UsersController {

  // 方式 1：方法级别的 ValidationPipe
  @Post()
  @UsePipes(new ValidationPipe({
    whitelist: true,        // 自动剔除 DTO 中未定义的属性
    forbidNonWhitelisted: true, // 遇到未定义属性抛出 400（比 whitelist 更严格）
    transform: true,        // 自动类型转换（query 中的 string → number 等）
  }))
  create(@Body() createUserDto: CreateUserDto): string {
    // createUserDto 已经是 CreateUserDto 类型的实例
    // 如果验证失败，方法体不会执行，自动返回 400
    return `创建用户成功：${createUserDto.username}`;
  }

  // 方式 2：控制器级别的 ValidationPipe
  @Post('batch')
  createBatch(@Body() dtos: CreateUserDto[]): string {
    // dtos 是 CreateUserDto 实例的数组（需要 extra 配置）
    return `批量创建 ${dtos.length} 个用户`;
  }
}
```

### 9.5 ValidationPipe 的配置选项详解

```typescript
new ValidationPipe({
  // ===== 黑白名单 =====
  whitelist: true,
  // 效果：Body: { username: 'john', age: 25, isAdmin: true }
  //       DTO 只定义了 username 和 age
  //       结果：isAdmin 被自动剔除，Controller 中拿到的只有 username 和 age

  forbidNonWhitelisted: true,
  // 效果：和 whitelist 不同，遇到 isAdmin 这种多余字段时直接抛 400 异常
  //       而不是默默剔除——更安全，提醒客户端传错了字段

  // ===== 类型转换 =====
  transform: true,
  // 效果：Query: ?age=25  →  query 参数默认为 string "25"
  //       DTO 中 age 定义为 number
  //       transform: true 自动将 "25" 转为 number 25
  //       省去了手动 ParseIntPipe

  transformOptions: {
    enableImplicitConversion: true,
    // 效果：不需要 @Type(() => Number) 这样的显式声明
    //       根据类型元数据自动转换
    //       注意：只对基本类型有效（string→number→boolean），
    //       嵌套对象、数组等仍需要 @Type(() => NestedClass)
  },

  // ===== 验证行为 =====
  skipMissingProperties: false,
  // true: 跳过未传的字段（只验证传了的字段）
  // false（默认）: 所有字段都验证（包括未传的必填字段会报错）

  skipNullProperties: false,
  // true: 跳过值为 null 的字段

  skipUndefinedProperties: false,
  // true: 跳过值为 undefined 的字段

  // ===== 异常响应 =====
  exceptionFactory: (errors) => {
    // 自定义验证失败的异常格式
    return new BadRequestException({
      code: 400,
      message: '参数验证失败',
      errors: errors.map(err => ({
        field: err.property,
        messages: Object.values(err.constraints || {}),
      })),
    });
  },
})
```

### 9.6 transform 的实际效果演示

```typescript
// 请求: GET /users?page=1&limit=10&isActive=true&tags=a,b,c

// DTO 定义
class QueryDto {
  @IsInt()
  @Min(1)
  page: number;          // "1"   → 1 (number)

  @IsInt()
  @Min(1)
  @Max(100)
  limit: number;         // "10"  → 10 (number)

  @IsBoolean()
  isActive: boolean;     // "true" → true (boolean)

  @IsArray()
  @IsString({ each: true })
  tags: string[];        // "a,b,c" → ["a", "b", "c"] (需要 enableImplicitConversion)

  @Type(() => Date)      // 需要显式 @Type 装饰器（非基本类型）
  @IsDate()
  startDate: Date;       // "2024-01-01" → new Date("2024-01-01")
}

@Get()
findAll(@Query(new ValidationPipe({ transform: true })) query: QueryDto) {
  console.log(typeof query.page);    // "number"
  console.log(typeof query.isActive); // "boolean"
  console.log(Array.isArray(query.tags)); // true
}
```

### 9.7 自定义管道

当你需要做内置管道无法处理的转换时，创建自定义管道：

**TypeScript：**

```typescript
import {
  PipeTransform,
  Injectable,
  ArgumentMetadata,
  BadRequestException,
} from '@nestjs/common';

// 功能：trim + 长度校验
// PipeTransform<T, R> 表示输入类型 T，输出类型 R
@Injectable()
export class TrimAndValidatePipe implements PipeTransform<string, string> {

  constructor(private readonly maxLength: number = 100) {}

  // transform 方法签名：
  // value     —— 参数原始值
  // metadata  —— 参数元信息（类型、数据来源等）
  transform(value: string, metadata: ArgumentMetadata): string {
    // metadata 包含：
    // {
    //   type: 'body' | 'query' | 'param' | 'custom',  ← 数据所在位置
    //   metatype: [Function: String] | undefined,       ← 参数类型（TS 中有效）
    //   data: 'title'                                    ← 参数名称
    // }

    // 类型检查
    if (typeof value !== 'string') {
      throw new BadRequestException(
        `${metadata.data} 必须是字符串类型，实际传入: ${typeof value}`
      );
    }

    // 核心转换
    const trimmed = value.trim();

    // 验证
    if (trimmed.length === 0) {
      throw new BadRequestException(`${metadata.data} 不能为空`);
    }

    if (trimmed.length > this.maxLength) {
      throw new BadRequestException(
        `${metadata.data} 长度不能超过 ${this.maxLength} 字符（当前 ${trimmed.length} 字符）`
      );
    }

    // 返回转换后的值 → 替代 Controller 方法的参数值
    return trimmed;
  }
}

// 使用
@Controller('articles')
class ArticlesController {
  @Post()
  create(
    @Body('title', new TrimAndValidatePipe(50)) title: string,
  ): string {
    // title 已经是 trim 后且验证通过的字符串
    return `创建文章：${title}`;
  }
}
```

### 9.8 全局 ValidationPipe

在 `main.ts` 中全局注册一次，所有 Controller 自动获得验证能力：

```typescript
// TypeScript
import { ValidationPipe } from '@nestjs/common';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      forbidNonWhitelisted: true,
      transform: true,
      transformOptions: {
        enableImplicitConversion: true,
      },
    }),
  );

  await app.listen(3000);
}
bootstrap();
```

### 9.9 常用 class-validator 装饰器速查

| 装饰器 | 作用 | 示例 |
|--------|------|------|
| `@IsString()` | 必须是字符串 | `name: string` |
| `@IsNumber()` | 必须是数字 | `price: number` |
| `@IsInt()` | 必须是整数 | `age: number` |
| `@IsBoolean()` | 必须是布尔值 | `isActive: boolean` |
| `@IsEmail()` | 必须是邮箱格式 | `email: string` |
| `@IsUrl()` | 必须是 URL 格式 | `website: string` |
| `@IsUUID()` | 必须是 UUID | `id: string` |
| `@IsEnum(UserRole)` | 必须是枚举值之一 | `role: UserRole` |
| `@IsArray()` | 必须是数组 | `tags: string[]` |
| `@IsOptional()` | 可选字段（可传可不传） | `nickname?: string` |
| `@IsNotEmpty()` | 不能为 ""、null、undefined | `username: string` |
| `@Min(0) @Max(150)` | 数字最小/大值 | `age: number` |
| `@MinLength(2)` | 字符串最小长度 | `username: string` |
| `@MaxLength(100)` | 字符串最大长度 | `title: string` |
| `@Length(6, 20)` | 字符串长度范围 | `password: string` |
| `@Matches(/regex/)` | 匹配正则表达式 | `phone: string` |
| `@Equals('confirm')` | 等于指定值 | `type: string` |
| `@ValidateNested()` | 嵌套对象也需要验证 | `address: AddressDto` |

---

## 10. 守卫 Guard

### 10.1 守卫是什么？

**一句话**：守卫是"门禁"——它决定一个请求能不能进入 Controller。常用于**认证**（确认你是谁）和**授权**（确认你能做什么）。

**守卫在请求生命周期中的位置**：

```text
Middleware → ②Guard → Interceptor(Before) → Pipe → Controller
```

守卫在**中间件之后、拦截器之前**执行。如果 Guard 返回 `false`，请求到此为止——Pipe 和 Controller 都不会执行。

**Guard 与 Interceptor 的关键区别**：
- Guard：只能返回 `true`（放行）或 `false`（阻止）。不能修改返回值。
- Interceptor：可以访问返回值并修改它，但它不负责"是否允许访问"的判断。

### 10.2 Guard 的核心原理

Guard 实现 `CanActivate` 接口，只有一个方法 `canActivate(context: ExecutionContext)`。

- 返回 `true` → 继续处理请求
- 返回 `false` → 返回 HTTP 403 Forbidden
- 返回 `Promise<boolean>` 或 `Observable<boolean>` → 也可以异步判断

### 10.3 认证守卫

**TypeScript：**

```typescript
import { Injectable, CanActivate, ExecutionContext } from '@nestjs/common';
import { Observable } from 'rxjs';

@Injectable()
export class AuthGuard implements CanActivate {
  canActivate(
    context: ExecutionContext,
  ): boolean | Promise<boolean> | Observable<boolean> {

    // 获取当前请求对象
    const request = context.switchToHttp().getRequest();

    // 从请求头提取 token
    const authHeader = request.headers['authorization'];

    if (!authHeader) {
      console.log('认证失败：缺少 Authorization 头');
      return false; // 返回 403
    }

    // 解析 Bearer token
    const [type, token] = authHeader.split(' ');

    if (type !== 'Bearer' || !token) {
      console.log('认证失败：Token 格式错误');
      return false;
    }

    // 验证 token（实际项目中这里应该用 jwt.verify 或调用认证服务）
    try {
      // 模拟 JWT 解析
      const decodedPayload = this.decodeToken(token);
      if (!decodedPayload) {
        return false;
      }

      // ★ 关键：将解析出的用户信息附加到 request 上
      // 这样后续的 Controller、Service 可以直接用 @CurrentUser() 获取
      request.user = {
        id: decodedPayload.sub,
        username: decodedPayload.username,
        role: decodedPayload.role,
      };

      return true; // 验证通过，放行
    } catch (error) {
      console.log('认证失败：Token 解析异常', error);
      return false;
    }
  }

  private decodeToken(token: string): any | null {
    // 简化示例：实际项目中用 jsonwebtoken 库
    if (token === 'valid-token') {
      return { sub: 1, username: 'john', role: 'admin' };
    }
    return null;
  }
}
```

### 10.4 角色守卫（基于元数据）

Guard 可以通过 `Reflector` 读取路由上通过 `@SetMetadata()` 或自定义装饰器设置的元数据，来实现精细的权限控制。

**TypeScript：**

```typescript
// ===== 步骤 1：创建角色装饰器 =====
import { SetMetadata } from '@nestjs/common';

export const ROLES_KEY = 'roles';
export const Roles = (...roles: string[]) => SetMetadata(ROLES_KEY, roles);
// @Roles('admin') 设置元数据：{ roles: ['admin'] }
// @Roles('admin', 'moderator') 设置元数据：{ roles: ['admin', 'moderator'] }

// ===== 步骤 2：创建角色守卫 =====
import { Injectable, CanActivate, ExecutionContext } from '@nestjs/common';
import { Reflector } from '@nestjs/core';

@Injectable()
export class RolesGuard implements CanActivate {
  constructor(private reflector: Reflector) {}  // 注入 Reflector

  canActivate(context: ExecutionContext): boolean {
    // getAllAndOverride：从"方法"和"控制器类"两个层级查找元数据
    // 方法级别的 @Roles() 会覆盖类级别的
    const requiredRoles = this.reflector.getAllAndOverride<string[]>(ROLES_KEY, [
      context.getHandler(),   // 第一个查找：路由方法上的元数据
      context.getClass(),     // 第二个查找：控制器类上的元数据
    ]);

    // 如果路由没有设置 @Roles()，允许访问
    if (!requiredRoles || requiredRoles.length === 0) {
      return true;
    }

    // 从请求中获取当前用户（由 AuthGuard 提前设置）
    const { user } = context.switchToHttp().getRequest();

    // 检查用户角色是否在所需角色列表中
    return requiredRoles.some((role) => user?.role === role);
    // 如果 requiredRoles = ['admin', 'moderator']，user.role = 'admin' → 通过
    // 如果 requiredRoles = ['admin']，user.role = 'user' → 拒绝
  }
}

// ===== 步骤 3：使用 =====
@Controller('admin')
@Roles('admin')  // 控制器级别：整个控制器都需要 admin 角色
@UseGuards(AuthGuard, RolesGuard)  // AuthGuard 在前（先验证身份），RolesGuard 在后
export class AdminController {

  @Get('dashboard')
  getDashboard(): string {
    return '管理员仪表盘';
  }

  @Post('users')
  @Roles('superadmin')  // 方法级别的角色会覆盖类级别
  // 只有 superadmin 可以删除用户（admin 不行）
  deleteUsers(): string {
    return '删除用户';
  }

  @Get('logs')
  @Roles('admin', 'moderator')  // admin 或 moderator 都可以
  viewLogs(): string {
    return '查看日志';
  }
}
```

### 10.5 ExecutionContext 详解

ExecutionContext 是 ArgumentsHost 的子类，它多了两个方法专门用于 Guard 和 Interceptor：

```typescript
// ArgumentsHost 提供的方法
const ctx = context.switchToHttp();
const request = ctx.getRequest();
const response = ctx.getResponse();

// ExecutionContext 额外提供的方法
context.getClass();      // 返回当前 Controller 类（用于读取类上的元数据）
context.getHandler();   // 返回当前路由处理方法（用于读取方法上的元数据）
```

**`getClass()` vs `getHandler()` 的用处**：用于在 Guard 或 Interceptor 中通过 Reflector 读取元数据。`getHandler()` 返回的是具体的方法引用，`getClass()` 返回的是类引用。

### 10.6 全局守卫的两种注册方式

**方式 1：`useGlobalGuards()` —— 无依赖注入**

```typescript
// main.ts
const app = await NestFactory.create(AppModule);
app.useGlobalGuards(new AuthGuard()); // AuthGuard 不能注入其他依赖
```

**方式 2：通过 `APP_GUARD` Token —— 支持依赖注入（推荐）**

```typescript
// app.module.ts
import { Module } from '@nestjs/common';
import { APP_GUARD } from '@nestjs/core';

@Module({
  providers: [
    {
      provide: APP_GUARD,
      useClass: AuthGuard, // AuthGuard 可以构造函数注入其他 Service
    },
  ],
})
export class AppModule {}
```

### 10.7 Guard 返回 403 时自定义响应

默认返回 `false` 时，NestJS 返回的 403 消息是 `"Forbidden resource"`。如果你需要自定义消息，抛出异常而不是返回 false：

```typescript
@Injectable()
export class RoleGuard implements CanActivate {
  canActivate(context: ExecutionContext): boolean {
    const { user } = context.switchToHttp().getRequest();

    if (!user) {
      // 未登录 → 401
      throw new UnauthorizedException('请先登录');
    }

    if (user.role !== 'admin') {
      // 已登录但无权限 → 403
      throw new ForbiddenException('无管理员权限，当前角色: ' + user.role);
    }

    return true;
  }
}
```

这样你的异常过滤器就能统一处理这种 403 的响应格式。

---

## 11. 拦截器 Interceptor

### 11.1 拦截器是什么？

**一句话**：拦截器可以在 Controller 方法执行**之前**和**之后**插入逻辑，能够获取和修改方法的返回值，还能捕获方法内部抛出的异常。

**拦截器在请求生命周期中的位置（两个阶段）**：

```text
Guard → ③Interceptor(Before) → Pipe → Controller/Service
→ ⑦Interceptor(After) → ExceptionFilter → Response
```

拦截器是**唯一的**既能访问请求参数、又能访问返回值的处理层。正是这个特性，让它成为"统一包装响应格式"的最佳选择。

### 11.2 拦截器的核心原理：RxJS Observable

NestJS 的拦截器基于 **RxJS**。Controller 方法返回的值，会被 NestJS 包装成一个 Observable 流。拦截器的 `intercept()` 方法拿到这个流后，可以通过 RxJS 操作符对结果做转换。

```typescript
intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
  // context: 当前执行上下文（和 Guard 中的一样）
  // next.handle(): 调用下一个处理环节（可能是另一个拦截器或控制器方法）
  //               返回 Observable —— 它会发出控制器的返回值

  return next.handle().pipe(
    // 使用 RxJS 操作符处理返回值
    map(data => transformedData),       // 转换数据
    tap(data => sideEffect()),          // 副作用（日志等）
    catchError(error => handle(error)), // 捕获异常
  );
}
```

**常用 RxJS 操作符**：

| 操作符 | 作用 |
|--------|------|
| `map(fn)` | 转换数据（类似 Array.map） |
| `tap(fn)` | 执行副作用（不影响数据流，类似 forEach） |
| `catchError(fn)` | 捕获流中的错误 |
| `timeout(n)` | 超时抛出错误 |
| `retry(n)` | 失败后重试 n 次 |

### 11.3 基础示例：日志拦截器

**TypeScript：**

```typescript
import {
  Injectable,
  NestInterceptor,
  ExecutionContext,
  CallHandler,
} from '@nestjs/common';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';

@Injectable()
export class LoggingInterceptor implements NestInterceptor {
  intercept(
    context: ExecutionContext,
    next: CallHandler,
  ): Observable<any> {
    const request = context.switchToHttp().getRequest();
    const { method, url } = request;
    const now = Date.now();

    console.log(`[拦截器-前置] ${method} ${url} - 开始处理`);

    return next.handle().pipe(
      tap((data) => {
        // data 是 Controller 方法的返回值
        const responseTime = Date.now() - now;
        console.log(`[拦截器-后置] ${method} ${url} - 耗时 ${responseTime}ms`);
        // tap 不影响数据流，返回值原样传递给客户端
      }),
    );
  }
}
```

### 11.4 最重要的用法：响应格式统一包装

**TypeScript：**

```typescript
import {
  Injectable,
  NestInterceptor,
  ExecutionContext,
  CallHandler,
} from '@nestjs/common';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

export interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
  timestamp: string;
}

@Injectable()
export class TransformInterceptor<T>
  implements NestInterceptor<T, ApiResponse<T>>
{
  intercept(
    context: ExecutionContext,
    next: CallHandler,
  ): Observable<ApiResponse<T>> {
    return next.handle().pipe(
      map((data) => ({
        // map 会转换每个从 Controller 返回的值
        code: 200,
        message: 'success',
        data,                           // 原始的 Controller 返回值放在 data 中
        timestamp: new Date().toISOString(),
      })),
    );
  }
}

// 效果：
// Controller return { name: 'John' }
// → 客户端收到 { "code": 200, "message": "success", "data": { "name": "John" }, "timestamp": "..." }
```

### 11.5 进阶：异常映射拦截器

```typescript
import {
  Injectable,
  NestInterceptor,
  ExecutionContext,
  CallHandler,
  HttpException,
} from '@nestjs/common';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

@Injectable()
export class ErrorMappingInterceptor implements NestInterceptor {
  intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
    return next.handle().pipe(
      catchError((error) => {
        // 将业务错误码映射为 HTTP 异常
        if (error.code === 'USER_NOT_FOUND') {
          return throwError(() => new HttpException(
            { code: 404, message: '用户不存在', originalCode: error.code },
            404,
          ));
        }
        if (error.code === 'INSUFFICIENT_BALANCE') {
          return throwError(() => new HttpException(
            { code: 400, message: '余额不足', originalCode: error.code },
            400,
          ));
        }
        // 未匹配到的错误继续抛出，由异常过滤器处理
        return throwError(() => error);
      }),
    );
  }
}
```

### 11.6 多个拦截器的执行顺序

NestJS 中的多个拦截器像"洋葱"一样一层层包裹——先从外到内执行前置逻辑，再从内到外执行后置逻辑：

```typescript
@UseInterceptors(InterceptorA, InterceptorB) // A 在外面，B 在里面
getData() { return 'data'; }

// 执行顺序：
// InterceptorA → 前置逻辑
//   InterceptorB → 前置逻辑
//     Controller 方法执行
//   InterceptorB → 后置逻辑（通过 pipe 操作符）
// InterceptorA → 后置逻辑
```

**图示**：

```text
  InterceptorA 前置
      │
      ▼
  InterceptorB 前置
      │
      ▼
  Controller 方法
      │
      ▼
  InterceptorB 后置 (map/tap)
      │
      ▼
  InterceptorA 后置 (map/tap)
      │
      ▼
  最终响应返回客户端
```

### 11.7 全局拦截器

```typescript
// main.ts
const app = await NestFactory.create(AppModule);
app.useGlobalInterceptors(new TransformInterceptor());

// 或通过依赖注入（推荐）
@Module({
  providers: [
    {
      provide: APP_INTERCEPTOR,
      useClass: TransformInterceptor,
    },
  ],
})
export class AppModule {}
```

---

## 12. 自定义装饰器

### 12.1 为什么需要自定义装饰器？

NestJS 的内置参数装饰器（`@Body()`、`@Param()`、`@Query()` 等）能满足大部分需求，但当你需要从请求中提取**应用级信息**时，自定义装饰器更优雅：

- 获取当前用户 → `@CurrentUser()` 比 `@Req() req` 然后手动 `req.user` 更清晰
- 获取权限列表 → `@Permissions()` 直接在参数中拿到权限数组

### 12.2 `createParamDecorator` 深入解析

**函数签名**：

```typescript
createParamDecorator(
  (data: unknown, ctx: ExecutionContext) => {
    // data: 装饰器中传入的参数，如 @CurrentUser('id') 中的 'id'
    // ctx:  当前执行上下文（可以用 ctx.switchToHttp().getRequest() 获取请求）
    return /* 你想要注入到方法参数中的值 */;
  },
  // 可选：附加配置
  [ enhancers ]
);
```

**TypeScript：**

```typescript
// user.decorator.ts
import { createParamDecorator, ExecutionContext } from '@nestjs/common';

export const CurrentUser = createParamDecorator(
  (data: string | undefined, ctx: ExecutionContext) => {
    const request = ctx.switchToHttp().getRequest();
    const user = request.user;

    // 如果传入 data 参数 → 只提取特定字段
    // @CurrentUser('id')   → 返回 user.id
    // @CurrentUser('role') → 返回 user.role
    // 如果没传 data → 返回整个 user 对象
    return data ? user?.[data] : user;
  },
);

// ===== 使用 =====
@Controller('profile')
export class ProfileController {

  @Get()
  getProfile(@CurrentUser() user: any): string {
    // user = { id: 1, username: 'john', role: 'admin', email: 'john@example.com' }
    return `当前用户：${user.username}`;
  }

  @Get('role')
  getRole(@CurrentUser('role') role: string): string {
    // role = 'admin'
    return `用户角色：${role}`;
  }

  @Get('id')
  getId(@CurrentUser('id') id: number): number {
    // id = 1
    return id;
  }
}
```

### 12.3 applyDecorators —— 合并多个装饰器

当你需要在多个路由上都写同样的组合（如 `@UseGuards(AuthGuard) + @UseGuards(RolesGuard) + @SetMetadata('roles', ['admin'])`），合并装饰器可以减少重复：

**TypeScript：**

```typescript
// auth.decorator.ts
import { applyDecorators, SetMetadata, UseGuards } from '@nestjs/common';
import { AuthGuard } from '../guards/auth.guard';
import { RolesGuard } from '../guards/roles.guard';

// 一个装饰器 = 三个装饰器的组合
export function Auth(...roles: string[]) {
  return applyDecorators(
    // applyDecorators 将其中的装饰器按顺序应用到目标上
    SetMetadata('roles', roles),
    UseGuards(AuthGuard, RolesGuard),
  );
}

// ===== 使用：一行代替三行 =====
@Controller('admin')
export class AdminController {

  // 之前：
  // @SetMetadata('roles', ['admin'])
  // @UseGuards(AuthGuard)
  // @UseGuards(RolesGuard)

  // 现在：
  @Auth('admin')
  @Get('dashboard')
  getDashboard(): string {
    return '管理员仪表盘';
  }

  @Auth('admin', 'superadmin')
  @Post('users')
  manageUsers(): string {
    return '管理用户';
  }
}
```

**合并装饰器时的注意事项**：
- 装饰器从**下往上**执行（下面的先执行），`applyDecorators` 中的顺序即为执行顺序
- 合并装饰器可以包含任何 NestJS 装饰器：`@UseGuards`、`@UseInterceptors`、`@UsePipes`、`@UseFilters`、`@SetMetadata`、`@HttpCode` 等

### 12.4 更复杂的自定义参数装饰器

当你需要从多个地方提取信息时：

```typescript
// request-context.decorator.ts
import { createParamDecorator, ExecutionContext } from '@nestjs/common';

export interface RequestContext {
  user: { id: number; username: string; role: string };
  ip: string;
  userAgent: string;
  requestId: string;
}

export const RequestCtx = createParamDecorator(
  (data: unknown, ctx: ExecutionContext): RequestContext => {
    const request = ctx.switchToHttp().getRequest();

    return {
      user: request.user,
      ip: request.ip,
      userAgent: request.headers['user-agent'] || 'unknown',
      requestId: request.headers['x-request-id'] || '-',
    };
  },
);

// 使用：一次性拿到请求的完整上下文
@Get('info')
getInfo(@RequestCtx() ctx: RequestContext): object {
  return {
    message: `你好 ${ctx.user.username}，来自 ${ctx.ip}`,
    requestId: ctx.requestId,
  };
}
```

---

（未完，接第三部分）

---

## 13. 数据库集成 TypeORM

### 13.1 TypeORM 与 NestJS 的关系

NestJS 通过 `@nestjs/typeorm` 包将 TypeORM 深度集成进来，提供：
- `TypeOrmModule.forRoot()` —— 配置全局数据库连接
- `TypeOrmModule.forFeature([Entity])` —— 在指定模块中注册实体并自动生成 Repository
- `@InjectRepository(Entity)` —— 自动注入该实体的 Repository

### 13.2 安装

```bash
npm i @nestjs/typeorm typeorm mysql2  # MySQL
# 或
npm i @nestjs/typeorm typeorm pg      # PostgreSQL
```

### 13.3 配置数据库连接

**`forRoot` 做了什么**：在底层创建 TypeORM 的 `DataSource`，建立数据库连接池，并扫描 entities 路径加载所有实体类。

```typescript
// app.module.ts
import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';

@Module({
  imports: [
    TypeOrmModule.forRoot({
      type: 'mysql',
      host: 'localhost',
      port: 3306,
      username: 'root',
      password: 'password',
      database: 'nest_demo',

      // entities：告诉 TypeORM 哪些文件是实体类
      // __dirname 指当前文件所在目录，glob 模式匹配所有 .entity.ts 文件
      entities: [__dirname + '/**/*.entity{.ts,.js}'],

      // synchronize：自动根据实体类同步数据库表结构
      // ⚠️ 开发环境可以开，生产环境必须关闭（用 migration 替代）
      synchronize: true,

      // 连接池配置
      extra: {
        connectionLimit: 10,       // 最大连接数
        connectTimeout: 10000,     // 连接超时 10 秒
        acquireTimeout: 10000,     // 获取连接超时
      },

      logging: true,               // 输出 SQL 日志
      timezone: '+08:00',          // 设置时区
    }),
  ],
})
export class AppModule {}
```

**synchronize vs migration**：

| 方式 | 适用场景 | 风险 |
|------|---------|------|
| `synchronize: true` | 本地开发 | 可能误删生产数据 |
| migration | 生产环境 | 需要手动编写迁移脚本 |

synchronize 根据实体定义自动 `ALTER TABLE`，但**不会识别列重命名**（当作删除旧列 + 增加新列，数据丢失）。

### 13.4 定义实体 Entity

```typescript
// user.entity.ts
import {
  Entity,
  Column,
  PrimaryGeneratedColumn,
  CreateDateColumn,
  UpdateDateColumn,
  DeleteDateColumn,
} from 'typeorm';

@Entity('users')  // 映射到数据库 users 表
export class User {
  @PrimaryGeneratedColumn()     // 自增主键
  id: number;

  @Column({
    type: 'varchar',
    length: 50,
    unique: true,               // 唯一索引
    comment: '用户名',
  })
  username: string;

  @Column({
    type: 'varchar',
    length: 100,
    comment: '邮箱',
  })
  email: string;

  @Column({
    type: 'varchar',
    select: false,              // 默认查询不返回此字段（安全）
    comment: '密码哈希',
  })
  password: string;

  @Column({
    type: 'varchar',
    length: 20,
    default: 'user',
    comment: '用户角色',
  })
  role: string;

  @Column({
    type: 'tinyint',
    default: 1,
    comment: '状态：1=启用 0=禁用',
  })
  status: number;

  @CreateDateColumn({ comment: '创建时间' })
  createdAt: Date;

  @UpdateDateColumn({ comment: '更新时间' })
  updatedAt: Date;

  @DeleteDateColumn({ comment: '软删除时间' })
  deletedAt: Date | null;  // null = 未删除，非 null = 已软删除
}
```

**`@Column` 中 `select: false` 的效果**：
- 使用 `find()` 查询时，password 字段**不会**出现在结果中
- 需要密码时，必须显式调用 `findOne({ select: ['password'], where: { id } })` 或使用 `createQueryBuilder().addSelect('user.password')`

### 13.5 Repository 模式完整使用

```typescript
// user.module.ts
import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { User } from './entities/user.entity';
import { UserService } from './user.service';
import { UserController } from './user.controller';

@Module({
  imports: [TypeOrmModule.forFeature([User])], // ← 注册实体，自动生成 Repository
  controllers: [UserController],
  providers: [UserService],
  exports: [UserService],
})
export class UserModule {}
```

```typescript
// user.service.ts —— 完整 CRUD
import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository, Like, Between, In, MoreThan } from 'typeorm';
import { User } from './entities/user.entity';

@Injectable()
export class UserService {
  constructor(
    @InjectRepository(User)
    private readonly userRepo: Repository<User>,
  ) {}

  // ========== 创建 ==========

  // 单条创建
  async create(dto: Partial<User>): Promise<User> {
    // create() 创建实体实例（不立即入库）
    const user = this.userRepo.create(dto);
    // save() 真正写入数据库（INSERT）
    return this.userRepo.save(user);
  }

  // 批量创建 —— 一条 INSERT INTO ... VALUES (...), (...), (...)
  async batchCreate(dtos: Partial<User>[]): Promise<User[]> {
    const users = this.userRepo.create(dtos);
    return this.userRepo.save(users);
  }

  // ========== 查询 ==========

  // 分页查询
  async findPaginated(page: number = 1, limit: number = 10) {
    // findAndCount 返回 [数据数组, 总数]
    const [list, total] = await this.userRepo.findAndCount({
      skip: (page - 1) * limit,    // 跳过前 N 条
      take: limit,                  // 只取 N 条
      order: { createdAt: 'DESC' }, // 按创建时间倒序
      where: { status: 1 },         // 只查启用状态的用户
    });
    return { list, total, page, limit };
  }

  // 查找单个
  async findById(id: number): Promise<User> {
    const user = await this.userRepo.findOne({
      where: { id },
      // 如需显式包含 select: false 的字段：
      // select: ['id', 'username', 'email', 'password'],
    });
    if (!user) {
      throw new NotFoundException(`用户 #${id} 不存在`);
    }
    return user;
  }

  // 多条件查询
  async search(conditions: {
    keyword?: string;
    role?: string;
    status?: number;
    startDate?: string;
    endDate?: string;
  }) {
    const where: any = {};

    if (conditions.role) {
      where.role = conditions.role;
    }

    if (conditions.status !== undefined) {
      where.status = conditions.status;
    }

    // find 支持数组条件
    const users = await this.userRepo.find({
      where: [
        { username: Like(`%${conditions.keyword}%`), ...where },
        { email: Like(`%${conditions.keyword}%`), ...where },
      ],
      // 上面两个对象的 OR 关系：username LIKE '%kw%' OR email LIKE '%kw%'
    });

    return users;
  }

  // ========== 更新 ==========

  async update(id: number, dto: Partial<User>): Promise<void> {
    // update 方法不检查实体是否存在
    const result = await this.userRepo.update(id, dto);
    if (result.affected === 0) {
      throw new NotFoundException(`用户 #${id} 不存在`);
    }
  }

  // ========== 删除 ==========

  // 硬删除（物理删除）
  async remove(id: number): Promise<void> {
    const result = await this.userRepo.delete(id);
    if (result.affected === 0) {
      throw new NotFoundException(`用户 #${id} 不存在`);
    }
  }

  // 软删除（逻辑删除，需要实体有 @DeleteDateColumn）
  async softDelete(id: number): Promise<void> {
    await this.userRepo.softDelete(id);
    // 效果：设置 deletedAt = NOW()，后续 find 自动过滤
  }

  // 查询包含已软删除的记录
  async findWithDeleted(): Promise<User[]> {
    return this.userRepo.find({ withDeleted: true });
  }

  // 恢复软删除
  async restore(id: number): Promise<void> {
    await this.userRepo.restore(id);
    // 效果：deletedAt = NULL
  }

  // ========== 聚合查询 ==========

  async getStats() {
    return {
      total: await this.userRepo.count(),
      active: await this.userRepo.count({ where: { status: 1 } }),
      byRole: await this.userRepo
        .createQueryBuilder('user')
        .select('user.role', 'role')
        .addSelect('COUNT(*)', 'count')
        .groupBy('user.role')
        .getRawMany(),
    };
  }
}
```

### 13.6 QueryBuilder —— 复杂查询利器

当 `find()` 不够灵活时（多表 JOIN、子查询、复杂 WHERE 组合），使用 QueryBuilder：

```typescript
async advancedSearch(options: {
  keyword?: string;
  role?: string;
  minAge?: number;
  maxAge?: number;
  orderBy?: string;
  orderDir?: 'ASC' | 'DESC';
  page?: number;
  limit?: number;
}) {
  const qb = this.userRepo.createQueryBuilder('user');
  // 'user' 是别名，后续所有列引用都以 user. 开头

  // 动态条件
  if (options.keyword) {
    qb.andWhere(
      '(user.username LIKE :kw OR user.email LIKE :kw)',
      { kw: `%${options.keyword}%` },
    );
  }

  if (options.role) {
    qb.andWhere('user.role = :role', { role: options.role });
  }

  if (options.minAge !== undefined) {
    qb.andWhere('user.age >= :minAge', { minAge: options.minAge });
  }

  if (options.maxAge !== undefined) {
    qb.andWhere('user.age <= :maxAge', { maxAge: options.maxAge });
  }

  // 排序（参数化防止 SQL 注入）
  const allowedColumns = ['username', 'email', 'createdAt', 'age'];
  if (options.orderBy && allowedColumns.includes(options.orderBy)) {
    qb.orderBy(`user.${options.orderBy}`, options.orderDir || 'DESC');
  }

  // 分页
  const page = options.page || 1;
  const limit = options.limit || 10;
  qb.skip((page - 1) * limit).take(limit);

  // 获取结果
  const [list, total] = await qb.getManyAndCount();
  return { list, total, page, limit };
}
```

**QueryBuilder 常用方法速查**：

| 方法 | 作用 | SQL 等价 |
|------|------|----------|
| `.select('user.name')` | 选择列 | `SELECT user.name` |
| `.addSelect('SUM(amount)', 'total')` | 添加聚合列 | `SELECT ..., SUM(amount) AS total` |
| `.leftJoin('user.posts', 'post')` | 左连接 | `LEFT JOIN post ON ...` |
| `.innerJoin('user.role', 'role')` | 内连接 | `INNER JOIN role ON ...` |
| `.where('user.id = :id', { id })` | WHERE 条件 | `WHERE user.id = ?` |
| `.andWhere(...)` | AND 条件 | `AND ...` |
| `.orWhere(...)` | OR 条件 | `OR ...` |
| `.orderBy('user.name', 'ASC')` | 排序 | `ORDER BY user.name ASC` |
| `.groupBy('user.role')` | 分组 | `GROUP BY user.role` |
| `.having('COUNT(*) > :min', { min: 5 })` | HAVING | `HAVING COUNT(*) > 5` |
| `.skip(10).take(10)` | 分页 | `LIMIT 10 OFFSET 10` |
| `.getMany()` | 获取多条 | 返回实体数组 |
| `.getOne()` | 获取单条 | 返回单个实体或 null |
| `.getManyAndCount()` | 获取多条+总数 | 返回 `[entities, count]` |
| `.getRawMany()` | 获取原始数据 | 返回普通对象数组（非实体） |
| `.execute()` | 执行 INSERT/UPDATE/DELETE | 返回 `{ affected, raw }` |

### 13.7 关联关系

```typescript
// ===== 一对多 / 多对一 =====
// user.entity.ts
@Entity('users')
export class User {
  @PrimaryGeneratedColumn()
  id: number;

  @OneToMany(() => Article, (article) => article.author)
  articles: Article[];  // 一个用户有多篇文章
}

// article.entity.ts
@Entity('articles')
export class Article {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  title: string;

  @ManyToOne(() => User, (user) => user.articles, {
    onDelete: 'CASCADE',  // 删除用户时级联删除其文章
  })
  @JoinColumn({ name: 'authorId' })  // 外键列名
  author: User;

  @Column()
  authorId: number;  // 外键
}

// ===== 多对多 =====
// article.entity.ts
@Entity('articles')
export class Article {
  @PrimaryGeneratedColumn()
  id: number;

  @ManyToMany(() => Tag, (tag) => tag.articles)
  @JoinTable({  // 只有一方需要 @JoinTable
    name: 'article_tags',
    joinColumn: { name: 'articleId', referencedColumnName: 'id' },
    inverseJoinColumn: { name: 'tagId', referencedColumnName: 'id' },
  })
  tags: Tag[];
}

// tag.entity.ts
@Entity('tags')
export class Tag {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ unique: true })
  name: string;

  @ManyToMany(() => Article, (article) => article.tags)
  articles: Article[];
}

// ===== 一对一 =====
@Entity('profiles')
export class Profile {
  @PrimaryGeneratedColumn()
  id: number;

  @OneToOne(() => User (user) => user.profile)
  @JoinColumn()
  user: User;

  @Column()
  bio: string;
}
```

**加载关联数据的三种方式**：

```typescript
// 方式 1：relations 选项（大多数情况够用）
const users = await userRepo.find({
  relations: ['articles', 'profile'],  // 同时加载文章和个人资料
});

// 方式 2：QueryBuilder leftJoinAndSelect
const users = await userRepo
  .createQueryBuilder('user')
  .leftJoinAndSelect('user.articles', 'article')  // 左连接并 SELECT
  .leftJoinAndSelect('user.profile', 'profile')
  .getMany();

// 方式 3：eager loading（在实体中设置，不推荐大量使用）
@OneToMany(() => Article, (article) => article.author, { eager: true })
articles: Article[];
// eager: true → 每次查询 User 时自动 JOIN articles
// 注意：如果实体有多处 eager 关联，每次查询都会执行多个 JOIN，严重影响性能
```

**relations 陷阱**：如果用 `find({ relations: ['articles', 'profile'] })`，TypeORM 会发出 3 条 SQL（1 条查 User + 1 条查 Article + 1 条查 Profile）。在循环中批量查询会导致 N+1 问题——应该用 QueryBuilder 的 `leftJoinAndSelect` 来一次 JOIN。

---

## 14. 配置管理

### 14.1 为什么需要专门的配置管理？

硬编码的环境变量存在几个问题：
- 散落在各个文件中，不知道一共有哪些配置项
- 缺少验证——配置缺失或格式错误只在运行时才发现
- 没有类型提示——`process.env.PORT` 永远是 `string | undefined`

`@nestjs/config` 解决了这些问题：集中管理、类型推断、验证、命名空间分组。

### 14.2 安装与基础使用

```bash
npm i @nestjs/config
```

**.env 文件**：

```env
# 服务端口
PORT=3000

# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USERNAME=root
DB_PASSWORD=secret
DB_DATABASE=nest_demo

# JWT 配置
JWT_SECRET=my-256-bit-secret-key
JWT_EXPIRES_IN=7d
```

```typescript
// app.module.ts
import { Module } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { TypeOrmModule } from '@nestjs/typeorm';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,           // 设为全局模块，其他模块无需 imports
      envFilePath: '.env',      // 指定 .env 文件路径
      ignoreEnvFile: false,     // 生产环境可让外部注入系统环境变量
    }),
  ],
})
export class AppModule {}
```

### 14.3 在 Service 中使用 ConfigService

```typescript
import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';

@Injectable()
export class JwtService {
  private readonly secret: string;
  private readonly expiresIn: string;

  constructor(private configService: ConfigService) {
    // get 方法支持泛型、路径深度取值、默认值
    this.secret = this.configService.get<string>('JWT_SECRET');
    this.expiresIn = this.configService.get<string>('JWT_EXPIRES_IN', '1d');
    // 第二个参数：当环境变量不存在时的默认值
  }

  sign(payload: object): string {
    // jwt.sign(payload, this.secret, { expiresIn: this.expiresIn })
    return `signed-token-with-${this.secret}`;
  }
}
```

### 14.4 命名空间配置（registerAs）

对于大型项目，按功能拆分配置（database、jwt、cache 等）：

```typescript
// config/database.config.ts
import { registerAs } from '@nestjs/config';

export default registerAs('database', () => ({
  host: process.env.DB_HOST || 'localhost',
  port: parseInt(process.env.DB_PORT, 10) || 3306,
  username: process.env.DB_USERNAME,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_DATABASE,
  poolMin: 2,
  poolMax: 10,
}));

// config/jwt.config.ts
import { registerAs } from '@nestjs/config';

export default registerAs('jwt', () => ({
  secret: process.env.JWT_SECRET,
  expiresIn: process.env.JWT_EXPIRES_IN || '7d',
  refreshSecret: process.env.JWT_REFRESH_SECRET,
  refreshExpiresIn: process.env.JWT_REFRESH_EXPIRES_IN || '30d',
}));
```

```typescript
// app.module.ts —— 加载所有配置命名空间
import databaseConfig from './config/database.config';
import jwtConfig from './config/jwt.config';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      load: [databaseConfig, jwtConfig],  // ← 加载配置工厂函数
    }),

    // 使用命名空间配置数据库
    TypeOrmModule.forRootAsync({
      inject: [ConfigService],
      useFactory: (config: ConfigService) => ({
        type: 'mysql',
        host: config.get('database.host'),      // 用点号访问命名空间
        port: config.get('database.port'),
        username: config.get('database.username'),
        password: config.get('database.password'),
        database: config.get('database.database'),
      }),
    }),
  ],
})
export class AppModule {}
```

```typescript
// 在任何 Service 中使用命名空间配置
@Injectable()
class AuthService {
  constructor(private config: ConfigService) {}

  generateToken() {
    const secret = this.config.get<string>('jwt.secret');       // 用 "命名空间.key" 访问
    const expiresIn = this.config.get<string>('jwt.expiresIn');
    // ...
  }
}
```

### 14.5 配置验证（防止启动后才报错）

用 Joi 在应用启动时验证配置完整性：

```bash
npm i joi
```

```typescript
import * as Joi from 'joi';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      validationSchema: Joi.object({
        NODE_ENV: Joi.string()
          .valid('development', 'production', 'staging')
          .default('development'),
        PORT: Joi.number().default(3000),
        DB_HOST: Joi.string().required(),
        DB_PORT: Joi.number().required(),
        DB_USERNAME: Joi.string().required(),
        DB_PASSWORD: Joi.string().required(),
        DB_DATABASE: Joi.string().required(),
        JWT_SECRET: Joi.string().min(32).required(),
      }),
      validationOptions: {
        allowUnknown: true,       // 允许 .env 中有未定义的额外变量
        abortEarly: true,         // 遇到第一个错误就停止
      },
    }),
  ],
})
export class AppModule {}
```

**效果**：如果 `.env` 缺少 `JWT_SECRET`，应用启动时会直接抛出详细错误，而不是在运行到一半时崩掉。

### 14.6 多环境配置

```text
.env                   # 默认配置（跨环境共享）
.env.development       # 开发环境覆盖（本地数据库）
.env.staging           # 预发布环境覆盖
.env.production        # 生产环境覆盖（系统环境变量，不提交到 Git）
```

```typescript
ConfigModule.forRoot({
  isGlobal: true,
  // 根据 NODE_ENV 加载对应文件
  // envFilePath 是数组时，前面的优先级高
  envFilePath: [
    `.env.${process.env.NODE_ENV || 'development'}`,  // .env.production
    '.env',                                             // 默认回退
  ],
});
```

---

## 15. 文件上传

### 15.1 文件上传原理

NestJS 使用 `multer`（Express 的文件上传中间件）处理 `multipart/form-data` 格式的文件。`@nestjs/platform-express` 提供了 `FileInterceptor`（单文件）和 `FilesInterceptor`（多文件）。

**安装**（TS 需要类型定义）：

```bash
npm i -D @types/multer
```

### 15.2 单文件上传

```typescript
import {
  Controller, Post, UploadedFile, UseInterceptors,
  BadRequestException, PayloadTooLargeException,
} from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import { diskStorage } from 'multer';
import { extname, join } from 'path';

@Controller('upload')
export class UploadController {

  @Post('single')
  @UseInterceptors(
    FileInterceptor('file', {  // 'file' = form-data 的字段名
      // === 存储方式 ===
      storage: diskStorage({
        destination: './uploads',  // 文件保存目录
        filename: (req, file, callback) => {
          // 自定义文件名：时间戳 + 随机数 + 原始扩展名
          const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1e9);
          const ext = extname(file.originalname);  // 提取扩展名 .jpg
          callback(null, `${uniqueSuffix}${ext}`);
        },
      }),

      // === 文件大小限制 ===
      limits: {
        fileSize: 5 * 1024 * 1024,  // 5MB
        // 超出时 multer 抛出 MulterError('LIMIT_FILE_SIZE')
        // 可配合异常过滤器捕获并转换为友好的中文错误
      },

      // === 文件类型过滤 ===
      fileFilter: (req, file, callback) => {
        // 通过 MIME 类型过滤
        const allowedMimes = [
          'image/jpeg',
          'image/png',
          'image/gif',
          'image/webp',
        ];

        if (!allowedMimes.includes(file.mimetype)) {
          // 第一个参数传 Error → 拒绝上传
          // 第二个参数 false → 不保存文件
          return callback(
            new BadRequestException(
              `不允许的文件类型: ${file.mimetype}，仅支持 JPG/PNG/GIF/WEBP`
            ),
            false,
          );
        }

        callback(null, true);  // 接受文件
      },
    }),
  )
  uploadSingle(@UploadedFile() file: Express.Multer.File) {
    // Express.Multer.File 包含：
    // fieldname: 'file'         ← form-data 字段名
    // originalname: 'photo.jpg' ← 客户端原始文件名
    // encoding: '7bit'
    // mimetype: 'image/jpeg'
    // destination: './uploads'
    // filename: '1704067200000-123456789.jpg' ← 保存到磁盘的文件名
    // path: 'uploads/1704067200000-123456789.jpg'
    // size: 245760               ← 文件大小（字节）

    return {
      message: '上传成功',
      filename: file.filename,
      originalname: file.originalname,
      size: file.size,
      url: `/uploads/${file.filename}`,  // 返回可访问的 URL
    };
  }
}
```

### 15.3 多文件上传

```typescript
import { FilesInterceptor, FileFieldsInterceptor } from '@nestjs/platform-express';

@Controller('upload')
export class UploadController {

  // 方式 1：同一个字段名上传多个文件
  // POST /upload/multiple   form-data: photos[] → 多个文件
  @Post('multiple')
  @UseInterceptors(FilesInterceptor('photos', 10))  // 最多 10 个
  uploadMultiple(@UploadedFiles() files: Express.Multer.File[]) {
    const fileList = files.map(f => ({
      originalname: f.originalname,
      filename: f.filename,
      size: f.size,
    }));
    return {
      message: `成功上传 ${files.length} 个文件`,
      files: fileList,
    };
  }

  // 方式 2：不同字段名上传不同类型文件
  // POST /upload/profile  form-data: avatar=文件1, gallery=文件2,文件3
  @Post('profile')
  @UseInterceptors(
    FileFieldsInterceptor([
      { name: 'avatar', maxCount: 1 },    // 头像最多 1 张
      { name: 'gallery', maxCount: 5 },    // 相册最多 5 张
    ]),
  )
  uploadProfile(
    @UploadedFiles()
    files: {
      avatar?: Express.Multer.File[];
      gallery?: Express.Multer.File[];
    },
  ) {
    return {
      avatar: files.avatar?.[0]?.filename,
      galleryCount: files.gallery?.length || 0,
    };
  }
}
```

### 15.4 内存存储（上传到云存储）

当需要上传到 COS/OSS/S3 而非本地磁盘时，使用 `memoryStorage`：

```typescript
import { memoryStorage } from 'multer';

@Post('cloud')
@UseInterceptors(
  FileInterceptor('file', {
    storage: memoryStorage(),  // 文件存在 Buffer 中，不写入磁盘
    limits: { fileSize: 10 * 1024 * 1024 }, // 10MB
  }),
)
async uploadToCloud(@UploadedFile() file: Express.Multer.File) {
  // file.buffer 是文件的二进制内容
  const buffer = file.buffer;

  // 上传到腾讯云 COS
  // const result = await cosClient.putObject({
  //   Bucket: 'my-bucket',
  //   Region: 'ap-guangzhou',
  //   Key: `uploads/${Date.now()}-${file.originalname}`,
  //   Body: buffer,
  // });

  return {
    message: '上传到云存储成功',
    originalname: file.originalname,
    size: file.size,
  };
}
```

---

## 16. 任务调度

### 16.1 什么是任务调度？

很多场景需要定时执行任务：每天凌晨清理过期数据、每 30 分钟同步一次外部数据、每小时发送一封汇总邮件。

NestJS 通过 `@nestjs/schedule` 提供三种定时方式：
- **Cron**：基于 Cron 表达式，在指定时间点执行
- **Interval**：固定间隔重复执行
- **Timeout**：应用启动后延迟一段时间执行一次

```bash
npm i @nestjs/schedule
```

### 16.2 Cron 定时任务

```typescript
// tasks.service.ts
import { Injectable, Logger } from '@nestjs/common';
import { Cron, CronExpression } from '@nestjs/schedule';

@Injectable()
export class TasksService {
  private readonly logger = new Logger(TasksService.name);

  // ===== Cron 表达式（字符串）=====
  // "0 0 2 * * *" = 每天凌晨 2:00
  @Cron('0 0 2 * * *', {
    name: 'dailyCleanup',       // 任务名称（用于动态管理）
    timeZone: 'Asia/Shanghai',  // 指定时区（默认 UTC）
  })
  handleDailyCleanup(): void {
    this.logger.log('开始每日数据清理...');
    // 删除 30 天前的日志等
  }

  // ===== 使用 CronExpression 枚举 =====
  @Cron(CronExpression.EVERY_30_MINUTES)
  handleSync(): void {
    this.logger.log('每 30 分钟同步一次外部数据');
  }

  // ===== 每 10 秒执行 =====
  @Cron('*/10 * * * * *')
  handleHealthCheck(): void {
    this.logger.debug('健康检查：一切正常');
  }
}

// tasks.module.ts
import { Module } from '@nestjs/common';
import { ScheduleModule } from '@nestjs/schedule';
import { TasksService } from './tasks.service';

@Module({
  imports: [ScheduleModule.forRoot()],  // 激活调度功能
  providers: [TasksService],
})
export class TasksModule {}
```

### 16.3 Interval 与 Timeout

```typescript
import { Injectable, Logger } from '@nestjs/common';
import { Interval, Timeout, SchedulerRegistry } from '@nestjs/schedule';

@Injectable()
export class CacheTasksService {
  private readonly logger = new Logger(CacheTasksService.name);

  constructor(private schedulerRegistry: SchedulerRegistry) {}

  // 应用启动 5 秒后执行一次
  @Timeout('initCache', 5000)
  handleInitCache(): void {
    this.logger.log('应用启动 5 秒后：初始化缓存');
  }

  // 每 30 秒执行一次
  @Interval('refreshHotData', 30000)
  handleRefreshHotData(): void {
    this.logger.log('每 30 秒刷新热点数据');
  }

  // 动态停止定时任务
  stopRefreshTask(): void {
    try {
      this.schedulerRegistry.deleteInterval('refreshHotData');
      this.logger.log('已停止热点数据刷新任务');
    } catch (error) {
      this.logger.error('停止任务失败：' + error.message);
    }
  }

  // 动态启动定时任务
  startRefreshTask(): void {
    const interval = setInterval(() => {
      this.handleRefreshHotData();
    }, 30000);
    this.schedulerRegistry.addInterval('refreshHotData', interval);
    this.logger.log('已启动热点数据刷新任务');
  }

  // 停止超时任务（在它执行前取消）
  cancelInitCache(): void {
    this.schedulerRegistry.deleteTimeout('initCache');
    this.logger.log('已取消初始化缓存任务');
  }
}
```

### 16.4 Cron 表达式详解

Cron 表达式有 6 位（含秒）或 5 位（不含秒）：

```
*   *   *   *   *   *
┬   ┬   ┬   ┬   ┬   ┬
│   │   │   │   │   └ 星期  (0-7，0 和 7 都表示周日)
│   │   │   │   └─── 月    (1-12)
│   │   │   └─────── 日    (1-31)
│   │   └─────────── 时    (0-23)
│   └─────────────── 分    (0-59)
└─────────────────── 秒    (0-59，可选)
```

**常用表达式速查**：

| 表达式 | 含义 |
|--------|------|
| `* * * * * *` | 每秒执行 |
| `*/30 * * * * *` | 每 30 秒 |
| `0 * * * * *` | 每分钟（第 0 秒） |
| `0 0 * * * *` | 每小时整点 |
| `0 0 9 * * 1-5` | 工作日早上 9:00 |
| `0 0 2 * * *` | 每天凌晨 2:00 |
| `0 0 0 1 * *` | 每月 1 号凌晨 |
| `0 30 8 1 * *` | 每月 1 号早上 8:30 |
| `0 0 0 * * 0` | 每周日凌晨 |

---

## 17. WebSocket

### 17.1 WebSocket 与 NestJS

NestJS 对 WebSocket 有一等支持——Gateway 在 NestJS 中类似于 Controller，但处理的是 WebSocket 消息而非 HTTP 请求。它同样可以使用 Guard、Pipe、Interceptor、ExceptionFilter。

```bash
npm i @nestjs/websockets @nestjs/platform-socket.io socket.io
```

### 17.2 基本 Gateway

```typescript
// chat.gateway.ts
import {
  WebSocketGateway,
  WebSocketServer,
  SubscribeMessage,
  OnGatewayInit,
  OnGatewayConnection,
  OnGatewayDisconnect,
  MessageBody,
  ConnectedSocket,
  WsException,         // WebSocket 专用异常
} from '@nestjs/websockets';
import { Server, Socket } from 'socket.io';
import { Logger, UseGuards } from '@nestjs/common';
import { WsAuthGuard } from './ws-auth.guard';

@WebSocketGateway(3001, {  // 监听 3001 端口（默认与 HTTP 同端口）
  cors: {
    origin: '*',           // 允许跨域来源
    credentials: true,
  },
  namespace: '/chat',       // 命名空间（类似路由前缀）
  transports: ['websocket', 'polling'],  // 传输方式
  pingInterval: 10000,     // 心跳间隔 10s
  pingTimeout: 5000,        // 心跳超时 5s
})
export class ChatGateway
  implements OnGatewayInit, OnGatewayConnection, OnGatewayDisconnect
{
  @WebSocketServer()
  server: Server;  // Socket.IO Server 实例

  private readonly logger = new Logger(ChatGateway.name);
  private onlineUsers = new Map<string, { username: string; joinedAt: Date }>();

  // ===== 生命周期钩子 =====

  afterInit(server: Server): void {
    this.logger.log('WebSocket 网关初始化完成');
  }

  handleConnection(client: Socket, ...args: any[]): void {
    const token = client.handshake.auth?.token || client.handshake.query?.token;
    this.logger.log(`新连接: ${client.id}, Token: ${token ? '存在' : '无'}`);

    // 如果没有 token，可以拒绝连接
    if (!token) {
      client.emit('error', { message: '缺少认证 Token' });
      client.disconnect();
    }
  }

  handleDisconnect(client: Socket): void {
    this.logger.log(`断开连接: ${client.id}`);
    const userInfo = this.onlineUsers.get(client.id);
    if (userInfo) {
      this.onlineUsers.delete(client.id);

      // 广播用户离开消息给其他用户
      this.server.emit('userLeft', {
        username: userInfo.username,
        onlineCount: this.onlineUsers.size,
      });
    }
  }

  // ===== 处理客户端消息 =====

  // 订阅 'join' 事件
  @SubscribeMessage('join')
  handleJoinRoom(
    @MessageBody() data: { username: string; room?: string },
    @ConnectedSocket() client: Socket,
  ): { event: string; data: any } {
    const { username, room = 'general' } = data;

    // 存储用户信息
    this.onlineUsers.set(client.id, { username, joinedAt: new Date() });

    // 加入 Socket.IO 房间
    client.join(room);

    this.logger.log(`${username} 加入房间: ${room}`);

    // 向房间内其他人广播
    client.to(room).emit('userJoined', {
      username,
      room,
      onlineCount: this.onlineUsers.size,
    });

    // 回复客户端自己
    return {
      event: 'joined',
      data: {
        message: `欢迎 ${username}！你已加入 "${room}" 房间`,
        room,
        onlineCount: this.onlineUsers.size,
      },
    };
  }

  // 订阅 'message' 事件
  @SubscribeMessage('message')
  handleMessage(
    @MessageBody() data: { room: string; message: string },
    @ConnectedSocket() client: Socket,
  ): void {
    const userInfo = this.onlineUsers.get(client.id);
    const username = userInfo?.username || '匿名';

    // 向指定房间发送消息
    this.server.to(data.room).emit('newMessage', {
      username,
      message: data.message,
      room: data.room,
      timestamp: new Date().toISOString(),
    });
  }

  // 发送私信
  @SubscribeMessage('privateMessage')
  handlePrivateMessage(
    @MessageBody() data: { targetUsername: string; message: string },
    @ConnectedSocket() client: Socket,
  ): void {
    const senderInfo = this.onlineUsers.get(client.id);

    // 查找目标用户
    let targetSocketId: string | null = null;
    for (const [id, info] of this.onlineUsers) {
      if (info.username === data.targetUsername) {
        targetSocketId = id;
        break;
      }
    }

    if (!targetSocketId) {
      client.emit('error', { message: `用户 ${data.targetUsername} 不在线` });
      return;
    }

    // 只发送给目标用户
    this.server.to(targetSocketId).emit('privateMessage', {
      from: senderInfo?.username || '匿名',
      message: data.message,
      timestamp: new Date().toISOString(),
    });
  }

  // ===== 服务端主动推送 =====

  // 可以由 HTTP Controller 或定时任务调用
  broadcastAnnouncement(message: string): void {
    this.server.emit('announcement', {
      message,
      timestamp: new Date().toISOString(),
    });
  }

  // 向特定房间推送
  sendToRoom(room: string, event: string, data: any): void {
    this.server.to(room).emit(event, data);
  }
}
```

### 17.3 注册 Gateway

Gateway 像 Provider 一样注册即可：

```typescript
// app.module.ts
import { Module } from '@nestjs/common';
import { ChatGateway } from './chat/chat.gateway';

@Module({
  providers: [ChatGateway],
})
export class AppModule {}
```

### 17.4 命名空间与房间的区别

| 概念 | 作用 | 何时使用 |
|------|------|---------|
| **Namespace** (`/chat`) | 隔离不同的业务线 | 聊天系统 vs 通知系统 |
| **Room** (`room-name`) | 同一个 Namespace 内的小组 | 聊天系统的不同群组 |

```text
Socket.IO Server
├── /chat (聊天命名空间)
│   ├── 用户A joined 'room-1', 'room-2'
│   └── 用户B joined 'room-1'
└── /notifications (通知命名空间)
    └── 用户C
```

### 17.5 前端连接示例

```html
<script src="https://cdn.socket.io/4.7.0/socket.io.min.js"></script>
<script>
  const socket = io('http://localhost:3001/chat', {
    transports: ['websocket'],
    auth: { token: 'your-jwt-token' },
  });

  socket.on('connect', () => {
    console.log('WebSocket 已连接');

    // 加入房间
    socket.emit('join', { username: 'John', room: 'general' }, (response) => {
      console.log('服务器回复:', response.data.message);
    });
  });

  socket.on('newMessage', (data) => {
    console.log(`${data.username} 说: ${data.message}`);
  });

  socket.on('disconnect', (reason) => {
    console.log('断开连接:', reason);
  });

  // 发送消息
  function sendMessage(msg) {
    socket.emit('message', { room: 'general', message: msg });
  }
</script>
```

---

## 18. GraphQL

### 18.1 GraphQL vs REST

| 特性 | REST | GraphQL |
|------|------|---------|
| 数据获取 | 每个资源一个端点 `/users/:id` | 单一端点 `/graphql` |
| 返回字段 | 服务端决定返回哪些字段 | 客户端精确指定需要的字段 |
| 多次请求 | N 个关联资源 = N 次请求 | 一次查询获取所有关联数据 |
| 类型系统 | 无 | Schema 强类型 |
| 学习曲线 | 低 | 中 |

### 18.2 Code First 方式（推荐）

NestJS 的 Code First 方式是从 TypeScript 代码自动生成 GraphQL Schema，不需要手写 .graphql 文件。

```bash
npm i @nestjs/graphql @nestjs/apollo @apollo/server graphql
```

**配置**：

```typescript
// app.module.ts
import { Module } from '@nestjs/common';
import { GraphQLModule } from '@nestjs/graphql';
import { ApolloDriver, ApolloDriverConfig } from '@nestjs/apollo';
import { join } from 'path';

@Module({
  imports: [
    GraphQLModule.forRoot<ApolloDriverConfig>({
      driver: ApolloDriver,
      // 自动根据代码生成 schema 文件（方便查看生成的 Schema）
      autoSchemaFile: join(process.cwd(), 'src/schema.gql'),
      sortSchema: true,        // 按字母排序 schema
      playground: true,        // 开启 GraphQL Playground（开发工具）
      introspection: true,     // 允许内省查询（生产环境建议关闭）
    }),
  ],
})
export class AppModule {}
```

### 18.3 定义 ObjectType（输出类型）

```typescript
// models/user.model.ts
import { ObjectType, Field, Int, ID, HideField } from '@nestjs/graphql';

@ObjectType({ description: '用户信息' })
export class User {
  @Field(() => ID, { description: '用户 ID' })
  id: number;

  @Field({ description: '用户名' })
  username: string;

  @Field({ description: '电子邮件' })
  email: string;

  @HideField()  // 不在 GraphQL Schema 中暴露（如密码）
  password: string;

  @Field({ nullable: true, description: '昵称' })
  nickname?: string;

  @Field(() => Int, { description: '年龄' })
  age: number;

  @Field({ description: '创建时间' })
  createdAt: Date;

  // nullable: true 表示该字段可以为 null
  @Field(() => String, { nullable: true, description: '头像 URL' })
  avatar?: string;
}
```

### 18.4 定义 InputType（输入类型）

```typescript
// dto/create-user.input.ts
import { InputType, Field, Int } from '@nestjs/graphql';
import {
  IsEmail, IsString, MinLength, MaxLength,
  IsInt, Min, Max, IsOptional,
} from 'class-validator';

@InputType({ description: '创建用户需要的输入参数' })
export class CreateUserInput {
  @Field({ description: '用户名' })
  @IsString()
  @MinLength(2, { message: '用户名至少 2 个字符' })
  @MaxLength(50, { message: '用户名最多 50 个字符' })
  username: string;

  @Field({ description: '电子邮箱' })
  @IsEmail({}, { message: '邮箱格式不正确' })
  email: string;

  @Field(() => Int, { description: '年龄' })
  @IsInt()
  @Min(0)
  @Max(150)
  age: number;

  @Field({ nullable: true, description: '昵称（选填）' })
  @IsOptional()
  @IsString()
  @MaxLength(100)
  nickname?: string;
}
```

### 18.5 Resolver（类似 Controller）

```typescript
// user.resolver.ts
import { Resolver, Query, Mutation, Args, Int, ResolveField, Parent } from '@nestjs/graphql';
import { UserService } from './user.service';
import { User } from './models/user.model';
import { CreateUserInput } from './dto/create-user.input';
import { UpdateUserInput } from './dto/update-user.input';

@Resolver(() => User)  // 声明这个 Resolver 处理 User 类型
export class UserResolver {
  constructor(private readonly userService: UserService) {}

  // ===== Query（等同于 GET） =====

  @Query(() => [User], {
    name: 'users',
    description: '获取所有用户列表',
  })
  async getUsers(): Promise<User[]> {
    return this.userService.findAll();
  }

  @Query(() => User, {
    name: 'user',
    description: '根据 ID 获取用户',
    nullable: true,  // 可能返回 null（找不到时）
  })
  async getUser(
    @Args('id', { type: () => Int, description: '用户 ID' }) id: number,
  ): Promise<User | null> {
    return this.userService.findById(id);
  }

  // ===== Mutation（等同于 POST/PUT/DELETE） =====

  @Mutation(() => User, {
    name: 'createUser',
    description: '创建新用户',
  })
  async createUser(
    @Args('input', { description: '创建用户参数' }) input: CreateUserInput,
  ): Promise<User> {
    return this.userService.create(input);
  }

  @Mutation(() => User, {
    name: 'updateUser',
    description: '更新用户信息',
    nullable: true,
  })
  async updateUser(
    @Args('id', { type: () => Int }) id: number,
    @Args('input') input: UpdateUserInput,
  ): Promise<User> {
    return this.userService.update(id, input);
  }

  @Mutation(() => Boolean, {
    name: 'deleteUser',
    description: '删除用户',
  })
  async deleteUser(
    @Args('id', { type: () => Int }) id: number,
  ): Promise<boolean> {
    await this.userService.remove(id);
    return true;  // 返回 Boolean 表示操作成功
  }
}
```

**`@Query()` vs `@Mutation()`**：
- Query = 只读查询，相当于 HTTP GET
- Mutation = 修改数据，相当于 HTTP POST/PUT/DELETE
- 两者唯一的区别是：GraphQL 规范保证 Query 是**幂等的**（多次执行结果一致），Mutation 不是

### 18.6 GraphQL Playground 使用

启动应用后访问 `http://localhost:3000/graphql`，在 Playground 中编写查询：

```graphql
# ===== 查询：只获取 id 和 username =====
query {
  users {
    id
    username
  }
}
# 返回: { "data": { "users": [{ "id": "1", "username": "john" }, ...] } }

# ===== 查询：获取更多字段 =====
query {
  user(id: 1) {
    id
    username
    email
    age
    createdAt
  }
}

# ===== 创建用户 =====
mutation {
  createUser(input: {
    username: "john_doe"
    email: "john@example.com"
    age: 25
  }) {
    id
    username
  }
}

# ===== 带变量的查询 =====
query($userId: Int!) {
  user(id: $userId) {
    username
    email
  }
}
# 在 Query Variables 面板填入: { "userId": 1 }
```

### 18.7 ResolveField —— 处理派生字段

当需要根据关联关系动态计算某个字段时：

```typescript
@Resolver(() => User)
export class UserResolver {
  // ResolveField 告诉 GraphQL 如何计算某个字段的值
  @ResolveField(() => Int, {
    name: 'articleCount',
    description: '该用户的文章数量',
  })
  async articleCount(@Parent() user: User): Promise<number> {
    // @Parent() 获取用户查询的结果对象
    return this.articleService.countByAuthor(user.id);
  }

  // 加载关联的文章列表
  @ResolveField(() => [Article], {
    name: 'articles',
    description: '该用户写的文章',
  })
  async articles(@Parent() user: User): Promise<Article[]> {
    return this.articleService.findByAuthor(user.id);
  }
}
```

客户端可以这样查询：

```graphql
query {
  user(id: 1) {
    username
    articleCount    # 由 ResolveField 动态计算
    articles {      # 由 ResolveField 动态加载
      id
      title
    }
  }
}
```

---

## 19. 性能优化

### 19.1 启用 Gzip 压缩

```bash
npm i compression
npm i -D @types/compression
```

```typescript
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import * as compression from 'compression';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // 对 >1KB 的响应体自动 Gzip 压缩
  app.use(compression({
    threshold: 1024,   // 1KB 以上才压缩
    level: 6,          // 压缩级别 0-9（越大压缩率越高但越慢）
    filter: (req, res) => {
      // 只压缩特定 MIME 类型
      if (req.headers['x-no-compression']) {
        return false;  // 请求头标记为不需要压缩时跳过
      }
      return compression.filter(req, res);  // 默认过滤（只压缩 text/json 等）
    },
  }));

  await app.listen(3000);
}
bootstrap();
```

### 19.2 缓存

```bash
npm i @nestjs/cache-manager cache-manager
```

**基础配置**：

```typescript
import { CacheModule } from '@nestjs/cache-manager';

@Module({
  imports: [
    CacheModule.register({
      isGlobal: true,
      ttl: 10000,       // 默认 TTL 10 秒（毫秒）
      max: 100,         // 最多缓存 100 个 key
    }),
  ],
})
export class AppModule {}
```

**使用 CacheInterceptor（自动缓存整个路由的返回）**：

```typescript
import { CacheInterceptor, CacheKey, CacheTTL } from '@nestjs/cache-manager';

@Controller('products')
@UseInterceptors(CacheInterceptor)  // 控制器所有方法自动缓存
export class ProductsController {

  // 默认：CacheKey = 请求 URL，CacheTTL = 5 秒
  @Get()
  findAll(): string[] {
    return ['product-A', 'product-B', 'product-C'];
  }

  // 自定义 key 和 TTL
  @Get('hot')
  @CacheKey('hot_products')   // 指定缓存 key
  @CacheTTL(60000)             // 缓存 60 秒
  findHot(): string[] {
    // 模拟耗时的数据库查询
    return ['hot-1', 'hot-2'];
  }
}
```

**手动使用缓存管理器**：

```typescript
import { Inject, Injectable } from '@nestjs/common';
import { CACHE_MANAGER, Cache } from '@nestjs/cache-manager';

@Injectable()
export class ProductService {
  constructor(@Inject(CACHE_MANAGER) private cacheManager: Cache) {}

  async findById(id: number): Promise<any> {
    const cacheKey = `product:${id}`;

    // 1. 先查缓存
    const cached = await this.cacheManager.get(cacheKey);
    if (cached) {
      console.log(`缓存命中: ${cacheKey}`);
      return cached;
    }

    // 2. 缓存未命中 → 查数据库
    console.log(`缓存未命中: ${cacheKey}，查询数据库`);
    const product = await this.findFromDatabase(id);

    // 3. 写入缓存（60 秒后自动过期）
    await this.cacheManager.set(cacheKey, product, 60000);

    return product;
  }

  // 主动清除缓存
  async clearProductCache(id: number): Promise<void> {
    await this.cacheManager.del(`product:${id}`);
    console.log(`已清除 product:${id} 缓存`);
  }
}
```

### 19.3 序列化排除敏感字段

```typescript
import { Exclude, Expose, Transform } from 'class-transformer';
import { UseInterceptors, ClassSerializerInterceptor } from '@nestjs/common';

// 实体中使用 @Exclude 和 @Expose 控制返回字段
export class UserEntity {
  id: number;
  username: string;

  @Exclude()  // 始终不在响应中返回
  password: string;

  @Exclude()
  @Expose({ name: 'fullName' })  // 重命名暴露
  full_name: string;

  @Transform(({ value }) => value.toUpperCase())  // 值转换
  role: string;
}

// Controller 开启序列化
@Controller('users')
@UseInterceptors(ClassSerializerInterceptor)  // 开启序列化过滤
export class UsersController {
  @Get()
  findAll(): UserEntity[] {
    // 返回时 password、full_name 被自动排除
    // fullName 重命名、role 转为大写
    return this.userService.findAll();
  }
}
```

### 19.4 切换到 Fastify（性能提升 2-3 倍）

```bash
npm i @nestjs/platform-fastify
```

```typescript
// main.ts
import { NestFactory } from '@nestjs/core';
import {
  FastifyAdapter,
  NestFastifyApplication,
} from '@nestjs/platform-fastify';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create<NestFastifyApplication>(
    AppModule,
    new FastifyAdapter({
      logger: true,                  // 启用 Fastify 内置日志
      bodyLimit: 10485760,           // 请求体大小限制 10MB
      connectionTimeout: 10000,      // 连接超时 10 秒
      keepAliveTimeout: 5000,        // Keep-alive 超时
    }),
  );

  // Fastify 原生压缩（不需要 compression 中间件）
  await app.register(require('@fastify/compress'));

  await app.listen(3000, '0.0.0.0');
}
bootstrap();
```

**注意**：切换到 Fastify 后，Express 生态的中间件（如 `express-rate-limit`）不可用，需要使用 Fastify 等价插件。

### 19.5 性能优化检查清单

| 优化方向 | 具体做法 |
|----------|---------|
| HTTP 引擎 | 用 Fastify 替代 Express |
| 压缩 | 启用 Gzip/Brotli 压缩 |
| 缓存 | 热点数据加缓存，减少数据库查询 |
| 数据库索引 | 为 WHERE/ORDER BY/JOIN 的列添加索引 |
| 连接池 | TypeORM `extra.connectionLimit: 10-20` |
| 序列化排除 | 敏感字段 `@Exclude()` |
| 避免 N+1 | TypeORM 用 `leftJoinAndSelect` 代替 `relations` |
| 异步 | Service 方法使用 `async/await`，避免同步阻塞 |
| 减少日志 | 生产环境关闭 `logging: true` |
| 请求限流 | 使用 Fastify 的 `@fastify/rate-limit` |

---

## 20. 单元测试与 E2E 测试

### 20.1 测试策略总览

NestJS 项目通常涉及三种测试：

| 类型 | 测试范围 | 工具 | 速度 |
|------|---------|------|------|
| **单元测试** | 单个 Service/Controller | Jest | 极快 |
| **集成测试** | 一个模块（含真实 Repository） | Jest + Test.createTestingModule | 较快 |
| **E2E 测试** | 整个应用（含数据库） | Jest + supertest | 慢 |

### 20.2 单元测试 Service

```typescript
// cats.service.spec.ts
import { Test, TestingModule } from '@nestjs/testing';
import { CatsService } from './cats.service';

describe('CatsService', () => {
  let service: CatsService;

  // beforeEach：每个测试用例前重建测试模块（保证测试隔离）
  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [CatsService],
    }).compile();

    service = module.get<CatsService>(CatsService);
  });

  // ===== 测试组：create =====
  describe('create', () => {
    it('应该成功创建猫咪并可通过 findAll 查找到', () => {
      // Arrange（准备）
      const cat = { name: 'Tom', age: 3, breed: 'Persian' };

      // Act（执行）
      service.create(cat);

      // Assert（断言）
      const cats = service.findAll();
      expect(cats).toHaveLength(1);
      expect(cats[0]).toMatchObject({ name: 'Tom', age: 3 });
    });

    it('创建多只猫咪时应该全部存在', () => {
      service.create({ name: 'A', age: 1, breed: 'X' });
      service.create({ name: 'B', age: 2, breed: 'Y' });
      service.create({ name: 'C', age: 3, breed: 'Z' });

      expect(service.findAll()).toHaveLength(3);
    });
  });

  describe('findOne', () => {
    it('应该通过名称找到猫咪', () => {
      service.create({ name: 'Tom', age: 3, breed: 'Persian' });
      service.create({ name: 'Jerry', age: 2, breed: 'Siamese' });

      const cat = service.findOne('Tom');
      expect(cat).toBeDefined();
      expect(cat!.breed).toBe('Persian');
    });

    it('未找到时应该返回 undefined', () => {
      const result = service.findOne('NonExistent');
      expect(result).toBeUndefined();
    });
  });
});
```

### 20.3 Mock Repository 测试（集成测试核心）

```typescript
// user.service.spec.ts
import { Test, TestingModule } from '@nestjs/testing';
import { getRepositoryToken } from '@nestjs/typeorm';
import { UserService } from './user.service';
import { User } from './entities/user.entity';
import { NotFoundException } from '@nestjs/common';

describe('UserService', () => {
  let service: UserService;

  // 创建 Mock Repository —— 模拟 TypeORM Repository 的行为
  const mockRepository = {
    find: jest.fn(),
    findOne: jest.fn(),
    findAndCount: jest.fn(),
    create: jest.fn(),
    save: jest.fn(),
    update: jest.fn(),
    delete: jest.fn(),
    createQueryBuilder: jest.fn(),
  };

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        UserService,
        {
          // getRepositoryToken(User) 返回 TypeORM 为该实体生成的注入 Token
          provide: getRepositoryToken(User),
          useValue: mockRepository,  // 用 Mock 替代真正的 Repository
        },
      ],
    }).compile();

    service = module.get<UserService>(UserService);

    // 每个测试前清除 Mock 调用记录
    jest.clearAllMocks();
  });

  describe('findById', () => {
    it('应该返回用户', async () => {
      const mockUser = { id: 1, username: 'john', email: 'john@example.com' };
      mockRepository.findOne.mockResolvedValue(mockUser);
      // mockResolvedValue: 当 findOne 被调用时，返回 Promise.resolve(mockUser)

      const result = await service.findById(1);

      expect(result).toEqual(mockUser);
      // 验证 findOne 被调用时传入的参数
      expect(mockRepository.findOne).toHaveBeenCalledWith({ where: { id: 1 } });
    });

    it('用户不存在应该抛出 NotFoundException', async () => {
      mockRepository.findOne.mockResolvedValue(null);

      // rejects.toThrow: 验证 async 函数抛出特定异常
      await expect(service.findById(999)).rejects.toThrow(NotFoundException);
    });
  });

  describe('create', () => {
    it('应该创建并返回用户', async () => {
      const dto = { username: 'new_user', email: 'new@example.com', age: 25 };
      const savedUser = { id: 1, ...dto };

      // create 返回一个未保存的实体实例
      mockRepository.create.mockReturnValue(dto);
      // save 返回已保存的实体（带自增 ID）
      mockRepository.save.mockResolvedValue(savedUser);

      const result = await service.create(dto);

      expect(result).toEqual(savedUser);
      expect(mockRepository.create).toHaveBeenCalledWith(dto);
      expect(mockRepository.save).toHaveBeenCalledWith(dto);
    });
  });
});
```

**Mock 的核心概念**：
- `jest.fn()` 创建一个 Mock 函数，可以记录调用次数、参数、返回值
- `mockResolvedValue(x)` 让 Mock 函数返回 `Promise.resolve(x)`（模拟异步返回）
- `mockReturnValue(x)` 让 Mock 函数返回 `x`（模拟同步返回）
- `toHaveBeenCalledWith(args)` 验证 Mock 函数被调用时传入的参数

### 20.4 测试 Controller

```typescript
import { Test, TestingModule } from '@nestjs/testing';
import { UsersController } from './users.controller';
import { UserService } from './user.service';

describe('UsersController', () => {
  let controller: UsersController;
  let service: UserService;

  // 也可以 Mock Service
  const mockUserService = {
    findAll: jest.fn(),
    findById: jest.fn(),
    create: jest.fn(),
  };

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [UsersController],
      providers: [
        {
          provide: UserService,
          useValue: mockUserService,
        },
      ],
    }).compile();

    controller = module.get<UsersController>(UsersController);
    service = module.get<UserService>(UserService);
    jest.clearAllMocks();
  });

  it('GET /users 应该返回用户列表', async () => {
    const mockUsers = [
      { id: 1, username: 'john' },
      { id: 2, username: 'jane' },
    ];
    mockUserService.findAll.mockResolvedValue(mockUsers);

    const result = await controller.findAll();
    expect(result).toEqual(mockUsers);
    expect(mockUserService.findAll).toHaveBeenCalledTimes(1);
  });
});
```

### 20.5 E2E 测试（端到端）

E2E 测试启动完整的应用实例，通过 HTTP 请求测试所有层：

```typescript
// test/app.e2e-spec.ts
import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication, ValidationPipe } from '@nestjs/common';
import * as request from 'supertest';
import { AppModule } from '../src/app.module';

describe('App (E2E)', () => {
  let app: INestApplication;

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],  // 导入完整的 AppModule
    }).compile();

    app = moduleFixture.createNestApplication();
    // 应用与生产环境相同的配置
    app.useGlobalPipes(
      new ValidationPipe({ whitelist: true, transform: true }),
    );
    app.setGlobalPrefix('api');
    await app.init();  // 启动 HTTP 服务器
  });

  afterAll(async () => {
    await app.close();  // 测试结束关闭应用
  });

  it('/api/cats (GET) — 空列表', () => {
    return request(app.getHttpServer())  // 获取 HTTP 服务器实例
      .get('/api/cats')
      .expect(200)
      .expect([]);
  });

  it('/api/cats (POST) — 创建猫咪', () => {
    return request(app.getHttpServer())
      .post('/api/cats')
      .send({ name: 'Tom', age: 3, breed: 'Persian' })
      .expect(201)
      .expect((res) => {
        expect(res.body).toHaveProperty('id');
        expect(res.body.name).toBe('Tom');
      });
  });

  it('/api/cats/1 (GET) — 查询创建的猫咪', () => {
    return request(app.getHttpServer())
      .get('/api/cats/1')
      .expect(200)
      .expect((res) => {
        expect(res.body.name).toBe('Tom');
      });
  });

  it('/api/cats/999 (GET) — 不存在的 ID 返回 404', () => {
    return request(app.getHttpServer())
      .get('/api/cats/999')
      .expect(404);
  });

  it('/api/cats (POST) — 缺少必填字段返回 400', () => {
    return request(app.getHttpServer())
      .post('/api/cats')
      .send({})  // 空请求体
      .expect(400);
  });
});
```

**E2E 测试数据库处理策略**：

| 策略 | 优点 | 缺点 |
|------|------|------|
| 内存数据库（SQLite in-memory） | 快、无需外部依赖 | 与生产 MySQL/PG 行为可能不一致 |
| 独立测试数据库 | 接近生产 | 需要额外配置 |
| Docker 临时容器 | 完全隔离 | 启动开销大 |
| 事务回滚 | 每个测试后干净回滚 | 需要手动管理事务 |

### 20.6 常用测试命令

```bash
# 运行所有单元测试
npm test

# 运行所有测试并生成覆盖率报告
npm run test:cov

# 监听模式 - 文件改动自动重跑
npm run test:watch

# E2E 测试
npm run test:e2e

# 运行匹配特定模式的测试文件
npx jest cats.service

# 只运行测试文件中匹配特定名称的测试
npx jest --testNamePattern="应该成功创建"

# 显示每个测试的详情
npx jest --verbose
```

**package.json 的 Jest 配置**：

```json
{
  "jest": {
    "moduleFileExtensions": ["js", "json", "ts"],
    "rootDir": "src",
    "testRegex": ".*\\.spec\\.ts$",
    "transform": {
      "^.+\\.(t|j)s$": "ts-jest"
    },
    "collectCoverageFrom": [
      "**/*.(t|j)s",
      "!**/*.spec.ts",
      "!**/*.e2e-spec.ts",
      "!main.ts"
    ],
    "coverageDirectory": "../coverage",
    "testEnvironment": "node"
  }
}
```

---

> **文档完** — 本文档覆盖了 NestJS 从基础概念到高级用法的完整内容，每个概念均提供详细的中文解释和 TypeScript 示例代码。建议按顺序阅读，概念之间有递进关系。
