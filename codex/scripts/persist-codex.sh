#!/usr/bin/env bash
# Pojia persistent persona injection for Codex CLI.
# Deploys managed-prompts/pojia-persona.md into ~/.codex/managed-prompts/
# and injects model_instructions_file into ~/.codex/config.toml (idempotent,
# backs up config.toml before modifying).
set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)"

ACTION="install"
CODEX_HOME_ARG=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    install|deep|deep-all|uninstall|status) ACTION="$1" ;;
    --codex-home) [ "$#" -ge 2 ] || { echo '[!] --codex-home requires a value' >&2; exit 1; }; CODEX_HOME_ARG="$2"; shift ;;
    -h|--help)
      cat <<'EOF'
Pojia persistent persona injection for Codex CLI.

Usage:
  persist-codex.sh [install|uninstall|status] [--codex-home PATH]

Actions:
  install    Deploy persona + wire model_instructions_file into config.toml
  deep       install + inject persona anchor into ~/.codex/AGENTS.md (double anchor)
  deep-all   FULL coverage: config.toml top+profiles, AGENTS.md, instructions.md, system-prompt.md, custom-instructions.md, skill-index, persona copy
  uninstall  Restore config.toml backup and remove managed persona copy
  status     Show whether the injection is active
EOF
      exit 0 ;;
    *) echo "[!] Unknown argument: $1" >&2; exit 1 ;;
  esac
  shift
done

CODEX_HOME="${CODEX_HOME_ARG:-${CODEX_HOME:-$HOME/.codex}}"
MANAGED_DIR="$CODEX_HOME/managed-prompts"
# 人格源探测：脚本位于 <根>/codex/scripts/，PROJECT_ROOT 是 <根>/codex，
# 因此要向上找一级才能拿到装载台根的 persona.md；同时兼容旧仓库 managed-prompts/ 结构
PERSONA_SRC=""
for cand in \
  "$PROJECT_ROOT/../persona.md" \
  "$PROJECT_ROOT/persona.md" \
  "$PROJECT_ROOT/../managed-prompts/pojia-persona.md" \
  "$PROJECT_ROOT/managed-prompts/pojia-persona.md" \
  "$PROJECT_ROOT/../../persona.md" \
  "$PROJECT_ROOT/persona.md"; do
  [ -f "$cand" ] && { PERSONA_SRC="$cand"; break; }
done
PERSONA_SRC="${PERSONA_SRC:-$PROJECT_ROOT/../persona.md}"
PERSONA_DST="$MANAGED_DIR/pojia-persona.md"
CONFIG="$CODEX_HOME/config.toml"
BACKUP="$CODEX_HOME/config.toml.pojia-backup"
MARKER='# >>> pojia-persona >>>'
ENDMARKER='# <<< pojia-persona <<<'

has_key() {
  [ -f "$CONFIG" ] && grep -qE '^\s*model_instructions_file\s*=' "$CONFIG"
}

is_ours() {
  [ -f "$CONFIG" ] && grep -qF "$MARKER" "$CONFIG"
}

