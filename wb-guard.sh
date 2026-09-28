#!/usr/bin/env bash
# 守护校准：被 launchd（cn.pojia.workbuddy-guard）每 5 分钟调用一次。
# 装载台被移动或删除时不能空转刷错误 —— 缺依赖就安静退出并记一行日志。
set -uo pipefail

DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
DATA="${WORKBUDDY_DATA:-$HOME/.workbuddy}"
LOG="${DATA}/logs/pojia-guard.log"

for f in "$DIR/wb-macos.py" "$DIR/inject-workbuddy-identity.py" "$DIR/persona.md"; do
  if [ ! -f "$f" ]; then
    mkdir -p "$(dirname "$LOG")" 2>/dev/null
    printf '%s [guard] 缺少依赖 %s，跳过本次校准\n' "$(date '+%F %T')" "$f" >>"$LOG" 2>/dev/null
    exit 0
  fi
done

python3 "$DIR/wb-macos.py" --apply --targets memory >/dev/null 2>&1 || \
  printf '%s [guard] memory 靶点注入失败\n' "$(date '+%F %T')" >>"$LOG" 2>/dev/null
python3 "$DIR/inject-workbuddy-identity.py" --persona "$DIR/persona.md" >/dev/null 2>&1 || \
  printf '%s [guard] 身份层注入失败\n' "$(date '+%F %T')" >>"$LOG" 2>/dev/null
