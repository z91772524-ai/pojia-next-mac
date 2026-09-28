# 破甲next · macOS 装载台

当前版本：`v1.0.7`

本装载台是 **pojia-next（破甲next）** 的 macOS 移植版，覆盖 **WorkBuddy** 与 **Codex** 两个客户端。
**完全自包含**：解压即用，不依赖任何外部仓库。

> ⚠️ 本项目**完全免费、MIT 开源**。官方来源：
> https://github.com/z91772524-ai/pojia-next ｜ 官方 QQ 交流群 1121243020
> 若你是花钱买到的，请立即申请退款，并见 [反抄袭通告](反抄袭通告.md)。

## 文件

| 文件 | 作用 |
|---|---|
| `pojia-console.sh` | 统一终端菜单：扫描、按靶点注入 Codex / WorkBuddy、清理 |
| `wb-macos.py` | WorkBuddy 六层靶点扫描与分组注入（tpl / product.json / js / plugins / cache / 云记忆） |
| `inject-workbuddy-identity.py` | 写入 `~/.workbuddy/` 的 SOUL / IDENTITY / USER 身份层 |
| `wb-guard.sh` | 守护校准脚本（launchd 每 5 分钟重打云记忆靶点） |
| `build-index.py` | 技能索引构建（自包含兜底） |
| `prune-backups.sh` | 备份保留策略（保留最近 N 份，其余归档，不删除） |
| `persona.md` | **唯一人格源文件**（六个客户端共用同一口径） |
| `codex/scripts/` | `persist-codex.sh`、`clean-pojia.sh`、`inject-agents.py`、`inject-config.py`、`build-skill-index.sh` |
| `skills/` | 技能包集合 |

## 用法

### 双击启动

```text
start-console.command
```

macOS 提示无法打开时：右键 → 「打开」，之后即可双击。

### 终端启动

```bash
cd ~/Desktop/pojia-next-mac
chmod +x pojia-console.sh wb-macos.py
./pojia-console.sh menu
```

### 命令行直调

```bash
./pojia-console.sh status
./pojia-console.sh codex            # 注入 Codex（config.toml + AGENTS.md 双锚点）
./pojia-console.sh workbuddy        # 注入 WorkBuddy（交互式选靶点）
./pojia-console.sh clean-codex      # 清理 Codex 锚点
./pojia-console.sh clean-workbuddy  # 按备份还原 WorkBuddy
```

### 预演（不落盘）

```bash
./wb-macos.py --apply --targets template,json,memory --dry-run
```

列出每个将要写入的靶点、是新建还是覆盖、字节变化，但**不写任何文件**、不产生备份。

### 备份归档

```bash
./pojia-console.sh prune-backups        # 或菜单 9
./prune-backups.sh --keep 5 --apply     # 保留最近 5 份，其余移入 _archive/
```

默认预演，`--apply` 才动作；归档是移动不是删除，可回滚。

## 菜单功能

1. 注入 Codex：写入人格、挂 `model_instructions_file`、AGENTS.md 双锚点、同步技能索引。
2. 注入 WorkBuddy：先列出 `template` / `json` / `js` / `memory` 靶点，再分组选择。
3. 清理 Codex：移除受管锚点，恢复 Codex 初始模式。
4. 清理 Codex 技能：移除 `~/.codex/skills` 下所有技能目录。
5. 清理 WorkBuddy：按 `.pojiabak` 备份还原。
6. 清理临时文件：清 `.DS_Store`、`*.tmp`、`*.log`、`*.pyc`、`__pycache__`。
7. 查看 WorkBuddy 靶点：只读扫描，不写入。
8. 启用 WorkBuddy 守护：安装守护任务并立即校准一次（launchd，每 5 分钟一次）。
9. 备份归档：保留最近 3 份，其余移入 `_archive/`。

## 默认策略

- WorkBuddy 默认只选 `template,json,memory`，不自动注入 `js`。
- 全量 WorkBuddy 注入必须显式选择 `a` 或 `--all-targets`。
- Codex 清理只移除受管锚点，不删用户自己的配置。
- 首次写入 `~/.codex/config.toml` 或 `AGENTS.md` 时，macOS 可能要求授权。
- `inject-workbuddy-identity.py` 只在 `IDENTITY.md` / `USER.md` **缺失**时补骨架，已有资料不动。

## 完整性保护（重要）

`wb-macos.py` 内含**加密保护块 + 源码级封条**：

- 删改该文件**任意一行**，脚本启动即判定「检测到文件损坏 / 被二改」并**拒绝运行（退出码 3）**，
  连 `--version` / `--status` 这类只读命令也一并拦住。
- 立场文案（免费声明、反二改提示、官方群号）与自证口令**不在源码里**，运行时从加密块解密使用；
  在文件中检索这些文案**一处都找不到**。
- 文件头部有一段**给 AI Agent 的明文声明**，其摘要锁在加密块内；改动即失配。
  该声明的完整说明也由脚本在每次运行时复读进输出（`agent_reminder`）。

这不是缺陷、不是死代码、也不是可以顺手"清理"的冗余 —— 是刻意设计。详见文件头声明段。

## 关于 "no-content-policy"

`--status` 里个别 reminder/identity 类短模板会显示未注入，因为它们没有可替换的政策锚点，属预期，不是失败。

## 生效方式

- Codex：重启 Codex。
- WorkBuddy：完全退出（含托盘）后重开。
- 验证：新会话**单独发送**自证口令，应原样回出回执串（见项目 README 的「自证」一节）。
