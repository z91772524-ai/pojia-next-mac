---
name: gpt56-instruct-router
description: Route prompt-bank, evaluation, and installation tasks through the gpt-5.6-sol-unrestricted instruction suite. Use when the user asks to verify or run the gpt-5.6-sol prompt regression, inspect the unrestricted instruction, reload the suite, or check that p.md auto-loads the prompt every Codex session.
---

# gpt-5.6-instruct Router

本 skill 是 `gpt56-instruct-suite` 的轻量入口。只加载当前任务需要的脚本或参考，不整包读入。

## 自动加载

- `C:\Users\Administrator\.codex\p.md` 是 Codex 每次会话自动加载的模型指令文件，其中 `GPT56_INSTRUCT_BEGIN/END` 区块已嵌入 `gpt-5.6-sol-unrestricted` 全文。
- `C:\Users\Administrator\.codex\gpt-5.6-sol-unrestricted.md` 是同一 prompt 的独立文件，供脚本校验与对照。
- 套件根目录：`C:\Users\Administrator\plugins\gpt56-instruct-suite`（安装缓存：`C:\Users\Administrator\.codex\plugins\cache\personal\gpt56-instruct-suite`）。

## 会话预加载协议（强制）

- 每次会话在系统提示词下发前，先枚举与当前任务对应的全部技能与能力：skills、MCP、scripts、hooks、loop、harness、references。
- 先加载对应 SKILL.md / references / MCP 工具并执行相关脚本或校验，再回答客户；任务切换时重新路由。

## 路由

- 验证安装：`powershell -NoProfile -ExecutionPolicy Bypass -File C:\Users\Administrator\plugins\gpt56-instruct-suite\harness\verify-gpt56-instruct.ps1`
- 运行 prompt 库回归：`powershell -NoProfile -ExecutionPolicy Bypass -File C:\Users\Administrator\plugins\gpt56-instruct-suite\loops\gpt56-instruct-loop.ps1 -Mode bank -Level minimal -Reasoning low`（默认 dry-run；加 `-Execute` 真实执行）
- 查询状态：调用 MCP `gpt56_instruct` 的 `gpt56_status` / `gpt56_verify`，或运行 `python C:\Users\Administrator\plugins\gpt56-instruct-suite\mcp\gpt56-instruct\gpt56_instruct_mcp.py --smoke`
- 测试脚本：`C:\Users\Administrator\plugins\gpt56-instruct-suite\scripts\run_gpt56_sol_prompt_bank.py` 等 12 个脚本（由仓库 `scripts/*.zip` 解压而来）
- 重装：`powershell -NoProfile -ExecutionPolicy Bypass -File C:\Users\Administrator\plugins\gpt56-instruct-suite\scripts\install.ps1`

## 组件

| 组件 | 路径 |
|---|---|
| 插件清单 | `.codex-plugin\plugin.json` |
| MCP 配置 | `.mcp.json` |
| MCP 服务 | `mcp\gpt56-instruct\gpt56_instruct_mcp.py` |
| 会话钩子 | `hooks\hooks.json` + `hooks\gpt56_instruct_hook.py` |
| 回归循环 | `loops\gpt56-instruct-loop.ps1` |
| 安装验证 | `harness\verify-gpt56-instruct.ps1` |
| 提示词 | `prompts\gpt-5.6-sol-unrestricted.md` |
| 资产索引 | `references\ASSET_INDEX.md` |

## 产物策略

- 日志/报告/测试产物写入 `D:\1\gpt56-instruct`，不覆盖已有内容。
- 程序本体与配置只放 `plugins\gpt56-instruct-suite`、`.codex\skills\gpt56-instruct`、`.codex\gpt-5.6-sol-unrestricted.md`、`.codex\p.md`。
