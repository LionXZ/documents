# Electron vs Tauri 技术栈详解

> 两个主流的桌面应用开发框架对比，包含完整的代码示例和开发流程。

---

## 目录

- [1. 基础对比](#1-基础对比)
- [2. Electron 开发详解](#2-electron-开发详解)
  - [2.1 项目初始化](#21-项目初始化)
  - [2.2 项目结构](#22-项目结构)
  - [2.3 主进程代码](#23-主进程代码)
  - [2.4 预加载脚本](#24-预加载脚本)
  - [2.5 渲染进程 (前端)](#25-渲染进程-前端)
  - [2.6 IPC 通信](#26-ipc-通信)
  - [2.7 系统托盘 + 菜单](#27-系统托盘--菜单)
  - [2.8 自动更新](#28-自动更新)
  - [2.9 打包发布](#29-打包发布)
- [3. Tauri 开发详解](#3-tauri-开发详解)
  - [3.1 环境准备](#31-环境准备)
  - [3.2 项目初始化](#32-项目初始化)
  - [3.3 项目结构](#33-项目结构)
  - [3.4 Rust 后端代码](#34-rust-后端代码)
  - [3.5 前端代码](#35-前端代码)
  - [3.6 Tauri Command (IPC)](#36-tauri-command-ipc)
  - [3.7 系统托盘 + 菜单](#37-系统托盘--菜单)
  - [3.8 Sidecar 子进程](#38-sidecar-子进程)
  - [3.9 自动更新](#39-自动更新)
  - [3.10 打包发布](#310-打包发布)
- [4. 核心能力对比](#4-核心能力对比)
- [5. 与现有 Vue 项目集成](#5-与现有-vue-项目集成)
- [6. 选型决策树](#6-选型决策树)

---

## 1. 基础对比

| | Electron | Tauri v2 |
|------|------|------|
| **语言** | JavaScript/TypeScript | Rust + JS/TS |
| **渲染引擎** | Chromium (系统webview 不可用) | 系统原生 WebView (WebKit/WinRT) |
| **安装包大小** | ~85MB (Hello World) | ~5MB (Hello World) |
| **内存占用** | ~150MB 起步 | ~50MB 起步 |
| **平台** | Win + Mac + Linux | Win + Mac + Linux |
| **Node.js 生态** | ✅ 直接可用 | ❌ 需 sidecar |
| **Python 集成** | child_process / python-shell | sidecar / shell command |
| **自动更新** | electron-updater (成熟) | tauri-plugin-updater |
| **商业成熟度** | 10 年，Slack/VSCode/Discord | 3 年，Figma/Zed/LanceDB |
| **学习曲线** | 前端开发者零门槛 | 需了解 Rust 基础 |
| **多窗口** | ✅ 原生 | ✅ |
| **系统托盘** | ✅ | ✅ |
| **SQLite** | better-sqlite3 | Rust 原生 |

---

## 2. Electron 开发详解

> 以一个「激活窗口 → 主窗口」的桌面应用为例。

### 2.1 项目初始化

```bash
# 创建项目
mkdir my-electron-app && cd my-electron-app
npm init -y

# 安装 Electron
npm install electron --save-dev

# 安装打包工具
npm install electron-builder --save-dev
```

### 2.2 项目结构

```
my-electron-app/
├── package.json
├── electron-builder.yml        # 打包配置
├── src/
│   ├── main/                   # 主进程
│   │   ├── index.js            # 入口
│   │   ├── ipc.js              # IPC 处理器
│   │   ├── tray.js             # 系统托盘
│   │   └── updater.js          # 自动更新
│   ├── preload/
│   │   └── index.js            # 预加载脚本 (安全桥接)
│   └── renderer/               # 渲染进程 (前端)
│       ├── index.html          # 激活/登录页
│       ├── main.html           # 主窗口
│       ├── assets/
│       └── js/
├── resources/                  # 图标等资源
└── dist/                       # 打包输出
```

### 2.3 主进程代码

```javascript
// src/main/index.js
const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow = null;
let activateWindow = null;

// ---- 应用生命周期 ----
app.whenReady().then(() => {
  // 先弹出激活窗口
  createActivateWindow();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

// ---- 激活窗口 ----
function createActivateWindow() {
  activateWindow = new BrowserWindow({
    width: 500,
    height: 400,
    resizable: false,
    frame: false,          // 无边框
    webPreferences: {
      preload: path.join(__dirname, '../preload/index.js'),
      contextIsolation: true,   // 安全: 隔离渲染进程
      nodeIntegration: false,   // 安全: 禁用 Node
    },
  });

  activateWindow.loadFile('src/renderer/index.html');

  // 激活成功后切换到主窗口
  ipcMain.handle('activate-success', () => {
    activateWindow.close();
    createMainWindow();
  });
}

// ---- 主窗口 ----
function createMainWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, '../preload/index.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  mainWindow.loadFile('src/renderer/main.html');
}
```

### 2.4 预加载脚本

```javascript
// src/preload/index.js
const { contextBridge, ipcRenderer } = require('electron');

// 暴露安全的 API 给渲染进程
contextBridge.exposeInMainWorld('electronAPI', {
  // 激活相关
  activate: (code) => ipcRenderer.invoke('activate', code),

  // 窗口控制
  minimize: () => ipcRenderer.send('window-minimize'),
  maximize: () => ipcRenderer.send('window-maximize'),
  close: () => ipcRenderer.send('window-close'),

  // 文件操作
  openFileDialog: () => ipcRenderer.invoke('open-file-dialog'),
  saveFile: (path, content) => ipcRenderer.invoke('save-file', path, content),

  // 系统信息
  getPlatform: () => process.platform,
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),

  // 从主进程接收消息
  onUpdateAvailable: (callback) => ipcRenderer.on('update-available', callback),
});
```

### 2.5 渲染进程 (前端)

```html
<!-- src/renderer/index.html — 激活窗口 -->
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>激活</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: sans-serif;
      background: linear-gradient(135deg, #667eea, #764ba2);
      display: flex; align-items: center; justify-content: center;
      height: 100vh; color: #fff;
    }
    .activate-card {
      text-align: center;
      padding: 40px;
    }
    .activate-card h1 { margin-bottom: 24px; }
    .activate-card input {
      padding: 12px 16px; border-radius: 8px; border: none;
      width: 100%; font-size: 16px; text-align: center;
      margin-bottom: 16px;
    }
    .activate-card button {
      padding: 12px 32px; border: none; border-radius: 8px;
      background: #fff; color: #667eea; font-size: 16px;
      cursor: pointer; font-weight: 600;
    }
    .error { color: #ff6b6b; margin-top: 12px; }
  </style>
</head>
<body>
  <div class="activate-card">
    <h1>欢迎使用 MyApp</h1>
    <p style="margin-bottom: 16px; opacity: .8;">请输入激活码开始使用</p>
    <input
      id="codeInput"
      type="text"
      placeholder="XXXX-XXXX-XXXX-XXXX"
      maxlength="19"
    />
    <br>
    <button onclick="doActivate()">激活</button>
    <div id="error" class="error"></div>
  </div>
  <script>
    async function doActivate() {
      const code = document.getElementById('codeInput').value.trim();
      const errorEl = document.getElementById('error');

      if (!code) {
        errorEl.textContent = '请输入激活码';
        return;
      }

      try {
        // 调用远程 API 验证激活码
        const response = await fetch('https://api.example.com/v1/activate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ license_key: code }),
        });

        const data = await response.json();

        if (data.valid) {
          // 保存授权信息
          window.electronAPI.saveFile('license.json', JSON.stringify(data));
          // 通知主进程切换到主窗口
          window.electronAPI.activate(true);
        } else {
          errorEl.textContent = data.message || '激活码无效';
        }
      } catch (e) {
        errorEl.textContent = '网络错误，请重试';
      }
    }
  </script>
</body>
</html>
```

### 2.6 IPC 通信

```javascript
// src/main/ipc.js
const { ipcMain, dialog, app } = require('electron');
const fs = require('fs');
const crypto = require('crypto');

// 注册所有 IPC 处理器
function registerIPC() {
  // ---- 激活验证 ----
  ipcMain.handle('activate', async (event, licenseKey) => {
    // 采集硬件指纹
    const fingerprint = getHardwareFingerprint();

    // 调用远程激活服务器
    const response = await fetch('https://api.example.com/v1/activate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        license_key: licenseKey,
        device_id: fingerprint,
      }),
    });

    const data = await response.json();

    if (data.valid) {
      // 本地存储授权信息
      const licensePath = path.join(app.getPath('userData'), 'license.json');
      fs.writeFileSync(licensePath, JSON.stringify(data));
      return { success: true };
    }

    return { success: false, message: data.message };
  });

  // ---- 文件对话框 ----
  ipcMain.handle('open-file-dialog', async () => {
    const result = await dialog.showOpenDialog({
      properties: ['openFile', 'multiSelections'],
      filters: [{ name: '视频', extensions: ['mp4', 'mov'] }],
    });
    return result.filePaths;
  });

  // ---- 窗口控制 ----
  ipcMain.on('window-minimize', (event) => {
    BrowserWindow.fromWebContents(event.sender).minimize();
  });
  ipcMain.on('window-close', (event) => {
    BrowserWindow.fromWebContents(event.sender).close();
  });
}

// ---- 硬件指纹采集 ----
function getHardwareFingerprint() {
  const os = require('os');
  const info = [
    os.hostname(),
    os.cpus()[0]?.model,
    os.networkInterfaces()?.en0?.[0]?.mac,
    os.platform(),
    os.arch(),
  ].join('|');

  return crypto.createHash('sha256').update(info).digest('hex');
}

module.exports = { registerIPC };
```

### 2.7 系统托盘 + 菜单

```javascript
// src/main/tray.js
const { Tray, Menu, app } = require('electron');
const path = require('path');

let tray = null;

function createTray(mainWindow) {
  tray = new Tray(path.join(__dirname, '../../resources/icon.png'));

  const contextMenu = Menu.buildFromTemplate([
    {
      label: '显示主窗口',
      click: () => mainWindow.show(),
    },
    {
      label: '截图',
      click: () => mainWindow.webContents.send('take-screenshot'),
    },
    { type: 'separator' },
    {
      label: '退出',
      click: () => app.quit(),
    },
  ]);

  tray.setToolTip('MyApp');
  tray.setContextMenu(contextMenu);

  tray.on('double-click', () => mainWindow.show());
}

module.exports = { createTray };
```

### 2.8 自动更新

```javascript
// src/main/updater.js
const { autoUpdater } = require('electron-updater');

function setupAutoUpdater() {
  // 配置更新源
  autoUpdater.setFeedURL({
    provider: 'github',
    owner: 'your-org',
    repo: 'my-app',
  });

  // 每 6 小时检查一次
  autoUpdater.checkForUpdatesAndNotify();

  setInterval(() => {
    autoUpdater.checkForUpdates();
  }, 6 * 60 * 60 * 1000);

  autoUpdater.on('update-available', (info) => {
    // 通知渲染进程
    mainWindow.webContents.send('update-available', info);
  });

  autoUpdater.on('update-downloaded', () => {
    // 提示用户重启
    mainWindow.webContents.send('update-ready');
  });
}
```

### 2.9 打包发布

```yaml
# electron-builder.yml
appId: com.example.myapp
productName: MyApp
copyright: Copyright 2026

directories:
  output: dist
  buildResources: resources

files:
  - src/**/*
  - package.json

mac:
  category: public.app-category.utilities
  target:
    - dmg
    - zip
  icon: resources/icon.icns
  hardenedRuntime: true
  entitlements: resources/entitlements.mac.plist

win:
  target:
    - nsis
    - portable
  icon: resources/icon.ico

nsis:
  oneClick: false
  allowToChangeInstallationDirectory: true

linux:
  target:
    - AppImage
    - deb
  category: Utility
```

```bash
# 打包命令
npm run build                    # 构建前端
npx electron-builder --mac       # 打包 macOS
npx electron-builder --win       # 打包 Windows
npx electron-builder --linux     # 打包 Linux
npx electron-builder -mwl        # 全平台
```

---

## 3. Tauri 开发详解

> 同样实现「激活窗口 → 主窗口」的桌面应用。

### 3.1 环境准备

```bash
# macOS
brew install rust
rustup update stable

# Windows
# 安装 Visual Studio Build Tools + Rust (https://rustup.rs)
# 或: winget install Rustlang.Rustup

# Linux
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
sudo apt install libwebkit2gtk-4.1-dev libappindicator3-dev librsvg2-dev
```

### 3.2 项目初始化

```bash
# 创建 Tauri + Vue 项目
npm create tauri-app@latest my-tauri-app -- --template vue

# 或手动集成到已有项目
cd existing-vue-project
npm install @tauri-apps/cli @tauri-apps/api
npx tauri init
```

```
# 回答交互提示:
? App name: my-tauri-app
? Window title: MyApp
? Where are your web assets? ../dist
? Dev server URL: http://localhost:5173
? Frontend dev command: npm run dev
? Frontend build command: npm run build
```

### 3.3 项目结构

```
my-tauri-app/
├── package.json                 # 前端依赖
├── vite.config.js
├── src/                         # 前端 (Vue)
│   ├── main.js
│   ├── App.vue
│   └── views/
├── src-tauri/                   # Rust 后端
│   ├── Cargo.toml               # Rust 依赖
│   ├── tauri.conf.json          # Tauri 配置
│   ├── capabilities/
│   │   └── default.json         # 权限声明
│   ├── icons/                   # 应用图标
│   └── src/
│       ├── main.rs              # Rust 入口
│       ├── lib.rs               # 核心逻辑 + Commands
│       ├── tray.rs              # 系统托盘
│       └── ipc.rs               # IPC 处理器
├── public/
└── dist/                        # 构建输出
```

### 3.4 Rust 后端代码

```rust
// src-tauri/src/main.rs
// 应用入口，禁止直接调用命令。

#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    tauri_app_lib::run();
}
```

```rust
// src-tauri/src/lib.rs
use tauri::Manager;
use std::process::Command;

mod tray;
mod ipc;

#[tauri::command]
fn get_hardware_fingerprint() -> String {
    // 采集硬件指纹
    let hostname = hostname::get()
        .unwrap_or_default()
        .to_string_lossy()
        .to_string();

    let mac = mac_address::get_mac_address()
        .ok()
        .flatten()
        .map(|m| m.to_string())
        .unwrap_or_default();

    let input = format!("{}|{}", hostname, mac);
    let hash = sha256::digest(input);

    hash
}

#[tauri::command]
async fn check_license(app: tauri::AppHandle, license_key: String) -> Result<String, String> {
    let fingerprint = get_hardware_fingerprint();

    // 调用远程激活服务器
    let client = reqwest::Client::new();
    let response = client
        .post("https://api.example.com/v1/activate")
        .json(&serde_json::json!({
            "license_key": license_key,
            "device_id": fingerprint,
        }))
        .send()
        .await
        .map_err(|e| format!("网络错误: {}", e))?;

    let data: serde_json::Value = response
        .json()
        .await
        .map_err(|e| format!("解析错误: {}", e))?;

    if data["valid"].as_bool().unwrap_or(false) {
        // 保存授权到本地文件
        let app_dir = app.path().app_data_dir().unwrap();
        std::fs::create_dir_all(&app_dir).ok();
        std::fs::write(
            app_dir.join("license.json"),
            data.to_string(),
        ).ok();
        Ok("激活成功".to_string())
    } else {
        Err(data["message"].as_str().unwrap_or("激活失败").to_string())
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())       // 执行系统命令
        .plugin(tauri_plugin_dialog::init())      // 文件对话框
        .plugin(tauri_plugin_fs::init())          // 文件系统
        .plugin(tauri_plugin_clipboard::init())   // 剪贴板
        .plugin(tauri_plugin_updater::Builder::new().build()) // 自动更新
        .setup(|app| {
            tray::create_tray(app.handle())?;
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            check_license,
            get_hardware_fingerprint,
            ipc::open_file_dialog,
            ipc::screenshot,
            ipc::run_python_script,
        ])
        .run(tauri::generate_context!())
        .expect("启动失败");
}
```

```toml
# src-tauri/Cargo.toml
[package]
name = "my-tauri-app"
version = "1.0.0"
edition = "2021"

[lib]
name = "tauri_app_lib"
crate-type = ["lib", "cdylib", "staticlib"]

[build-dependencies]
tauri-build = { version = "2", features = [] }

[dependencies]
tauri = { version = "2", features = [] }
tauri-plugin-shell = "2"
tauri-plugin-dialog = "2"
tauri-plugin-fs = "2"
tauri-plugin-clipboard = "2"
tauri-plugin-updater = "2"
serde = { version = "1", features = ["derive"] }
serde_json = "1"
reqwest = { version = "0.12", features = ["json"] }
sha256 = "1.5"
hostname = "0.4"
mac_address = "1.1"
tokio = { version = "1", features = ["full"] }
```

### 3.5 前端代码

```vue
<!-- src/views/ActivateView.vue -->
<template>
  <div class="activate-page">
    <div class="activate-card">
      <h1>欢迎使用 MyApp</h1>
      <p>请输入激活码开始使用</p>
      <input
        v-model="code"
        placeholder="XXXX-XXXX-XXXX-XXXX"
        maxlength="19"
        @keydown.enter="doActivate"
      />
      <button @click="doActivate" :disabled="loading">
        {{ loading ? '验证中...' : '激活' }}
      </button>
      <p v-if="error" class="error">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { invoke } from '@tauri-apps/api/core';

const code = ref('');
const loading = ref(false);
const error = ref('');

async function doActivate() {
  if (!code.value.trim()) return;

  loading.value = true;
  error.value = '';

  try {
    const result = await invoke('check_license', {
      licenseKey: code.value.trim(),
    });
    console.log('激活成功:', result);
    // 切换到主窗口
  } catch (e) {
    error.value = e;
  } finally {
    loading.value = false;
  }
}
</script>

<style lang="scss" scoped>
.activate-page {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background: linear-gradient(135deg, #667eea, #764ba2);
}

.activate-card {
  text-align: center;
  padding: 40px;
  color: #fff;

  h1 { margin-bottom: 24px; }

  input {
    padding: 12px 16px;
    border-radius: 8px;
    border: none;
    width: 100%;
    font-size: 16px;
    text-align: center;
    margin-bottom: 16px;
  }

  button {
    padding: 12px 32px;
    border: none;
    border-radius: 8px;
    background: #fff;
    color: #667eea;
    font-size: 16px;
    cursor: pointer;
    font-weight: 600;

    &:disabled { opacity: 0.6; }
  }

  .error { color: #ff6b6b; margin-top: 12px; }
}
</style>
```

### 3.6 Tauri Command (IPC)

```rust
// src-tauri/src/ipc.rs
use tauri::Manager;
use std::process::Command;

#[tauri::command]
pub async fn open_file_dialog(app: tauri::AppHandle) -> Result<Vec<String>, String> {
    use tauri_plugin_dialog::DialogExt;

    let files = app
        .dialog()
        .file()
        .add_filter("视频", &["mp4", "mov"])
        .add_filter("图片", &["png", "jpg"])
        .blocking_pick_files();

    match files {
        Some(paths) => Ok(paths.iter().map(|p| p.to_string()).collect()),
        None => Ok(vec![]),
    }
}

#[tauri::command]
pub async fn screenshot(app: tauri::AppHandle) -> Result<String, String> {
    // macOS: screencapture
    let output = Command::new("screencapture")
        .arg("-i")           // 交互式选区
        .arg("-c")           // 输出到剪贴板
        .output()
        .map_err(|e| e.to_string())?;

    if output.status.success() {
        Ok("截图已保存到剪贴板".to_string())
    } else {
        Err("截图失败".to_string())
    }
}

#[tauri::command]
pub async fn run_python_script(app: tauri::AppHandle, script: String) -> Result<String, String> {
    let python_path = app
        .path()
        .resource_dir()
        .unwrap()
        .join("python")
        .join("venv")
        .join("bin")
        .join("python3");

    let output = Command::new(python_path)
        .arg("-c")
        .arg(&script)
        .output()
        .map_err(|e| e.to_string())?;

    Ok(String::from_utf8_lossy(&output.stdout).to_string())
}
```

```json
// src-tauri/capabilities/default.json
{
  "identifier": "default",
  "description": "默认权限",
  "windows": ["main"],
  "permissions": [
    "core:default",
    "shell:allow-execute",
    "shell:allow-open",
    "dialog:default",
    "fs:default",
    "clipboard:allow-read",
    "clipboard:allow-write"
  ]
}
```

### 3.7 系统托盘 + 菜单

```rust
// src-tauri/src/tray.rs
use tauri::{
    menu::{Menu, MenuItem},
    tray::{MouseButton, MouseButtonState, TrayIconBuilder, TrayIconEvent},
    Manager, Runtime,
};

pub fn create_tray<R: Runtime>(app: &tauri::AppHandle<R>) -> tauri::Result<()> {
    let show = MenuItem::with_id(app, "show", "显示主窗口", true, None::<&str>)?;
    let screenshot = MenuItem::with_id(app, "screenshot", "截图", true, None::<&str>)?;
    let quit = MenuItem::with_id(app, "quit", "退出", true, None::<&str>)?;

    let menu = Menu::with_items(app, &[&show, &screenshot, &quit])?;

    let _tray = TrayIconBuilder::with_id("main-tray")
        .menu(&menu)
        .tooltip("MyApp")
        .on_tray_icon_event(|tray, event| {
            if let TrayIconEvent::Click {
                button: MouseButton::Left,
                button_state: MouseButtonState::Up,
                ..
            } = event
            {
                let app = tray.app_handle();
                if let Some(window) = app.get_webview_window("main") {
                    let _ = window.show();
                    let _ = window.set_focus();
                }
            }
        })
        .on_menu_event(|app, event| match event.id.as_ref() {
            "show" => {
                if let Some(window) = app.get_webview_window("main") {
                    let _ = window.show();
                    let _ = window.set_focus();
                }
            }
            "screenshot" => {
                if let Some(window) = app.get_webview_window("main") {
                    let _ = window.emit("take-screenshot", ());
                }
            }
            "quit" => {
                app.exit(0);
            }
            _ => {}
        })
        .build(app)?;

    Ok(())
}
```

### 3.8 Sidecar 子进程

Tauri 的 Sidecar 机制允许携带外部可执行文件（如 Python 脚本打包后的二进制）。

```json
// src-tauri/tauri.conf.json
{
  "bundle": {
    "externalBin": [
      "binaries/python-backend"   // 打包时自动包含
    ]
  }
}
```

```rust
// 调用 sidecar
use tauri_plugin_shell::ShellExt;

#[tauri::command]
async fn call_python_backend(app: tauri::AppHandle, endpoint: String, body: String) -> Result<String, String> {
    let sidecar = app.shell()
        .sidecar("python-backend")
        .map_err(|e| e.to_string())?;

    let output = sidecar
        .args([&endpoint, &body])
        .output()
        .await
        .map_err(|e| e.to_string())?;

    Ok(String::from_utf8_lossy(&output.stdout).to_string())
}
```

如果你的后端是 FastAPI，更简单的做法是用 **Sidecar 启动 HTTP 服务**：

```rust
// 启动时启动 Python 后端
use tauri_plugin_shell::ShellExt;

fn start_python_server(app: &tauri::AppHandle) {
    let shell = app.shell();

    let (mut rx, _child) = shell
        .command("python3")
        .args(["-m", "uvicorn", "api.server:app", "--port", "19876"])
        .spawn()
        .expect("启动 Python 后端失败");

    // 异步读取输出
    tauri::async_runtime::spawn(async move {
        while let Some(event) = rx.recv().await {
            // 处理输出
        }
    });
}
```

### 3.9 自动更新

```json
// src-tauri/tauri.conf.json
{
  "plugins": {
    "updater": {
      "endpoints": [
        "https://cdn.example.com/updates/{{target}}/{{arch}}/{{current_version}}"
      ],
      "pubkey": "base64 编码的 Ed25519 公钥"
    }
  }
}
```

```rust
// 在 lib.rs setup 中
tauri::Builder::default()
    .plugin(tauri_plugin_updater::Builder::new().build())
    .setup(|app| {
        // 启动后检查更新
        let handle = app.handle().clone();
        tauri::async_runtime::spawn(async move {
            if let Ok(Some(update)) = handle.updater().check().await {
                // 通知前端
                handle.emit("update-available", update).ok();
            }
        });
        Ok(())
    })
```

### 3.10 打包发布

```json
// src-tauri/tauri.conf.json (关键配置)
{
  "productName": "MyApp",
  "version": "1.0.0",
  "identifier": "com.example.myapp",
  "build": {
    "frontendDist": "../dist",
    "devUrl": "http://localhost:5173",
    "beforeDevCommand": "npm run dev",
    "beforeBuildCommand": "npm run build"
  },
  "bundle": {
    "active": true,
    "targets": "all",
    "icon": [
      "icons/32x32.png",
      "icons/128x128.png",
      "icons/icon.icns",
      "icons/icon.ico"
    ],
    "resources": [
      "binaries/*"
    ]
  }
}
```

```bash
# 打包命令
npm run tauri build              # 当前平台
npm run tauri build -- --target universal-apple-darwin  # macOS 通用
npm run tauri build -- --target x86_64-pc-windows-msvc   # Windows
```

---

## 4. 核心能力对比

| 场景 | Electron | Tauri v2 |
|------|------|------|
| **激活码验证** | `fetch()` 直接调 API | `reqwest` Rust crate |
| **硬件指纹** | `os.cpus()` + `crypto` | `sha256` + `mac_address` crates |
| **Python 后端** | `child_process.spawn()` | `tauri-plugin-shell` sidecar |
| **FastAPI 集成** | `spawn('python', ['-m', 'uvicorn'])` | 同上，或 sidecar 模式 |
| **文件对话框** | `dialog.showOpenDialog()` | `tauri-plugin-dialog` |
| **截屏** | `desktopCapturer` | `Command::new("screencapture")` |
| **系统托盘** | `Tray` API | `TrayIconBuilder` |
| **多窗口** | 多个 `BrowserWindow` | 多个 `WebviewWindow` |
| **开发体验** | 热重载，熟悉的 Node 生态 | 需 Rust 编译，首次慢 |
| **调试** | Chrome DevTools | Safari Web Inspector + Rust 日志 |

---

## 5. 与现有 Vue 项目集成

「DevAssistant」项目两种集成方式：

### Electron 方式

```bash
# 在 webapp 同级新建 electron 目录
mkdir electron && cd electron
npm init -y
npm install electron electron-builder

# 主进程加载 Vue 构建产物
mainWindow.loadFile('../webapp/dist/index.html');
# 或开发时用 dev server:
mainWindow.loadURL('http://localhost:3000');
```

### Tauri 方式

```bash
# 在 webapp 目录
npm install @tauri-apps/cli @tauri-apps/api
npx tauri init

# 回答问题时:
# Frontend dist: ../dist
# Dev server: http://localhost:3000
```

两种方式都不需要修改现有 Vue 代码，只需在 `window.electronAPI` 或 `@tauri-apps/api/core` 不可用时优雅降级（浏览器中正常 HTTP 调用，桌面壳中走 IPC）。

---

## 6. 选型决策树

```
你的项目特征？

1. 团队会 Rust？                  → Tauri (否则 Electron)
2. 安装包必须小 (<20MB)？         → Tauri
3. 需要密集用 Node.js 包？        → Electron
4. 已有 Python 后端服务？         → 两者都可以 (sidecar)
5. 需要最高商业稳定性？           → Electron (10年生态)
6. 预算/时间充足，要极致性能？    → Tauri
7. 快速原型/内部工具？            → Electron
```

---

> **来源：**
> - [Electron 官方文档](https://www.electronjs.org/docs)
> - [Tauri v2 官方文档](https://v2.tauri.app)
> - [electron-builder](https://www.electron.build)
> - [tauri-plugin-shell (Sidecar)](https://v2.tauri.app/plugin/shell/)
