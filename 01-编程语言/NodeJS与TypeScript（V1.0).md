# 第 1 章 必备基础知识

## 计算机组成

### 硬件

计算机硬件主要由五个部分组成，分别是：运算器、控制器、存储器、输入设备、输出设备。

> **📋备注：**『运算器』和『控制器』一起组成了**中央处理器（CPU）**。

> 📢**注意：**计算机的 CPU 只能理解并执行**二进制（用 0和1表示信息）**的**机器指令**。

> **内存 VS 硬盘：**
> + 硬盘：持久化存储，读写速度不如内存快，但容量通常比较大（500GB、1TB、2TB 等）。
> + 内存：暂时性存储，读写速度快，但容量通常不如硬盘大（8GB、16GB、32GB、64GB 等）。
>
> **通俗理解**：能安装多少个游戏，取决于硬盘的大小；能同时开几个游戏，取决于内存的大小。

| 运算器 | 运算器（简称：ALU），专门负责执行各种『算术运算』和『逻辑运算』，它需要与控制单元、寄存器等紧密配合。 |
| :---: | --- |
| 控制器 | 计算机的控制中心，它指挥计算机各部分协调地工作，保证计算机按照预先规定的任务，有条不紊地进行操作及处理。 |
| 存储器 | 计算机中的"资料库"，它既保存程序指令，又保存数据，各个硬件在需要访问或更新数据时，都会与它打交道，有了存储器，计算机才有"记忆"。 |
| 输入设备 | 向计算机输入数据和信息的设备，是计算机与外界通信的桥梁。 |
| 输出设备 | 用于输出计算机执行任务的结果，把各种结果数据或信息以：数字、字符、图像、声音等形式表示出来。 |

### 软件

计算机软件主要分为：系统软件、应用软件。

| 系统软件 | 直接管理和控制计算机硬件的软件，为应用软件提供运行平台，它负责协调硬件资源（如内存、处理器）并提供通用服务，例如：文件管理、设备控制、任务调度。 |
| :---: | --- |
| 应用软件 | 用于执行特定任务的软件，满足用户的具体需求，如：文档编辑、数据分析、娱乐等，它依赖系统软件提供的资源和服务。 |

## 计算机语言、代码、程序

### 计算机语言

计算机语言是人类与计算机进行**『交互』**和**『指令传达』**所使用的一种形式化语言。比如：人与人之间，需要使用各种语言进行交流，那人与计算机之间，同样也需要语言进行沟通。

### 代码

代码是在计算机语言规则的约束下，编写出来的一组指令，具体描述了要让计算机去执行的操作。简言之就是：计算机语言是规则，代码是基于这些规则，所编写出来的一行一行的指令。

### 程序

代码按照特定的顺序和逻辑组合后，就是程序；程序通常用于完成某种特定的任务或功能。如果说程序是一道菜，那代码就是做这道菜的某个步骤。

## 计算机语言简史

### 第一代语言：机器语言

计算机问世的初期，人们只能通过**『机器语言』**（又称机器码）来操作计算机，所谓机器语言，就是`0`和 `1`组成的二进制内容。而且在当时，录入和修改信息通常都需要：拨动开关、或插拔连线、或使用打孔纸带来输入指令。

机器语言虽然能充分利用硬件性能，但所有操作都必须通过二进制来完成，所以编程的过程极为繁琐，且容易出错，对程序员的理解能力和耐心，都要求极高。

> 例如：在`x86`的 CPU 架构下，使用机器码编写`1 + 1`的运算代码如下：
>
> ```
> 10110000 00000001 00000100 00000001
> ```

### 第二代语言：汇编语言

用机器语言编程，程序员很难理解每一条指令的含义，为了解决这个问题，**『汇编语言』**应运而生，它将机器语言中的二进制指令，转化为更容易记忆的助记符（如`MOV`、`ADD`、`LOAD`等），从而让程序员能以近似"英文简写"的方式进行编程，简单说就是：**『汇编语言』**是对**『机器语言』**的"人性化翻译"，汇编语言**显著降低了编程的门槛**，也为后续高级语言的诞生，打下了基础。

> 例如：在`x86`的 CPU 架构下，使用**『汇编语言』**编写`1 + 1`的运算代码如下：
>
> ```
> mov al, 1
> add al, 1
> ```

> 📢**注意：****『汇编语言』**需要翻译成**『机器码』**，才能交给 CPU 执行，因为 CPU 只认二进制指令。

### 第三代语言：高级语言

相对**『机器语言』**和**『汇编语言』**而言，**『高级语言』**更接近人类的自然语言，它允许程序员使用英语来编写程序，并向程序员屏蔽了大部分的底层细节，语言中的符号和算式，也和日常的数学算式差不多，它更容易被掌握，常见的**『高级语言』**有：C、C++、Java、PHP、Go、Rust、JavaScript、Python 等。

> 例如：下面的 JavaScript 代码，可以输出`"Hello, world!"`
>
> ```javascript
> console.log("Hello, world!");
> ```

## 编译型 vs 解释型

高级语言中的源代码无法直接被 CPU 执行，需要**『翻译』**成机器码。翻译方式主要有两种：编译型和解释型。

| 对比维度 | 编译型 | 解释型 |
| :---: | --- | --- |
| 翻译方式 | 一次性翻译所有代码，生成独立的可执行文件 | 逐行读取、翻译、执行（无需独立可执行文件） |
| 执行时机 | 先全量翻译，再执行 | 边翻译边执行 |
| 典型代表 | C、C++、Go、Rust | JavaScript、Python、Ruby |
| 特点 | 运行速度快，但代码修改后需要重新编译 | 开发灵活，修改代码即改即生效，但运行速度相对慢 |

> 📢**注意：**TypeScript 的设计比较特殊：它需要先**编译（transpile）**为 JavaScript，再由 Node.js 或浏览器来执行。这个"编译"过程实际上叫"转译"，它将 TypeScript 代码转换为 JavaScript 代码，并不直接产生机器码。

---

# 第 2 章 初识 TypeScript

## TypeScript 概述

### TypeScript 的起源

TypeScript 由微软公司的 **Anders Hejlsberg**（C# 的首席架构师）主导开发，于 **2012 年 10 月**首次公开发布。

JavaScript 最初被设计用于在浏览器中编写简单的交互脚本，但随着 Web 应用越来越复杂，大型项目中 JavaScript 的动态类型特性暴露出诸多问题：代码难以维护、重构困难、编辑器无法提供良好的智能提示……

2012 年，微软推出了 TypeScript——它在 JavaScript 之上添加了**可选的静态类型系统**，并完全兼容现有 JavaScript 代码，任何合法的 JavaScript 代码同时也就是合法的 TypeScript 代码（在允许隐式 any 的情况下）。

> TypeScript 的设计哲学是**"始于 JavaScript，归于 JavaScript"**——它是 JavaScript 的超集，编译后产出纯净的 JavaScript。

### TypeScript 的核心特点

**优点：**

1. **静态类型检查**：在编译阶段就能发现类型错误，避免大量运行时bug
2. **更好的 IDE 支持**：代码补全、重命名、跳转定义、参数提示
3. **代码可维护性**：类型即文档，大型项目代码更易于理解和重构
4. **JavaScript 超集**：所有合法的 JavaScript 就是合法的 TypeScript，可以渐进式迁移
5. **拥抱 ES 最新特性**：可以使用最新的 ECMAScript 特性，编译为兼容老环境的 JavaScript
6. **活跃的社区生态**：Angular、Vue、React、Node.js 等主流生态全面支持 TypeScript

**缺点：**

1. 需要额外的编译步骤和构建配置
2. 类型系统的学习有一定曲线，尤其是高级类型
3. 引入类型后，小型项目可能显得繁琐
4. 某些第三方库的类型定义可能不完善或不准确（需要安装 `@types/*` 包）

### TypeScript 的版本演进

+ 2012 年：`TypeScript 0.8` 首次公开发布
+ 2013 年：`TypeScript 0.9` 引入泛型支持
+ 2014 年：`TypeScript 1.0` 正式版发布
+ 2016 年：`TypeScript 2.0` 引入 `null` 严格检查、`readonly`、控制流类型分析
+ 2018 年：`TypeScript 3.0` 引入项目引用（Project References）、元组增强
+ 2021 年：`TypeScript 4.0` 引入可变元组类型、模板字面量类型
+ 2022 年：`TypeScript 4.7` 支持 Node.js 下的 ESM（`.mts`/`.cts`）
+ 2023 年：`TypeScript 5.0` 引入装饰器标准、`const` 类型参数
+ 2024 年：`TypeScript 5.4` 持续迭代
+ 2025 年：`TypeScript 5.7` 持续迭代

## 搭建 TypeScript 开发环境

### 安装 Node.js

TypeScript 的编译器 `tsc` 运行在 Node.js 上，因此首先需要安装 Node.js。

**安装步骤：**

1. 进入官网 [https://nodejs.org](https://nodejs.org)，下载 LTS 版本
2. 双击下载好的安装包
3. 保持默认选项，一路 Next 完成安装
4. 打开终端，输入以下命令验证安装成功：

```bash
node --version
npm --version
```

### 安装 TypeScript 编译器

通过 npm（Node.js 包管理器）全局安装 TypeScript：

```bash
npm install -g typescript
```

验证安装：

```bash
tsc --version
```

### 第一个 TypeScript 程序

① 在任意目录下创建文件 `hello.ts`，内容如下：

```typescript
const message: string = "Hello, TypeScript!";
console.log(message);
```

② 打开终端，进入该文件所在目录，执行编译：

```bash
tsc hello.ts
```

③ 编译后会在同目录下生成 `hello.js` 文件，内容如下：

```javascript
var message = "Hello, TypeScript!";
console.log(message);
```

④ 使用 Node.js 运行编译后的 JavaScript 文件：

```bash
node hello.js
```

终端输出：

```
Hello, TypeScript!
```

### tsconfig.json 配置文件

`tsconfig.json` 是 TypeScript 项目的配置文件，它告诉 TypeScript 编译器如何编译代码。

**生成默认配置文件：**

```bash
tsc --init
```

**常用的配置项：**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "strict": true,
    "outDir": "./dist",
    "rootDir": "./src",
    "esModuleInterop": true,
    "forceConsistentCasingInFileNames": true,
    "skipLibCheck": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules"]
}
```

| 配置项 | 说明 |
| --- | --- |
| `target` | 编译后的 JavaScript 版本（如 `ES2020`、`ES6`） |
| `module` | 模块系统（如 `commonjs`、`esnext`） |
| `strict` | 启用所有严格类型检查选项 |
| `outDir` | 编译输出目录 |
| `rootDir` | 源码根目录 |
| `include` | 需要编译的文件范围 |
| `exclude` | 排除的文件范围 |

### 通过 ts-node 直接运行 TypeScript

安装 `ts-node` 可以跳过手动编译步骤，直接运行 TypeScript 文件：

```bash
npm install -g ts-node
```

运行 TypeScript 文件：

```bash
ts-node hello.ts
```

终端直接输出：

```
Hello, TypeScript!
```

> 📋**备注：**`ts-node` 内部仍然会先编译 TypeScript 再执行，只是对用户屏蔽了中间步骤。适合开发调试，生产环境建议先编译再执行。

---

# 第 3 章 TypeScript 核心基础

## 字面量

### 概述

来看这样一个场景：老师让学生把：姓名、年龄、体重写在纸上，纸上的文字，就是学生想要表达的内容，这些内容不需要计算、也不需要转换，就是字面上的含义，一看就能理解。

在程序中，也有上述这些"写出来就能被理解"的内容，这些内容在程序中叫做**字面量**，即：字面量就是直接写在代码中的"具体值"。

### 写法

下面代码中的内容，都是字面量。

```typescript
"张三"
18
65.2

