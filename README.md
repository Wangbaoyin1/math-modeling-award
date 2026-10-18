# aishumo · AI 数模主控

> **一个 DeepSeek Harness 预设，把数学建模竞赛从读题到论文的全流程跑通。**
>
> 贴题 → 框架 → 推导 → 编码 → 验算 → 论文 → 审稿；阶段门禁、独立验算、三席盲评，全部内置。

<p>
  <img alt="DSH plugin" src="https://img.shields.io/badge/DeepSeek%20Harness-agent%20preset-4FC08D.svg">
  <img alt="License: MIT" src="https://img.shields.io/badge/code-MIT-blue.svg">
  <img alt="Docs: CC BY-NC 4.0" src="https://img.shields.io/badge/docs-CC%20BY--NC%204.0-lightgrey.svg">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10%2B-3776AB.svg">
  <img alt="LaTeX" src="https://img.shields.io/badge/LaTeX-XeLaTeX-008080.svg">
</p>

<p>
  <a href="https://github.com/Wangbaoyin1/math-modeling-award">GitHub</a> ·
  <a href="https://gitee.com/wangbao-yin/math-modeling-award">Gitee 镜像</a>
</p>

> 作者用 aishumo 完成 2026 年高教社杯全国大学生数学建模竞赛 A 题，获 **全国二等奖**。
> 仅作效果背书；获奖论文、赛题求解过程与相关软件不在本仓库公开。

---

## 为什么做这个插件

数学建模竞赛最耗人的不是“不会某个算法”，而是流程失控：

- 拿到题，题型判断错，后面全白做；
- 推导、代码、图表、论文各写各的，数值口径对不上；
- 代码跑出结果，没人独立复算，错了也不知道；
- 论文写完，摘要、图表、检验、合规全靠自觉。

aishumo 把这些环节固化成**可执行的阶段门禁**，让 AI 按流程交付，而不是一次性生成一篇“看起来像论文”的文本。

---

## 一条流水线

| 阶段 | 产物 | 门禁 |
|---|---|---|
| **Phase 0 框架** | `求解/模型推导/框架设计.md` | 核心思想 / 核心量≤3 / 五问递进 / 命题树 / 题型判定 |
| **Phase 1 推导** | 每问 `问题X_数学推导.md` | 量纲、假设[强/弱]、方法理由 + 备选方案 |
| **Phase 2 编码** | 每问 `问题X_求解.py` + `结果/*.csv` + `图片/*.png` | 必须实际运行，结果/图片非空 |
| **Phase 2.5 验算** | 独立验算报告 | 信息隔离复算；分歧 >30% FAIL |
| **Phase 3 论文** | `论文/*.tex` + `main.pdf` | xelatex ×2，Error=0；摘要/页数/图表硬检查 |
| **Phase 4 审稿** | 三席 scorecard + 聚合结论 | B1-B9 阻断项一票否决；三席盲评 ≥2 轮 |

### 五个角色

| 角色 | 职责 |
|---|---|
| **主控 Lead** | 读题、分派、监控、交付、回退协调 |
| **数学家** | 数据预检、深度推导、写推导文件 |
| **工程师** | 写代码、实际运行、产出 CSV/PNG、验算 |
| **作家** | 读推导与结果、写 LaTeX、编译、去 AI 味 |
| **审稿人** | 逐项检查、阻断项否决、证据驱动评审 |

### 质量机制

- **独立验算**：另派 subagent，信息隔离，用不同方法复算关键数值。
- **三席盲评**：旗舰通审 / 创新与决策 / 正确性可复现，三份 scorecard 独立打分。
- **数字冻结**：论文每个数字可追溯到 CSV / 脚本输出，改代码后检测 stale 引用。
- **技术失败止损**：同一 bug 修复 ≥3 次、偏差 >10% 未收敛、出现物理不可能结果 → 停止自试并上报。
- **学术诚信门控**：抄袭、数据造假、引用伪造、图片伪造、不可复现、匿名性违规、越权署名，任一触发一票否决。

---

## 安装

要求：**DeepSeek Harness（DSH）桌面版**。

```bash
git clone https://github.com/Wangbaoyin1/math-modeling-award.git
cd math-modeling-award

# Windows
powershell -ExecutionPolicy Bypass -File aishumo/install.ps1

# macOS / Linux
bash aishumo/install.sh
```

安装完成后**重启 DSH**，新建会话，在预设选择器中选择 **「AI 数模主控（aishumo）」**。

安装脚本会自动：

1. 把 `知识库/` 复制到 `~/.dsh/skills/aishumo-method/知识库/`
2. 安装 `aishumo-method` 技能与工具脚本
3. 把主控预设写入 `~/.dsh/.agent-presets/aishumo/`
4. 替换预设中的知识库/工具路径

> 详细安装、手动安装与卸载说明见 [`aishumo/README.md`](aishumo/README.md)。

