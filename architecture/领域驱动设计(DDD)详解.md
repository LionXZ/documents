# 领域驱动设计（DDD）详解

## 一、DDD 是什么

领域驱动设计（Domain-Driven Design）是一种**软件设计方法论**，核心思想是：**把业务领域的核心逻辑放在第一位，技术实现服务于业务**。由 Eric Evans 在 2003 年提出。

不是一套框架或代码模式，而是一套**思维方式**——让代码中的概念和业务专家口中的概念保持一致。

### DDD 与面向对象的关系

DDD 不是凭空出现的，它是对 OOP 核心原则的**继承和深化**：

```
OOP 告诉你：封装、继承、多态
DDD 告诉你：具体怎么用 OOP 解决复杂业务问题

OOP 说"用对象封装行为"
DDD 说"具体哪些行为该放哪些对象里，这些对象之间怎么组织"

OOP 说"依赖抽象不依赖具体"
DDD 说"把抽象接口（端口）放在领域层，具体实现在外面做适配器"
```

**DDD = OOP 的原则拉到项目结构维度重做了一遍：**

| OOP 原则 | DDD 对应 |
|-----------|----------|
| 封装（Encapsulation） | 聚合根控制内部对象访问 |
| 单一职责（SRP） | 限界上下文；领域服务只协调跨实体的行为 |
| 依赖倒转（DIP） | 六边形架构：领域层定义接口，基础设施层实现 |
| 接口隔离（ISP） | 每个仓储接口只暴露聚合根需要的操作 |

如果你觉得 DDD 难理解，一个捷径是：**把它当成"把 OOP 做对"的方法论**。很多项目写了 Service + DAO，觉得用了 class 就是 OOP，实际上只是面向过程换了个写法。DDD 就是在纠正这个。

### 为什么需要 DDD

```
❌ 传统贫血模型：
Controller → Service → DAO → 数据库
业务逻辑散落在 Service 层，领域对象（Entity）只有 getter/setter，没有行为

✅ DDD 充血模型：
Controller → Application Service → Domain（Entity + ValueObject + Service）→ Repository → 数据库
核心业务逻辑封装在领域对象内部，对象有状态也有行为
```

---

## 二、核心概念总览

```
                    ┌─────────────────────────────────┐
                    │        Strategic Design         │
                    │   战略设计（大的划分）             │
                    │  Bounded Context · Context Map  │
                    │  Ubiquitous Language            │
                    └──────────────┬──────────────────┘
                                   │
                    ┌──────────────▼──────────────────┐
                    │        Tactical Design          │
                    │     战术设计（落地实现）           │
                    │  Entity · ValueObject           │
                    │  Aggregate · Repository         │
                    │  Domain Service · Domain Event  │
                    │  Factory · Specification        │
                    └─────────────────────────────────┘
```

---

## 三、战略设计

### 3.1 通用语言（Ubiquitous Language）

项目所有人（开发、产品、业务、测试）使用**同一套术语**，这套术语直接反映在代码中。

```java
// ❌ 坏例子：代码术语和业务术语不一致
user.setStatus(3);  // 3 是什么意思？

// ✅ 好例子：代码即文档
order.confirm();    // 确认订单，业务术语直接表达
order.cancel("用户主动取消");
```

**落地方式：** 维护一份术语表文档，并在代码评审中确保领域模型命名与术语表一致。

**开发场景举例——为什么通用语言不是"写好听的变量名"那么简单：**

```
真实案例：订单系统中一个叫"退款"的操作

产品说：退款 = 用户发起退款申请 → 客服审核 → 财务打款
运营说：退款 = 系统自动退款（无需审核的订单）
财务说：退款 = 钱从公司账户退回到用户账户

如果你在代码里写了一个 refund() 方法，它到底做哪个？
❌ 只有一个 refund()  → 三个人三个预期，必然出 bug
✅ 分别建模：
   - 订单上下文: order.initiateRefund()  // 发起退款申请
   - 审核上下文: audit.approveRefund()    // 审核退款
   - 支付上下文: payment.executeRefund()  // 执行退款打款
```

**OOP 对应：** 这就是"谁拥有这个行为"的问题——OOP 里你问"这个方法的职责属于哪个对象"，通用语言就是告诉你"去问问业务专家这个动词是哪个名词的职责"。

### 3.2 限界上下文（Bounded Context）

一个**明确的边界**，在这个边界内，通用语言有统一明确的含义。

```
        电商系统
        │
  ┌─────┼──────────┐
  │     │          │
  ▼     ▼          ▼
┌────┐ ┌────────┐ ┌──────┐
│商品│ │  订单   │ │ 用户  │
│上下│ │ 下单/  │ │ 注册  │
│文  │ │支付/物流│ │ 登录  │
└────┘ └────────┘ └──────┘
```

- 同一个词"商品"，在**商品上下文**里关注的是描述、规格、图片，在**订单上下文**里关注的是价格、数量、快照
- 每个上下文内部独立演化，互不污染

**OOP 对应：**

限界上下文在 OOP 里能找到两个对应：**Java 的 package 设计和类的单一职责**。