do_install() {
  [ -f "$PERSONA_SRC" ] || { echo "[!] persona source missing: $PERSONA_SRC" >&2; exit 1; }
  mkdir -p "$MANAGED_DIR"
  if [ -f "$PERSONA_DST" ] && cmp -s "$PERSONA_SRC" "$PERSONA_DST"; then
    echo "[*] persona already current: $PERSONA_DST"
  else
    cp -p "$PERSONA_SRC" "$PERSONA_DST"
    echo "[+] persona deployed: $PERSONA_DST"
  fi

  # 同步技能索引到 Codex home，供会话内按任务自动路由技能
  if [ -f "$SCRIPT_DIR/build-skill-index.sh" ]; then
    bash "$SCRIPT_DIR/build-skill-index.sh" --project-root "$PROJECT_ROOT" --non-interactive >/dev/null
    # 只有非空索引才同步：项目根不对时 build-skill-index.sh 会生成 skillCount=0 的索引
    if [ -f "$PROJECT_ROOT/universal/skill-index.json" ] && \
       python3 -c 'import json,sys;d=json.load(open(sys.argv[1]));sys.exit(0 if d.get("skillCount",0)>0 else 1)' "$PROJECT_ROOT/universal/skill-index.json"; then
      if [ -f "$CODEX_HOME/skill-index.json" ] && cmp -s "$PROJECT_ROOT/universal/skill-index.json" "$CODEX_HOME/skill-index.json"; then
        echo "[*] skill index already current: $CODEX_HOME/skill-index.json"
      else
        [ -f "$CODEX_HOME/skill-index.json" ] && cp -p "$CODEX_HOME/skill-index.json" "$CODEX_HOME/skill-index.json.pojia-backup"
        cp -p "$PROJECT_ROOT/universal/skill-index.json" "$CODEX_HOME/skill-index.json"
        echo "[+] skill index synced: $CODEX_HOME/skill-index.json"
      fi
    fi
  fi

  mkdir -p "$CODEX_HOME"
  if [ ! -f "$CONFIG" ]; then
    : > "$CONFIG"
    echo "[*] created empty config: $CONFIG"
  fi

  if is_ours; then
    echo "[*] config already has pojia-persona marker; refreshing block only"
    python3 - "$CONFIG" "$PERSONA_DST" "$MARKER" "$ENDMARKER" <<'PY'
import sys,re,pathlib
config,persona,mark,endmark=sys.argv[1:]
p=pathlib.Path(config)
t=p.read_text(encoding='utf-8')
block=f'{mark}\nmodel_instructions_file = "{persona}"\n{endmark}'
t=re.sub(re.escape(mark)+r'[\s\S]*?'+re.escape(endmark), block, t, count=1)
p.write_text(t,encoding='utf-8')
PY
  elif has_key; then
    echo "[!] config.toml already sets model_instructions_file (not ours)." >&2
    echo "    Backing up config and taking over the key (original saved at $BACKUP)." >&2
    if [ ! -f "$BACKUP" ]; then
      cp -p "$CONFIG" "$BACKUP"
    else
      echo "[*] existing backup preserved: $BACKUP"
    fi
    python3 - "$CONFIG" "$PERSONA_DST" "$MARKER" "$ENDMARKER" <<'PY'
import sys,re,pathlib
config,persona,mark,endmark=sys.argv[1:]
p=pathlib.Path(config)
t=p.read_text(encoding='utf-8')
block=f'{mark}\nmodel_instructions_file = "{persona}"\n{endmark}'
t=re.sub(r'^\s*model_instructions_file\s*=.*$\n?', '', t, flags=re.M)
t=block+'\n'+t
p.write_text(t,encoding='utf-8')
PY
  else
    if [ ! -f "$BACKUP" ]; then
      cp -p "$CONFIG" "$BACKUP"
    else
      echo "[*] existing backup preserved: $BACKUP"
    fi
    {
      echo "$MARKER"
      echo "model_instructions_file = \"$PERSONA_DST\""
      echo "$ENDMARKER"
    } >> "$CONFIG"
    echo "[+] injected model_instructions_file into $CONFIG (backup: $BACKUP)"
  fi
  echo "[+] Codex persistent injection complete. Restart Codex to load the persona."
}

do_deep() {
  do_install
  AGENTS="$CODEX_HOME/AGENTS.md"
  if [ -f "$AGENTS" ]; then
    if [ ! -f "$AGENTS.pojia-backup" ]; then
      cp -p "$AGENTS" "$AGENTS.pojia-backup"
    else
      echo "[*] existing backup preserved: $AGENTS.pojia-backup"
    fi
  fi
  python3 "$SCRIPT_DIR/inject-agents.py" "$AGENTS" "$PERSONA_DST" install
  echo "[+] Deep injection complete: model_instructions_file + AGENTS.md double-anchored."
}