"李四"
22
74.6

"王五"
25
80
```

> 以上代码中的 `"张三"`、`"李四"`、`"王五"` 均为**字符串**。所谓字符串，就是由"字符"组成的"串"。例如，字符串 `"张三"` 由 `"张"` 和 `"三"` 两个字符构成。
>
> 从本质上看，字符串属于文本类型，可以由任意数量的字符组成——无论是中文、英文、数字，还是各种符号。

> 📢**注意：**在 TypeScript 中，字符串可以用：单引号 `'xxx'`、双引号 `"xxx"`、反引号 `` `xxx` ``（模板字符串）包裹，但必须是英文标点符号。单引号和双引号没有本质区别，反引号支持变量插值。

## 变量与常量

### 变量的概念

假如你要多次使用学生的体重值 `65.2`：

```typescript
console.log("张三的体重是", 65.2);
console.log("对于", 65.2, "这个体重，张三觉得不满意");
console.log("张三决定开始减肥，希望体重比", 65.2, "还要小");
```

当要把 `65.2` 改为 `64.2` 时，需要手动修改 3 个地方——这就是直接写字面量的不便之处。

**变量**就是数据的"代号"——把数据和某个名字绑定在一起，以后使用时直接调用名字即可。

```typescript
let weight: number = 65.2;

console.log("张三的体重是", weight);
console.log("对于", weight, "这个体重，张三觉得不满意");
console.log("张三决定开始减肥，希望体重比", weight, "还要小");
```

现在只需修改一处：

```typescript
let weight: number = 65.2;
weight = 64.2;  // 修改一次即可

console.log("张三的体重是", weight);          // 64.2
console.log("对于", weight, "这个体重，张三觉得不满意");
console.log("张三决定开始减肥，希望体重比", weight, "还要小");
```

### 变量的几个关键点

1. 代码 `let weight: number = 65.2` 被称为**赋值语句**，其中 `=` 表示将右侧的值绑定到左侧的变量上（不是"等于"）。
2. 变量和值的绑定关系可以随时改变（所以叫"变"量）。
3. 变量名不能加引号。

### let、const、var 的区别

TypeScript（和 JavaScript）有三种声明变量的关键字：

```typescript
var age1 = 18;      // ES5 方式，不推荐使用
let age2 = 18;      // ES6 引入，可变变量（推荐）
const age3 = 18;    // ES6 引入，不可变常量（推荐优先使用）
```

| 关键字 | 能否重新赋值 | 作用域 | 是否推荐 |
| :---: | :---: | :---: | :---: |
| `var` | 能 | 函数作用域 | 不推荐（有变量提升、无块级作用域等问题） |
| `let` | 能 | 块级作用域 | 推荐（需要重新赋值时使用） |
| `const` | **不能** | 块级作用域 | **优先使用**（不需要重新赋值时） |

```typescript
// var 的问题1：变量提升
console.log(x);  // undefined（不报错，但 x 是 undefined）
var x = 10;

// let/const 没有变量提升
// console.log(y);  // 编译错误：在赋值前使用了变量 y
let y = 10;

// var 的问题2：没有块级作用域
if (true) {
    var a = 100;
}
console.log(a);  // 100（var 声明的 a 在块外部仍然能访问）

if (true) {
    let b = 200;
}
// console.log(b);  // 编译错误：b 只存在于 if 块内

// const 不能重新赋值
const name = "张三";
// name = "李四";  // 编译错误：无法重新赋值常量
```

> 📢**注意：**`const` 声明的是**引用不可变**，而非值不可变。对于数组和对象，`const` 变量本身的引用不能变，但内部的元素或属性可以修改：
>
> ```typescript
> const nums = [1, 2, 3];
> nums.push(4);      // ✅ 允许：修改数组内容
> // nums = [4, 5];  // ❌ 禁止：重新赋值
>
> const person = { name: "张三" };
> person.name = "李四";   // ✅ 允许：修改对象属性
> // person = { name: "王五" }; // ❌ 禁止：重新赋值
> ```

### 标识符命名规则

**什么是标识符？**

在程序中我们给：变量、函数、类……所起的**名字**，统称为**标识符**，即：在程序中所有我们可以自己起的名字，都是标识符。

**标识符命名规则如下：**

1. 只能包含：数字、字母、下划线（`_`）、美元符号（`$`），且**不能**以数字开头，**不能**包含空格。
2. 区分大小写，即 `Name` 和 `name` 是两个不同的标识符。
3. **不能**使用关键字和保留字。
4. 标识符虽然没有长度限制，但应追求：简洁清晰，具有描述性。

**命名风格建议：**

| 应用场景 | 命名风格 | 示例 |
| :---: | --- | --- |
| 变量、函数 | camelCase（驼峰命名） | `userName`、`getUserInfo` |
| 类、接口、类型别名 | PascalCase（帕斯卡命名） | `Person`、`UserInfo` |
| 常量（特别是枚举值） | UPPER_SNAKE_CASE | `MAX_COUNT`、`API_URL` |
| 私有属性 | 下划线前缀（约定） | `_internalState` |

**TypeScript 中的关键字和保留字：**

```
break     case      catch     class     const     continue
debugger  default   delete    do        else      enum
export    extends   false     finally   for       function
if        import    in        instanceof interface let
new       null      return    super     switch    this
throw     true      try       typeof    var       void
while     with      as        any       boolean   constructor
declare   get       module    require   number    set
string    symbol    type      from      of        async
await     yield     implements namespace package  protected
private   public    static    readonly  abstract  keyof
infer     never     unknown   override
```

## 基本数据类型

TypeScript 在 JavaScript 原有类型的基础上，增加了丰富的类型系统。TypeScript 中的数据类型分为：**原始类型**和**对象类型**。

### 数字（number）

TypeScript 中的数字类型不区分整数和浮点数，统一使用 `number`。

```typescript
let integer: number = 42;
let float: number = 3.14;
let negative: number = -10;
let hex: number = 0xff;       // 十六进制：255
let binary: number = 0b1010;  // 二进制：10
let octal: number = 0o744;    // 八进制：484
let scientific: number = 1.5e6; // 科学计数法：1500000
```

### 字符串（string）

```typescript
let single: string = 'hello';
let double: string = "你好";
let template: string = `你好，${single}`;  // 模板字符串（反引号包裏，支持变量插值）
```

> `\` 符（反引号/Template Literal）是 Es6 引入的特性，支持：
> - **变量插值**：`${变量名}`
> - **换行字符串**：可以写在模板字符串里面，不需要 `\n`

```typescript
let name: string = "张三";
let age: number = 18;

// 变量插值
let msg: string = `我叫${name}，今年${age}岁`;
console.log(msg);  // 我叫张三，今年18岁

// 多行字符串
let multiline: string = `
第一行
第二行
第三行
`;
```

### 布尔值（boolean）

```typescript
let isDone: boolean = true;
let hasError: boolean = false;
```

### 数组（Array）

数组有两种声明方式：

```typescript
// 方式一：类型[]
let numbers: number[] = [1, 2, 3, 4, 5];
let names: string[] = ["张三", "李四", "王五"];

// 方式二：Array<类型>（泛型写法）
let scores: Array<number> = [85, 92, 78];
```

> 📋**备注：**两种写法完全等价，使用哪种取决于团队风格。项目中建议统一使用一种。

### 元组（Tuple）

**元组是 TypeScript 特有的编译时类型**，它允许声明一个**已知元素数量**和**各位置类型**的数组。运行时本质仍然是普通数组。

```typescript
// 声明一个有两个元素的元组：第一个是 string，第二个是 number
let person: [string, number] = ["张三", 18];

// 访问元组元素
console.log(person[0]);  // "张三"
console.log(person[1]);  // 18

// 类型错误：位置对应的类型必须匹配
// person = [18, "张三"];  // ❌ 编译错误
// person = ["张三", 18, true];  // ❌ 编译错误：多了一个元素

// 元组配合可选元素
let optional: [string, number?] = ["张三"];  // 第二个元素可选

// 元组配合剩余元素
let rest: [string, ...number[]] = ["张三", 90, 85, 88];
```

> 📢**注意：**TypeScript 的元组和 Python 的元组有本质区别：
> - **TypeScript 元组**：编译时类型约束，运行时就是普通 JS 数组，元素可以任意修改。
> - **Python 元组**：运行时不可变序列，无法修改内部元素。

```typescript
// 运行时：TypeScript 元组就是普通数组
let tuple: [string, number] = ["hello", 42];
tuple[0] = "world";    // ✅ 运行时允许（数组是可变的）
tuple.push(100);       // ✅ 运行时允许（数组操作正常）
console.log(tuple);    // ["world", 42, 100] —— 绕过了编译时的长度检查
```

### 枚举（Enum）

枚举是 TypeScript 特有的类型，用于定义一组命名常量。

```typescript
// 数字枚举（默认从 0 开始）
enum Direction {
    Up,      // 0
    Down,    // 1
    Left,    // 2
    Right    // 3
}

let dir: Direction = Direction.Up;
console.log(dir);  // 0

// 手动指定值
enum Status {
    Success = 200,
    NotFound = 404,
    ServerError = 500
}

console.log(Status.NotFound);  // 404
console.log(Status[200]);      // "Success"（数字枚举支持反向映射）

// 字符串枚举（不支持反向映射）
enum Color {
    Red = "red",
    Green = "green",
    Blue = "blue"
}

let color: Color = Color.Red;
console.log(color);  // "red"
```

### 特殊类型

**any — 任意类型**

关闭类型检查，变量可以赋值为任意类型。尽量少用，否则失去了 TypeScript 的意义。

```typescript
let anything: any = "hello";
anything = 42;        // ✅ 允许
anything = true;      // ✅ 允许
anything.foo.bar();   // ✅ 允许（但运行时会报错）
```

**unknown — 未知类型**

与 `any` 类似，但**类型安全得多**：在对 `unknown` 类型的值做任何操作之前，必须先进行类型收窄。

```typescript
let unknownValue: unknown = "hello";

// unknownValue.toUpperCase();  // ❌ 编译错误：不能直接调用方法

// 必须先收窄类型
if (typeof unknownValue === "string") {
    console.log(unknownValue.toUpperCase());  // ✅ "HELLO"
}

