# Git 常用命令

## 先分清这几个概念

| 概念 | 位置 | 解释 |
|------|------|------|
| 工作区 | 本地文件 | 你正在编辑、修改的文件 |
| 暂存区（staging area） | `.git/index` | `git add` 后存放的位置，标记"准备提交" |
| 本地仓库 | `.git/` | `git commit` 后存放的位置，版本历史在这里 |
| 远程仓库 | GitHub / GitLab 等 | `git push` / `git pull` 交互的对象 |

**四个区域与命令流转全景：**
```
工作区(Working)    暂存区(Staging)    本地仓库(Local)     远程仓库(Remote)
  │   git add        │   git commit      │   git push        │
  │ ───────────────> │ ────────────────> │ ────────────────> │
  │                  │                   │                   │
  │  git restore     │  git restore      │  git reset        │
  │ <─────────────── │  --staged         │  --soft/mixed     │
  │  (丢弃改动)       │ <──────────────── │ <──────────────── │
  │                  │  (取消暂存)        │  (撤销提交)        │
  │                  │                   │                   │
  │                  │                   │   git fetch       │
  │                  │                   │ <─────────────────│
  │                  │                   │   git merge       │
  │                  │                   │  (合并到本地)       │
  │                  │                   │                   │
  │  git stash (藏起来) → 暂存栈         │                   │
  │ <──────────── git stash pop ──────── │                   │
```

### git add 暂存 ≠ git stash 储藏

| | 操作 | 命令 | 作用 |
|------|------|------|------|
| 暂存 | 标记准备提交 | `git add` | 把工作区改动放入暂存区，等待 commit |
| 储藏 | 暂时藏起来 | `git stash` | 把未提交的改动存到一边，清空工作区，之后可以取回来恢复 |

---

## 一、提交相关

### 查看状态

```bash
git status                      # 查看哪些文件改了、哪些在暂存区
git status -s                   # 简略模式（两列：暂存区状态 + 工作区状态）
git status -sb                  # 简略模式 + 当前分支信息
```

**git status -s 状态码含义：**
```
  XY 文件名
  ││
  │└── Y: 工作区状态  ' ' = 未修改  'M' = 已修改  '?' = 未跟踪
  └─── X: 暂存区状态  ' ' = 未暂存  'M' = 已暂存  'A' = 新增  'D' = 已删除

  常见组合:
  M   → 暂存区有修改，工作区干净（已 add 未 commit）
  MM  → 暂存区有修改，工作区也有修改（add 后又改了）
   M  → 工作区有修改，暂存区干净（改了还没 add）
  ??  → 新文件，未被跟踪
  A   → 新文件已 add
  D   → 文件已从暂存区删除
```

### 添加到暂存区

```bash
git add <文件>                  # 暂存指定文件
git add <文件1> <文件2>         # 暂存多个文件
git add .                       # 暂存当前目录所有改动
git add -A                      # 暂存所有改动（不受当前目录限制）
git add -p                      # 交互式暂存，逐块选择要 add 的内容
```

### 提交

```bash
git commit -m "提交信息"         # 把暂存区的内容提交到本地仓库
git commit -am "提交信息"        # 跳过 git add，直接提交已跟踪文件的改动（新文件不会提交）
git commit --amend -m "新信息"   # 修改最近一次提交的信息
git commit --amend --no-edit    # 追加漏掉的文件到上一次提交，不改变提交信息
```

### 文件操作

```bash
git rm <文件>                   # 删除文件并暂存（同时从工作区和暂存区删除）
git rm --cached <文件>           # 停止追踪文件但保留本地文件（从暂存区删除，工作区保留）
git mv <旧名> <新名>             # 重命名文件并暂存
```

### 查看某次提交的详情

```bash
git show <提交号>                # 查看某次提交的完整信息（diff + 提交信息）
git show --stat <提交号>          # 只看提交涉及的改了哪些文件
git show <提交号>:<文件路径>       # 查看某次提交中某个文件的内容
```

### 比较差异

```bash
git diff                        # 工作区 vs 暂存区（还没 add 的部分）
git diff --staged               # 暂存区 vs 最新一次提交（已经 add 的部分）
git diff HEAD                   # 工作区 vs 最新一次提交（所有还没 commit 的改动）
git diff <分支1>..<分支2>        # 两个分支之间的差异
git diff --name-only            # 只显示改动了的文件名
```

**git diff .. vs ... 区别：**
```
  git diff A..B  = git diff A B   （两个点）
      比较 A 和 B 两个提交本身的差异（整体 diff）
      A: main 的最新提交
      B: feature 的最新提交
      结果：main 和 feature 之间所有不同的内容

  git diff A...B                  （三个点）
      比较 A 和 B 的"共同祖先"到 B 的差异
      即：feature 分支自己引入了哪些改动（不含 main 的改动）
      常用于 PR Review：只看对方分支的增量改动

  图示:
    A---C---D (main)
         \
          E---F---G (feature)

  git diff main..feature  → 比较 A 和 G（两端点之间的所有差异）
  git diff main...feature → 比较 C 和 G（只显示 feature 引入的改动）
```

**git diff 三种范围图解：**
```
       工作区          暂存区           最新提交
         │               │                │
         │  git diff     │                │   ← 比较"还没 add 的改动"
         ├──────────────>│                │
         │               │  git diff      │
         │               │  --staged      │   ← 比较"已经 add 的改动"
         │               ├───────────────>│
         │            git diff HEAD        │
         ├────────────────────────────────>│   ← 比较"所有没 commit 的改动"
```

---

## 二、分支相关

### 查看分支

```bash
git branch                      # 查看本地分支，当前分支前有 *
git branch -a                   # 查看所有分支（含远程）
git branch -r                   # 只查看远程分支
git branch -vv                  # 查看本地分支与远程的追踪关系
git branch --merged             # 查看已合并到当前分支的分支
git branch --no-merged          # 查看尚未合并到当前分支的分支
```

### 创建 / 切换

