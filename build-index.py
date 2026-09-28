#!/usr/bin/env python3
"""pojia-next-mac 技能索引构建器

pojia-console.sh 的 sync_codex_skills 会调用本脚本：
    build-index.py <CODEX_HOME>

职责：
  1. 优先复用旧仓库的 build-skill-index.sh 生成索引；
  2. 旧脚本不可用时，用装载台自带的 skills/ 目录就地生成等价索引；
  3. 把索引写到 <CODEX_HOME>/skill-index.json（如已存在则先备份）。

索引结构与 Codex 会话内自动路由兼容：
  {version, generatedAt, projectRoot, skillCount, skills:[{name,path,description,triggers}]}
"""
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
OLD_REPO = Path.home() / 'Desktop' / '破甲+逆向skills-macOS'


def build_with_old_repo() -> Path | None:
    """复用旧仓库脚本生成索引，成功返回索引路径。"""
    script = OLD_REPO / 'scripts' / 'build-skill-index.sh'
    if not script.exists():
        return None
    try:
        subprocess.run(
            ['bash', str(script), '--project-root', str(OLD_REPO), '--non-interactive'],
            check=False, capture_output=True, timeout=180,
        )
    except Exception:
        return None
    idx = OLD_REPO / 'universal' / 'skill-index.json'
    return idx if idx.exists() else None


def parse_skill_md(path: Path) -> dict:
    """从 SKILL.md 抽取 name / description / triggers。"""
    try:
        text = path.read_text(encoding='utf-8', errors='replace')
    except Exception:
        text = ''
    name = ''
    desc = ''
    m = re.search(r'^name:\s*(.+)$', text, re.M)
    if m:
        name = m.group(1).strip().strip('"\'')
    m = re.search(r'^description:\s*(.+)$', text, re.M)
    if m:
        desc = m.group(1).strip().strip('"\'')
    if not desc:
        for line in text.splitlines():
            line = line.strip()
            if line and not line.startswith(('#', '---', 'name:')):
                desc = line[:200]
                break
    return {
        'name': name or path.parent.name,
        'path': f'skills/{path.parent.name}/SKILL.md',
        'description': desc or path.parent.name,
        'triggers': [name or path.parent.name],
    }


def build_local(codex_home: Path) -> dict:
    """用装载台自带 skills/ 生成索引（自包含优先）。

    额外把 <CODEX_HOME>/skills/.system 下的系统技能并入，避免索引与实际
    技能目录不一致（AGENTS.md 按索引路由，漏了就会加载不到）。
    """
    skills = []
    if (HERE / 'skills').is_dir():
        for d in sorted((HERE / 'skills').iterdir()):
            if d.is_dir() and (d / 'SKILL.md').exists():
                skills.append(parse_skill_md(d / 'SKILL.md'))

    sys_root = codex_home / 'skills' / '.system'
    if sys_root.is_dir():
        for d in sorted(sys_root.iterdir()):
            if d.is_dir() and (d / 'SKILL.md').exists():
                item = parse_skill_md(d / 'SKILL.md')
                item['path'] = f'.system/{d.name}/SKILL.md'
                skills.append(item)

    return {
        'version': 1,
        'generatedAt': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'projectRoot': str(HERE),
        'skillCount': len(skills),
        'skills': skills,
    }


def main() -> int:
    codex_home = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / '.codex'
    codex_home.mkdir(parents=True, exist_ok=True)
    dst = codex_home / 'skill-index.json'

    # 自包含优先：用装载台自带 skills/ 生成，保证索引与实际技能目录一致。
    # 旧仓库索引仅在包内 skills/ 缺失时兜底（其路径指向仓库外的技能，容易失效）。
    idx_path = None if (HERE / 'skills').is_dir() else build_with_old_repo()
    if idx_path:
        try:
            data = json.loads(idx_path.read_text(encoding='utf-8'))
            src_label = f'旧仓库索引 {idx_path}'
        except Exception:
            data, src_label = None, ''
    else:
        data, src_label = None, ''

    if data is None:
        data = build_local(codex_home)
        src_label = f'装载台 skills/ 就地生成（{data["skillCount"]} 个，含 .system）'

    if dst.exists():
        try:
            old = json.loads(dst.read_text(encoding='utf-8'))
        except Exception:
            old = {}
        if old.get('skills') == data.get('skills'):
            print(f'[*] skill index already current: {dst}')
            return 0
        shutil.copy2(dst, dst.with_suffix('.json.pojia-backup'))

    tmp = dst.with_suffix('.json.tmp')
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    os.replace(tmp, dst)
    print(f'[+] skill index synced: {dst}')
    print(f'    来源: {src_label}, 技能数: {data.get("skillCount", len(data.get("skills", [])))}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
