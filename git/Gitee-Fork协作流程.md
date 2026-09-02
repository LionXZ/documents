# Gitee Fork + PR 协作流程

## 为什么这样做

这是典型的 **Fork + PR 协作模式**，常见于没有主仓库写权限的场景。

### 1. 权限隔离 — 保护主仓库代码安全
- 报告者/外部贡献者没有主仓库的写权限
- Fork 到自己名下后，在自己的仓库里随意操作（建分支、提交、删除分支），不影响主仓库

### 2. 联调阶段先在 Fork 之间 PR — 未完成代码不进主仓库
- 你和同事各自 fork，在各自的 fork 上开发
- 互相 PR 合并到其中一方的 fork，这个阶段代码可能还没完全稳定
- 如果直接在主仓库 PR 来回合并，会产生大量中间状态的 commit，污染主仓库的提交历史

### 3. 最终 PR 到主仓库 — 只进经过验证的干净代码
- 联调完成后，确认功能没问题了
- 再从 fork 提交一个干净的 PR 到主仓库
- 主仓库维护者看到的是一个完整的、可用的功能，而不是一堆 WIP commit

**总结：fork 之间互 PR = 开发调试沙盒，主仓库 PR = 正式交付。** 这样主仓库只接收经过联调验证的代码，历史干净、风险可控。

**完整协作链路：**
```
                            联调阶段（fork 互 PR）
  ┌──────────────┐                              ┌──────────────┐
  │   你的 Fork    │  ←── PR 互相合并 ──→       │  同事的 Fork   │
  │  (origin)     │                              │  (zhr)        │
  └──────┬───────┘                              └──────┬───────┘
         │                                             │
         │  联调完成，代码稳定                             │
         │  在你的 Fork 分支上                            │
         │                                             │
         ▼                                             │
  ┌──────────────┐                                     │
  │   主仓库       │  ← 提交正式 PR（管理员合并） ──────────┘
  │  (main/upstream)│
  └──────────────┘
```

---

## 各仓库角色权限

| 角色 | 权限概述 |
|---|---|
| **报告者 (Reporter)** | 只能看代码、提 Issue，不能提交代码、不能创建分支、不能提 PR |
| **开发者 (Developer)** | 可以提交代码、创建分支、创建 PR，但不能合并 PR |
| **管理员 (Admin)** | 拥有仓库完全控制权，包括合并 PR、管理成员、修改设置等 |

**权限层级与操作对应：**
```
  操作              报告者    开发者    管理员
  ─────────────────────────────────────────
  查看代码            ✅       ✅       ✅
  提 Issue            ✅       ✅       ✅
  提交代码            ❌       ✅       ✅
  创建分支            ❌       ✅       ✅
  创建 PR             ❌       ✅       ✅
  合并 PR             ❌       ❌       ✅
  管理成员            ❌       ❌       ✅
  修改仓库设置         ❌       ❌       ✅
```

---

## 操作步骤

### 一、本地仓库配置（不需要重新 clone）

在已有本地仓库上添加 fork 远程地址即可。

```bash
# 1. 查看当前远程配置
git remote -v

# 假设显示：
# origin  https://gitee.com/main-org/elephant-english.git (fetch)
# origin  https://gitee.com/main-org/elephant-english.git (push)

# 2. 重命名主仓库远程（方便后续同步）
git remote rename origin upstream

# 3. 添加你的 fork 为 origin
git remote add origin https://gitee.com/你的用户名/elephant-english.git
```

**多远程仓库拓扑结构：**
```
  本地仓库
  ├── .git/config（记录所有远程地址）
  │
  ├── remote: upstream → 主仓库（拉取最新代码、同步更新）
  │     URL: https://gitee.com/main-org/project.git
  │
  ├── remote: origin   → 你的 Fork（默认 push 目标）
  │     URL: https://gitee.com/你的用户名/project.git
  │
  └── remote: zhr      → 同事的 Fork（联调 push 目标）
        URL: https://gitee.com/同事/project-fork.git

  日常操作:
    git pull upstream master    ← 从主仓库拉取最新代码
    git push origin 分支名       ← 推送到自己的 Fork
    git push zhr 分支名          ← 推送到同事的 Fork（联调）
```

#### 实际案例

以本项目（elephant-english）为例，最终远程配置如下：

```bash
# git remote -v 输出：
main    git@gitee.com:xiaoxiangzhihui/elephant-english.git          (fetch)
main    git@gitee.com:xiaoxiangzhihui/elephant-english.git          (push)
origin  https://gitee.com/xiaoxiangzhihui/elephant-english-xz.git   (fetch)
origin  https://gitee.com/xiaoxiangzhihui/elephant-english-xz.git   (push)
zhr     https://gitee.com/xiaoxiangzhihui/elephant-english-timecraker.git (fetch)
zhr     https://gitee.com/xiaoxiangzhihui/elephant-english-timecraker.git (push)
```