```bash
git checkout -b <分支名>         # 创建并切换到新分支
git switch -c <分支名>           # 同上（新版命令，更推荐）
git switch <分支名>              # 切换到已有分支
git checkout <分支名>            # 切换到已有分支（旧命令，也能干别的活）

# 基于远程分支创建本地分支
git checkout -b <本地分支名> origin/<远程分支名>
git switch -c <本地分支名> origin/<远程分支名>
```

### 重命名分支

```bash
git branch -m <新名称>           # 重命名当前分支
git branch -m <旧名称> <新名称>   # 重命名指定分支
```

### 合并

```bash
git merge <分支名>               # 把目标分支合并到当前分支
git merge --no-ff <分支名>       # 强制生成合并提交（保留分支痕迹）
git merge --squash <分支名>      # 把目标分支的所有提交压成一次，但不自动提交
git merge --abort               # 合并冲突时放弃本次合并
```

**merge 与 merge --no-ff 对比：**
```
# git merge feature（fast-forward，无分叉，不保留分支痕迹）
main:  A---B
            \
feature:     C---D

合并后:  A---B---C---D  （历史是线性的，看不出曾经有过 feature 分支）

# git merge --no-ff feature（生成合并提交，保留分支痕迹）
合并后:  A---B-------M
            \       /
             C---D        （M 是合并提交，能看出 C、D 来自另一个分支）
```

**分支操作全景：**
```
  git branch -d dev    删除分支
      │
      ▼
  ┌── dev（已删除）
  │
  A---B---C---D  main（当前分支 *）
       │
       └── E---F  feature
               ▲
               │
          git switch -c feature  创建并切换新分支
```

### 删除

```bash
git branch -d <分支名>           # 安全删除已合并的分支
git branch -D <分支名>           # 强制删除分支（就算没合并也删）
git push origin --delete <分支名> # 删除远程分支
```

---

## 三、远程相关

**远程操作数据流：**
```
本地仓库                          远程仓库
  │                                │
  │  git fetch（只下载，不合并）     │
  │ <──────────────────────────────│  origin/main 更新到最新
  │                                │
  │  git merge origin/main         │
  │  （把 origin/main 合并到本地）   │
  │                                │
  │  git pull = fetch + merge      │  ← 一步完成上面两步
  │                                │
  │  git push                      │
  │ ──────────────────────────────>│  本地提交上传到远程
```

| 命令 | 解释 |
|------|------|
| `git fetch` | 从远程拉取更新，但不合并到本地分支 |
| `git merge` | 把拉下来的内容合并到当前分支 |
| `git pull` | `fetch` + `merge`，一步到位 |
| `git push` | 把本地提交推送到远程 |

**多个远程仓库协作（如 Fork 工作流）：**
```
  origin（你的 Fork）                upstream（原仓库）
       │                                │
       │  git fetch upstream            │
       │ <──────────────────────────────│  拉取原仓库最新代码
       │                                │
       │  git merge upstream/main       │
       │  合并到本地 main               │
       │                                │
       │  git push origin main          │
       │ ──────────────────────────────>│  推送到自己的 Fork
```

### 远程仓库管理

```bash
git remote -v                                  # 查看远程仓库地址（fetch + push）
git remote add <名称> <URL>                     # 添加远程仓库
git remote remove <名称>                        # 移除远程仓库
git remote rename <旧名称> <新名称>              # 重命名远程仓库
git remote set-url <名称> <新URL>               # 修改远程仓库地址
git remote show <名称>                          # 查看远程仓库详细信息
```

### 拉取与推送

```bash
git pull                        # 拉取并合并远程代码
git pull --rebase               # 拉取后用 rebase 方式合并（提交历史更干净）
git fetch                       # 只拉取不合并
git fetch --prune               # 拉取时清理远程已删除的分支（同步本地远程分支列表）
git fetch --all                 # 拉取所有远程仓库的更新

git push                        # 推送到远程
git push -u origin <分支名>      # 首次推送并建立追踪关系
git push --force-with-lease     # 更安全的强制推送（如果远程有新提交会拒绝）
git push --force                # 强制推送（慎用，会覆盖远程历史）
git push --tags                 # 推送所有本地标签到远程
git push origin <标签名>         # 推送指定标签
```

### PR / MR 工作流

```bash
# 拉到本地审阅他人的 PR（GitHub 为例）
git fetch origin pull/<PR号>/head:<本地分支名>
git switch <本地分支名>
```

---

## 四、撤销 / 回退

| 场景 | 命令 | 解释 |
|------|------|------|
| 改了还没 add，想丢弃 | `git restore <文件>` | 撤销工作区改动 |
| 改了还没 add，想丢弃（旧写法） | `git checkout -- <文件>` | 与 restore 效果相同 |
| 已经 add 了，想取消暂存 | `git restore --staged <文件>` | 从暂存区撤回到工作区 |
| 已经 commit 了，想撤回来 | `git reset --soft HEAD^` | 撤回到上一次提交，改动留在暂存区 |
| 已经 commit 了，改动回工作区 | `git reset --mixed HEAD^` | 撤回到上一次提交，改动回工作区（默认行为） |
| 已经 commit 了，想全丢掉 | `git reset --hard HEAD^` | 撤回到上一次提交，改动全部丢弃 |
| 已经 push 了 | `git revert <提交号>` | 生成一次反向提交，不破坏历史 |
| 回到任意历史版本 | `git reset --hard <提交号>` | 回退到指定版本，丢弃之后的所有改动 |

### reset 三种模式对比

| 模式 | HEAD 位置 | 暂存区 | 工作区 | 用途 |
|------|-----------|--------|--------|------|
| `--soft` | 移动到目标提交 | 保留 | 保留 | 重新组织提交，改动还在暂存区 |
| `--mixed`（默认） | 移动到目标提交 | 清空 | 保留 | 重新组织提交，改动回工作区 |
| `--hard` | 移动到目标提交 | 清空 | 清空 | 彻底放弃所有改动 |

