#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)"
UNIVERSAL_ROOT="$PROJECT_ROOT/universal"
PROJECT_ROOT_ARG=""
JSON_PATH_ARG=""
MARKDOWN_PATH_ARG=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --project-root|-p) [ "$#" -ge 2 ] || { echo '[!] --project-root requires a value' >&2; exit 1; }; PROJECT_ROOT_ARG="$2"; shift ;;
    --json-path) [ "$#" -ge 2 ] || { echo '[!] --json-path requires a value' >&2; exit 1; }; JSON_PATH_ARG="$2"; shift ;;
    --markdown-path) [ "$#" -ge 2 ] || { echo '[!] --markdown-path requires a value' >&2; exit 1; }; MARKDOWN_PATH_ARG="$2"; shift ;;
    --non-interactive|-n) ;;
    -h|--help) echo 'Usage: build-skill-index.sh [--project-root PATH] [--json-path PATH] [--markdown-path PATH]'; exit 0 ;;
    *) echo "[!] Unknown argument: $1" >&2; exit 1 ;;
  esac
  shift
done
[ -n "$PROJECT_ROOT_ARG" ] || PROJECT_ROOT_ARG="$PROJECT_ROOT"
PROJECT_ROOT="$(CDPATH= cd -P -- "$PROJECT_ROOT_ARG" && pwd)"
[ -n "$JSON_PATH_ARG" ] || JSON_PATH_ARG="$UNIVERSAL_ROOT/skill-index.json"
[ -n "$MARKDOWN_PATH_ARG" ] || MARKDOWN_PATH_ARG="$UNIVERSAL_ROOT/skill-index.md"
mkdir -p "$(dirname -- "$JSON_PATH_ARG")" "$(dirname -- "$MARKDOWN_PATH_ARG")"
command -v python3 >/dev/null 2>&1 || { echo '[!] python3 is required' >&2; exit 1; }
NOW="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
python3 - "$PROJECT_ROOT" "$JSON_PATH_ARG" "$MARKDOWN_PATH_ARG" "$NOW" <<'PY'
import json,re,sys,pathlib
project_root=pathlib.Path(sys.argv[1]).resolve()
json_out=pathlib.Path(sys.argv[2])
md_out=pathlib.Path(sys.argv[3])
now=sys.argv[4]
def fm(lines):
    if not lines or lines[0].strip()!='---': return []
    for i in range(1,len(lines)):
        if lines[i].strip()=='---': return lines[1:i]
    return []
def scalar(lines,key):
    p=re.compile(rf'^{re.escape(key)}:\s*(.*)$')
    for l in lines:
        m=p.match(l)
        if m: return m.group(1).strip().strip('"').strip("'")
    return ''
def desc(lines):
    v=scalar(lines,'description')
    if v and v not in ('|','>'): return v
    started=False; out=[]
    for l in lines:
        if not started and l.startswith('#'): started=True; continue
        if not started: continue
        if not l.strip():
            if out: break
            continue
        out.append(l.strip())
    return ' '.join(out).strip()
def triggers(lines):
    vals=[]; active=False
    for l in lines:
        if re.match(r'^triggers:\s*$',l): active=True; continue
        m=re.match(r'^\s+-\s+(.+)$',l)
        if active and m: vals.append(m.group(1).strip().strip('"').strip("'")); continue
        if active and not l.startswith(' '): active=False
    return vals
skills=[]
for f in sorted(project_root.rglob('SKILL.md')):
    text=f.read_text(encoding='utf-8',errors='replace').splitlines(); front=fm(text)
    skills.append({'name':scalar(front,'name') or f.parent.name,'path':f.relative_to(project_root).as_posix(),'description':desc(front),'triggers':triggers(front),'size':f.stat().st_size,'lastWriteTime':int(f.stat().st_mtime)})
json_out.write_text(json.dumps({'version':1,'generatedAt':now,'projectRoot':str(project_root),'skillCount':len(skills),'skills':skills},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rows=['# Pojia skill index','','Generated: '+now,'Skill count: '+str(len(skills)),'','| Name | Path | Triggers | Description |','|---|---|---|---|']
for s in skills:
    d=str(s['description']).replace('|','\\|').replace('\n',' ')
    t=', '.join(str(x).replace('|','\\|') for x in s['triggers'])
    rows.append(f"| {s['name']} | `{s['path']}` | {t} | {d} |")
md_out.write_text('\n'.join(rows)+'\n',encoding='utf-8')
PY
echo "[+] Skill index: $JSON_PATH_ARG"
echo "[+] Skill count: $(python3 -c 'import json,sys; print(json.load(open(sys.argv[1],encoding="utf-8"))["skillCount"])' "$JSON_PATH_ARG")"