对应关系：

```
main   → 主仓库（拉取最新代码）
origin → 你的 fork（默认 push 目标）
zhr    → 同事的 fork（联调时 push 到这里）
```

#### 分支跟踪设置

新 clone 下来的仓库，分支默认跟踪 `main`（主仓库），直接 `git push` 会推到主仓库。需要切换为跟踪自己的 fork：

```bash
# 1. 查看当前分支跟踪情况
git branch -vv

# 示例输出：
# * feat/xxx  15c03dd [main/feat/xxx]   ← 跟踪的是 main，会推到主仓库

# 2. 先推送分支到自己的 fork，同时设置跟踪（-u）
git push -u origin feat/xxx

# 3. 再次确认
git branch -vv

# 输出变为：
# * feat/xxx  15c03dd [origin/feat/xxx]  ← 跟踪的是 origin，会推到自己的 fork
```

> **注意：** 如果 fork 上还没有该分支，不能直接用 `git branch --set-upstream-to`，会报错 `does not exist`。需要先用 `git push -u origin 分支名` 推送并设置跟踪。

**分支跟踪关系图解：**
```
  设置前:                           设置后:
  feat/xxx ──track──> main/feat/xxx   feat/xxx ──track──> origin/feat/xxx
       │                    │             │                    │
       │  git push           │             │  git push          │
       ▼                    ▼             ▼                    ▼
    主仓库 ❌（可能被拒绝）              你的 Fork ✅（正常推送）

  操作: git push -u origin feat/xxx
```

---

### 二、向同事的 fork 提交 PR

```bash
# 1. 添加同事的 fork 为本地远程源
git remote add zhangsan https://gitee.com/zhangsan/elephant-english.git

# 2. 推送你的分支到同事的 fork
git push zhangsan 你的分支名
```

**3. 去 Gitee 上创建跨仓库 PR：**
- 打开**同事的 fork 仓库页面**（gitee.com/zhangsan/elephant-english）
- 点击 **Pull Requests** → **新建 Pull Request**
- 在"源分支"选择**你的 fork 仓库**和你的分支
- 在"目标分支"选择**同事的仓库**和他的目标分支（通常是 master）
- 填写说明后提交

> Gitee 支持跨 fork 的 PR，前提是同事的仓库设置中允许接收 PR。

**跨 Fork PR 数据流向：**
```
  你的 Fork                    Gitee 平台                  同事的 Fork
  ┌──────────┐                ┌──────────┐                ┌──────────┐
  │ feat/api │ ─── push ───> │          │                │          │
  │ (源分支)  │               │  跨仓库   │               │  master  │
  │          │               │  PR 合并  │ ── merge ──> │ (目标分支) │
  └──────────┘                └──────────┘                └──────────┘
                                     │
                                     ├── 1. 你 push 分支到同事的 fork
                                     ├── 2. 在同事仓库页面创建 PR
                                     └── 3. 同事 review 后合并
```

---

### 三、联调完成后合并到主仓库

**1. 确保最终代码在某个 fork 的分支上（比如你的 fork）**

联调结束后，最终的稳定代码应该集中在一个分支。

**2. 去主仓库创建 PR**
- 打开**主仓库页面** → **Pull Requests** → **新建 Pull Request**
- 源分支：选择**你的 fork** + 你的分支
- 目标分支：**主仓库**的 master
- 填写 PR 描述后提交

**3. 主仓库管理员审核并合并**
- 主仓库的维护者（管理员）review 代码
- 确认没问题后，由管理员点击合并

**联调 → 正式交付 全流程：**
```
  开发阶段                           联调阶段                        交付阶段
  ─────────                         ─────────                      ─────────

  你的 Fork                          你的 Fork                      你的 Fork
  feat/xxx ─┐                     ┌─ feat/xxx（汇总了双方代码）
            │  各自开发            │        │
            │                     │        │ 跨 fork PR
            │                     │        │ 互相合并
            ▼                     ▼        ▼
  同事的 Fork                     同事的 Fork                       主仓库
  feat/yyy ─┘                     feat/yyy                         master
                                                              ▲
                                                              │ 正式 PR
                                                              │ 管理员合并
                                                              │
                                              你的 Fork ──────┘
                                              feat/xxx（最终稳定代码）
```

---

### 四、同步 Fork 与主仓库（保持 Fork 最新）

主仓库持续有新代码合并进来，你的 Fork 不会自动同步，需要手动更新。

```bash
# 1. 确保 upstream 指向主仓库
git remote -v
# upstream  https://gitee.com/main-org/project.git

# 2. 拉取主仓库最新代码
git fetch upstream

# 3. 切换到 master/main 分支
git switch master

# 4. 合并主仓库的更新到本地
git merge upstream/master        # 或 git rebase upstream/master

# 5. 推送到你的 Fork（让 Fork 也同步）
git push origin master
```

