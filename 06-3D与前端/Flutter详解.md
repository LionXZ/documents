# Flutter 详解

> 一份通俗易懂的 Flutter 文档，从零开始到实战场景，每个知识点都有可运行的代码示例。

---

## 目录

- [1. 基础概念](#1-基础概念)
- [2. 环境搭建](#2-环境搭建)
- [3. Dart 语言详解](#3-dart-语言详解)
- [4. Widget 基础](#4-widget-基础)
- [5. 布局体系](#5-布局体系)
- [6. 交互与表单](#6-交互与表单)
- [7. 状态管理](#7-状态管理)
- [8. 路由与导航](#8-路由与导航)
- [9. 动画](#9-动画)
- [10. 网络与数据](#10-网络与数据)
- [11. 实用技能](#11-实用技能)
- [12. 实战场景](#12-实战场景)
- [13. 常见问题排查](#13-常见问题排查)
- [14. 速查卡片](#14-速查卡片)
- [15. Widget 属性速查](#15-widget-属性速查)

---

## 1. 基础概念

### Flutter 是什么？

Flutter 是 Google 推出的**开源 UI 框架**，使用 Dart 语言开发，可以用**一套代码**构建 iOS、Android、Web、Windows、macOS、Linux 应用。

它最大的特点是**自绘引擎**：不使用平台原生控件，而是自己接管每一个像素的绘制（Skia / Impeller 渲染引擎），所以在不同平台上表现完全一致，不受系统版本差异影响。

### 核心概念

| 概念 | 说明 | 类比 |
|------|------|------|
| **Widget（组件）** | UI 的配置描述，不可变 | 菜谱（写明怎么做） |
| **Element（元素）** | Widget 在树中的实例，管理生命周期 | 厨师（按菜谱做菜的人） |
| **RenderObject（渲染对象）** | 真正负责布局和绘制 | 炉灶（实际干活） |
| **State（状态）** | 可变的数据，变化时触发界面重建 | 食材库存（会变化） |
| **BuildContext（上下文）** | Element 的引用，用于查找祖先/推送路由 | 厨师的工牌（身份凭证） |
| **Scaffold（脚手架）** | 页面骨架：AppBar + 内容 + 底部导航 | 房间的毛坯结构 |

### 一切皆 Widget

Flutter 的核心设计哲学：**组合优于继承**。界面不是靠一个巨型控件拼出来的，而是像乐高一样由无数小 Widget 套娃组合而成：

```
MaterialApp                  ← 应用根
 └── Scaffold                ← 页面骨架
      ├── AppBar             ← 顶部栏（本身也是一堆 Widget 组合）
      │    └── Text          ← 标题文字
      └── Center             ← 居中容器
           └── Column        ← 垂直布局
                ├── Text     ← 文字
                └── ElevatedButton  ← 按钮
```

连内边距（Padding）、居中（Center）、手势（GestureDetector）都是 Widget。

### 三棵树

Flutter 界面由三棵并行的树构成，理解它们就理解了 Flutter 的渲染机制：

```
Widget 树          Element 树          RenderObject 树
（配置说明书）  →   （实例/生命周期） →   （布局与绘制）
  不可变              可复用              真正干活
```

- **Widget 树**：每次 `setState` 后 `build()` 返回一棵**全新**的 Widget 树（Widget 轻量，重建成本极低）
- **Element 树**：Flutter 对比新旧 Widget 树（同一位置、同类型 → 复用 Element），是连接配置与渲染的桥梁
- **RenderObject 树**：只有真正需要布局绘制的地方才存在，布局变化时只做增量更新

> 类比：Widget 是图纸，Element 是工地，RenderObject 是大楼。改图纸（重建 Widget）很快，真正改建大楼（重排 RenderObject）才昂贵——Flutter 用 Diff 算法把改建次数降到最少。

### 与其他方案对比

| 方案 | 渲染方式 | 语言 | 性能 | 一致性 |
|------|---------|------|------|--------|
| **Flutter** | 自绘引擎，接管所有像素 | Dart | 接近原生 | 各平台完全一致 |
| React Native | 调用平台原生控件 | JavaScript | 有 JS 桥接开销 | 各平台外观有差异 |
| 原生开发 | 平台各自控件 | Kotlin/Swift | 最优 | 各平台需分别开发 |
| H5 混合 | WebView 渲染 | HTML/JS | 最弱 | 一致但体验差 |

### Dart 为什么快

Dart 同时支持两种编译模式：

- **JIT（即时编译）**：开发时使用，支持**热重载**（改代码 1 秒内看到效果，保留状态）
- **AOT（提前编译）**：发布时编译为机器码，启动快、运行流畅，没有 JS 那样的解释开销

---

## 2. 环境搭建

### 方式 1：官网 SDK 安装（通用）

```bash
# macOS 使用 Homebrew（推荐）
brew install --cask flutter

# 或手动下载 SDK，解压后配置 PATH
# 下载地址：https://docs.flutter.cn/get-started/install
```

安装完成后运行体检命令，它会告诉你缺什么：

```bash
flutter doctor

# 典型输出：
# [✓] Flutter (Channel stable, 3.x.x)
# [✓] Android toolchain
# [✓] Xcode - develop for iOS and macOS
# [!] Android Studio（缺插件会有提示）
# [✓] Chrome
```

### 方式 2：VS Code（轻量推荐）

1. 安装 VS Code
2. 扩展商店搜索安装 **Flutter** 插件（会自动带上 Dart 插件）
3. `Cmd + Shift + P` → `Flutter: New Project` 即可创建项目

### 方式 3：Android Studio（功能最全）

1. 安装 Android Studio（自带 Android SDK 和模拟器管理）
2. Plugins 中安装 **Flutter** 插件
3. `New → New Flutter Project`

### 创建并运行第一个项目

```bash
# 创建项目（org 是 iOS/Android 的包标识，按需修改）
flutter create hello_flutter
cd hello_flutter

# 查看可用设备
flutter devices

# 运行（连接手机/模拟器后）
flutter run

# 运行到 Chrome
flutter run -d chrome

# 运行到指定设备（从 flutter devices 列表里选 id）
flutter run -d iphone
```

运行后进入交互模式，**这三个快捷键必会**：

| 按键 | 作用 | 说明 |
|------|------|------|
| `r` | 热重载 | 保留状态，秒级看到改动（最常用） |
| `R` | 热重启 | 保留状态的改动失效时使用（如改了 main()） |
| `q` | 退出 | 结束调试 |

### 项目结构逐文件解析

```
hello_flutter/
├── lib/                    ← ★ 你 99% 的代码都在这里
│   └── main.dart           ← 入口文件
├── android/                ← Android 原生工程（一般不动）
├── ios/                    ← iOS 原生工程（一般不动）
├── web/                    ← Web 工程（一般不动）
├── test/                   ← 单元测试
├── pubspec.yaml            ← ★ 依赖与资源清单（等于 package.json）
├── analysis_options.yaml   ← 代码规范配置（默认内置 flutter_lints）
└── README.md
```

pubspec.yaml 是项目的"身份证"：

```yaml
name: hello_flutter        # 包名
description: 我的第一个 Flutter 应用

environment:
  sdk: ^3.5.0              # Dart SDK 版本要求

dependencies:              # 运行时依赖
  flutter:
    sdk: flutter
  http: ^1.2.0             # 第三方包（写完运行 flutter pub get）

dev_dependencies:          # 开发期依赖（测试/lint）
  flutter_test:
    sdk: flutter
  flutter_lints: ^4.0.0

flutter:                   # Flutter 专属配置
  uses-material-design: true
  assets:                  # 资源文件声明（图片/字体等）
    - assets/images/
```

### main.dart 最小结构

```dart
// lib/main.dart —— 入口文件
import 'package:flutter/material.dart'; // Material 设计风格的组件库

void main() {
  runApp(const MyApp()); // runApp：把根 Widget 挂载到屏幕上
}

// 应用根 Widget
class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    // MaterialApp：Material 风格应用的壳（管路由/主题/国际化）
    return MaterialApp(
      title: '我的应用',
      theme: ThemeData(primarySwatch: Colors.blue), // 全局主题色
      home: const HomePage(), // 首页
    );
  }
}

// 首页 Widget
class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    // Scaffold：页面骨架（AppBar + body）
    return Scaffold(
      appBar: AppBar(title: const Text('首页')),
      body: const Center(child: Text('Hello Flutter')),
    );
  }
}
```

---

## 3. Dart 语言详解

Dart 是一门**强类型、支持空安全**的现代语言，语法对有 Java/JavaScript/TypeScript 基础的人非常友好。本章覆盖 Flutter 开发中用到的全部核心语法。

### 3.1 变量与常量

```dart
// var：类型自动推断，推断之后类型不可变
var name = '小明';        // 推断为 String
var age = 18;             // 推断为 int

// 显式声明类型（团队协作推荐，类型一目了然）
String city = '北京';
double price = 9.9;

// final：运行时常量（赋值后不可改，可以运行时才确定值）
final now = DateTime.now();

// const：编译期常量（编译时就要确定值，性能更好）
const double pi = 3.14159;
const List<String> colors = ['红', '绿']; // const 集合内容也不可改

// final 与 const 的核心区别：
final listA = [1, 2];  // ✅ 可以 listA.add(3)，引用不可变但内容可变
const listB = [1, 2];  // ❌ listB.add(3) 报错，内容也冻结了
```

| 关键字 | 赋值次数 | 确定时机 | 集合内容 | 使用建议 |
|--------|---------|---------|---------|---------|
| `var` | 1 次 | 运行时 | 可变 | 局部变量偷懒用 |
| `final` | 1 次 | 运行时 | 可变 | **默认首选** |
| `const` | 1 次 | 编译期 | 不可变 | 编译期就能确定的值 |

### 3.2 内置类型

```dart
// 数值：num / int / double
int count = 10;
double score = 88.5;
int hex = 0xFF;              // 十六进制
double exp = 1.2e3;          // 科学计数法 = 1200.0
print(10.isEven);            // true —— int 自带很多实用方法
print(3.14159.toStringAsFixed(2)); // "3.14" 保留两位小数

// 字符串
String s1 = '单引号';
String s2 = "双引号";
String s3 = '''              // 三引号：多行字符串
第一行
第二行
''';
// 插值表达式：$变量 或 ${表达式}
String msg = '我是 $name，明年 ${age + 1} 岁';

// 布尔（严格布尔：条件必须是 bool，不存在 JS 的 truthy/falsy）
bool isVip = true;
// if (name) {}  ❌ 报错！字符串不能直接当条件

// List（列表，即数组）
List<String> fruits = ['苹果', '香蕉'];
fruits.add('橘子');
print(fruits[0]);            // 苹果
print(fruits.length);        // 3

// Set（集合，自动去重）
Set<int> ids = {1, 2, 2, 3}; // 实际是 {1, 2, 3}

// Map（键值对）
Map<String, int> scores = {'语文': 90, '数学': 95};
scores['英语'] = 88;
print(scores['语文']);       // 90
print(scores['体育']);       // null（不存在返回 null）
```

### 3.3 函数

Dart 函数的参数是所有语言里设计得最舒服的之一，**Flutter 的 Widget 参数全是命名参数**，必须掌握：

```dart
// 基础函数（可省略类型，但建议写全）
int add(int a, int b) {
  return a + b;
}

// 箭头函数：函数体只有一句时的简写（Flutter 里到处都是）
int add2(int a, int b) => a + b;

// —— 可选位置参数 [ ]：按顺序传，用方括号 ——
String greet(String name, [String? title]) {
  return title == null ? '你好，$name' : '你好，$title$name';
}
greet('张三');              // 你好，张三
greet('张三', '张教授');     // 你好，张教授张三

// —— 命名参数 { }：传参时必须写参数名（Flutter Widget 全是这种）——
void createUser({required String name, int age = 18}) {
  // required：必传；否则就是可选；= 默认值
  print('$name / $age');
}
createUser(name: '李四');            // 李四 / 18
createUser(name: '王五', age: 20);   // 王五 / 20

// 匿名函数 + 立即赋值（回调写法）
var multiply = (int a, int b) => a * b;
print(multiply(3, 4));      // 12

// 闭包：函数可以捕获外部变量（Flutter 状态管理的基础）
Function makeCounter() {
  int count = 0;
  return () => ++count;     // 返回的函数一直持有 count
}
var counter = makeCounter();
counter(); // 1
counter(); // 2 —— count 被闭包记住了
```

| 参数形式 | 语法 | 调用方式 | 典型场景 |
|---------|------|---------|---------|
| 位置参数 | `f(a, b)` | 按顺序传 | 工具函数 |
| 可选位置参数 | `f(a, [b])` | 按顺序、可省略 | 少用 |
| **命名参数** | `f({a, b})` | `f(a: 1, b: 2)` | **Flutter Widget** |
| 必填命名参数 | `f({required a})` | 必须写 `f(a: 1)` | Widget 必填项 |

### 3.4 类与对象

```dart
// —— 基础类 ——
class Person {
  // 成员变量（未初始化的非空字段必须在构造函数里赋值）
  String name;
  int age;

  // 传统写法：this.name = name（Java 风格）
  // Dart 简写：构造参数直接给字段赋值
  Person(this.name, this.age);

  // 命名构造函数：一个类可以有多个构造函数
  Person.guest() : name = '游客', age = 0;

  // getter：像字段一样访问的方法
  bool get isAdult => age >= 18;

  // 普通方法
  String introduce() => '我是 $name，$age 岁';
}

var p = Person('赵六', 25);
print(p.isAdult);                 // true —— getter 不用加括号
print(Person.guest().introduce()); // 我是 游客，0 岁

// —— 初始化列表：构造函数体执行前先初始化变量 ——
class Rect {
  final int area;
  Rect(int w, int h) : area = w * h; // area 是 final，只能在这里算
}

// —— factory 工厂构造函数：不必须创建新实例（单例/缓存常用）——
class Logger {
  static Logger? _instance;
  factory Logger() => _instance ??= Logger._internal();
  Logger._internal(); // 私有构造函数（下划线开头 = 私有）
}

// —— 级联调用 ..：对同一对象连续操作 ——
var list = <int>[]
  ..add(1)
  ..add(2)
  ..add(3);   // 等价于 add 三次，不用反复写 list.
```

### 3.5 继承、抽象类、接口与 Mixin

```dart
// —— 继承 extends + super ——
class Animal {
  void breathe() => print('呼吸');
}
class Dog extends Animal {
  void bark() => print('汪汪');
}
var dog = Dog();
dog.breathe(); // 继承来的
dog.bark();    // 自己的

// —— 抽象类 abstract：规定子类必须实现什么（不能被实例化）——
abstract class Shape {
  double getArea();              // 抽象方法：只有签名没有实现
  void describe() => print('面积是 ${getArea()}'); // 可以有具体方法
}
class Circle extends Shape {
  final double r;
  Circle(this.r);
  @override
  double getArea() => 3.14159 * r * r; // 必须实现抽象方法
}

// Dart 里没有 interface 关键字——每个类都隐式是接口
class Cat implements Animal {   // implements：全量重写，不复用实现
  @override
  void breathe() => print('猫在呼吸');
}

// —— Mixin：横向复用能力（Flutter 的 vsync、主题查找都靠它）——
mixin Flyable {
  void fly() => print('飞起来了');
}
mixin Swimmable {
  void swim() => print('游起来了');
}
// with 可以混入多个能力，解决"单继承不够用"
class Duck extends Animal with Flyable, Swimmable {}

Duck().fly();   // 飞起来了
Duck().swim();  // 游起来了
```

| 机制 | 关键字 | 特点 | 类比 |
|------|--------|------|------|
| 继承 | `extends` | 单继承，复用父类实现 | 亲儿子（继承家产） |
| 接口 | `implements` | 只要声明，实现全自己写 | 签合同（必须履约） |
| 混入 | `with` | 可混入多个，横向加能力 | 技能包（装了就能用） |

### 3.6 泛型

```dart
// 泛型：类型参数化，写一次容器适配所有类型
class Box<T> {
  final T value;
  Box(this.value);
}
var box = Box<String>('手机');   // T 被指定为 String
// box.value.length ✅ 有类型提示
// box.value + 1    ❌ 编译期就报错

// 泛型约束：限定 T 必须是什么
class Comparer<T extends Comparable<T>> {
  T max(T a, T b) => a.compareTo(b) > 0 ? a : b;
}

// 泛型方法
T firstOrDefault<T>(List<T> list, T defaultValue) =>
    list.isEmpty ? defaultValue : list.first;
```

### 3.7 集合的函数式操作（Flutter 高频）

Flutter 开发中处理列表数据基本不用 for 循环，全部使用集合管道：

```dart
List<int> numbers = [3, 1, 4, 1, 5, 9, 2, 6];

// map：一对一转换（for + push 的替代品）
var doubled = numbers.map((n) => n * 2).toList();
// [6, 2, 8, 2, 10, 18, 4, 12]

// where：过滤（for + if + push 的替代品）
var evens = numbers.where((n) => n.isEven).toList();
// [4, 2, 6]

// reduce：两两合并成一个值
int sum = numbers.reduce((a, b) => a + b);  // 31

// fold：带初始值的 reduce（结果类型可以不同）
int total = numbers.fold(100, (acc, n) => acc + n); // 131

// 组合管道：先过滤再转换再取前 3 个
var top3 = numbers
    .where((n) => n > 2)          // [3, 4, 5, 9, 6]
    .map((n) => '编号$n')          // [编号3, 编号4, 编号5, 编号9, 编号6]
    .take(3)                       // 取前 3 个
    .toList();

// 其他常用
numbers.contains(9);          // 是否包含
numbers.indexOf(4);           // 下标
numbers.any((n) => n > 8);    // 任一满足
numbers.every((n) => n > 0);  // 全部满足
[1, 2, 3].join('-');          // "1-2-3"
```

### 3.8 空安全（Null Safety）★ 重点

Dart 从 2.12 起强制空安全：**类型默认不可空**，这从语言层面消灭了空指针崩溃。

```dart
String name = '小明';
// name = null;  ❌ 编译报错！String 类型不能装 null

// —— 可空类型：类型后面加 ? ——
String? nickname;              // 声明时不初始化，默认 null

// 使用可空变量前必须处理，编译器强制你思考 null：

// 方式 1：?. 条件访问（为 null 时整个表达式是 null，不崩溃）
print(nickname?.length);       // null（不会报错）

// 方式 2：?? 空值合并（为 null 时取后面的默认值）
print(nickname ?? '未设置');    // 未设置

// 方式 3：! 断言非空（你确定不为 null，骗编译器；错了运行时崩溃）
print(nickname!.length);       // ⚠️ 此处 nickname 为 null 会抛异常，慎用

// 方式 4：if 判空后自动提升类型
if (nickname != null) {
  print(nickname.length);      // ✅ 这里自动被识别为非空 String
}

// late：延迟初始化的非空变量（先声明后赋值）
class HomeState extends State {
  late final String title;     // 承诺：使用前一定会赋值
  @override
  void initState() {
    super.initState();
    title = '首页';             // 在生命周期里才赋值
  }
}

// ?.. 空安全级联
Path? path;
path?..moveTo(0, 0)..lineTo(1, 1); // path 为 null 时整条链跳过
```

| 语法 | 名称 | 作用 |
|------|------|------|
| `String?` | 可空类型 | 允许装 null |
| `?.` | 条件访问 | null 时不崩溃，返回 null |
| `??` | 空值合并 | null 时给默认值 |
| `??=` | 空值赋值 | 为 null 才赋值 |
| `!` | 非空断言 | 强制当非空用（危险） |
| `late` | 延迟初始化 | 承诺之后会赋值 |

### 3.9 异步编程（Flutter 高频）★ 重点

网络请求、文件读写、数据库操作全是异步，这是 Flutter 开发的命脉。

```dart
import 'dart:async';

// —— Future：一次性的异步结果（相当于 JS 的 Promise）——
Future<String> fetchUserName() async {
  // 模拟网络延迟
  await Future.delayed(const Duration(seconds: 2));
  return '张三';
}

// —— async/await：用同步的写法写异步 ——
void load() async {
  print('开始加载');
  String name = await fetchUserName(); // 等待结果，但不阻塞界面
  print('拿到结果：$name');
}

// —— Future 链式（不使用 await 时）——
fetchUserName()
    .then((name) => print('成功：$name'))
    .catchError((e) => print('失败：$e'))
    .whenComplete(() => print('完成（无论成败）'));

// —— 并发等待多个 Future ——
Future.wait([fetchUserName(), fetchUserName()]).then((results) {
  print(results); // [张三, 张三] 两个都完成后拿到列表
});

// —— 超时控制 ——
fetchUserName().timeout(
  const Duration(seconds: 5),
  onTimeout: () => throw TimeoutException('请求超时'),
);

// —— Stream：持续多次的异步数据流（相当于 JS 的事件/可观察对象）——
Stream<int> countDown(int from) async* {
  // async* 生成器函数：yield 吐出一个个值
  for (var i = from; i > 0; i--) {
    await Future.delayed(const Duration(seconds: 1));
    yield i; // 每秒吐出一个数字
  }
}

void listen() {
  countDown(3).listen(
    (value) => print('倒计时：$value'), // 每收到一个值触发
    onDone: () => print('完成'),
    onError: (e) => print('出错'),
  );
}
```

| 概念 | 对应 JS 概念 | 产出次数 | 典型场景 |
|------|-------------|---------|---------|
| `Future` | `Promise` | 1 次 | HTTP 请求、读文件 |
| `Stream` | `EventEmitter` | N 次 | WebSocket、监听输入框、滚动位置 |
| `async/await` | `async/await` | — | 消除回调地狱 |
| `async*` + `yield` | generator | N 次 | 产生 Stream |

> 在 Flutter 里，Future 用 `FutureBuilder` 渲染、Stream 用 `StreamBuilder` 渲染（见第 10 章）。

### 3.10 异常处理

```dart
try {
  var result = await fetchData();
} on FormatException catch (e) {
  // 精确捕获特定类型异常
  print('数据格式错误：$e');
} on TimeoutException {
  print('超时了');
} catch (e, stack) {
  // e 是异常对象，stack 是调用栈
  print('未知错误：$e');
  print(stack);
} finally {
  // 无论如何都执行（隐藏 loading 等）
  hideLoading();
}

// 主动抛异常
throw ArgumentError('参数不能为空');
```

### 3.11 实用语法糖

```dart
// 展开运算符 ...（组合 Widget 列表时极其高频）
var baseWidgets = [const Text('标题'), const Text('副标题')];
var allWidgets = [
  ...baseWidgets,               // 展开塞入
  ...?optionalWidgets,          // 可空展开（null 时跳过）
  const Text('结尾'),
];

// is 类型判断 / as 类型强转
if (user is Admin) {
  print(user.adminLevel);  // is 判断后自动类型提升
}
var a = user as Admin;     // 强转（转错崩溃，优先用 is）

// ??= 空值赋值
String? token;
token ??= 'abc';  // token 是 null 才赋值

// extension 扩展方法：给已有类型加方法（不改动源码）
extension PriceFormat on double {
  String get yuan => '¥${toStringAsFixed(2)}';
}
print(9.9.yuan);  // ¥9.90
```

---

## 4. Widget 基础

### StatelessWidget vs StatefulWidget

Flutter 里所有 Widget 分两大类，这是第一个必须搞清的概念：

| 对比项 | StatelessWidget（无状态） | StatefulWidget（有状态） |
|--------|--------------------------|------------------------|
| 界面是否随数据变化 | ❌ 创建后不再变化 | ✅ 数据变了自动刷新界面 |
| 有无 State 对象 | 无 | 有（数据存放在 State 里） |
| build 调用时机 | 只在插入树时调用一次 | initState / setState 后调用 |
| 性能开销 | 更低 | 稍高 |
| 典型场景 | 纯展示（Text、Icon、卡片） | 计数器、开关、输入框、需要交互 |

```dart
// 无状态：数据写死或从外部传入，传入什么显示什么
class GreetingCard extends StatelessWidget {
  final String name;              // 外部传入，构造后不可变
  const GreetingCard({super.key, required this.name});

  @override
  Widget build(BuildContext context) {
    return Text('你好，$name');
  }
}

// 有状态：内部数据变化时界面跟着变
class Counter extends StatefulWidget {
  const Counter({super.key});

  @override
  State<Counter> createState() => _CounterState(); // 创建状态对象
}

class _CounterState extends State<Counter> {
  // ★ 状态（会变的数据）定义在这里，不定义在 Widget 里
  int count = 0;

  void _increment() {
    setState(() {          // ★ setState：修改数据 + 通知 Flutter 重新 build
      count++;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text('点击了 $count 次'),   // count 变化后这里自动更新
        ElevatedButton(
          onPressed: _increment,    // 按钮点击回调
          child: const Text('加一'),
        ),
      ],
    );
  }
}
```

> 类比：StatelessWidget 是**照片**（拍完定格），StatefulWidget 是**直播**（数据流变化，画面跟着变）。

### StatefulWidget 生命周期 ★ 必会

```
创建 Widget
    │
    ▼
createState() ──────→ 创建 State 对象
    │
    ▼
initState() ───────── ★ 初始化：只执行一次（发请求、开定时器、控制器初始化）
    │
    ▼
didChangeDependencies() ── 依赖变化时（如主题/语言切换、首次也会执行）
    │
    ▼
build() ──────────── ★ 构建界面（会被调用多次，必须纯粹、廉价）
    │                     │
    │                     ▼ setState() 后回到 build
    ▼
didUpdateWidget() ─── 父组件重建并传了新参数时
    │
    ▼
deactivate() ──────── 被移出树时（可能被复用，不一定销毁）
    │
    ▼
dispose() ─────────── ★ 销毁：只执行一次（取消订阅、销毁控制器、关定时器）
```

```dart
class _DemoState extends State<Demo> with SingleTickerProviderStateMixin {
  late final AnimationController _controller;

  @override
  void initState() {
    super.initState();          // 永远第一行调用 super
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 1),
    );
    fetchData();                // 网络请求放这里，不放 build 里
  }

  @override
  void dispose() {
    _controller.dispose();      // ★ 和 initState 成对出现，防止内存泄漏
    super.dispose();            // 永远最后一行调用 super
  }

  @override
  Widget build(BuildContext context) {
    // build 必须纯粹：不要在这里发请求/开定时器/写耗时逻辑
    return const SizedBox();
  }
}
```

### 文本与样式

```dart
// Text：必会的参数
const Text(
  '重要通知',
  style: TextStyle(
    fontSize: 24,               // 字号
    fontWeight: FontWeight.bold,// 粗细
    color: Colors.red,          // 颜色
    letterSpacing: 2,           // 字间距
    decoration: TextDecoration.underline, // 下划线
    height: 1.5,                // 行高（字号倍数）
  ),
  textAlign: TextAlign.center,  // 对齐
  maxLines: 2,                  // 最多 2 行
  overflow: TextOverflow.ellipsis, // 超出显示省略号
)

// RichText：一段文字多种样式
const Text.rich(
  TextSpan(
    text: '原价 ¥99，',
    children: [
      TextSpan(
        text: '限时 ¥9.9',
        style: TextStyle(color: Colors.red, fontWeight: FontWeight.bold),
      ),
    ],
  ),
)
```

### 图片

```dart
// 网络图片
Image.network(
  'https://example.com/avatar.png',
  width: 100,
  height: 100,
  fit: BoxFit.cover,        // 填充模式：cover 剪裁填满 / contain 完整显示
  loadingBuilder: (ctx, child, progress) =>
      progress == null ? child : const CircularProgressIndicator(),
  errorBuilder: (ctx, error, stack) => const Icon(Icons.error), // 加载失败占位
)

// 本地资源图片（需先在 pubspec.yaml 的 assets 声明）
Image.asset('assets/images/logo.png')

// CircleAvatar：圆形头像（内部自动裁剪成圆）
const CircleAvatar(
  radius: 30,               // 半径
  backgroundImage: NetworkImage('https://example.com/a.png'),
)

// FadeInImage：占位图 + 淡入过渡
FadeInImage.assetNetwork(
  placeholder: 'assets/images/placeholder.png',
  image: 'https://example.com/photo.png',
)
```

| BoxFit 值 | 效果 | 类比 CSS |
|-----------|------|---------|
| `cover` | 填满容器，可能裁剪 | `cover` |
| `contain` | 完整显示，可能留白 | `contain` |
| `fill` | 拉伸变形填满 | `fill` |
| `fitWidth` / `fitHeight` | 宽/高撑满 | — |
| `scaleDown` | 像 contain 但不放大 | `scale-down` |

### 图标

```dart
// Material 图标库内置 1000+ 图标，直接用
const Icon(Icons.favorite, size: 32, color: Colors.red)      // 爱心
const Icon(Icons.shopping_cart)                              // 购物车
const Icon(Icons.arrow_back_ios_new, size: 16)               // 返回箭头

// 带文字的图标按钮
IconButton(
  icon: const Icon(Icons.thumb_up),
  onPressed: () => print('点赞'),
)
```

### 按钮家族

```dart
// 三大标准按钮（onPressed 为 null 时按钮自动置灰禁用）
ElevatedButton(                 // 悬浮按钮：强调操作
  onPressed: () {},
  style: ElevatedButton.styleFrom(
    backgroundColor: Colors.blue,
    foregroundColor: Colors.white,
    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
  ),
  child: const Text('提交'),
)

TextButton(                     // 文字按钮：低强调
  onPressed: () {},
  child: const Text('查看详情'),
)

OutlinedButton(                 // 描边按钮：中强调
  onPressed: () {},
  child: const Text('取消'),
)

IconButton(                     // 纯图标按钮
  icon: const Icon(Icons.close),
  onPressed: () {},
)

FloatingActionButton(           // 悬浮操作按钮（配合 Scaffold）
  onPressed: () {},
  child: const Icon(Icons.add),
)
```

| 按钮 | 外观 | 使用场景 |
|------|------|---------|
| ElevatedButton | 有背景有阴影 | 主操作（提交/保存） |
| FilledButton | 有背景无阴影 | 主操作（Material 3 推荐） |
| OutlinedButton | 描边无背景 | 次要操作 |
| TextButton | 纯文字 | 低优先级（取消/链接） |
| IconButton | 纯图标 | 工具栏操作 |
| FloatingActionButton | 圆形悬浮 | 页面级主操作（新增） |

### 实战：第一个完整计数器

```dart
import 'package:flutter/material.dart';

void main() => runApp(const CounterApp());

class CounterApp extends StatelessWidget {
  const CounterApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '计数器',
      theme: ThemeData(colorSchemeSeed: Colors.indigo, useMaterial3: true),
      home: const CounterPage(),
    );
  }
}

class CounterPage extends StatefulWidget {
  const CounterPage({super.key});

  @override
  State<CounterPage> createState() => _CounterPageState();
}

class _CounterPageState extends State<CounterPage> {
  int _count = 0;                 // ① 定义状态

  void _change(int delta) {
    setState(() => _count += delta); // ② 修改状态必须包在 setState 里
  }

  @override
  Widget build(BuildContext context) {   // ③ 状态变化后自动重新执行
    return Scaffold(
      appBar: AppBar(title: const Text('计数器')),
      body: Center(
        child: Text(
          '$_count',                          // ④ 界面读取状态
          style: const TextStyle(fontSize: 80, fontWeight: FontWeight.bold),
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _change(1),
        child: const Icon(Icons.add),
      ),
    );
  }
}
```

---

## 5. 布局体系

### Flutter 布局三定律（理解布局的钥匙）

1. **约束（Constraints）向下**：父 Widget 把约束传给子 Widget（"你的宽度必须在 0~300 之间，高度必须正好 50"）
2. **尺寸（Size）向上**：子 Widget 根据约束确定自己的尺寸，汇报给父 Widget
3. **位置（Position）由父决定**：父 Widget 决定子 Widget 放在哪里

> 与 Web CSS 的区别：CSS 子元素可以"顶开"父容器，Flutter 里**父的约束是圣旨**，子只能在约束内决定尺寸。理解这一点，90% 的布局报错都能自己排查。

### Row / Column：线性布局（最高频）

```dart
// Row：水平排列；Column：垂直排列，参数完全一样
Row(
  mainAxisAlignment: MainAxisAlignment.spaceBetween, // 主轴对齐
  crossAxisAlignment: CrossAxisAlignment.center,     // 交叉轴对齐
  mainAxisSize: MainAxisSize.max,                    // 主轴尺寸
  children: const [
    Icon(Icons.star, color: Colors.amber),
    Text('4.8 分'),
    Text('已售 2000+'),
  ],
)
```

| mainAxisAlignment（主轴） | 效果 |
|---------------------------|------|
| `start` | 起点对齐（默认） |
| `center` | 居中 |
| `end` | 终点对齐 |
| `spaceBetween` | 两端贴边，中间平分 |
| `spaceAround` | 两侧留一半空隙，中间平分 |
| `spaceEvenly` | 所有空隙完全相等 |

| crossAxisAlignment（交叉轴） | 效果 |
|-------------------------------|------|
| `start` / `center` / `end` | 起点/居中/终点 |
| `stretch` | 拉伸填满交叉轴（子不设高时） |
| `baseline` | 文本基线对齐 |

```
Row 的主轴是水平方向，交叉轴是垂直方向
Column 的主轴是垂直方向，交叉轴是水平方向
```

### Expanded / Flexible：弹性分配空间

```dart
Row(
  children: const [
    Expanded(                       // ★ 占满剩余空间（常用）
      flex: 2,                      // 比例 2
      child: ColoredBox(color: Colors.red, child: SizedBox(height: 40)),
    ),
    Expanded(
      flex: 1,                      // 比例 1 → 红色占 2/3，蓝色占 1/3
      child: ColoredBox(color: Colors.blue, child: SizedBox(height: 40)),
    ),
  ],
)
```

| 对比 | Expanded | Flexible |
|------|----------|----------|
| 是否强制占满空间 | ✅ 必须填满分配的空间 | ❌ 允许子 Widget 更小 |
| fit 值 | `FlexFit.tight` | `FlexFit.loose` |
| 典型场景 | 文字超长挤压其他元素时 | 让子组件"最多这么大" |

> 实战经验：Row 里放长文本报溢出错误时，给 Text 包一层 `Expanded` 就能解决（给它约束让它换行）。

### Stack / Positioned：层叠布局

```dart
// Stack：子 Widget 层叠摆放，后面的盖在前面上面
SizedBox(
  width: 120,
  height: 120,
  child: Stack(
    alignment: Alignment.center,     // 未定位子组件的对齐方式
    children: [
      // 底层：圆形背景
      Container(
        decoration: const BoxDecoration(
          color: Colors.red,
          shape: BoxShape.circle,
        ),
      ),
      // 中层：定位元素（四个边距至少指定两个）
      const Positioned(
        top: 4, right: 4,
        child: CircleAvatar(          // 角标：消息小红点就是这么做出来的
          radius: 10,
          backgroundColor: Colors.white,
          child: Text('3', style: TextStyle(fontSize: 10)),
        ),
      ),
      // 顶层：居中内容
      const Icon(Icons.notifications, color: Colors.white, size: 40),
    ],
  ),
)
```

### Container 剖析：万能容器的真面目

`Container` 不是单一控件，它是多个基础 Widget 的**组合包装器**，传什么参数就组合什么：

```dart
Container(
  width: 200,                       // 尺寸（不传则包裹子元素）
  height: 80,
  margin: const EdgeInsets.all(16), // 外边距
  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8), // 内边距
  alignment: Alignment.center,      // 子元素对齐
  decoration: BoxDecoration(        // ★ 装饰（设置后不能再用 color 参数）
    color: Colors.white,
    borderRadius: BorderRadius.circular(12),
    border: Border.all(color: Colors.grey.shade300),
    boxShadow: [
      BoxShadow(
        color: Colors.black.withOpacity(0.1),
        blurRadius: 8,
        offset: const Offset(0, 2),
      ),
    ],
  ),
  child: const Text('卡片内容'),
)
```

> Container 本质 ≈ `ConstrainedBox` + `DecoratedBox` + `Padding` + `Align` 的合体。只用到单一功能时（如只要内边距），直接用 `Padding` 等单一用途 Widget 更轻量。

### 常用单一布局 Widget 速览

| Widget | 作用 | 代码 |
|--------|------|------|
| `Padding` | 内边距 | `Padding(padding: EdgeInsets.all(8), child: ...)` |
| `Center` | 居中 | `Center(child: ...)` |
| `Align` | 任意对齐 | `Align(alignment: Alignment.bottomRight, child: ...)` |
| `SizedBox` | 固定尺寸/占位空隙 | `SizedBox(width: 10, height: 10)` |
| `AspectRatio` | 固定宽高比 | `AspectRatio(aspectRatio: 16 / 9, child: ...)` |
| `Opacity` | 透明度 | `Opacity(opacity: 0.5, child: ...)` |
| `ClipRRect` | 圆角裁剪（裁图片） | `ClipRRect(borderRadius: ..., child: Image...)` |
| `InkWell` | 可点击区域（水波纹） | `InkWell(onTap: () {}, child: ...)` |
| `SafeArea` | 避开刘海/状态栏 | `SafeArea(child: ...)` |
| `Visibility` | 控制显隐 | `Visibility(visible: flag, child: ...)` |

### EdgeInsets：边距的四种写法

```dart
const EdgeInsets.all(8)                              // 四边全 8
const EdgeInsets.only(left: 16, top: 8)              // 指定边
const EdgeInsets.symmetric(horizontal: 16, vertical: 8) // 水平/垂直对称
const EdgeInsets.fromLTRB(16, 8, 16, 8)              // 左上右下逐个指定
```

### 滚动布局

```dart
// ListView children 版：适合少量固定项（一次性全构建）
ListView(
  padding: const EdgeInsets.all(16),
  children: const [
    ListTile(leading: Icon(Icons.map), title: Text('地图')),
    ListTile(leading: Icon(Icons.photo), title: Text('相册')),
    ListTile(leading: Icon(Icons.phone), title: Text('电话')),
  ],
)

// ListView.builder 版：★ 海量数据必用（惰性构建，只构建屏幕内的）
ListView.builder(
  itemCount: 10000,                          // 数据总数
  itemBuilder: (context, index) {            // 滚到哪构建到哪
    return ListTile(title: Text('第 $index 条'));
  },
)

// ListView.separated 版：带分隔线
ListView.separated(
  itemCount: 50,
  itemBuilder: (context, index) => ListTile(title: Text('第 $index 条')),
  separatorBuilder: (context, index) => const Divider(height: 1), // 分隔线
)

// GridView 网格
GridView.builder(
  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
    crossAxisCount: 3,          // 每行 3 个
    mainAxisSpacing: 8,         // 垂直间距
    crossAxisSpacing: 8,        // 水平间距
    childAspectRatio: 0.75,     // 子项宽高比
  ),
  itemCount: 60,
  itemBuilder: (context, index) => Container(
    color: Colors.primaries[index % Colors.primaries.length],
  ),
)
```

| 滚动方案 | 适用场景 |
|---------|---------|
| `ListView(children:)` | 几个到几十个固定项 |
| `ListView.builder` | **长列表（默认首选）** |
| `ListView.separated` | 长列表 + 分隔线 |
| `GridView.builder` | 瀑布/网格 |
| `CustomScrollView` + Sliver | 复杂滚动（吸顶、折叠头部） |
| `SingleChildScrollView` | 内容可能超屏但不需要复用 |

### 实战：商品卡片陈列

```dart
class ProductList extends StatelessWidget {
  const ProductList({super.key});

  final List<Map<String, dynamic>> products = const [
    {'name': '机械键盘', 'price': 299.0, 'sold': 1200},
    {'name': '无线鼠标', 'price': 99.0, 'sold': 3500},
    {'name': '显示器', 'price': 1299.0, 'sold': 800},
  ];

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      padding: const EdgeInsets.all(12),
      itemCount: products.length,
      separatorBuilder: (_, __) => const SizedBox(height: 12),
      itemBuilder: (context, index) {
        final p = products[index];
        return Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(12),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.05),
                blurRadius: 6,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: Row(
            children: [
              // 左侧：占位图
              Container(
                width: 80, height: 80,
                decoration: BoxDecoration(
                  color: Colors.grey.shade200,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Icon(Icons.image_outlined, size: 32),
              ),
              const SizedBox(width: 12),
              // 中间：标题和销量用 Expanded 占满剩余空间
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(p['name'] as String,
                        style: const TextStyle(
                            fontSize: 16, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 4),
                    Text('已售 ${p['sold']}',
                        style: TextStyle(
                            fontSize: 12, color: Colors.grey.shade600)),
                  ],
                ),
              ),
              // 右侧：价格
              Text('¥${p['price']}',
                  style: const TextStyle(
                      color: Colors.red, fontWeight: FontWeight.bold)),
            ],
          ),
        );
      },
    );
  }
}
```

---

## 6. 交互与表单

### GestureDetector：手势识别（万能但无视觉反馈）

```dart
GestureDetector(
  onTap: () => print('单击'),
  onDoubleTap: () => print('双击'),
  onLongPress: () => print('长按'),
  // 拖动系列
  onPanUpdate: (details) {
    // details.delta：本次移动增量（可用于拖拽移动元素）
    print('拖动中 ${details.delta}');
  },
  // 缩放系列
  onScaleUpdate: (details) => print('缩放 ${details.scale}'),
  child: Container(
    width: 100, height: 100,
    color: Colors.blue,
    child: const Icon(Icons.touch_app, color: Colors.white),
  ),
)
```

### InkWell：带水波纹的点击（Material 风格）

```dart
// InkWell 必须有 Material 祖先才能显示水波纹（Scaffold 内天然满足）
InkWell(
  onTap: () => print('点击卡片'),
  borderRadius: BorderRadius.circular(12), // 水波纹也变圆角
  child: const Padding(
    padding: EdgeInsets.all(12),
    child: Text('点我有水波纹'),
  ),
)
```

| 对比 | GestureDetector | InkWell |
|------|------------------|---------|
| 视觉反馈 | 无 | Material 水波纹 |
| 手势种类 | 全（拖动/缩放/长按…） | 主要是点击类 |
| 使用建议 | 自定义手势交互 | 列表项/卡片点击 |

### TextField：输入框

```dart
// 受控输入框：TextEditingController 读取/设置内容
class _LoginState extends State<LoginPage> {
  final _accountCtrl = TextEditingController(); // 控制器：操作输入框

  @override
  void dispose() {
    _accountCtrl.dispose(); // ★ 用完必须销毁，防内存泄漏
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        TextField(
          controller: _accountCtrl,                    // 绑定控制器
          keyboardType: TextInputType.phone,           // 键盘类型
          decoration: const InputDecoration(
            labelText: '手机号',                        // 悬浮标签
            hintText: '请输入 11 位手机号',             // 占位提示
            prefixIcon: Icon(Icons.phone_android),     // 前置图标
            border: OutlineInputBorder(),              // 外描边样式
            counterText: '',                           // 去掉字数统计
          ),
        ),
        TextField(
          obscureText: true,                           // 密码模式（显示圆点）
          decoration: const InputDecoration(labelText: '密码'),
        ),
        const SizedBox(height: 20),
        ElevatedButton(
          onPressed: () {
            print('输入的内容：${_accountCtrl.text}');  // 读取输入内容
          },
          child: const Text('登录'),
        ),
      ],
    );
  }
}

// 监听输入变化（实时搜索框就是这么做的）
TextField(
  onChanged: (value) => print('输入中：$value'),
)
```

### Form + TextFormField：带校验的表单

单打独斗的 TextField 各管各的，正式表单用 **GlobalKey 统一收集与校验**：

```dart
class LoginForm extends StatefulWidget {
  const LoginForm({super.key});

  @override
  State<LoginForm> createState() => _LoginFormState();
}

class _LoginFormState extends State<LoginForm> {
  // 表单全局钥匙：通过它访问整个表单的状态
  final _formKey = GlobalKey<FormState>();

  String? _phone;
  String? _password;

  // 校验器：返回 null 表示通过，返回字符串就是错误提示
  String? validatePhone(String? value) {
    if (value == null || value.isEmpty) return '手机号不能为空';
    if (!RegExp(r'^1\d{10}$').hasMatch(value)) return '手机号格式不正确';
    return null; // 校验通过
  }

  void _submit() {
    // 触发所有字段的校验器；任意一个不过返回 false
    if (_formKey.currentState!.validate()) {
      _formKey.currentState!.save(); // 触发每个字段的 onSaved 回调
      print('提交成功：$_phone / $_password');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Form(
      key: _formKey,
      child: Column(
        children: [
          TextFormField(
            decoration: const InputDecoration(labelText: '手机号'),
            validator: validatePhone,                    // 挂校验器
            onSaved: (value) => _phone = value,          // 校验通过时收集
          ),
          TextFormField(
            decoration: const InputDecoration(labelText: '密码'),
            obscureText: true,
            validator: (v) =>
                (v == null || v.length < 6) ? '密码至少 6 位' : null,
            onSaved: (value) => _password = value,
          ),
          const SizedBox(height: 24),
          ElevatedButton(onPressed: _submit, child: const Text('登录')),
        ],
      ),
    );
  }
}
```

### 常用交互组件速览

```dart
// 开关
Switch(value: isOn, onChanged: (v) => setState(() => isOn = v))

// 复选框
Checkbox(value: agree, onChanged: (v) => setState(() => agree = v!))

// 单选组
Radio<int>(
  value: 1, groupValue: _selected,
  onChanged: (v) => setState(() => _selected = v!),
)

// 滑块
Slider(value: _volume, min: 0, max: 100, onChanged: (v) => setState(() => _volume = v))

// 弹窗与提示
showDialog(
  context: context,
  builder: (ctx) => AlertDialog(
    title: const Text('确认删除？'),
    actions: [
      TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('取消')),
      TextButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('删除')),
    ],
  ),
);

// 轻提示（Toast）
ScaffoldMessenger.of(context).showSnackBar(
  const SnackBar(content: Text('保存成功'), duration: Duration(seconds: 2)),
);

// 底部弹层（BottomSheet）
showModalBottomSheet(
  context: context,
  builder: (ctx) => const SizedBox(
    height: 200,
    child: Center(child: Text('我是底部弹层')),
  ),
);
```

---

## 7. 状态管理

### 什么是状态？

**状态 = 会随时间变化、且影响界面显示的数据**。Flutter 的 UI 公式：

```
界面 = f(状态)

状态变了 → setState 通知 → build 重新执行 → 界面自动更新
```

| 状态类型 | 例子 | 生命周期 |
|---------|------|---------|
| 局部状态 | 输入框内容、开关开合、Tab 下标 | 单个页面 |
| 跨页面/全局状态 | 登录用户信息、购物车、主题 | 整个应用 |

### setState 的边界：三层问题

setState 只能刷新**当前 State** 对应的 Widget，跨组件传数据就捉襟见肘：

```
层级：  App
       ├── 页面 A（要显示购物车数量）
       │    └── B（子组件）
       │         └── C（点击"加购"要改数量）

问题 1：数据从 A 一路传到 C（构造函数层层传递）
问题 2：C 修改数据后要通知 A 刷新（回调层层传递）
问题 3：A 和 D 是兄弟，共享数据必须提升到共同父级
```

### 方案一：父子直接传递（简单场景够用）

```dart
// —— 父传子：构造函数传递 ——
class Parent extends StatelessWidget {
  const Parent({super.key});

  @override
  Widget build(BuildContext context) {
    const username = '张三';
    return UserCard(name: username);      // 数据向下传
  }
}

class UserCard extends StatelessWidget {
  final String name;
  const UserCard({super.key, required this.name}); // 子组件声明接收

  @override
  Widget build(BuildContext context) => Text('用户：$name');
}

// —— 子传父：回调函数传递 ——
class Parent2 extends StatefulWidget {
  const Parent2({super.key});

  @override
  State<Parent2> createState() => _Parent2State();
}

class _Parent2State extends State<Parent2> {
  int _count = 0;

  @override
  Widget build(BuildContext context) {
    return CounterChild(
      count: _count,                      // 数据向下
      onChanged: (newVal) => setState(() => _count = newVal), // 回调向上
    );
  }
}

class CounterChild extends StatelessWidget {
  final int count;
  final ValueChanged<int> onChanged;      // 声明回调类型参数
  const CounterChild({super.key, required this.count, required this.onChanged});

  @override
  Widget build(BuildContext context) {
    return ElevatedButton(
      // 子组件不持有状态，只负责"报告事件"
      onPressed: () => onChanged(count + 1),
      child: Text('当前 $count，点我加一'),
    );
  }
}
```

> 这与 React 的 props + 回调完全同构。两层组件这样写没问题，五六层就是灾难（俗称"prop drilling"），需要下面的广播机制。

### 方案二：InheritedWidget：数据向下广播（Provider 的地基）

InheritedWidget 让**子树里任意深度的组件**都能直接取到数据，跳过中间层：

```dart
// ① 定义共享数据容器
class UserScope extends InheritedWidget {
  final String username;   // 真正要共享的数据
  const UserScope({
    super.key,
    required this.username,
    required super.child,
  });

  // ② 提供取值入口（子树任何地方调用）
  static UserScope of(BuildContext context) {
    return context.dependOnInheritedWidgetOfExactType<UserScope>()!;
  }

  // ③ 数据变化时是否通知子树重建
  @override
  bool updateShouldNotify(UserScope old) => username != old.username;

  @override
  Widget build(BuildContext context) => child!; // 原样返回子树
}

// ④ 在上层挂载（通常在 MaterialApp 之上）
UserScope(
  username: '张三',
  child: MaterialApp(...),
)

// ⑤ 任意深度的后代直接取值，无需层层传递
Text('你好，${UserScope.of(context).username}')
```

> InheritedWidget 是只读广播：数据放在祖先，后代统一读。修改数据仍需配合 StatefulWidget / ChangeNotifier。Flutter 内部的 Theme、MediaQuery（屏幕尺寸）都是这么实现的。

### 方案三：ValueNotifier：轻量级局部状态

`ValueNotifier` 是"带通知能力的值"——值变了自动通知监听者，不需要整个页面 setState：

```dart
class CartBadge extends StatelessWidget {
  const CartBadge({super.key});

  // ① 在合适的位置（页面/单例）创建可监听的值
  static final cartCount = ValueNotifier<int>(0);

  @override
  Widget build(BuildContext context) {
    // ② ValueListenableBuilder：只监听这一个值，值变只重建这一小块
    return ValueListenableBuilder<int>(
      valueListenable: cartCount,
      builder: (context, count, child) {
        // 只有 cartCount 变化时，这个 builder 才重新执行
        return Badge(label: Text('$count'), child: const Icon(Icons.shopping_cart));
      },
    );
  }
}

// ③ 任何地方修改值，所有监听的界面自动刷新
// cartCount.value++;   ← 比如加购按钮的回调里
```

> 适合：主题切换、购物车角标、全局播放状态等"一个值多处消费"的场景。第三方 GetX 的 `.obs`、Riverpod 的 StateProvider 都是这一思想的延伸。

### 方案四：ChangeNotifier + Provider（工程主流起点）

ChangeNotifier 是 Flutter 内置的"通知中心"类——`notifyListeners()` 一喊，所有监听者刷新。把它和一个页面/业务的**全部状态与逻辑**包在一起，就是 ViewModel 模式；Provider 是官方推荐的第三方包，负责把它插到树上任意位置。

```yaml
# pubspec.yaml
dependencies:
  provider: ^6.1.0
```

```dart
import 'package:flutter/foundation.dart';

// ① 定义状态类：数据 + 修改数据的方法都在这（可独立测试）
class CartModel extends ChangeNotifier {
  final List<String> _items = [];

  List<String> get items => List.unmodifiable(_items); // 对外只读
  int get count => _items.length;

  void add(String item) {
    _items.add(item);
    notifyListeners();   // ★ 数据变了喊一嗓子，所有 Consumer 刷新
  }

  void remove(String item) {
    _items.remove(item);
    notifyListeners();
  }
}

// ② 在应用根部挂载（MultiProvider 可挂多个）
void main() {
  runApp(
    ChangeNotifierProvider(
      create: (context) => CartModel(),
      child: const MyApp(),
    ),
  );
}

// ③ 任意后代消费（两种方式）
class CartPage extends StatelessWidget {
  const CartPage({super.key});

  @override
  Widget build(BuildContext context) {
    // 方式 A：context.watch —— 整个 build 依赖数据，数据变整页重建
    final cart = context.watch<CartModel>();
    return Scaffold(
      appBar: AppBar(title: Text('购物车 (${cart.count})')),
      body: ListView(
        children: [
          for (final item in cart.items) ListTile(title: Text(item)),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        // 方式 B：context.read —— 只在回调里用一次，不建立监听（性能更好）
        onPressed: () => context.read<CartModel>().add('新商品 ${DateTime.now()}'),
        child: const Icon(Icons.add),
      ),
    );
  }
}
```

| API | 建立监听？ | 使用位置 | 性能 |
|-----|----------|---------|------|
| `context.watch<T>()` | ✅ | build 方法内 | 整块重建 |
| `context.read<T>()` | ❌ | 回调/onPressed 里 | 最优 |
| `Consumer<T>` | ✅ | 包住小块区域 | 精准重建 |

### 状态管理方案选型路线

```
简单页面状态        →  setState
跨小组件的一个值    →  ValueNotifier + ValueListenableBuilder
页面级业务状态      →  ChangeNotifier（状态类）
跨页面/全局状态    →  Provider（官方推荐起点）
大型应用复杂流     →  Riverpod / Bloc（学完 Provider 再看，思想相通）
```

---

## 8. 路由与导航

### Navigator 基础：push / pop

Flutter 路由的本质是**栈**：push 压入新页面，pop 弹出回到上一页。

```dart
import 'package:flutter/material.dart';

// —— 跳转：push ——
void goToDetail(BuildContext context) {
  Navigator.push(
    context,
    // MaterialPageRoute：带平台风格的滑入转场（iOS 左滑入/Android 底部滑入）
    MaterialPageRoute(
      builder: (context) => const DetailPage(id: 42),
    ),
  );
}

// —— 返回：pop ——
Navigator.pop(context);                  // 直接返回
Navigator.pop(context, '返回的结果');     // 返回并携带数据

// —— 跳转并等结果：await push（场景：从选择页带结果回来）——
Future<void> pickAndShow(BuildContext context) async {
  final result = await Navigator.push<String>(
    context,
    MaterialPageRoute(builder: (context) => const CityPickerPage()),
  );
  // 这里的代码在目标页 pop 之后才执行，result 是 pop 带回来的值
  if (result != null) {
    print('用户选择了：$result');   // 例如 "杭州"
  }
}
```

### 命名路由（集中管理）

```dart
// ① 集中注册路由表
MaterialApp(
  initialRoute: '/',
  routes: {
    '/': (context) => const HomePage(),
    '/login': (context) => const LoginPage(),
    '/detail': (context) => const DetailPage(),
  },
)

// ② 按名字跳转
Navigator.pushNamed(context, '/login');
Navigator.pushNamed(context, '/detail', arguments: {'id': 42}); // 传参

// ③ 目标页取参数
class DetailPage extends StatelessWidget {
  const DetailPage({super.key});
  @override
  Widget build(BuildContext context) {
    // 通过 ModalRoute 取参数
    final args = ModalRoute.of(context)!.settings.arguments as Map;
    return Text('详情 ${args['id']}');
  }
}
```

### 复杂传参：onGenerateRoute

命名路由的 `routes` 无法优雅传对象参数，正式项目用 `onGenerateRoute`：

```dart
MaterialApp(
  onGenerateRoute: (settings) {
    switch (settings.name) {
      case '/detail':
        // 参数类型安全，直接拿到对象
        final product = settings.arguments as Product;
        return MaterialPageRoute(
          settings: settings,                       // 保留路由信息
          builder: (context) => DetailPage(product: product),
        );
      default:
        return MaterialPageRoute(builder: (_) => const NotFoundPage());
    }
  },
)
```

### 常用导航操作速查

```dart
Navigator.pop(context);                          // 返回上一页
Navigator.popUntil(context, ModalRoute.withName('/'));  // 一路退到首页
Navigator.pushReplacementNamed(context, '/home'); // 替换当前页（登录成功后用）
Navigator.pushAndRemoveUntil(                    // 清空栈再进入（登出重登用）
  context,
  MaterialPageRoute(builder: (_) => const LoginPage()),
  (route) => false,                              // false = 移除所有旧路由
);
```

| 操作 | 场景 |
|------|------|
| `push` / `pushNamed` | 正常进入下一页 |
| `pop` | 返回 |
| `pushReplacement...` | 登录成功进首页（不能返回登录页） |
| `pushAndRemoveUntil` | 退出登录回登录页（清空整个栈） |
| `popUntil` | 多层页面直接退回某页 |

---

## 9. 动画

### 核心概念：四兄弟

Flutter 动画是"流水线"协作，理解四个角色的分工就懂了一半：

| 角色 | 职责 | 类比 |
|------|------|------|
| **AnimationController** | 控制器：管理时间（0→1 的进度值），可播放/暂停/倒放/循环 | 播放器（遥控器） |
| **CurvedAnimation** | 曲线：把线性进度映射为缓动节奏（先快后慢等） | 变速齿轮 |
| **Tween** | 补间：把 0→1 的进度映射到实际值域（如 0→300 像素、红→蓝） | 量程转换器 |
| **AnimatedBuilder** | 构建器：进度每变一帧，重建依赖动画的 Widget | 画布 |

```
AnimationController 产生 0.0 ~ 1.0 线性进度
        │
        ▼ 经过 CurvedAnimation 变形节奏
        │
        ▼ 经过 Tween 映射到实际值（宽度/透明度/颜色）
        │
        ▼ AnimatedBuilder 拿到每帧的值 → setState-free 地重建界面
```

### 隐式动画：AnimatedContainer（最常用，5 行代码）

**隐式动画 = 你只管改属性值，Flutter 自动做过渡**。不需要控制器，代码量最少：

```dart
class AnimatedBoxPage extends StatefulWidget {
  const AnimatedBoxPage({super.key});

  @override
  State<AnimatedBoxPage> createState() => _AnimatedBoxPageState();
}

class _AnimatedBoxPageState extends State<AnimatedBoxPage> {
  bool _expanded = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('隐式动画')),
      body: Center(
        // AnimatedContainer：属性变了自动用动画过渡到新值
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 500), // ★ 动画时长
          curve: Curves.easeInOutBack,                 // 缓动曲线
          width: _expanded ? 260 : 100,
          height: _expanded ? 260 : 100,
          decoration: BoxDecoration(
            color: _expanded ? Colors.indigo : Colors.amber,
            borderRadius: BorderRadius.circular(_expanded ? 130 : 12),
          ),
          child: const Icon(Icons.favorite, color: Colors.white, size: 40),
        ),
      ),
      floatingActionButton: FloatingActionButton(
        // 点击只切换状态，动画完全自动
        onPressed: () => setState(() => _expanded = !_expanded),
        child: Icon(_expanded ? Icons.minimize : Icons.add),
      ),
    );
  }
}
```

**隐式动画家族**（改属性即动画，用法与上面同构）：

| Widget | 过渡的属性 |
|--------|-----------|
| `AnimatedContainer` | 尺寸/颜色/圆角/阴影等一揽子 |
| `AnimatedOpacity` | 透明度（淡入淡出） |
| `AnimatedPadding` | 内边距 |
| `AnimatedAlign` / `AnimatedPositioned` | 位置 |
| `AnimatedSwitcher` | 新旧子元素切换过渡 |
| `AnimatedCrossFade` | 两个子 Widget 交叉淡切 |
| `AnimatedDefaultTextStyle` | 文字样式 |
| `TweenAnimationBuilder` | 任意自定义值（隐式版万能款） |

```dart
// TweenAnimationBuilder：隐式动画的万能款（对任意值做补间）
TweenAnimationBuilder<double>(
  tween: Tween(begin: 0, end: 0.85),          // 目标值变了自动重新过渡
  duration: const Duration(milliseconds: 800),
  builder: (context, value, child) =>
      Opacity(opacity: value, child: child),  // child 参数避免不必要的重建
  child: const Text('我会慢慢出现', style: TextStyle(fontSize: 24)),
)
```

### 显式动画：AnimationController + AnimatedBuilder

需要**精确控制**（循环、暂停、反向、序列编排）时用显式动画：

```dart
import 'package:flutter/material.dart';

class PulsePage extends StatefulWidget {
  const PulsePage({super.key});

  @override
  State<PulsePage> createState() => _PulsePageState();
}

class _PulsePageState extends State<PulsePage>
    with SingleTickerProviderStateMixin {   // ★ Mixin 提供 vsync 信号源
  late final AnimationController _controller;
  late final Animation<double> _scale;

  @override
  void initState() {
    super.initState();
    // 控制器：管理动画时间轴（必须给 vsync，防止页面不可见时白耗电）
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 800),
    )..repeat(reverse: true);   // 创建后立即：往返循环播放

    // 曲线 + 补间：0~1 进度 → 弹性缩放 0.6~1.2
    _scale = CurvedAnimation(parent: _controller, curve: Curves.easeInOut)
        .drive(Tween(begin: 0.6, end: 1.2));
  }

  @override
  void dispose() {
    _controller.dispose();  // ★ 必须销毁
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('心跳脉冲')),
      body: Center(
        // AnimatedBuilder：每帧调用 builder（不需要手动 setState）
        child: AnimatedBuilder(
          animation: _scale,
          builder: (context, child) {
            // 只包住动画部分，child 放静态内容提升性能
            return Transform.scale(scale: _scale.value, child: child);
          },
          child: const Icon(Icons.favorite,
              color: Colors.red, size: 80),
        ),
      ),
    );
  }
}
```

### 常用缓动曲线

| Curves | 效果 |
|--------|------|
| `linear` | 匀速 |
| `easeIn` / `easeOut` / `easeInOut` | 慢入 / 慢出 / 慢入慢出 |
| `easeOutBack` | 冲过头再回弹（活泼） |
| `elasticOut` | 弹簧抖动 |
| `bounceOut` | 小球落地弹跳 |

### 过渡 Widget 家族（*Transition）

配合显式动画控制器使用的"半成品"——传入 `Animation` 对象即可，不用自己写 builder：

```dart
// FadeTransition：淡入淡出
FadeTransition(opacity: _animation, child: const Text('淡入淡出'))

// SlideTransition：位移（FractionalOffset 是比例位移）
SlideTransition(
  position: _animation.drive(
    Tween(begin: const FractionalOffset(-1, 0), end: FractionalOffset.zero),
  ),
  child: const Text('从左侧滑入'),
)

// ScaleTransition / RotationTransition / SizeTransition：缩放/旋转/展开收起
ScaleTransition(scale: _animation, child: const Icon(Icons.star))
RotationTransition(turns: _animation, child: const FlutterLogo(size: 60))
```

### Hero：跨页面共享元素飞跃 ★ 高频

列表页的封面图"飞"到详情页大图——两个页面里用 `Hero` 包住同一个 tag 的 Widget，路由转场时自动产生飞跃动画：

```dart
// 列表页：小图
Hero(
  tag: 'product-42',              // ★ 两边 tag 必须一致
  child: Image.network(url, width: 80),
)
// 点击进入详情页（普通 push 即可，Hero 自动触发）
Navigator.push(context,
    MaterialPageRoute(builder: (_) => const DetailPage()));

// 详情页：大图
Hero(
  tag: 'product-42',              // 相同 tag
  child: Image.network(url, width: double.infinity, height: 240, fit: BoxFit.cover),
)
```

### 交错动画简介

多个子元素依次入场（列表逐条滑入的效果）用 `Interval` 给每个元素分配时间片：

```dart
// 第 i 个元素在总时间轴上占的时间片：错开 0.1
final interval = Interval(
  0.1 * i,                        // 开始时刻
  (0.1 * i + 0.4).clamp(0.0, 1.0),// 结束时刻（clamp 防越界）
);
final delayed = CurvedAnimation(parent: _controller, curve: interval);
```

### 动画方案选择路线

```
属性变了想要过渡效果（一次性）  →  隐式动画（AnimatedContainer 家族）
任意自定义值的隐式过渡          →  TweenAnimationBuilder
循环/暂停/反转/精确控制          →  AnimationController + AnimatedBuilder
淡入/位移/缩放/旋转（配控制器）  →  *Transition 家族
跨页面共享元素                  →  Hero
多个元素依次入场                →  Interval 交错动画
```

---

## 10. 网络与数据

### http 包：基础请求

```yaml
# pubspec.yaml
dependencies:
  http: ^1.2.0
```

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;

// GET 请求
Future<List<dynamic>> fetchUsers() async {
  final response = await http.get(
    Uri.parse('https://api.example.com/users'),
    headers: {'Authorization': 'Bearer xxx'},   // 请求头
  );

  if (response.statusCode == 200) {
    // 响应体是字符串，需要 jsonDecode 解析成 Dart 对象
    final List<dynamic> json = jsonDecode(response.body);
    return json;
  } else {
    // 非 2xx 都按异常处理（业务层不用判断 statusCode）
    throw Exception('请求失败：${response.statusCode}');
  }
}

// POST 请求
Future<void> login(String phone, String code) async {
  final response = await http.post(
    Uri.parse('https://api.example.com/login'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({'phone': phone, 'code': code}), // 对象转 JSON 字符串
  );
  print(jsonDecode(response.body));
}
```

> `jsonDecode` / `jsonEncode` 是字符串与 Dart 对象互转的核心函数，来自 `dart:convert`。

### dio：功能更全的第三方库（正式项目主流）

```yaml
dependencies:
  dio: ^5.4.0
```

```dart
import 'package:dio/dio.dart';

// 拦截器：统一加 token、统一错误处理（http 包没有的能力）
final dio = Dio(BaseOptions(
  baseUrl: 'https://api.example.com', // ★ 统一前缀，接口路径只写后半段
  connectTimeout: const Duration(seconds: 5),
));

void setupDio() {
  dio.interceptors.add(InterceptorsWrapper(
    onRequest: (options, handler) {
      options.headers['Authorization'] = 'Bearer xxx'; // 每个请求自动带
      handler.next(options);
    },
    onError: (error, handler) {
      print('统一错误处理：${error.message}');
      handler.next(error);
    },
  ));
}

// 使用：路径不用写全
final res = await dio.get('/users');
final created = await dio.post('/login', data: {'phone': '13800138000'});
```

| 对比 | http | dio |
|------|------|-----|
| 定位 | 官方轻量库 | 功能型库 |
| 拦截器 | ❌ | ✅ |
| 超时/重试 | 手动 | 内置 |
| baseUrl | ❌ | ✅ |
| 使用建议 | 学习/小工具 | 正式项目 |

### FutureBuilder：把异步结果渲染成界面

FutureBuilder 监听 Future 的三个阶段（等待/成功/失败），自动切换界面：

```dart
class UserListPage extends StatelessWidget {
  const UserListPage({super.key});

  Future<List<String>> fetchUsers() async {
    await Future.delayed(const Duration(seconds: 2)); // 模拟网络延迟
    return ['张三', '李四', '王五'];
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('用户列表')),
      // FutureBuilder：自动管理 等待/成功/失败 三态
      body: FutureBuilder<List<String>>(
        future: fetchUsers(),
        builder: (context, snapshot) {
          // ★ snapshot.connectionState 判断当前阶段
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator()); // 加载中
          }
          if (snapshot.hasError) {
            return Center(child: Text('加载失败：${snapshot.error}'));  // 失败
          }
          // 成功：snapshot.data 拿到结果
          final users = snapshot.data!;
          return ListView(
            children: [for (final u in users) ListTile(title: Text(u))],
          );
        },
      ),
    );
  }
}
```

> ⚠️ 注意：`future` 参数不要直接写 `fetchUsers()` 在 build 里调用的结果每次都新建 Future 会反复请求。正确做法：在 State 里保存 Future（`late final _future = fetchUsers();`）再传给 FutureBuilder。

### StreamBuilder：渲染数据流

```dart
// 监听输入框实时搜索
StreamBuilder<String>(
  stream: searchStream,        // Stream<String>
  builder: (context, snapshot) {
    if (snapshot.hasData) {
      return Text('搜索关键词：${snapshot.data}');
    }
    return const Text('等待输入...');
  },
)
```

### JSON 模型类：手写 fromJson

动态取 `map['xxx']` 满屏都是，既没类型提示又容易拼错字段名。标准做法是定义模型类：

```dart
class User {
  final int id;
  final String name;
  final String avatar;

  User({required this.id, required this.name, required this.avatar});

  // ★ 工厂构造：从 JSON Map 创建对象（网络层 → 模型层的转换入口）
  factory User.fromJson(Map<String, dynamic> json) => User(
        id: json['id'] as int,
        name: json['name'] as String,
        avatar: json['avatar'] as String? ?? '',   // 可空字段给默认值
      );

  // 对象 → JSON（提交给服务端时用）
  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'avatar': avatar,
      };
}

// 使用
final user = User.fromJson(jsonDecode(response.body));
print(user.name);   // 有类型提示、有编译期检查
```

字段多的模型推荐用代码生成库 `json_serializable`（注解 + build_runner 自动生成 fromJson），思路一致只是免手写。

### 分页加载：ListView + 滚动监听

```dart
class _FeedState extends State<Feed> {
  final List<String> _items = [];
  int _page = 1;
  bool _loading = false;
  bool _hasMore = true;
  final _scrollCtrl = ScrollController();

  @override
  void initState() {
    super.initState();
    _scrollCtrl.addListener(() {
      // 滚动到距底部 100 像素以内时加载下一页
      if (_scrollCtrl.position.pixels >=
          _scrollCtrl.position.maxScrollExtent - 100) {
        _loadMore();
      }
    });
    _loadMore(); // 首屏
  }

  Future<void> _loadMore() async {
    if (_loading || !_hasMore) return;   // ★ 防重复加载
    setState(() => _loading = true);
    final newItems = await fetchPage(_page);   // 请求某一页数据
    setState(() {
      _items.addAll(newItems);
      _page++;
      _hasMore = newItems.isNotEmpty;
      _loading = false;
    });
  }

  @override
  void dispose() {
    _scrollCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      controller: _scrollCtrl,
      itemCount: _items.length + 1,        // 多一个尾部"加载中"项
      itemBuilder: (context, index) {
        if (index == _items.length) {
          return _hasMore
              ? const Padding(
                  padding: EdgeInsets.all(16),
                  child: Center(child: CircularProgressIndicator()),
                )
              : const Padding(
                  padding: EdgeInsets.all(16),
                  child: Center(child: Text('没有更多了')),
                );
        }
        return ListTile(title: Text(_items[index]));
      },
    );
  }
}
```

---

## 11. 实用技能

### 依赖管理

```bash
# 添加依赖（自动写入 pubspec.yaml 并安装）
flutter pub add http
flutter pub add provider

# 安装 pubspec.yaml 里声明的全部依赖（拉取别人项目后第一步）
flutter pub get

# 升级依赖
flutter pub upgrade

# 查看过期依赖
flutter pub outdated

# 移除依赖
flutter pub remove http
```

### 本地存储：shared_preferences（键值对）

```yaml
dependencies:
  shared_preferences: ^2.2.0
```

```dart
import 'package:shared_preferences/shared_preferences.dart';

// 所有可能为空，注意判空
Future<void> saveToken() async {
  final prefs = await SharedPreferences.getInstance();
  await prefs.setString('token', 'abc123');   // 写
  await prefs.setBool('isFirstLaunch', false);
  await prefs.setInt('launchCount', 5);
}

Future<void> readToken() async {
  final prefs = await SharedPreferences.getInstance();
  final token = prefs.getString('token');     // 读（不存在返回 null）
  print(token ?? '未登录');
}
```

| 存储方案 | 数据形态 | 适用 |
|---------|---------|------|
| `shared_preferences` | 键值对（token/设置项） | 轻量配置 |
| `path_provider` + 文件 | 任意文件 | 日志/缓存 |
| `sqflite` / `drift` | 关系型数据库 | 结构化大量数据 |
| `hive` / `isar` | NoSQL | 高性能本地库 |

### 屏幕信息与适配

```dart
// MediaQuery：屏幕尺寸/像素密度/安全区域
final size = MediaQuery.of(context).size;               // 逻辑尺寸
print('宽 ${size.width} × 高 ${size.height}');
print('像素密度 ${MediaQuery.of(context).devicePixelRatio}');

// SafeArea：内容避开刘海屏/状态栏/小白条
SafeArea(
  child: ...,
)

// 屏幕宽度的百分比布局（常用小工具函数）
double vw(BuildContext context, double percent) =>
    MediaQuery.of(context).size.width * percent;
// 使用：width: vw(context, 0.5)  → 屏幕一半宽
```

### 全局主题（统一风格的关键）

```dart
MaterialApp(
  theme: ThemeData(                 // 亮色主题
    colorSchemeSeed: Colors.indigo, // 种子色：自动推导整套配色
    useMaterial3: true,
    fontFamily: 'PingFangSC',
    appBarTheme: const AppBarTheme(centerTitle: true),
    textTheme: const TextTheme(
      titleLarge: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
      bodyMedium: TextStyle(fontSize: 14, height: 1.6),
    ),
  ),
  darkTheme: ThemeData(             // 暗色主题（跟随系统自动切换）
    colorSchemeSeed: Colors.indigo,
    brightness: Brightness.dark,
  ),
)

// 后代里取主题值（而不是写死颜色，换主题自动生效）
Text('标题', style: Theme.of(context).textTheme.titleLarge),
Icon(Icons.star, color: Theme.of(context).colorScheme.primary),
```

### 常用第三方包清单

| 包名 | 用途 |
|------|------|
| `dio` | 网络请求（拦截器/超时） |
| `provider` / `riverpod` | 状态管理 |
| `shared_preferences` | 键值存储 |
| `cached_network_image` | 网络图片缓存 |
| `flutter_svg` | SVG 渲染 |
| `pull_to_refresh` / 原生 RefreshIndicator | 下拉刷新 |
| `go_router` | 声明式路由（深链接/守卫） |
| `json_serializable` | JSON 模型代码生成 |

---

## 12. 实战场景

### 场景 1：登录页（表单校验 + 提交状态）

```dart
class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _formKey = GlobalKey<FormState>();
  final _phoneCtrl = TextEditingController();
  final _pwdCtrl = TextEditingController();
  bool _submitting = false;    // 提交状态（防重复提交）

  @override
  void dispose() {
    _phoneCtrl.dispose();
    _pwdCtrl.dispose();
    super.dispose();
  }

  Future<void> _login() async {
    if (!_formKey.currentState!.validate()) return; // 先校验
    setState(() => _submitting = true);
    try {
      // final ok = await api.login(...);   // 真实项目：调用接口
      await Future.delayed(const Duration(seconds: 2)); // 模拟请求
      if (!mounted) return;                          // ★ 异步后先判挂载
      // 登录成功：替换路由，不能返回登录页
      // ignore: use_build_context_synchronously
      Navigator.pushReplacementNamed(context, '/home');
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('登录')),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              TextFormField(
                controller: _phoneCtrl,
                keyboardType: TextInputType.phone,
                decoration: const InputDecoration(
                  labelText: '手机号', prefixIcon: Icon(Icons.phone),
                ),
                validator: (v) =>
                    (v != null && RegExp(r'^1\d{10}$').hasMatch(v))
                        ? null : '请输入正确的手机号',
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _pwdCtrl,
                obscureText: true,
                decoration: const InputDecoration(
                  labelText: '密码', prefixIcon: Icon(Icons.lock),
                ),
                validator: (v) =>
                    (v != null && v.length >= 6) ? null : '密码至少 6 位',
              ),
              const SizedBox(height: 32),
              ElevatedButton(
                onPressed: _submitting ? null : _login,   // 提交中禁用按钮
                child: _submitting
                    ? const SizedBox(
                        width: 20, height: 20,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Text('登 录'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
```

### 场景 2：网络数据列表（加载三态 + 下拉刷新）

```dart
class ArticleListPage extends StatefulWidget {
  const ArticleListPage({super.key});

  @override
  State<ArticleListPage> createState() => _ArticleListPageState();
}

class _ArticleListPageState extends State<ArticleListPage> {
  List<Map<String, dynamic>> _articles = [];
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();   // 进入页面自动加载
  }

  Future<void> _load() async {
    setState(() { _loading = true; _error = null; });
    try {
      // 真实项目替换为 dio 请求；这里模拟数据
      await Future.delayed(const Duration(seconds: 1));
      setState(() {
        _articles = List.generate(
          15,
          (i) => {'title': '文章标题 ${i + 1}', 'author': '作者${i % 5}'},
        );
        _loading = false;
      });
    } catch (e) {
      setState(() { _error = e.toString(); _loading = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('文章列表')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())  // 态 1：加载中
          : _error != null
              ? _ErrorView(message: _error!, onRetry: _load)  // 态 2：失败
              : RefreshIndicator(                             // 态 3：成功
                  onRefresh: _load,                            // 下拉刷新
                  child: ListView.separated(
                    itemCount: _articles.length,
                    separatorBuilder: (_, __) => const Divider(height: 1),
                    itemBuilder: (context, i) {
                      final a = _articles[i];
                      return ListTile(
                        title: Text(a['title'] as String),
                        subtitle: Text(a['author'] as String),
                        trailing: const Icon(Icons.chevron_right),
                        onTap: () => Navigator.pushNamed(
                          context, '/detail',
                          arguments: a,   // 整个对象传过去
                        ),
                      );
                    },
                  ),
                ),
    );
  }
}

// 失败重试视图（抽成独立 Widget，网络页面都能复用）
class _ErrorView extends StatelessWidget {
  const _ErrorView({required this.message, required this.onRetry});
  final String message;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.wifi_off, size: 48, color: Colors.grey),
          const SizedBox(height: 12),
          Text(message, style: const TextStyle(color: Colors.grey)),
          const SizedBox(height: 12),
          ElevatedButton(onPressed: onRetry, child: const Text('重试')),
        ],
      ),
    );
  }
}
```

### 场景 3：列表 → 详情 Hero 飞跃转场

```dart
// —— 列表页：网格里的小图 ——
class GalleryPage extends StatelessWidget {
  const GalleryPage({super.key});

  final List<Color> colors = const [
    Colors.red, Colors.pink, Colors.purple, Colors.deepPurple,
    Colors.indigo, Colors.blue, Colors.teal, Colors.green,
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('画廊')),
      body: GridView.builder(
        padding: const EdgeInsets.all(8),
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 3, crossAxisSpacing: 8, mainAxisSpacing: 8,
        ),
        itemCount: colors.length,
        itemBuilder: (context, i) {
          return GestureDetector(
            onTap: () => Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => ColorDetailPage(color: colors[i], index: i),
              ),
            ),
            child: Hero(
              tag: 'color-$i',                       // ★ 与详情页同 tag
              child: Container(color: colors[i]),
            ),
          );
        },
      ),
    );
  }
}

// —— 详情页：全屏大图 ——
class ColorDetailPage extends StatelessWidget {
  const ColorDetailPage({super.key, required this.color, required this.index});
  final Color color;
  final int index;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('颜色 #$index')),
      body: Hero(
        tag: 'color-$index',                          // ★ 同 tag 自动飞跃
        child: Container(color: color),
      ),
    );
  }
}
```

### 场景 4：启动页（隐式动画组合，无控制器）

```dart
class SplashPage extends StatefulWidget {
  const SplashPage({super.key});

  @override
  State<SplashPage> createState() => _SplashPageState();
}

class _SplashPageState extends State<SplashPage> {
  bool _started = false;   // false → true 触发所有隐式动画

  @override
  void initState() {
    super.initState();
    // 第一帧之后切换状态，让动画从初始值开始播
    WidgetsBinding.instance.addPostFrameCallback((_) {
      setState(() => _started = true);
    });
    // 2.4 秒后进入首页
    Future.delayed(const Duration(milliseconds: 2400), () {
      if (!mounted) return;
      Navigator.pushReplacementNamed(context, '/home');
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.indigo,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // 图标缩放 + 弹性出现
            AnimatedScale(
              scale: _started ? 1 : 0,
              duration: const Duration(milliseconds: 600),
              curve: Curves.easeOutBack,
              child: const Icon(Icons.flutter_dash,
                  size: 96, color: Colors.white),
            ),
            const SizedBox(height: 24),
            // 文字上滑淡入
            AnimatedSlide(
              offset: _started ? Offset.zero : const Offset(0, 0.5),
              duration: const Duration(milliseconds: 600),
              curve: Curves.easeOut,
              child: AnimatedOpacity(
                opacity: _started ? 1 : 0,
                duration: const Duration(milliseconds: 600),
                child: const Text('Flutter 详解',
                    style: TextStyle(
                        color: Colors.white,
                        fontSize: 28,
                        fontWeight: FontWeight.bold)),
              ),
            ),
            const SizedBox(height: 48),
            // 进度条宽度增长
            AnimatedContainer(
              duration: const Duration(milliseconds: 1800),
              curve: Curves.easeInOut,
              width: _started ? 160 : 0,
              height: 3,
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
```

---

## 13. 常见问题排查

### 黄黑相间条纹（RenderFlex overflowed）

**现象**：界面某边缘出现黄黑斜纹，控制台报 `A RenderFlex overflowed by N pixels`。

**原因**：Row/Column 里的子内容总尺寸超出了可用空间。

**解决**：

```dart
// 方案 1：长文本包 Expanded（让其收缩换行）
Row(children: [Expanded(child: Text('很长的文本...'))])

// 方案 2：内容可能超屏，改用滚动容器
SingleChildScrollView(child: Column(...))

// 方案 3：图片/固定内容设 Flexible 或减小尺寸
Flexible(child: Image.network(url, fit: BoxFit.contain))

// 方案 4：文本限制行数
Text('...', maxLines: 1, overflow: TextOverflow.ellipsis)
```

### setState called after dispose

**现象**：报 `setState() called after dispose()`。

**原因**：异步操作（请求/定时器）还没回来，页面已经被关掉了，回来后调用 setState 就崩溃。

**解决**：

```dart
Future<void> _load() async {
  final data = await fetchData();
  if (!mounted) return;    // ★ 异步返回后先判断页面还活着没有
  setState(() => _list = data);
}

// 定时器/监听记得在 dispose 里清理
@override
void dispose() {
  _timer?.cancel();
  _controller.dispose();
  _subscription.cancel();
  super.dispose();
}
```

### 网络图片不显示

排查顺序：

1. **Android**：`android/app/src/main/AndroidManifest.xml` 加网络权限

```xml
<uses-permission android:name="android.permission.INTERNET"/>
```

2. **iOS**：Info.plist 的 ATS 限制（http 明文地址），用 https 或配置例外
3. 加 `errorBuilder` 看是否 404/防盗链：

```dart
Image.network(url, errorBuilder: (_, e, __) => Text('加载失败: $e'))
```

### 图片变形 / 尺寸失控

```dart
// 图片必须显式给约束和填充模式
Image.network(url, width: 100, height: 100, fit: BoxFit.cover)

// 圆角图片用 ClipRRect 包裹（不是给 Image 加 borderRadius）
ClipRRect(
  borderRadius: BorderRadius.circular(12),
  child: Image.network(url, width: 100, height: 100, fit: BoxFit.cover),
)
```

### 嵌套地狱（回调箭头墙）

**现象**：`))))` 排成一排，改动一处缩进全乱。

**方案**：把 build 拆成多个方法/Widget（Flutter 官方建议）：

```dart
// 差：全部堆在 build 里
Widget build(context) => Scaffold(
  appBar: AppBar(title: Text(...), actions: [IconButton(...)]),
  body: Column(children: [Container(...), Row(...)]),
);

// 好：按区域拆分，每个方法职责单一
Widget build(context) => Scaffold(
  appBar: _buildAppBar(),
  body: _buildBody(),
);
Widget _buildAppBar() => AppBar(title: const Text('首页'));
Widget _buildBody() => Column(children: [_buildHeader(), _buildList()]);
// 复用多的直接抽成独立 StatelessWidget 类
```

### 热重载不生效

以下改动热重载（r）无效，需要热重启（R）：

- 改了 `main()` / `runApp`
- 改了 `initState` 里的初始化逻辑（已执行过不会重来）
- 改了全局变量/静态常量的初始值
- 改了 native 代码（需要完全重新编译运行）

### 动画控制器报错

**现象**：`AnimationController` 报 `vsync` 相关错误或页面耗电异常。

**解决**：State 必须混入 `TickerProviderStateMixin`：

```dart
class _PageState extends State<Page>
    with SingleTickerProviderStateMixin {   // 单个控制器
  // ...
}

// 多个控制器时改用
with TickerProviderStateMixin
```

### FutureBuilder 反复请求

**原因**：`future: fetch()` 写在 build 里，每次重建都发起新请求。

```dart
// ❌ 错误：build 每次执行都调用 fetch
FutureBuilder(future: fetch(), ...)

// ✅ 正确：Future 存在 State 字段里，只创建一次
late final _future = fetch();
// build 里：
FutureBuilder(future: _future, ...)
```

### setState 的数据没刷新界面

```dart
// ❌ 原因 1：直接改集合/对象，没包 setState
_list.add(item);                       // 界面不刷新

// ✅ 修改必须包在 setState 回调里
setState(() => _list.add(item));

// ❌ 原因 2：改的是 List 引用副本之外的内容（状态类未 notify）
// 用 ChangeNotifier 时忘记调用 notifyListeners()
```

### 命令行卡在 Running Gradle / 下载慢

```bash
# 国内网络问题：给 Gradle 和 pub 配镜像
# pub 镜像（终端写入环境变量）
export PUB_HOSTED_URL=https://pub.flutter-io.cn
export FLUTTER_STORAGE_BASE_URL=https://storage.flutter-io.cn

# Android 构建卡住：先 flutter clean 再试
flutter clean && flutter pub get && flutter run
```

---

## 14. 速查卡片

### 最小模板（复制即可运行）

```dart
import 'package:flutter/material.dart';

void main() => runApp(const MyApp());

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) => MaterialApp(
        title: 'Flutter Demo',
        theme: ThemeData(colorSchemeSeed: Colors.blue, useMaterial3: true),
        home: const HomePage(),
      );
}

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  int _count = 0;

  @override
  Widget build(BuildContext context) => Scaffold(
        appBar: AppBar(title: const Text('首页')),
        body: Center(child: Text('$_count', style: const TextStyle(fontSize: 48))),
        floatingActionButton: FloatingActionButton(
          onPressed: () => setState(() => _count++),
          child: const Icon(Icons.add),
        ),
      );
}
```

### 常用 API 速查

```dart
// —— 状态 ——
setState(() => value = newValue);          // 修改状态并刷新
mounted;                                   // State 是否还在树上