// 或者使用类型断言
console.log((unknownValue as string).length);  // ✅ 类型断言后可以使用
```

| 对比 | `any` | `unknown` |
| :---: | --- | --- |
| 安全程度 | 不安全，完全跳过类型检查 | 安全，必须收窄类型后才能使用 |
| 使用场景 | 快速原型、动态内容、迁移 JS 项目 | 需要灵活性但仍想保证类型安全 |
| 推荐程度 | 不推荐，尽量不用 | 可以作为 `any` 的安全替代 |

**void — 无返回值**

通常用于函数的返回值类型，表示函数没有返回值。

```typescript
function log(message: string): void {
    console.log(message);
    // 没有 return 语句
}
```

**null 和 undefined**

```typescript
let u: undefined = undefined;
let n: null = null;

// 开启 strictNullChecks 时（推荐），null/undefined 不能赋值给其他类型
// let name: string = null;  // ❌ 编译错误
let name: string | null = null;  // ✅ 联合类型写法
```

**never — 永不存在的值**

表示永远不会发生的类型，常用于：
- 永远抛出异常的函数
- 永远不返回的函数（如无限循环）

```typescript
// 抛出异常的函数永远不会有返回值
function throwError(message: string): never {
    throw new Error(message);
}

// 无限循环的函数
function infiniteLoop(): never {
    while (true) {
        // 永远在循环中
    }
}

// never 可用于穷尽性检查
type Shape = "circle" | "square";

function getArea(shape: Shape): number {
    switch (shape) {
        case "circle":
            return Math.PI;
        case "square":
            return 4;
        default:
            // 如果 Shape 新增了类型但没有处理，这里会编译报错
            const exhaustiveCheck: never = shape;
            return exhaustiveCheck;
    }
}
```

## 类型推断与类型注解

### 类型注解

显式写明变量或函数的类型：

```typescript
let name: string = "张三";
let age: number = 18;
let isStudent: boolean = true;

function greet(person: string): string {
    return `你好，${person}`;
}
```

### 类型推断

当你没有显式注明类型时，TypeScript 会根据初始赋值**自动推断**类型：

```typescript
let name = "张三";       // 推断为 string
let age = 18;           // 推断为 number
let scores = [85, 92];  // 推断为 number[]

// name = 42;           // ❌ 编译错误：类型推断为 string，不能赋 number
```

> 📋**建议：**当初始值能明确表达意图时，可以省略类型注解（交给 TS 推断）。当变量声明和赋值分离，或值类型不明显时，建议显式注解。

## 联合类型与交叉类型

### 联合类型（Union Types）

一个值可以是多种类型之一，使用 `|` 分隔：

```typescript
// id 可以是 number 或 string
let id: number | string = 101;
id = "A102";  // ✅ 允许

// 函数参数联合类型
function printId(id: number | string): void {
    // 使用前需要收窄类型
    if (typeof id === "string") {
        console.log(id.toUpperCase());
    } else {
        console.log(id.toFixed(2));
    }
}
```

### 交叉类型（Intersection Types）

将多个类型合并成一个类型，使用 `&` 连接：

```typescript
interface Person {
    name: string;
    age: number;
}

interface Employee {
    employeeId: number;
    department: string;
}

// 交叉类型：同时拥有 Person 和 Employee 的所有属性
type EmployeePerson = Person & Employee;

const worker: EmployeePerson = {
    name: "张三",
    age: 30,
    employeeId: 1001,
    department: "技术部"
};
```

## 类型别名（Type Alias）

类型别名就是给一个类型起个新名字：

```typescript
// 基本类型别名
type ID = number | string;
type Name = string;

let userId: ID = 1001;
userId = "USER_1001";

// 对象类型别名
type User = {
    name: string;
    age: number;
    isAdmin: boolean;
};

const user: User = {
    name: "张三",
    age: 18,
    isAdmin: false
};
```

## 接口（Interface）

接口是 TypeScript 中定义**对象形状**的核心方式之一：

```typescript
interface Person {
    name: string;
    age: number;
    greet(): string;  // 方法
}

const person: Person = {
    name: "张三",
    age: 18,
    greet() {
        return `你好，我是${this.name}`;
    }
};

console.log(person.greet());  // 你好，我是张三
```

**可选属性与只读属性：**

```typescript
interface Config {
    readonly id: number;      // 只读，创建后不可修改
    name: string;
    description?: string;     // 可选属性（可写可不写）
}

const config: Config = { id: 1, name: "我的配置" };
// config.id = 2;  // ❌ 编译错误：只读属性不能修改
```

### Type Alias vs Interface

| 对比维度 | `type` | `interface` |
| :---: | --- | --- |
| 基本用途 | 定义类型别名（联合、交叉、原始类型别名等） | 定义对象的结构形状 |
| 能否声明联合类型 | ✅ 能 | ❌ 不能 |
| 能否扩展 | 通过交叉类型 `&` | 通过 `extends` |
| 能否被类实现 | ❌ 不能 | ✅ `class Foo implements MyInterface` |
| 声明合并 | ❌ 不支持同名合并 | ✅ 同名 interface 自动合并 |
| 推荐使用场景 | 联合类型、元组、函数类型 | 对象的形状定义、类的实现约定 |

```typescript
// interface 的声明合并
interface Book {
    title: string;
}
interface Book {
    author: string;
}
// Book 现在同时有 title 和 author
const book: Book = { title: "活着", author: "余华" };

// type 同名会报错
type Film = { title: string };
// type Film = { author: string };  // ❌ 编译错误
```

---

# 第 4 章 流程控制语句

程序并不是简单的"从上到下"执行，很多时候，我们希望程序能根据不同的情况，做出不同的选择，比如：根据情况跳过某些代码，或者重复执行某些代码，那这时就需要用到『流程控制语句』，程序的执行流程大体上可分为三类：**顺序**、**分支**、**循环**。

> 📋**备注：**其中顺序执行是最简单的，就是按照程序的编写顺序依次执行，所以我们不再探讨顺序执行。

## 分支

分支有很多其他的称呼，比如：条件控制语句、分支语句、选择语句。分支是通过条件判断，来决定执行哪些代码。

### 单分支（if）

**语法格式：**

```typescript
if (判断条件) {
    条件【成立】时执行的代码1
    条件【成立】时执行的代码2
}
```

**示例代码：**

```typescript
const age: number = 20;

if (age >= 18) {
    console.log("你是成年人");
    console.log("成年人的世界，虽不容易，但很精彩！");
}
```

### 双分支（if-else）

**语法格式：**

```typescript
if (判断条件) {
    条件【成立】时执行的代码
} else {
    条件【不成立】时执行的代码
}
```

**示例代码：**

```typescript
const age: number = 16;

if (age >= 18) {
    console.log("你是成年人");
} else {
    console.log("你是未成年人");
}
```

### 多分支（if-else if-else）

**语法格式：**

```typescript
if (条件1) {
    条件1成立时执行
} else if (条件2) {
    条件2成立时执行
} else {
    以上条件都不成立时执行
}
```

**示例代码：**

```typescript
const score: number = 85;

if (score >= 90) {
    console.log("优秀");
} else if (score >= 80) {
    console.log("良好");
} else if (score >= 60) {
    console.log("及格");
} else {
    console.log("不及格");
}
// 输出：良好
```

### switch 语句

当需要对一个变量的值进行多种等值判断时，`switch` 比多层 `if-else` 更清晰：

**语法格式：**

```typescript
switch (表达式) {
    case 值1:
        代码块1
        break;
    case 值2:
        代码块2
        break;
    default:
        默认代码块
}
```

**示例代码：**

```typescript
const day: number = 3;
let dayName: string;

switch (day) {
    case 1:
        dayName = "星期一";
        break;
    case 2:
        dayName = "星期二";
        break;
    case 3:
        dayName = "星期三";
        break;
    case 4:
        dayName = "星期四";
        break;
    case 5:
        dayName = "星期五";
        break;
    case 6:
    case 7:
        dayName = "周末";
        break;
    default:
        dayName = "无效日期";
}

console.log(dayName);  // 星期三
```

> 📢**注意：**每个 `case` 后必须加 `break`，否则会穿透到下一个 `case`（case 6 和 7 故意利用了穿透，共享同一个处理逻辑）。

## 循环

循环用于重复执行某段代码，直到满足某个终止条件。

### for 循环

最基础的循环，已知循环次数时使用：

**语法格式：**

```typescript
for (初始化; 条件; 更新) {
    循环体
}
```

**示例代码：**

```typescript
// 打印 0 到 4
for (let i = 0; i < 5; i++) {
    console.log(i);
}
// 输出：0  1  2  3  4
```

### while 循环

当循环次数不确定，但循环条件明确时使用：

```typescript
let count = 0;

while (count < 5) {
    console.log(count);
    count++;
}
// 输出：0  1  2  3  4
```

### do-while 循环

`do-while` 保证循环体**至少执行一次**（先执行后判断）：

```typescript
let i = 10;

do {
    console.log("至少打印一次");
    i++;
} while (i < 5);
// 输出：至少打印一次
```

### for-of 循环（遍历数组）

ES6 引入的 `for-of` 用于遍历**可迭代对象**（Array、Map、Set 等）的值：

```typescript
const fruits: string[] = ["苹果", "香蕉", "橙子"];

for (const fruit of fruits) {
    console.log(fruit);
}
// 输出：苹果  香蕉  橙子
```

### for-in 循环（遍历对象的键）

```typescript
const person = { name: "张三", age: 18, city: "北京" };

for (const key in person) {
    console.log(`${key}: ${person[key]}`);
}
// 输出：
// name: 张三
// age: 18
// city: 北京
```

### break 与 continue

```typescript
// break：终止整个循环
for (let i = 0; i < 10; i++) {
    if (i === 5) break;
    console.log(i);
}
// 输出：0  1  2  3  4

// continue：跳过本次循环，进入下一次
for (let i = 0; i < 10; i++) {
    if (i % 2 === 0) continue;
    console.log(i);
}
// 输出：1  3  5  7  9
```

---

# 第 5 章 函数入门

## 概念

函数（function）是：**组织好的**、可**重复使用**的、用于执行**特定任务**的代码块。

> 🌰举个生活中的例子：
>
> 函数就像是智能家居中的一个场景，我们提前配置好场景中要执行的操作，等需要时，直接呼唤场景的名字，场景中的操作就会开始执行。

使用函数的主要优势：

- 减少重复代码，提高可维护性
- 将复杂任务拆分为小模块，便于理解和协作
- 一处修改多处生效

## 定义和调用函数

### 函数定义

**语法格式：**

```typescript
function 函数名(参数列表): 返回值类型 {
    函数体
    return 返回值;
}
```

**示例代码：**

```typescript
function greet(): void {
    console.log("欢迎来到 TypeScript 课堂！");
    console.log("让天下没有难学的技术！");
}
```

> 函数定义完毕后，只是告诉 TypeScript 我们定义了一个函数可以完成某些功能，但此时函数体还没有执行，需要**调用函数**后，函数体才会执行！

### 函数调用

**语法格式：**

```typescript
函数名(实际参数);
```

```typescript
function greet(): void {
    console.log("欢迎来到 TypeScript 课堂！");
}