```java
// ❌ 没有上下文边界——一个 User 类要扮演所有角色
public class User {
    String username;        // 登录上下文关心的
    String password;        // 登录上下文关心的
    String phone;           // 又是登录又是下单都要用
    String defaultAddress;  // 下单关心，登录不关心
    int creditScore;        // 风控关心，下单不关心
    int points;             // 积分关心，下单不关心
    // 一个类同时服务 4 个上下文 → 任何修改都可能影响所有地方
}
```

用限界上下文划分后：

```java
// 每个上下文有自己的包和自己的 User 模型
// com.example.auth.domain
public class User {
    private UserId id;
    private String username;
    private String hashedPassword;
    private boolean enabled;
    // 只管认证相关
}

// com.example.order.domain
public class User {
    private UserId id;       // 通过 ID 引用，不是直接引用 auth.User
    private String phone;    // 订单需要的联系方式
    private Address defaultAddress;
    // 只管下单需要的用户信息
}

// com.example.risk.domain
public class User {
    private UserId id;
    private int creditScore;
    private List<RiskEvent> riskHistory;
    // 只管风控需要的用户画像
}
```

**同一个 "User" 词在不同包里有不同含义，互不污染。这就是包级别的单一职责。**

**一个容易混淆的点：** 限界上下文和你写 package/subpackage 不是一回事。限界上下文强调的是**概念的独立性**，一个上下文可以是一个独立微服务，也可以是一个大单体里的 `module`。关键不是物理隔离，而是概念隔离——让每个上下文可以独立演化。

描述不同限界上下文之间的关系：

| 关系模式 | 说明 | 适用场景 |
|----------|------|----------|
| 共享内核（Shared Kernel） | 两个上下文共享一部分模型 | 团队协作紧密 |
| 客户-供应商（Customer-Supplier） | 上游定义接口，下游使用 | 上下游明确 |
| 防腐层（Anti-Corruption Layer） | 在调用外部系统时加一层转换 | 对接遗留系统 |
| 开放主机服务（Open Host Service） | 对外提供统一 API | 多个下游消费者 |
| 发布语言（Published Language） | 使用标准格式交互（JSON、XML） | 系统间通信 |

> **防腐层**最重要也最常用——对接外部系统时，不要让外部模型污染你的领域模型。

**开发场景举例——防腐层（ACL）是怎么避免你的代码腐烂的：**

假设你要对接一个老旧的 ERP 系统，它返回的 JSON 长这样：

```json
// ERP 系统返回的"订单"——充满了别人的命名和结构
{
  "DING_DAN_HAO": "DD20240101",
  "XT_ZT": 3,              // 3 表示什么？只有 ERP 团队知道
  "SKJE": "199.00",        // 全是拼音缩写
  "XDRQ": "2024-01-01",
  "MX": [                  // 明细？毛线？总之不是 OrderItem
    { "SPDM": "P001", "JJ": "99.50", "SL": "2" }
  ]
}
```

没有防腐层的做法（数据直接渗透到你的领域）：

```java
// ❌ ERP 的数据结构直接散落在你的 OrderService 里
public class OrderService {
    public void syncFromERP(ERPOrder erpOrder) {
        // 你的代码里到处都是 XT_ZT、SKJE、SPDM 这些 ERP 的术语
        // 哪一天 ERP 升级了字段名，你的核心业务逻辑全得改
        if (erpOrder.getXT_ZT() == 3) {
            order.setStatus(OrderStatus.PAID);
        }
    }
}
```

有防腐层的做法：

```java
// ✅ 防腐层专门做翻译，你的领域模型保持干净
public class ERPOrderAdapter {
    public Order toDomainOrder(ERPOrderDTO erpDTO) {
        // 所有翻译逻辑集中在这里，ERP 升级了只需改这一处
        return Order.create(
            new OrderId(erpDTO.getDING_DAN_HAO()),
            mapStatus(erpDTO.getXT_ZT()),       // 3 → OrderStatus.PAID
            new Money(erpDTO.getSKJE(), CNY),   // "199.00" → Money(199.00, CNY)
            mapItems(erpDTO.getMX())            // 我叫 OrderItem，不叫 MX
        );
    }

    private OrderStatus mapStatus(int erpStatus) {
        return switch (erpStatus) {
            case 1 -> OrderStatus.PENDING;
            case 3 -> OrderStatus.PAID;
            // 所有状态映射集中管理
        };
    }
}
```

**OOP 中的对应——适配器模式（Adapter Pattern）：** ACL 就是 GoF 适配器模式的升级版。OOP 适配器在你自己的代码内把一个接口转成另一个接口，ACL 把同样的思想拉到系统边界层面，确保"别人家的模型"不要污染"我家的模型"。

---

## 四、战术设计

### 4.1 实体（Entity）

拥有**唯一标识**的对象，标识在其整个生命周期中保持不变，即使其他属性变了。