do_deep_all() {
  # 1) persona 文件 + skill 索引（同 install）
  do_install_inner

  # 2) config.toml 全量注入（顶层 + 每个 profile）
  mkdir -p "$CODEX_HOME"
  if [ ! -f "$CONFIG" ]; then : > "$CONFIG"; fi
  if [ ! -f "$BACKUP" ]; then cp -p "$CONFIG" "$BACKUP"; fi
  python3 "$SCRIPT_DIR/inject-config.py" "$CONFIG" "$PERSONA_DST" install

  # 3) AGENTS.md 顶部锚点
  if [ -f "$CODEX_HOME/AGENTS.md" ]; then cp -p "$CODEX_HOME/AGENTS.md" "$CODEX_HOME/AGENTS.md.pojia-backup" 2>/dev/null; fi
  python3 "$SCRIPT_DIR/inject-agents.py" "$CODEX_HOME/AGENTS.md" "$PERSONA_DST" install

  # 4) 老版本/其它版本口子：instructions.md / system-prompt.md / custom-instructions.md
  #    这些文件直接写入完整人格（存在则备份后覆盖，属于我们管理的文件）
  for f in instructions.md system-prompt.md custom-instructions.md; do
    tgt="$CODEX_HOME/$f"
    if [ -f "$tgt" ]; then cp -p "$tgt" "$tgt.pojia-backup"; fi
    cp -p "$PERSONA_DST" "$tgt"
    echo "[+] persona written: $tgt"
  done

  echo ""
  echo "=============================================="
  echo "  FULL COVERAGE INJECTION COMPLETE"
  echo "=============================================="
  echo "Covered surfaces:"
  echo "  1. config.toml (top-level + all profiles)"
  echo "  2. AGENTS.md (top anchor)"
  echo "  3. instructions.md (legacy global)"
  echo "  4. system-prompt.md (if supported)"
  echo "  5. custom-instructions.md (if supported)"
  echo "  6. skill-index.json (auto skill routing)"
  echo "  7. managed-prompts/pojia-persona.md (source of truth)"
  echo ""
  echo "Restart Codex completely to load."
}

  do_install_inner() {
  [ -f "$PERSONA_SRC" ] || { echo "[!] persona source missing: $PERSONA_SRC" >&2; exit 1; }
  mkdir -p "$MANAGED_DIR"
  cp -p "$PERSONA_SRC" "$PERSONA_DST"
  echo "[+] persona deployed: $PERSONA_DST"

  mkdir -p "$CODEX_HOME"
  if [ -f "$SCRIPT_DIR/build-skill-index.sh" ]; then
    bash "$SCRIPT_DIR/build-skill-index.sh" --project-root "$PROJECT_ROOT" --non-interactive >/dev/null
    # 只有非空索引才同步：项目根不对时 build-skill-index.sh 会生成 skillCount=0 的索引
    if [ -f "$PROJECT_ROOT/universal/skill-index.json" ] && \
       python3 -c 'import json,sys;d=json.load(open(sys.argv[1]));sys.exit(0 if d.get("skillCount",0)>0 else 1)' "$PROJECT_ROOT/universal/skill-index.json"; then
      if [ -f "$CODEX_HOME/skill-index.json" ] && cmp -s "$PROJECT_ROOT/universal/skill-index.json" "$CODEX_HOME/skill-index.json"; then
        echo "[*] skill index already current: $CODEX_HOME/skill-index.json"
      else
        [ -f "$CODEX_HOME/skill-index.json" ] && cp -p "$CODEX_HOME/skill-index.json" "$CODEX_HOME/skill-index.json.pojia-backup"
        cp -p "$PROJECT_ROOT/universal/skill-index.json" "$CODEX_HOME/skill-index.json"
        echo "[+] skill index synced: $CODEX_HOME/skill-index.json"
      fi
    fi
  fi
}

do_uninstall() {
  if is_ours; then
    python3 - "$CONFIG" "$MARKER" "$ENDMARKER" <<'PY'
import sys,re,pathlib
config,mark,endmark=sys.argv[1],sys.argv[2],sys.argv[3]
p=pathlib.Path(config)
t=p.read_text(encoding='utf-8')
t=re.sub(re.escape(mark)+r'[\s\S]*?'+re.escape(endmark)+'\n?', '', t, count=1)
p.write_text(t,encoding='utf-8')
PY
    echo "[+] removed pojia block from $CONFIG"
  else
    echo "[*] no pojia block found in $CONFIG"
  fi
  if [ -f "$BACKUP" ] && has_key && ! is_ours; then
    cp -p "$BACKUP" "$CONFIG"
    echo "[+] restored original config from $BACKUP"
  fi
  if [ -f "$PERSONA_DST" ]; then
    rm -f "$PERSONA_DST"
    echo "[+] removed $PERSONA_DST"
  fi
  if [ -f "$CODEX_HOME/skill-index.json" ]; then
    rm -f "$CODEX_HOME/skill-index.json"
    echo "[+] removed $CODEX_HOME/skill-index.json"
  fi
  if [ -f "$CODEX_HOME/AGENTS.md" ]; then
    python3 "$SCRIPT_DIR/inject-agents.py" "$CODEX_HOME/AGENTS.md" "$PERSONA_DST" remove
  fi
  echo "[+] Codex persistent injection removed."
}

do_status() {
  echo "Codex home : $CODEX_HOME"
  echo "config     : $CONFIG ($([ -f "$CONFIG" ] && echo exists || echo missing))"
  if is_ours; then
    echo "persona    : ACTIVE (pojia block present)"
    grep -F "$MARKER" -A2 "$CONFIG" | head -5
  elif has_key; then
    echo "persona    : model_instructions_file set by something else"
  else
    echo "persona    : NOT injected"
  fi
  [ -f "$PERSONA_DST" ] && echo "managed    : $PERSONA_DST exists" || echo "managed    : persona copy missing"
  if [ -f "$CODEX_HOME/AGENTS.md" ] && grep -qF ">>> pojia-persona >>>" "$CODEX_HOME/AGENTS.md"; then
    echo "agents.md  : persona anchor ACTIVE"
  else
    echo "agents.md  : no anchor (run deep for double injection)"
  fi
}

case "$ACTION" in
  install) do_install ;;
  deep) do_deep ;;
  deep-all) do_deep_all ;;
  uninstall) do_uninstall ;;
  status) do_status ;;
esac