// 调用函数
greet();  // 输出：欢迎来到 TypeScript 课堂！
greet();  // 可重复调用
```

## 函数的参数与返回值

### 参数

参数是函数**接收数据**的通道，定义时的参数叫**形参**，调用时传入的叫**实参**。

```typescript
function greet(name: string): void {
    console.log(`你好，${name}！`);
}

greet("张三");  // 你好，张三！
greet("李四");  // 你好，李四！
```

**可选参数与默认参数：**

```typescript
// 可选参数：用 ? 标记（必须放在必选参数后面）
function introduce(name: string, age?: number): void {
    if (age) {
        console.log(`我叫${name}，今年${age}岁`);
    } else {
        console.log(`我叫${name}`);
    }
}

introduce("张三", 18);  // 我叫张三，今年18岁
introduce("李四");      // 我叫李四

// 默认参数
function createUser(name: string, role: string = "普通用户"): void {
    console.log(`${name} - ${role}`);
}

createUser("张三", "管理员");  // 张三 - 管理员
createUser("李四");            // 李四 - 普通用户（使用默认值）
```

**剩余参数（rest parameters）：**

```typescript
// ... 收集剩余参数到一个数组中
function sum(...numbers: number[]): number {
    let total = 0;
    for (const n of numbers) {
        total += n;
    }
    return total;
}

console.log(sum(1, 2, 3));       // 6
console.log(sum(1, 2, 3, 4, 5)); // 15
```

### 返回值

函数可以返回一个计算结果，使用 `return` 关键字：

```typescript
function add(a: number, b: number): number {
    return a + b;
}

const result: number = add(10, 20);
console.log(result);  // 30
```

> 📢**注意：**`return` 之后的代码不会执行，函数在遇到 `return` 时就结束了。

### 函数类型签名

在 TypeScript 中，可以为函数声明类型签名：

```typescript
// 方式一：直接在函数上写类型
function add(a: number, b: number): number {
    return a + b;
}

// 方式二：给变量标注函数类型
let calculate: (x: number, y: number) => number;

calculate = function(a, b) {
    return a * b;  // a 和 b 自动推断为 number
};

console.log(calculate(3, 4));  // 12
```

---

# 第 6 章 函数进阶

## 函数也是对象（一等公民）

在 JavaScript/TypeScript 中，函数是**一等公民**——函数本身也可以被赋值给变量、作为参数传递、或作为另一个函数的返回值。

### 函数赋值给变量

```typescript
function greet(): void {
    console.log("你好啊！");
}

// 将函数赋值给变量（注意：不是调用，不带括号）
const sayHello = greet;

// 通过新变量调用
sayHello();  // 你好啊！
greet();     // 你好啊！
```

### 函数作为参数（回调函数）

```typescript
// callback 是一个函数类型的参数
function doSomething(task: string, callback: (result: string) => void): void {
    console.log(`正在执行：${task}`);
    const result = `${task} 完成`;
    callback(result);  // 调用回调，传递结果
}

doSomething("上传文件", (result) => {
    console.log(`回调收到：${result}`);
});
// 输出：
// 正在执行：上传文件
// 回调收到：上传文件 完成
```

### 函数作为返回值

```typescript
// 返回一个函数
function createGreeter(language: string): (name: string) => string {
    if (language === "zh") {
        return (name) => `你好，${name}`;
    } else {
        return (name) => `Hello, ${name}`;
    }
}

const greetInChinese = createGreeter("zh");
console.log(greetInChinese("张三"));  // 你好，张三

const greetInEnglish = createGreeter("en");
console.log(greetInEnglish("John"));  // Hello, John
```

## 闭包

**闭包**是指：函数能够"记住"并访问其**定义时所在的作用域**中的变量，即使该函数在别处被调用。

```typescript
function createCounter(): () => number {
    let count = 0;  // 外部函数的局部变量

    // 返回一个函数
    return function(): number {
        count++;  // 这里访问的是外部作用域的 count
        return count;
    };
}

const counter1 = createCounter();
console.log(counter1());  // 1
console.log(counter1());  // 2
console.log(counter1());  // 3

const counter2 = createCounter();  // 每个闭包有独立的作用域
console.log(counter2());  // 1（新的计数器从 1 开始）
```

> 📋**说明：**`createCounter()` 执行完后，按理说 `count` 变量应该被销毁。但由于内部返回的匿名函数引用着 `count`，所以 `count` 被保留了下来，形成了闭包。每个 `createCounter()` 调用都创建了一个独立的作用域。

## 函数重载

TypeScript 的**函数重载**允许为同一个函数声明多个不同的调用签名，针对不同的参数类型或数量返回不同的类型。

```typescript
// 重载签名（只声明，不实现）
function format(value: string): string;
function format(value: number): string;
function format(value: boolean): string;

// 实现签名（处理所有情况）
function format(value: string | number | boolean): string {
    if (typeof value === "string") {
        return `字符串：${value}`;
    } else if (typeof value === "number") {
        return `数字：${value.toFixed(2)}`;
    } else {
        return `布尔值：${value}`;
    }
}

console.log(format("hello"));  // 字符串：hello
console.log(format(3.14159));  // 数字：3.14
console.log(format(true));     // 布尔值：true
```

> 📢**注意：**TypeScript 的函数重载和 Java/C++ 的概念不同。TS 只有**一个**实际的函数实现，上面定义的是多个类型签名（告诉编译器有哪些使用方式），内部需要靠类型守卫自行处理不同情况。

## 泛型函数

**泛型**是 TypeScript 最重要的特性之一，它让函数可以处理**多种类型**的数据，而不丢失类型信息。

### 泛型的基本概念

```typescript
// 不使用泛型：丢失了类型信息
function identity1(value: any): any {
    return value;
}

// 使用泛型：保留类型信息
function identity<T>(value: T): T {
    return value;
}

// 指定类型参数调用
const str = identity<string>("hello");      // str 类型是 string
const num = identity<number>(42);            // num 类型是 number

// 类型参数可以推断，可以省略 <类型>
const inferred = identity("hello");          // 推断为 string
```

> 📋**说明：**`<T>` 中的 `T` 是**类型变量**的名字，和函数参数一样，可以任意命名（习惯用 `T`、`U`、`V` 等大写字母）。调用时，编译器会自动推断 `T` 的具体类型。

### 泛型约束

```typescript
// 要求传入的类型必须包含 length 属性
interface HasLength {
    length: number;
}

function logLength<T extends HasLength>(value: T): T {
    console.log(`长度：${value.length}`);
    return value;
}

logLength("hello");           // 长度：5
logLength([1, 2, 3]);         // 长度：3
// logLength(123);             // ❌ 编译错误：number 没有 length 属性
```

### 多个泛型参数

```typescript
// 函数接收两个类型不同的参数，返回一个组合后的对象
function pair<T, U>(first: T, second: U): [T, U] {
    return [first, second];
}

const result = pair<string, number>("张三", 18);  // [string, number]
const result2 = pair("hello", true);               // 自动推断 [string, boolean]
```

---

# 第 7 章 数据容器

## 概述

在编程中，我们经常需要一次保存多个数据，比如：多个学生的名字、一组商品的价格、或一串测量数据等等，如果把一条数据看作一个"物品"，那这些物品需要被放进"容器"里统一管理，在 TypeScript 中，常用的数据容器有：

1. 数组（Array）
2. 对象（Object）
3. 元组（Tuple）
4. Map / Set

## 数组（Array）

**数组：**用来存放一组**有序的数据**，并且可以对其中的数据进行：增删改查。

数组就像一个长度可变的收纳盒，能按顺序装下多个元素，还可以随时添加、拿出、替换里面的元素。

### 定义数组

```typescript
// 三种等价的定义方式
const list1: number[] = [34, 56, 21, 56, 11];
const list2: Array<string> = ["北京", "尚硅谷", "你好啊"];
const list3 = [23, "尚硅谷", true];  // 类型推断为 (string | number | boolean)[]

// 定义空数组（需要显式注明类型）
const empty1: number[] = [];
const empty2: Array<number> = [];

// 嵌套数组（多维数组）
const matrix: number[][] = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
];
```

### 下标（索引值）

下标又叫索引值，其实就是元素在数组中的"位置编号"，从 `0` 开始。

```typescript
const nums: number[] = [10, 20, 30, 40, 50];

console.log(nums[0]);   // 10（第一个元素）
console.log(nums[2]);   // 30（第三个元素）
console.log(nums[4]);   // 50（第五个元素）

// TypeScript 中数组没有负索引
// console.log(nums[-1]);  // undefined（运行时）
```

### 常用数组方法

```typescript
const fruits: string[] = ["苹果", "香蕉"];

// --- 添加 ---
fruits.push("橙子");            // 末尾添加 → ["苹果", "香蕉", "橙子"]
fruits.unshift("草莓");         // 开头添加 → ["草莓", "苹果", "香蕉", "橙子"]

// --- 删除 ---
const last = fruits.pop();      // 删除并返回末尾元素 → last = "橙子"
const first = fruits.shift();   // 删除并返回开头元素 → first = "草莓"

// --- 截取 ---
const nums = [1, 2, 3, 4, 5];
const slice1 = nums.slice(1, 3);   // [2, 3]（从索引1到3，不含3）
const slice2 = nums.slice(2);      // [3, 4, 5]（从索引2到末尾）

// --- 删除/替换/插入：splice ---
const arr = [10, 20, 30, 40, 50];
arr.splice(2, 1);             // 从索引2删除1个 → [10, 20, 40, 50]
arr.splice(1, 2, 99, 98);     // 从索引1删除2个，插入99和98 → [10, 99, 98, 50]

// --- 合并 ---
const combined = [1, 2].concat([3, 4]);  // [1, 2, 3, 4]
// 或者用展开运算符
const combined2 = [...[1, 2], ...[3, 4]]; // [1, 2, 3, 4]

// --- 查找 ---
const items = [10, 20, 30, 40];
console.log(items.indexOf(30));       // 2（元素30的索引，不存在返回 -1）
console.log(items.includes(20));      // true
console.log(items.find(n => n > 25)); // 30（第一个满足条件的元素）
console.log(items.findIndex(n => n > 25)); // 2

// --- 遍历方法 ---
// forEach：对每个元素执行操作（无返回值）
[1, 2, 3].forEach(n => console.log(n));

// map：对每个元素做转换，返回新数组
const doubled = [1, 2, 3].map(n => n * 2);  // [2, 4, 6]

// filter：过滤出满足条件的元素
const evens = [1, 2, 3, 4, 5].filter(n => n % 2 === 0);  // [2, 4]

// reduce：将数组归纳为单个值
const sum = [1, 2, 3, 4].reduce((total, n) => total + n, 0);  // 10
```

## 对象（Object）

对象是无序的**键值对（key-value）**集合，是 JavaScript/TypeScript 中最核心的数据结构之一。

### 定义对象

```typescript
// 字面量方式
const person: { name: string; age: number } = {
    name: "张三",
    age: 18
};