```java
// 实体：有唯一ID，通过 ID 判断是否为同一个对象
public class Order {
    private OrderId id;          // 唯一标识（不变）
    private OrderStatus status;  // 可变属性
    private Money totalAmount;   // 可变属性

    // 行为封装在实体内部
    public void pay(Money paidAmount) {
        if (!this.status.equals(OrderStatus.PENDING)) {
            throw new OrderException("订单状态不允许支付");
        }
        if (!paidAmount.equals(this.totalAmount)) {
            throw new OrderException("支付金额不匹配");
        }
        this.status = OrderStatus.PAID;
    }

    public void cancel(String reason) {
        if (this.status.equals(OrderStatus.SHIPPED)) {
            throw new OrderException("已发货的订单不能取消");
        }
        this.status = OrderStatus.CANCELED;
    }
}
```

**特征：** 有 ID、有生命周期、可变、通过 ID 判断相等性。

**OOP 深入——身份 vs 相等：引用语义 vs 值语义**

OOP 里有个很基础但常常被忽略的区分：

```java
// Java 里两个最经典的类型就体现了实体和值对象的区别

// String 是值对象思维——内容一样就是一样
String a = "hello";
String b = "hello";
a.equals(b);  // true —— 内容一样就是同一个东西

// 实体是引用（identity）思维——同一个 ID 才是同一个东西
// 即使你克隆了一个 Order 的所有属性，它的 ID 不同就是不同的订单
```

Java 里你见过的实体模式：

```java
// JPA/Hibernate 的 @Entity 就是 DDD 实体概念的技术实现
@Entity
public class Order {
    @Id  // ← 这就是 identity
    private Long id;       // 唯一，不变

    private String status; // 其他的都可以变
    private BigDecimal amount;
}
```

**开发场景举例——为什么实体必须通过 ID 而非属性判等：**

```java
// 一个用户修改了头像和昵称
User user1 = userRepo.findById(1L);  // id=1, name="张三", avatar="a.png"
user1.changeName("张三疯");
user1.changeAvatar("b.png");

// 过一会再查出来——还是他，但属性全变了
User user2 = userRepo.findById(1L);  // id=1, name="张三疯", avatar="b.png"

// 怎么判断 user1 == user2 是同一个"他"？
// ✅ 通过 ID：因为 id 都是 1，所以是同一个人
// ❌ 通过属性：name 从"张三"变成"张三疯"了，属性不一样 → 你以为他换了个人？
```

这就是为什么实体需要 ID——因为**实体的本质是会变的**，你必须有一个不变的东西来判断"这是同一个东西"。

再看贫血模型 vs 充血模型：

```java
// ❌ 贫血模型：实体只是数据容器
public class Order {
    private String id;
    private String status;
    // 只有 getter/setter，没有行为
}
// 然后在 Service 里写业务逻辑
service.payOrder(order, amount);  // 行为在外部

// ✅ 充血模型：实体拥有行为
order.pay(amount);  // 行为在内部，业务逻辑内聚
```

### 4.2 值对象（Value Object）

没有唯一标识，通过**属性值**来定义相等性。不可变。

```java
// 值对象：没有 ID，通过所有属性判断相等，不可变
public class Money {
    private final BigDecimal amount;
    private final Currency currency;

    public Money(BigDecimal amount, Currency currency) {
        this.amount = amount;
        this.currency = currency;
    }

    public Money add(Money other) {
        if (!this.currency.equals(other.currency)) {
            throw new IllegalArgumentException("币种不匹配");
        }
        return new Money(this.amount.add(other.amount), this.currency);
    }

    // 没有 setter，所有操作返回新对象（不可变）
}
```

| 特征 | 实体（Entity） | 值对象（Value Object） |
|------|---------------|----------------------|
| 唯一标识 | 有（ID） | 无 |
| 相等性 | 通过 ID | 通过所有属性 |
| 可变性 | 可变 | 不可变 |
| 生命周期 | 有 | 无（属于某个实体） |

**为什么要用值对象？**

```java
// ❌ 使用原始类型
public void updateAddress(Long userId, String province, String city,
                          String district, String detail) {
    // 参数爆炸，含义不清
}

// ✅ 使用值对象
public void updateAddress(UserId userId, Address newAddress) {
    // 概念清晰，校验内聚在 Address 内部
}

public class Address {
    private final String province;
    private final String city;
    private final String district;
    private final String detail;

    // 构造时做校验
    public Address(String province, String city, String district, String detail) {
        if (province == null || city == null) {
            throw new IllegalArgumentException("省市不能为空");
        }
        this.province = province;
        this.city = city;
        this.district = district;
        this.detail = detail;
    }
}
```

**OOP 深入——值对象是"不可变对象"的最佳实践**

OOP 里教过不可变对象的好处（线程安全、无副作用），值对象就是这个原则在业务代码里的应用：

```java
// OOP 中你见过的不可变类——本质上就是值对象
String str = "hello";
str.toUpperCase();  // 返回 "HELLO"，但 str 自己没变
// String 就是 Java 标准库里最经典的值对象

// java.time.LocalDate 也是值对象
LocalDate d1 = LocalDate.of(2024, 1, 1);
LocalDate d2 = d1.plusDays(30);  // 返回新对象，d1 不变
```