---

## 使用

### 全自动跑通

新建会话 → 选「AI 数模主控」→ 直接贴题目 + 数据附件：

```
帮我做这道题，全自动跑通，最后交付论文 PDF 和支撑材料。
```

### 只做某一步

```
只做问题 1 的建模和求解，先不写论文
```

```
已有推导和结果，直接帮我写论文并编译
```

```
已成稿，只跑评审收敛：多视角评审 → 修复 → 终审
```

### 人工把关

```
用人工把关模式：每个关键决策点停下来给我编号选项确认，再继续
```

### 中途续跑

把已有 `求解/` 目录放进工作区，说：

```
继续求解
```

会读取 `求解/进度.md` 从断点继续。

---

## 产出结构

```
<你的题目目录>/
├─ 求解/
│  ├─ 模型推导/
│  │  ├─ 框架设计.md
│  │  └─ 问题X_数学推导.md
│  ├─ 问题X/
│  │  ├─ 问题X_求解.py
│  │  ├─ 结果/*.csv
│  │  └─ 图片/*.png
│  └─ 进度.md
├─ 论文/
│  ├─ main.tex
│  ├─ main.pdf
│  └─ 图片/
└─ 审稿/
   ├─ seat_A_scorecard.md
   ├─ seat_B_scorecard.md
   ├─ seat_C_scorecard.md
   └─ 聚合结论.md
```

---

## 知识库

`知识库/` 是 aishumo 的方法论底座：

- **底层逻辑**：建模七步法、框架设计、模型选择、假设合理性、检验与敏感性、结果解释
- **模型工具箱**：优化 / 评价 / 预测 / 图论 / 机理 / 统计 / 随机 / 数据 / 量纲 + 可运行模板
- **图表库**：出版级图函数（含龙卷风图、空间地图、3D 曲面）
- **获奖方法论**：选题决策、降 AI 写法、国奖论文六维拆解、失败模式库
- **论文模板**：`cumcmthesis.cls` + 标准骨架

入口：[`知识库/知识库总导航.md`](知识库/知识库总导航.md)

---

## 仓库结构

```
数学建模/
├─ aishumo/                    插件包
│  ├─ presets/aishumo/         主控预设（agent.cordis.yml + preset.yml）
│  ├─ skills/aishumo-method/   方法论技能
│  ├─ tools/                   图示生成 / PDF 编译脚本
│  ├─ install.ps1              Windows 安装
│  ├─ install.sh               macOS / Linux 安装
│  └─ README.md                插件安装与使用说明
├─ 知识库/                     方法论 / 模型工具箱 / 模板 / 失败模式库
├─ docs/                       架构与使用文档
├─ scripts/                    本地自检
├─ README.md
├─ LICENSE                     代码 MIT
└─ NOTICE.md                   授权、第三方归属与声明
```

---

## 常见问题

**必须用 DSH 吗？**
是。aishumo 是 DSH 的 agent 预设 + 技能包，依赖 DSH 的 subagent、todo、terminal 等工具。

**没有 xelatex 怎么办？**
Phase 3 会先探测 xelatex；没有时回退到 matplotlib PDF 排版。建议安装 MiKTeX / TeX Live 以获得正式论文排版。

**会编造数据吗？**
不会。Phase 2 强制代码实际运行、产出 CSV/PNG；Phase 2.5 独立复算；Phase 4 有学术诚信门控。

**和 UltraMath 的关系？**
aishumo 的 Phase 0-4 流程框架参考了 [UltraMath / dsh-ultramath](https://github.com/Andiii208/dsh-ultramath)（MIT），并注入自研方法论、知识库与审稿规则。详见 `NOTICE.md`。

**支持哪些竞赛？**
CUMCM 国赛、美赛 MCM/ICM、研赛等数学建模类竞赛均可使用；论文模板默认国赛 `cumcmthesis`。

---

## 边界

- 这是**竞赛与科研辅助工具**，不替代参赛者的核心建模判断与人工核验。
- AI 使用需遵守赛事规定：论文中放 AI 使用声明，核心建模由参赛队主导。
- 不生成、不伪造实验数据；所有数值必须来自实际运行的代码。
- 获奖论文、2026A 赛题求解代码、仿真软件与软著材料均不在本仓库。

---

## 许可与致谢

- 代码 / 预设 / 脚本：**MIT**（见 [`LICENSE`](LICENSE)）
- 知识库文档：**CC BY-NC 4.0**
- 流程框架参考：[UltraMath / dsh-ultramath](https://github.com/Andiii208/dsh-ultramath)（MIT）
- 论文模板：`cumcmthesis` 作者

<p align="center">
  <sub>如果这个插件对你有帮助，欢迎 Star ⭐ / Fork 🍴 / 提 Issue 💬</sub>
</p>