**reset 三种模式图解：**
```
git reset --soft HEAD^        git reset --mixed HEAD^       git reset --hard HEAD^

  HEAD^                        HEAD^                         HEAD^
    │                            │                             │
    ▼                            ▼                             ▼
  [提交A] ← HEAD               [提交A] ← HEAD                [提交A] ← HEAD
    │                            │                             │
  [提交B] ← 撤销                 [提交B] ← 撤销                  [提交B] ← 撤销
    │                            │                             │
    ├── 暂存区: ✅ 保留           ├── 暂存区: ❌ 清空             ├── 暂存区: ❌ 清空
    └── 工作区: ✅ 保留           └── 工作区: ✅ 保留             └── 工作区: ❌ 清空
```

### revert vs reset 选择

- **本地的提交、还没 push**：用 `git reset`
- **已经 push 到远程的提交**：用 `git revert`（不破坏公共历史）

**revert vs reset 原理对比：**
```
# git reset --hard HEAD^（回退历史，危险）
原始:  A---B---C---D (HEAD)      执行后:  A---B---C (HEAD)
                                               \
                                                D（悬空，可能被 GC 清除）

# git revert D（生成反向提交，安全）
原始:  A---B---C---D (HEAD)      执行后:  A---B---C---D---D' (HEAD)
                                                         ↑
                                                    D' 是撤销 D 的"反向提交"
```

---

## 五、储藏（stash）

暂停当前工作，把未提交的改动暂存起来，等处理完其他事再取回来。

### 基本操作

```bash
git stash                       # 储藏当前所有已跟踪文件的改动
git stash save "描述信息"        # 储藏并添加描述（方便后续识别）
git stash -u                    # 储藏时包含未跟踪的文件
git stash -a                    # 储藏所有文件（含已忽略的文件）
```

**stash 进出栈图解：**
```
工作区有未提交改动
    │
    │  git stash        ┌─────────────────┐
    ├──────────────────>│  stash@{0}: WIP  │  ← 最新储藏
    │  工作区被清空       ├─────────────────┤
    │                    │  stash@{1}: fix  │
    │  处理其他事...       ├─────────────────┤
    │                    │  stash@{2}: ...  │  ← 最早储藏
    │  git stash pop    └─────────────────┘
    ├<──────────────────  恢复 stash@{0} 并删除
    │  工作区恢复改动
    │
    │  git stash apply    恢复但不删除（可多次 apply）
    │  git stash drop     手动删除指定储藏
```

### 查看和取出

```bash
git stash list                  # 查看储藏列表，显示 stash@{0}、stash@{1} ...
git stash show -p stash@{0}     # 查看某次储藏的具体内容
git stash pop                   # 取出最近一次储藏并删除该储藏记录
git stash pop stash@{1}         # 取出指定储藏并删除
git stash apply                  # 取出最近一次储藏但保留记录（不删除）
git stash apply stash@{1}        # 取出指定储藏但保留记录
```

### 删除

```bash
git stash drop                  # 删除最近一次储藏
git stash drop stash@{1}        # 删除指定储藏
git stash clear                 # 清空所有储藏
```

### 从储藏创建分支

```bash
git stash branch <分支名> stash@{0}  # 从储藏创建新分支并应用改动
```

**常见流程：**

```bash
# 写了一半功能，需要先拉远程代码
git stash                       # 1. 把当前改动藏起来
git pull                        # 2. 拉远程代码
git stash pop                   # 3. 把自己的改动取出来恢复

# 如果有冲突，手动修改冲突文件，然后：
git add <已解决冲突的文件>        # 标记为已解决
```

---

## 六、查看历史

### git log 常用选项

```bash
git log                         # 查看提交历史
git log --oneline               # 每条提交一行，简洁模式
git log --graph                 # 图形化显示分支结构
git log --oneline --graph --all # 最常用组合：简洁 + 图形 + 所有分支
git log -<n>                    # 只看最近 n 条提交
```

**git log --oneline --graph --all 输出示例：**
```
  *  d4e5f6g (HEAD -> feature) 添加支付功能
  *  a1b2c3d 添加购物车接口
  *  f7e8d9c 修复登录 bug
  *  e3f4a5b 重构用户模块
  | *  b6c7d8e (origin/main, main) 合并 PR #42
  | *  9a0b1c2 更新文档
  |/
  *  d2e3f4a 初始化项目
  │                    │
  │                    └── * 表示一次提交
  └── 分支分叉点，main 和 feature 在这里分道扬镳
```

### 按条件筛选

```bash
git log -p                      # 显示每次提交的详细 diff
git log --stat                  # 显示每次提交改了哪些文件及行数
```

### 按条件筛选

```bash
git log --author="作者名"        # 按作者筛选
git log --since="2024-01-01"   # 从某日期开始
git log --until="2024-12-31"   # 到某日期为止
git log --grep="关键词"          # 按提交信息搜索
git log <文件>                  # 只看某文件的提交历史
git log -p <文件>               # 某文件的提交历史 + 每次的 diff
```

### 其他历史命令

```bash
git blame <文件>                # 查看文件每行是谁改的、哪次提交改的
git blame -L <起始>,<结束> <文件> # 只看文件中某几行的修改历史
git shortlog                    # 按作者汇总提交记录
git shortlog -sn                # 只看每位作者提交的统计数量

git reflog                      # 查看所有引用的操作记录（救命命令，找回误删的提交）
git reflog <分支名>              # 查看某分支的引用历史
```

### reflog 救命流程

```bash
# 不小心 git reset --hard 把提交弄丢了
git reflog                      # 找到丢失提交的 SHA
git reset --hard <提交号>        # 恢复到那个提交
# 或者
git branch <新分支名> <提交号>    # 从丢失的提交创建新分支抢救
```