// —— 路由 ——
Navigator.push(context, MaterialPageRoute(builder: (_) => Page()));
Navigator.pop(context);                     // 返回
Navigator.pop(context, result);             // 返回并带结果
Navigator.pushNamed(context, '/login');     // 命名路由
Navigator.pushReplacementNamed(context, '/home');  // 替换

// —— 弹窗提示 ——
showDialog(context: context, builder: (ctx) => AlertDialog(...));
showModalBottomSheet(context: context, builder: (ctx) => ...);
ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('')));

// —— 动画 ——
AnimationController(vsync: this, duration: Duration(seconds: 1))..repeat(reverse: true);
AnimatedContainer(duration: Duration(ms: 300), width: x, color: y);
Hero(tag: 'same-tag', child: ...);

// —— 网络 ——
final res = await http.get(Uri.parse(url));
jsonDecode(res.body);                       // JSON 字符串 → 对象
jsonEncode(obj);                            // 对象 → JSON 字符串

// —— 屏幕与主题 ——
MediaQuery.of(context).size;                // 屏幕尺寸
Theme.of(context).colorScheme.primary;      // 主题色
MediaQuery.of(context).platformBrightness;  // 当前亮暗模式

// —— 生命周期 ——
initState() {}                              // 初始化（一次）
dispose() {}                                // 销毁（一次）
```

---

## 15. Widget 属性速查

### 15.1 Text

| 属性 | 类型 | 说明 |
|------|------|------|
| `data` | `String` | 文本内容 |
| `style` | `TextStyle` | 样式（字号/颜色/粗细） |
| `textAlign` | `TextAlign` | 对齐：left/center/right/justify |
| `maxLines` | `int` | 最大行数 |
| `overflow` | `TextOverflow` | 溢出处理：ellipsis/fade/clip |
| `textScaleFactor` | `double` | 缩放比例 |

### 15.2 TextStyle

| 属性 | 说明 |
|------|------|
| `fontSize` | 字号（默认 14） |
| `fontWeight` | 粗细：w100~w900 / bold / normal |
| `color` | 颜色 |
| `letterSpacing` / `wordSpacing` | 字间距 / 词间距 |
| `height` | 行高（字号的倍数） |
| `decoration` | 装饰：underline/lineThrough/overline |
| `fontStyle` | italic 斜体 |

### 15.3 Container

| 属性 | 类型 | 说明 |
|------|------|------|
| `width` / `height` | `double?` | 尺寸（不设则包裹内容） |
| `color` | `Color?` | 背景色（与 decoration 互斥） |
| `padding` / `margin` | `EdgeInsetsGeometry?` | 内/外边距 |
| `alignment` | `AlignmentGeometry?` | 子元素对齐 |
| `decoration` | `Decoration?` | 装饰（圆角/边框/阴影） |
| `constraints` | `BoxConstraints?` | 尺寸约束 |
| `transform` | `Matrix4?` | 变换矩阵 |
| `child` | `Widget?` | 子组件 |

### 15.4 BoxDecoration

| 属性 | 说明 |
|------|------|
| `color` | 背景色 |
| `borderRadius` | 圆角：`BorderRadius.circular(12)` |
| `border` | 边框：`Border.all(color:, width:)` |
| `boxShadow` | 阴影列表：`[BoxShadow(color:, blurRadius:, offset:)]` |
| `shape` | 形状：rectangle / circle |
| `gradient` | 渐变：`LinearGradient(colors: [...])` |
| `image` | 背景图：`DecorationImage(image:, fit:)` |

### 15.5 Row / Column

| 属性 | 说明 |
|------|------|
| `mainAxisAlignment` | 主轴对齐：start/center/end/spaceBetween/spaceAround/spaceEvenly |
| `crossAxisAlignment` | 交叉轴对齐：start/center/end/stretch/baseline |
| `mainAxisSize` | 主轴尺寸：max（默认）/ min |
| `textDirection` / `verticalDirection` | 排列方向 |
| `children` | 子组件列表 |

### 15.6 ListView

| 属性 | 说明 |
|------|------|
| `scrollDirection` | 滚动方向：vertical（默认）/ horizontal |
| `itemCount` | 条目总数（builder 模式必传） |
| `itemBuilder` | 构建函数 `(context, index) => Widget` |
| `separatorBuilder` | 分隔线构建（separated 模式） |
| `padding` | 内边距 |
| `shrinkWrap` | true = 高度包裹内容（嵌套在 Column 里时用） |
| `physics` | 滚动物理：`NeverScrollableScrollPhysics()` 禁滚 / `BouncingScrollPhysics()` iOS 弹性 |
| `controller` | 滚动控制器（监听位置/主动滚动） |

### 15.7 Stack / Positioned

| 属性 | 说明 |
|------|------|
| Stack `alignment` | 未定位子组件的对齐 |
| Stack `fit` | expand = 子组件撑满 Stack |
| Positioned `top/right/bottom/left` | 距各边的距离（至少设两个） |
| Positioned `width/height` | 定位元素的显式尺寸 |
| Positioned.fill | 四边归零填满 |

### 15.8 TextField / TextFormField

| 属性 | 说明 |
|------|------|
| `controller` | 文本控制器（读值/设值/监听） |
| `decoration` | 装饰：labelText/hintText/prefixIcon/suffixIcon/border |
| `keyboardType` | 键盘：text/number/phone/emailAddress/url |
| `obscureText` | 密码模式 |
| `maxLines` | 多行（null = 自动增高；1 = 单行） |
| `maxLength` | 最大字数 |
| `onChanged` | 内容变化回调 |
| `onSubmitted` | 按回车回调 |
| `enabled` / `readOnly` | 禁用 / 只读 |
| `validator`（FormField） | 校验器，返回错误文案或 null |
| `onSaved`（FormField） | Form save 时收集值 |
| `autovalidateMode` | 校验时机：onUserInteraction 推荐 |

### 15.9 按钮家族

| 属性 | 说明 |
|------|------|
| `onPressed` | 点击回调（null = 禁用置灰） |
| `onLongPress` | 长按回调 |
| `child` | 按钮内容 |
| `style` | 样式：`ElevatedButton.styleFrom(...)` |
| styleFrom `backgroundColor` | 背景色 |
| styleFrom `foregroundColor` | 前景色（文字/图标） |
| styleFrom `shape` | 形状：`RoundedRectangleBorder(borderRadius:)` |
| styleFrom `padding` | 内边距 |

### 15.10 Image

| 属性 | 说明 |
|------|------|
| 构造器 | `Image.network(url)` / `Image.asset(path)` / `Image.file(file)` |
| `width` / `height` | 尺寸 |
| `fit` | 填充：cover/contain/fill/fitWidth/fitHeight |
| `color` / `colorBlendMode` | 着色（做占位灰调图） |
| `alignment` | 对齐 |
| `repeat` | 平铺 |
| `errorBuilder` | 失败占位 |
| `loadingBuilder` | 加载进度 |
| `frameBuilder` | 帧渲染回调（做淡入） |

### 15.11 动画相关

| 类/属性 | 说明 |
|---------|------|
| AnimationController `duration` | 一次正向播放时长 |
| AnimationController `value` | 当前进度（0~1，可读写） |
| AnimationController `vsync` | 信号源（State with mixin 提供 this） |
| controller 方法 | `forward()` / `reverse()` / `repeat(reverse:)` / `stop()` / `reset()` / `dispose()` |
| CurvedAnimation `curve` / `reverseCurve` | 正向/反向曲线 |
| Tween `begin` / `end` | 值域起止 |
| AnimatedContainer `duration` | 过渡时长 |
| AnimatedContainer `curve` | 缓动曲线 |
| AnimatedBuilder `animation` | 监听的动画对象 |
| AnimatedBuilder `child` | 不参与动画的静态部分（性能优化） |
| Hero `tag` | 匹配标记（两页一致） |
| Hero `flightShuttleBuilder` | 飞行途中替换的 Widget |
| Interval `begin` / `end` | 交错时间片（0~1 内的区间） |

### 15.12 Navigator / 路由

| API | 说明 |
|-----|------|
| `Navigator.push(context, route)` | 压入新路由 |
| `Navigator.pop(context, [result])` | 弹出并可选回传结果 |
| `Navigator.pushReplacement(...)` | 替换当前路由 |
| `Navigator.pushAndRemoveUntil(...)` | 压入并清栈 |
| `Navigator.popUntil(context, predicate)` | 弹到满足条件的路由 |
| `MaterialPageRoute(builder:)` | 平台风格转场 |
| `ModalRoute.of(context)` | 当前路由信息（取 arguments） |
| MaterialApp `routes` | 命名路由表 |
| MaterialApp `initialRoute` | 初始路由 |
| MaterialApp `onGenerateRoute` | 动态生成路由（复杂传参） |

### 15.13 FutureBuilder / StreamBuilder

| 属性 | 说明 |
|------|------|
| `future` / `stream` | 监听的异步源（★ 存 State 字段，别在 build 里现调） |
| `builder` | `(context, snapshot) => Widget` |
| snapshot `connectionState` | waiting（等）/ active（流中）/ done（完） |
| snapshot `data` | 成功数据 |
| snapshot `error` | 错误对象 |
| snapshot `hasData` / `hasError` | 快捷判断 |

### 15.14 生命周期与状态

| 钩子/属性 | 说明 |
|-----------|------|
| `initState()` | 插入树，一次（初始化请求/控制器） |
| `didChangeDependencies()` | 依赖变化（InheritedWidget 更新） |
| `didUpdateWidget(oldWidget)` | 父重建传入新配置 |
| `build(context)` | 构建界面（必须纯粹） |
| `deactivate()` | 被移出树（可能回来） |
| `dispose()` | 销毁，一次（清理控制器/订阅） |
| `setState(fn)` | 修改状态并触发 build |
| `mounted` | State 是否还在树上（异步后必判） |
| `SingleTickerProviderStateMixin` | 单动画控制器的 vsync 源 |
| `TickerProviderStateMixin` | 多动画控制器的 vsync 源 |
| `WidgetsBinding.instance.addPostFrameCallback` | 第一帧渲染后回调（进页面就拿尺寸/触发入场动画） |

