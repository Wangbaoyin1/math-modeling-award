#!/usr/bin/env bash
# aishumo 安装脚本（macOS / Linux）
# 用法：
#   bash aishumo/install.sh
#   DSH_HOME=/path/to/.dsh bash aishumo/install.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DSH_HOME="${DSH_HOME:-$HOME/.dsh}"

SKILL_DIR="$DSH_HOME/skills/aishumo-method"
PRESET_DIR="$DSH_HOME/.agent-presets/aishumo"
KNOWLEDGE_DST="$SKILL_DIR/知识库"
TOOLS_DST="$SKILL_DIR/tools"

echo "aishumo 安装"
echo "  仓库：$REPO_ROOT"
echo "  DSH ：$DSH_HOME"

mkdir -p "$SKILL_DIR" "$PRESET_DIR" "$KNOWLEDGE_DST" "$TOOLS_DST"

if [ ! -d "$REPO_ROOT/知识库" ]; then
  echo "找不到知识库目录：$REPO_ROOT/知识库" >&2
  exit 1
fi

cp -R "$REPO_ROOT/知识库/." "$KNOWLEDGE_DST/"
cp -R "$SCRIPT_DIR/tools/." "$TOOLS_DST/"

python3 - "$SCRIPT_DIR" "$SKILL_DIR" "$PRESET_DIR" "$KNOWLEDGE_DST" "$TOOLS_DST" <<'PY'
import pathlib
import sys

script_dir, skill_dir, preset_dir, knowledge_dst, tools_dst = map(pathlib.Path, sys.argv[1:])
knowledge = str(knowledge_dst).replace('\\', '/')
tools = str(tools_dst).replace('\\', '/')


def render(src: pathlib.Path, dst: pathlib.Path) -> None:
    text = src.read_text(encoding='utf-8')
    text = text.replace('{{KNOWLEDGE_ROOT}}', knowledge)
    text = text.replace('{{TOOLS_ROOT}}', tools)
    dst.write_text(text, encoding='utf-8', newline='\n')


render(script_dir / 'skills' / 'aishumo-method' / 'SKILL.md', skill_dir / 'SKILL.md')
render(script_dir / 'presets' / 'aishumo' / 'agent.cordis.yml', preset_dir / 'agent.cordis.yml')
(preset_dir / 'preset.yml').write_bytes(
    (script_dir / 'presets' / 'aishumo' / 'preset.yml').read_bytes()
)
PY

echo
echo "安装完成。"
echo "  预设：$PRESET_DIR"
echo "  技能：$SKILL_DIR"
echo
echo "下一步：重启 DSH，新建会话，在预设选择器中选择「AI 数模主控（aishumo）」。"