// 利用类型推断
const user = {
    name: "李四",
    age: 22,
    city: "北京"
};
// user 自动推断为 { name: string; age: number; city: string }

// 通过 interface 定义结构
interface Product {
    id: number;
    name: string;
    price: number;
}

const product: Product = {
    id: 1,
    name: "键盘",
    price: 299
};
```

### 访问和修改

```typescript
const person = { name: "张三", age: 18 };

// 点语法
console.log(person.name);   // 张三
person.age = 19;

// 方括号语法（支持动态 key）
console.log(person["name"]);  // 张三
const key = "age";
console.log(person[key]);     // 19
```

### 对象的方法

```typescript
// 获取所有键
Object.keys({ name: "张三", age: 18 });  // ["name", "age"]

// 获取所有值
Object.values({ name: "张三", age: 18 });  // ["张三", 18]

// 获取键值对数组
Object.entries({ name: "张三", age: 18 });  // [["name", "张三"], ["age", 18]]

// 合并对象（展开运算符）
const obj1 = { a: 1, b: 2 };
const obj2 = { c: 3, d: 4 };
const merged = { ...obj1, ...obj2 };  // { a: 1, b: 2, c: 3, d: 4 }

// 解构赋值
const { name, age } = person;
console.log(name, age);  // 张三 19

// 解构时重命名
const { name: userName, age: userAge } = person;
console.log(userName, userAge);  // 张三 19
```

## 元组（Tuple）

元组是 TypeScript 中一个**编译时**的数组类型，允许固定长度的数组里，每个位置的元素有不同的类型。

```typescript
// 基本元组
let pair: [string, number] = ["张三", 18];

// 包含可选元素的元组
let optional: [string, number?] = ["hello"];  // 第二个元素可选
optional = ["hello", 42];

// 剩余元素
let namedScores: [string, ...number[]] = ["张三", 85, 90, 88, 76];

// 解构赋值
let [userName2, age2] = pair;
console.log(userName2, age2);  // 张三 18
```

> 📢**再次强调：**TypeScript 元组运行时不具备不可变性，它可以像普通数组一样修改。这与 Python 元组完全不同。元组在 TS 中只提供**编译时**的类型形状约束。

## Map 与 Set

### Map

`Map` 是键值对的集合，与对象不同，它的键可以是**任意类型**（对象/函数/原始值皆可），且保持插入顺序。

```typescript
// 创建 Map
const map = new Map<string, number>();

// 添加
map.set("apple", 5);
map.set("banana", 3);
map.set("orange", 8);

// 获取
console.log(map.get("apple"));  // 5
console.log(map.get("grape"));   // undefined（不存在的 key）

// 判断是否存在
console.log(map.has("banana"));  // true

// 删除
map.delete("banana");

// 大小
console.log(map.size);  // 2

// 遍历
for (const [key, value] of map) {
    console.log(`${key}: ${value}`);
}

// 批量初始化
const map2 = new Map([
    ["key1", "value1"],
    ["key2", "value2"]
]);
```

### Set

`Set` 是**不重复**值的集合，每个值只能出现一次。

```typescript
const set = new Set<number>();

// 添加
set.add(10);
set.add(20);
set.add(10);  // 重复的值不会被添加
console.log(set.size);  // 2

// 判断是否存在
console.log(set.has(10));  // true

// 删除
set.delete(20);

// 遍历
for (const value of set) {
    console.log(value);
}

// 去重实战
const numbers = [1, 2, 2, 3, 3, 3, 4];
const unique = [...new Set(numbers)];  // [1, 2, 3, 4]
```

---

# 第 8 章 面向对象

## 类（Class）

### 概念

类是**对象的模板**，它定义了对象应该包含哪些数据（属性）和**能做什么**（方法）。根据类创建出来的一个个具体的对象叫**实例**。

> 🌰生活中的类比：
>
> - **类**就像汽车的设计图纸
> - **实例**就是根据图纸造出来的一辆辆具体的汽车
> - 图纸只有一份，但车可以造很多辆

### 类的定义与实例化

```typescript
class Person {
    name: string;
    age: number;

    constructor(name: string, age: number) {
        this.name = name;
        this.age = age;
    }

    greet(): string {
        return `你好，我是${this.name}，今年${this.age}岁`;
    }
}

// 创建实例
const p1 = new Person("张三", 18);
const p2 = new Person("李四", 22);

console.log(p1.greet());  // 你好，我是张三，今年18岁
console.log(p2.greet());  // 你好，我是李四，今年22岁
```

> 📋**说明：**
> - `constructor` 是构造函数，创建实例（`new`）时自动调用，用于初始化实例属性。
> - `this` 指向当前实例对象。

### 访问修饰符

TypeScript 为类属性/方法提供了**三种**编译时的访问修饰符。这些都是 TypeScript 特有的，运行时在 JavaScript 中是可访问的（除非在 JS 中使用 `#` 私有字段）。

| 修饰符 | 含义 | 能否在子类中访问 | 能否在外部访问 |
| :---: | --- | :---: | :---: |
| `public` | 公开（默认） | ✅ | ✅ |
| `protected` | 受保护 | ✅ | ❌ |
| `private` | 私有 | ❌ | ❌ |

```typescript
class Animal {
    public name: string;           // 公开：任何地方都能访问
    protected age: number;         // 受保护：类内部 + 子类可访问
    private internalId: string;    // 私有：仅类内部可访问

    constructor(name: string, age: number, id: string) {
        this.name = name;
        this.age = age;
        this.internalId = id;
    }

    showInternalId() {
        console.log(this.internalId);  // ✅ 类内部可访问
    }
}

const animal = new Animal("🐱", 2, "CAT001");
console.log(animal.name);        // ✅ public：可访问
// console.log(animal.age);      // ❌ 编译错误：protected 不可外部访问
// console.log(animal.internalId); // ❌ 编译错误：private 不可外部访问

class Dog extends Animal {
    showAge() {
        console.log(this.age);   // ✅ protected：子类可访问
        // console.log(this.internalId); // ❌ private：子类不可访问
    }
}
```

此外，TypeScript 还支持**参数属性**语法（在构造函数参数前加修饰符，自动生成并赋值属性）：

```typescript
class User {
    // 简写：构造函数中直接声明和初始化
    constructor(
        public name: string,       // 自动声明并赋值为 public 属性
        public readonly id: number, // 自动声明为 readonly 属性
        private password: string    // 自动声明为 private 属性
    ) {}

    showName() {
        console.log(this.name);
    }
}

const user = new User("张三", 1, "secret");
console.log(user.name);  // 张三
console.log(user.id);    // 1
// console.log(user.password); // ❌ 编译错误
```

### 只读属性（readonly）

```typescript
class Config {
    readonly version: string = "1.0";
    readonly port: number;

    constructor(port: number) {
        this.port = port;  // 只读属性只能在声明时或构造函数中赋值
    }

    updateVersion() {
        // this.version = "2.0";  // ❌ 编译错误
    }
}

const cfg = new Config(8080);
console.log(cfg.port);   // 8080
// cfg.port = 3000;      // ❌ 编译错误：只读
```

## 继承

继承允许一个类**复用**另一个类的属性和方法。

```typescript
// 父类（基类）
class Animal {
    name: string;

    constructor(name: string) {
        this.name = name;
    }

    makeSound(): string {
        return "动物发出叫声";
    }
}

// 子类使用 extends 继承父类
class Cat extends Animal {
    // 子类可以添加自己的属性
    color: string;

    constructor(name: string, color: string) {
        super(name);         // 必须先调用 super() 初始化父类
        this.color = color;
    }

    // 覆盖父类方法
    makeSound(): string {
        return `${this.name}说：喵喵喵！`;
    }

    // 新增方法
    climb(): string {
        return `${this.name}在爬树`;
    }
}

const cat = new Cat("小花", "橘色");
console.log(cat.name);        // 小花（继承自 Animal）
console.log(cat.color);       // 橘色
console.log(cat.makeSound()); // 小花说：喵喵喵！（覆盖后的方法）
console.log(cat.climb());     // 小花在爬树
```

> 📢**注意：**在子类的 `constructor` 中，必须先用 `super()` 调用父类构造函数，然后才能使用 `this`。

## 抽象类

抽象类**不能直接实例化**，只能被继承，用于定义一些子类**必须实现**的方法。

```typescript
abstract class Animal {
    name: string;

    constructor(name: string) {
        this.name = name;
    }

    // 普通方法
    sleep(): void {
        console.log(`${this.name}正在睡觉`);
    }

    // 抽象方法（子类必须实现）
    abstract makeSound(): void;
}

// const animal = new Animal("动物");  // ❌ 编译错误：不能实例化抽象类

class Dog extends Animal {
    // 子类必须实现抽象方法
    makeSound(): void {
        console.log(`${this.name}说：汪汪汪！`);
    }
}

const dog = new Dog("大黄");
dog.makeSound();  // 大黄说：汪汪汪！
dog.sleep();      // 大黄正在睡觉
```

## 接口与类

### 类实现接口（implements）

接口定义了类必须遵循的"行为契约"，让类必须实现接口中的属性和方法：

```typescript
interface Flyable {
    fly(): void;
}

interface Swimmable {
    swim(): void;
}

// 一个类可以实现多个接口
class Duck implements Flyable, Swimmable {
    fly(): void {
        console.log("鸭子在飞");
    }

    swim(): void {
        console.log("鸭子在游");
    }
}

const duck = new Duck();
duck.fly();   // 鸭子在飞
duck.swim();  // 鸭子在游
```

### 接口继承接口

```typescript
interface Animal {
    name: string;
    eat(): void;
}

interface Pet extends Animal {
    ownerName: string;
    play(): void;
}

// Pet 同时拥有 Animal 的属性方法和自己的属性方法
const myPet: Pet = {
    name: "旺财",
    ownerName: "张三",
    eat() {
        console.log("吃东西");
    },
    play() {
        console.log("玩耍");
    }
};
```

## 泛型类

```typescript
// 泛型类：数据仓库，可以存放任意类型的数据
class Box<T> {
    private content: T;

    constructor(content: T) {
        this.content = content;
    }

    getContent(): T {
        return this.content;
    }

    setContent(content: T): void {
        this.content = content;
    }
}

const stringBox = new Box<string>("一本书");
console.log(stringBox.getContent());  // 一本书

const numberBox = new Box<number>(42);
console.log(numberBox.getContent());  // 42
```

---

# 第 9 章 错误与异常

## 错误与异常

**错误：**代码本身有语法错误，解释器/编译器无法执行。—— **无法**通过异常处理机制解决。

```typescript
// 语法错误示例（编译阶段就报错）
// const age = 18
// if age >= 18 {  // 少写了括号
//     console.log('成年人');
// }
```

**异常：**代码在语法上没问题，但执行过程中出现了问题。—— **可以**通过异常处理机制解决。

