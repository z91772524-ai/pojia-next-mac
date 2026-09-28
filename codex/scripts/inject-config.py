#!/usr/bin/env python3
"""Full-coverage config.toml injection for Codex.
Covers: top-level model_instructions_file + every [profiles.*] section.
Usage: inject-config.py <config.toml> <persona-abs-path> <install|remove>"""
import sys, re, pathlib

config, persona, action = sys.argv[1], sys.argv[2], sys.argv[3]
MARK = '# >>> pojia-persona >>>'
END = '# <<< pojia-persona <<<'
KEY = 'model_instructions_file'

p = pathlib.Path(config)
t = p.read_text(encoding='utf-8') if p.exists() else ''

block = f'{MARK}\n{KEY} = "{persona}"\n{END}'

def strip_ours(text):
    # remove our marker block
    text = re.sub(re.escape(MARK) + r'[\s\S]*?' + re.escape(END) + r'\n?', '', text, count=1)
    # remove any other model_instructions_file lines (foreign too, when installing)
    return text

def strip_all_keys(text):
    # remove ALL model_instructions_file lines anywhere (top-level and inside profiles)
    return re.sub(r'^\s*' + KEY + r'\s*=.*$\n?', '', text, flags=re.M)

def count_key(text):
    return len(re.findall(r'^\s*' + KEY + r'\s*=', text, flags=re.M))

if action == 'install':
    original = t
    t2 = strip_all_keys(t)
    t2 = t2.rstrip('\n')
    header = f'{MARK}\n# Pojia persona: applies globally AND to every profile\n'
    # top-level (file scope)
    top_block = header + KEY + f' = "{persona}"\n'
    new = top_block + '\n' + t2.lstrip('\n')
    # now also add into every [profiles.X] section
    lines = new.split('\n')
    out = []
    i = 0
    injected_profiles = []
    while i < len(lines):
        line = lines[i]
        out.append(line)
        m = re.match(r'^\s*\[profiles\.([^\]]+)\]\s*$', line)
        if m:
            name = m.group(1)
            # skip until next section header or EOF; append key at section end
            j = i + 1
            while j < len(lines) and not re.match(r'^\s*\[', lines[j]):
                out.append(lines[j]); j += 1
            out.append(KEY + f' = "{persona}"')
            injected_profiles.append(name)
            i = j
            continue
        i += 1
    new = '\n'.join(out)
    if not new.endswith('\n'):
        new += '\n'
    p.write_text(new, encoding='utf-8')
    print(f'[+] top-level {KEY} injected')
    if injected_profiles:
        print(f'[+] injected into profiles: {", ".join(injected_profiles)}')
    else:
        print('[*] no [profiles.*] sections found (nothing extra to cover)')
elif action == 'remove':
    t = re.sub(re.escape(MARK) + r'[\s\S]*?' + re.escape(END) + r'\n?', '', t, count=1)
    p.write_text(t, encoding='utf-8')
    print('[+] removed pojia block from config')
