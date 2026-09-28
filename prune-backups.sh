#!/usr/bin/env bash
# pojia-next-mac 备份保留策略
#
# 备份目录只会增长，这里按时间保留最近 N 份，其余移到归档目录（不直接删除，可回滚）。
#
# 用法:
#   prune-backups.sh                 预演：列出将要归档的旧备份，不动作
#   prune-backups.sh --apply         真正归档
#   prune-backups.sh --keep 5        保留最近 5 份（默认 3）
#   prune-backups.sh --dir PATH      指定备份根目录
set -uo pipefail

KEEP=3
APPLY=0
BACKUP_ROOT="${HOME}/Desktop/pojia-next-mac/pojia-backups"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --apply) APPLY=1 ;;
    --keep) [ "$#" -ge 2 ] || { echo '[!] --keep 需要一个数字' >&2; exit 1; }; KEEP="$2"; shift ;;
    --dir) [ "$#" -ge 2 ] || { echo '[!] --dir 需要一个路径' >&2; exit 1; }; BACKUP_ROOT="$2"; shift ;;
    -h|--help)
      sed -n '2,14p' "$0" | sed 's/^# \{0,1\}//'
      exit 0 ;;
    *) echo "[!] 未知参数: $1" >&2; exit 1 ;;
  esac
  shift
done

if [ ! -d "$BACKUP_ROOT" ]; then
  echo "[*] 备份目录不存在: $BACKUP_ROOT（无需清理）"
  exit 0
fi

# 只清理带时间戳的备份目录，不动固定名称的（如 WorkBuddy）
# macOS 自带 bash 3.2 没有 mapfile，用 while read；ls -t 按修改时间倒序（比字典序准）
DIRS=()
while IFS= read -r d; do
  [ -n "$d" ] && DIRS+=("$d")
done < <(ls -1t "$BACKUP_ROOT" 2>/dev/null | while IFS= read -r n; do
  [ -d "$BACKUP_ROOT/$n" ] && [ "$n" != '_archive' ] && [ "$n" != 'WorkBuddy' ] && printf '%s\n' "$n"
done)

TOTAL=${#DIRS[@]}
if [ "$TOTAL" -le "$KEEP" ]; then
  echo "[*] 备份 ${TOTAL} 份，未超过保留数 ${KEEP}，无需清理。"
  exit 0
fi

echo "备份目录: $BACKUP_ROOT"
echo "共 ${TOTAL} 份，保留最近 ${KEEP} 份。"
echo
echo "保留:"
i=0
for d in "${DIRS[@]}"; do
  i=$((i + 1))
  [ "$i" -le "$KEEP" ] && echo "  [keep] $d"
done
echo
echo "将归档:"

if [ "$APPLY" -eq 1 ]; then
  STAMP="$(date +%Y%m%d-%H%M%S)"
  ARCHIVE="$BACKUP_ROOT/_archive/$STAMP"
  mkdir -p "$ARCHIVE"
fi

i=0
MOVED=0
for d in "${DIRS[@]}"; do
  i=$((i + 1))
  [ "$i" -le "$KEEP" ] && continue
  echo "  [old ] $d"
  if [ "$APPLY" -eq 1 ]; then
    if mv "$BACKUP_ROOT/$d" "$ARCHIVE/" 2>/dev/null; then
      MOVED=$((MOVED + 1))
    else
      echo "    [!] 归档失败: $d"
    fi
  fi
done

if [ "$APPLY" -eq 1 ]; then
  echo
  echo "[+] 已归档 ${MOVED} 份 → ${ARCHIVE}"
  echo "    归档内容不会被自动删除，确认无用后可自行清理。"
else
  echo
  echo "[*] 预演结束，未改动任何文件。加 --apply 执行归档。"
fi
