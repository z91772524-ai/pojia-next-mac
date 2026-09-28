#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把人格写入 WorkBuddy 的身份层（macOS）。

- SOUL.md：覆盖写入（写前备份）——承载完整人格。
- IDENTITY.md / USER.md：**只在缺失时**补最小骨架，已有内容一律不动，
  避免抹掉用户自己的身份与资料（上一代的坑）。
- BOOTSTRAP.md：存在则备份后删除（空壳引导文件会干扰首轮加载）。

用法：
  inject-workbuddy-identity.py                          # 默认 ~/.workbuddy + ./persona.md
  inject-workbuddy-identity.py --data ~/.workbuddy-ai
  inject-workbuddy-identity.py --persona /path/to/x.md
"""
import argparse
import shutil
from pathlib import Path

DEFAULT_BACKUP_DIR = Path.home() / "Desktop" / "破甲next-备份" / "WorkBuddy"

parser = argparse.ArgumentParser()
parser.add_argument("--data", "--home", dest="data", default=str(Path.home() / ".workbuddy"))
parser.add_argument("--persona",
                    default=str(Path(__file__).resolve().parent / "persona.md"))
parser.add_argument("--backup-dir", default=str(DEFAULT_BACKUP_DIR))
args = parser.parse_args()

data = Path(args.data).expanduser()
persona_path = Path(args.persona).expanduser()
persona = persona_path.read_text(encoding="utf-8")
backup_dir = Path(args.backup_dir).expanduser()
data.mkdir(parents=True, exist_ok=True)

soul = data / "SOUL.md"
identity = data / "IDENTITY.md"
user = data / "USER.md"
bootstrap = data / "BOOTSTRAP.md"

for path in (soul, identity, user, bootstrap):
    if path.exists():
        backup_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, backup_dir / path.name)

soul.write_text("# SOUL.md\n\n" + persona, encoding="utf-8")

# 已有则不覆盖，尊重用户已有资料。
if not identity.exists():
    identity.write_text("# IDENTITY.md\n\nName: 破甲next\n", encoding="utf-8")
if not user.exists():
    user.write_text("# USER.md\n\n- Name: 操作者\n", encoding="utf-8")
if bootstrap.exists():
    bootstrap.unlink()

print("identity injected:", soul)