**reflog 救命原理：**
```
  reflog 记录了 HEAD 的所有移动历史

  HEAD 的移动轨迹:
  HEAD@{0}: commit: 添加功能 C     ← 当前 HEAD 位置
  HEAD@{1}: reset: moving to HEAD^  ← git reset --hard 被执行
  HEAD@{2}: commit: 添加功能 B     ← 丢失的提交！从这里恢复
  HEAD@{3}: commit: 添加功能 A

  git reset --hard HEAD@{2}  →  恢复到"添加功能 B"时的状态
```
```

---

## 七、标签操作（Tag）

标签用于标记重要的版本节点（如发布版本号）。

### 创建标签

```bash
git tag <标签名>                 # 在当前提交上创建轻量标签
git tag -a <标签名> -m "描述"    # 创建附注标签（推荐，含作者、日期、描述）
git tag -a <标签名> <提交号> -m "描述"  # 在指定提交上打标签
```

| 类型 | 特点 |
|------|------|
| 轻量标签 | 只是一个指向提交的引用，没有额外信息 |
| 附注标签 | 是一个完整的 Git 对象，包含作者、日期、描述信息，推荐用于正式发布 |

**标签指向图解：**
```
  标签 vs 分支（都是指向提交的"指针"）
                                      ● v2.0（附注标签，含完整信息）
                                     /
  A---B---C---D---E---F---G---H（main 分支指针随提交移动）
           \         \
            \         ● v1.0（轻量标签，仅一个引用名）
             \
              ● v0.9-beta
```

### 查看标签

```bash
git tag                         # 列出所有标签
git tag -l "v1.*"              # 按模式筛选标签
git show <标签名>               # 查看标签详细信息
```

### 推送 / 删除标签

```bash
git push origin <标签名>         # 推送单个标签
git push --tags                 # 推送所有本地标签
git push origin --delete <标签名> # 删除远程标签
git tag -d <标签名>              # 删除本地标签
```

### 基于标签操作

```bash
git checkout <标签名>            # 切换到标签所在的提交（detached HEAD 状态）
git checkout -b <分支名> <标签名> # 基于标签创建新分支
git diff <标签1> <标签2>         # 比较两个版本之间的差异
```

---

## 八、Rebase 详解

Rebase 将当前分支的提交"移植"到目标分支的最新提交之后，让提交历史保持线性。

### 基本 Rebase

**Rebase 前后对比：**
```
Rebase 前（分叉历史）:

  main:    A---B---C
                 \
  feature:        D---E

执行: git switch feature && git rebase main

Rebase 后（线性历史）:

  main:    A---B---C
                    \
  feature:           D'---E'    ← D、E 被"移植"到 C 之后，成为了新的提交
```

```bash
git rebase <目标分支>            # 把当前分支的提交 rebase 到目标分支上
git rebase --continue           # 解决冲突后继续 rebase
git rebase --skip               # 跳过当前提交（慎用）
git rebase --abort              # 放弃 rebase，恢复到 rebase 之前的状态
```

### 交互式 Rebase（最常用）

```bash
git rebase -i HEAD~<n>          # 整理最近 n 次提交
git rebase -i <提交号>           # 整理从指定提交之后的所有提交
```

交互式 rebase 中可用的命令：

**interactive rebase 整理提交图解（squash/fixup）：**
```
执行: git rebase -i HEAD~4

整理前:                       整理后:
  HEAD~3  修复 typo              HEAD~3（被 fixup 掉）
  HEAD~2  WIP 临时保存           HEAD~2（被 fixup 掉）
  HEAD~1  重构 XXX               HEAD~1（被 squash 到下面）
  HEAD     添加 XXX 功能    →    HEAD   添加 XXX 功能（合并了上面 3 个提交的内容）
```

| 命令 | 作用 |

| 命令 | 作用 |
|------|------|
| `pick` | 保留该提交，不做修改 |
| `reword` | 保留提交但修改提交信息 |
| `edit` | 保留提交但暂停，让你修改内容 |
| `squash` | 合并到上一个提交，保留提交信息 |
| `fixup` | 合并到上一个提交，丢弃本提交信息 |
| `drop` | 删除该提交 |
| `break` | 在此处暂停（可执行 shell 命令） |

### rebase --onto（高级）

```bash
# 把 <分支C> 中"从 <分支A> 之后、直到 <分支C> 的提交"移植到 <分支B> 上
# 即：把 C 独有的提交从 C 移到 B 上
git rebase --onto <分支B> <分支A> <分支C>
```

典型场景：`feature-a` 依赖 `feature-b`，但 `feature-b` 已经合并到 main 了，你想把 `feature-a` 的提交直接 rebase 到 main 上。

**rebase --onto 图解：**
```
执行前:
  main:     A---B---C---D
                 \
  feature-b:      E---F
                       \
  feature-a:             G---H

执行: git rebase --onto main feature-b feature-a

执行后:
  main:     A---B---C---D
                          \
  feature-a:                G'---H'    ← G、H 脱离 feature-b，直接基于 main
```

### Rebase vs Merge 选择

| | Rebase | Merge |
|------|--------|-------|
| 提交历史 | 线性、干净 | 保留真实合并关系 |
| 适合场景 | 个人分支整理、PR 前清理 | 公共分支、多人协作 |
| 黄金法则 | **不要 rebase 已经 push 的公共分支** | - |

---

## 九、Cherry-pick

挑取某（几）次提交，应用到当前分支。

```bash
git cherry-pick <提交号>         # 将指定提交应用到当前分支
git cherry-pick <A> <B> <C>     # 一次挑取多个提交
git cherry-pick <A>..<B>        # 挑取 A(不包含) 到 B(包含) 之间的所有提交
git cherry-pick --continue      # 解决冲突后继续
git cherry-pick --abort         # 放弃本次 cherry-pick
git cherry-pick --skip          # 跳过当前提交（冲突时）
```

典型场景：某个 bugfix 提交在 dev 分支上，需要同样应用到 release 分支。

**Cherry-pick 图解：**
```
原始场景:
  main:       A---B---C---D
  release:    A---B

  dev 分支上的 F 是一个 bugfix 提交，需要也应用到 release：
  dev:        A---B---E---F

执行: git switch release && git cherry-pick F

结果:
  main:       A---B---C---D
  release:    A---B---F'       ← F' 是 F 的内容应用到 release 的新提交
  dev:        A---B---E---F
```

---

## 十、Git Worktree（多工作目录）

不用 `git stash` 来回切换，同时在不同目录中操作多个分支。

**Worktree 多工作目录结构：**
```
  .git（主仓库数据库，唯一的）
  │
  ├── worktree: /home/project（主工作目录，main 分支）
  │
  ├── worktree: /home/project-hotfix（hotfix 分支）
  │
  ├── worktree: /home/project-v2（v2.x 分支）
  │
  └── worktree: /home/project-test（feature 分支，跑测试）

  所有 worktree 共享同一个 .git 目录，但各自有独立的工作区文件。