```typescript
// 1. RangeError：数值超出有效范围
const arr = new Array(9999999999);  // RangeError

// 2. ReferenceError：使用了未声明的变量（TS 在编译时就能发现）
// console.log(undefinedVariable);   // ReferenceError

// 3. TypeError：操作的数据类型不正确
const num: any = null;
// num.toFixed();  // TypeError: Cannot read properties of null

// 4. URIError：URI 编解码出错
// decodeURIComponent('%');  // URIError
```

## 异常处理 try...catch...finally

```typescript
try {
    // 可能抛出异常的代码
    const result = JSON.parse('{"name": "张三"');  // 故意写一个格式错误的 JSON
    console.log(result);
} catch (error) {
    // 捕获并处理异常
    console.log("捕获到异常：", (error as Error).message);
} finally {
    // 无论是否发生异常，都会执行
    console.log("清理工作完成");
}
```

## throw 主动抛出异常

```typescript
function divide(a: number, b: number): number {
    if (b === 0) {
        throw new Error("除数不能为零！");
    }
    return a / b;
}

try {
    console.log(divide(10, 0));
} catch (error) {
    console.log((error as Error).message);  // 除数不能为零！
}
```

## 自定义错误类

```typescript
class ValidationError extends Error {
    constructor(message: string) {
        super(message);
        this.name = "ValidationError";  // 设置错误名称
    }
}

function validateAge(age: number): void {
    if (age < 0 || age > 150) {
        throw new ValidationError(`无效的年龄：${age}，年龄应在0-150之间`);
    }
}

try {
    validateAge(200);
} catch (error) {
    if (error instanceof ValidationError) {
        console.log("验证错误：", error.message);
    } else {
        console.log("未知错误：", error);
    }
}
```

## 错误类型体系

JavaScript/TypeScript 中的主要内置错误类型：

```
Error（所有错误的基类）
├── EvalError              —— eval() 使用不当
├── RangeError             —— 数值超出有效范围
├── ReferenceError         —— 引用了不存在的变量
├── SyntaxError            —— 语法错误
├── TypeError              —— 类型错误（最常见）
└── URIError               —— URI 编解码错误
```

---

# 第 10 章 模块系统

## 模块的概念

模块是**组织代码**的基本方式。把一个大程序拆分成多个独立的小文件（模块），每个模块负责特定的功能，然后通过导入导出来组合使用。

优势：
1. **代码组织清晰**：一个文件一个关注点
2. **避免命名冲突**：每个模块有自己的作用域
3. **可复用性强**：一个模块可以被多个地方引用

## ES Module（推荐）

TypeScript 推荐使用 ES Module 语法（`import`/`export`）。

### 导出（export）

```typescript
// ===== file: math.ts =====

// 命名导出
export function add(a: number, b: number): number {
    return a + b;
}

export function subtract(a: number, b: number): number {
    return a - b;
}

export const PI = 3.14159;

// 默认导出（每个模块只能有一个）
export default function multiply(a: number, b: number): number {
    return a * b;
}
```

### 导入（import）

```typescript
// ===== file: main.ts =====

// 命名导入
import { add, subtract, PI } from "./math";

// 默认导入（名字可以自己取）
import multiply from "./math";

// 同时导入默认和命名
import mul, { add, PI } from "./math";

// 全部导入（作为命名空间）
import * as math from "./math";
console.log(math.add(1, 2));     // 3
console.log(math.subtract(5, 3)); // 2

// 使用
console.log(add(1, 2));      // 3
console.log(subtract(5, 3));  // 2
console.log(multiply(3, 4));  // 12
console.log(PI);              // 3.14159
```

### 导入时重命名

```typescript
import { add as plus, subtract as minus } from "./math";
console.log(plus(1, 2));  // 3
```

### re-export（重新导出）

```typescript
// ===== file: index.ts =====
// 将多个模块的导出汇总到一个入口
export { add, subtract } from "./math";
export { default as multiply } from "./math";
```

---

# 第 11 章 初识 Node.js

## Node.js 概述

### 什么是 Node.js？

Node.js 是一个基于 **Chrome V8 引擎** 的 **JavaScript 运行时环境**。它让 JavaScript 可以脱离浏览器，在服务器端运行。

> 🌰简单来说：浏览器让 JS 能在网页上跑，Node.js 让 JS 能在你的电脑上作为一个独立程序来跑——操作文件、启动服务器、连接数据库都不在话下。

### Node.js 的诞生

2009 年，**Ryan Dahl** 创建了 Node.js。他的核心想法是：传统的 Web 服务器（如 Apache）在处理大量并发请求时，每个请求都要开一个线程，资源开销很大。而 Node.js 基于 **事件驱动** 和 **非阻塞 I/O** 模型，用一个进程就能高效处理成千上万个并发连接。

### Node.js 的特点

| 特点 | 说明 |
| :---: | --- |
| **单线程 + 事件驱动** | 使用一个主线程 + Event Loop 来处理并发，无需为每个请求创建线程 |
| **非阻塞 I/O** | 文件读写、网络请求等 I/O 操作不会阻塞主线程 |
| **NPM 生态** | 拥有全球最大的开源包管理生态（npm），超过 200 万个包 |
| **跨平台** | 支持 Windows、macOS、Linux |
| **全栈能力** | 前端（浏览器JS）和后端（Node.js）使用同一种语言 |

### Node.js 版本说明

Node.js 每 6 个月发布一个大版本，分为：
- **LTS（Long Term Support）**：偶数版本，长期支持，推荐生产环境使用
- **Current**：奇数版本，试验性新特性，适合尝鲜

截至 2025 年，推荐使用的 LTS 版本为 Node.js 22.x。

## Node.js REPL

REPL（Read-Eval-Print Loop）是 Node.js 提供的交互式解释器，可以在终端中直接输入并执行 JavaScript 代码：

```bash
node
```

```javascript
> 1 + 1
2
> console.log("Hello, Node.js!")
Hello, Node.js!
undefined
> const name = "张三"
undefined
> `你好，${name}`
'你好，张三'
>
```

按两次 `Ctrl+C` 或一次 `Ctrl+D` 退出。

## npm（Node Package Manager）

npm 是 Node.js 的包管理器，用于：
- 安装和管理第三方库
- 管理项目依赖
- 运行脚本

### 初始化项目

```bash
npm init -y  # -y 表示使用默认配置
```

会在当前目录创建 `package.json` 文件。

### package.json 核心字段

```json
{
  "name": "my-app",              // 项目名称
  "version": "1.0.0",           // 版本号
  "description": "项目描述",     // 项目描述
  "main": "dist/index.js",      // 入口文件
  "scripts": {                  // 脚本命令
    "start": "node dist/index.js",
    "build": "tsc",
    "dev": "ts-node src/index.ts"
  },
  "dependencies": {             // 生产依赖
    "express": "^4.18.2"
  },
  "devDependencies": {          // 开发依赖（仅开发时需要）
    "typescript": "^5.4.0",
    "ts-node": "^10.9.0"
  }
}
```

### 安装依赖

```bash
# 安装生产依赖
npm install express

# 安装开发依赖
npm install -D typescript @types/node

# 全局安装
npm install -g typescript

# 根据 package.json 安装所有依赖
npm install
```

### 运行脚本

```bash
npm run start    # 运行 package.json 中 scripts 下的 "start"
npm run build    # 运行 "build"
npm run dev      # 运行 "dev"
```

## CommonJS vs ES Module

Node.js 中主要有两套模块系统：

| 对比维度 | CommonJS | ES Module |
| :---: | --- | --- |
| 导出语法 | `module.exports = {}` | `export default` / `export {}` |
| 导入语法 | `const xxx = require("xxx")` | `import xxx from "xxx"` |
| 加载时机 | 运行时同步加载 | 编译时静态分析，运行时异步加载 |
| 是否可条件导入 | 可以（`if` 中 `require`） | 不可以（顶层 `import` 静态） |
| Node.js 默认 | 是（`.js` 文件默认） | 需要 `.mjs` 或在 `package.json` 设置 `"type": "module"` |
| 推荐 | 历史遗留项目仍在使用 | **新项目推荐** |

```typescript
// ===== CommonJS 风格 =====
// 导出（math.cjs）
const PI = 3.14;
function add(a, b) { return a + b; }
module.exports = { PI, add };

// 导入
const { PI, add } = require("./math.cjs");

// ===== ES Module 风格（推荐） =====
// 导出（math.ts）
export const PI = 3.14;
export function add(a: number, b: number): number { return a + b; }

// 导入（main.ts）
import { PI, add } from "./math";
```

---

# 第 12 章 异步编程

## 同步 vs 异步

这是理解 Node.js 最核心的概念之一。

### 同步（Synchronous）

代码**一行一行顺序执行**，前一行没执行完，后一行就必须等着。

```typescript
console.log("第一步");
console.log("第二步");
console.log("第三步");
// 输出：
// 第一步
// 第二步
// 第三步
```

> 🌰类比：你去银行排队办业务，前面的人没办完，你就必须一直等着——这就是同步。

### 异步（Asynchronous）

当一个操作需要等待（如读取文件）时，程序不会**阻塞**在原地，而是**继续执行后面的代码**，等操作完成后再通过**回调/通知**来处理结果。

```typescript
console.log("第一步");

// setTimeout 是异步操作，不会阻塞
setTimeout(() => {
    console.log("延时 2 秒后执行");
}, 2000);

console.log("第二步");
// 输出：
// 第一步
// 第二步
// （2秒后）延时 2 秒后执行
```

> 🌰类比：你去餐厅点菜，点完单后不用在柜台等着，可以坐下玩手机，菜好了服务员会端给你——这就是异步。

## 回调函数（Callback）

回调函数是最基础的异步处理方式：把一个函数作为参数传给异步操作，操作完成后调用该函数。

```typescript
import * as fs from "fs";

console.log("开始读取文件");

fs.readFile("test.txt", "utf8", (err, data) => {
    if (err) {
        console.log("读取失败：", err.message);
        return;
    }
    console.log("文件内容：", data);
});

console.log("继续执行其他代码");
// 输出：
// 开始读取文件
// 继续执行其他代码
// 文件内容：Hello, World!（等文件读取完毕后回调执行）
```

### 回调地狱（Callback Hell）

当多个异步操作存在依赖关系时，回调会层层嵌套，代码难以阅读和维护：

```typescript
// 回调地狱示例（模拟：读文件A → 处理 → 读文件B → 处理 → 写文件C）
fs.readFile("a.txt", "utf8", (err, dataA) => {
    if (err) return console.error(err);
    const processedA = dataA.trim();

    fs.readFile("b.txt", "utf8", (err, dataB) => {
        if (err) return console.error(err);
        const processedB = dataB.trim();

        const result = processedA + processedB;
        fs.writeFile("c.txt", result, (err) => {
            if (err) return console.error(err);
            console.log("写入完成");

            fs.readFile("c.txt", "utf8", (err, data) => {
                if (err) return console.error(err);
                console.log("验证：", data);
                // 如果再嵌套下去……
            });
        });
    });
});
```

