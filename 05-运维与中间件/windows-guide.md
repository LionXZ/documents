# Windows 速查手册

> 一份通俗易懂的 Windows 命令行文档，涵盖 CMD 和 PowerShell 中最常用的命令和概念，适合快速查阅和上手。

---

## 目录

- [1. 基础概念](#1-基础概念)
- [2. 文件与目录操作](#2-文件与目录操作)
- [3. 文件内容查看与编辑](#3-文件内容查看与编辑)
- [4. 用户与权限](#4-用户与权限)
- [5. 进程与服务管理](#5-进程与服务管理)
- [6. 磁盘与内存](#6-磁盘与内存)
- [7. 网络操作](#7-网络操作)
- [8. 软件安装与包管理](#8-软件安装与包管理)
- [9. 压缩与解压](#9-压缩与解压)
- [10. 批处理与 PowerShell 脚本](#10-批处理与-powershell-脚本)
- [11. 文本处理](#11-文本处理)
- [12. 日志与系统信息](#12-日志与系统信息)
- [13. 定时任务](#13-定时任务)
- [14. 远程连接](#14-远程连接)
- [15. 实用技巧汇总](#15-实用技巧汇总)

---

## 1. 基础概念

### 1.1 CMD vs PowerShell vs Terminal

| 工具 | 说明 | 特点 |
|------|------|------|
| CMD (cmd.exe) | 传统命令行，源于 DOS | 语法简单，脚本为 .bat/.cmd |
| PowerShell (powershell.exe) | 现代 Shell，面向对象 | 管道传对象而非文本，脚本为 .ps1 |
| Windows Terminal | 统一终端应用 | 可同时打开 CMD/PowerShell/WSL 标签页 |
| pwsh.exe | PowerShell 7+（跨平台版） | 基于 .NET Core，推荐新项目使用 |

### 1.2 核心术语

| 术语 | 说明 | Linux 类比 |
|------|------|-----------|
| 驱动器盘符 C:\ | 系统盘，类似 Windows 的 / | Linux 的 / |
| 注册表 Registry | 系统和软件的配置数据库 | /etc 目录 |
| 环境变量 | PATH、TEMP 等 | 完全相同的概念 |
| 管理员 Administrator | 超级管理员账户 | root |
| 用户目录 %USERPROFILE% | C:\Users\你的用户名 | ~ 或 /home/user |
| AppData | 应用的配置和数据 | ~/.config / ~/.local |
| CMD | 传统命令行解释器 | Bash |
| PowerShell | 面向对象的现代 Shell | Bash + Python 的感觉 |

### 1.3 目录结构速览

```
C:\                          # 系统盘根目录
├── C:\Windows               # 系统文件（不要乱动）
│   ├── C:\Windows\System32  # 系统核心程序
│   └── C:\Windows\SysWOW64 # 32 位系统程序
├── C:\Program Files         # 64 位程序安装目录
├── C:\Program Files (x86)   # 32 位程序安装目录
├── C:\Users                 # 用户目录
│   └── C:\Users\用户名
│       ├── Desktop          # 桌面
│       ├── Documents        # 文档
│       ├── Downloads        # 下载
│       └── AppData          # 应用数据（通常是隐藏的）
│           ├── Local        # 本机应用数据
│           ├── Roaming      # 漫游应用数据
│           └── LocalLow     # 低权限应用数据
├── C:\ProgramData           # 所有用户共享的应用数据（隐藏）
└── C:\Temp                  # 临时文件
```

### 1.4 环境变量速查

```bat
REM CMD 查看环境变量
echo %USERPROFILE%            REM C:\Users\你的用户名
echo %APPDATA%                REM C:\Users\你的用户名\AppData\Roaming
echo %LOCALAPPDATA%           REM C:\Users\你的用户名\AppData\Local
echo %TEMP%                   REM 临时目录
echo %PATH%                   REM 可执行文件搜索路径
echo %HOMEDRIVE%%HOMEPATH%    REM 用户目录另一种写法
echo %COMPUTERNAME%           REM 计算机名
echo %USERNAME%               REM 当前用户名
echo %OS%                     REM 操作系统
echo %PROCESSOR_ARCHITECTURE% REM CPU 架构
```

```powershell
# PowerShell 查看环境变量（推荐）
$env:USERPROFILE
$env:APPDATA
$env:PATH -split ';'          # 按行显示 PATH（更易读）
Get-ChildItem Env:            # 列出所有环境变量
```

---

## 2. 文件与目录操作

### 2.1 导航

```bat
REM CMD
REM 当前目录
cd                           REM 显示当前目录（等同于 pwd）
echo %cd%                    REM 同上

REM 切换目录
cd C:\Users                  REM 绝对路径
cd ..                        REM 返回上一级
cd \                         REM 回到盘符根目录
D:                           REM 切换到 D 盘（盘符切换用 盘符:）

REM 列出目录内容
dir                          REM 列出文件
dir /b                       REM 简洁模式（只要文件名）
dir /a                       REM 包括隐藏文件和系统文件
dir /s                       REM 递归子目录
dir /o:n                     REM 按名称排序
dir /o:-d                    REM 按日期倒序（最新的在前）
dir *.txt                    REM 筛选 .txt 文件
```

```powershell
# PowerShell
# 当前目录
Get-Location                  # 或 pwd / gl
$PWD                          # 同上

# 切换目录
Set-Location C:\Users         # 或 cd / sl
cd ..                         # 返回上一级
cd ~                          # 回到用户目录

# 列出目录内容
Get-ChildItem                 # 或 ls / dir / gci
ls -Hidden                    # 包括隐藏文件
ls -Recurse *.log             # 递归查找（-Recurse 或 -r）
ls | Sort-Object Length -Desc # 按大小倒序
ls | Sort-Object LastWriteTime -Desc  # 按时间倒序
```

### 2.2 创建与删除

```bat
REM CMD
REM 创建目录
mkdir project                 REM 创建一个
mkdir a\b\c\d                 REM 递归创建多层目录（Windows 原生支持）

REM 创建文件
type nul > file.txt           REM 创建空文件
echo hello > file.txt         REM 创建并写入内容
copy nul file.txt             REM 另一种创建空文件的方式

REM 删除（没有回收站！）
del file.txt                  REM 删除文件
del *.tmp                     REM 批量删除
del /f file.txt               REM 强制删除只读文件
rmdir folder                  REM 删除空目录
rmdir /s folder               REM 递归删除目录（会确认）
rmdir /s /q folder            REM 静默递归删除（不确认，危险！）
```

```powershell
# PowerShell
# 创建目录
New-Item -ItemType Directory project        # 或 mkdir project
mkdir a/b/c/d -Force                        # 递归创建

# 创建文件
New-Item file.txt                            # 或 ni file.txt
"" > file.txt                                # 创建空文件

# 删除
Remove-Item file.txt           # 或 rm / del / ri
Remove-Item *.tmp              # 批量删除
Remove-Item folder -Recurse -Force  # 递归强制删除
```

### 2.3 复制与移动

```bat
REM CMD
REM 复制
copy source.txt dest.txt       REM 复制文件
copy /y source.txt dest.txt   REM 覆盖不提示
xcopy source\ dest\ /e /i /h  REM 复制目录（/e 含空目录 /i 目标是目录 /h 含隐藏文件）
robocopy source\ dest\ /mir   REM 镜像同步（更强大的复制工具，推荐）

REM 移动/重命名
move old.txt new.txt           REM 重命名文件
ren old.txt new.txt            REM 同上（纯重命名）
move file.txt D:\backup\       REM 移动文件
move folder1 folder2           REM 重命名目录
```

```powershell
# PowerShell
# 复制
Copy-Item source.txt dest.txt          # 或 cp / copy
Copy-Item source\ dest\ -Recurse       # 复制目录
Copy-Item source\ dest\ -Recurse -Force  # 覆盖

# 移动/重命名
Move-Item old.txt new.txt              # 或 mv / move
Rename-Item old.txt new.txt            # 或 ren
```

### 2.4 查找

```bat
REM CMD
REM where：查找可执行文件的位置（类似 Linux which）
where python                    REM 找到 python 的路径
where notepad                   REM 找到记事本的路径

REM dir 搜索
dir /s /b *.log                 REM 当前目录及子目录下所有 .log 文件

REM where /r：递归搜索任意文件
where /r . *.txt                REM 当前目录及子目录下所有 .txt 文件
where /r C:\Project *.config   REM 指定目录下搜索
```

```powershell
# PowerShell
# Get-Command：查找命令的位置（类似 which）
Get-Command python              # 或 gcm python
(Get-Command python).Source     # 只看路径

# Get-ChildItem：递归查找文件（类似 find）
Get-ChildItem -Recurse -Filter "*.log"   # 递归找 .log
Get-ChildItem -Recurse -Filter "*.log" | Select-Object FullName
ls -r *.log | select FullName            # 简写

# 按大小查找
ls -r | Where-Object { $_.Length -gt 100MB }

# 按时间查找（最近 7 天）
ls -r | Where-Object { $_.LastWriteTime -gt (Get-Date).AddDays(-7) }

# 找到并执行操作
ls -r *.tmp | Remove-Item       # 找到并删除
```

### 2.5 文件信息

```bat
REM CMD
REM 文件属性
attrib file.txt                 REM 查看/修改文件属性（R=只读 H=隐藏 S=系统 A=存档）
attrib +r file.txt              REM 设为只读
attrib -r file.txt              REM 去掉只读

REM 目录大小（CMD 没有直接命令，用 PowerShell 或 dir 变通）
dir /s folder                   REM 最后一行会显示总大小

REM 文件统计
find /c /v "" file.txt          REM 统计行数（变通方法）
```

```powershell
# PowerShell
# 文件信息
Get-Item file.txt               # 或 gi file.txt
Get-Item file.txt | Format-List *  # 全部属性

# 目录大小
(ls -r folder | Measure-Object -Property Length -Sum).Sum  # 字节
"{0:N2} MB" -f ((ls -r folder | Measure-Object Length -Sum).Sum / 1MB)  # 转为 MB

# 文件统计
Get-Content file.txt | Measure-Object -Line    # 统计行数
Get-Content file.txt | Measure-Object -Word    # 统计单词数
Get-Content file.txt | Measure-Object -Char    # 统计字符数
```

---

## 3. 文件内容查看与编辑

### 3.1 查看命令对比

| 命令 | CMD | PowerShell | 适用场景 |
|------|-----|------------|---------|
| 全量输出 | type | Get-Content / type | 小文件 |
| 分页浏览 | more | more / Out-Host -Paging | 大文件 |
| 看前 N 行 | — | gc file -Head 20 | 看文件开头 |
| 看后 N 行 | — | gc file -Tail 20 | 看文件末尾 |
| 实时追踪 | — | gc file -Wait | 查日志（类似 tail -f） |

```bat
REM CMD
type file.txt                  REM 显示全部内容
type file.txt | more           REM 分页显示（空格下一页，回车下一行）
more file.txt                  REM 同上
more +10 file.txt              REM 从第 10 行开始显示
```

```powershell
# PowerShell
# 全量输出
Get-Content file.txt           # 或 gc / cat / type

# 分页浏览
Get-Content huge.log | Out-Host -Paging

# 看前 20 行
Get-Content file.txt -Head 20   # 或 gc file.txt -First 20
gc file.txt | Select-Object -First 20

# 看后 20 行（查日志必备）
Get-Content app.log -Tail 20    # 或 gc app.log -Last 20

# 🔥 实时追踪日志（类似 tail -f）
Get-Content app.log -Wait       # Ctrl+C 退出
Get-Content app.log -Tail 100 -Wait  # 追踪，但先显示最后 100 行

# 看中间几行
gc file.txt | Select-Object -Skip 10 -First 10  # 跳过 10 行，取接下来 10 行（11-20 行）

# 大文件高效读取
[System.IO.File]::ReadLines("huge.log") | Select-Object -First 1000
```

### 3.2 文本编辑器

```bat
REM 记事本
notepad file.txt               REM 基本文本编辑
notepad++ file.txt             REM 如果装了 Notepad++

REM 命令行编辑器（Windows 没有自带 vim/nano，需安装）
REM 可以装 Git for Windows 获得 vim，或装 micro 等
```

```powershell
# PowerShell 自带 ISE（集成脚本环境）
ise file.ps1                   # 图形化编辑 PowerShell 脚本

# VS Code（推荐）
code file.txt                  # 如果装了 VS Code 并配置了 PATH
code .                         # 打开当前目录为项目
```

---

## 4. 用户与权限

### 4.1 权限体系

Windows 权限比 Linux 复杂，核心概念：

- **ACL (访问控制列表)**：每个文件/目录有 ACL，包含多个 ACE（访问控制条目）
- **SID (安全标识符)**：每个用户/组的唯一 ID（类似 UID/GID）
- **icacls**：管理文件权限的命令行工具

```
权限类型：
  F  = 完全控制 (Full Control)
  M  = 修改 (Modify)
  RX = 读取和执行 (Read & Execute)
  R  = 读取 (Read)
  W  = 写入 (Write)
  D  = 删除 (Delete)
```

### 4.2 查看与修改权限

```bat
REM CMD - icacls
REM 查看权限
icacls file.txt                REM 查看文件的 ACL
icacls folder\                 REM 查看目录的 ACL

REM 修改权限
icacls file.txt /grant Everyone:F       REM 给所有人完全控制（危险！）
icacls file.txt /grant username:R       REM 给某用户只读权限
icacls file.txt /grant "username":(RX)  REM 给读+执行
icacls file.txt /remove username        REM 移除某用户的权限

REM 重置权限
icacls file.txt /reset                  REM 恢复继承的默认权限

REM 递归修改
icacls folder\ /grant username:F /t     REM /t 递归应用到所有子项

REM 查看所有权
dir /q file.txt                         REM 显示所有者
```

```powershell
# PowerShell
# 查看权限
Get-Acl file.txt | Format-List           # 查看 ACL

# 修改权限
$acl = Get-Acl file.txt
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule("username","Read","Allow")
$acl.SetAccessRule($rule)
Set-Acl file.txt $acl

# 更简单的方式：直接用 icacls（PowerShell 也能调用）
icacls file.txt /grant username:R
```

### 4.3 用户管理

```bat
REM CMD
REM 当前用户
whoami                         REM 当前用户名
whoami /user                   REM 当前用户的 SID
whoami /groups                 REM 当前用户所属的组
echo %USERNAME%                REM 用户名

REM 查看所有用户
net user                       REM 列出所有本地用户
net user username              REM 查看某用户详细信息

REM 管理用户（需要管理员权限）
net user newuser pwd123 /add   REM 创建用户
net user newuser /delete       REM 删除用户
net user newuser *             REM 修改密码（交互式输入）

REM 用户组
net localgroup                 REM 列出所有本地组
net localgroup Administrators  REM 查看管理员组
net localgroup Administrators newuser /add    REM 将用户加入管理员组
net localgroup Administrators newuser /delete REM 从管理员组移除
```

```powershell
# PowerShell
# 当前用户信息
whoami
[System.Security.Principal.WindowsIdentity]::GetCurrent().Name

# 本地用户管理（需要管理员权限，推荐使用 CMD 的 net user）
# PowerShell 原生方式较复杂，通常直接调用 net user

# Active Directory 用户（域环境）
Get-ADUser -Filter *           # 列出所有 AD 用户
Get-ADUser username            # 查看某用户
```

### 4.4 提权运行

```bat
REM CMD - runas（以其他用户身份运行）
runas /user:Administrator cmd  REM 以管理员身份打开 CMD
runas /user:domain\user cmd    REM 以域用户身份运行

REM 以管理员身份运行程序的常见做法：
REM 右键 → "以管理员身份运行"
REM 或在 PowerShell 中：Start-Process cmd -Verb RunAs
```

```powershell
# PowerShell 提权
Start-Process powershell -Verb RunAs     # 以管理员身份打开新 PowerShell
Start-Process cmd -Verb RunAs            # 以管理员身份打开新 CMD
```

---

## 5. 进程与服务管理

### 5.1 查看进程

```bat
REM CMD
REM tasklist：查看进程
tasklist                       REM 列出所有进程
tasklist /v                    REM 详细信息
tasklist /svc                  REM 显示进程对应的服务
tasklist /fi "IMAGENAME eq notepad.exe"   REM 按名称过滤
tasklist /fi "MEMUSAGE gt 100000"        REM 内存使用大于 100MB
tasklist /fi "STATUS eq running"         REM 只显示运行中的进程
tasklist /m                     REM 列出进程加载的 DLL

REM 字段含义：
REM 映像名称 = 进程名
REM PID      = 进程 ID
REM 会话名    = 会话
REM 内存使用  = 物理内存占用 (KB)
```

```powershell
# PowerShell
Get-Process                          # 或 ps / gps
Get-Process | Sort-Object CPU -Desc  # 按 CPU 倒序
Get-Process | Sort-Object WS -Desc   # 按内存倒序（WS = Working Set）
Get-Process notepad                  # 查找特定进程
Get-Process | Where-Object { $_.CPU -gt 10 }  # CPU 时间 > 10s 的进程
Get-Process | Select-Object Name, Id, CPU, WorkingSet | Format-Table

# 查看进程树
Get-Process | Format-List Name, Id, Path, Company
```

### 5.2 终止进程

```bat
REM CMD
REM taskkill：终止进程
taskkill /pid 1234             REM 按 PID 终止
taskkill /pid 1234 /f          REM 强制终止（/f = force）
taskkill /im notepad.exe       REM 按映像名称终止
taskkill /im notepad.exe /f    REM 强制按名称终止
taskkill /im chrome.exe /t     REM /t 同时终止子进程

REM 经典组合：找到并杀掉
tasklist | findstr "notepad"   REM 先找到进程
```

```powershell
# PowerShell
Stop-Process -Id 1234                   # 或 kill 1234
Stop-Process -Name notepad              # 或 kill -Name notepad
Stop-Process -Name notepad -Force       # 强制终止

# 按内存占用杀掉
Get-Process | Where-Object { $_.WS -gt 1GB } | Stop-Process
```

### 5.3 服务管理

```bat
REM CMD - sc 命令（服务控制管理器）
sc query                        REM 查看所有运行中的服务
sc query state= all             REM 查看所有服务（注意等号后有空格）
sc query nginx                  REM 查看特定服务
sc start nginx                  REM 启动服务
sc stop nginx                   REM 停止服务
sc config nginx start= auto     REM 设为开机自启
sc config nginx start= demand   REM 设为手动启动
sc config nginx start= disabled REM 禁止启动

REM net 命令（更简单的服务操作）
net start                       REM 列出已启动的服务
net start nginx                 REM 启动服务
net stop nginx                  REM 停止服务
net start | findstr nginx       REM 查找某服务是否启动
```

```powershell
# PowerShell 服务管理
Get-Service                          # 查看所有服务
Get-Service | Where-Object Status -eq "Running"
Get-Service nginx                    # 查看特定服务
Start-Service nginx                  # 启动
Stop-Service nginx                   # 停止
Restart-Service nginx                # 重启
Set-Service nginx -StartupType Automatic  # 设为开机自启

# 查看服务依赖
Get-Service nginx -DependentServices   # 依赖此服务的其他服务
Get-Service nginx -RequiredServices    # 此服务依赖的其他服务
```

### 5.4 任务管理器

```bat
REM 打开任务管理器
taskmgr                        REM 图形界面
Ctrl+Shift+Esc                 REM 快捷键（最常用）
```

---

## 6. 磁盘与内存

### 6.1 磁盘

```bat
REM CMD
REM 查看磁盘使用
wmic logicaldisk get size,freespace,caption   # 磁盘分区使用率
wmic logicaldisk get DeviceID,FileSystem,Size,FreeSpace
fsutil volume diskfree C:                     # C 盘空间

REM 查看目录占用（CMD 没有 du 命令）
dir /s folder                   REM 总大小在最后一行

REM 磁盘管理
diskpart                       REM 打开磁盘分区工具（交互式）
REM diskpart> list disk        REM 列出所有磁盘
REM diskpart> select disk 0    REM 选择磁盘
REM diskpart> list partition   REM 列出分区

REM 磁盘检查
chkdsk C:                      REM 检查 C 盘（只读模式）
chkdsk C: /f                   REM 修复文件系统错误
chkdsk C: /r                   REM 查找坏扇区并恢复
```

```powershell
# PowerShell
# 磁盘使用
Get-PSDrive -PSProvider FileSystem   # 查看所有驱动器
Get-Volume                           # 查看卷信息

# 目录大小（以 GB 显示）
(ls -r folder | Measure-Object Length -Sum).Sum / 1GB

# 找到大文件
ls -r C:\ -ErrorAction SilentlyContinue |
    Where-Object { $_.Length -gt 1GB } |
    Select-Object FullName, @{N="SizeGB";E={[math]::Round($_.Length/1GB,2)}}

# 磁盘清理
cleanmgr /sagerun:1             # 运行磁盘清理
```

### 6.2 内存

```bat
REM CMD
REM systeminfo：查看内存信息
systeminfo | findstr "内存"     REM 中文系统
systeminfo | findstr "Memory"  REM 英文系统

REM wmic 查看内存
wmic memorychip get capacity   REM 物理内存容量（字节）
wmic os get TotalVisibleMemorySize,FreePhysicalMemory  REM 总内存和可用内存
```

```powershell
# PowerShell
# 内存总览
systeminfo | Select-String "内存"     # 中文
systeminfo | Select-String "Memory"   # 英文

# 更精确的内存信息
Get-CimInstance Win32_PhysicalMemory | Select-Object Capacity, Speed, Manufacturer
Get-CimInstance Win32_OperatingSystem | Select-Object TotalVisibleMemorySize, FreePhysicalMemory

# 计算可用内存 GB
$os = Get-CimInstance Win32_OperatingSystem
"总内存: {0:N2} GB" -f ($os.TotalVisibleMemorySize / 1MB)
"可用: {0:N2} GB" -f ($os.FreePhysicalMemory / 1MB)

# 查看内存占用 Top 进程
Get-Process | Sort-Object WS -Desc | Select-Object Name, Id, @{N="MemoryMB";E={[math]::Round($_.WS/1MB,2)}} -First 10

# 任务管理器
taskmgr                        # 图形化查看（性能标签页 → 内存）
```

---

## 7. 网络操作

### 7.1 网络诊断

```bat
REM CMD
REM 查看 IP
ipconfig                       REM 基础信息
ipconfig /all                  REM 详细信息（MAC 地址、DNS、DHCP 等）
ipconfig /release              REM 释放 DHCP IP
ipconfig /renew                REM 重新获取 DHCP IP
ipconfig /flushdns             REM 刷新 DNS 缓存（常用！）

REM 连通性测试
ping 8.8.8.8                   REM 测试连通性
ping -t 8.8.8.8                REM 持续 ping（Ctrl+C 退出）
ping -n 4 google.com           REM 发 4 个包

REM 路由追踪
tracert google.com             REM 看经过哪些节点
tracert -d google.com          REM 不解析主机名（更快）
tracert -h 10 google.com       REM 最多 10 跳

REM 路由表
route print                    REM 查看路由表
route print -4                 REM 只看 IPv4
netstat -r                     REM 同上

REM DNS 查询
nslookup google.com            REM 查询 DNS
nslookup google.com 8.8.8.8   REM 指定 DNS 服务器查询
nslookup -type=mx google.com   REM 查询 MX 记录（邮件）

REM ARP 表
arp -a                         REM 查看 ARP 缓存（IP-MAC 对照）
```

```powershell
# PowerShell
# IP 信息
Get-NetIPAddress                        # 查看所有 IP
Get-NetIPConfiguration                  # 网络配置总览
Get-NetAdapter                          # 查看网卡信息

# 连通性测试
Test-Connection google.com -Count 4     # 类似 ping -n 4
Test-Connection google.com              # 默认 4 次

# 路由追踪
Test-Connection google.com -Traceroute  # PowerShell 方式

# DNS
Resolve-DnsName google.com              # 类似 nslookup
Resolve-DnsName google.com -Type MX     # 查询 MX 记录

# 刷新 DNS
Clear-DnsClientCache                    # 等同于 ipconfig /flushdns
```

### 7.2 端口与连接

```bat
REM CMD - netstat
REM 端口监听
netstat -ano                   REM 查看所有连接和监听（-a 所有 -n 数字 -o PID）
netstat -ano | findstr 8080   REM 查看 8080 端口
netstat -ano | findstr LISTENING  REM 只看监听的

REM 查看连接统计
netstat -s                     REM 协议统计

REM 查看某进程的网络连接
netstat -ano | findstr 12345  REM 按 PID 过滤

REM 检查远程端口
telnet 10.0.0.1 3306          REM 测试端口是否通（需要先启用 Telnet 客户端）
REM Windows 没有 nc 命令，可用 Test-NetConnection (PowerShell)
```

```powershell
# PowerShell
# 端口监听
Get-NetTCPConnection -State Listen      # 所有监听的 TCP 端口
Get-NetTCPConnection -State Listen | Where-Object LocalPort -eq 8080
Get-NetUDPEndpoint                       # UDP 端点

# 检查远程端口（PowerShell 版 nc）
Test-NetConnection 10.0.0.1 -Port 3306   # 测试端口是否通
Test-NetConnection google.com -Port 443  # 测试 HTTPS
tnc 10.0.0.1 -p 3306                     # 简写

# 查看进程对应的网络连接
Get-Process -Id 12345 | Select-Object Name, Id
Get-NetTCPConnection -OwningProcess 12345
```

### 7.3 防火墙

```bat
REM CMD - netsh advfirewall
REM 查看防火墙状态
netsh advfirewall show allprofiles

REM 添加入站规则（开放端口）
netsh advfirewall firewall add rule name="Open Port 8080" dir=in action=allow protocol=TCP localport=8080

REM 删除规则
netsh advfirewall firewall delete rule name="Open Port 8080"

REM 启用/禁用防火墙
netsh advfirewall set allprofiles state on
netsh advfirewall set allprofiles state off
```

```powershell
# PowerShell 防火墙（更友好）
Get-NetFirewallRule | Where-Object Enabled -eq True   # 启用的规则
Get-NetFirewallProfile | Select-Object Name, Enabled  # 查看各配置文件状态

# 新增防火墙规则
New-NetFirewallRule -DisplayName "Open 8080" -Direction Inbound -Protocol TCP -LocalPort 8080 -Action Allow

# 删除
Remove-NetFirewallRule -DisplayName "Open 8080"

# 启用/禁用防火墙
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True
```

### 7.4 下载文件

```bat
REM CMD（Windows 10+ 自带 curl）
curl https://example.com/file.zip -o file.zip   REM 下载文件
curl https://api.example.com/users             REM GET 请求
curl -I https://example.com                   REM 只看响应头

REM certutil（更古老的下载方式）
certutil -urlcache -split -f https://example.com/file.zip file.zip
```

```powershell
# PowerShell
# Invoke-WebRequest：下载和 HTTP 请求
Invoke-WebRequest https://example.com              # 或 curl / wget（别名）
Invoke-WebRequest https://example.com/file.zip -OutFile file.zip  # 下载

# Invoke-RestMethod：REST API 请求（自动解析 JSON）
$users = Invoke-RestMethod https://api.example.com/users  # 或 irm
$users | ConvertTo-Json                              # 格式化为 JSON

# POST 请求
$body = @{ name = "zhang"; age = 25 } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri https://api.example.com/users -Body $body -ContentType "application/json"

# 下载进度条
Invoke-WebRequest -Uri "https://example.com/large.zip" -OutFile "large.zip"
```

### 7.5 文件传输

```bat
REM CMD（Windows 10+ 自带 OpenSSH）
REM scp：远程拷贝
scp file.txt user@10.0.0.1:/home/user/
scp user@10.0.0.1:/home/user/file.txt ./
scp -r folder/ user@10.0.0.1:/home/user/

REM sftp：交互式文件传输
sftp user@10.0.0.1
REM sftp> get remote.txt     REM 下载
REM sftp> put local.txt      REM 上传
```

```powershell
# PowerShell（同上，支持 scp/sftp）
# 也可以使用 WinRM 传输文件
Copy-Item -Path .\file.txt -Destination \\remote-pc\C$\Temp\ -ToSession $session
```

---

## 8. 软件安装与包管理

### 8.1 winget（Windows 官方包管理器，推荐）

```bat
REM winget（Windows 10 1809+ 自带，或从 Microsoft Store 安装）
REM 搜索
winget search nginx            REM 搜索软件
winget search python           REM 查找 Python

REM 安装
winget install Git.Git         REM 安装 Git
winget install Microsoft.VisualStudioCode  REM 安装 VS Code
winget install Python.Python.3.12          REM 安装 Python

REM 卸载
winget uninstall Git.Git

REM 升级
winget upgrade                 REM 查看可升级的软件
winget upgrade --all           REM 升级所有软件

REM 列表
winget list                    REM 列出已安装
winget show Firefox            REM 查看详细信息
```

### 8.2 Chocolatey（老牌第三方包管理器）

```powershell
# 安装 Chocolatey（需要管理员 PowerShell）
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# 常用命令
choco search nginx              # 搜索
choco install nginx             # 安装
choco uninstall nginx           # 卸载
choco upgrade nginx             # 升级
choco upgrade all               # 升级所有
choco list --local-only         # 列出已安装
```

### 8.3 Scoop（轻量级，不需要管理员权限）

```powershell
# 安装 Scoop
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
irm get.scoop.sh | iex

# 常用命令
scoop search nginx              # 搜索
scoop install nginx             # 安装
scoop uninstall nginx           # 卸载
scoop update *                  # 更新所有
scoop list                      # 列出已安装
scoop bucket add extras         # 添加 extras 桶（更多软件）
```

### 8.4 包管理器对比

| 特性 | winget | Chocolatey | Scoop |
|------|--------|-----------|-------|
| 需要管理员 | 部分需要 | 是 | 否 |
| 安装路径 | 程序默认路径 | 程序默认路径 | ~\scoop\ |
| 软件数量 | 多（Microsoft Store + 社区） | 最多 | 较少 |
| 自带 | Win 10 1809+ | 需安装 | 需安装 |

---

## 9. 压缩与解压

```bat
REM CMD（Windows 10+ 自带 tar）
tar -czvf archive.tar.gz folder\          REM 打包为 .tar.gz
tar -xzvf archive.tar.gz                  REM 解压 .tar.gz
tar -xzvf archive.tar.gz -C D:\target\   REM 解压到指定目录

REM compact：NTFS 压缩（透明压缩，不影响使用）
compact /c file.txt                        REM 压缩文件
compact /u file.txt                        REM 解压缩
compact /c /s:folder\                      REM 递归压缩整个目录
```

```powershell
# PowerShell 原生压缩（跨平台通用）
# 压缩为 .zip
Compress-Archive -Path folder\ -DestinationPath archive.zip
Compress-Archive -Path file1.txt,file2.txt -DestinationPath archive.zip

# 解压 .zip
Expand-Archive -Path archive.zip -DestinationPath .\
Expand-Archive -Path archive.zip -DestinationPath D:\target\

# 列出 zip 内容
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::OpenRead("archive.zip").Entries | Select-Object Name, Length

# 7-Zip（如果安装，命令行使用）
7z a archive.7z folder\                    # 压缩
7z x archive.7z                            # 解压
7z l archive.7z                            # 列出内容

# tar（Windows 10+ 自带，支持各种 Linux 格式）
tar -czvf archive.tar.gz folder\           # .tar.gz 压缩
tar -xzvf archive.tar.gz                   # .tar.gz 解压
tar -xzvf archive.tar.gz -C D:\target\    # 指定目录
```

---

## 10. 批处理与 PowerShell 脚本

### 10.1 批处理基础 (.bat/.cmd)

```bat
@echo off
REM 这是注释
REM 第一个脚本: hello.bat

echo Hello World
echo 当前时间: %date% %time%
echo 当前用户: %USERNAME%

REM 运行:
REM hello.bat          -- 直接双击或在 CMD 中输入文件名
```

**变量**

```bat
@echo off
REM 定义变量
set name=zhangsan
set age=25

REM 使用变量
echo 名字: %name%
echo 年龄: %age% 岁

REM 命令结果赋给变量
for /f "tokens=*" %%i in ('date /t') do set today=%%i
echo 今天是 %today%

REM 数学运算（set /a）
set /a result=5+3
echo 5 + 3 = %result%
set /a count=0
set /a count+=1

REM 删除变量
set name=
```

**条件判断**

```bat
@echo off
REM if 语句
set age=20
if %age% gtr 18 (
    echo 成年了
) else if %age% equ 18 (
    echo 刚好 18 岁
) else (
    echo 未成年
)

REM 比较运算符: equ(等于) neq(不等于) gtr(大于) lss(小于) geq(≥) leq(≤)
REM 字符串比较: if "%name%"=="zhangsan" (注意引号!)

REM 文件判断
if exist "C:\Windows\System32\notepad.exe" (
    echo 记事本存在
)

if not exist "config.txt" (
    echo 配置文件不存在
)

REM 检查上一条命令是否成功
if %errorlevel% equ 0 (
    echo 上条命令执行成功
)
```

**循环**

```bat
@echo off
REM for 循环遍历列表
for %%i in (1 2 3 4 5) do (
    echo 第 %%i 次
)

REM 范围循环
for /l %%i in (1,1,10) do echo %%i
REM 格式: for /l %%i in (起始,步长,结束)

REM 遍历文件
for %%f in (*.txt) do (
    echo 处理: %%f
)

REM 遍历目录
for /d %%d in (*) do (
    echo 目录: %%d
)

REM 逐行读取文件
for /f "delims=" %%a in (file.txt) do (
    echo 行内容: %%a
)

REM 递归遍历
for /r . %%f in (*.log) do (
    echo 找到: %%f
)
```

### 10.2 PowerShell 脚本基础 (.ps1)

```powershell
# 第一个脚本: hello.ps1
Write-Host "Hello World"
Write-Host "当前时间: $(Get-Date)"
Write-Host "当前用户: $env:USERNAME"

# 运行:
# ./hello.ps1                         -- 需要执行策略允许
# 或 powershell -ExecutionPolicy Bypass -File hello.ps1
```

**变量**

```powershell
# 定义变量
$name = "zhangsan"
$age = 25

# 使用变量
Write-Host "名字: $name"
Write-Host "年龄: ${age}岁"
Write-Host "名字长度: $($name.Length)"    # 表达式用 $()

# 命令结果赋给变量
$today = Get-Date -Format "yyyy-MM-dd"
$fileCount = (Get-ChildItem | Measure-Object).Count
Write-Host "今天是 $today，当前有 $fileCount 个文件"

# 变量类型
[string]$text = "hello"
[int]$number = 42
[DateTime]$date = Get-Date

# 删除变量
Remove-Variable name
```

**条件判断**

```powershell
$age = 20
if ($age -gt 18) {
    Write-Host "成年了"
} elseif ($age -eq 18) {
    Write-Host "刚好 18 岁"
} else {
    Write-Host "未成年"
}

# 比较运算符: -eq(等于) -ne(不等于) -gt(大于) -lt(小于) -ge(≥) -le(≤)
# 字符串运算符: -eq, -like(通配), -match(正则), -contains(包含)

# 文件判断
if (Test-Path "C:\Windows\notepad.exe") {
    Write-Host "记事本存在"
}

if (Test-Path "config.txt" -PathType Leaf) {
    Write-Host "是文件"
}

if (Test-Path "folder" -PathType Container) {
    Write-Host "是目录"
}

# 逻辑运算
if ($age -gt 18 -and $name -eq "zhangsan") {
    Write-Host "成年且叫 zhangsan"
}
```

**循环**

```powershell
# for 循环
for ($i = 1; $i -le 5; $i++) {
    Write-Host "第 $i 次"
}

# foreach 循环
foreach ($item in 1..10) {
    Write-Host $item
}

# 遍历文件
foreach ($file in Get-ChildItem *.txt) {
    Write-Host "处理: $($file.Name)"
    Write-Host "大小: $($file.Length) 字节"
}

# ForEach-Object（管道循环）
Get-ChildItem *.txt | ForEach-Object {
    Write-Host "处理: $($_.Name)"
}

# while 循环
$count = 1
while ($count -le 5) {
    Write-Host "计数: $count"
    $count++
}

# do-while
do {
    $input = Read-Host "输入 quit 退出"
} while ($input -ne "quit")

# 逐行读取文件
Get-Content file.txt | ForEach-Object {
    Write-Host "行内容: $_"
}
```

**函数**

```powershell
# 定义函数
function Greet {
    param(
        [string]$Name
    )
    Write-Host "你好，$Name！"
}

# 调用
Greet -Name "张三"
Greet "张三"                    # 位置参数也可以

# 带返回值的函数
function Add-Numbers {
    param([int]$a, [int]$b)
    return $a + $b
}

$sum = Add-Numbers 3 5
Write-Host "3 + 5 = $sum"

# 管道输入函数
function Process-File {
    param(
        [Parameter(ValueFromPipeline=$true)]
        [string]$Path
    )
    process {
        $content = Get-Content $Path
        Write-Host "$Path 有 $($content.Count) 行"
    }
}
Get-ChildItem *.txt | Process-File
```

**常用特殊变量**

| 变量 | CMD | PowerShell |
|------|-----|------------|
| 退出码 | `%ERRORLEVEL%` | `$LASTEXITCODE` 或 `$?` |
| 当前目录 | `%cd%` | `$PWD` |
| 脚本路径 | `%~dp0` | `$PSScriptRoot` |
| 参数 | `%1 %2 %3` | `$args[0]` 或 `param()` |
| 参数个数 | — | `$args.Count` |
| 日期时间 | `%date% %time%` | `Get-Date` |

---

## 11. 文本处理

### 11.1 findstr（CMD 版 grep）

```bat
REM CMD - findstr
REM 基础搜索
findstr "error" app.log                REM 搜索包含 error 的行
findstr /i "error" app.log             REM 忽略大小写
findstr /v "debug" app.log             REM 排除包含 debug 的行
findstr /n "error" app.log             REM 显示行号
findstr /c:"exact phrase" app.log      REM 精确匹配（包含空格）

REM 递归搜索
findstr /s /i "TODO" *.txt             REM 当前目录递归搜索
findstr /s /i /m "TODO" *.cs           REM 只显示文件名

REM 正则
findstr /r "[0-9][0-9]*" file.txt     REM 正则匹配数字

REM 常用组合
findstr /n /i /c:"error" app.log      REM 带行号、忽略大小写
find /c "error" app.log               REM 统计匹配行数（find 比 findstr 简单）
```

### 11.2 Select-String（PowerShell 版 grep）

```powershell
# 基础搜索
Select-String "error" app.log                   # 或 sls "error" app.log
Select-String "error" app.log -CaseSensitive    # 区分大小写
Select-String "error" *.log                     # 搜索多个文件

# 高级选项
Get-Content app.log | Select-String "error"     # 管道方式
Select-String "error" app.log | Select-Object LineNumber, Line  # 显示行号和内容
Select-String -NotMatch "debug" app.log         # 排除匹配行

# 上下文
Select-String "error" app.log -Context 3        # 前后各 3 行
Select-String "error" app.log -Context 2,5      # 前 2 行，后 5 行

# 正则
Select-String "\d{4}-\d{2}-\d{2}" app.log     # 查找日期格式

# 递归搜索
Get-ChildItem -Recurse *.log | Select-String "error"
ls -r *.cs | Select-String "TODO"               # 递归搜索代码

# 统计
Select-String "ERROR" app.log | Measure-Object | Select-Object Count
```

### 11.3 其他文本处理

```bat
REM CMD
REM sort：排序
sort file.txt                   REM 升序
sort /r file.txt                REM 降序
sort /+5 file.txt               REM 按第 5 列排序

REM 行数/字数统计
find /c /v "" file.txt          REM 统计行数
```

```powershell
# PowerShell
# sort：排序
Get-Content file.txt | Sort-Object         # 升序
Get-Content file.txt | Sort-Object -Desc   # 降序
Get-Content file.txt | Sort-Object -Unique # 去重排序

# 去重
Get-Content file.txt | Select-Object -Unique
Get-Content file.txt | Group-Object | Where-Object Count -gt 1  # 查重复行

# 分组统计
Get-Content file.txt | Group-Object | Select-Object Count, Name | Sort-Object Count -Desc

# 按列切分（类似 awk/cut）
Get-Content data.csv | ForEach-Object { ($_ -split ',')[0,2] }
Import-Csv data.csv | Select-Object Column1, Column3   # 对 CSV 更友好

# 计算
Get-Content data.txt | ForEach-Object { [int]$_ } | Measure-Object -Sum -Average

# 实战：分析日志
# 统计每个 IP 访问次数
Select-String "(\d+\.\d+\.\d+\.\d+)" access.log -AllMatches |
    ForEach-Object { $_.Matches.Value } |
    Group-Object |
    Sort-Object Count -Desc |
    Select-Object -First 10 Count, Name

# tee：输出到屏幕同时写入文件
./app 2>&1 | Tee-Object app.log

# diff：比较文件
Compare-Object (gc file1.txt) (gc file2.txt)   # 或 diff (gc a) (gc b)
fc file1.txt file2.txt                         # CMD 方式
```

---

## 12. 日志与系统信息

### 12.1 事件查看器（Windows 版系统日志）

```bat
REM CMD - wevtutil（Windows 事件日志）
REM 查看事件日志列表
wevtutil el                     REM 列出所有日志

REM 查询事件
wevtutil qe System /c:10 /f:text   REM 最近 10 条系统事件
wevtutil qe Application /c:10      REM 最近 10 条应用程序事件
wevtutil qe Security /c:10         REM 安全事件（需要管理员）

REM 过滤
wevtutil qe System /q:"*[System[EventID=6006]]" /c:5   REM 特定事件 ID
wevtutil qe System /q:"*[System[(Level=2)]]" /c:10     REM 错误级别
```

```powershell
# PowerShell - 事件日志（更友好）
Get-EventLog -LogName System -Newest 10        # 最近 10 条系统日志
Get-EventLog -LogName Application -Newest 10   # 应用程序日志
Get-EventLog -LogName Security -Newest 10      # 安全日志（需管理员）

# 新版方式（Windows 7+）
Get-WinEvent -LogName System -MaxEvents 10
Get-WinEvent -FilterHashtable @{LogName='System'; Level=2; StartTime=(Get-Date).AddHours(-1)}  # 最近 1 小时的错误

# 日志来源
Get-WinEvent -LogName System | Group-Object ProviderName | Sort-Object Count -Desc
```

### 12.2 系统信息

```bat
REM CMD
REM 系统概览
systeminfo                     REM 系统完整信息
systeminfo | findstr /i "OS"  REM 只看系统版本
systeminfo | findstr /i "Memory"  REM 只看内存

REM winver：Windows 版本弹窗
winver                         REM 图形弹窗

REM 主机名
hostname                       REM 计算机名

REM 驱动信息
driverquery                    REM 列出所有驱动
driverquery /v                 REM 详细信息
```

```powershell
# PowerShell
# 系统信息
Get-ComputerInfo               # 系统信息总览（Windows 10+）
Get-ComputerInfo | Select-Object OsName, OsVersion, CsTotalPhysicalMemory, CsProcessors

# 版本
[System.Environment]::OSVersion.VersionString

# 硬件信息
Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores       # CPU
Get-CimInstance Win32_PhysicalMemory | Select-Object Capacity, Speed      # 内存
Get-CimInstance Win32_LogicalDisk | Select-Object DeviceID, Size, FreeSpace  # 硬盘
Get-CimInstance Win32_BIOS | Select-Object Manufacturer, SMBIOSBIOSVersion   # BIOS

# 显卡
Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion

# 系统启动时间
(Get-CimInstance Win32_OperatingSystem).LastBootUpTime
Get-CimInstance Win32_OperatingSystem | Select-Object LastBootUpTime

# 设备管理器相关
Get-PnpDevice | Where-Object Status -eq "Error"   # 有问题的设备
```

### 12.3 服务状态（续 5.3）

```powershell
# 快速检查关键服务
$services = @("W3SVC", "MSSQLSERVER", "Spooler")
foreach ($svc in $services) {
    $status = Get-Service $svc -ErrorAction SilentlyContinue
    if ($status) {
        "$svc : $($status.Status)"
    } else {
        "$svc : 未安装"
    }
}
```

---

## 13. 定时任务

### 13.1 schtasks（任务计划程序）

```bat
REM CMD - schtasks
REM 查看任务
schtasks /query                          REM 查看所有定时任务
schtasks /query /fo list /v             REM 详细信息
schtasks /query /tn "MyTask"             REM 查看特定任务

REM 创建任务
REM 每天凌晨 2:30 执行
schtasks /create /tn "BackupTask" /tr "C:\backup\backup.bat" /sc daily /st 02:30

REM 每 5 分钟执行
schtasks /create /tn "CheckTask" /tr "python C:\scripts\check.py" /sc minute /mo 5

REM 每小时执行
schtasks /create /tn "HourlyTask" /tr "C:\scripts\run.bat" /sc hourly

REM 工作日早上 9 点
schtasks /create /tn "WeekdayTask" /tr "C:\scripts\run.bat" /sc weekly /d mon,tue,wed,thu,fri /st 09:00

REM 开机时运行
schtasks /create /tn "StartupTask" /tr "C:\scripts\run.bat" /sc onstart

REM 用户登录时运行
schtasks /create /tn "LogonTask" /tr "C:\scripts\run.bat" /sc onlogon

REM 删除任务
schtasks /delete /tn "MyTask" /f         REM /f 不确认

REM 运行/结束任务
schtasks /run /tn "MyTask"
schtasks /end /tn "MyTask"

REM 禁用/启用
schtasks /change /tn "MyTask" /disable
schtasks /change /tn "MyTask" /enable
```

```powershell
# PowerShell 定时任务（ScheduledJob）
# 创建任务
$trigger = New-JobTrigger -Daily -At "02:30"
Register-ScheduledJob -Name "BackupJob" -FilePath "C:\backup\backup.ps1" -Trigger $trigger

# 查看
Get-ScheduledJob

# 删除
Unregister-ScheduledJob -Name "BackupJob"

# 也可以直接调用 schtasks（更灵活）
schtasks /create /tn "PS_Task" /tr "powershell.exe -File C:\scripts\script.ps1" /sc daily /st 02:30
```

**定时任务格式速查：**
```
/sc daily         每天
/sc weekly        每周
/sc monthly       每月
/sc minute /mo 5  每 5 分钟
/sc hourly        每小时
/sc onstart       开机
/sc onlogon       登录时
/st 02:30         时间
```

---

## 14. 远程连接

### 14.1 远程桌面 (RDP)

```bat
REM 启动远程桌面连接
mstsc                          REM 打开远程桌面（图形界面）
mstsc /v:10.0.0.1              REM 直接连接指定 IP
mstsc /admin                   REM 管理员模式（控制台会话）

REM 远程桌面设置
sysdm.cpl                      REM 打开系统属性 → 远程设置
```

### 14.2 SSH（Windows 10+ 自带 OpenSSH）

```bat
REM CMD - SSH 连接（与 Linux 完全一样）
ssh user@10.0.0.1              REM 默认端口 22
ssh -p 2222 user@10.0.0.1     REM 指定端口

REM 免密登录
ssh-keygen -t rsa -b 4096     REM 生成密钥（在 %USERPROFILE%\.ssh\）
type %USERPROFILE%\.ssh\id_rsa.pub | ssh user@10.0.0.1 "cat >> ~/.ssh/authorized_keys"

REM 或使用 ssh-copy-id（如果安装了）
ssh-copy-id user@10.0.0.1

REM SSH 配置文件
REM %USERPROFILE%\.ssh\config（与 Linux 格式完全一样）
REM 参考 linux-guide.md 第 14.2 节
```

### 14.3 WinRM / PowerShell Remoting

```powershell
# PowerShell Remoting（Windows 原生远程管理）
# 启用 WinRM（需要管理员）
Enable-PSRemoting -Force

# 交互式远程会话
Enter-PSSession -ComputerName remote-pc          # 进入远程会话
Enter-PSSession -ComputerName 10.0.0.1 -Credential domain\user

# 执行单条命令
Invoke-Command -ComputerName remote-pc -ScriptBlock { Get-Service }
Invoke-Command -ComputerName server1,server2 -ScriptBlock { hostname }

# 远程复制文件
$session = New-PSSession -ComputerName remote-pc
Copy-Item -Path .\file.txt -Destination C:\Temp\ -ToSession $session
Copy-Item -Path C:\Temp\remote.txt -Destination .\ -FromSession $session

# 断开连接
Exit-PSSession                   # 退出交互会话
Get-PSSession | Remove-PSSession # 清理会话
```

### 14.4 远程工具对比

| 功能 | 工具 | 说明 |
|------|------|------|
| 图形远程桌面 | mstsc (RDP) | Windows 原生，体验最好 |
| 命令行远程 | SSH | Win 10+ 自带，与 Linux 互通 |
| PowerShell 远程 | WinRM | Windows 原生，自动化管理 |
| 远程协助 | msra | Windows 远程协助 |
| 第三方 | VNC / TeamViewer | 跨平台 |

---

## 15. 实用技巧汇总

### 15.1 重定向与管道

```bat
REM CMD 重定向
command > file.txt             REM 覆盖写入（标准输出）
command >> file.txt            REM 追加写入（标准输出）
command 2> error.txt           REM 错误输出写入文件
command > file.txt 2>&1        REM 标准输出和错误都写入文件
command > nul 2>&1             REM 丢弃所有输出

REM 管道 |：把一个命令的输出作为下一个命令的输入
type app.log | findstr ERROR
tasklist | findstr chrome
```

```powershell
# PowerShell 重定向（兼容 CMD 语法，还支持更多）
command > file.txt
command >> file.txt
command 2> error.txt
command *> all.txt             # 所有流（比 CMD 的 2>&1 更彻底）

# 管道（传递对象而非文本！这是 PowerShell 的核心优势）
Get-Process | Where-Object { $_.CPU -gt 10 } | Sort-Object CPU -Desc

# 管道到文件
Get-Process | Out-File processes.txt
Get-Process | Export-Csv processes.csv
Get-Process | ConvertTo-Json | Out-File processes.json
```

### 15.2 快捷键速查

| 快捷键 | CMD | PowerShell | 作用 |
|--------|-----|------------|------|
| `Ctrl+C` | 是 | 是 | 终止当前命令 |
| `Ctrl+V` | 是 | 是 | 粘贴（Win 10+ CMD 支持） |
| `Tab` | 是 | 是 | 自动补全文件名/命令 |
| `F7` | 是 | 是 | 命令历史列表 |
| `F1` | 是 | — | 逐字符复制上一条命令 |
| `F3` | 是 | — | 复制上一条命令 |
| `↑/↓` | 是 | 是 | 浏览历史命令 |
| `Ctrl+←/→` | — | 是 | 按单词跳转 |
| `Ctrl+Home/End` | — | 是 | 跳到行首/行尾 |
| `Esc` | 是 | 是 | 清除当前行 |
| `Alt+Space → E → P` | 是 | — | CMD 粘贴（传统方式） |
| `Ctrl+Shift+Enter` | — | — | 以管理员身份运行程序 |

### 15.3 环境变量设置

```bat
REM CMD - 临时设置（当前终端）
set MY_VAR=hello
echo %MY_VAR%

REM 永久设置（用户级别）
setx MY_VAR "hello"
REM 永久设置（系统级别，需管理员）
setx MY_VAR "hello" /m

REM 添加到 PATH
setx PATH "%PATH%;C:\MyTools"
```

```powershell
# PowerShell - 临时设置
$env:MY_VAR = "hello"

# 永久设置（用户级别）
[System.Environment]::SetEnvironmentVariable("MY_VAR", "hello", "User")

# 永久设置（系统级别，需管理员）
[System.Environment]::SetEnvironmentVariable("MY_VAR", "hello", "Machine")

# 添加到 PATH
$oldPath = [System.Environment]::GetEnvironmentVariable("PATH", "User")
[System.Environment]::SetEnvironmentVariable("PATH", "$oldPath;C:\MyTools", "User")
```

### 15.4 注册表操作

```bat
REM CMD - reg 命令
REM 查询
reg query HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion" /v ProductName

REM 添加/修改
reg add HKCU\Software\MyApp /v Setting /t REG_SZ /d "value" /f

REM 删除
reg delete HKCU\Software\MyApp /v Setting /f
reg delete HKCU\Software\MyApp /f   REM 删除整个键

REM 导出/导入
reg export HKCU\Software\MyApp backup.reg
reg import backup.reg
```

```powershell
# PowerShell 注册表（像文件系统一样操作）
cd HKCU:\Software
Get-ChildItem                    # 浏览注册表
Get-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer"
Set-ItemProperty "HKCU:\Software\MyApp" -Name Setting -Value "value"
Remove-ItemProperty "HKCU:\Software\MyApp" -Name Setting
```

### 15.5 Winget 必装软件推荐

```bat
REM 开发工具
winget install Git.Git
winget install Microsoft.VisualStudioCode
winget install Microsoft.WindowsTerminal
winget install Microsoft.PowerShell

REM 编程语言
winget install Python.Python.3.12
winget install OpenJS.NodeJS
winget install Oracle.JDK.21

REM 工具软件
winget install 7zip.7zip
winget install Notepad++.Notepad++
winget install Microsoft.Sysinternals.ProcessExplorer

REM 网络
winget install Microsoft.PowerToys
winget install WireGuard.WireGuard

REM 数据库客户端
winget install DBeaver.DBeaver
```

### 15.6 一行命令技巧

```bat
REM CMD
REM 批量重命名（加前缀）
for %f in (*.txt) do ren "%f" "backup_%f"

REM 批量删除 7 天前的日志
forfiles /p "C:\logs" /s /m *.log /d -7 /c "cmd /c del @file"

REM 查看占用端口最多的进程
netstat -ano | findstr LISTENING

REM 快速备份文件
copy config.conf config.conf.bak

REM 查看外网 IP
curl ifconfig.me
```

```powershell
# PowerShell
# 批量重命名（加前缀）
Get-ChildItem *.txt | Rename-Item -NewName { "backup_" + $_.Name }

# 批量重命名（替换文本）
Get-ChildItem *.txt | Rename-Item -NewName { $_.Name -replace 'old','new' }

# 批量删除 7 天前的文件
Get-ChildItem C:\logs\*.log -Recurse |
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-7) } |
    Remove-Item

# 统计代码行数
ls -r *.cs,*.js,*.py | gc | Measure-Object -Line

# 最耗 CPU 的进程
Get-Process | Sort-Object CPU -Desc | Select-Object -First 10 Name, CPU

# 最耗内存的进程
Get-Process | Sort-Object WS -Desc | Select-Object -First 10 Name, @{N="MB";E={$_.WS/1MB}}

# 查看外网 IP
Invoke-RestMethod ifconfig.me
```

### 15.7 新手常见问题

| 问题 | 解决 |
|------|------|
| 'xxx' 不是内部或外部命令 | 没装此软件，或 PATH 没配置 |
| 拒绝访问 / Access denied | 需要管理员权限，右键"以管理员身份运行" |
| 无法加载文件 xxx.ps1（执行策略） | `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| 系统找不到指定的文件 | 路径写错了，用 `dir` 和 `cd` 确认 |
| 端口被占用 | `netstat -ano \| findstr 端口号`，然后 `taskkill /pid xxx` |
| 文件被锁定无法删除 | 关闭使用该文件的程序，或重启 |
| 中文乱码 | CMD 用 `chcp 65001` 切换到 UTF-8 |
| 远程桌面连不上 | 检查防火墙 3389 端口、远程桌面是否启用 |
| 系统卡顿 | 任务管理器查 CPU/内存/磁盘，`resmon` 看资源监视器 |

---

## Windows 与 Linux 命令对照表

| 功能 | CMD | PowerShell | Linux |
|------|-----|------------|-------|
| 列出文件 | dir | ls / Get-ChildItem | ls |
| 当前目录 | cd / echo %cd% | pwd / Get-Location | pwd |
| 切换目录 | cd / chdir | cd / Set-Location | cd |
| 创建目录 | mkdir / md | mkdir / New-Item -Type Directory | mkdir |
| 删除文件 | del | rm / Remove-Item | rm |
| 删除目录 | rmdir / rd | rm -r / Remove-Item -Recurse | rm -r |
| 复制 | copy / xcopy | cp / Copy-Item | cp |
| 移动/重命名 | move / ren | mv / Move-Item | mv |
| 查看文件内容 | type | cat / Get-Content | cat |
| 分页查看 | more | more / Out-Host -Paging | less |
| 查看末尾 | — | gc -Tail / Get-Content -Tail | tail |
| 实时追踪 | — | gc -Wait | tail -f |
| 搜索文本 | findstr | sls / Select-String | grep |
| 查找文件 | where / dir /s | ls -r / Get-ChildItem -Recurse | find |
| 查找命令路径 | where | gcm / Get-Command | which |
| 查进程 | tasklist | ps / Get-Process | ps |
| 杀进程 | taskkill | kill / Stop-Process | kill |
| 服务管理 | sc / net start | Get-Service / Start-Service | systemctl |
| 查看 IP | ipconfig | Get-NetIPAddress | ip a / ifconfig |
| 网络统计 | netstat | Get-NetTCPConnection | netstat / ss |
| DNS 查询 | nslookup | Resolve-DnsName | nslookup / dig |
| 路由追踪 | tracert | Test-Connection -Traceroute | traceroute |
| 下载文件 | curl | Invoke-WebRequest | curl / wget |
| SSH | ssh | ssh | ssh |
| 远程桌面 | mstsc | — | — |
| 磁盘使用 | wmic / fsutil | Get-PSDrive / Get-Volume | df -h |
| 内存查看 | systeminfo | Get-CimInstance | free -h |
| 系统信息 | systeminfo | Get-ComputerInfo | uname / cat /proc/ |
| 防火墙 | netsh advfirewall | Get-NetFirewallRule | iptables / ufw |
| 包管理 | winget | winget / choco / scoop | apt / yum / brew |
| 压缩/解压 | tar | Compress-Archive / Expand-Archive | tar / zip / unzip |
| 定时任务 | schtasks | Register-ScheduledJob | crontab |
| 环境变量 | set | $env: / Get-ChildItem Env: | env / export |
| 清屏 | cls | cls / Clear-Host | clear |
| 帮助 | help / ? | Get-Help | man / --help |
| 历史命令 | doskey /history | Get-History / h | history |
| 退出 | exit | exit | exit |

---

> **最好的学习方法是多用。CMD 中加 `/?` 查看帮助（如 `dir /?`），PowerShell 中用 `Get-Help`（如 `Get-Help Get-Process`）或 `Get-Command` 查找命令。**