DDD 让你在自己的代码里也这么写——把用 `BigDecimal`、`String` 的地方换成有业务含义的不可变对象。

**开发场景举例——再看一遍"基本类型偏执"的危害：**

```java
// 场景：订单支付，各种地方都用到"金额"

// ❌ 用 BigDecimal 代表金额
public class Order {
    private BigDecimal amount;      // 金额
    private String currency;        // 币种——和 amount 分开了！容易造成不一致
}

// 在 Service 里校验
public void pay(Order order, BigDecimal paidAmount, String paidCurrency) {
    if (!order.getAmount().equals(paidAmount)) {  // 金额比较
        throw new RuntimeException("金额不匹配");
    }
    if (!order.getCurrency().equals(paidCurrency)) {  // 币种也得单独比较
        throw new RuntimeException("币种不匹配");
    }
    // 每次都要写两段验证，容易漏
}

// 100 个地方用到金额，散落着 100 段类似的校验代码
// 需求量变更：支持多币种转换 → 噩梦
```

```java
// ✅ 用 Money 值对象
public class Money {
    private final BigDecimal amount;
    private final Currency currency;

    public Money(BigDecimal amount, Currency currency) {
        if (amount == null || currency == null) throw ...;
        if (amount.scale() > currency.getDefaultFractionDigits()) throw ...;
        this.amount = amount;
        this.currency = currency;
    }

    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Money other)) return false;
        return amount.equals(other.amount) && currency == other.currency;
    }

    public Money add(Money other) {
        validateSameCurrency(other);
        return new Money(amount.add(other.amount), currency);
    }
    // 所有金额相关逻辑都在这一个类里
}

// Service 代码变得极其干净
public void pay(Order order, Money paidAmount) {
    if (!order.getTotalAmount().equals(paidAmount)) {  // 一句话搞定
        throw new RuntimeException("支付金额不匹配");
    }
}
```

### 4.3 聚合（Aggregate）

一组关联的对象，作为一个**整体**对外提供访问。聚合有**聚合根**（Aggregate Root），外部只能通过聚合根访问聚合内部的对象。

```
        聚合边界
  ┌──────────────────────────────┐
  │  Order（聚合根）              │
  │   - id: OrderId              │
  │   - userId: UserId           │
  │   - status: OrderStatus      │
  │   - totalAmount: Money       │
  │   - items: List<OrderItem>   │  ← 内部实体，外部不能直接访问
  │   - deliveryAddress: Address │  ← 值对象
  │                              │
  │  OrderItem（内部实体）        │
  │   - productId: ProductId     │
  │   - quantity: int            │
  │   - unitPrice: Money         │
  └──────────────────────────────┘

  外部只能通过 Order（聚合根）操作：
  ✅ order.addItem(productId, quantity, price)
  ❌ orderItem.setQuantity(10)  // 不能绕过聚合根
```

**聚合设计原则：**
1. 聚合内部要保持数据一致性
2. 设计小聚合——能小就不大
3. 通过 ID 引用其他聚合，不要直接引用对象（关联通过 ID）
4. 一次事务只修改一个聚合（最终一致性处理跨聚合操作）

```java
// ✅ 通过 ID 引用其他聚合
public class Order {
    private OrderId id;
    private UserId userId;        // ID引用，不是 User 对象
    private List<OrderItemId> itemIds;  // ID引用
}

// ❌ 直接引用其他聚合
public class Order {
    private User user;            // 容易把聚合边界搞模糊
    private List<OrderItem> items;
}
```

**OOP 深入——聚合就是"最小一致性单元"**

聚合本质上是在回答 OOP 的一个经典问题：**"访问控制做到哪一层？"**

```java
// java.util.List 就是聚合的 OOP 原型
List<String> list = new ArrayList<>();
list.add("a");        // 你直接调 list.add()，不直接调 elementData[0] = "a"
list.remove(0);       // 你直接调 list.remove()，不能绕过 List 直接动底层数组
// List 是聚合根，elementData 是内部元素
// 外部不能越过 List 直接操作内部数组——否则 size 字段就乱了
```

聚合的设计思维和 `List` 封装内部数组是一样的——**你不能绕开聚合根直接修改内部对象，否则内部的不变式就崩溃了**。

**开发场景举例——订单系统的聚合边界到底怎么画：**

场景：一个下单功能，包含 `Order`（订单）、`OrderItem`（订单项）、`Payment`（支付）。

```
方案A：一个大聚合（把 payment 也包进来）  ← ❌ 不好

    Order 聚合（太大）
    ├── Order（根）
    ├── OrderItem[]（内部实体）
    └── Payment  （内部实体）← payment 有自己的生命周期！

    问题：取消订单时需要一起操作 Payment？
          Payment 失败时需要锁住整个 Order？
          两个独立的生命周期被绑在一起，事务范围过大

方案B：两个小聚合（推荐） ← ✅

    Order 聚合               Payment 聚合（独立的！）
    ├── Order（根）          ├── Payment（根）
    ├── OrderItem[]          └── PaymentMethod
    └── deliveryAddress

    Order 只持有 PaymentId  ← 通过 ID 引用另一个聚合
    两个聚合独立演化，各自管理自己的事务
```