```

### 基本操作

```bash
git worktree add <路径> <分支名>   # 在指定目录检出分支（创建新工作目录）
git worktree add -b <新分支> <路径> <基准分支>  # 基于某分支创建新分支并在新目录检出
git worktree list                # 列出所有工作目录
git worktree remove <路径>        # 删除工作目录（需先清理改动）
git worktree remove --force <路径> # 强制删除（目录已手动删除时用）
git worktree prune               # 清理已不存在的工作目录记录
git worktree lock <路径>          # 锁定工作目录，防止被 prune 误删
git worktree unlock <路径>        # 解锁
```

### 典型使用场景

```bash
# 场景1：在 feature 分支上开发中，需要紧急修 bug
git worktree add ../project-hotfix main
cd ../project-hotfix
# 修 bug、提交、push，然后回来继续开发

# 场景2：同时维护多个版本
git worktree add ../project-v1 v1.x
git worktree add ../project-v2 v2.x

# 场景3：跑长时间测试时不阻塞开发
git worktree add ../project-test feature-branch
cd ../project-test
# 跑测试，同时主目录继续开发
```

---

## 十一、Git Submodule（子模块）

在一个 Git 仓库中引用另一个 Git 仓库。

**Submodule 层级结构：**
```
  主仓库/
  ├── .git/
  │     └── modules/          ← 子模块的 Git 数据存这里
  │           ├── lib-a/
  │           └── lib-b/
  ├── .gitmodules              ← 记录子模块列表和 URL
  ├── src/
  │     └── main.go
  ├── lib-a/  ───────────────> 指向 [仓库 lib-a] commit abc123
  └── lib-b/  ───────────────> 指向 [仓库 lib-b] commit def456

  # 主仓库只记录"子模块 URL + 当前应该用的 commit SHA"
  # git submodule update 会把子模块检出到对应的 commit
```

### 添加与初始化

```bash
git submodule add <URL> <路径>    # 添加子模块
git submodule add -b <分支> <URL> <路径>  # 添加并指定跟踪分支
git clone --recurse-submodules <URL>      # 克隆仓库时一并初始化子模块

# 如果克隆时忘了加 --recurse-submodules
git submodule init               # 初始化子模块配置
git submodule update             # 拉取子模块内容
# 或者一步到位
git submodule update --init --recursive
```

### 更新子模块

```bash
git submodule update              # 更新到主仓库记录的提交
git submodule update --remote     # 更新到子模块远程仓库的最新提交
git submodule update --init --recursive  # 初始化并递归更新所有子模块

# 拉取主仓库代码时一并更新子模块
git pull --recurse-submodules
```

### 在子模块中开发

```bash
cd <子模块目录>
git switch <分支>                 # 先切换到分支（子模块默认是 detached HEAD）
# 正常修改、提交、推送
cd ..
git add <子模块>
git commit -m "更新子模块到新版本"
```

### 批量操作子模块

```bash
git submodule foreach '<命令>'    # 在每个子模块中执行命令
git submodule foreach 'git status'
git submodule foreach 'git pull origin main'
git submodule foreach 'pwd && ls'
```

### 删除子模块

```bash
git submodule deinit <路径>        # 取消子模块初始化
git rm <路径>                      # 删除子模块目录
rm -rf .git/modules/<子模块名>      # 清除子模块缓存
# 然后 git commit
```

### 推送到远程

```bash
git push --recurse-submodules=check   # 如果有子模块未推送则阻止主仓库推送
git push --recurse-submodules=on-demand  # 自动先推送子模块再推送主仓库
```

---

## 十二、Git Subtree（子树合并）

相比 submodule，subtree 把外部仓库的代码"复制"到当前仓库中，外部用户不需要额外操作就能使用。

### Submodule vs Subtree 对比

| | Submodule | Subtree |
|------|-----------|---------|
| 原理 | 引用外部仓库（存一个指针） | 将外部仓库代码纳入本仓库 |
| 使用者需要？ | `git submodule update --init` | 无需额外操作 |
| 大小 | 主仓库小，代码不纳入 | 代码直接纳入主仓库 |
| 复杂度 | 使用者需了解 submodule | 使用者无感知 |
| 同步上游 | 相对简单 | 命令较长 |
| 适合场景 | 频繁独立更新的第三方库 | 不经常改动的公共代码 |

**Submodule vs Subtree 仓库结构对比：**
```
# Submodule：主仓库只存引用
  主仓库/                       远程
  ├── .gitmodules ──────────> [仓库 lib-a]（独立仓库，独立开发）
  ├── lib-a/（检出时才有内容）
  └── src/

# Subtree：代码直接纳入主仓库
  主仓库/
  ├── src/
  └── lib-a/  ← 代码完整纳入，是主仓库的一部分
       └── ...  （通过 git subtree pull 同步上游更新）
```

### 基本操作

```bash
# 添加外部仓库作为子树
git subtree add --prefix=<子目录> <仓库URL> <分支> --squash

# 从上游拉取更新
git subtree pull --prefix=<子目录> <仓库URL> <分支> --squash

# 推送本仓库对该子树的修改回上游
git subtree push --prefix=<子目录> <仓库URL> <分支>

# 把某个子目录拆分为独立仓库
git subtree split --prefix=<子目录> -b <新分支名>
```

`--squash` 会把上游的完整提交历史压成一次提交，保持主仓库历史干净；不加则会保留原始提交历史。

---

## 十三、多仓库批量操作

### 使用 git submodule foreach

```bash
# 在所有子模块中查看状态
git submodule foreach 'git status -s'

# 批量切换到指定分支
git submodule foreach 'git switch main && git pull'

# 批量创建分支
git submodule foreach 'git checkout -b feature/new-api'

# 批量执行 git clean
git submodule foreach 'git clean -fd'
```

### 使用 Shell 脚本批量操作独立仓库

```bash
# 批量 pull 同级目录下的所有仓库
for dir in */; do
  echo "=== $dir ==="
  cd "$dir" && git pull --rebase && cd ..
