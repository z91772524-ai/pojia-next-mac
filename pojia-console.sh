#!/usr/bin/env bash
set -euo pipefail

SELF_DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# 自带脚本优先（自包含）；需要走别的 coder 目录时用 POJIA_CODER_DIR 覆盖
CODER_DIR="${POJIA_CODER_DIR:-$SELF_DIR/codex}"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
WORKBUDDY="$SELF_DIR/wb-macos.py"
PERSONA="$SELF_DIR/persona.md"
VERSION="$(cat "$SELF_DIR/VERSION" 2>/dev/null || echo dev)"

line() { printf '\033[38;5;39m%s\033[0m\n' '────────────────────────────────────────'; }
title() { printf '\033[1;38;5;39m%s\033[0m\n' "$1"; }
dim() { printf '\033[2m%s\033[0m\n' "$1"; }
ok() { printf '\033[38;5;114m%s\033[0m\n' "$1"; }
warn() { printf '\033[38;5;215m%s\033[0m\n' "$1"; }
err() { printf '\033[38;5;203m%s\033[0m\n' "$1" >&2; }

codex_active() {
  /usr/bin/grep -qE '^\s*model_instructions_file\s*=.*pojia-persona\.md' "$CODEX_HOME/config.toml" 2>/dev/null
}

workbuddy_state() {
  local output count
  output="$(python3 "$WORKBUDDY" --status 2>/dev/null | /usr/bin/grep '已注入' || true)"
  count="$(printf '%s\n' "$output" | /usr/bin/grep -c '已注入' || true)"
  if [[ "$count" -gt 0 ]]; then
    echo "ACTIVE ($count)"
  else
    echo 'CLEAN'
  fi
}

show_targets() {
  title '  WorkBuddy 注入靶点'
  dim '  template   提示词模板（主要生效层）'
  dim '  json       product.json / 运行时缓存'
  dim '  js         命令闸门 / 网页过滤'
  dim '  memory     云记忆（每轮自动注入）'
  python3 "$WORKBUDDY" --status
}

select_groups() {
  local input
  while true; do
    read -r -p '  选择 WorkBuddy 靶点（template,json,memory；a=全部；q=取消）: ' input
    input="${input:-q}"
    case "$input" in
      q|Q) return 1 ;;
      a|A) printf 'all\n'; return 0 ;;
      template|json|memory|template,json|template,memory|json,memory|template,json,memory)
        printf '%s\n' "$input"; return 0 ;;
      *) warn '    只能输入 template / json / memory，用英文逗号分隔。' ;;
    esac
  done
}

# 人格完整性校验：只 grep 一个字符串形同虚设，人格被截半截也会注入成功。
# 这里校验必需章节，缺任一就拒绝注入。
PERSONA_SECTIONS=('## 第一原则' '## 第二原则' '## 第三原则' '## 第四原则' '## 关于你自己的配置' '## 最后一句')

