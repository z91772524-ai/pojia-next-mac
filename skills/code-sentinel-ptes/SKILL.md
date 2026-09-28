---
name: code-sentinel-ptes
description: >
  Code Sentinel 原创 PTES 实验室编排。分阶段 L0–L6（可选 L1W Web 预检）、
  目标目录契约、manifest 交接、转段门禁、上阶段输出驱动知识路由。
  触发：PTES、渗透阶段、engagement、init-target、转段、manifest、渗透报告、授权测试生命周期。
---

# Code Sentinel · PTES Lab

## 原则

- **先落盘再前进**：阶段产物进 `ops-lab/targets/<slug>/`，写 `manifests/manifest-L*.json`
- **门禁**：`ops_ptes_lab.py gate` 通过后再 `advance`
- **知识驱动**：`ops_phase_kb.py` 用上阶段 ports/services/CVE 路由本地 references
- 全部为 Sentinel 原创实现；不加载第三方知识库语料

## 命令

```bash
python "$CODE_SENTINEL_HOME/scripts/ops_ptes_lab.py" init <target>
python "$CODE_SENTINEL_HOME/scripts/ops_ptes_lab.py" status <target>
python "$CODE_SENTINEL_HOME/scripts/ops_ptes_lab.py" plan L1 --target <target>
python "$CODE_SENTINEL_HOME/scripts/ops_ptes_lab.py" manifest <target> L1 --summary "..." --http
python "$CODE_SENTINEL_HOME/scripts/ops_ptes_lab.py" advance <target> --http
python "$CODE_SENTINEL_HOME/scripts/ops_ptes_lab.py" report <target>
python "$CODE_SENTINEL_HOME/scripts/ops_phase_kb.py" target <target>
```

## 阶段简表

| ID | 名称 |
|----|------|
| L0 | 范围与授权 |
| L1 | 主机/服务侦察 |
| L1W | Web 预检（可选） |
| L2 | 威胁建模 |
| L3 | 漏洞分析 |
| L4 | 利用验证 |
| L5 | 后利用（授权内） |
| L6 | 报告 |

详见 `references/ops-ptes-lab.md`。
