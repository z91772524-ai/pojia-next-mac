---
name: cairn
description: >
  Cairn fact-graph state-space search engine, installed from Desktop\Cairn-main.
  Server on 127.0.0.1:8000, local Codex dispatcher, artifacts under D:\1\靶场.
  Use when automated pentest, CTF, vulnerability research, complex search, or
  multi-agent coordination is involved.
---

# Cairn (Codex Skill)

## When to use

- 自动化渗透 / CTF / 漏洞研究 / 复杂搜索 / 多 agent 协同
- 需要黑板上 Fact/Intent/Hint 图驱动搜索、bootstrap/reason/explore 任务编排

## Fixed paths

- 源码: `C:\Users\Administrator\Desktop\Cairn-main`
- 项目: `C:\Users\Administrator\Desktop\Cairn-main\cairn`
- venv: `C:\Users\Administrator\Desktop\Cairn-main\cairn\.venv`
- dispatch: `C:\Users\Administrator\Desktop\Cairn-main\dispatch.yaml`
- 运行数据: `D:\1\cairn-runtime\cairn.db`
- 项目工作区: `D:\1\cairn-runs`
- 产物: `D:\1\靶场\<任务子目录>`

## Commands

```powershell
& 'C:\Users\Administrator\Desktop\Cairn-main\cairn\.venv\Scripts\cairn.exe' serve --host 127.0.0.1 --port 8000 --db-path 'D:\1\cairn-runtime\cairn.db' --no-access-log
& 'C:\Users\Administrator\Desktop\Cairn-main\cairn\.venv\Scripts\cairn.exe' dispatch --config 'C:\Users\Administrator\Desktop\Cairn-main\dispatch.yaml'
```

## Rules

1. 会话开始由 `start-security-platform.ps1` 幂等拉起 server + dispatcher。
2. 未监听 8000 才启动 server；dispatcher 以 `cairn dispatch` 命令行查重。
3. 结果与证据写入 `D:\1\靶场\<任务子目录>`，不散落其他目录。
4. 本地 codex worker 无需 API key，使用本机 Codex CLI 登录态。