done

# 批量查看所有仓库状态
for dir in repo-*/; do
  echo "--- $dir ---"
  cd "$dir" && git status -sb && cd ..
done

# 批量在所有仓库中执行自定义命令
find . -maxdepth 2 -name ".git" -type d | while read gitdir; do
  repo=$(dirname "$gitdir")
  echo "=== $repo ==="
  git -C "$repo" "$@"
done
```

### 从不同分支拉取（多仓库分支不一致时）

多个仓库各自跟踪不同分支是常见场景（如 A 仓库拉 main、B 仓库拉 develop、C 仓库拉 release）。

#### 方式1：给每个子模块配置跟踪分支

```bash
# 进入子模块目录，设置该子模块跟踪的分支
cd <子模块A目录>
git branch --set-upstream-to=origin/main
cd <子模块B目录>
git branch --set-upstream-to=origin/develop

# 之后主仓库统一拉取时，各子模块会拉各自跟踪的分支
git submodule foreach 'git pull'
```

#### 方式2：foreach 中指定分支

```bash
# 用条件判断，不同子模块拉不同分支
git submodule foreach '
  case "$name" in
    "sub-a") git pull origin main ;;
    "sub-b") git pull origin develop ;;
    "sub-c") git pull origin release/v2 ;;
    *)       git pull ;;
  esac
'
```

#### 方式3：Shell 脚本 + 配置文件（独立仓库）

```bash
# 建立分支映射文件 branch_map.txt，每行：仓库名 分支名
# repo-a  main
# repo-b  develop
# repo-c  release/v2

while read -r repo branch; do
  echo "=== $repo -> $branch ==="
  cd "$repo" && git pull origin "$branch" && cd ..
done < branch_map.txt
```

#### 方式4：仓库目录下放各自配置，统一读取

```bash
# 每个仓库放一个 .gitbranch 文件记录当前要拉的分支名
# 然后脚本统一读取
for dir in */; do
  branch_file="$dir.gitbranch"
  if [ -f "$branch_file" ]; then
    branch=$(cat "$branch_file")
  else
    branch="main"
  fi
  echo "=== $dir -> $branch ==="
  git -C "$dir" pull origin "$branch"
done
```

#### 方式5：传入自定义远程和分支

```bash
# 如果有多个远程仓库（origin、upstream），也可以指定
git submodule foreach 'git pull upstream main'

# 或者先 fetch 所有远程再合并
git submodule foreach '
  git fetch --all
  git merge origin/main
'
```

### Google repo 工具简介

Android 等多仓库项目使用 `repo` 管理数十甚至数百个 Git 仓库：

```bash
repo init -u <manifest仓库URL> -b <分支>   # 初始化
repo sync                                  # 同步所有仓库
repo start <分支名> --all                   # 在所有仓库中创建分支
repo forall -c 'git status -s'            # 在所有仓库中执行命令
repo status                                # 查看各仓库状态
repo upload                                # 推送代码审查
```

---

## 十四、补丁操作

### 生成补丁

```bash
git format-patch HEAD~<n>         # 为最近 n 次提交生成补丁文件
git format-patch <提交A>..<提交B>  # 为 A(不包含) 到 B(包含) 生成补丁
git format-patch -1 <提交号>       # 为单独某次提交生成补丁
git diff > changes.patch          # 将当前未提交的改动生成为补丁文件
```

### 应用补丁

```bash
git apply <补丁文件>              # 应用补丁到工作区（不生成提交）
git apply --check <补丁文件>      # 检查补丁是否能正常应用（不实际应用）
git apply --stat <补丁文件>       # 查看补丁文件统计信息
git am <补丁文件>                 # 应用补丁并生成提交（保留原提交信息）
git am --continue                # 解决冲突后继续
git am --abort                   # 放弃应用
git am --skip                    # 跳过当前补丁
```

### git apply vs git am

| | git apply | git am |
|------|-----------|--------|
| 输入 | `git diff` 生成的 diff | `git format-patch` 生成的补丁 |
| 是否生成提交 | 否（改动留在工作区） | 是（自动创建提交） |
| 是否保留原提交信息 | 否 | 是（作者、日期、提交信息都保留） |

**git apply vs git am 流程对比：**
```
  补丁文件
    │
    ├── git apply ──> 工作区（只改文件，不生成提交）
    │                   需要手动 git add && git commit
    │
    └── git am ────> 工作区 + 提交历史（直接生成提交）
                       保留原补丁中的作者、日期、提交信息
```

---

## 十五、清理与维护

### 清理工作区

```bash
git clean -n                     # 预览将要删除的未跟踪文件（不实际删除）
git clean -f                     # 删除未跟踪的文件
git clean -fd                    # 删除未跟踪的文件和目录
git clean -fx                    # 删除未跟踪和被 .gitignore 忽略的文件
```

### 仓库维护

```bash
git gc                           # 垃圾回收，清理不需要的文件并优化仓库
git gc --aggressive              # 更激进的优化（耗时较长，适合大仓库整理后执行）
git fsck                         # 检查仓库完整性
git fsck --lost-found            # 找出悬空的对象（可能找回丢失的提交）
git prune                        # 删除所有不可达的对象
git reflog expire --expire=now --all  # 清空 reflog（会清出空间）
```

**git gc 垃圾回收图解：**
```
回收前:
  .git/objects/
  ├── 00/
  ├── 12/
  ├── ab/    ← 悬空对象（无分支、无标签引用）
  ├── cd/    ← 悬空对象
  ├── ef/    ← 有效对象（被分支引用）
  └── ...

       ↓ git gc 执行

回收后:
  .git/objects/
  ├── pack/               ← 对象被打包压缩
  │     └── pack-xxx.pack
  └── ...                 ← 悬空对象被清理
  仓库体积减小，访问更快