## Promise

`Promise` 是 ES6 引入的解决方案，它用**链式调用**替代了层层嵌套的回调。

### Promise 的三种状态

| 状态 | 说明 |
| :---: | --- |
| **pending**（待定） | Promise 刚创建，异步操作还在进行中 |
| **fulfilled**（已兑现） | 异步操作成功，通过 `resolve()` 触发 |
| **rejected**（已拒绝） | 异步操作失败，通过 `reject()` 触发 |

状态一旦从 `pending` 变为 `fulfilled` 或 `rejected`，就**不可逆转**。

### 基本用法

```typescript
// 创建 Promise
const promise = new Promise<string>((resolve, reject) => {
    // 异步操作
    setTimeout(() => {
        const success = true;
        if (success) {
            resolve("操作成功！");  // 转为 fulfilled
        } else {
            reject(new Error("操作失败！"));  // 转为 rejected
        }
    }, 1000);
});

// 使用 then/catch 处理
promise
    .then((result) => {
        console.log(result);  // 操作成功！
    })
    .catch((error) => {
        console.error(error.message);
    });
```

### 链式调用（then 链）

`.then()` 返回的也是 Promise，因此可以链式调用：

```typescript
function readFileAsync(path: string): Promise<string> {
    return new Promise((resolve, reject) => {
        fs.readFile(path, "utf8", (err, data) => {
            if (err) reject(err);
            else resolve(data);
        });
    });
}

readFileAsync("a.txt")
    .then((dataA) => {
        const processed = dataA.trim();
        return readFileAsync("b.txt").then((dataB) => processed + dataB.trim());
    })
    .then((result) => {
        console.log("最终结果：", result);
    })
    .catch((error) => {
        console.error("出错：", error.message);
    });
```

### Promise 静态方法

```typescript
// Promise.all：等待所有 Promise 完成（有一个失败就整体失败）
const [result1, result2, result3] = await Promise.all([
    fetchUser(1),
    fetchUser(2),
    fetchUser(3)
]);

// Promise.race：返回最先完成的 Promise（无论成功或失败）
const fastest = await Promise.race([
    fetchFromServer("server1"),
    fetchFromServer("server2")
]);

// Promise.allSettled：等待所有 Promise 都完成（不管成功或失败）
const results = await Promise.allSettled([
    fetchUser(1),
    fetchUser(999)  // 即使这个失败了，还会拿到结果
]);
```

## async / await

`async/await` 是 ES2017 引入的语法糖，让异步代码**写起来像同步代码**，是目前最推荐的异步处理方式。

```typescript
// async 声明函数返回 Promise
async function processData(): Promise<string> {
    // await 等待 Promise 完成，获取结果
    const dataA = await readFileAsync("a.txt");
    const dataB = await readFileAsync("b.txt");
    return dataA.trim() + dataB.trim();
}

// 调用
async function main() {
    try {
        const result = await processData();
        console.log(result);
    } catch (error) {
        console.error("出错：", (error as Error).message);
    }
}

main();
```

### 关键规则

```typescript
// 1. await 只能在 async 函数内部使用
async function example() {
    const data = await somePromise();  // ✅
}
// const data = await somePromise();  // ❌ 不能在顶层使用（除非是顶级 await 的 ES module）

// 2. async 函数默认返回 Promise
async function getValue(): Promise<number> {
    return 42;  // 自动包装成 Promise.resolve(42)
}

// 3. 多个独立的异步操作可以并行
async function fetchAll() {
    // ❌ 串行执行（不推荐）
    const user = await fetchUser();
    const posts = await fetchPosts();  // 等 user 完成才开始

    // ✅ 并行执行（推荐）
    const [user2, posts2] = await Promise.all([
        fetchUser(),
        fetchPosts()   // 两个请求同时发出
    ]);
}
```

## Event Loop（事件循环）

Event Loop 是 Node.js 异步非阻塞的核心机制。理解它需要区分几种"队列"：

### 宏任务与微任务

| 分类 | 包含 | 执行时机 |
| :---: | --- | --- |
| **宏任务**（Macro Task） | `setTimeout`、`setInterval`、I/O 回调、`setImmediate`（Node.js） | 每次 Event Loop 的某一阶段执行 |
| **微任务**（Micro Task） | `Promise.then/catch/finally`、`queueMicrotask`、`process.nextTick`（Node.js） | 每个宏任务执行完毕后**立即**执行（且会清空微任务队列） |

### 执行顺序示例

```typescript
console.log("1. 同步代码开始");

setTimeout(() => {
    console.log("2. setTimeout 回调（宏任务）");
}, 0);

Promise.resolve().then(() => {
    console.log("3. Promise.then 回调（微任务）");
});

console.log("4. 同步代码结束");

// 输出顺序：
// 1. 同步代码开始
// 4. 同步代码结束
// 3. Promise.then 回调（微任务）
// 2. setTimeout 回调（宏任务）
```

**解释**：同步代码最先执行 → 然后清空微任务队列（Promise.then）→ 最后执行宏任务（setTimeout），即使 setTimeout 的延迟是 0。

> 📢**这是 Node.js 面试高频考点**，务必理解透彻。

---

# 第 13 章 文件操作

## fs 模块

Node.js 通过内置的 `fs`（File System）模块来操作文件。所有文件操作都有**同步**、**回调**、**Promise** 三种方式，推荐使用 Promise 方式。

```typescript
import * as fs from "fs";
import * as fsPromises from "fs/promises";  // Promise 版本（推荐）
```

### 读取文件

```typescript
import * as fs from "fs/promises";

async function readFile() {
    try {
        // 一次性读取整个文件
        const data = await fs.readFile("test.txt", "utf8");
        console.log(data);
    } catch (err) {
        console.error("读取失败：", (err as Error).message);
    }
}

readFile();
```

### 写入文件

```typescript
import * as fs from "fs/promises";

async function writeFile() {
    try {
        // 写入文件（会覆盖已有内容）
        await fs.writeFile("output.txt", "Hello, Node.js!", "utf8");
        console.log("写入成功");

        // 追加内容（不会覆盖）
        await fs.appendFile("output.txt", "\n追加的一行内容", "utf8");
        console.log("追加成功");
    } catch (err) {
        console.error("写入失败：", (err as Error).message);
    }
}

writeFile();
```

### 创建和删除目录

```typescript
import * as fs from "fs/promises";

async function manageDir() {
    // 创建目录（recursive: true 表示递归创建所有不存在的父目录）
    await fs.mkdir("./data/logs", { recursive: true });

    // 删除空目录
    await fs.rmdir("./data/logs");

    // 删除目录及其中的所有内容
    await fs.rm("./data", { recursive: true, force: true });
}
```

### 检查文件/目录状态

```typescript
import * as fs from "fs/promises";

async function checkPath() {
    try {
        const stats = await fs.stat("test.txt");
        console.log("文件大小（字节）：", stats.size);
        console.log("是文件：", stats.isFile());     // true
        console.log("是目录：", stats.isDirectory()); // false
        console.log("最后修改时间：", stats.mtime);
    } catch (err) {
        console.error("路径不存在：", (err as Error).message);
    }
}
```

### 列出目录内容

```typescript
import * as fs from "fs/promises";

async function listDir() {
    const files = await fs.readdir("./src");
    console.log(files);  // ["index.ts", "utils.ts", ...]
}
```

## 文件流（Stream）

当文件**很大**时（比如几个 GB），一次性读到内存会导致内存爆满。`Stream` 可以**分块**读取或写入，极大降低内存占用。

```typescript
import * as fs from "fs";

// 创建可读流
const readStream = fs.createReadStream("large-file.txt", { encoding: "utf8" });

// 监听 data 事件，每次读取一个 chunk
readStream.on("data", (chunk: string) => {
    console.log("收到一块数据，大小：", chunk.length);
});

readStream.on("end", () => {
    console.log("文件读取完毕");
});

readStream.on("error", (err) => {
    console.error("读取出错：", err.message);
});
```

**管道（pipe）—— 将可读流直接连接到可写流：**

```typescript
import * as fs from "fs";

// 从 source.txt 读取内容，写入 dest.txt
const readStream = fs.createReadStream("source.txt");
const writeStream = fs.createWriteStream("dest.txt");

readStream.pipe(writeStream);

writeStream.on("finish", () => {
    console.log("复制完成");
});
```

## Buffer

`Buffer` 是 Node.js 中专门用来处理**二进制数据**的类。文件读写、网络传输、图片处理等场景都会用到。

```typescript
// 创建一个 Buffer
const buf1 = Buffer.from("Hello");      // 从字符串创建
const buf2 = Buffer.alloc(10);           // 分配 10 字节（初始化为 0）
const buf3 = Buffer.allocUnsafe(10);    // 分配 10 字节（不初始化，更快但不安全）

console.log(buf1);         // <Buffer 48 65 6c 6c 6f>
console.log(buf1.length);  // 5

// Buffer 与字符串互转
const str = buf1.toString("utf8");  // "Hello"
console.log(str);

// 读取文件时默认返回 Buffer
import * as fs from "fs/promises";
async function readAsBuffer() {
    const buffer = await fs.readFile("test.txt");  // 不指定编码 => Buffer
    console.log(buffer);        // <Buffer ...>
    console.log(buffer.toString("utf8"));  // 转为字符串
}
```

## path 模块

`path` 模块用于**处理文件路径**，避免在不同操作系统中因斜杠方向（`/` vs `\`）导致的兼容性问题。

```typescript
import * as path from "path";

// 拼接路径（自动处理分隔符）
const fullPath = path.join("/home", "user", "docs", "file.txt");
// 在 macOS/Linux：/home/user/docs/file.txt
// 在 Windows：\home\user\docs\file.txt

// 获取文件扩展名
console.log(path.extname("index.html"));  // .html

// 获取文件名
console.log(path.basename("/home/user/file.txt"));  // file.txt

// 获取目录名
console.log(path.dirname("/home/user/file.txt"));  // /home/user

// 解析路径（返回对象）
const parsed = path.parse("/home/user/file.txt");
// { root: "/", dir: "/home/user", base: "file.txt", ext: ".txt", name: "file" }
```

---

# 第 14 章 网络编程

## HTTP 模块

Node.js 内置了 `http` 模块，可以直接创建 HTTP 服务器，**无需安装任何第三方依赖**。

### 创建一个最简 HTTP 服务器

```typescript
import * as http from "http";

const server = http.createServer((req, res) => {
    // 设置响应头
    res.setHeader("Content-Type", "text/plain; charset=utf-8");

    // 根据请求的 URL 返回不同内容
    if (req.url === "/") {
        res.statusCode = 200;
        res.end("你好，这是首页");
    } else if (req.url === "/about") {
        res.statusCode = 200;
        res.end("这是关于页面");
    } else {
        res.statusCode = 404;
        res.end("页面未找到");
    }
});