**这个设计决策在日常开发中的体现：**

```java
// 一天下午的评审会上：

// "User 表和 Order 表有外键关系，我们在 Order 类里加一个 User user 吧"
// ❌ 不要在聚合里引用其他聚合对象——

// ✅ 正确做法
public class Order {
    private UserId userId;  // 只存 ID
    // 不要 private User user;
}

// 原因很简单：
// 如果你有 order.getUser().getAddress()，那你随时可能把 User 的修改
// 带到 Order 的事务里来，事务越来越长，锁越来越多
// 只存 ID = 明确告诉所有人："我是我，User 是 User，我们通过 ID 认识，仅此而已"
```

### 4.4 领域服务（Domain Service）

当业务逻辑不属于任何一个实体或值对象时，放在领域服务中。领域服务是**无状态的**。

```java
// 转账逻辑涉及两个账户，不属于任何一个实体
public class TransferService {
    public void transfer(Account from, Account to, Money amount) {
        from.debit(amount);
        to.credit(amount);
    }
}
```

| 特征 | 领域服务 | 应用服务 |
|------|----------|----------|
| 包含业务逻辑 | 是 | 否 |
| 状态 | 无状态 | 无状态 |
| 职责 | 协调领域对象完成业务操作 | 事务管理、权限校验、调用领域层 |
| 依赖 | 只依赖领域对象 | 依赖领域服务和仓储 |

> 不要把所有逻辑放领域服务里，否则又退化成"贫血模型 + Service"的老路。

**OOP 深入——领域服务是"无处安放的协作行为"的归宿**

OOP 里学单一职责时，有一个经典困惑：**"转账这个行为属于哪个对象？"**

```java
// 转账操作同时修改两个 Account 的内部状态
// — 塞在 Account A 里？那 A 需要知道 B 的内部结构 → 耦合
// — 塞在 Account B 里？同样的问题
// — 单独写一个 DB 存储过程？那你放弃了 OOP

// OOP 的回答：行为不属于任何已有对象时，做一个新对象来承载
// 这就是领域服务
```

**开发场景举例——认识领域服务 vs 应用服务的区别：**

```java
// 场景：用户下单

// 应用服务（Application Service）——不包含业务逻辑，只管"组装调用"
public class OrderApplicationService {
    @Transactional  // ← 事务管理在应用层
    public void createOrder(CreateOrderCmd cmd) {
        // 1. 权限校验（应用层职责）
        authService.checkPermission(cmd.getUserId(), "CREATE_ORDER");

        // 2. 调领域层做事（应用层自己不写业务规则）
        Order order = Order.create(
            cmd.getUserId(), cmd.getItems(), cmd.getAddress()
        );

        // 3. 保存（应用层协调基础设施）
        orderRepo.save(order);

        // 4. 发通知（应用层协调基础设施）
        notificationService.notify(new OrderCreatedNotification(order));
    }
}
```

```java
// 领域服务（Domain Service）——包含领域逻辑，但不属于实体

// 场景：库存预留——涉及 Order 聚合 + Inventory 聚合的协作
public class InventoryReservationService {
    // 既不放在 Order 里（Order 不应该知道库存规则）
    // 也不放在 Inventory 里（Inventory 不应该知道订单规则）
    // 放在领域服务里，精准地表达了"库存预留"这个领域概念

    public void reserve(Order order, Inventory inventory) {
        for (OrderItem item : order.getItems()) {
            if (!inventory.hasStock(item.getProductId(), item.getQuantity())) {
                throw new InsufficientStockException(item.getProductId());
            }
        }
        for (OrderItem item : order.getItems()) {
            inventory.reserve(item.getProductId(), item.getQuantity());
        }
    }
}
```

**一句话区分：** 应用服务是"导演"（喊 Action，管理场景，但不演戏），领域服务是"配角演员"（演具体的戏，但不是主角实体）。

### 4.5 仓储（Repository）

提供领域对象的持久化和检索，**隐藏数据库细节**，让领域层感觉像是在操作内存集合。

```java
// 接口定义在领域层
public interface OrderRepository {
    Optional<Order> findById(OrderId id);
    List<Order> findByUserId(UserId userId);
    void save(Order order);
    void delete(Order order);
}

// 实现在基础设施层
public class OrderRepositoryImpl implements OrderRepository {
    private final JdbcTemplate jdbc;
    // 具体的数据库操作...
}
```

> 仓储只作用于聚合根——每个聚合根对应一个仓储。

**OOP 深入——仓储模拟的是"内存中的集合"**

仓储（Repository）这个名字的选择很精妙。在 OOP 里你操作内存里的集合是这样的：

```java
// 操作内存集合——直接用 Collection API
List<Order> orders = new ArrayList<>();
orders.add(order);              // 添加
Order o = orders.get(0);        // 通过下标取
orders.removeIf(o -> o.isCanceled());  // 按条件删除

// 操作数据库集合——用 Repository 提供同样的体验
Order o = orderRepo.findById(id);      // 取，像 map.get(key)
orderRepo.save(order);                 // 存，像 list.add()
orderRepo.delete(order);               // 删，像 list.remove()
// 你不需要知道后面是 MySQL 还是 Redis，就像你不需要知道 ArrayList 的内部数组
```

