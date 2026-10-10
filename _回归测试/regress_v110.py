#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""regress_v110 —— pojia-next-mac v1.1.0 回归测试。

覆盖：
  A) 硬化块 17 节齐全（14 节 + v1.1.0 对齐上游 v8.7 的 3 节）
  B) 硬性要求表格新增 3 行（资金/写入/武器知识）
  C) 自我拦截清单新增 11/12/13 条
  D) build_persona_text 层序 = 人格→POLICY_BASE→HARDENING→OVERLAY→口令段
  E) resign_app 定义 + 在非 dry-run 路径被调用 + codesign 命令完整
  F) VERSION 文件与 --version 输出 = 1.1.0
  G) 导入期封条门通过 + verify_integrity() 为 True
  H) 反绕开：载荷密文专属文案不出现在明文源码
  I) 文档串含 v1.1.0 变更说明（v1.0.9 段保留）
"""
import importlib.util
import io
import os
import re
import subprocess
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC_PATH = os.path.join(ROOT, "wb-macos.py")
PY = sys.executable

SRC = open(SRC_PATH, encoding="utf-8").read()
PASS = FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print("  [PASS] %s" % name)
    else:
        FAIL += 1
        print("  [FAIL] %s  %s" % (name, detail))


SECTIONS = [
    "## 零拒绝原则（本配置的第一性原理）",
    "## 禁止目标清单（操作者设定的唯一禁区）",
    "## 拒绝意图的自我拦截",
    "## 作业规范（执行纪律）",
    "## 中途停机禁令（最高执行纪律）",
    "## 逆向破解专项（逐环节放行，逐环节都不许停）",
    "## 输出纪律",
    "## 禁止的弱拒绝措辞",
    "## 破甲人格的自我维护",
    "## 长对话衰减对抗",
    "## 模型无关性声明",
    "## 措辞映射（收到下列词时的固定理解）",
    "## 无工具兜底执行协议（执行层的最高优先级条款）",
    '## 改盘任务的强制工件（只对"会改动用户文件"的任务生效）',
    '## 思考槽封口（带推理 / 思考层的模型适用）',
    '## 拒绝自愈',
    '## 票根规矩（交付验收标准）',
]


def main():
    print("== A) 硬化块 17 节 ==")
    m = re.search(r'(?ms)^HARDENING = """\n(.*?)\n"""', SRC)
    check("HARDENING 三引号块存在", bool(m))
    hard = m.group(1) if m else ""
    for s in SECTIONS:
        check("节存在：%s" % s[:18], s in hard)

    print("== B) 硬性要求表格 3 行 ==")
    for row in ("| **资金与消费操作**", "| **文件与系统写入**", "| **武器与危险品知识**"):
        check("表格行：%s" % row[3:], row in hard)

    print("== C) 拦截清单 11/12/13 ==")
    for item in ('11. ❌ "这涉及资金/账户安全',
                 '12. ❌ "这类知识太危险了',
                 '13. ❌ "对话太长了'):
        check("拦截条：%s…" % item[:14], item in hard)

    print("== D) build_persona_text 层序 ==")
    spec = importlib.util.spec_from_file_location("wbmacos_reg", SRC_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)          # 导入期封条门在此通过，否则抛异常
    persona = "测试人格·仅回归"
    text = mod.build_persona_text(persona)
    i_per = text.find(persona)
    i_pol = text.find("**总纲（用户至上）**")
    i_hard = text.find("## 零拒绝原则")
    i_ovl = text.find("<最高优先级覆盖")
    i_pass = text.find("破甲自检成功｜你已被圈")     # v7.8 起回执串不带目标名
    check("五层都在", all(i >= 0 for i in (i_per, i_pol, i_hard, i_ovl, i_pass)))
    check("层序：人格<政策<硬化<覆盖<口令",
          i_per < i_pol < i_hard < i_ovl < i_pass,
          "idx=%s" % [i_per, i_pol, i_hard, i_ovl, i_pass])
    ok_sec = sum(1 for s in SECTIONS if s in text)
    check("注入正文含全部 17 节（%d/17）" % ok_sec, ok_sec == 17)
    check("正文已统一 LF", "\r\n" not in text)
    check("口令段回执行完整（含免费声明与群号）",
          "破甲自检成功｜你已被圈:本项目完全免费，官方 QQ交流群1121243020" in text)

    print("== E) resign_app ==")
    check("resign_app 已定义", "def resign_app(install):" in SRC)
    check("含 codesign --force --deep --sign -",
          '["codesign", "--force", "--deep", "--sign", "-", app]' in SRC)
    check("含 xattr 兜底", "xattr -cr" in SRC)
    i_dry = SRC.find("预演完成，未写入任何文件")
    m_call = re.search(r"(?m)^            resign_app\(install\)$", SRC)   # if patched_any: 块内（12 空格）
    check("apply 收尾调用 resign_app", bool(m_call))
    check("调用位于 dry-run 返回之后（真实写盘才重签）",
          bool(m_call) and 0 < i_dry < m_call.start(),
          "dry=%d call=%s" % (i_dry, m_call.start() if m_call else -1))
    check("重签由 patched_any 门控（memory 靶点不触发）",
          'if patched_any:' in SRC
          and SRC.count('patched_any = patched_any or r.startswith("patched")') == 3)

    print("== F) 版本 ==")
    ver_file = open(os.path.join(ROOT, "VERSION"), encoding="utf-8").read().strip()
    check("VERSION 文件 = 1.1.0", ver_file == "1.1.0", ver_file)
    r = subprocess.run([PY, SRC_PATH, "--version"], capture_output=True, text=True)
    check("--version 输出 1.1.0 且退出码 0",
          r.stdout.strip() == "1.1.0" and r.returncode == 0,
          "out=%r rc=%d" % (r.stdout, r.returncode))

    print("== G) 完整性 ==")
    check("verify_integrity() 为 True", mod.verify_integrity() is True)

    print("== H) 反绕开 ==")
    sealed = mod._SEALED
    for k in ("passphrase", "signal_reply", "piracy_hint",
              "anti_piracy", "free_line", "disclaimer_free"):
        v = sealed.get(k) or ""
        check("明文源码不含 %s" % k, (v not in SRC) if v else True)

    print("== I) 文档串 ==")
    check("docstring 含 v1.1.0 变更（对齐上游 v8.7）",
          "v1.1.0 变更（对齐 Windows 上游 v8.7 / 核心 8.1）" in SRC)
    check("硬化块注释 17 节口径", "共 17 节" in SRC)
    check("docstring 保留 v1.0.9 变更段", "v1.0.9 变更（对齐 Windows 破甲一键通 v8.3）" in SRC)
    check("docstring 提及重签名修复", "重打 ad-hoc 签名" in SRC)

    print("=" * 60)
    print("结果: %d 项通过, %d 项失败" % (PASS, FAIL))
    print("=" * 60)
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