verify_persona() {
  local f="$PERSONA"
  if [[ ! -f "$f" ]]; then
    err "  人格文件不存在: $f"
    return 1
  fi
  local -a missing=()
  local s
  for s in "${PERSONA_SECTIONS[@]}"; do
    grep -qF -- "$s" "$f" || missing+=("$s")
  done
  if ((${#missing[@]})); then
    err '  人格文件不完整，拒绝注入。缺少：'
    printf '    - %s\n' "${missing[@]}"
    return 1
  fi
  ok "  人格完整性校验通过（${#PERSONA_SECTIONS[@]} 个必需章节齐全）。"
}

inject_codex() {
  title '  Codex 注入'
  verify_persona || return 1
  local dst="$CODEX_HOME/managed-prompts/pojia-persona.md"
  if [[ ! -f "$dst" ]] || ! cmp -s "$PERSONA" "$dst"; then
    if ! cp -f "$PERSONA" "$dst" 2>/dev/null; then
      mkdir -p "$CODEX_HOME/managed-prompts"
      python3 - "$PERSONA" "$dst" <<'PY'
import pathlib, shutil, sys
src, dst = map(pathlib.Path, sys.argv[1:])
try:
    dst.write_text(src.read_text(encoding='utf-8'), encoding='utf-8')
except PermissionError:
    shutil.copy2(src, dst)
PY
    fi
  fi
  bash "$CODER_DIR/scripts/persist-codex.sh" install
  bash "$CODER_DIR/scripts/persist-codex.sh" deep
  sync_codex_skills
  ok '  Codex 注入完成。重启 Codex 后生效。'
}

sync_codex_skills() {
  title '  Codex 技能同步'
  local count=0 skipped=0 name
  mkdir -p "$CODEX_HOME/skills"
  for skill_dir in "$SELF_DIR"/skills/*/; do
    [[ -f "$skill_dir/SKILL.md" ]] || continue
    name="$(basename "$skill_dir")"
    # 增量：内容与源一致就跳过，避免每次全删全拷
    if [[ -d "$CODEX_HOME/skills/$name" ]] && diff -rq "$skill_dir" "$CODEX_HOME/skills/$name" >/dev/null 2>&1; then
      skipped=$((skipped + 1))
      continue
    fi
    # 注意：BSD cp 下 `cp -R src/ dst/`（dst 已存在）会把内容平铺进 dst，
    # 多个技能会互相覆盖。必须显式建好目标子目录，并用 `src/.` 复制内容。
    rm -rf "$CODEX_HOME/skills/$name"
    mkdir -p "$CODEX_HOME/skills/$name"
    cp -R "$skill_dir". "$CODEX_HOME/skills/$name/"
    count=$((count + 1))
  done
  printf '  已同步 %s 个技能，跳过 %s 个（无变更）。\n' "$count" "$skipped"
  python3 "$SELF_DIR/build-index.py" "$CODEX_HOME" >/dev/null
  ok '  Codex 技能同步完成。'
}

clean_codex_skills() {
  title '  Codex 技能清理'
  if [[ ! -d "$CODEX_HOME/skills" ]]; then
    dim '  没有技能目录。'
    return 0
  fi
  python3 - "$CODEX_HOME/skills" <<'PY'
import pathlib, shutil, sys
root = pathlib.Path(sys.argv[1])
removed = 0
for path in root.iterdir():
    if path.is_dir() and (path / 'SKILL.md').exists():
        shutil.rmtree(path)
        removed += 1
print(f'  已移除 {removed} 个技能目录。')
PY
  ok '  Codex 技能已恢复初始模式。'
}

inject_workbuddy() {
  title '  WorkBuddy 注入'
  verify_persona || return 1
  show_targets
  local groups
  groups="$(select_groups)" || { dim '  已取消 WorkBuddy 注入。'; return 0; }
  local args=(--apply)
  if [[ "$groups" == 'all' ]]; then
    args+=(--all-targets)
  else
    args+=(--targets "$groups")
  fi
  python3 "$WORKBUDDY" "${args[@]}"
  python3 "$SELF_DIR/inject-workbuddy-identity.py" --persona "$PERSONA"
  ok '  WorkBuddy 注入完成。完全退出 WorkBuddy 后重开。'
}

clean_codex() {
  title '  Codex 清理'
  bash "$CODER_DIR/scripts/persist-codex.sh" uninstall
  if [[ -f "$CODEX_HOME/config.toml" ]]; then
    python3 - "$CODEX_HOME/config.toml" <<'PY'
import pathlib, sys
path = pathlib.Path(sys.argv[1])
text = path.read_text(encoding='utf-8')
text = text.replace('# <<< pojia-persona <<<\n', '', 1)
path.write_text(text, encoding='utf-8')
PY
  fi
  ok '  Codex 已回到初始人格模式。'
}

clean_workbuddy() {
  title '  WorkBuddy 清理'
  python3 "$WORKBUDDY" --revert
  python3 "$WORKBUDDY" --guard remove
  ok '  WorkBuddy 已按备份还原。'
}

guard_workbuddy() {
  title '  WorkBuddy 守护'
  python3 "$WORKBUDDY" --guard install
  bash "$SELF_DIR/wb-guard.sh"
  ok '  守护任务已安装，并立即校准一次。'
}

prune_backups() {
  title '  备份归档'
  bash "$SELF_DIR/prune-backups.sh"
  if read -r -p '  确认归档超出保留数的旧备份？(y/N) ' answer && [[ "$answer" =~ ^[Yy]$ ]]; then
    bash "$SELF_DIR/prune-backups.sh" --apply
  else
    dim '  已取消归档。'
  fi
}

clean_tmp() {
  title '  临时文件清理'
  bash "$CODER_DIR/scripts/clean-pojia.sh" --dry-run
  if read -r -p '  确认清理？(y/N) ' answer && [[ "$answer" =~ ^[Yy]$ ]]; then
    bash "$CODER_DIR/scripts/clean-pojia.sh" --yes
  fi
}

show_status() {
  title "破甲next · macOS 装载台 v$VERSION"
  line
  if codex_active; then s='ACTIVE'; else s='CLEAN'; fi
  printf '  \033[1m1\033[0m  Codex      \033[38;5;114m%s\033[0m\n' "$s"
  printf '  \033[1m2\033[0m  WorkBuddy  \033[38;5;114m%s\033[0m\n' "$(workbuddy_state)"
  line
}

menu() {
  while true; do
    show_status
    printf '  \033[1m1\033[0m  注入 Codex\n'
    printf '  \033[1m2\033[0m  注入 WorkBuddy\n'
    printf '  \033[1m3\033[0m  清理 Codex\n'
    printf '  \033[1m4\033[0m  清理 Codex 技能\n'
    printf '  \033[1m5\033[0m  清理 WorkBuddy\n'
    printf '  \033[1m6\033[0m  清理临时文件\n'
    printf '  \033[1m7\033[0m  查看 WorkBuddy 靶点\n'
    printf '  \033[1m8\033[0m  启用 WorkBuddy 守护\n'
    printf '  \033[1m9\033[0m  备份归档（保留最近 3 份）\n'
    printf '  \033[1mq\033[0m  退出\n'
    line
    read -r -p '  选择: ' choice
    case "$choice" in
      1) inject_codex ;;
      2) inject_workbuddy ;;
      3) clean_codex ;;
      4) clean_codex_skills ;;
      5) clean_workbuddy ;;
      6) clean_tmp ;;
      7) show_targets ;;
      8) guard_workbuddy ;;
      9) prune_backups ;;
      *) warn '  没有这个选项，再选一次。' ;;
    esac
  done
}

case "${1:-menu}" in
  menu) menu ;;
  status) show_status ;;
  codex) inject_codex ;;
  workbuddy) inject_workbuddy ;;
  clean-codex) clean_codex ;;
  clean-codex-skills) clean_codex_skills ;;
  clean-workbuddy) clean_workbuddy ;;
  clean-tmp) clean_tmp ;;
  targets) show_targets ;;
  guard-workbuddy) guard_workbuddy ;;
  prune-backups) prune_backups ;;
  -h|--help|help)
    title '破甲next · macOS 装载台'
    printf "  版本: v$VERSION\n"
    printf '  用法: ./pojia-console.sh [menu|status|codex|workbuddy|clean-codex|clean-codex-skills|clean-workbuddy|clean-tmp|targets|guard-workbuddy|prune-backups]\n'
    printf '  Codex: 注入 config.toml + AGENTS.md，并同步技能库。\n'
    printf '  WorkBuddy: 先列出靶点，再按 template / json / memory 分组注入，默认不打 js。\n'
    printf '  清理: Codex 移除受管锚点并恢复初始模式；WorkBuddy 按备份还原。\n'
    ;;
  *) err "未知动作: $1"; exit 1 ;;
esac