**关键洞察：Repository 不叫 DAO。DAO（Data Access Object）的名字里有"Data"和"Access"，意味着数据库操作；而 Repository 的名字暗示"仓库/库房"，你想存的就放进去，想取的时候拿出来，跟用 `HashMap` 没区别。**

**开发场景举例——为什么接口放领域层、实现放基础设施层：**

```java
// domain/repository/OrderRepository.java —— 领域层定义接口
public interface OrderRepository {
    Optional<Order> findById(OrderId id);
    void save(Order order);
}

// infrastructure/repository/MySqlOrderRepository.java —— 基础设施层实现
// 用了 JPA、MyBatis、JDBC 随便你，领域层完全不知道
public class MySqlOrderRepository implements OrderRepository {
    private final JpaOrderDAO jpaOrderDAO;  // 只在基础设施层依赖 JPA

    @Override
    public Optional<Order> findById(OrderId id) {
        OrderPO po = jpaOrderDAO.findById(id.getValue()).orElse(null);
        if (po == null) return Optional.empty();
        return Optional.of(toDomain(po));  // PO → Domain 转换
    }

    @Override
    public void save(Order order) {
        OrderPO po = toPO(order);          // Domain → PO 转换
        jpaOrderDAO.save(po);
    }
}
```

**为什么这么分？** 因为这样当你决定把 MySQL 换成 PostgreSQL，或者从 JPA 换成 MyBatis——你只写一个新的 `XxxRepositoryImpl`，领域层代码一个字不改。这就是 OOP 里"依赖抽象不依赖具体"在模块级别的落地。

### 4.6 领域事件（Domain Event）

领域中发生的有意义的事情，以事件的形式表达。

```java
// 事件定义
public class OrderPaidEvent {
    private final OrderId orderId;
    private final Money amount;
    private final LocalDateTime paidAt;
}

// 在聚合内部发布事件
public class Order {
    public void pay(Money amount) {
        this.status = OrderStatus.PAID;
        // 发布领域事件
        this.events.add(new OrderPaidEvent(this.id, amount, LocalDateTime.now()));
    }
}

// 事件处理器
public class OrderPaidHandler {
    public void handle(OrderPaidEvent event) {
        // 发送通知、扣减库存等后续操作
    }
}
```

**OOP 深入——领域事件就是观察者模式在领域层的应用**

```java
// GoF 观察者模式：Subject 通知 Observer
button.addActionListener(e -> System.out.println("clicked!"));

// 领域事件：聚合根通知外部系统
order.pay(amount);  // 支付 → 发布 OrderPaidEvent
// → 扣库存系统 收到事件
// → 发短信系统 收到事件
// → 积分系统   收到事件
```

区别在于 OOP 的观察者通常是同步回调，领域事件可以异步、可以落盘（事件溯源）、可以在多个限界上下文之间消费。但核心思想是同一个——**"发生了某件事，让关心这件事的人知道，而不让发生这件事的人知道谁关心"**。

**开发场景举例——领域事件解决的实际问题：**

```java
// 场景：一个用户下单后的处理流程

// ❌ 无事件——下单方法变成大教堂
public class OrderService {
    @Transactional
    public void placeOrder(CreateOrderCmd cmd) {
        Order order = Order.create(cmd);
        orderRepo.save(order);

        // 下单后的一系列操作全耦合在一起
        inventoryService.deduct(order.getItems());   // 扣库存
        couponService.markUsed(cmd.getCouponId());   // 标记优惠券已用
        smsService.send(order.getUserId(), "下单成功"); // 发短信
        pointsService.addPoints(order.getUserId(), 100);  // 加积分
        // 每加一个新需求（比如还要通知数据分析），就要改这个方法
        // 事务越来越长，一个非核心环节挂了，整个下单回滚
    }
}

// ✅ 领域事件——下单方法只管下单
public class Order {
    public void place() {
        this.status = OrderStatus.PLACED;
        this.events.add(new OrderPlacedEvent(this.id, this.userId, this.items));
        // 我只发事件，不管谁来处理
    }
}

// 不同的 Handler 处理不同的事，各自独立
public class InventoryHandler {
    @EventListener
    public void on(OrderPlacedEvent e) { inventoryService.deduct(e.getItems()); }
}
public class CouponHandler {
    @EventListener
    public void on(OrderPlacedEvent e) { couponService.markUsed(e.getCouponId()); }
}
public class SmsHandler {
    @EventListener
    public void on(OrderPlacedEvent e) { smsService.send(e.getUserId(), "下单成功"); }
}
// 加一个新需求？写一个新 Handler，不改 Order
```

---

## 五、分层架构