// 监听端口
const PORT = 3000;
server.listen(PORT, () => {
    console.log(`服务器已启动：http://localhost:${PORT}`);
});
```

测试方法：在终端执行 `node server.js`，然后浏览器打开 `http://localhost:3000` 即可看到。

### 请求（Request）对象

```typescript
const server = http.createServer((req, res) => {
    console.log("请求方法：", req.method);   // GET、POST、PUT、DELETE 等
    console.log("请求路径：", req.url);       // /api/users?id=1
    console.log("请求头：", req.headers);     // { 'content-type': 'application/json', ... }

    res.end("OK");
});
```

### 接收 JSON 请求体

```typescript
const server = http.createServer(async (req, res) => {
    if (req.method === "POST" && req.url === "/api/users") {
        // 读取请求体（数据可能分块到达，需要手动拼接）
        let body = "";
        for await (const chunk of req) {
            body += chunk.toString();
        }

        try {
            const data = JSON.parse(body);
            console.log("收到数据：", data);

            res.statusCode = 201;
            res.setHeader("Content-Type", "application/json; charset=utf-8");
            res.end(JSON.stringify({ success: true, message: "用户创建成功" }));
        } catch {
            res.statusCode = 400;
            res.end(JSON.stringify({ success: false, message: "JSON 格式错误" }));
        }
    } else {
        res.statusCode = 404;
        res.end("Not Found");
    }
});
```

## 初识 Express

`http` 模块虽然能用，但每次都要手动处理路由、解析请求体、设置响应头……在实际项目中，一般使用更高级的 Web 框架，最流行的就是 **Express**。

```bash
npm install express
npm install -D @types/express
```

### 基本的 Express 应用

```typescript
import express, { Request, Response } from "express";

const app = express();
const PORT = 3000;

// 内置中间件：解析 JSON 请求体
app.use(express.json());

// 路由
app.get("/", (req: Request, res: Response) => {
    res.send("你好，这是首页");
});

app.get("/users", (req: Request, res: Response) => {
    res.json([
        { id: 1, name: "张三" },
        { id: 2, name: "李四" }
    ]);
});

app.post("/users", (req: Request, res: Response) => {
    const newUser = req.body;
    console.log("收到新用户：", newUser);
    res.status(201).json({
        success: true,
        data: newUser
    });
});

// 启动服务器
app.listen(PORT, () => {
    console.log(`服务器已启动：http://localhost:${PORT}`);
});
```

### 中间件的概念

**中间件（Middleware）** 是 Express 的核心概念。每个中间件是一个函数，它接收请求对象 `req`、响应对象 `res` 和 `next` 函数，可以在请求到达最终路由之前对请求做处理。

```typescript
import express, { Request, Response, NextFunction } from "express";

const app = express();

// 自定义中间件（记录每个请求）
app.use((req: Request, res: Response, next: NextFunction) => {
    console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`);
    next();  // 必须调用 next()，否则请求会"卡住"
});

// 错误处理中间件（四个参数）
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
    console.error("服务器错误：", err.message);
    res.status(500).json({ error: "服务器内部错误" });
});

// 路由
app.get("/", (req, res) => {
    res.send("Hello World");
});

app.listen(3000);
```

### RESTful API 完整示例

```typescript
import express, { Request, Response } from "express";

const app = express();
app.use(express.json());

interface Todo {
    id: number;
    title: string;
    completed: boolean;
}

let todos: Todo[] = [
    { id: 1, title: "学习 TypeScript", completed: true },
    { id: 2, title: "学习 Node.js", completed: false }
];

// GET     /api/todos     获取所有任务
// POST    /api/todos     创建新任务
// PUT     /api/todos/:id 更新任务
// DELETE  /api/todos/:id 删除任务

app.get("/api/todos", (req: Request, res: Response) => {
    res.json(todos);
});

app.post("/api/todos", (req: Request, res: Response) => {
    const newTodo: Todo = {
        id: todos.length + 1,
        title: req.body.title,
        completed: false
    };
    todos.push(newTodo);
    res.status(201).json(newTodo);
});

app.put("/api/todos/:id", (req: Request, res: Response) => {
    const id = parseInt(req.params.id);
    const todo = todos.find(t => t.id === id);
    if (!todo) {
        return res.status(404).json({ message: "任务不存在" });
    }
    todo.title = req.body.title ?? todo.title;
    todo.completed = req.body.completed ?? todo.completed;
    res.json(todo);
});

app.delete("/api/todos/:id", (req: Request, res: Response) => {
    const id = parseInt(req.params.id);
    const index = todos.findIndex(t => t.id === id);
    if (index === -1) {
        return res.status(404).json({ message: "任务不存在" });
    }
    todos.splice(index, 1);
    res.status(204).send();  // 204 No Content
});

app.listen(3000, () => {
    console.log("http://localhost:3000");
});
```

---

# 第 15 章 进程与线程

## 概述

默认情况下，Node.js 运行在**单线程**中（主线程），所有 JavaScript 代码都在这个线程上执行。事件循环让这个单线程能够高效处理并发 I/O。

但面对 **CPU 密集型任务**（如大量运算、图像处理等），单线程会"忙不过来"——事件循环被阻塞，连其他请求都无法响应。此时就需要多进程或多线程来解决。

> 🌰类比：
> - **单线程**：一个厨师一个灶台，炒菜、洗菜、切菜都是他一个人干。
> - **多进程/多线程**：雇多个厨师，每人一个灶台，可以同时干活。

## Child Process（子进程）

`child_process` 模块可以创建独立的子进程，每个子进程有自己的 V8 实例和内存空间。

### 创建子进程的四种方式

| 方法 | 说明 |
| :---: | --- |
| `exec` | 执行命令，缓存输出，适合执行简单命令（短输出） |
| `execFile` | 执行可执行文件，不启动 shell，比 `exec` 更高效 |
| `spawn` | 以流的方式执行命令，适合输出大量数据或长时间运行的程序 |
| `fork` | `spawn` 的变体，专门用于创建新的 Node.js 进程，自带 IPC 通信通道 |

### exec 示例

```typescript
import { exec } from "child_process";

exec("ls -la", (error, stdout, stderr) => {
    if (error) {
        console.error("执行出错：", error.message);
        return;
    }
    console.log("输出：\n", stdout);
});
```

### spawn 示例

```typescript
import { spawn } from "child_process";

// 执行长时间运行的命令
const child = spawn("ping", ["-c", "4", "google.com"]);

// 逐行接收输出
child.stdout.on("data", (data: Buffer) => {
    console.log(`输出：${data.toString()}`);
});

child.stderr.on("data", (data: Buffer) => {
    console.error(`错误：${data.toString()}`);
});

child.on("close", (code: number) => {
    console.log(`子进程退出，状态码：${code}`);
});
```

### fork 示例（Node.js 进程间通信）

```typescript
// ===== 主进程：main.ts =====
import { fork } from "child_process";

const child = fork("./worker.ts");  // 创建子进程（另起一个 Node.js 进程执行 worker.ts）

// 向子进程发送消息
child.send({ task: "计算", numbers: [1, 2, 3, 4, 5] });

// 接收子进程的消息
child.on("message", (result) => {
    console.log("子进程返回结果：", result);
});

// ===== 子进程：worker.ts =====
process.on("message", (msg: { task: string; numbers: number[] }) => {
    if (msg.task === "计算") {
        const sum = msg.numbers.reduce((a, b) => a + b, 0);
        // 将结果发送回主进程
        process.send!({ result: sum });
    }
});
```

## Worker Threads（工作线程）

Node.js 12 开始稳定支持的 **Worker Threads**， 让 Node.js 的主线程可以创建**真正的多线程**。与子进程不同，工作线程共享进程内存（通过 `SharedArrayBuffer`），开销更小。

适合 CPU 密集型任务（加密、压缩、大量运算等）。

```typescript
// ===== 主线程：main.ts =====
import { Worker } from "worker_threads";
import * as path from "path";

function runHeavyTask(data: number): Promise<number> {
    return new Promise((resolve, reject) => {
        const worker = new Worker(path.join(__dirname, "worker.js"), {
            workerData: data  // 传递初始数据给工作线程
        });

        worker.on("message", (result: number) => {
            resolve(result);
        });

        worker.on("error", (err) => {
            reject(err);
        });

        worker.on("exit", (code) => {
            if (code !== 0) {
                reject(new Error(`Worker 异常退出，退出码：${code}`));
            }
        });
    });
}

async function main() {
    try {
        const result = await runHeavyTask(1000000);
        console.log("计算结果：", result);
    } catch (err) {
        console.error("出错：", (err as Error).message);
    }
}

main();

// ===== 工作线程：worker.js =====
import { parentPort, workerData } from "worker_threads";

// 进行 CPU 密集型运算
function fibonacci(n: number): number {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

const result = fibonacci(workerData);
parentPort?.postMessage(result);
```

## Cluster 模块

`cluster` 模块利用**多进程**来充分利用多核 CPU，主进程将端口分发给多个子进程（Worker），每个子进程独立处理请求。这是 Node.js 在生产环境中扩展能力的常用方式。

```typescript
import cluster from "cluster";
import * as http from "http";
import { cpus } from "os";

if (cluster.isPrimary) {
    // 主进程：创建工作进程
    const numCPUs = cpus().length;
    console.log(`主进程 ${process.pid} 正在运行`);
    console.log(`正在启动 ${numCPUs} 个工作进程……`);

    // 为每个 CPU 核心创建一个子进程
    for (let i = 0; i < numCPUs; i++) {
        cluster.fork();  // 启动子进程
    }

    // 监听子进程退出并自动重启
    cluster.on("exit", (worker, code) => {
        console.log(`工作进程 ${worker.process.pid} 已退出，状态码：${code}`);
        console.log("正在重启新的工作进程……");
        cluster.fork();
    });
} else {
    // 工作进程：创建 HTTP 服务器
    http.createServer((req, res) => {
        res.statusCode = 200;
        res.setHeader("Content-Type", "text/plain; charset=utf-8");
        res.end(`你好！由进程 ${process.pid} 处理你的请求\n`);
    }).listen(8000);

    console.log(`工作进程 ${process.pid} 已启动`);
}
```

## Child Process vs Worker Threads vs Cluster

| 对比维度 | Child Process | Worker Threads | Cluster |
| :---: | :---: | :---: | :---: |
| **本质** | 独立的操作系统进程 | 同一进程内的多个线程 | 多个 Node.js 进程（fork 的变体） |
| **内存隔离** | 完全独立（各自 V8 实例） | 共享进程内存 | 完全独立（各自 V8 实例） |
| **通信方式** | IPC 管道 / 消息 | `MessageChannel` / `SharedArrayBuffer` | IPC 消息 |
| **适用场景** | 执行外部命令、隔离不稳定的任务 | CPU 密集型计算（加密/压缩/大量计算） | Web 服务器利用多核 CPU 处理并发请求 |
| **开销** | 高（每个进程独立内存） | 较低（共享内存） | 高（但会自动负载均衡） |

---

> 📋 **本文档持续更新中，如有疑问可随时交流。**
