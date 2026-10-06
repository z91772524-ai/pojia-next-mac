#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""发布助手：生成 SHA256SUMS.txt + 打包 Release 附件。

借鉴上游 pojia-next 的 release.py，但做了两处 macOS 侧的适配：

  1. **不依赖 Windows 的 cmd**（上游用 `cmd /c copy` 与 `rmdir`）——
     这里是纯 Python 的 shutil/zipfile，Linux / macOS / Windows 都能跑。
  2. **打出来的 zip 带一层外层文件夹** `pojia-next-mac-vX.Y.Z/`。
     上一版 v1.0.7 的附件是**平的**（19 个顶层文件直接铺在 zip 根），
     用户"解压到桌面"会把桌面弄乱；这也违反了本项目的发布自检项。

用法：
    python3 release.py              # 生成 SHA256SUMS.txt + 打包附件到 dist/
    python3 release.py --print      # 只打印各文件哈希（用于更新 README 表格）
"""
import hashlib
import os
import shutil
import sys
import zipfile

REPO = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(REPO, "dist")

# 不进包的东西：版本控制、运行时产物、打包产物、系统垃圾、开发期回归测试
SKIP_DIRS = {".git", "dist", "_archive", "__pycache__", ".pytest_cache", "_回归测试"}
SKIP_FILES = {"破甲日志.txt", ".DS_Store", "Thumbs.db", "desktop.ini"}
SKIP_SUFFIX = (".pojiabak", ".pyc", ".pyo", ".log")


def read_version():
    p = os.path.join(REPO, "VERSION")
    if os.path.isfile(p):
        return open(p, encoding="utf-8").read().strip()
    return "0.0.0"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 16), b""):
            h.update(b)
    return h.hexdigest()


def collect():
    """返回 [(相对路径, 绝对路径)]，按相对路径排序，保证清单稳定可复现。"""
    out = []
    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in files:
            if fn in SKIP_FILES or fn.endswith(SKIP_SUFFIX):
                continue
            full = os.path.join(root, fn)
            rel = os.path.relpath(full, REPO).replace(os.sep, "/")
            out.append((rel, full))
    out.sort()
    return out


def main():
    ver = read_version()
    print("版本:", ver)
    files = collect()

    if "--print" in sys.argv:
        for rel, full in files:
            print("| `%s` | `%s` | %d |" % (rel, sha256(full), os.path.getsize(full)))
        return 0

    # ---- 1) 生成 SHA256SUMS.txt（LF、无 BOM —— 与 .gitattributes 的 eol=lf 一致）----
    lines = ["# 破甲next · macOS v%s —— SHA256 校验清单" % ver,
             "# 校验方法（macOS / Linux）:",
             "#   cd 解压出来的目录 && shasum -a 256 -c SHA256SUMS.txt",
             "# 校验方法（Windows PowerShell）:",
             "#   Get-FileHash .\\wb-macos.py -Algorithm SHA256",
             ""]
    for rel, full in files:
        if rel == "SHA256SUMS.txt":
            continue
        lines.append("%s  %s" % (sha256(full), rel))
    sums_path = os.path.join(REPO, "SHA256SUMS.txt")
    with open(sums_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    n = sum(1 for l in lines if not l.startswith("#") and l.strip())
    print("已写 %s（%d 项）" % (sums_path, n))

    # ---- 2) 打 zip：外层文件夹 + 内含 SHA256SUMS.txt ----
    os.makedirs(DIST, exist_ok=True)
    inner = "pojia-next-mac-v%s" % ver
    zip_path = os.path.join(DIST, "%s.zip" % inner)
    if os.path.exists(zip_path):
        os.remove(zip_path)
    # 重新收集一次，把刚生成的 SHA256SUMS.txt 也收进去
    files = collect()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for rel, full in files:
            z.write(full, "%s/%s" % (inner, rel))
    print("已打包:", zip_path, os.path.getsize(zip_path), "字节")
    print("zip sha256:", sha256(zip_path))
    with zipfile.ZipFile(zip_path) as z:
        names = z.namelist()
        tops = sorted({x.split("/")[0] for x in names})
        print("条目:", len(names), " 顶层:", tops)
        assert tops == [inner], "外层文件夹不正确：%s" % tops
        assert "SHA256SUMS.txt" in "".join(names), "包里没有 SHA256SUMS.txt"
    print("自检通过：外层文件夹正确、包内含 SHA256SUMS.txt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
