# 第 1 章 必备基础知识

## 计算机组成

### 硬件
计算机硬件主要由五个部分组成，分别是：运算器、控制器、存储器、输入设备、输出设备。

:::tips
**备注**:『运算器』和『控制器』一起组成了**中央处理器（CPU）**。
:::

![计算机硬件](https://cdn.nlark.com/yuque/0/2025/png/35780599/1748393561986-f7bc28d7-d244-4777-8a38-03493153f17b.png)

:::color4
**注意：**计算机的 CPU 只能理解并执行**二进制（用 0和1表示信息）**的**机器指令**。
:::

:::info
**内存 VS 硬盘：**

+ 硬盘：持久化存储，读写速度不如内存快，但容量通常比较大（500GB、1TB、2TB 等）。
+ 内存：暂时性存储，读写速度快，但容量通常不如硬盘大（8GB、16GB、32GB、64GB 等）。

**通俗理解**：能安装多少个游戏，取决于硬盘的大小；能同时开几个游戏，取决于内存的大小。
:::

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
计算机问世的初期，人们只能通过**『机器语言』**（又称机器码）来操作计算机，所谓机器语言，就是`0`和 `1`组成的二进制内容。

> 例如：在`x86`的 CPU 架构下，使用机器码编写`1 + 1`的运算代码如下：
```asm
10110000 00000001 00000100 00000001
```

### 第二代语言：汇编语言
用机器语言编程，程序员很难理解每一条指令的含义，为了解决这个问题，**『汇编语言』**应运而生，它将机器语言中的二进制指令，转化为更容易记忆的助记符（如`MOV`、`ADD`、`LOAD`等）。

> 例如：在`x86`的 CPU 架构下，使用**『汇编语言』**编写`1 + 1`的运算代码如下：
```asm
mov al, 1
add al, 1
```

:::color4
**注意：****『汇编语言』**需要翻译成**『机器码』**，才能交给 CPU 执行，因为 CPU 只认二进制指令。
:::

### 第三代语言：高级语言
相对**『机器语言』**和**『汇编语言』**而言，**『高级语言』**更接近人类的自然语言，常见的**『高级语言』**有：C、C++、Java、PHP、Go、Rust、JavaScript、Python 等。

> Go 语言输出 "Hello, world!"：
```go
package main

import "fmt"

func main() {
    fmt.Println("Hello, world!")
}
```

:::color4
**注意：**计算机不能直接执行**『高级语言』**，同样需要将其转换为**『机器语言』**才能被计算机执行。
:::

## 『编译型语言』与『解释型语言』

### 编译型语言
将程序翻译成计算机能理解的二进制内容，并且通常会**生成一个可执行文件**，常见的**『编译型』**语言有：C、C++、**Go**、Rust 等。

:::info
+ 优势：同一运行平台，代码只需编译一次，且执行效率高。
+ 劣势：跨平台性差（但 Go 的交叉编译很好地解决了这个问题），大型项目编译时间较长。
:::

### 解释型语言
将程序一句一句地翻译为：计算机可以执行的指令，整个过程通常**不生成可执行文件**，常见的解释型语言有：Python、Php、JavaScript 等。

:::info
+ 优势：跨平台性好，无需编译，开发调试灵活高效。
+ 劣势：每次运行都需要解释，执行效率较低。
:::

### 二者对比

|  | **编译型语言** | **解释型语言** |
| --- | --- | --- |
| **举例** | C、C++、**Go**、Rust 等 | Python、JavaScript、Ruby 等 |
| **执行流程** | 运行前把所有程序一次性翻译成机器码，并生成可执行文件。 | 运行时靠对应的解释器，把代码一句一句翻译成机器码执行。 |
| **是否生成可执行文件** | 是，一次编译多处运行。 | 否，每次都要靠解释器翻译后再运行。 |
| **运行速度** | 快 | 慢 |
| **是否跨平台** | 传统否，但 Go 支持交叉编译。 | 是，只要该平台下有解释器，就能运行。 |
| **适合场景** | 系统底层、性能要求较高的场景。 | 脚本、数据分析、AI 应用、Web 开发等。 |

---

# 第 2 章 初识 Go

## Go 语言概述

### Go 的起源

:::tips
Go 语言（又称 Golang）由 Google 的三位大神：Robert Griesemer、Rob Thompson 和 Ken Thompson 于 2007 年开始设计，2009 年正式对外发布。

三位作者都是计算机界的传奇人物：
+ Ken Thompson：Unix 之父、C 语言设计者之一、图灵奖得主
+ Rob Pike：Unix 团队成员、UTF-8 设计者之一
+ Robert Griesemer：Google V8 引擎参与者、Java HotSpot 编译器贡献者

他们设计 Go 的初衷是解决 Google 内部的大规模并发、多核编程、超长编译时间等实际问题。
:::

:::info
Go 语言的设计哲学是"少即是多"（Less is more），它刻意省去了很多传统语言中的特性（如类继承、泛型（早期）、异常处理），以求简洁和高效。Go 提倡：代码要清晰、直接，做一件事最好只有一种清晰的方法。
:::

### Go 的特点

**Go 的优点：**

+ **编译速度快**：大型项目编译只需几秒，甚至几毫秒
+ **并发编程简单**：goroutine + channel 让并发变得优雅
+ **静态类型 + 类型推导**：既安全又不啰嗦（`x := 10` 自动推导为 int）
+ **内存安全**：垃圾回收（GC）+ 没有指针运算
+ **交叉编译**：一条命令编译出 Windows/Linux/macOS 的可执行文件
+ **部署简单**：编译成单个二进制文件，无外部依赖
+ **代码风格强制统一**：gofmt 工具自动格式化

**Go 的缺点：**

+ 没有泛型（Go 1.18 已补充，但仍较简化）
+ 错误处理比较啰嗦（需要大量 `if err != nil`）
+ 没有传统意义上的继承和多态
+ 生态相对年轻，部分领域第三方库不够丰富

### 哪些项目在用 Go？

+ **Docker**：容器化技术的标杆
+ **Kubernetes（K8s）**：容器编排的事实标准
+ **Prometheus**：监控和告警系统
+ **Etcd**：分布式键值存储
+ **Terraform**：基础设施即代码
+ **Consul**：服务发现和配置中心
+ **TiDB**：分布式 NewSQL 数据库
+ **Gin/Echo/Fiber**：高性能 Web 框架
+ **Bilibili、字节跳动、腾讯、阿里**等大量后端服务

## 环境搭建

### 安装 Go

```bash
# macOS
brew install go

# Linux (Ubuntu/Debian)
sudo apt update && sudo apt install golang-go

# 或用官方二进制包
wget https://go.dev/dl/go1.22.0.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.22.0.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bin

# Windows
# 去 https://go.dev/dl/ 下载 .msi 安装包，双击安装
```

### 验证安装

```bash
go version
# 输出：go version go1.22.0 linux/amd64
```

### 配置环境变量

```bash
# ~/.bashrc 或 ~/.zshrc
export GOPATH=$HOME/go              # 工作目录（第三方库、编译缓存等）
export PATH=$PATH:$GOPATH/bin       # 全局安装的 Go 工具
export GO111MODULE=on               # 开启 Go Modules（默认已开）
export GOPROXY=https://goproxy.cn,direct   # 国内代理（加速下载依赖）
```

```bash
# 让配置生效
source ~/.bashrc

# 查看所有环境变量
go env

# 重要的环境变量
go env GOPATH      # 工作空间
go env GOROOT      # Go 安装目录
go env GOPROXY     # 模块代理
go env GO111MODULE # 是否启用 Go Modules
```

## 第一个 Go 程序

### 编写代码

```go
// hello.go
package main

import "fmt"

func main() {
    fmt.Println("Hello, 世界!")
}
```

### 运行方式

```bash
# 方式 1：直接运行（开发调试用）
go run hello.go
# 输出：Hello, 世界!

# 方式 2：编译后运行（生产部署用）
go build hello.go       # 生成 hello 可执行文件
./hello                 # 运行
# 输出：Hello, 世界!

# 交叉编译（在 macOS 上编译出 Linux 可执行文件）
GOOS=linux GOARCH=amd64 go build hello.go

# 交叉编译（在 Linux 上编译出 Windows 可执行文件）
GOOS=windows GOARCH=amd64 go build hello.go
```

### 代码结构解析

```go
package main    // ① 声明包名，main 包表示可执行程序

import "fmt"    // ② 导入 fmt 包，用于格式化输入输出

func main() {   // ③ main 函数，程序的入口
    fmt.Println("Hello, 世界!")  // ④ 调用 fmt.Println 打印内容
}
```

:::color4
**注意：**Go 语言中，程序的执行入口是 `main` 包下的 `main()` 函数，和 C 语言类似。
:::

## IDE 与编辑器推荐

| 工具 | 特点 |
|------|------|
| **VS Code + Go 插件** | 免费，最主流，功能完善 |
| **GoLand (JetBrains)** | 功能最强大，需付费 |
| **Vim/Neovim + gopls** | 轻量，适合终端玩家 |

---

# 第 3 章 Go 核心基础

## 注释

```go
// 这是单行注释

/*
   这是多行注释
   可以跨越多行
*/

// 包级别的注释通常用 // 开头，而非 /*
// Package main implements the entry point.
package main
```

## 变量

### 变量的定义

Go 是**静态类型**语言，变量类型在编译时确定。有三种声明方式：

```go
package main

import "fmt"

func main() {
    // 方式 1：标准声明（var 变量名 类型 = 值）
    var name string = "张三"
    fmt.Println(name)  // 张三

    // 方式 2：类型推导（省略类型）
    var age = 25
    fmt.Println(age)  // 25

    // 方式 3：短变量声明（最常用！只能在函数内使用）
    weight := 70.5
    fmt.Println(weight)  // 70.5

    // 先声明后赋值
    var city string
    city = "北京"
    fmt.Println(city)  // 北京
}
```

### 批量声明变量

```go
// 批量声明（风格 1）
var (
    name   string = "张三"
    age    int    = 25
    salary float64
)

// 批量声明（风格 2）
var x, y, z int = 1, 2, 3

// 短变量声明多个
a, b, c := 1, 2, 3
```

## 数据类型

Go 的数据类型分为四大类：

```
数据类型
├── 基本类型
│   ├── 整数：int, int8, int16, int32, int64
│   ├── 无符号整数：uint, uint8(uint8即byte), uint16, uint32, uint64
│   ├── 浮点数：float32, float64
│   ├── 复数：complex64, complex128
│   ├── 布尔：bool
│   └── 字符串：string
├── 复合类型
│   ├── 数组（array）
│   ├── 切片（slice）
│   ├── 映射（map）
│   ├── 结构体（struct）
├── 引用类型
│   ├── 指针（pointer）
│   ├── 切片（slice）
│   ├── 映射（map）
│   ├── 通道（channel）
│   └── 函数（function）
└── 接口类型（interface）
```

### 整数类型

| 类型 | 字节数 | 范围 |
|------|--------|------|
| int8 | 1 | -128 ~ 127 |
| int16 | 2 | -32768 ~ 32767 |
| int32 | 4 | -21亿 ~ 21亿 |
| int64 | 8 | 非常大 |
| uint8 | 1 | 0 ~ 255 |
| uint16 | 2 | 0 ~ 65535 |
| uint32 | 4 | 0 ~ 约42亿 |
| uint64 | 8 | 非常大 |
| int | 4或8 | 依平台而定（64位系统为8字节） |
| uint | 4或8 | 依平台而定 |
| byte | 1 | uint8 的别名 |
| rune | 4 | int32 的别名，存 Unicode 码点 |

```go
var (
    a int8   = 127
    b int16  = 32767
    c int32  = 2147483647
    d int64  = 9223372036854775807
    e uint8  = 255
    f byte   = 'A'      // byte 就是 uint8，等于 65
    g rune   = '中'      // rune 就是 int32，等于 20013
    h int    = 42
)
```

### 浮点数类型

```go
var (
    pi  float32 = 3.1415926               // 约 6 位精度
    e   float64 = 2.718281828459045       // 约 15 位精度（默认）
    x           = 3.14                     // 自动推导为 float64
)
```

:::color4
**注意：**金额计算不要用浮点数！会有精度丢失问题。金额建议用整数（单位：分）或 `decimal` 库。
:::

```go
// 浮点数比较陷阱
x := 0.1
y := 0.2
z := 0.3

// ❌ 不精确：输出 false
fmt.Println(x+y == z)  // false

// ✅ 正确做法：允许一定误差
const epsilon = 0.0000001
fmt.Println((x+y-z) < epsilon && (z-x-y) < epsilon)  // true
```

### 布尔类型

```go
var (
    isActive bool = true
    isDone   bool = false
)

// 布尔类型只能用 true / false，不能用 0 / 1
// var flag bool = 1  ← 编译错误！

// 布尔运算
fmt.Println(true && false) // false (与)
fmt.Println(true || false) // true  (或)
fmt.Println(!true)         // false (非)
```

### 字符串类型

```go
// 字符串是不可变的字节序列
var s1 string = "Hello"

// 字符串拼接
s2 := "Hello" + " " + "World"
fmt.Println(s2)  // Hello World

// 多行字符串（反引号，原样输出，包括换行）
s3 := `第一行
第二行
第三行`
fmt.Println(s3)

// 字符串长度
fmt.Println(len("Hello"))      // 5（字节数）
fmt.Println(len("你好"))        // 6（中文 UTF-8 占3字节）

// 字符串访问
str := "Hello"
fmt.Println(str[0])            // 72（'H' 的 ASCII 码）
fmt.Printf("%c\n", str[0])     // H

// 字符串不可修改！
// str[0] = 'h'  ← 编译错误！
```

## 常量和 iota

### 常量定义

```go
// 单常量
const PI = 3.14159

// 批量常量
const (
    STATUS_OK    = 200
    STATUS_ERROR = 500
)

// 类型化常量
const Pi float64 = 3.141592653589793

// 无类型常量（精度更高，可被不同类型使用）
const E = 2.71828  // 无类型浮点数
const N = 100      // 无类型整数
```

### iota：常量计数器

```go
// iota 在 const 块中从 0 开始自动递增
const (
    Monday = iota    // 0
    Tuesday          // 1
    Wednesday        // 2
    Thursday         // 3
    Friday           // 4
    Saturday         // 5
    Sunday           // 6
)

// iota 的高级用法
const (
    _  = iota             // 0（跳过）
    KB = 1 << (10 * iota) // 1 << 10 = 1024
    MB                     // 1 << 20 = 1048576
    GB                     // 1 << 30 = 1073741824
    TB                     // 1 << 40 = 1099511627776
)

// 位掩码
const (
    READ   = 1 << iota // 1 = 0001
    WRITE              // 2 = 0010
    EXEC               // 4 = 0100
)
permission := READ | WRITE  // 3 = 0011
```

## 类型转换

Go 是**强类型**语言，**不支持隐式类型转换**，必须显式转换。

```go
var a int = 10
var b float64 = float64(a)  // int → float64
var c int64 = int64(a)      // int → int64

// byte 与 字符串
var d byte = 'A'
fmt.Println(string(d))      // "A"

// int 与 string（需用 strconv 包）
import "strconv"

// int → string
num := 42
str := strconv.Itoa(num)         // "42"

// string → int
n, err := strconv.Atoi("42")     // 42, nil
```

## 输出函数对比

```go
import "fmt"

fmt.Print("Hello")               // 不换行
fmt.Println("Hello")             // 换行
fmt.Printf("姓名:%s, 年龄:%d\n", "张三", 25) // 格式化输出

// Printf 常用格式化动词
// %v   默认格式
// %+v  结构体会加上字段名
// %#v  Go 语法表示
// %T   打印类型
// %d   整数（十进制）
// %b   整数（二进制）
// %f   浮点数
// %s   字符串
// %q   带引号的字符串
// %p   指针地址
// %t   布尔值
```

---

# 第 4 章 流程控制语句

## 条件判断

### if 语句

```go
age := 18

// 基本 if
if age >= 18 {
    fmt.Println("成年了")
}

// if-else
if age >= 18 {
    fmt.Println("成年了")
} else {
    fmt.Println("未成年")
}

// if-else if-else
score := 85
if score >= 90 {
    fmt.Println("优秀")
} else if score >= 80 {
    fmt.Println("良好")
} else if score >= 60 {
    fmt.Println("及格")
} else {
    fmt.Println("不及格")
}
```

**Go 的 if 特色：初始化语句**

```go
// 可以在 if 中声明变量，作用域限定在 if 块内
if err := doSomething(); err != nil {
    fmt.Println("出错了:", err)
    return
}

// 典型场景：从 map 取值并判断
if value, ok := myMap["key"]; ok {
    fmt.Println("找到了:", value)
} else {
    fmt.Println("没有这个 key")
}
```

:::color4
**注意：**Go 的 if 条件**不用括号**，但**大括号必须写**，左大括号 `{` 必须和 if 在同一行。
:::

### switch 语句

Go 的 switch 比 C/Java 更强大、更简洁。

```go
// 基础 switch（不需要 break，默认自动跳出）
day := 3
switch day {
case 1:
    fmt.Println("星期一")
case 2:
    fmt.Println("星期二")
case 3:
    fmt.Println("星期三")
default:
    fmt.Println("其他")
}

// 多值匹配
switch day {
case 1, 2, 3, 4, 5:
    fmt.Println("工作日")
case 6, 7:
    fmt.Println("周末")
}

// 条件 switch（相当于多个 if-else）
score := 85
switch {
case score >= 90:
    fmt.Println("优秀")
case score >= 80:
    fmt.Println("良好")
case score >= 60:
    fmt.Println("及格")
default:
    fmt.Println("不及格")
}

// 带初始化的 switch
switch lang := getLanguage(); lang {
case "zh":
    fmt.Println("中文")
case "en":
    fmt.Println("英文")
default:
    fmt.Println("其他语言")
}
```

## 循环

Go 只有一种循环：**for**。但可以通过不同写法实现各种循环效果。

### 基本 for 循环

```go
// 标准三段式（初始化; 条件; 后置）
for i := 0; i < 5; i++ {
    fmt.Println(i)
}

// 只写条件（相当于 while）
count := 0
for count < 5 {
    fmt.Println(count)
    count++
}

// 无限循环（相当于 while(true)）
for {
    fmt.Println("死循环，需要 break 跳出")
    break
}
```

### for range：遍历容器

```go
// 遍历字符串
for i, ch := range "你好Go" {
    fmt.Printf("索引:%d, 字符:%c, 类型:%T\n", i, ch, ch)
}
// 输出：
// 索引:0, 字符:你
// 索引:3, 字符:好   注意：UTF-8 中文占 3 字节，索引跳过了1-2
// 索引:6, 字符:G

// 遍历切片/数组
nums := []int{10, 20, 30}
for i, v := range nums {
    fmt.Printf("索引:%d, 值:%d\n", i, v)
}

// 遍历 map
scores := map[string]int{"语文": 90, "数学": 85}
for k, v := range scores {
    fmt.Printf("科目:%s, 分数:%d\n", k, v)
}

// 只要索引
for i := range nums {
    fmt.Println(i)
}

// 只要值（用 _ 忽略索引）
for _, v := range nums {
    fmt.Println(v)
}

// 只要 key
for k := range scores {
    fmt.Println(k)
}
```

## 跳转语句

```go
// break：跳出循环
for i := 0; i < 10; i++ {
    if i == 5 {
        break  // 跳出循环
    }
    fmt.Println(i)
}
// 输出：0 1 2 3 4

// continue：跳过本次
for i := 0; i < 5; i++ {
    if i == 2 {
        continue  // 跳过 i=2
    }
    fmt.Println(i)
}
// 输出：0 1 3 4

// goto：跳转到标签（慎用）
func main() {
    i := 0
loop:
    fmt.Println(i)
    i++
    if i < 3 {
        goto loop
    }
}
```

---

# 第 5 章 函数入门

## 函数定义

```go
// 基本格式
func 函数名(参数列表) 返回值类型 {
    // 函数体
    return 值
}
```

```go
// 示例
func add(a int, b int) int {
    return a + b
}

// 简化：参数类型相同可合并
func add(a, b int) int {
    return a + b
}

// 调用
result := add(3, 5)
fmt.Println(result)  // 8
```

## 多返回值

Go 支持函数返回多个值，这是 Go 的一大特色。

```go
// 返回两个值
func divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, fmt.Errorf("除数不能为零")
    }
    return a / b, nil
}

// 调用
result, err := divide(10, 2)
if err != nil {
    fmt.Println("出错:", err)
} else {
    fmt.Println("结果:", result)  // 结果: 5
}

// 不需要某个返回值（用 _ 忽略）
result2, _ := divide(10, 3)
fmt.Println(result2)  // 3.3333333333333335
```

## 命名返回值

```go
// 命名返回值可以提高可读性
func split(sum int) (x, y int) {
    x = sum * 4 / 9
    y = sum - x
    return  // 裸 return，返回命名值
}

// 调用
a, b := split(100)
fmt.Println(a, b)  // 44 56
```

## 可变参数

```go
// 使用 ... 表示可变参数（本质是切片）
func sum(nums ...int) int {
    total := 0
    for _, num := range nums {
        total += num
    }
    return total
}

fmt.Println(sum(1, 2))          // 3
fmt.Println(sum(1, 2, 3, 4, 5)) // 15

// 切片展开传给可变参数
numbers := []int{1, 2, 3, 4, 5}
fmt.Println(sum(numbers...))     // 15
```

## 函数作为值

Go 中函数是一等公民，可以赋值、传参、作为返回值。

```go
// 函数赋值给变量
add := func(a, b int) int {
    return a + b
}
fmt.Println(add(3, 5))  // 8

// 函数作为参数
func compute(fn func(int, int) int, a, b int) int {
    return fn(a, b)
}

result := compute(func(x, y int) int {
    return x * y
}, 4, 5)
fmt.Println(result)  // 20
```

## 匿名函数与闭包

```go
// 匿名函数立即执行
func(a, b int) {
    fmt.Println(a + b)
}(3, 5)  // 输出：8

// 闭包：函数"记住"了外部变量
func counter() func() int {
    count := 0
    return func() int {
        count++
        return count
    }
}

c := counter()
fmt.Println(c())  // 1
fmt.Println(c())  // 2
fmt.Println(c())  // 3
```

---

# 第 6 章 数据容器

## 数组

### 声明与初始化

```go
// 数组是固定长度的、同类型元素的集合

// 声明方式
var arr1 [5]int                     // 默认值为 [0 0 0 0 0]
arr2 := [3]int{1, 2, 3}            // 指定值
arr3 := [...]int{1, 2, 3, 4, 5}   // 自动计算长度
arr4 := [5]int{0: 10, 4: 50}       // 按索引初始化，其余为0
// arr4 = [10 0 0 0 50]

// 数组长度是类型的一部分！
// [3]int 和 [5]int 是不同类型，不能互相赋值
```

### 数组操作

```go
arr := [5]int{10, 20, 30, 40, 50}

// 访问
fmt.Println(arr[0])     // 10
fmt.Println(arr[4])     // 50

// 修改
arr[0] = 100

// 长度
fmt.Println(len(arr))   // 5

// 遍历
for i, v := range arr {
    fmt.Printf("arr[%d] = %d\n", i, v)
}

// 二维数组
matrix := [3][3]int{
    {1, 2, 3},
    {4, 5, 6},
    {7, 8, 9},
}
fmt.Println(matrix[1][1])  // 5
```

## 切片

切片是 Go 中最重要的数据结构之一，它是**动态长度的、基于数组的视图**。

### 创建切片

```go
// 方式 1：直接声明
var s1 []int           // nil 切片，长度和容量均为0
s2 := []int{1, 2, 3}  // 初始化

// 方式 2：make 创建（指定长度和容量）
s3 := make([]int, 5)      // 长度=5, 容量=5, 元素全为0
s4 := make([]int, 3, 10)  // 长度=3, 容量=10

// 方式 3：从数组/切片截取
arr := [5]int{1, 2, 3, 4, 5}
s5 := arr[1:4]         // [2, 3, 4]，截取索引 1 到 3（左闭右开）
s6 := arr[:3]          // [1, 2, 3]，从开头到索引 2
s7 := arr[2:]          // [3, 4, 5]，从索引 2 到结尾
s8 := arr[:]           // [1, 2, 3, 4, 5]，全部
```

### 切片操作

```go
s := []int{10, 20, 30}

// 追加元素
s = append(s, 40)          // [10, 20, 30, 40]
s = append(s, 50, 60, 70)  // [10, 20, 30, 40, 50, 60, 70]

// 追加另一个切片（需要 ... 展开）
s2 := []int{100, 200}
s = append(s, s2...)       // [10, 20, 30, 40, 50, 60, 70, 100, 200]

// 长度和容量
fmt.Println(len(s))  // 长度（元素个数）= 9
fmt.Println(cap(s))  // 容量（底层数组大小）

// 复制
src := []int{1, 2, 3, 4, 5}
dst := make([]int, 3)
copied := copy(dst, src)  // copied=3, dst=[1,2,3]

// 删除元素（删除索引 2 的元素）
s = append(s[:2], s[3:]...)
```

### 切片底层原理

```
切片结构（24字节）：
┌──────────┐
│  ptr     │ → 指向底层数组
├──────────┤
│  len     │ = 3（长度）
├──────────┤
│  cap     │ = 5（容量）
└──────────┘

底层数组：[1][2][3][空][空]
           ↑        ↑
          ptr   容量到这里
```

```go
// 切片扩容规则（Go 1.18+）：
// 当 len < 256 时，新容量约为旧容量的 2 倍
// 当 len >= 256 时，新容量 ≈ old + (old + 3*256) / 4

s := make([]int, 0)
for i := 0; i < 10; i++ {
    s = append(s, i)
    fmt.Printf("len=%d, cap=%d\n", len(s), cap(s))
}
// 输出大致为：1→1, 2→2, 3→4, 5→8, 9→16
```

## Map

### 创建和使用

```go
// 方式 1：make 创建
m1 := make(map[string]int)

// 方式 2：字面量
m2 := map[string]int{
    "语文": 90,
    "数学": 85,
    "英语": 92,
}

// 方式 3：声明后初始化（nil map 不能直接赋值！）
var m3 map[string]int  // nil map
// m3["key"] = 1  ← 会 panic！

// 增删改查
m := make(map[string]int)

// 增 / 改
m["张三"] = 90
m["李四"] = 85

// 查
score := m["张三"]
fmt.Println(score)  // 90

// 安全查找（key 不存在时返回零值，ok=false）
value, ok := m["王五"]
if ok {
    fmt.Println("找到了:", value)
} else {
    fmt.Println("不存在")  // 输出这个
}

// 删
delete(m, "张三")

// 遍历
for key, value := range m {
    fmt.Printf("%s: %d\n", key, value)
}
```

:::color4
**注意：**Map 遍历顺序是随机的！不要依赖遍历顺序。如果需要有序，先把 keys 取出来排序后再遍历。
:::

### 嵌套 Map

```go
// 学生成绩表：学科 → 成绩
students := map[string]map[string]int{
    "张三": {"语文": 90, "数学": 85},
    "李四": {"语文": 88, "数学": 92},
}

fmt.Println(students["张三"]["语文"])  // 90

// 追加
students["张三"]["英语"] = 95
```

## 结构体

结构体是自定义的复合类型，把不同字段组合在一起。

### 定义和使用

```go
// 定义结构体
type Person struct {
    Name   string
    Age    int
    Email  string
}

// 创建结构体
// 方式 1：字段名赋值（推荐）
p1 := Person{
    Name:  "张三",
    Age:   25,
    Email: "zhangsan@example.com",
}

// 方式 2：按顺序赋值（不推荐，字段多了容易错）
p2 := Person{"李四", 30, "lisi@example.com"}

// 方式 3：先声明后赋值
var p3 Person
p3.Name = "王五"
p3.Age = 28

// 访问字段
fmt.Println(p1.Name)  // 张三

// 结构体指针
p4 := &Person{Name: "赵六", Age: 22}
fmt.Println(p4.Name)  // 赵六（自动解引用，不需要写 (*p4).Name）
```

### 匿名字段与嵌套

```go
type Address struct {
    City    string
    Street  string
}

type User struct {
    Name    string
    Age     int
    Address Address  // 嵌套结构体
}

u := User{
    Name: "张三",
    Age:  25,
    Address: Address{
        City:   "北京",
        Street: "长安街",
    },
}

fmt.Println(u.Address.City)  // 北京

// 匿名嵌入（类似于"继承"）
type Employee struct {
    Name   string
    Person        // 匿名嵌入！Employee 可以直接使用 Person 的字段
}

e := Employee{Name: "员工1", Person: Person{Age: 30}}
e.Age = 31  // 直接访问，不需要 e.Person.Age
```

---

# 第 7 章 Go 的"面向对象"

Go 没有 class 和继承，但通过 **结构体 + 方法 + 接口** 实现了面向对象的核心思想。

## 方法

方法是**带有接收者（receiver）的函数**。

```go
type Rectangle struct {
    Width  float64
    Height float64
}

// 值接收者方法（不修改原值）
func (r Rectangle) Area() float64 {
    return r.Width * r.Height
}

// 指针接收者方法（可以修改原值）
func (r *Rectangle) Scale(factor float64) {
    r.Width *= factor
    r.Height *= factor
}

// 使用
rect := Rectangle{Width: 10, Height: 5}
fmt.Println(rect.Area())  // 50

rect.Scale(2)
fmt.Println(rect.Width, rect.Height)  // 20 10
```

:::color4
**重要规则：**

+ 要修改接收者的值 → 用指针接收者
+ 接收者是大型结构体 → 用指针接收者（避免拷贝开销）
+ 其他情况 → 用值接收者
+ **一条建议：** 同一个类型的方法，接收者类型保持一致。
:::

## 接口

接口是 Go 语言中最强大的抽象机制。

### 接口定义与实现

```go
// 定义接口
type Speaker interface {
    Speak() string
}

type Dog struct {
    Name string
}

type Cat struct {
    Name string
}

// Dog 实现了 Speaker 接口（隐式实现，不需要写 implements）
func (d Dog) Speak() string {
    return d.Name + "说: 汪汪汪"
}

// Cat 实现了 Speaker 接口
func (c Cat) Speak() string {
    return c.Name + "说: 喵喵喵"
}

// 面向接口编程
func MakeSpeak(s Speaker) {
    fmt.Println(s.Speak())
}

func main() {
    dog := Dog{Name: "旺财"}
    cat := Cat{Name: "加菲"}

    MakeSpeak(dog)  // 旺财说: 汪汪汪
    MakeSpeak(cat)  // 加菲说: 喵喵喵

    // 接口变量可以存任何实现了该接口的类型
    var s Speaker
    s = Dog{Name: "小黑"}
    fmt.Println(s.Speak())  // 小黑说: 汪汪汪
    s = Cat{Name: "小花"}
    fmt.Println(s.Speak())  // 小花说: 喵喵喵
}
```

### 空接口与类型断言

```go
// 空接口 interface{} 可以存储任意类型的值
var anything interface{}
anything = 42
anything = "hello"
anything = []int{1, 2, 3}

// 类型断言
var i interface{} = "hello"

// 方式 1：直接断言（不安全的写法）
s := i.(string)
fmt.Println(s)  // "hello"

// 方式 2：安全的断言（推荐！）
s, ok := i.(string)
if ok {
    fmt.Println("是字符串:", s)
} else {
    fmt.Println("不是字符串")
}

// 类型 switch
func describe(i interface{}) {
    switch v := i.(type) {
    case string:
        fmt.Printf("字符串: %s\n", v)
    case int:
        fmt.Printf("整数: %d\n", v)
    case bool:
        fmt.Printf("布尔: %t\n", v)
    default:
        fmt.Printf("其他类型: %T\n", v)
    }
}
```

### 常见内置接口

```go
// fmt.Stringer：控制 print 输出
type Person struct {
    Name string
    Age  int
}

func (p Person) String() string {
    return fmt.Sprintf("%s(%d岁)", p.Name, p.Age)
}

p := Person{"张三", 25}
fmt.Println(p)  // 张三(25岁)

// error 接口：定义错误
type MyError struct {
    Code    int
    Message string
}

func (e MyError) Error() string {
    return fmt.Sprintf("错误码:%d, 描述:%s", e.Code, e.Message)
}

// sort.Interface：自定义排序
type ByAge []Person

func (a ByAge) Len() int           { return len(a) }
func (a ByAge) Swap(i, j int)      { a[i], a[j] = a[j], a[i] }
func (a ByAge) Less(i, j int) bool { return a[i].Age < a[j].Age }
```

---

# 第 8 章 函数进阶

## defer

`defer` 将函数调用推迟到当前函数返回之前执行，常用于资源清理。

```go
// defer 的执行顺序：后进先出（LIFO，像叠盘子）
func main() {
    defer fmt.Println("第一个 defer")
    defer fmt.Println("第二个 defer")
    defer fmt.Println("第三个 defer")
    fmt.Println("正常执行")
}
// 输出：
// 正常执行
// 第三个 defer
// 第二个 defer
// 第一个 defer
```

### defer 经典应用

```go
// 1. 关闭文件
func readFile(path string) error {
    f, err := os.Open(path)
    if err != nil {
        return err
    }
    defer f.Close()  // 确保文件一定会被关闭

    // 读取操作...
    return nil
}

// 2. 释放锁
func updateData() {
    mu.Lock()
    defer mu.Unlock()  // 不管函数怎么返回，锁都会被释放

    // 更新操作...
}

// 3. 记录函数执行时间
func trace(name string) func() {
    start := time.Now()
    fmt.Printf("开始执行 %s\n", name)
    return func() {
        fmt.Printf("%s 执行完毕，耗时: %v\n", name, time.Since(start))
    }
}

func doWork() {
    defer trace("doWork")()
    time.Sleep(100 * time.Millisecond)
}
```

:::color4
**注意：**defer 的参数在声明时求值，不是执行时求值。

```go
x := 1
defer fmt.Println(x)  // x 此时是 1
x = 2
// 输出：1，不是 2！
```
:::

## panic 和 recover

```go
// panic：抛出错误，导致程序崩溃
// recover：捕获 panic，让程序继续运行

func safeDivide(a, b int) (result int) {
    defer func() {
        if r := recover(); r != nil {
            fmt.Println("捕获到 panic:", r)
            result = 0  // 设置默认返回值
        }
    }()

    if b == 0 {
        panic("除数不能为零")  // 主动抛出 panic
    }
    return a / b
}

func main() {
    fmt.Println(safeDivide(10, 2))  // 5
    fmt.Println(safeDivide(10, 0))  // 捕获到 panic: 除数不能为零 → 0
    fmt.Println("程序继续运行")        // 能执行到这里
}
```

:::color4
**注意：** `panic/recover` 不是 Go 的异常处理机制！Go 的惯例是用 `error` 返回值处理可预见的错误，`panic` 只用于不可恢复的严重错误。
:::

## 函数式编程

```go
// 高阶函数：接受或返回函数的函数

// map 实现
func Map[T any, R any](slice []T, fn func(T) R) []R {
    result := make([]R, len(slice))
    for i, v := range slice {
        result[i] = fn(v)
    }
    return result
}

// filter 实现
func Filter[T any](slice []T, fn func(T) bool) []T {
    var result []T
    for _, v := range slice {
        if fn(v) {
            result = append(result, v)
        }
    }
    return result
}

// 使用
nums := []int{1, 2, 3, 4, 5, 6}

doubled := Map(nums, func(n int) int { return n * 2 })
// [2, 4, 6, 8, 10, 12]

evens := Filter(nums, func(n int) bool { return n%2 == 0 })
// [2, 4, 6]
```

---

# 第 9 章 错误处理

Go 的错误处理理念是：**显式地处理每一个错误**。

## error 接口

```go
// error 是一个内置接口
type error interface {
    Error() string
}
```

## 创建 error

```go
import (
    "errors"
    "fmt"
)

// 方式 1：errors.New
err1 := errors.New("这是一个错误")

// 方式 2：fmt.Errorf（可格式化）
err2 := fmt.Errorf("打开文件 %s 失败: %w", filename, originalErr)

// 方式 3：自定义错误类型
type ValidationError struct {
    Field   string
    Message string
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("校验失败 [%s]: %s", e.Field, e.Message)
}
```

## 处理 error

```go
// Go 的错误处理模式
func processFile(path string) error {
    f, err := os.Open(path)
    if err != nil {
        return fmt.Errorf("processFile: 打开文件失败: %w", err)
    }
    defer f.Close()

    data, err := io.ReadAll(f)
    if err != nil {
        return fmt.Errorf("processFile: 读取文件失败: %w", err)
    }

    fmt.Println(string(data))
    return nil
}

// 调用方
if err := processFile("data.txt"); err != nil {
    fmt.Println("出错:", err)
}
```

## 错误包装与判断

```go
import (
    "errors"
    "fmt"
)

// error wrapping（Go 1.13+）
var ErrNotFound = errors.New("not found")

func findUser(id int) error {
    return fmt.Errorf("findUser(%d): %w", id, ErrNotFound)
}

func main() {
    err := findUser(12345)

    // errors.Is：判断错误链中是否包含特定错误
    if errors.Is(err, ErrNotFound) {
        fmt.Println("用户不存在")
    }

    // errors.As：提取特定类型的错误
    var valErr *ValidationError
    if errors.As(err, &valErr) {
        fmt.Printf("校验错误: %s → %s\n", valErr.Field, valErr.Message)
    }
}
```

---

# 第 10 章 包与模块管理

## 包的组织

```bash
myproject/
├── go.mod              # 模块定义文件
├── main.go             # package main
├── user/               # package user
│   ├── user.go
│   └── profile.go
├── service/            # package service
│   └── service.go
└── utils/              # package utils
    └── helper.go
```

### 包的声明和导入

```go
// main.go
package main

import (
    "fmt"
    "myproject/user"      // 本地包
    "myproject/utils"

    "github.com/gin-gonic/gin"  // 第三方包
)

func main() {
    u := user.New("张三")
    fmt.Println(utils.Greet(u.Name))
}
```

### 标识符可见性

```go
// Go 没有 public/private 关键字，通过首字母大小写控制！
// 首字母大写 → 公开（Public），外部可访问
// 首字母小写 → 私有（private），仅包内可访问

package user

type User struct {
    Name   string  // 公开字段
    email  string  // 私有字段（外部不可访问）
}

func New(name string) *User {  // 公开函数
    return &User{Name: name}
}

func (u *User) setEmail(e string) {  // 私有方法
    u.email = e
}
```

## Go Modules

```bash
# 初始化模块
go mod init myproject
# 生成 go.mod 文件

# 安装依赖
go get github.com/gin-gonic/gin       # 安装最新版本
go get github.com/gin-gonic/gin@v1.9.0  # 安装指定版本

# 整理依赖（清理不需要的，添加需要的）
go mod tidy

# 查看依赖
go list -m all

# 查看为什么需要某个依赖
go mod why github.com/pkg/errors

# 本地替换依赖（调试用）
go mod edit -replace github.com/xxx/yyy=../local-yyy
```

### go.mod 文件

```
module myproject

go 1.22

require (
    github.com/gin-gonic/gin v1.9.1
    github.com/go-sql-driver/mysql v1.7.1
)

require (
    // 间接依赖会自动列在这里...
)
```

---

# 第 11 章 并发编程

Go 的并发模型是其最大的亮点，核心是两个概念：**goroutine** 和 **channel**。

## Goroutine

Goroutine 是轻量级线程，由 Go 运行时调度。

```go
import (
    "fmt"
    "time"
)

// 使用 go 关键字启动 goroutine
func sayHello() {
    fmt.Println("Hello from goroutine")
}

func main() {
    go sayHello()  // 启动一个新的 goroutine
    // 等价于：
    go func() {
        fmt.Println("匿名 goroutine")
    }()

    time.Sleep(time.Millisecond)  // 等待 goroutine 执行完
    fmt.Println("main 结束")
}
```

### Goroutine 的特点

```go
// 1. 启动成本极低（几 KB 栈空间，远小于线程的 MB 级别）
// 2. 可以轻松启动成千上万个 goroutine
for i := 0; i < 10000; i++ {
    go func(n int) {
        // 处理任务
    }(i)
}

// 3. 栈动态伸缩（需要时增长，不需要时缩小）
// 4. 基于 GPM 调度模型，性能极高
```

## sync.WaitGroup：等待一组 goroutine

```go
import "sync"

func main() {
    var wg sync.WaitGroup

    for i := 1; i <= 5; i++ {
        wg.Add(1)  // 计数器 +1

        go func(n int) {
            defer wg.Done()  // 执行完毕，计数器 -1
            fmt.Printf("任务 %d 执行中\n", n)
            time.Sleep(time.Second)
        }(i)
    }

    wg.Wait()  // 等待计数器变为 0
    fmt.Println("所有任务完成")
}
```

## Channel

Channel 是 goroutine 之间通信的管道，遵循 **"不要通过共享内存来通信，而要通过通信来共享内存"**。

### 创建和使用

```go
// 创建 channel
ch := make(chan int)       // 无缓冲 channel
ch := make(chan int, 10)   // 带缓冲的 channel（容量为10）

// 发送和接收
ch <- 42                    // 发送
value := <-ch              // 接收
<-ch                       // 接收但丢弃值

// 关闭 channel
close(ch)

// 安全接收（判断 channel 是否关闭）
value, ok := <-ch
if !ok {
    fmt.Println("channel 已关闭")
}
```

### 无缓冲 vs 有缓冲

```go
// 无缓冲 channel：发送方必须等接收方准备好
ch := make(chan int)

go func() {
    ch <- 1  // 阻塞，直到有人接收
    fmt.Println("发送完毕")
}()

time.Sleep(time.Second)
value := <-ch  // 接收，goroutine 继续执行
fmt.Println(value)

// 有缓冲 channel：缓冲区满前不阻塞发送
ch := make(chan int, 3)

ch <- 1  // 不阻塞
ch <- 2  // 不阻塞
ch <- 3  // 不阻塞
// ch <- 4  // 阻塞！缓冲区满了

fmt.Println(<-ch) // 1
fmt.Println(<-ch) // 2
fmt.Println(<-ch) // 3
```

### for range 遍历 channel

```go
func producer(ch chan<- int) {
    for i := 1; i <= 5; i++ {
        ch <- i
    }
    close(ch)  // 生产者关闭 channel
}

func main() {
    ch := make(chan int, 5)

    go producer(ch)

    // for range 自动循环直到 channel 关闭
    for value := range ch {
        fmt.Println(value)
    }
    fmt.Println("channel 已关闭，循环结束")
}
```

### select 多路复用

```go
func main() {
    ch1 := make(chan string)
    ch2 := make(chan string)

    go func() {
        time.Sleep(time.Second)
        ch1 <- "来自 ch1"
    }()

    go func() {
        time.Sleep(2 * time.Second)
        ch2 <- "来自 ch2"
    }()

    // select 会等待多个 channel，哪个先有数据就处理哪个
    for i := 0; i < 2; i++ {
        select {
        case msg1 := <-ch1:
            fmt.Println(msg1)
        case msg2 := <-ch2:
            fmt.Println(msg2)
        case <-time.After(3 * time.Second):
            fmt.Println("超时了")
        default:
            // 非阻塞操作
        }
    }
}
```

### 常见并发模式

```go
// 1. 扇出（Fan-out）：一个生产者，多个消费者
func fanOut() {
    jobs := make(chan int, 100)
    var wg sync.WaitGroup

    // 启动 3 个 worker
    for w := 1; w <= 3; w++ {
        wg.Add(1)
        go func(workerID int) {
            defer wg.Done()
            for job := range jobs {
                fmt.Printf("Worker %d 处理任务 %d\n", workerID, job)
            }
        }(w)
    }

    // 发送任务
    for j := 1; j <= 10; j++ {
        jobs <- j
    }
    close(jobs)
    wg.Wait()
}

// 2. 扇入（Fan-in）：多个生产者，一个消费者
func fanIn(ch1, ch2 <-chan int) <-chan int {
    out := make(chan int)
    go func() {
        for {
            select {
            case v := <-ch1:
                out <- v
            case v := <-ch2:
                out <- v
            }
        }
    }()
    return out
}

// 3. Pipeline：数据经多个阶段处理
func gen(nums ...int) <-chan int {
    out := make(chan int)
    go func() {
        for _, n := range nums {
            out <- n
        }
        close(out)
    }()
    return out
}

func square(in <-chan int) <-chan int {
    out := make(chan int)
    go func() {
        for n := range in {
            out <- n * n
        }
        close(out)
    }()
    return out
}

// 使用 pipeline
func main() {
    in := gen(1, 2, 3, 4, 5)
    out := square(in)
    for result := range out {
        fmt.Println(result) // 1 4 9 16 25
    }
}
```

## sync.Mutex：互斥锁

```go
import "sync"

type Counter struct {
    mu    sync.Mutex
    value int
}

func (c *Counter) Inc() {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.value++
}

func (c *Counter) Value() int {
    c.mu.Lock()
    defer c.mu.Unlock()
    return c.value
}

func main() {
    var wg sync.WaitGroup
    counter := &Counter{}

    for i := 0; i < 1000; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            counter.Inc()
        }()
    }

    wg.Wait()
    fmt.Println(counter.Value())  // 1000
}
```

### sync.RWMutex：读写锁

```go
type SafeMap struct {
    mu   sync.RWMutex
    data map[string]int
}

// 写操作：排他性，不能和其他读写同时进行
func (m *SafeMap) Set(key string, value int) {
    m.mu.Lock()
    defer m.mu.Unlock()
    m.data[key] = value
}

// 读操作：可以多个 goroutine 同时读
func (m *SafeMap) Get(key string) (int, bool) {
    m.mu.RLock()
    defer m.mu.RUnlock()
    v, ok := m.data[key]
    return v, ok
}
```

---

# 第 12 章 文件操作

## 读取文件

```go
import (
    "bufio"
    "fmt"
    "io"
    "os"
)

// 方式 1：一次性读取全部（小文件）
func readAll(path string) {
    data, err := os.ReadFile(path)
    if err != nil {
        fmt.Println("读取失败:", err)
        return
    }
    fmt.Println(string(data))
}

// 方式 2：带缓冲读取（大文件推荐）
func readBufio(path string) {
    f, err := os.Open(path)
    if err != nil {
        fmt.Println("打开失败:", err)
        return
    }
    defer f.Close()

    scanner := bufio.NewScanner(f)
    for scanner.Scan() {
        fmt.Println(scanner.Text())  // 逐行处理
    }

    if err := scanner.Err(); err != nil {
        fmt.Println("读取出错:", err)
    }
}

// 方式 3：精确控制读取大小
func readChunk(path string) {
    f, err := os.Open(path)
    if err != nil {
        return
    }
    defer f.Close()

    buf := make([]byte, 1024)  // 每次读 1KB
    for {
        n, err := f.Read(buf)
        if err == io.EOF {
            break
        }
        if err != nil {
            fmt.Println("读取失败:", err)
            return
        }
        fmt.Print(string(buf[:n]))
    }
}
```

## 写入文件

```go
// 方式 1：一次性写入
func writeAll(path, content string) error {
    return os.WriteFile(path, []byte(content), 0644)
}

// 方式 2：追加写入
func appendToFile(path, content string) error {
    f, err := os.OpenFile(path, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
    if err != nil {
        return err
    }
    defer f.Close()

    _, err = f.WriteString(content + "\n")
    return err
}

// 方式 3：带缓冲的写入
func bufferedWrite(path string) error {
    f, err := os.Create(path)
    if err != nil {
        return err
    }
    defer f.Close()

    w := bufio.NewWriter(f)
    for i := 0; i < 100; i++ {
        w.WriteString(fmt.Sprintf("第 %d 行\n", i))
    }
    return w.Flush()  // 必须 Flush！否则数据还在缓冲区
}
```

## 文件路径操作

```go
import (
    "fmt"
    "os"
    "path/filepath"
)

func pathOps() {
    // 路径拼接（自动处理分隔符）
    path := filepath.Join("data", "users", "profile.json")
    fmt.Println(path)  // data/users/profile.json (Linux) 或 data\users\profile.json (Windows)

    // 获取文件名
    fmt.Println(filepath.Base("/home/user/file.txt"))  // file.txt

    // 获取目录
    fmt.Println(filepath.Dir("/home/user/file.txt"))   // /home/user

    // 获取扩展名
    fmt.Println(filepath.Ext("image.jpg"))              // .jpg

    // 判断文件是否存在
    _, err := os.Stat("data.txt")
    if os.IsNotExist(err) {
        fmt.Println("文件不存在")
    }

    // 创建目录
    os.Mkdir("newdir", 0755)           // 创建单层
    os.MkdirAll("a/b/c/d", 0755)       // 递归创建

    // 遍历目录
    filepath.Walk(".", func(path string, info os.FileInfo, err error) error {
        if err != nil {
            return err
        }
        fmt.Println(path)
        return nil
    })
}
```

---

# 第 13 章 标准库精选

## encoding/json

```go
import (
    "encoding/json"
    "fmt"
)

type User struct {
    Name    string   `json:"name"`          // 指定 JSON 字段名
    Age     int      `json:"age"`
    Email   string   `json:"email,omitempty"` // omitempty: 零值时忽略
    Hobbies []string `json:"hobbies,omitempty"`
    private string   `json:"-"`             // -: 永远不序列化
}

// 序列化（Go → JSON）
func marshal() {
    u := User{
        Name:    "张三",
        Age:     25,
        Hobbies: []string{"篮球", "编程"},
    }

    data, err := json.Marshal(u)
    if err != nil {
        fmt.Println(err)
        return
    }
    fmt.Println(string(data))
    // {"name":"张三","age":25,"hobbies":["篮球","编程"]}

    // 带缩进的输出
    data, _ = json.MarshalIndent(u, "", "  ")
    fmt.Println(string(data))
}

// 反序列化（JSON → Go）
func unmarshal() {
    jsonStr := `{"name":"李四","age":30,"hobbies":["读书"]}`

    var u User
    err := json.Unmarshal([]byte(jsonStr), &u)
    if err != nil {
        fmt.Println(err)
        return
    }
    fmt.Printf("%+v\n", u)  // {Name:李四 Age:30 Hobbies:[读书]}

    // 解析到 map
    var m map[string]interface{}
    json.Unmarshal([]byte(jsonStr), &m)
    fmt.Println(m["name"])  // 李四
}
```

## time

```go
import (
    "fmt"
    "time"
)

func timeOps() {
    now := time.Now()
    fmt.Println(now)                    // 2024-01-15 14:30:00 +0800 CST
    fmt.Println(now.Format("2006-01-02 15:04:05"))  // 格式化（记住这个模板时间！）
    fmt.Println(now.Format("2006/01/02"))
    fmt.Println(now.Unix())             // 时间戳（秒）
    fmt.Println(now.UnixMilli())        // 时间戳（毫秒）

    // 解析时间
    t, _ := time.Parse("2006-01-02", "2024-01-15")
    fmt.Println(t)

    // 时间运算
    tomorrow := now.Add(24 * time.Hour)
    yesterday := now.Add(-24 * time.Hour)
    fmt.Println(tomorrow.After(now))     // true
    fmt.Println(yesterday.Before(now))   // true
    fmt.Println(tomorrow.Sub(now))       // 24h0m0s

    // 定时器
    timer := time.NewTimer(3 * time.Second)
    <-timer.C
    fmt.Println("3秒到了")

    // 打点器（每隔一段时间执行）
    ticker := time.NewTicker(time.Second)
    for i := 0; i < 3; i++ {
        <-ticker.C
        fmt.Println("滴答")
    }
    ticker.Stop()

    // 超时控制
    select {
    case <-someChannel:
        fmt.Println("收到数据")
    case <-time.After(5 * time.Second):
        fmt.Println("超时了")
    }
}
```

## strings

```go
import "strings"

func stringOps() {
    s := "Hello, 世界"

    strings.Contains(s, "世界")         // true
    strings.HasPrefix(s, "Hello")      // true
    strings.HasSuffix(s, "世界")        // true
    strings.Index(s, "世")             // 7（字节索引）

    strings.ToUpper("hello")           // HELLO
    strings.ToLower("WORLD")           // world

    strings.Trim("  hello  ", " ")     // "hello"
    strings.TrimSpace("  hello  ")      // "hello"

    strings.Replace("a,b,c", ",", "-", 1)   // "a-b,c"（替换1个）
    strings.ReplaceAll("a,b,c", ",", "-")   // "a-b-c"（全部替换）

    strings.Split("a,b,c", ",")         // ["a", "b", "c"]
    strings.Join([]string{"a","b","c"}, "-")  // "a-b-c"

    // 高效拼接（大量字符串拼接场景）
    var builder strings.Builder
    for i := 0; i < 100; i++ {
        builder.WriteString(fmt.Sprintf("第%d行\n", i))
    }
    result := builder.String()
}
```

## strconv

```go
import "strconv"

func strconvOps() {
    // int ↔ string
    s := strconv.Itoa(42)               // int → string: "42"
    n, _ := strconv.Atoi("42")          // string → int: 42

    // string → 其他数字
    f, _ := strconv.ParseFloat("3.14", 64)   // → 3.14
    i, _ := strconv.ParseInt("255", 10, 64)  // → 255（十进制）

    // 数字 → string
    strconv.FormatFloat(3.14159, 'f', 2, 64) // "3.14"
    strconv.FormatInt(255, 16)               // "ff"（十六进制）
    strconv.FormatBool(true)                 // "true"

    // 字符串引用
    strconv.Quote("hello")  // `"hello"`（带引号）
}
```

## net/http

```go
import (
    "fmt"
    "io"
    "net/http"
)

// 发送 GET 请求
func httpGet(url string) {
    resp, err := http.Get(url)
    if err != nil {
        fmt.Println("请求失败:", err)
        return
    }
    defer resp.Body.Close()

    body, _ := io.ReadAll(resp.Body)
    fmt.Println(resp.StatusCode)  // 状态码
    fmt.Println(string(body))     // 响应体
}

// 发送 POST 请求
func httpPost(url string, jsonBody []byte) {
    resp, err := http.Post(url, "application/json", bytes.NewReader(jsonBody))
    if err != nil {
        fmt.Println("请求失败:", err)
        return
    }
    defer resp.Body.Close()
}

// 自定义请求
func httpRequest() {
    req, _ := http.NewRequest("GET", "https://api.example.com/data", nil)
    req.Header.Set("Authorization", "Bearer token123")
    req.Header.Set("User-Agent", "MyApp/1.0")

    client := &http.Client{Timeout: 10 * time.Second}
    resp, err := client.Do(req)
    if err != nil {
        fmt.Println("请求失败:", err)
        return
    }
    defer resp.Body.Close()
}

// 启动 HTTP 服务器
func httpServer() {
    http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
        fmt.Fprintf(w, "Hello, %s!", r.URL.Path[1:])
    })

    http.HandleFunc("/api/hello", func(w http.ResponseWriter, r *http.Request) {
        w.Header().Set("Content-Type", "application/json")
        w.Write([]byte(`{"message":"Hello World"}`))
    })

    fmt.Println("服务启动在 http://localhost:8080")
    http.ListenAndServe(":8080", nil)
}
```

---

# 第 14 章 Go 工具链

## 常用命令

| 命令 | 说明 |
|------|------|
| `go build` | 编译成可执行文件 |
| `go run` | 编译并运行 |
| `go test` | 运行测试 |
| `go fmt` | 格式化代码 |
| `go vet` | 代码静态检查 |
| `go mod init` | 初始化模块 |
| `go mod tidy` | 整理依赖 |
| `go get` | 安装包 |
| `go install` | 编译并安装到 $GOPATH/bin |
| `go env` | 查看环境变量 |
| `go doc` | 查看文档 |

## 测试

```go
// math_test.go（文件名以 _test.go 结尾）
package math

import "testing"

// 测试函数必须以 Test 开头
func TestAdd(t *testing.T) {
    result := Add(2, 3)
    expected := 5

    if result != expected {
        t.Errorf("Add(2, 3) = %d; want %d", result, expected)
    }
}

// 表驱动测试（Go 最常用的测试模式）
func TestAdd_Table(t *testing.T) {
    tests := []struct {
        name     string
        a, b     int
        expected int
    }{
        {"正数相加", 1, 2, 3},
        {"负数相加", -1, -2, -3},
        {"零", 0, 0, 0},
        {"正负相加", 1, -1, 0},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            result := Add(tt.a, tt.b)
            if result != tt.expected {
                t.Errorf("Add(%d, %d) = %d; want %d", tt.a, tt.b, result, tt.expected)
            }
        })
    }
}

// 基准测试
func BenchmarkAdd(b *testing.B) {
    for i := 0; i < b.N; i++ {
        Add(1, 2)
    }
}
```

```bash
# 运行测试
go test                     # 当前包
go test ./...               # 递归所有包
go test -v                  # 详细输出
go test -cover              # 测试覆盖率
go test -run TestAdd        # 运行指定测试
go test -bench=.            # 运行基准测试
```

## 代码格式化与规范

```bash
# 自动格式化
go fmt ./...

# 静态检查
go vet ./...

# 代码规范检查（需安装 golangci-lint）
golangci-lint run

# 生成文档
go doc fmt.Println  # 查看某个函数的文档
```

---

## 速查卡片

### 变量声明

```go
var x int = 10        // 完整声明
var y = 20            // 类型推导
z := 30               // 短变量声明（函数内）
const PI = 3.14       // 常量
```

### 数据类型

```go
bool                   // true/false
string                 // "hello"
int, int8~64          // 整数
uint, uint8~64        // 无符号整数
float32, float64      // 浮点数
byte                  // uint8 别名
rune                  // int32 别名（存 unicode）
```

### 流程控制

```go
if x > 0 { } else { }
if err := fn(); err != nil { }  // if 中声明变量
switch { case x>0: default: }   // 条件 switch
for i := 0; i < n; i++ { }     // for 循环
for _, v := range slice { }     // range 遍历
```

### 容器

```go
arr := [3]int{1, 2, 3}              // 数组（定长）
s := []int{1, 2, 3}                 // 切片（动态）
s = append(s, 4)                    // 追加
m := map[string]int{"a": 1}         // map
type S struct { X int; Y string }   // 结构体
```

### 函数

```go
func f(a int) int { return a }
func f() (int, error) { return 0, nil }  // 多返回值
func f(nums ...int) { }                   // 可变参数
```

### 并发

```go
go func() { }()               // 启动 goroutine
ch := make(chan int)          // 创建 channel
ch := make(chan int, 10)      // 缓冲 channel
ch <- v                       // 发送
v := <-ch                     // 接收
var mu sync.Mutex             // 互斥锁
var rw sync.RWMutex           // 读写锁
var wg sync.WaitGroup         // 等待组
```

### 错误处理

```go
if err != nil {
    return fmt.Errorf("...: %w", err)
}
errors.Is(err, ErrNotFound)   // 判断错误类型
errors.As(err, &target)       // 提取错误
```

### 常见 panic 场景

| 场景 | 原因 | 解决 |
|------|------|------|
| nil pointer | 调用 nil 接口/指针的方法 | 确保初始化 |
| index out of range | 切片/数组越界 | 检查 len |
| nil map assignment | nil map 直接赋值 | `make(map[...]...)` |
| divide by zero | 除法分母为 0 | 检查分母 |
| concurrent map write | 并发写 map | 用 sync.Map 或加锁 |
| close of closed channel | 重复 close channel | 只在发送方 close 一次 |

---

# 第 15 章 开发实务常用框架

> Go 不像 Java 有 Spring 这种"全家桶"，Go 社区更倾向于**小而精的库组合**。下面按实际开发场景分类介绍。

## 15.1 Web 框架

### Gin（最主流，推荐首选）

```go
package main

import (
    "github.com/gin-gonic/gin"
    "net/http"
)

func main() {
    r := gin.Default()

    // 路由 + 分组
    v1 := r.Group("/api/v1")
    {
        v1.GET("/users", func(c *gin.Context) {
            c.JSON(http.StatusOK, gin.H{
                "users": []string{"张三", "李四"},
            })
        })

        v1.POST("/users", func(c *gin.Context) {
            var body struct {
                Name string `json:"name" binding:"required"`
                Age  int    `json:"age" binding:"gte=0,lte=150"`
            }
            if err := c.ShouldBindJSON(&body); err != nil {
                c.JSON(400, gin.H{"error": err.Error()})
                return
            }
            c.JSON(201, body)
        })
    }

    // 路径参数
    r.GET("/users/:id", func(c *gin.Context) {
        id := c.Param("id")
        // 查询参数  /users?page=1&size=10
        page := c.DefaultQuery("page", "1")
        c.String(200, "id=%s, page=%s", id, page)
    })

    // 中间件
    r.Use(gin.Logger(), gin.Recovery())
    // 自定义中间件
    r.Use(func(c *gin.Context) {
        token := c.GetHeader("Authorization")
        if token == "" {
            c.AbortWithStatusJSON(401, gin.H{"error": "未登录"})
            return
        }
        c.Next()
    })

    r.Run(":8080")
}
```

| 特性 | 说明 |
|------|------|
| 路由 | RESTful、分组、路径参数 |
| 中间件 | Logger、Recovery、CORS、自定义 |
| 绑定 | JSON/Form/Query 自动绑定 + 校验 |
| 渲染 | JSON/XML/HTML/Protobuf |
| 生态 | gin-swagger、gin-jwt、gin-session |

### 其他 Web 框架对比

| 框架 | 特点 | 适用场景 |
|------|------|---------|
| **Gin** | 速度快、生态成熟、社区最大 | API 服务、微服务（首选） |
| **Echo** | 简洁、性能略高于 Gin | API 服务 |
| **Fiber** | 借鉴 Express.js，极致性能 | 高并发 API |
| **Beego** | Go 版"RoR"，大而全 | 全栈 Web 应用 |
| **Iris** | 功能极丰富 | 复杂企业应用 |
| **net/http** | 标准库，零依赖 | 简单服务、学习用途 |

### net/http 标准库（零依赖方案）

```go
// 简单场景直接用标准库，不需要框架
package main

import (
    "encoding/json"
    "net/http"
)

func main() {
    mux := http.NewServeMux()

    mux.HandleFunc("/api/hello", func(w http.ResponseWriter, r *http.Request) {
        if r.Method != http.MethodGet {
            http.Error(w, "Method not allowed", 405)
            return
        }

        w.Header().Set("Content-Type", "application/json")
        json.NewEncoder(w).Encode(map[string]string{
            "message": "Hello World",
        })
    })

    // 带中间件
    handler := loggingMiddleware(corsMiddleware(mux))

    http.ListenAndServe(":8080", handler)
}

func loggingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        println(r.Method, r.URL.Path)
        next.ServeHTTP(w, r)
    })
}

func corsMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        w.Header().Set("Access-Control-Allow-Origin", "*")
        if r.Method == "OPTIONS" {
            w.WriteHeader(200)
            return
        }
        next.ServeHTTP(w, r)
    })
}
```

---

## 15.2 ORM 与数据库

### GORM（最主流）

```go
import (
    "gorm.io/gorm"
    "gorm.io/driver/mysql"
)

// 1. 连接数据库
dsn := "user:pass@tcp(127.0.0.1:3306)/dbname?charset=utf8mb4&parseTime=True"
db, err := gorm.Open(mysql.Open(dsn), &gorm.Config{})

// 2. 定义模型
type User struct {
    ID        uint      `gorm:"primaryKey"`
    Name      string    `gorm:"column:name;type:varchar(100);not null;index"`
    Age       int       `gorm:"default:0"`
    Email     string    `gorm:"uniqueIndex"`
    CreatedAt time.Time
    DeletedAt gorm.DeletedAt `gorm:"index"` // 软删除
}

// 3. 自动迁移
db.AutoMigrate(&User{})

// 4. CRUD
// 增
db.Create(&User{Name: "张三", Age: 25})

// 批量增
db.Create(&[]User{{Name: "李四"}, {Name: "王五"}})

// 查
var user User
db.First(&user, 1)                         // 按主键
db.First(&user, "name = ?", "张三")        // 按条件
db.Where("age > ?", 18).Find(&[]User{})     // 批量

// 改
db.Model(&user).Update("age", 26)
db.Model(&user).Updates(User{Name: "张三丰", Age: 30})

// 删（软删除）
db.Delete(&user, 1)
// 真删除
db.Unscoped().Delete(&user, 1)

// 5. 关联
type Order struct {
    ID     uint
    UserID uint
    Amount float64
    User   User `gorm:"foreignKey:UserID"`
}

// 预加载
var orders []Order
db.Preload("User").Find(&orders)
```

**GORM 常用标签：**

| 标签 | 含义 |
|------|------|
| `primaryKey` | 主键 |
| `autoIncrement` | 自增 |
| `not null` | 非空 |
| `uniqueIndex` | 唯一索引 |
| `default:0` | 默认值 |
| `size:255` | 字段长度 |
| `column:xxx` | 指定列名 |
| `-` | 忽略此字段 |

### sqlx（轻量选择）

```go
import "github.com/jmoiron/sqlx"
import _ "github.com/go-sql-driver/mysql"

db, _ := sqlx.Connect("mysql", "user:pass@/dbname")

// 直接写 SQL，结果映射到 struct
type User struct {
    ID   int    `db:"id"`
    Name string `db:"name"`
}

var users []User
db.Select(&users, "SELECT id, name FROM users WHERE age > ?", 18)

// 命名参数
db.NamedExec("INSERT INTO users (name, age) VALUES (:name, :age)",
    User{Name: "张三", Age: 25})

// 适合喜欢手写 SQL、不想用 GORM 的团队
```

### 其他 ORM

| 库 | 特点 | 星级 |
|----|------|------|
| **GORM** | 功能最全，链式调用 | 最流行 |
| **Ent** | Facebook 出品，代码生成，类型安全 | 上升趋势 |
| **sqlx** | 轻量封装标准库 | 经典 |
| **sqlc** | 从 SQL 自动生成类型安全代码 | 性能极致 |
| **Bun** | 现代化 ORM，支持多数据库 | 新秀 |

---

## 15.3 Redis 客户端

### go-redis（最主流）

```go
import "github.com/redis/go-redis/v9"

func main() {
    rdb := redis.NewClient(&redis.Options{
        Addr:     "localhost:6379",
        Password: "",
        DB:       0,
    })

    ctx := context.Background()

    // String
    rdb.Set(ctx, "key", "value", 10*time.Minute)
    val, _ := rdb.Get(ctx, "key").Result()

    // Hash
    rdb.HSet(ctx, "user:1", "name", "张三", "age", 25)
    name, _ := rdb.HGet(ctx, "user:1", "name").Result()
    // 获取整个 hash
    user, _ := rdb.HGetAll(ctx, "user:1").Result()  // map[name:张三 age:25]

    // List（队列）
    rdb.LPush(ctx, "queue", "task1", "task2")
    task, _ := rdb.RPop(ctx, "queue").Result()

    // Set（去重、集合运算）
    rdb.SAdd(ctx, "tags", "Go", "Redis", "Web")
    isMember, _ := rdb.SIsMember(ctx, "tags", "Go").Result()

    // ZSet（排行榜）
    rdb.ZAdd(ctx, "ranking", redis.Z{Score: 100, Member: "张三"})
    rdb.ZAdd(ctx, "ranking", redis.Z{Score: 90, Member: "李四"})
    // 按分数降序
    ranking, _ := rdb.ZRevRangeWithScores(ctx, "ranking", 0, -1).Result()

    // 分布式锁
    ok, _ := rdb.SetNX(ctx, "lock:order:123", 1, 30*time.Second).Result()
    if ok {
        defer rdb.Del(ctx, "lock:order:123")
        // 业务逻辑...
    }

    // Pipeline（批量操作，减少 RTT）
    pipe := rdb.Pipeline()
    pipe.Set(ctx, "a", 1, 0)
    pipe.Set(ctx, "b", 2, 0)
    pipe.Exec(ctx)
}
```

---

## 15.4 配置管理

### Viper（事实标准）

```go
import "github.com/spf13/viper"

func main() {
    v := viper.New()

    // 支持多种格式
    v.SetConfigName("config")  // 文件名（不带后缀）
    v.SetConfigType("yaml")    // 或 json, toml, env
    v.AddConfigPath(".")       // 搜索路径

    if err := v.ReadInConfig(); err != nil {
        panic(err)
    }

    // 环境变量覆盖
    v.AutomaticEnv()
    v.SetEnvPrefix("APP")

    // 读取
    port := v.GetInt("server.port")
    dbHost := v.GetString("database.host")

    // 反序列化到 struct
    type Config struct {
        Server   ServerConfig
        Database DatabaseConfig
    }
    var cfg Config
    v.Unmarshal(&cfg)
}
```

```yaml
# config.yaml
server:
  port: 8080
  mode: release  # debug, release, test

database:
  host: 127.0.0.1
  port: 3306
  user: root
  password: ${DB_PASSWORD}  # 环境变量

redis:
  addr: localhost:6379
  db: 0
```

---

## 15.5 日志库

### Zap（高性能首选）

```go
import "go.uber.org/zap"

func main() {
    // 生产环境（JSON 格式，性能最高）
    logger, _ := zap.NewProduction()
    defer logger.Sync()

    // 开发环境（友好格式）
    // logger, _ := zap.NewDevelopment()

    // 结构化日志
    logger.Info("用户登录成功",
        zap.String("username", "zhangsan"),
        zap.Int("user_id", 1001),
        zap.Duration("耗时", 25*time.Millisecond),
    )

    logger.Error("数据库连接失败",
        zap.String("host", "10.0.0.1"),
        zap.Error(err),
    )

    // SugaredLogger（更灵活的格式）
    sugar := logger.Sugar()
    sugar.Infow("用户登录",
        "username", "zhangsan",
        "ip", "192.168.1.1",
    )
    sugar.Infof("用户 %s 登录成功，耗时 %v", "zhangsan", time.Millisecond*25)
}
```

### 其他日志方案

| 库 | 特点 |
|----|------|
| **Zap** | Uber 出品，性能极致，结构化 |
| **Zerolog** | 零分配 JSON 日志，更轻量 |
| **log/slog** | Go 1.21+ 内置的结构化日志 |
| **Logrus** | 老牌日志库，兼容性好 |

---

## 15.6 进程内定时任务

### Cron

```go
import "github.com/robfig/cron/v3"

func main() {
    c := cron.New(cron.WithSeconds()) // 支持秒级 cron

    // @every 写法（最实用）
    c.AddFunc("@every 5s", func() {
        log.Println("每5秒执行")
    })

    c.AddFunc("@every 10m", func() {
        log.Println("每10分钟执行")
    })

    c.AddFunc("0 30 2 * * *", func() {
        log.Println("每天凌晨2:30执行")
    })

    // 也可用 struct
    type MyJob struct{}
    func (j MyJob) Run() { log.Println("自定义Job") }
    c.AddJob("@every 1h", MyJob{})

    c.Start()
    // 阻塞或其他 goroutine 中 c.Stop()
    select {}
}
```

---

## 15.7 消息队列

### RabbitMQ 客户端

```go
import amqp "github.com/rabbitmq/amqp091-go"

func sendMQ() {
    conn, _ := amqp.Dial("amqp://guest:guest@localhost:5672/")
    defer conn.Close()

    ch, _ := conn.Channel()
    defer ch.Close()

    // 声明队列
    q, _ := ch.QueueDeclare("task_queue", true, false, false, false, nil)

    // 发布消息
    ch.PublishWithContext(ctx, "", q.Name, false, false,
        amqp.Publishing{
            ContentType: "text/plain",
            Body:        []byte("Hello World"),
        })

    // 消费消息
    msgs, _ := ch.Consume(q.Name, "", false, false, false, false, nil)

    for msg := range msgs {
        process(msg.Body)
        msg.Ack(false)  // 手动确认
    }
}
```

### Kafka 客户端

```go
import "github.com/IBM/sarama"

// 生产者
producer, _ := sarama.NewSyncProducer([]string{"localhost:9092"}, nil)
producer.SendMessage(&sarama.ProducerMessage{
    Topic: "orders",
    Value: sarama.StringEncoder(`{"order_id": 123}`),
})

// 消费者
consumer, _ := sarama.NewConsumer([]string{"localhost:9092"}, nil)
partitionConsumer, _ := consumer.ConsumePartition("orders", 0, sarama.OffsetNewest)

for msg := range partitionConsumer.Messages() {
    fmt.Printf("收到: %s\n", string(msg.Value))
}
```

---

## 15.8 测试相关

### Testify（断言 + Mock）

```go
import (
    "testing"
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/mock"
)

// 断言
func TestAdd(t *testing.T) {
    assert.Equal(t, 4, Add(2, 2))
    assert.NotNil(t, result)
    assert.Contains(t, "hello world", "world")
    assert.Greater(t, 10, 5)
}

// Mock
type MockUserRepo struct {
    mock.Mock
}

func (m *MockUserRepo) GetUser(id int) (*User, error) {
    args := m.Called(id)
    return args.Get(0).(*User), args.Error(1)
}

func TestUserService(t *testing.T) {
    mockRepo := new(MockUserRepo)
    mockRepo.On("GetUser", 1).Return(&User{Name: "张三"}, nil)

    svc := NewUserService(mockRepo)
    user, err := svc.GetUser(1)

    assert.NoError(t, err)
    assert.Equal(t, "张三", user.Name)
    mockRepo.AssertExpectations(t)  // 验证 mock 方法确实被调用了
}
```

---

## 15.9 RPC 框架

### gRPC + Protocol Buffers

```protobuf
// user.proto
syntax = "proto3";
option go_package = "./pb";

message UserRequest { int64 id = 1; }
message UserResponse { int64 id = 1; string name = 2; int32 age = 3; }

service UserService {
    rpc GetUser(UserRequest) returns (UserResponse);
    rpc ListUsers(stream UserRequest) returns (stream UserResponse);
}
```

```go
// 服务端
type userServer struct {
    pb.UnimplementedUserServiceServer
}

func (s *userServer) GetUser(ctx context.Context, req *pb.UserRequest) (*pb.UserResponse, error) {
    return &pb.UserResponse{
        Id:   req.Id,
        Name: "张三",
        Age:  25,
    }, nil
}

// 客户端
conn, _ := grpc.Dial("localhost:50051", grpc.WithInsecure())
client := pb.NewUserServiceClient(conn)

resp, _ := client.GetUser(context.Background(), &pb.UserRequest{Id: 1})
fmt.Println(resp.Name, resp.Age)
```

---

## 15.10 项目结构推荐

### 标准 Go 项目布局

```
myapp/
├── main.go                  # 入口
├── go.mod                   # 模块定义
├── go.sum                   # 依赖校验
├── config/                  # 配置
│   └── config.go
├── internal/                # 私有代码（外部不可导入）
│   ├── handler/             # HTTP 处理器（Controller 层）
│   │   ├── user_handler.go
│   │   └── order_handler.go
│   ├── service/             # 业务逻辑层
│   │   └── user_service.go
│   ├── repository/          # 数据访问层（DAO）
│   │   └── user_repo.go
│   └── model/               # 数据模型
│       └── user.go
├── pkg/                     # 可复用的公共代码
│   └── middleware/
│       └── auth.go
├── cmd/                      # 多个可执行程序（可选）
│   └── worker/
│       └── main.go
├── api/                      # API 定义（proto、openapi 等）
├── scripts/                  # 脚本
└── deployments/              # Docker、k8s 部署文件
```

### MVC 分层示例

```go
// model/user.go —— 数据模型层
package model

type User struct {
    ID   int64  `json:"id"`
    Name string `json:"name"`
}

// repository/user_repo.go —— 数据访问层
package repository

func GetUserByID(db *gorm.DB, id int64) (*model.User, error) {
    var user model.User
    err := db.First(&user, id).Error
    return &user, err
}

// service/user_service.go —— 业务逻辑层
package service

func GetUserProfile(repo UserRepository, id int64) (*model.User, error) {
    if id <= 0 {
        return nil, errors.New("invalid user id")
    }
    return repo.GetUserByID(id)
}

// handler/user_handler.go —— 接入层（Controller）
package handler

func (h *UserHandler) GetUser(c *gin.Context) {
    id, _ := strconv.ParseInt(c.Param("id"), 10, 64)
    user, err := h.service.GetUserProfile(id)
    if err != nil {
        c.JSON(404, gin.H{"error": "用户不存在"})
        return
    }
    c.JSON(200, user)
}
```

---

## 15.11 框架选型速查

```
Web 框架:     Gin（API首选） > Echo > Fiber > net/http（零依赖场景）
ORM:          GORM（首选） > Ent（类型安全） > sqlx（手写SQL）
Redis:        go-redis（唯一主流）
配置:         Viper（标配）
日志:         Zap（生产环境） > slog（标准库，Go 1.21+）
消息队列:     RabbitMQ → amqp091-go | Kafka → sarama
定时任务:     cron（进程内） > asynq（Redis 分布式）
RPC:          gRPC（首选）
测试:         testify（断言+Mock） + 标准 testing
API文档:      swaggo/swag（自动生成 Swagger）
参数校验:     go-playground/validator
重试:         cenkalti/backoff（指数退避）
限流:         golang.org/x/time/rate（令牌桶）
```

---

> **Go 的核心哲学：简洁、并发、高效。不追求花哨的语法，而是用简单的工具构建可靠的软件。**
