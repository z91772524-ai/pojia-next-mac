---
name: code-sentinel-engagement
description: >
  Code Sentinel 全量交战编排（原创）。覆盖目标目录契约校验、阶段链与并行包、
  端口服务枚举剧本、Web 预检蓝图、solutions 全局合并、报告门禁、范围一问一答、
  工具就绪探测。与 ops_ptes_lab / ops_phase_kb 联用。
  触发：engagement、交战、枚举剧本、web 预检、solutions 合并、范围访谈、
  bootstrap 渗透、全阶段链。
---

# Code Sentinel · Engagement Suite

```bash
python "$CODE_SENTINEL_HOME/scripts/ops_engagement.py" essences
python "$CODE_SENTINEL_HOME/scripts/ops_engagement.py" bootstrap <target>
python "$CODE_SENTINEL_HOME/scripts/ops_engagement.py" chain <target>
python "$CODE_SENTINEL_HOME/scripts/ops_engagement.py" enum-plan <host> --ports 22,80,443,445
python "$CODE_SENTINEL_HOME/scripts/ops_engagement.py" web-pretest <url>
python "$CODE_SENTINEL_HOME/scripts/ops_engagement.py" validate <target>
python "$CODE_SENTINEL_HOME/scripts/ops_engagement.py" report <target>
python "$CODE_SENTINEL_HOME/scripts/ops_engagement.py" solutions-merge
python "$CODE_SENTINEL_HOME/scripts/ops_engagement.py" scope-ask

# 真执行闭环
python "$CODE_SENTINEL_HOME/scripts/ops_phase_runner.py" run <target> --advance
python "$CODE_SENTINEL_HOME/scripts/ops_phase_runner.py" auto <target> --ports 22,80,443
python "$CODE_SENTINEL_HOME/scripts/ops_engagement.py" auto <target>
```

精髓表：`references/ops-engagement-atlas.md`  
阶段生命周期：`ops_ptes_lab` · 知识路由：`ops_phase_kb` · 执行器：`ops_phase_runner`
