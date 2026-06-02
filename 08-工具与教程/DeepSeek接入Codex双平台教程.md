# DeepSeek 模型接入 Codex 双平台完整教程

> Windows + Mac 双平台完整教程，通过 mimo2codex 中间件 + CC Switch 实现 DeepSeek 模型接入 Codex，无需修改核心文件，安全稳定。

---

## 方案概述

通过**本地中间件转发**实现 DeepSeek 模型接入 Codex，无需修改 Codex 核心文件，安全稳定、成本低。DeepSeek API Key 只在本地使用，不会泄露到第三方。

**核心组件：**

- **mimo2codex**：本地中间件，负责请求转发和模型适配
- **CC Switch**：跨平台配置管理工具，管理 Codex 供应商配置
- **DeepSeek API**：提供模型能力

![方案架构图](https://mmbiz.qpic.cn/sz_mmbiz_png/hD3LeQ7JOicsVQEic6goicic9XoFnPBKEkaZd6ZxCmZMFJhqxUdcURaMoYxw9qWdkrJb1Oe0Af8njQ4INJdPwtR4Oe5HF6j5hicG95ficnBFww6XQ/640?wx_fmt=png&from=appmsg)

---

## 前置准备（Mac & Windows 通用）

### 1. 安装 Node.js

推荐 LTS 版本（v18 或更高）。

**Mac（推荐 Homebrew）：**

```bash
brew install node
```

**Windows：**

从 Node.js 官网下载安装包。

**验证安装：**

```bash
node -v
npm -v
```

### 2. 获取 DeepSeek API Key

1. 访问 DeepSeek 平台
2. 注册/登录账号
3. 进入 **API Keys** 页面
4. 创建新 Key 并复制保存

> **安全提示**：API Key 只在本地使用，不要分享给他人或上传到公开仓库。

### 3. 安装 CC Switch

**Mac（推荐 Homebrew）：**

```bash
brew tap farion1231/ccswitch
brew install --cask cc-switch
```

或从 GitHub Releases 下载 `.dmg` 文件，双击安装并拖入 Applications 文件夹。

**Windows：**

下载 `.msi` 安装包或便携版，按提示安装。

**首次启动：**

- Mac 用户若遇到 Gatekeeper 提示，前往"系统设置 → 隐私与安全性"允许应用运行
- CC Switch 会自动管理 Codex 等工具的配置文件

### 4. 安装 Codex

按照 Codex 官方文档安装 CLI 或桌面版，确保能正常启动。

---

## 步骤 1：全局安装 mimo2codex 中间件

**Mac（Terminal）：**

```bash
npm install -g mimo2codex
```

如遇权限问题，使用 `sudo`：

```bash
sudo npm install -g mimo2codex
```

**Windows（管理员 PowerShell）：**

```powershell
npm install -g mimo2codex
```

**验证安装：**

```bash
mimo2codex --help
```

---

## 步骤 2：启动本地转发服务（核心步骤）

**Mac（Terminal）：**

```bash
export DEEPSEEK_API_KEY="sk-你的真实DeepSeek_API_Key在这里"
mimo2codex --model ds --port 8789
```

**Windows（PowerShell）：**

```powershell
$env:DEEPSEEK_API_KEY="sk-你的真实DeepSeek_API_Key在这里"
mimo2codex --model ds --port 8789
```

**参数说明：**

| 参数 | 说明 |
|------|------|
| `--model ds` | 使用 DeepSeek 模型 |
| `--port 8789` | 本地服务端口（可改为其他空闲端口） |
| `DEEPSEEK_API_KEY` | 你的 DeepSeek API Key |

**重要提示：**

- 替换 `sk-你的真实DeepSeek_API_Key在这里` 为你的实际 Key
- **保持此终端窗口一直打开**，服务会持续运行
- 服务启动后监听 `http://127.0.0.1:8789`

---

## 步骤 3：获取 CC Switch 配置信息

**新开另一个 Terminal / PowerShell 窗口**（不要关闭服务窗口），运行：

```bash
mimo2codex --model ds --port 8789 print-cc-switch
```

输出包含 **auth.json** 和 **config.toml** 两段配置，**完整复制**备用。

---

## 步骤 4：在 CC Switch 中添加 DeepSeek 供应商

**Mac & Windows 操作相同：**

1. 打开 **CC Switch** 应用
2. 切换到 **Codex** 标签页
3. 点击 **添加新供应商** → 选择 **自定义 / OpenAI 兼容**
4. 填写配置信息：

| 配置项 | 值 |
|--------|-----|
| **供应商名称** | `DeepSeek` 或 `DEEPSEEK` |
| **API Key** | `mimo2codex-local`（或工具输出的对应值） |
| **Base URL** | `http://127.0.0.1:8789/v1` |
| **模型名称** | `deepseek-v4-pro`、`deepseek-v4-flash` 等 |

5. 在 config.toml 编辑区粘贴步骤 3 的内容，修改 `name` 为 `DEEPSEEK`，保存并启用
6. CC Switch 会自动写入 Codex 配置文件

---

## 步骤 5：验证与使用

1. **重启 Codex** 应用
2. 在模型选择栏选择 **DEEPSEEK**
3. 发送测试指令，例如：

```
你好
```

4. 看到 DeepSeek 正常回复即表示接入成功

![验证成功截图](https://mmbiz.qpic.cn/sz_mmbiz_png/hD3LeQ7JOict6M1YOOeGEko21BUAKEhiaZ2BcGCcwTDAicicYd61rZCDK9RFku8tOPb3iba4nW6HxiciclKBq8kC6icDIbofk9tjSvS67HRTePbAuz4/640?wx_fmt=png&from=appmsg)

---

## Mac 专属常见问题排查

### 权限问题

全局 npm 安装常用 `sudo`，或使用 `nvm` 管理 Node.js 避免 sudo：

```bash
brew install nvm
nvm install node
```

### 端口占用

检查并释放端口：

```bash
lsof -i :8789
kill -9 <PID>
```

### 环境变量持久化

`export` 只在当前 Terminal 有效，可写成启动脚本：

```bash
#!/bin/bash
# ~/deepseek-mimo.sh
export DEEPSEEK_API_KEY="sk-xxx"
mimo2codex --model ds --port 8789
```

赋予执行权限：

```bash
chmod +x ~/deepseek-mimo.sh
```

### 后台运行（推荐）

使用 PM2 进程管理器：

```bash
brew install pm2
pm2 start "mimo2codex --model ds --port 8789" --name deepseek-mimo --env DEEPSEEK_API_KEY=sk-xxx
```

**常用 PM2 命令：**

```bash
pm2 list          # 查看运行状态
pm2 logs          # 查看日志
pm2 stop all      # 停止所有服务
pm2 startup       # 配置开机自启
```

### Gatekeeper 问题

首次打开 CC Switch `.dmg` 时，若提示不安全：

1. 前往"系统设置 → 隐私与安全性"
2. 找到 CC Switch 相关提示
3. 点击"仍要打开"

---

## Windows & Mac 通用排查

| 问题 | 解决方案 |
|------|---------|
| 服务没启动 / 端口冲突 | 换端口并同步修改配置 |
| 配置不生效 | 重启 CC Switch 和 Codex，检查 `~/.codex/` 目录 |
| 响应慢 | 检查网络或 DeepSeek API 限流 |
| 更新 mimo2codex | `npm update -g mimo2codex` |

---

## 进阶建议

### 开机自启

使用 PM2 配置开机自启：

```bash
pm2 startup
pm2 save
```

或使用 LaunchAgents 配置系统级自启。

### 多模型支持

重复步骤 1-4，添加其他模型供应商：

- Claude
- GPT-4
- 本地模型（Ollama 等）

### 安全性加固

- API Key 只在本地循环，不泄露到外部
- 使用环境变量或密钥管理工具存储 Key
- 定期轮换 API Key

### 脚本自动化

Mac 用户可编写 shell 脚本一键启动：

```bash
#!/bin/bash
# 一键启动 DeepSeek + Codex

# 启动中间件
export DEEPSEEK_API_KEY="sk-xxx"
pm2 start "mimo2codex --model ds --port 8789" --name deepseek-mimo

# 等待服务启动
sleep 2

# 启动 Codex
open -a Codex

echo "DeepSeek 服务已启动，Codex 已打开"
```

---

## 总结

本教程提供了 Windows 和 Mac 双平台的完整部署方案：

1. **安装依赖**：Node.js、CC Switch、Codex
2. **部署中间件**：全局安装并启动 mimo2codex
3. **配置连接**：通过 CC Switch 添加 DeepSeek 供应商
4. **验证使用**：重启 Codex 并测试模型响应

**方案优势：**

- 无需修改 Codex 核心文件
- 本地转发，安全稳定
- 成本低，按需使用
- 支持多模型切换

> 实际操作中遇到任何报错，把具体错误信息或截图发给我，我继续帮你调试！
> 祝你部署顺利，编程效率大幅提升！