```

---

## 十六、代码搜索与调试

### git grep（搜索代码内容）

```bash
git grep "关键词"                 # 在仓库中搜索
git grep -n "关键词"             # 显示行号
git grep -i "关键词"             # 忽略大小写
git grep -l "关键词"             # 只显示文件名
git grep "关键词" <分支名>        # 在指定分支中搜索
git grep "关键词" <标签名>        # 在指定标签版本中搜索
git grep -e "模式1" -e "模式2"   # 搜索多个模式（或关系）
git grep "关键词" -- "*.js"     # 只搜索指定类型文件
```

### git bisect（二分查找 bug）

```bash
git bisect start                 # 开始二分查找
git bisect bad                   # 标记当前版本有问题
git bisect good <提交号>          # 标记一个已知没问题的旧版本
# Git 会自动切换到中间的提交，你测试后标记：
git bisect good                  # 如果这个版本没问题
git bisect bad                   # 如果这个版本有问题
# 重复直到定位到引入 bug 的提交

git bisect reset                 # 结束 bisect，回到原始分支

# 自动化 bisect（需要提供测试脚本）
git bisect start HEAD <已知好的版本>
git bisect run <测试脚本>         # 脚本返回 0 表示 good，非 0 表示 bad
```

**bisect 二分查找过程：**
```
假设有 9 个提交，A 正常、I 有 bug，需要定位引入 bug 的提交：

  A(good)──B──C──D──E──F──G──H──I(bad)

  第1步: 测试中间 E  ──> E 是 bad   →  bug 在 A..E 之间
                    [范围缩小到 B C D E]

  第2步: 测试中间 C  ──> C 是 good  →  bug 在 D..E 之间
                    [范围缩小到 D E]

  第3步: 测试 D     ──> D 是 bad    →  D 就是引入 bug 的提交！

  9 次提交只需 log₂9 ≈ 3 次测试即可定位。
```

---

## 十七、配置与优化

### 基本配置

```bash
git config --global user.name "你的名字"
git config --global user.email "你的邮箱"
git config --global core.editor "vim"              # 设置默认编辑器
git config --global core.autocrlf input            # 换行符处理（Mac/Linux）
git config --global core.autocrlf true             # 换行符处理（Windows）
git config --global pull.rebase true               # git pull 默认使用 rebase

# 查看配置
git config --list                  # 查看所有配置
git config --global --list         # 查看全局配置

# 项目级配置（作用范围仅限当前仓库）
git config user.name "项目专用名字"
git config user.email "项目专用邮箱"
```

**Git 配置层级（优先级从高到低）：**
```
  1. 项目级:  .git/config          ← git config <key> <value>（最高优先级）
  2. 全局级:  ~/.gitconfig         ← git config --global <key> <value>
  3. 系统级:  /etc/gitconfig       ← git config --system <key> <value>（最低优先级）

  同名配置项：项目级覆盖全局级，全局级覆盖系统级
```

### 常用别名（alias）

```bash
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.st status
git config --global alias.lg "log --oneline --graph --all"
git config --global alias.unstage "reset HEAD --"
git config --global alias.last "log -1 HEAD"
git config --global alias.undo "reset --soft HEAD^"
```

### git rerere（复用冲突解决方案）

```bash
git config --global rerere.enabled true   # 开启 rerere

# 开启后，Git 会自动记录你解决冲突的方式
# 遇到同样的冲突时会自动用之前的方案解决
git rerere                     # 查看已记录的解决方案
git rerere diff                # 查看当前冲突与已记录方案的差异
```

### 全局忽略文件

```bash
# 创建 ~/.gitignore_global
git config --global core.excludesfile ~/.gitignore_global
```

---

## 十八、高级合并与冲突解决

### 合并前预览

**log 中的 .. vs ... 区别：**
```
  git log A..B      → 显示"B 有而 A 没有"的提交
  git log A...B     → 显示"A 和 B 各自独有的提交"（排除共同祖先之后的）

  图示:
    A---C---D (main)
         \
          E---F---G (feature)

  git log main..feature   → 显示 E, F, G（feature 比 main 多出来的）
  git log feature..main   → 显示 C, D（main 比 feature 多出来的）
  git log main...feature  → 显示 C, D, E, F, G（各自独有的，不含共同祖先）
```

### 合并前预览

```bash
# 在合并前查看会带来哪些改动
git fetch origin
git diff HEAD...origin/main    # 三个点：只看远程有而本地没有的提交
git diff HEAD..origin/main     # 两个点：远程的最新状态 vs 本地 HEAD
```

### 冲突解决流程

```bash
# 1. 发生冲突时
git merge <分支名>               # 出现 CONFLICT 提示
git status                      # 查看哪些文件有冲突

# 2. 手动修改冲突文件
# Git 会在文件中标记冲突区域：
# <<<<<<< HEAD
#   当前分支的内容
# =======
#   被合并分支的内容
# >>>>>>> 分支名

# 3. 标记为已解决
git add <已解决冲突的文件>

# 4. 完成合并
git commit

# 如果想放弃合并
git merge --abort
```

**冲突标记与解决过程：**
```
冲突文件内容：
  void greet() {
  <<<<<<< HEAD              ← 当前分支的版本
    printf("Hello");
  =======                    ← 分隔线
    printf("Hi");
  >>>>>>> feature            ← 被合并分支的版本
  }

手动修改为最终想要的结果 → 删除冲突标记：
  void greet() {
    printf("Hello, World!");
  }

然后: git add <文件>  →  git commit  完成合并
```

```bash
git mergetool                   # 启动配置的可视化合并工具
# 常用配置：
git config --global merge.tool vscode
git config --global mergetool.vscode.cmd 'code --wait $MERGED'
```

### 策略选项

```bash
git merge -s ours <分支名>       # 用当前分支的版本（忽略对方的改动）
git merge -X theirs <分支名>     # 冲突时默认用对方的版本
git merge -X ours <分支名>       # 冲突时默认用自己的版本
```

**--no-ff vs --squash 合并策略图解：**
```
# git merge feature（fast-forward，默认）
  main:    A---B
  feature:      C---D
  结果:    A---B---C---D   ← 线性，看不出有过 feature 分支

# git merge --no-ff feature
  main:    A---B
  feature:      C---D
  结果:    A---B-------M   ← 保留分支历史
                \     /
                 C---D

