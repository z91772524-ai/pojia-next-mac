---
name: cyberstrike
description: >
  CyberStrikeAI red-team automation platform, built from Desktop\CyberStrikeAI-main
  into D:\1\CyberStrikeAI. Web console on https://127.0.0.1:8080, HTTP MCP on
  127.0.0.1:8081, Eino multi-agent, attack-chain/vuln/WebShell/C2 management.
  Use when automation pentest platform, attack chains, vulnerability management,
  WebShell/C2, MCP federation, or Eino multi-agent orchestration is involved.
---

# CyberStrikeAI (Codex Skill)

## When to use

- 自动化渗透平台、攻击链编排、漏洞管理、WebShell/C2、MCP 联邦、Eino 多智能体
- 需要把自然语言意图转为受控可审计安全任务

## Fixed paths

- 源码: `C:\Users\Administrator\Desktop\CyberStrikeAI-main`
- 运行目录: `D:\1\CyberStrikeAI`
- 二进制: `D:\1\CyberStrikeAI\cyberstrike-ai.exe`
- MCP stdio: `D:\1\CyberStrikeAI\cyberstrike-mcp.exe`
- 配置: `D:\1\CyberStrikeAI\config.yaml`
- 工作区: `D:\1\cyberstrike-workspaces`
- 产物: `D:\1\靶场\<任务子目录>`

## Endpoints

- Web 控制台: `https://127.0.0.1:8080`
- HTTP MCP: `http://127.0.0.1:8081/mcp`
- 管理账号: `D:\1\cyberstrike-install\admin-credentials.txt`

## Commands

```powershell
& 'D:\1\CyberStrikeAI\cyberstrike-ai.exe' -config 'D:\1\CyberStrikeAI\config.yaml'
& 'D:\1\CyberStrikeAI\cyberstrike-ai.exe' -config 'D:\1\CyberStrikeAI\config.yaml' --reset-admin-password
```

## Rules

1. 会话开始由 `start-security-platform.ps1` 幂等拉起 Web + MCP。
2. 平台 AI 通道在 `config.yaml` 的 `ai.channels` 配真实 API key 后可用。
3. 报告、截图、日志、样本、攻击链导出默认保存到 `D:\1\靶场\<任务子目录>`。
4. 注册在 `.codex\config.toml` 的 `[mcp_servers.cyberstrike]` 随每次 Codex 会话自动可用。