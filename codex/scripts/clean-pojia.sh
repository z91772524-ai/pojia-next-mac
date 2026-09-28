#!/usr/bin/env bash
set -euo pipefail
ROOT="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
YES=0
PURGE_BACKUPS=0
for arg in "$@"; do
  case "$arg" in
    --yes) YES=1 ;;
    --purge-backups) PURGE_BACKUPS=1 ;;
    --dry-run) YES=0 ;;
    -h|--help) echo '用法: clean-pojia.sh [--dry-run] [--yes] [--purge-backups]' ; exit 0 ;;
  esac
done
TARGETS=()
while IFS= read -r -d '' f; do TARGETS+=("$f"); done < <(find "$ROOT" -type f \( -name '.DS_Store' -o -name '*.tmp' -o -name '*.log' -o -name '*.pyc' \) -print0)
while IFS= read -r -d '' d; do TARGETS+=("$d"); done < <(find "$ROOT" -type d -name '__pycache__' -print0)
if [ "$PURGE_BACKUPS" -eq 1 ]; then
  while IFS= read -r -d '' f; do TARGETS+=("$f"); done < <(find "$ROOT" "$CODEX_HOME" -maxdepth 3 -type f -name '*.pojia-backup*' -print0 2>/dev/null)
fi
if [ "${#TARGETS[@]}" -eq 0 ]; then echo '[*] 没有发现可清理的破甲临时文件。'; exit 0; fi
echo '[*] 将清理以下文件：'
printf '  %s\n' "${TARGETS[@]}"
if [ "$YES" -ne 1 ]; then
  echo '[*] 这是预览模式；确认执行请加 --yes，备份文件需额外加 --purge-backups。'
  exit 0
fi
for f in "${TARGETS[@]}"; do rm -f -- "$f"; done
while IFS= read -r -d '' d; do rm -rf -- "$d"; done < <(find "$ROOT" -type d -name '__pycache__' -print0)
echo "[+] 已清理 ${#TARGETS[@]} 个文件。"