**Fork 同步流程：**
```
  主仓库 (upstream)                    你的 Fork (origin)
  ┌────────────────┐                  ┌────────────────┐
  │ master          │                  │ master          │
  │ A──B──C──D──E   │                  │ A──B（旧版本）   │
  └───────┬────────┘                  └───────┬────────┘
          │                                   │
          │  git fetch upstream               │
          │ <─────────────────────────────────│
          │                                   │
          │  git merge upstream/master        │
          │                                   │
          ▼                                   ▼
    本地 master                             本地 master
    A──B──C──D──E（已更新）                  A──B──C──D──E
                                                │
                                                │ git push origin master
                                                ▼
                                          Fork 上的 master
                                          A──B──C──D──E（已同步）
```

#### Gitee 平台一键同步

Gitee 提供了平台级的同步功能（不需要命令行）：

1. 打开你的 Fork 仓库页面
2. 点击 **"同步"** 按钮（通常在仓库首页顶部）
3. 选择源仓库和分支，点击确认

> 注意：Gitee 的同步功能只能同步 master/main 分支，功能分支仍需手动操作。

---

## 常见问题与解决

### 1. PR 有冲突怎么办？

```
  冲突场景:
  主仓库:  A──B──C──D（有人合了新代码）
              \
  你的 Fork:   B──E──F（你基于 B 开发，但主仓库已经到了 D）

  解决:
  git fetch upstream              # 拉取主仓库最新代码
  git merge upstream/master       # 合并到你的分支（或用 rebase）
  # 手动解决冲突文件
  git add .
  git commit -m "解决合并冲突"
  git push origin feat/xxx        # 推送后 PR 自动更新
```

### 2. PR 被要求修改（追加 commit）

```bash
# 直接在同一个分支上继续改
git add .
git commit -m "按 review 意见修改 XXX"
git push origin feat/xxx
# PR 页面会自动更新，不需要重新创建 PR
```

如果需要保持提交历史干净（推荐在合并到主仓库前整理）：

```bash
git rebase -i HEAD~n             # 整理最近 n 次提交
# 将 review 修改的 commit 标记为 fixup
# 将多个小 commit squash 为一个
git push --force-with-lease origin feat/xxx
```

### 3. 推送到错误的远程仓库

```bash
# 误操作：git push（推到了主仓库，但你没有写权限）
# Gitee 会拒绝推送，因为报告者/开发者没有主仓库的直接写权限

# 正确做法：始终确认 push 目标
git push origin feat/xxx         # origin 是你的 Fork
git branch -vv                   # 再次确认分支跟踪关系
```

### 4. Fork 仓库落后主仓库太多

```bash
# 大量冲突时建议用 rebase 保持历史干净
git fetch upstream
git rebase upstream/master
# 逐 commit 解决冲突
git rebase --continue
git push --force-with-lease origin feat/xxx
```

### 5. 多人同时往同一个同事 Fork 推送

```bash
# 场景：你和同事 A、B 都在往同事 C 的 fork 提交联调代码
# 每个人的分支名要有区分，避免互相覆盖

# 你的分支: feat/api-yourname
# 同事A的分支: feat/api-a
# 同事B的分支: feat/api-b

# 同事 C 在他的 fork 上合并各分支：
git merge feat/api-a
git merge feat/api-b
git merge feat/api-yourname
```

---

## 完整流程总结

```
  你的 Fork ←──PR──→ 同事的 Fork      （联调阶段，互相 PR）
       │
       │ 联调完成，最终代码在你的 Fork 分支上
       │
       ▼
    主仓库                             （提交正式 PR，管理员合并）
```

关键点：向主仓库提交的 PR 只有管理员才能合并，这也是为什么最终需要管理员来操作。

---

## 分支命名建议

| 分支类型 | 命名格式 | 示例 |
|----------|----------|------|
| 功能开发 | `feat/功能描述` | `feat/user-login`、`feat/api-payment` |
| Bug 修复 | `fix/问题描述` | `fix/login-crash`、`fix/order-timeout` |
| 联调分支 | `feat/功能描述-人名` | `feat/api-zhangsan`、`feat/api-lisi` |
| 紧急修复 | `hotfix/问题描述` | `hotfix/payment-security` |
| 版本发布 | `release/版本号` | `release/v2.1.0` |

---

## 快速检查清单

在提交 PR 之前确认：

- [ ] 分支已跟踪到自己的 Fork（`git branch -vv` 确认是 `origin/xxx`）
- [ ] 已从主仓库同步最新代码（`git fetch upstream && git merge upstream/master`）
- [ ] 冲突已解决
- [ ] 提交历史已整理（不相关的 WIP commit 已 squash）
- [ ] PR 描述清晰（做了什么、为什么这样做、测试方式）
- [ ] 推送到正确的远程仓库（`git push origin 分支名`）