```
┌──────────────────────────────────────────────┐
│              用户接口层（UI / API）            │
│          Controller、DTO、参数校验             │
├──────────────────────────────────────────────┤
│             应用层（Application）              │
│    应用服务、事务管理、权限校验、用例编排        │
├──────────────────────────────────────────────┤
│              领域层（Domain）                  │
│   Entity、ValueObject、Aggregate             │
│   DomainService、DomainEvent、Repository接口  │
│   ★ 最核心，不依赖任何外部框架                  │
├──────────────────────────────────────────────┤
│           基础设施层（Infrastructure）          │
│  Repository 实现、ORM、消息队列、外部 API 调用  │
└──────────────────────────────────────────────┘
```

**关键原则：领域层是纯 POJO，不依赖 Spring、MyBatis 等框架。** 依赖方向总是从外向内。

### 六边形架构（端口-适配器架构）详解

传统四层架构虽然分层了，但依赖方向容易出问题。六边形架构把"端口"概念显式化：

```
                   ┌─────────────────────────────────────┐
                   │          领域模型（Domain）            │
                   │   Entity · ValueObject · Aggregate  │
                   │       DomainService · Event          │
                   │                                     │
                   │  ★ 完全纯净，不 import 任何框架        │
                   │  ★ 只定义端口接口                     │
                   └────┬────────────────────────┬───────┘
                        │     端口（Port）         │
                        │   领域层定义的接口        │
              ┌─────────┴──────────┐  ┌──────────┴──────────┐
              │   入站适配器        │  │    出站适配器         │
              │  REST Controller   │  │  MySQL Repository    │
              │  gRPC Handler     │  │  Redis Cache        │
              │  MQ Listener      │  │  External API Client│
              │  消息队列消费者     │  │  外部 API 客户端      │
              └────────────────────┘  └─────────────────────┘
                  "谁调用领域"              "领域调用什么"
```

**核心区别对比：**

```
传统三层：                    六边形架构：
Controller →                  端口（接口）← Controller 适配器
    ↓                              ↓
  Service（业务+事务混一起）      领域层（纯业务，定义端口接口）
    ↓                              ↓
   DAO                         端口（接口）← DAO 适配器
```

**OOP 对应——就是 DIP（依赖反转）的架构级应用：**

```java
// 传统：高层依赖低层（违反 DIP）
// domain/OrderService.java  ← 高层策略
import com.mysql.jdbc.Driver;  // ← 居然依赖了具体的数据库驱动！
// 想换个数据库 → 得改业务代码

// 六边形：低层依赖高层（遵循 DIP）
// domain/repository/OrderRepository.java  ← 端口，在领域层定义
public interface OrderRepository {
    Optional<Order> findById(OrderId id);
    void save(Order order);
}

// domain/OrderService.java  ← 只依赖端口（接口）
public class OrderService {
    private final OrderRepository repo;  // 依赖抽象，不依赖具体
}

// infrastructure/MySqlOrderRepository.java  ← 适配器实现端口
// 实现了接口，依赖方向指向领域层
public class MySqlOrderRepository implements OrderRepository {
    // 所有数据库框架的依赖都限制在这个类里
}
```

**为什么叫六边形而不叫四层？** 四层架构的隐含假设是"上面调下面"，容易让人写出领域层依赖 DAO 层的代码。六边形在画法上就把领域放中间、所有外部依赖都通过端口接入，强调的是**"里面不依赖外面，外面依赖里面"**。

### 代码目录结构示例

```
order/
├── application/          # 应用层
│   ├── OrderApplicationService.java
│   └── dto/
│       └── CreateOrderCmd.java
├── domain/               # 领域层（核心）
│   ├── model/
│   │   ├── Order.java            # 聚合根
│   │   ├── OrderItem.java        # 内部实体
│   │   ├── OrderStatus.java      # 枚举
│   │   └── valueobject/
│   │       ├── OrderId.java
│   │       ├── Money.java
│   │       └── Address.java
│   ├── service/
│   │   └── OrderDomainService.java
│   ├── event/
│   │   └── OrderCreatedEvent.java
│   └── repository/
│       └── OrderRepository.java  # 接口
└── infrastructure/       # 基础设施层
    ├── repository/
    │   └── OrderRepositoryImpl.java
    └── mapper/
        └── OrderMapper.java
```

---

## 六、常用战术模式详解

### 6.1 工厂（Factory）

当对象的创建逻辑很复杂时，把创建逻辑封装在工厂里，而不是散落在各处。

**OOP 对应——工厂方法模式和抽象工厂模式**。GoF 的工厂模式在 DDD 里被用来创建复杂的领域对象（尤其是聚合）。

**开发场景举例——创建聚合什么时候需要工厂：**

```java
// ❌ 创建订单的逻辑散落在多个地方
// Controller 里
Order order = new Order();
order.setId(OrderId.next());
order.setUserId(cmd.getUserId());
order.setStatus(OrderStatus.PENDING);
order.setCreatedAt(LocalDateTime.now());
// 需要初始化一个订单号、初始化订单项、计算总额...
// 这段代码在 Controller、Service、MQ Listener 里到处复制

// Service 里又来一遍
Order order2 = new Order();
order2.setId(OrderId.next());
// ... 又一遍
```

