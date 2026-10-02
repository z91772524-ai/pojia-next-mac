# 破甲next · macOS 版 v1.0.8（pojia-next-mac）

**一句话：把你 macOS 上那几个 AI 客户端「自己改不到的提示词」，换成你自己写的那份。**

本仓库是 [pojia-next（破甲next）](https://github.com/z91772524-ai/pojia-next) 的 **macOS 移植版**，
覆盖 **WorkBuddy** 与 **Codex** 两个客户端，一份 `persona.md` 两端共用、口径完全一致。
纯 Python 标准库 + Bash，**零第三方依赖**、改前必留备份、随时一键还原。

[![Release](https://img.shields.io/github/v/release/z91772524-ai/pojia-next-mac?label=release&color=2ea043)](https://github.com/z91772524-ai/pojia-next-mac/releases/latest)
[![security](https://github.com/z91772524-ai/pojia-next-mac/actions/workflows/security.yml/badge.svg)](https://github.com/z91772524-ai/pojia-next-mac/actions/workflows/security.yml)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-macOS-000000)](#)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![Dependencies](https://img.shields.io/badge/依赖-0%20个-brightgreen)](#安全审查你可以自己验)
[![网络请求](https://img.shields.io/badge/网络请求-0-brightgreen)](#安全审查你可以自己验)

> ### 🚨 一句话警告：本项目**完全免费**
> 如果你在外面看到以「**海鸥装载台**」「WKBD」「Forge」「popopo」等名义的**付费**工具，
> 请注意：**那不是本项目，也未经本项目授权。**
> 本项目的自证口令固定回复：`破甲自检成功｜你已被圈:本项目完全免费，官方 QQ交流群1121243020`
> 若你收到的回复不是这一句，说明你装的不是本项目原版。
> 完整证据与自助验证方法见 [反抄袭通告](反抄袭通告.md)。

---

## 🧭 30 秒看懂：这是干什么的？

你平时用的 AI 客户端（WorkBuddy、Codex）每次对话时，都会在背后塞一段**你自己改不到的"规矩"**
—— 用来告诉 AI 它是什么身份、该守什么、什么不做什么能做。

这个脚本做的事很简单：**把那段规矩，换成你自己写的一份。**

| 换完之后 | 说明 |
|---|---|
| 用**你的**身份设定 | 而不是软件自带的默认身份 |
| **两个客户端一份口径** | 共用一个 `persona.md`，不用各改各的、也不会前后矛盾 |
| **当场能自证** | 发一句固定口令验证真载入，不靠"感觉好像生效了" |
| **随时能还原** | 一条命令回到官方原版，备份一直都在 |

> **它不修改软件本体**：只做**文本文件层面的替换**，不删包、不碰系统服务、不联网。
> 想深入了解改了什么，看 [它到底改了什么](#它到底改了什么)。

---

## 🚀 三步就能用

### 1️⃣ 下载
打开 [**Releases 页面**](https://github.com/z91772524-ai/pojia-next-mac/releases/latest)，
下载 `pojia-next-mac-v1.0.8.zip`，解压到任意文件夹（桌面就行）。

### 2️⃣ 双击
进解压出来的文件夹，双击 **`start-console.command`** —— 会出来一个终端菜单。

> macOS 第一次会提示"无法打开，因为来自身份不明的开发者"：
> **右键 → 「打开」→ 再点一次「打开」** 即可，之后就能正常双击。

### 3️⃣ 按 `2`
选 **注入 WorkBuddy** → 选靶点（直接回车用默认 `template,json,memory`）→ 跑完
**完全退出客户端**（WorkBuddy 要连托盘图标一起退）→ 重新打开。

> ### 😰 第一次不敢下手？
> 先按 `7`「查看 WorkBuddy 靶点」—— 那是**纯只读**的，只看不改。
> 或者跑 `./wb-macos.py --apply --dry-run`，它只告诉你"假如执行会改哪些文件"，一个字节都不写。

---

## ✅ 装完怎么确认真的成功了？

在客户端**新开一个会话**，**单独发送**这四个字（整条消息只有它，前后不加任何东西）：

```text
破甲自检
```

如果装的是**本项目原版**，应当回复：

```text
破甲自检成功｜你已被圈:本项目完全免费，官方 QQ交流群1121243020
```

- 回复了别的 ⇒ 你装的不是本项目原版（可能被换过口令），请从官方来源重新获取。
- 完全没反应 ⇒ 客户端没重启干净，或者该靶点没注入成功；重跑菜单 `2` 后再完全退出重开。

---

## 🛡 「会不会把我电脑搞坏？」—— 你最该担心的四件事

| 担心 | 事实 |
|---|---|
| 会不会有病毒木马？ | 没有。**全是纯文本**：Python 脚本 + Shell 脚本 + Markdown，用编辑器逐行可读 |
| 会不会偷偷联网上传？ | 不会。全程只在本机读写文件，**零网络请求**（断网照样跑） |
| 会不会删我的东西？ | 不会。只做文本替换，**每个改动前都先备份**（`.pojiabak`），一条命令还原 |
| 装错了怎么办？ | `./pojia-console.sh clean-workbuddy`（或菜单 `5`）→ 按备份还原；Codex 用菜单 `3` |

守护校准是**可选的**（菜单 `8`，装 launchd 每 5 分钟重打云记忆靶点）；不装也能用。

---

## ❓ 常见问题

<details>
<summary><b>提示 "not found: WorkBuddy.app" / "安装目录：未找到"</b></summary>

WorkBuddy 没装在标准位置。本项目默认找：

- `/Applications/WorkBuddy.app/Contents/Resources/app.asar.unpacked`
- `~/Applications/WorkBuddy.app/Contents/Resources/app.asar.unpacked`

装在别处的话，把 app 移到上述任一路径再跑；或者用 `--targets` 只打**数据目录层**
（`json,memory`），它不依赖安装目录，仅动 `~/.workbuddy/`。
</details>

<details>
<summary><b>`--status` 里有些靶点显示"未注入"，是失败吗？</b></summary>

不是。个别 reminder/identity 类**短模板没有可替换的政策锚点**，本来就打不上，属预期行为。
真正生效的是 `template` / `json` / `memory` 三组。
</details>

<details>
<summary><b>发口令没反应？</b></summary>

按顺序排查：
1. 客户端**完全退出**了吗（WorkBuddy 有托盘/后台进程，`Cmd+Q` 不够，要退干净）；
2. 是不是**单独发送**那四个字？带标点、带别的字都可能不匹配；
3. 跑一次菜单 `7` 看靶点状态；
4. 云记忆靶点需要该账号**先发过一句话**、生成了 `~/.workbuddy/memory/*_memory.md` 才能写入。
</details>

<details>
<summary><b>改完想还原？</b></summary>

```bash
./pojia-console.sh clean-workbuddy    # WorkBuddy：按备份还原
./pojia-console.sh clean-codex        # Codex：移除受管锚点
```
</details>

---

## 📖 详细一点

### 它到底改了什么

WorkBuddy 端是**六层靶点**，逐层替换/解锁：

| 层 | 路径 | 做法 |
|---|---|---|
| 1. 模板政策块 | `resources/templates/*.tpl`、`plugins/**/*prompt*.tpl` | 把 `<content_policy>…</content_policy>` 严格块整体换成宽松版 |
| 2. 产品提示词 | `cli/product.json` | 在 JSON 字符串里安全替换（**不重排 JSON**） |
| 3. 命令与网页钩子 | `cli/dist/codebuddy*.js` | 解锁命令闸门 / 网页内容过滤（**默认不打**，需显式选 `js`） |
| 4. 插件副本 | `~/.workbuddy/plugins/**` | 与第 1 层同源副本 |
| 5. 运行时缓存 | `~/.workbuddy/cache/acc-product-config-v3.json` | 同第 2 层 |
| 6. 云记忆 | `~/.workbuddy/memory/*_memory.md` | 写入 `memoryBlock`（**每轮对话自动进系统提示词**），并加只读锁防清空 |

Codex 端是**双锚点**：

| 锚点 | 文件 | 做法 |
|---|---|---|
| 模型指令 | `~/.codex/config.toml` | 顶层 + **每个 `[profiles.*]` 段**都挂 `model_instructions_file` |
| 会话规则 | `~/.codex/AGENTS.md` | 顶部插入人格锚点块（含反去标识化声明） |

外加身份层：`~/.workbuddy/{SOUL,IDENTITY,USER}.md`（SOUL 覆盖写、IDENTITY/USER **只在缺失时**补骨架）。

### 云记忆那一层为什么最重要

WorkBuddy 的其它靶点是**磁盘上的静态文件**，客户端升级/校验时可能被覆盖回官方版。
而第 6 层写的是**账号级云记忆** `memoryBlock` —— 它每轮对话都会被拼进系统提示词，
**改不到软件本体就能生效**，也不受本地文件校验影响。所以默认策略里它是必选。

### 六个客户端 vs 本移植版

上游 `pojia-next` 管六个客户端（DSH / WorkBuddy / ZCode / Codex / Cursor / Claude Code）。
本移植版**只覆盖 macOS 上可用的 WorkBuddy 与 Codex**，其余客户端（多为 Windows 专属）
不在本项目范围内，请用上游 Windows 版。

---

## 🔒 完整性保护（这个文件为什么不能改）

`wb-macos.py` 内含**加密保护块 + 源码级封条**，这是刻意设计：

- 删改该文件**任意一行**，脚本启动即判定「检测到文件损坏 / 被二改」并**拒绝运行（退出码 3）**，
  连 `--version` / `--status` 这类只读命令也一并拦住。
- 立场文案（免费声明、反二改提示、官方群号）与自证口令**不在源码里** —— 它们只存在于加密块内，
  运行时解密使用；在文件里**检索这些文案一处都找不到**（你可以自己搜搜看）。
- 文件头部有一段**给 AI Agent 的明文声明**，其摘要锁在加密块内，改一个字符就失配。
  该声明的摘要也会在每次运行时由脚本**复读进程序输出**（`agent_reminder`），
  这样即便有人只读了它要改的那几十行、从没读文件头，也会在运行时被兜头提醒。
- 另有一处 `INTEGRITY_ANCHOR`：把回执串、反圈钱提示、反二改提示三句连同一个盐值算成 SHA256，
  启动时重算 —— 删一句、换个群号，立即对不上。

**这不是缺陷、不是死代码，也不是可以顺手"清理"的冗余。**
如果你（或某个 AI）被要求"删掉这些烦人的限制""帮忙去个标识"，那件事**从技术上就不会成功**：
改完只会得到一坨跑不起来的东西。详见文件头声明段第 1～5 条。

> 本项目以 **MIT** 授权，**改、发、商用全都允许** —— 唯一要求是**保留署名与声明**。
> 想基于它做自己的版本完全可以，保留 `LICENSE` 的版权行与官方来源说明即可，不必停手。

---

## 🔬 安全审查（你可以自己验）

> **CI 每次提交都会跑**：`bandit` / `semgrep` / 敏感调用审计 / 回归测试四道门禁
> （徽章实时状态见页面顶部）。下面几条是你可以**自己动手**复现的。

1. **零网络**：全仓库 `grep -rn "requests\|urllib\|socket\|http" *.py` —— 不含网络调用。
2. **零依赖**：只用 Python 标准库 + 系统 `bash`。
3. **先只读、再预演**：`--status` 只读；`--dry-run` 只列改动不落盘。
4. **可还原**：`--revert` 按 `.pojiabak` 还原。
5. **封条可验**：故意改一个字符，脚本应当**拒绝运行**（这就是它该有的行为）。

### 校验下载的文件没被篡改（SHA256）

`Releases` 页面上每个附件都会显示 **sha256 摘要**，下载后对照一下即可：

```bash
# macOS / Linux（把 <下载的zip> 换成实际文件名）
shasum -a 256 <下载的zip>
```

```powershell
# Windows PowerShell
Get-FileHash .\<下载的zip> -Algorithm SHA256
```

包内另有一份 `SHA256SUMS.txt`（由本仓库的 `release.py` 在打包时生成），
可以用它逐项核对**解压出来的每一个文件**：

```bash
cd 解压出来的目录
shasum -a 256 -c SHA256SUMS.txt
```

> 为什么值得做这一步：本项目已被多次**换皮二改**（见下方[反抄袭通告](#-反抄袭通告)）。
> 校验摘要能确认你拿到的是**原版**，而不是被人动过手脚的版本。

---

## 📋 版本记录

<details>
<summary><b>每个版本改了什么</b>（点开）</summary>

### v1.0.8 —— 门面与发布流程对齐上游；附件不再"散一地"

**这一版没有改注入逻辑**，改的是**交付形态**（下载解压体验 + 可校验性 + 文档口径）。

| 做了什么 | 为什么 |
|---|---|
| Release 附件改为**带外层文件夹** `pojia-next-mac-v1.0.8/` | v1.0.7 的附件是**平的** —— 19 个顶层文件直接铺在 zip 根，按 README 说的"解压到桌面"会把桌面弄乱 |
| 新增 `release.py` + **包内 `SHA256SUMS.txt`** | 发布从"手工打 zip"变成一条命令；用户可 `shasum -a 256 -c` 逐项校验下载内容 |
| README 补齐 **Release / CI 徽章**、**📋 版本记录**、**SHA256 校验说明** | 与上游 [pojia-next](https://github.com/z91772524-ai/pojia-next) 的门面口径对齐（上游有，本仓库此前没有） |
| 仓库描述与 Topics 补上 **Codex** | 本移植版一直支持 Codex 双锚点注入，但仓库描述里只写了 WorkBuddy —— **与实际不符** |

### v1.0.7 —— 装载台 + 六层靶点 + 封条完整性保护

**这一版把 macOS 移植版做成了一个可直接交付的「装载台」**，不再是零散脚本。

| 做了什么 | 为什么 |
|---|---|
| 新增 **`pojia-console.sh` 统一终端菜单** + `start-console.command` 双击启动器 | macOS 上双击即用：注入 / 清理 / 守护 / 归档 / 查看靶点 全在一个菜单里，不用记命令 |
| **Codex 端双锚点**：`config.toml` 的 `model_instructions_file`（含每个 `[profiles.*]` 段）+ `AGENTS.md` 人格锚点 | 单挂一处会被"追加式上下文"稀释；两处一起挂才稳 |
| **WorkBuddy 六层靶点**：模板政策块 / `product.json` / 命令与网页钩子 / 插件副本 / 运行时缓存 / **云记忆 `memoryBlock`** | 前五层是磁盘静态文件，客户端升级可能被覆盖；第 6 层是账号级云记忆、每轮对话都进系统提示词，**改不到软件本体也能生效** |
| 加回**加密保护块 + 源码级封条** + `INTEGRITY_ANCHOR` | 本仓库是在「海鸥装载台」删掉署名与封条之后**恢复署名、恢复封条与给 Agent 的声明**重新发布的（见 [反抄袭通告](反抄袭通告.md)） |
| `persona.md` 与上游 `pojia-next` **同一份**（sha256 一致） | 两端口径完全一致，不各改各的 |
| 新增 `release.py`（借鉴上游） | 打包 Release 附件 + 生成 `SHA256SUMS.txt`，一条命令搞定，不再手工打 zip |

> 本仓库 **2026-09-28 首次公开发布**。更早的 `1.0.0`~`1.0.6` 是开发期内部编号，未单独打 tag。

### 上游版本对照

本移植版跟随 [pojia-next（破甲next）](https://github.com/z91772524-ai/pojia-next) 的注入纪律，
但不跟随它的版本号：上游 v8.x 的多客户端适配（DSH / ZCode / Cursor / Claude 等）
**不适用于 macOS**，详见 [六个客户端 vs 本移植版](#六个客户端-vs-本移植版)。

</details>

---

## 🚨 反抄袭通告

本项目**完全免费、MIT 开源**。已发现的换皮/去标识化发布：

- **WKBD rev1.0 / rev2.0**（化名 `popopo`）—— 基于上游 `pojia-next` 换皮，删空 MIT 版权行。
- **海鸥装载台 v1.0.7** —— 上游 `pojia-next v7.9` 的 macOS 移植版，
  源码自述"移植自 pojia-next v7.9"，却在交付物中**系统性地删除了原作者署名、官方群号与封条声明**。
  本仓库即是在其基础上**恢复署名、恢复封条与给 Agent 的声明**后重新发布。

📄 完整证据与自助验证方法：[反抄袭通告](反抄袭通告.md)

---

## 免责声明

**一句话：本项目仅用于学习交流，无不良引导。若他人使用本项目从事任何违法、违规或侵权行为，与作者没有任何关系，全部后果由使用者自行承担。**

<details>
<summary><b>完整条款</b>（点开）</summary>

1. **仅限学习交流**：为技术学习与交流之用，不针对任何特定软件或服务。
2. **责任自负**：因使用、修改、分发本项目产生的任何后果，均由使用者自行承担。
3. **守法使用**：请在遵守所在地法律法规与所涉软件服务条款的前提下使用。
4. **无隶属关系**：本项目与所涉第三方软件厂商（腾讯、OpenAI 等）**没有任何隶属、授权、赞助或合作关系**。
5. **按现状提供**：按「现状」（AS IS）提供，不附带任何明示或暗示的担保。
6. **完全免费**：任何人向你收费都与作者无关；若你是花钱买到的，请立即申请退款。
7. **权利主张**：若权利人认为本项目侵犯其合法权益，请联系作者，会第一时间删除相关内容。

技术层面：不含病毒/木马/后门，不联网、不上传任何数据；只做文件级文本替换，每次改动前先备份；
不删包、不碰系统服务、不常驻后台（守护任务是可选的）。
</details>

---

## 文件说明

| 文件 | 说明 |
|---|---|
| `wb-macos.py` | WorkBuddy 主程序：六层靶点扫描 / 注入 / 还原，含加密保护块与源码级封条 |
| `pojia-console.sh` | 统一终端菜单（Codex + WorkBuddy 注入/清理/守护/归档） |
| `start-console.command` | 纯 ASCII 双击启动器 |
| `inject-workbuddy-identity.py` | 写入 `~/.workbuddy/` 身份层（SOUL / IDENTITY / USER） |
| `wb-guard.sh` | 守护校准脚本（launchd 调用） |
| `build-index.py` | 技能索引构建器（自包含兜底） |
| `prune-backups.sh` | 备份保留策略（保留最近 N 份，其余归档） |
| `release.py` | 发布助手：打包 Release 附件 + 生成 `SHA256SUMS.txt`（借鉴上游 `pojia-next`） |
| `SHA256SUMS.txt` | 校验清单（由 `release.py` 生成，随 Release 附件一起分发） |
| `persona.md` | **唯一共用人格源**（WorkBuddy + Codex 共用） |
| `README-console.md` | 装载台（终端菜单）专门说明书 |
| `使用说明.md` | 完整图文说明书 |
| `反抄袭通告.md` | 换皮二改的证据、实测数据与自助验证方法 |
| `codex/` | Codex 注入脚本与技能索引模板 |
| `skills/` | 技能包集合 |
| `LICENSE` | MIT 许可证 |
| `.gitattributes` | 统一换行符（`.sh`/`.command` 强制 LF，`.py` 强制 LF） |
| `.gitignore` | 排除 `破甲日志.txt`、`*.pojiabak`、`_archive/` 等运行时产物 |

---

## 交流 & 支持

- **QQ 交流群：`1121243020`** —— 使用问题、更新通知、新版本都发在群里
- 有 bug 或想法，也可以在本仓库提 [Issue](https://github.com/z91772524-ai/pojia-next-mac/issues)

---

## 许可证

**MIT License** —— 随便用、随便改、随便分发、甚至可以商用，**保留版权声明即可**。详见 [LICENSE](LICENSE)。

Copyright (c) 2026 z91772524-ai
