# aishumo 安装脚本（Windows PowerShell）
# 用法：
#   powershell -ExecutionPolicy Bypass -File aishumo/install.ps1
#   powershell -ExecutionPolicy Bypass -File aishumo/install.ps1 -DshHome "D:\my-dsh"

param(
    [string]$DshHome = (Join-Path $HOME '.dsh')
)

$ErrorActionPreference = 'Stop'

$RepoRoot = Split-Path -Parent $PSScriptRoot
$SkillDir = Join-Path $DshHome 'skills\aishumo-method'
$PresetDir = Join-Path $DshHome '.agent-presets\aishumo'
$KnowledgeDst = Join-Path $SkillDir '知识库'
$ToolsDst = Join-Path $SkillDir 'tools'

Write-Host "aishumo 安装"
Write-Host "  仓库：$RepoRoot"
Write-Host "  DSH ：$DshHome"

New-Item -ItemType Directory -Force $SkillDir, $PresetDir, $KnowledgeDst, $ToolsDst | Out-Null

# 1. 知识库
$KnowledgeSrc = Join-Path $RepoRoot '知识库'
if (-not (Test-Path $KnowledgeSrc)) {
    throw "找不到知识库目录：$KnowledgeSrc"
}
Copy-Item (Join-Path $KnowledgeSrc '*') $KnowledgeDst -Recurse -Force

# 2. 工具脚本
Copy-Item (Join-Path $PSScriptRoot 'tools\*') $ToolsDst -Recurse -Force

# 3. 渲染路径占位符
$KnowledgePath = $KnowledgeDst.Replace('\', '/')
$ToolsPath = $ToolsDst.Replace('\', '/')

function Render-Template {
    param([string]$Source, [string]$Destination)
    $text = [System.IO.File]::ReadAllText($Source, [System.Text.Encoding]::UTF8)
    $text = $text.Replace('{{KNOWLEDGE_ROOT}}', $KnowledgePath)
    $text = $text.Replace('{{TOOLS_ROOT}}', $ToolsPath)
    [System.IO.File]::WriteAllText(
        $Destination,
        $text,
        (New-Object System.Text.UTF8Encoding($false))
    )
}

Render-Template `
    -Source (Join-Path $PSScriptRoot 'skills\aishumo-method\SKILL.md') `
    -Destination (Join-Path $SkillDir 'SKILL.md')

Render-Template `
    -Source (Join-Path $PSScriptRoot 'presets\aishumo\agent.cordis.yml') `
    -Destination (Join-Path $PresetDir 'agent.cordis.yml')

Copy-Item (Join-Path $PSScriptRoot 'presets\aishumo\preset.yml') (Join-Path $PresetDir 'preset.yml') -Force

Write-Host ""
Write-Host "安装完成。" -ForegroundColor Green
Write-Host "  预设：$PresetDir"
Write-Host "  技能：$SkillDir"
Write-Host ""
Write-Host "下一步：重启 DSH，新建会话，在预设选择器中选择「AI 数模主控（aishumo）」。"
Write-Host "如需正式论文排版，请确认 xelatex 在 PATH 中（MiKTeX / TeX Live）。"