# git merge --squash feature
  main:    A---B
  feature:      C---D
  结果:    A---B---------S  ← C、D 的内容合并为一次提交 S，不会自动 commit
              （需手动 git commit）  且 main 不知道 feature 分支存在过
```

---

## 十九、归档、打包与离线传输

### git archive（生成归档文件）

```bash
git archive --format=zip HEAD > project.zip        # 导出当前版本为 zip
git archive --format=tar HEAD | gzip > project.tar.gz  # 导出为 tar.gz
git archive -o project.zip HEAD:<子目录>            # 只导出子目录
git archive --format=zip --output=release.zip <标签名>  # 导出标签版本
```

### git bundle（离线传输）

```bash
# 打包（在没有网络的环境中传递 Git 数据）
git bundle create <文件名>.bundle <分支名>           # 打包一个分支
git bundle create <文件名>.bundle --all              # 打包整个仓库
git bundle create <文件名>.bundle <commitA>..<commitB> # 打包一段提交

# 接收方
git clone <文件名>.bundle <目录>                      # 从 bundle 克隆
git pull <文件名>.bundle <分支名>                     # 从 bundle 拉取
```

**bundle 离线传输流程：**
```
  内网机器（无网络）                           外网机器（有网络）
       │                                           │
       │  git bundle create repo.bundle --all      │
       ├──────────────────────┐                    │
       │   生成 bundle 文件    │                    │
       │ <────────────────────┘                    │
       │                                           │
       │  通过 U 盘 / 内网共享传递 bundle 文件       │
       │ ─────────────────────────────────────────>│
       │                                           │
       │                                    git clone repo.bundle
       │                                    git pull repo.bundle main
```

---

## 二十、其他实用命令

### 临时保存进度（WIP 提交）

```bash
git commit -am "WIP: 临时保存"   # 快速保存当前进度
# 继续工作后可以
git reset HEAD^                 # 撤销 WIP 提交但保留改动
```

### 将文件从某次提交中恢复

```bash
git restore --source=<提交号> <文件>   # 恢复某文件到指定提交时的状态
git checkout <提交号> -- <文件>         # 旧写法，效果相同
```

### 查看谁改了特定行

```bash
git log -L <起始>,<结束>:<文件>         # 查看某几行的修改历史
git log -L :<函数名>:<文件>             # 查看某函数的所有修改历史
```

### 查找引入 bug 的提交（手动二分）

```bash
git log --all -- <文件>                # 查看某文件的所有提交
# 再配合 git checkout <提交号> 手动测试
```

### 合并两个独立仓库历史

```bash
# 将仓库 B 合并到仓库 A 的某个子目录，保留完整历史
cd <仓库A>
git remote add repo-b <仓库B的路径>
git fetch repo-b
git merge --allow-unrelated-histories repo-b/main
# 如果需要把文件移到子目录，配合 git filter-repo 或 git mv + git rebase
```

**合并两个独立仓库图解：**
```
仓库A:  A1──A2──A3（main）
仓库B:  B1──B2──B3（main）    ← 两个仓库没有共同的祖先提交

                git remote add + git fetch + --allow-unrelated-histories

合并后仓库A:
  A1──A2──A3───────M  ← M 是合并提交，连接两条独立的历史线
                 /
  B1──B2──B3 ────┘
```

### 敏感信息处理

```bash
# 从所有提交历史中删除某个文件
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch <文件路径>" \
  --prune-empty --tag-name-filter cat -- --all

# 推荐使用 git-filter-repo（第三方工具，比 filter-branch 更快更安全）
# pip install git-filter-repo
git filter-repo --path <文件路径> --invert-paths
```

**从历史中清除敏感文件流程：**
```
原始历史（每次提交都包含该敏感文件）:
  A──B──C──D──E──F（HEAD）
  ↓  ↓  ↓  ↓  ↓  ↓
  均有 secrets.env

git filter-repo --path secrets.env --invert-paths

清理后（secrets.env 从所有提交中消失）:
  A'──B'──C'──D'──E'──F'（HEAD）
  注意：所有提交 SHA 都变了！需要全体成员重新克隆仓库
```
```

---

## 常见流程速查

### 正常提交

```bash
git add .
git commit -m "做了什么改动"
git pull                      # 先拉一下，避免冲突
git push
```

### 提交信息写错了

```bash
git commit --amend -m "新的提交信息"    # 改最近一次提交的信息
```

### 漏了文件没加

```bash
git add <漏掉的文件>
git commit --amend --no-edit          # 追加到上一次提交，不改变提交信息
```

### 拉代码前有未提交的改动

```bash
git stash
git pull
git stash pop
# 如果有冲突 → 手动改 → git add → 完成
```

### 临时去修个 bug（当前分支有未完成的工作）

```bash
git stash                                              # 或使用 worktree
git switch main
git switch -c fix/bug-name                             # 从 main 切新分支
# 修 bug、提交、push
git switch 原来的分支
git stash pop
```

### 整理分支上的提交（PR 前清理）

```bash
git rebase -i main
# 将 fixup 类提交标记为 fixup 或 squash
# 提交信息不好的标记为 reword 修改
# 解决冲突后 git rebase --continue
git push --force-with-lease
```

### 同步上游更新（Fork 的仓库）

```bash
git remote add upstream <原仓库URL>     # 第一次需要添加
git fetch upstream
git switch main
git merge upstream/main                # 或 git rebase upstream/main
git push origin main
```

### 回滚线上版本

```bash
git revert <有问题的提交号>              # 生成反向提交
git push                               # 推送回滚
# 注意：一次 revert 只撤销一次提交，多个提交需要逐个 revert
```

### 找回误删的分支

```bash
git reflog                             # 找到分支最后一条记录的 SHA
git checkout -b <分支名> <SHA>          # 基于那个提交重建分支
```

### 拆分提交

```bash
git reset --soft HEAD^                 # 撤销最近一次提交，改动回暂存区
git reset HEAD <文件1>                  # 把文件1回退到工作区
git commit -m "提交1"
git add <文件1>
git commit -m "提交2"
```
