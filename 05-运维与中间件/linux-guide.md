# Linux 速查手册

> 一份通俗易懂的 Linux 文档，涵盖日常开发和运维中最常用的命令和概念，适合快速查阅和上手。

---

## 目录

- [1. 基础概念](#1-基础概念)
- [2. 文件与目录操作](#2-文件与目录操作)
- [3. 文件内容查看与编辑](#3-文件内容查看与编辑)
- [4. 用户与权限](#4-用户与权限)
- [5. 进程管理](#5-进程管理)
- [6. 磁盘与内存](#6-磁盘与内存)
- [7. 网络操作](#7-网络操作)
- [8. 软件安装与包管理](#8-软件安装与包管理)
- [9. 压缩与解压](#9-压缩与解压)
- [10. Shell 脚本基础](#10-shell-脚本基础)
- [11. 文本处理三剑客](#11-文本处理三剑客)
- [12. 日志与系统信息](#12-日志与系统信息)
- [13. 定时任务](#13-定时任务)
- [14. SSH 远程连接](#14-ssh-远程连接)
- [15. 实用技巧汇总](#15-实用技巧汇总)

---

## 1. 基础概念

### 1.1 什么是 Linux？

Linux 是一个**开源操作系统内核**，我们通常说的 Linux 指的是基于这个内核的发行版（如 Ubuntu、CentOS）。它用命令行操作，是服务器端的事实标准。

### 1.2 核心术语

| 术语 | 说明 | 类比 |
|------|------|------|
| Shell | 命令行解释器，你和系统的翻译官 | Windows 的 cmd/PowerShell |
| Bash | 最常用的 Shell | "普通话" |
| 终端 Terminal | 输入命令的窗口 | 对话框 |
| 内核 Kernel | 操作系统核心，管硬件 | 发动机 |
| 发行版 Distro | Ubuntu、CentOS、Debian 等 | 不同品牌的汽车 |
| root | 超级管理员账户 | Administrator |
| / | 根目录，一切文件的起点 | C:\ |
| ~ | 当前用户的家目录 | C:\Users\你的用户名 |

### 1.3 目录结构速览

```
/              # 根目录，一切从这里开始
├── /bin       # 基础命令（ls, cp, cat 等）
├── /boot      # 启动文件
├── /dev       # 设备文件（硬盘、U盘等）
├── /etc       # 配置文件（系统设置都在这里）
├── /home      # 普通用户的家目录 /home/用户名
├── /opt       # 第三方软件安装目录
├── /proc      # 进程和系统信息（虚拟文件系统）
├── /root      # root 用户的家目录
├── /tmp       # 临时文件（重启可能清空）
├── /usr       # 用户软件（大部分软件装这里）
├── /var       # 日志、缓存等可变数据
│   ├── /var/log    # 日志文件（重点！排查问题必看）
│   └── /var/lib    # 数据库等运行时数据
└── /mnt       # 临时挂载点
```

---

## 2. 文件与目录操作

### 2.1 导航

```bash
# 当前目录
pwd                              # /home/zhangsan

# 切换目录
cd /home                         # 绝对路径
cd ..                            # 返回上一级
cd -                             # 返回上次的目录（超实用！）
cd ~                             # 回到家目录
cd                               # 也是回到家目录

# 列出目录内容
ls                               # 列出文件
ls -l                            # 详细信息（权限、大小、时间）
ls -la                           # 包括隐藏文件（.开头的文件）
ls -lh                           # 人类可读的大小（1K, 234M）
ls -lrt                          # 按时间排序，最新的在最后
ls -lS                           # 按大小排序
```

### 2.2 创建与删除

```bash
# 创建目录
mkdir project                    # 创建一个
mkdir -p a/b/c/d                 # 递归创建多层目录

# 创建文件
touch file.txt                   # 创建空文件（或更新文件时间）
touch file{1,2,3}.txt            # 批量创建 file1.txt file2.txt file3.txt

# 删除（小心！Linux 没有回收站）
rm file.txt                      # 删除文件
rm -r folder/                    # 递归删除目录
rm -rf folder/                   # 强制删除，不提示（⚠️ 危险！）
rm -i *.txt                      # 删除前逐个确认

# 🔥 最危险的命令，千万别执行：
# rm -rf /                       # 删除整个系统！
# rm -rf / home/user             # 注意这个空格！会删根目录！
```

### 2.3 复制与移动

```bash
# 复制
cp source.txt dest.txt           # 复制文件
cp -r source_dir/ dest_dir/      # 复制目录（-r 递归）
cp -p source.txt dest.txt        # 保留属性（权限、时间）
cp -a source_dir/ dest_dir/      # 归档复制（保留一切）

# 移动/重命名
mv old.txt new.txt               # 重命名
mv file.txt /tmp/                # 移动文件
mv dir1/ dir2/                   # dir2 存在则移入，不存在则重命名
```

### 2.4 查找

```bash
# find：按文件名、时间、大小等查找（功能强大，速度稍慢）
find . -name "*.log"             # 当前目录下找 .log 文件
find / -name "nginx.conf"        # 全盘搜索（慢）
find . -type d -name "log"       # 找目录
find . -type f -size +100M       # 找大于 100M 的文件
find . -mtime -7                 # 最近 7 天修改的文件
find . -name "*.tmp" -delete     # 找到并删除（一句话搞定）
find . -name "*.log" -exec gzip {} \;  # 找到并压缩

# locate：从数据库查，速度快但可能不实时
locate nginx.conf
updatedb                         # 更新 locate 数据库（macOS 不需要）

# which：找命令的位置
which python3                    # /usr/bin/python3

# whereis：找命令的二进制、源码、手册
whereis nginx
```

### 2.5 文件信息

```bash
# 文件类型
file unknown.bin                 # 告诉你这是什么文件

# 文件大小
ls -lh file.txt                  # 单个文件
du -sh folder/                   # 目录总大小
du -h --max-depth=1 /var         # 一层子目录各占多少
du -sh *                         # 当前目录下每个文件/目录的大小

# 文件统计
wc file.txt                      # 行数、单词数、字节数
wc -l file.txt                   # 只看行数（最常用）
```

---

## 3. 文件内容查看与编辑

### 3.1 查看命令对比

| 命令 | 特点 | 适用场景 |
|------|------|---------|
| cat | 全量输出 | 小文件 |
| less | 分页浏览，上下翻 | 大文件，查日志首选 |
| head | 只看前 N 行 | 看文件开头 |
| tail | 只看后 N 行 | 查最新日志 |
| nl | 带行号输出 | 看代码 |

```bash
# cat：全量输出
cat file.txt                     # 显示全部内容
cat -n file.txt                  # 带行号

# less：分页浏览（最推荐看大文件）
less huge.log
# 操作：空格=下一页, b=上一页, /关键词=搜索, n=下一个匹配, q=退出

# head：看开头
head -20 file.txt                # 前 20 行
head -n 20 file.txt              # 同上

# tail：看末尾（查日志必备）
tail -20 app.log                 # 最后 20 行
tail -f app.log                  # 🔥 实时追踪日志（ctrl+c 退出）
tail -f -n 100 app.log           # 追踪，但先显示最后 100 行
tail -f *.log                    # 同时追踪多个文件

# 取中间某几行
sed -n '10,20p' file.txt         # 第 10 到 20 行
awk 'NR>=10 && NR<=20' file.txt  # 同上
```

### 3.2 文本编辑器速成

```bash
# vim（最常用，服务器上一定有）
vim file.txt
# 三种模式：
#   i       → 插入模式（开始编辑）
#   Esc     → 命令模式
#   :       → 底行模式（输入命令）
#
# 必备命令（在命令模式下，按 : 进入底行）：
#   :w      保存
#   :q      退出
#   :wq     保存并退出
#   :q!     强制退出不保存
#   /关键词  搜索
#   dd      删除当前行
#   u       撤销
#   gg      跳到开头
#   G       跳到末尾

# nano（更简单友好的编辑器）
nano file.txt
# Ctrl+O 保存, Ctrl+X 退出, 底部有提示

# vim 紧急逃生指南：
# 1. 先按 Esc
# 2. 输入 :q! 回车 → 强制退出
```

---

## 4. 用户与权限

### 4.1 权限体系

Linux 权限是三组三位：**所有者 - 所属组 - 其他人**，每组有**读(r)写(w)执行(x)**。

```
-rwxr-xr--  1 zhangsan  devteam  4096 Jan 01 12:00 script.sh
 └┬┘└┬┘└┬┘      │         │
  所有者 组  其他人  所有者     所属组

r = read  = 4（读）
w = write = 2（写）
x = exec  = 1（执行）

rwx = 4+2+1 = 7（读写执行）
rw- = 4+2   = 6（读写）
r-- = 4     = 4（只读）
```

### 4.2 chmod 修改权限

```bash
# 数字方式（最常用）
chmod 755 script.sh              # rwxr-xr-x（所有者全权限，别人只能读和执行）
chmod 644 file.txt               # rw-r--r--（文件标配权限）
chmod 600 secret.key             # rw-------（只有自己能读写，私钥文件用）
chmod 777 public.sh              # rwxrwxrwx（⚠️ 所有人随便改，不安全！）
chmod -R 755 project/            # 递归修改目录下所有文件

# 符号方式
chmod u+x script.sh              # 给所有者(u)加执行权限(+x)
chmod g-w file.txt               # 去掉组(g)的写权限(-w)
chmod o-rwx file.txt             # 去掉其他人(o)的所有权限
chmod a+x script.sh              # 给所有人(a)加执行权限
```

**常用权限速记：**
- `755`：目录 / 可执行脚本
- `644`：普通文件
- `600`：私密文件（密钥、配置）
- `777`：永远不要用

### 4.3 chown 修改归属

```bash
chown zhangsan file.txt                  # 改所有者
chown zhangsan:devteam file.txt          # 改所有者和组
chown -R zhangsan:devteam project/       # 递归修改整个目录
```

### 4.4 用户管理

```bash
# 用户
whoami                           # 我是谁
id                               # 我的 UID、GID
who                              # 当前谁在登录
w                                # 谁在登录，在干嘛
last                             # 最近的登录记录

# 切换用户
su - username                    # 切换到某用户（- 表示加载该用户环境）
sudo command                     # 以 root 身份执行一条命令
sudo -i                          # 变成 root（sudo su）
sudo su - username               # 变成某用户

# 创建用户
useradd -m -s /bin/bash newuser  # 创建用户（-m 创建家目录）
passwd newuser                   # 设置密码

# 把用户加入 sudo 组（让他能用 sudo）
usermod -aG sudo newuser         # Ubuntu/Debian
usermod -aG wheel newuser        # CentOS/RHEL
```

---

## 5. 进程管理

### 5.1 查看进程

```bash
# ps：当前快照
ps aux                           # 显示所有进程（最常用）
ps aux | grep nginx              # 查找 nginx 进程
ps -ef | grep java               # 另一种格式

# 字段含义：
# PID     进程 ID
# %CPU    CPU 使用率
# %MEM    内存使用率
# VSZ     虚拟内存
# RSS     物理内存
# STAT    进程状态（S=休眠, R=运行, Z=僵尸）
# TIME    累计 CPU 时间
# COMMAND 启动命令

# top：实时动态监控（类似任务管理器）
top
# 快捷键：q=退出, 1=看每个CPU, M=按内存排序, P=按CPU排序, k=杀进程

# htop：更友好的 top（需要安装）
htop

# 查进程树
pstree -p
```

### 5.2 终止进程

```bash
# kill：发信号给进程
kill PID                         # 优雅终止（SIGTERM，给程序清理的机会）
kill -9 PID                      # 强制杀（SIGKILL，立刻干掉，无法拦截）
kill -15 PID                     # 等同于默认的 kill

# 按名称杀
killall java                     # 杀所有 java 进程
pkill -f "python app.py"         # 按命令行匹配杀

# 经典组合：找到并杀掉
ps aux | grep nginx | grep -v grep | awk '{print $2}' | xargs kill -9
# 或更简单的：
pkill -f nginx
```

### 5.3 后台运行

```bash
# 后台启动
./app &                          # 启动到后台（关终端会停）
nohup ./app &                    # 关终端也不停，输出到 nohup.out
nohup ./app > app.log 2>&1 &    # 指定日志文件

# 查看后台任务
jobs                             # 当前终端后台任务

# 前后台切换
bg 1                             # 编号为 1 的任务放到后台
fg 1                             # 编号为 1 的任务放回前台
Ctrl+Z                           # 暂停当前前台任务

# screen / tmux（持久会话，更推荐）
screen -S mysession              # 创建新会话
screen -r mysession              # 重新连接到会话
Ctrl+A D                         # 从会话中脱离（screen）
# screen 内按 Ctrl+A 再按 D

# tmux（更现代）
tmux new -s mysession            # 创建会话
tmux attach -t mysession         # 重新连接
Ctrl+B D                         # 脱离（tmux）
```

---

## 6. 磁盘与内存

### 6.1 磁盘

```bash
# 查看磁盘使用情况
df -h                            # 磁盘分区使用率（最常用）

# 查看目录占用
du -sh /var/log                  # 这个目录多大
du -h --max-depth=1 /            # 根目录下各文件夹大小

# 找到大文件
find / -type f -size +1G 2>/dev/null   # 找大于 1G 的文件
du -ah / | sort -rh | head -20         # 当前最大的 20 个文件/目录

# 挂载
mount                            # 查看挂载情况
lsblk                            # 查看磁盘和分区（树形结构）
fdisk -l                         # 查看所有磁盘信息
```

### 6.2 内存

```bash
# 查看内存
free -h                          # 内存使用概况
#               total   used   free   shared   buff/cache   available
# Mem:           7.6G    2.1G   1.2G    234M        4.3G        5.0G
# Swap:          2.0G     0B    2.0G

# 关注 available 列，这才是"真正可用"的内存
# buff/cache 是系统缓存，需要时可以被回收

cat /proc/meminfo                # 详细内存信息
vmstat 1                         # 每秒刷新内存/CPU/IO
top -o %MEM                      # 按内存使用排序
```

---

## 7. 网络操作

### 7.1 网络诊断

```bash
# 查看 IP
ip a                             # 新方式（推荐）
ifconfig                         # 旧方式（可能需要装 net-tools）

# 查看路由
ip route                         # 默认网关等信息

# 连通性测试
ping -c 4 google.com             # 发 4 个包测试
ping -c 4 10.0.0.1               # 测试内网连通

# DNS 解析
nslookup google.com              # 查询 DNS
dig google.com                   # 更详细的 DNS 信息
dig +short google.com            # 只显示结果

# 路由追踪
traceroute google.com            # 看经过哪些节点
mtr google.com                   # 动态路由追踪（更好用）
```

### 7.2 端口与连接

```bash
# 端口监听
netstat -tlnp                    # 查看监听的 TCP 端口
# -t: TCP, -l: 监听, -n: 数字显示, -p: 显示进程名
netstat -tlnp | grep 8080        # 8080 端口是谁在用

ss -tlnp                         # 更现代的替代（速度更快）

# 查看所有连接
netstat -an                      # 所有连接（包括已建立的）
ss -s                            # 连接统计摘要

# 检查远程端口是否开放
nc -zv 10.0.0.1 3306             # 测试端口是否通
telnet 10.0.0.1 3306             # 同上

# 防火墙（iptables/firewalld）
iptables -L                      # 查看防火墙规则
firewall-cmd --list-all          # CentOS 7+ firewalld
ufw status                       # Ubuntu 防火墙
```

### 7.3 下载文件

```bash
# curl：发送 HTTP 请求（API 调试神器）
curl http://example.com                  # GET 请求
curl -I https://example.com              # 只看响应头
curl -X POST -d '{"name":"zhang"}' \
     -H "Content-Type: application/json" \
     https://api.example.com/users      # POST JSON

curl -o file.tar.gz https://example.com/file.tar.gz   # 下载文件
curl -O https://example.com/file.tar.gz               # 按原名保存

# wget：下载文件
wget https://example.com/file.tar.gz     # 下载
wget -c https://example.com/large.zip    # 断点续传
```

### 7.4 文件传输

```bash
# scp：远程拷贝（基于 SSH）
scp file.txt user@10.0.0.1:/home/user/          # 本地上传
scp user@10.0.0.1:/home/user/file.txt ./        # 远程下载
scp -r folder/ user@10.0.0.1:/home/user/        # 传目录

# rsync：同步（更智能，只传差异）
rsync -avz ./local/ user@10.0.0.1:/remote/       # 同步到远程
rsync -avz user@10.0.0.1:/remote/ ./local/       # 同步到本地
# -a: 归档模式, -v: 显示详情, -z: 压缩传输
```

---

## 8. 软件安装与包管理

### 8.1 各发行版包管理器

```bash
# Debian/Ubuntu (apt)
sudo apt update                              # 更新软件源
sudo apt upgrade                             # 升级所有软件
sudo apt install nginx                       # 安装
sudo apt remove nginx                        # 卸载（保留配置）
sudo apt purge nginx                         # 彻底卸载（删配置）
apt search nginx                             # 搜索
apt list --installed                         # 已安装列表
sudo apt autoremove                          # 清理无用依赖

# CentOS/RHEL (yum/dnf)
sudo yum update                              # RHEL 7 / CentOS 7
sudo dnf update                              # RHEL 8+ / Fedora
sudo yum install nginx
sudo dnf install nginx
sudo yum remove nginx

# Alpine (apk)
apk add nginx                                # 安装
apk del nginx                                # 卸载
apk update && apk upgrade                    # 更新所有
```

### 8.2 源码编译安装

```bash
# 三步走经典流程
./configure --prefix=/usr/local/myapp    # 配置（指定安装路径）
make                                      # 编译
sudo make install                         # 安装

# 卸载
sudo make uninstall
```

---

## 9. 压缩与解压

```bash
# tar 🏆 最常用
tar -cvf archive.tar folder/          # 打包（不压缩）
tar -czvf archive.tar.gz folder/      # 打包+压缩为 .tar.gz（gzip）
tar -czvf archive.tar.gz file1 file2  # 打包多个文件
tar -xvf  archive.tar                 # 解包
tar -xzvf archive.tar.gz              # 解压 .tar.gz
tar -xzvf archive.tar.gz -C /opt/     # 解压到指定目录

# 记忆技巧：c=create创建, x=extract解, z=gzip, v=verbose过程, f=file文件

# .tar.bz2（bzip2，压缩率高但慢）
tar -cjvf archive.tar.bz2 folder/     # 压缩
tar -xjvf archive.tar.bz2             # 解压

# .tar.xz（xz，压缩率最高）
tar -cJvf archive.tar.xz folder/      # 压缩
tar -xJvf archive.tar.xz              # 解压

# .zip（跨平台通用）
zip -r archive.zip folder/            # 压缩
unzip archive.zip                     # 解压
unzip -l archive.zip                  # 列出内容不解压

# .gz（单个文件）
gzip file                             # 压缩 -> file.gz
gunzip file.gz                        # 解压
# 或
gzip -d file.gz                       # 同上

# 查看压缩包内容（不解压）
tar -tzvf archive.tar.gz              # 列出内容
zcat file.gz                          # 看 .gz 内容
zless file.gz                         # 分页看 .gz 内容
```

---

## 10. Shell 脚本基础

### 10.1 第一个脚本

```bash
#!/bin/bash
# 这个叫 shebang，告诉系统用哪个解释器
# 文件名: hello.sh

echo "Hello World"
echo "当前时间: $(date)"
echo "当前用户: $USER"

# 运行:
# chmod +x hello.sh   # 加执行权限
# ./hello.sh          # 运行
# 或 bash hello.sh    # 直接用 bash 运行
```

### 10.2 变量

```bash
#!/bin/bash

# 定义变量（= 两边不能有空格！）
name="zhangsan"
age=25

# 使用变量
echo "名字: $name"
echo "年龄: ${age}岁"      # {} 可加可不加，加了好
echo "名字: ${name}san"    # 必须加，区分边界

# 命令结果赋给变量
today=$(date +%Y-%m-%d)
files_count=$(ls | wc -l)
echo "今天是 $today，当前有 $files_count 个文件"

# 只读变量
readonly PI=3.14159

# 删除变量
unset name
```

### 10.3 条件判断

```bash
#!/bin/bash

# if 语句
age=20
if [ $age -gt 18 ]; then
    echo "成年了"
elif [ $age -eq 18 ]; then
    echo "刚好 18 岁"
else
    echo "未成年"
fi

# 常用判断条件（注意 [ ] 里必须有空格！）
# 数字比较: -eq(等于) -ne(不等于) -gt(大于) -lt(小于) -ge(大于等于) -le(小于等于)
# 字符串:   =(等于) !=(不等于) -z(长度为0) -n(长度非0)
# 文件:     -f(是文件) -d(是目录) -e(存在) -r(可读) -w(可写) -x(可执行)

# 文件判断示例
if [ -f "/etc/nginx/nginx.conf" ]; then
    echo "nginx 配置文件存在"
fi

if [ -d "/var/log" ]; then
    echo "/var/log 目录存在"
fi

# 逻辑运算
if [ $age -gt 18 ] && [ "$name" = "zhangsan" ]; then
    echo "成年且叫 zhangsan"
fi

# 或
if [ $age -gt 18 ] || [ "$name" = "zhangsan" ]; then
    echo "成年或叫 zhangsan"
fi

# 现代写法 [[ ]]（推荐，更安全）
if [[ $age -gt 18 && $name == "zhangsan" ]]; then
    echo "成年且叫 zhangsan"
fi
```

### 10.4 循环

```bash
#!/bin/bash

# for 循环
for i in 1 2 3 4 5; do
    echo "第 $i 次"
done

# 范围循环
for i in {1..10}; do
    echo $i
done

# 遍历文件
for file in *.txt; do
    echo "处理: $file"
    wc -l "$file"
done

# while 循环
count=1
while [ $count -le 5 ]; do
    echo "计数: $count"
    count=$((count + 1))
done

# 逐行读取文件
while IFS= read -r line; do
    echo "行内容: $line"
done < file.txt
```

### 10.5 函数

```bash
#!/bin/bash

# 定义函数
greet() {
    local name=$1        # $1 是第一个参数，local 表示局部变量
    echo "你好，$name！"
}

# 调用
greet "张三"

# 带返回值的函数
add() {
    local result=$(($1 + $2))
    echo $result          # 用 echo 输出结果
}

sum=$(add 3 5)
echo "3 + 5 = $sum"
```

### 10.6 常用特殊变量

| 变量 | 含义 |
|------|------|
| `$0` | 脚本名称 |
| `$1-$9` | 第 1-9 个参数 |
| `$#` | 参数个数 |
| `$@` | 所有参数（各自独立） |
| `$*` | 所有参数（合并为一个） |
| `$?` | 上一条命令的退出码（0=成功） |
| `$$` | 当前脚本 PID |

```bash
#!/bin/bash

echo "脚本名: $0"
echo "参数1: $1"
echo "参数个数: $#"
echo "所有参数: $@"

# 检查命令是否执行成功
if [ $? -eq 0 ]; then
    echo "上条命令执行成功"
fi
```

---

## 11. 文本处理三剑客

### 11.1 grep：文本搜索

```bash
# 基础搜索
grep "error" app.log                      # 搜索包含 error 的行
grep -i "error" app.log                   # 忽略大小写
grep -v "debug" app.log                   # 排除 debug（取反）
grep -r "TODO" ./src/                     # 递归搜索目录

# 高级选项
grep -n "error" app.log                   # 显示行号
grep -c "error" app.log                   # 只显示匹配行数
grep -A 3 "error" app.log                 # 显示匹配行及后 3 行
grep -B 2 "error" app.log                 # 显示匹配行及前 2 行
grep -C 3 "error" app.log                 # 显示匹配行及前后 3 行
grep -E "error|fail" app.log              # 正则（或）
grep -o "ip=[0-9.]*" log.txt             # 只显示匹配部分

# 常用组合
grep -rn "TODO" .                         # 递归 + 行号
grep -c "ERROR" app.log                   # 统计报错次数
```

### 11.2 sed：流编辑器（查找替换）

```bash
# 替换（最常用）
sed 's/old/new/' file.txt                 # 每行替换第一个
sed 's/old/new/g' file.txt                # 全局替换
sed 's/old/new/2' file.txt                # 每行替换第二个
sed -i 's/old/new/g' file.txt             # 直接修改文件（-i 就位修改）
sed -i.bak 's/old/new/g' file.txt         # 改之前备份成 .bak

# 删除
sed '5d' file.txt                         # 删除第 5 行
sed '5,10d' file.txt                      # 删除第 5-10 行
sed '/pattern/d' file.txt                 # 删除匹配行

# 打印
sed -n '5p' file.txt                      # 只打印第 5 行
sed -n '5,10p' file.txt                   # 打印第 5-10 行

# 在匹配行后追加
sed '/pattern/a\新的一行' file.txt

# 实战：批量修改配置文件
sed -i 's/localhost/10.0.0.1/g' config.properties
```

### 11.3 awk：数据提取与处理

```bash
# awk 按列处理文本（默认按空格/Tab 分割）
awk '{print $1}' file.txt                 # 打印第 1 列
awk '{print $1, $3}' file.txt             # 打印第 1 列和第 3 列
awk '{print $NF}' file.txt                # 打印最后一列（NF=列数）
awk '{print $(NF-1)}' file.txt            # 打印倒数第二列

# 自定义分隔符
awk -F: '{print $1, $3}' /etc/passwd      # 冒号分隔
awk -F',' '{print $2}' data.csv           # 逗号分隔（CSV）

# 条件过滤
awk '$3 > 100' data.txt                   # 第 3 列 > 100 的行
awk '$1 == "ERROR"' app.log               # 第 1 列是 ERROR 的行
awk 'length($0) > 80' file.txt            # 行长度 > 80

# 计算
awk '{sum += $1} END {print sum}' data.txt    # 求和
awk '{sum += $1} END {print sum/NR}' data.txt # 求平均（NR=行数）

# 实战：分析日志
# 统计每个 IP 访问次数
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -10

# 统计每个状态码的数量
awk '{print $9}' access.log | sort | uniq -c | sort -rn

# 计算请求总耗时
awk '{sum += $NF} END {print "平均:", sum/NR, "总:", sum}' timing.log
```

### 11.4 其他利器

```bash
# sort：排序
sort file.txt                              # 升序
sort -r file.txt                           # 降序
sort -n file.txt                           # 按数字排序
sort -t',' -k2 data.csv                    # 按第 2 列排序（逗号分隔）
sort -u file.txt                           # 去重排序

# uniq：去重（通常先 sort）
sort file.txt | uniq                       # 去重
sort file.txt | uniq -c                    # 去重并计数（超常用！）
sort file.txt | uniq -d                    # 只显示重复的行

# cut：按列切分
cut -d':' -f1,3 /etc/passwd                # 取第 1、3 列
cut -c1-10 file.txt                        # 取每行前 10 个字符

# xargs：将标准输入转为命令参数
echo "file1.txt file2.txt" | xargs rm      # 删除这些文件
find . -name "*.log" | xargs rm            # 删除所有 log 文件
find . -name "*.py" | xargs wc -l          # 统计所有 Python 文件行数
cat urls.txt | xargs -I {} curl -O {}      # 批量下载

# tee：输出到屏幕同时写入文件
./app 2>&1 | tee app.log                   # 看日志的同时保存
```

---

## 12. 日志与系统信息

### 12.1 日志管理

```bash
# 系统日志位置
/var/log/syslog              # 系统主日志（Ubuntu/Debian）
/var/log/messages            # 系统主日志（CentOS/RHEL）
/var/log/auth.log            # 认证日志（登录记录）
/var/log/kern.log            # 内核日志
/var/log/dmesg               # 启动日志

# 查看 dmesg
dmesg | tail -50             # 最后 50 行内核日志
dmesg | grep -i error        # 查错误

# journalctl（systemd 日志）
journalctl -u nginx          # nginx 服务日志
journalctl -u nginx -f       # 实时追踪（-f = follow）
journalctl --since today     # 今天的日志
journalctl -u ssh --since "1 hour ago"
```

### 12.2 系统信息

```bash
# 概览
uname -a                       # 内核版本、架构等
cat /etc/os-release            # 系统版本
hostnamectl                    # 主机名和系统信息

# 硬件
lscpu                          # CPU 信息
cat /proc/cpuinfo | grep "model name" | head -1   # CPU 型号
free -h                        # 内存
lspci                          # PCI 设备
lsusb                          # USB 设备

# 时间
date                           # 当前时间
timedatectl                    # 时区等信息
cal                            # 日历

# 命令历史
history                        # 查看历史命令
history | grep git             # 搜用过的命令
!123                           # 重新执行第 123 条命令
!!                             # 重新执行上一条
!$                             # 上一条命令的最后一个参数（超有用！）
```

### 12.3 服务管理 (systemctl)

```bash
# 启动 / 停止 / 重启
systemctl start nginx               # 启动
systemctl stop nginx                # 停止
systemctl restart nginx             # 重启
systemctl reload nginx              # 重新加载配置（不中断服务）
systemctl status nginx              # 查看状态

# 开机自启
systemctl enable nginx              # 设为开机自启
systemctl disable nginx             # 禁止开机自启
systemctl is-enabled nginx          # 是否开机自启

# 查看
systemctl list-units --type=service    # 所有服务
systemctl list-unit-files --type=service  # 所有服务的启用状态
systemctl list-units --state=failed    # 失败的服务
```

---

## 13. 定时任务

### 13.1 Crontab

```bash
# crontab 格式
# 分 时 日 月 周 命令
# 0-59 0-23 1-31 1-12 0-7(0和7都是周日)

# 编辑
crontab -e                      # 编辑当前用户的定时任务
crontab -l                      # 查看定时任务
crontab -r                      # 删除所有定时任务

# 常见写法示例
30 2 * * * /backup/backup.sh            # 每天凌晨 2:30 执行
0 9 * * 1-5 echo "工作日好"              # 工作日早上 9:00
*/5 * * * * /usr/bin/python3 check.py   # 每 5 分钟执行
0 0 1 * * /opt/monthly/run.sh           # 每月 1 号零点
0 */2 * * * /opt/task.sh               # 每 2 小时执行
```

**crontab 在线验证工具**：crontab.guru，不确定就粘贴验证。

---

## 14. SSH 远程连接

### 14.1 基础使用

```bash
# 密码连接
ssh user@10.0.0.1                        # 默认端口 22
ssh -p 2222 user@10.0.0.1               # 指定端口

# 免密登录（三步）
# 1. 本机生成密钥
ssh-keygen -t rsa -b 4096               # 一路回车

# 2. 把公钥复制到远程服务器
ssh-copy-id user@10.0.0.1

# 3. 之后直接连
ssh user@10.0.0.1                        # 不需要密码了

# 上传/下载
scp local.txt user@10.0.0.1:/home/user/
scp user@10.0.0.1:/home/user/remote.txt ./
```

### 14.2 SSH 配置文件（超实用）

```bash
# ~/.ssh/config
Host myserver
    HostName 10.0.0.1
    User zhangsan
    Port 2222
    IdentityFile ~/.ssh/id_rsa

Host prod-db
    HostName db.prod.example.com
    User admin
    Port 22

# 之后只需：
ssh myserver                 # 代替 ssh -p 2222 -i ~/.ssh/id_rsa zhangsan@10.0.0.1
scp file.txt myserver:~/     # 简单！
```

### 14.3 SSH 隧道（端口转发）

```bash
# 本地端口转发：把远程端口映射到本地
ssh -L 3306:localhost:3306 user@10.0.0.1
# 然后本机连 3306 就等于连远程的 3306

# 跳板机：通过一台机器访问另一台
ssh -J jumpbox user@target-server
# 或配置 ~/.ssh/config:
# Host target
#     HostName 10.0.0.100
#     ProxyJump jumpbox
```

---

## 15. 实用技巧汇总

### 15.1 重定向与管道

```bash
# 输出重定向
command > file.txt             # 覆盖写入（标准输出）
command >> file.txt            # 追加写入（标准输出）
command 2> error.txt           # 错误输出写入文件
command &> all.txt             # 标准输出和错误都写入文件
command > /dev/null 2>&1       # 丢弃所有输出

# 管道 |：把一个命令的输出作为下一个命令的输入
cat access.log | grep ERROR | wc -l    # 统计错误行数
ps aux | grep nginx | awk '{print $2}' # 拿到 nginx 的 PID
```

### 15.2 快捷键速查

| 快捷键 | 作用 |
|--------|------|
| `Ctrl+C` | 终止当前命令 |
| `Ctrl+Z` | 暂停并放到后台 |
| `Ctrl+D` | 退出终端 / 发送 EOF |
| `Ctrl+L` | 清屏 |
| `Ctrl+R` | 搜索历史命令 |
| `Ctrl+A` | 跳到行首 |
| `Ctrl+E` | 跳到行尾 |
| `Ctrl+U` | 删除光标前的内容 |
| `Ctrl+K` | 删除光标后的内容 |
| `Ctrl+W` | 删除前一个单词 |
| `Tab` | 自动补全 |

### 15.3 别名

```bash
# 查看已有的别名
alias

# 临时设置
alias ll='ls -alh'

# 永久设置：加到 ~/.bashrc 或 ~/.zshrc
echo "alias ll='ls -alh'" >> ~/.bashrc
echo "alias la='ls -A'" >> ~/.bashrc
source ~/.bashrc

# 常用别名推荐
alias ll='ls -alh'
alias la='ls -A'
alias l='ls -CF'
alias grep='grep --color=auto'
alias ..='cd ..'
alias ...='cd ../..'
alias gs='git status'
alias gd='git diff'
alias gc='git commit'
alias gp='git push'
```

### 15.4 一行命令技巧

```bash
# 批量重命名（在文件名前加前缀）
for f in *.txt; do mv "$f" "backup_$f"; done

# 找到并删除 7 天前的日志
find /var/log -name "*.log" -mtime +7 -delete

# 统计代码行数
find . -name "*.py" | xargs wc -l
find . -name "*.py" -o -name "*.js" | xargs wc -l   # 多种文件

# 查看最耗 CPU 的进程
ps aux --sort=-%cpu | head -10

# 查看最耗内存的进程
ps aux --sort=-%mem | head -10

# 快速备份文件
cp config.conf{,.bak}          # 等同于 cp config.conf config.conf.bak

# 查看外网 IP
curl ifconfig.me
curl ipinfo.io

# 列出目录但排除某些文件
ls | grep -v "node_modules"

# 递归替换文本（需谨慎！）
find . -name "*.txt" -exec sed -i 's/old/new/g' {} \;
# macOS 用:
find . -name "*.txt" -exec sed -i '' 's/old/new/g' {} \;
```

### 15.5 新手常见问题

| 问题 | 解决 |
|------|------|
| Permission denied | `chmod +x file` 加执行权限 或 `sudo` |
| Command not found | 没装这个软件，用包管理器安装 |
| No such file or directory | 路径写错了或文件不存在，用 `pwd` 和 `ls` 确认 |
| Cannot open display | 这是服务器，没有图形界面 |
| E212: Can't open file for writing | vim 打开的文件你没写权限，用 `sudo vim` |
| 系统卡住不动了 | `top` 查 CPU/内存，`df -h` 查磁盘 |

---

## 速查卡片

### 最常用的 20 个命令

```bash
ls -la          # 看目录内容（包括隐藏文件）
cd -            # 回到上次的目录
pwd             # 当前在哪
mkdir -p a/b    # 创建多层目录
rm -rf dir/     # 删除目录（谨慎！）
cp -r a/ b/     # 复制目录
mv old new      # 移动/重命名
find . -name "*.txt"   # 找文件
grep "xxx" file # 搜文本
tail -f log     # 实时看日志
ps aux | grep xx    # 查进程
kill -9 PID     # 杀进程
top             # 看系统负载
df -h           # 磁盘使用
free -h         # 内存使用
chmod 755 file  # 改权限
tar -xzvf f.tar.gz  # 解压
curl URL        # 发 HTTP 请求
ssh user@host   # 远程连接
history         # 看用过的命令
```

### macOS vs Linux 的细微差异

```bash
# sed -i（macOS 需要额外参数）
sed -i '' 's/old/new/g' file.txt    # macOS
sed -i 's/old/new/g' file.txt       # Linux

# 没有 /proc 下的一些内容
# macOS 用 sysctl 代替
sysctl -n machdep.cpu.brand_string  # macOS 看 CPU 型号

# 包管理器
brew install nginx                   # macOS 用 Homebrew

# 命令差异
# 很多 Linux 命令在 macOS 上是 BSD 版本，参数可能不同
# 如 sed, grep, find 等，查 man 确认
```

---

> **最好的学习方法是多用。遇到不懂的加 `--help` 或查 `man`，例如 `ls --help` 或 `man ls`。**
