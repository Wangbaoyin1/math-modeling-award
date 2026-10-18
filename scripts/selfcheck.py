#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""aishumo 仓库自检。

检查：
1. 插件包关键文件齐全；
2. 模板占位符存在；
3. 不含本地绝对路径 / 明文密钥 / 获奖材料；
4. 知识库入口存在。

用法：
    python scripts/selfcheck.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "README.md",
    "LICENSE",
    "NOTICE.md",
    "aishumo/README.md",
    "aishumo/install.ps1",
    "aishumo/install.sh",
    "aishumo/presets/aishumo/agent.cordis.yml",
    "aishumo/presets/aishumo/preset.yml",
    "aishumo/skills/aishumo-method/SKILL.md",
    "aishumo/tools/gptimage2_gen.mjs",
    "知识库/知识库总导航.md",
    "docs/architecture.md",
]

FORBIDDEN_PATHS = [
    "2026A_药材烘干_重做/论文",
    "2026A_药材烘干_重做/求解",
    "drying_sim/",
    "答辩/",
    "软著申请材料/",
]

SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9]{16,}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
]

LOCAL_PATTERNS = [
    re.compile(r"E:\\数学建模"),
    re.compile(r"C:\\Users\\Administrator"),
]


def main() -> int:
    errors: list[str] = []

    for rel in REQUIRED:
        if not (ROOT / rel).exists():
            errors.append(f"缺少文件：{rel}")

    agent = ROOT / "aishumo/presets/aishumo/agent.cordis.yml"
    skill = ROOT / "aishumo/skills/aishumo-method/SKILL.md"
    for p in (agent, skill):
        if p.exists():
            text = p.read_text(encoding="utf-8")
            if "{{KNOWLEDGE_ROOT}}" not in text:
                errors.append(f"缺少知识库占位符：{p.relative_to(ROOT)}")
            if "{{TOOLS_ROOT}}" not in text and p == agent:
                errors.append(f"缺少工具占位符：{p.relative_to(ROOT)}")

    for rel in FORBIDDEN_PATHS:
        if (ROOT / rel).exists():
            errors.append(f"不应包含的获奖/私有目录：{rel}")

    text_exts = {".md", ".py", ".mjs", ".yml", ".yaml", ".sh", ".ps1", ".tex", ".txt"}
    for p in ROOT.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in text_exts:
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        for pat in SECRET_PATTERNS:
            if pat.search(text):
                errors.append(f"疑似明文密钥：{p.relative_to(ROOT)}")
        for pat in LOCAL_PATTERNS:
            if pat.search(text):
                errors.append(f"含本地绝对路径：{p.relative_to(ROOT)}")

    if errors:
        print("自检失败：")
        for e in errors:
            print(" -", e)
        return 1

    print("aishumo 自检通过：")
    print(f"  插件文件 {len(REQUIRED)} 项齐全")
    print("  模板占位符正常")
    print("  未发现获奖材料 / 明文密钥 / 本地绝对路径")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