```java
// ✅ 工厂统一创建逻辑
public class OrderFactory {
    public static Order create(UserId userId, List<OrderItemReq> itemReqs,
                                Address address) {
        // 所有初始化逻辑集中
        OrderId id = OrderId.next();
        List<OrderItem> items = itemReqs.stream()
            .map(req -> new OrderItem(
                OrderItemId.next(),
                req.getProductId(),
                req.getQuantity(),
                req.getUnitPrice()
            ))
            .toList();
        Money total = items.stream()
            .map(OrderItem::getSubtotal)
            .reduce(Money.ZERO, Money::add);

        return new Order(id, userId, items, total, address, OrderStatus.PENDING);
    }

    // 还可以提供不同场景的工厂方法
    public static Order createFromTemplate(OrderTemplate template, UserId userId) {
        // 从模板创建订单的逻辑
    }
}
```

**什么时候需要工厂？什么时候直接用构造函数？**

| 用构造函数 | 用工厂 |
|-----------|--------|
| 对象简单，就几个属性 | 对象复杂，涉及多个内部对象的创建 |
| 不需要任何计算/转换 | 创建时需要计算 (如汇总金额) |
| 只有一个创建方式 | 有多种创建方式 (模板创建、复制创建等) |

### 6.2 规格（Specification）

将业务规则封装成可组合的对象，替代 DAO 层里一堆 `findByXxxAndYyyAndZzz` 方法。

**OOP 对应——策略模式 + 组合模式**。做一个"条件对象"，它承载"什么东西满足什么条件"的含义，而不是在 SQL 里拼 AND。

**开发场景举例——查询条件的组合爆炸：**

```java
// ❌ DAO 里的查询方法爆炸
public interface OrderRepository {
    List<Order> findByUserId(Long userId);
    List<Order> findByUserIdAndStatus(Long userId, String status);
    List<Order> findByUserIdAndStatusAndAmountGreaterThan(Long userId, String status, BigDecimal amount);
    List<Order> findByStatusAndCreatedAtBetween(String status, LocalDateTime from, LocalDateTime to);
    // ... 无穷无尽的组合，每来一个新需求就加一个新方法
}
```

```java
// ✅ Specification：规则封装为对象，可自由组合
public interface Specification<T> {
    boolean isSatisfiedBy(T candidate);  // 判断对象是否满足规格
    Specification<T> and(Specification<T> other);
    Specification<T> or(Specification<T> other);
    Specification<T> not();
}

public class OrderStatusSpec implements Specification<Order> {
    private final OrderStatus status;
    public boolean isSatisfiedBy(Order order) {
        return order.getStatus() == this.status;
    }
}

public class OrderAmountSpec implements Specification<Order> {
    private final Money minAmount;
    public boolean isSatisfiedBy(Order order) {
        return order.getTotalAmount().compareTo(minAmount) >= 0;
    }
}

// 使用时自由组合——不用再加新方法
Specification<Order> spec = new OrderStatusSpec(OrderStatus.PAID)
    .and(new OrderAmountSpec(new Money(100, CNY)))
    .and(order -> order.getCreatedAt().isAfter(yesterday));  // 甚至可以用 lambda

List<Order> result = orderRepo.findAll().stream()
    .filter(spec::isSatisfiedBy)
    .toList();
```

> 注意：上面的 `filter` 是内存过滤，适用于数据量小的场景。数据量大时需要把 Specification 翻译成 SQL WHERE 条件（即"规格模式的数据库实现"），但核心思想没变——用组合替代 N 个方法。

### 6.3 其他模式速查

| 模式 | 职责 | 关键点 | OOP 对应 |
|------|------|--------|----------|
| **Strategy** | 封装可替换的算法 | 不同商品类型的折扣计算 | GoF 策略模式直接复用 |
| **Anti-Corruption Layer** | 隔离外部系统 | 对接老系统、第三方 API（见 3.3 节详细示例） | GoF 适配器模式的系统级应用 |

---

## 七、DDD 不是银弹

### 适合 DDD
- 业务逻辑复杂的系统（电商、金融、供应链）
- 团队能与业务专家紧密沟通
- 核心价值在领域逻辑，而不是纯 CRUD

### 不适合 DDD
- 简单的 CRUD 系统（后台管理、数据报表）
- 技术密集型项目（算法引擎、中间件）
- 团队对业务理解不足、沟通成本高

### 常见误区

1. **为 DDD 而 DDD** ——一个简单管理系统硬套聚合、事件，过度设计
2. **追求代码完美，忘记业务** ——DDD 的目的是解决业务复杂，不是写优雅代码
3. **把所有对象都搞成 Entity** ——很多对象应该是 ValueObject
4. **聚合太大** ——一个大聚合包罗万象，事务范围太大，性能差
5. **Service 太重** ——逻辑全在 Service 里，Entity 又变回贫血模型

---

## 八、一句话总结

> DDD 的本质：**把业务专家脑子里的领域知识，直接翻译成代码中的领域模型**。战术模式（Entity、ValueObject、Aggregate）是手段，战略设计（Bounded Context、通用语言）是前提。
