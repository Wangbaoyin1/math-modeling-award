# -*- coding: utf-8 -*-
"""
Python 出版级图表库（建模直接调用，共 25 款）
- 基础数据图 14 + 高级可视化 6（雷达/小提琴/气泡/脊线/桑基/和弦）+ 分析图 5（Pareto/预测vs真实/特征重要性/收敛/预测区间）
- 示意图（结构/流程/机理/技术路线）请用 draw.io/TikZ，见 获奖方法论/示意图绘制规范.md
- 中文字体 SimHei 第一（防止方块），Paul Tol 色板，出版级保存；上标用 mathtext（R² 写 $R^2$）
用法：from 图表库 import *   然后调用各函数
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import os

# ===== 注册 Windows 中文字体（SimHei 黑体 / 微软雅黑）=====
for _fp in [r"C:\Windows\Fonts\simhei.ttf", r"C:\Windows\Fonts\msyh.ttc"]:
    if os.path.exists(_fp):
        try:
            fm.fontManager.addfont(_fp)
        except Exception:
            pass

# ===== 全局出版样式 =====
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "Arial", "DejaVu Sans"]  # SimHei 必须第一！
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["axes.spines.right"] = False
plt.rcParams["axes.spines.top"] = False
plt.rcParams["legend.frameon"] = False
plt.rcParams["figure.dpi"] = 100

# Paul Tol Bright（色盲友好）: 蓝=主方法/灰=基线/红=警示
C_MAIN, C_ALT1, C_ALT2 = "#4477AA", "#EE6677", "#228833"
C_BASE, C_WARN = "#BBBBBB", "#B64342"

def savefig(fig, path, dpi=300):
    """统一出版级保存：去白边、高 DPI"""
    fig.tight_layout()
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    print(f"[图] 已保存 {path}")

# ===== 1. 折线图（趋势/收敛，最常用）=====
def line_chart(x, ys, labels, xlabel, ylabel, path,
               title=None, colors=None, lw=1.8, markers=None):
    fig, ax = plt.subplots(figsize=(6, 3.8))
    colors = colors or [C_MAIN, C_ALT1, C_ALT2, C_BASE]
    for i, (y, lab) in enumerate(zip(ys, labels)):
        ax.plot(x, y, color=colors[i % len(colors)], lw=lw,
                marker=markers[i] if markers else None, ms=3, label=lab)
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    if title: ax.set_title(title, fontsize=11)
    if labels: ax.legend()
    savefig(fig, path)

# ===== 2. 散点图（相关性/分布）=====
def scatter_plot(x, y, xlabel, ylabel, path, c=C_MAIN, alpha=0.6, s=18):
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.scatter(x, y, s=s, c=c, alpha=alpha, edgecolors="none")
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    savefig(fig, path)

# ===== 3. 分组柱状图（对比）=====
def grouped_bar(categories, groups, path, ylabel="", legend_labels=None):
    """groups: list of arrays，每组一个分类序列"""
    x = np.arange(len(categories))
    w = 0.8 / len(groups)
    fig, ax = plt.subplots(figsize=(7, 3.8))
    for i, g in enumerate(groups):
        ax.bar(x + i*w - w*(len(groups)-1)/2, g, width=w,
               color=[C_MAIN, C_ALT1, C_ALT2, C_BASE][i % 4],
               label=legend_labels[i] if legend_labels else f"组{i+1}")
    ax.set_xticks(x); ax.set_xticklabels(categories)
    ax.set_ylabel(ylabel)
    if legend_labels: ax.legend()
    savefig(fig, path)

# ===== 4. 热力图（相关性矩阵/参数扫描）=====
def heatmap(mat, xticklabels, yticklabels, path, cmap="cividis", fmt=".2f"):
    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    im = ax.imshow(mat, cmap=cmap)
    ax.set_xticks(range(len(xticklabels))); ax.set_xticklabels(xticklabels, rotation=45, ha="right")
    ax.set_yticks(range(len(yticklabels))); ax.set_yticklabels(yticklabels)
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            ax.text(j, i, f"{mat[i,j]:{fmt}}", ha="center", va="center", color="white" if mat[i,j] > mat.max()*0.6 else "black")
    fig.colorbar(im, ax=ax, shrink=0.8)
    savefig(fig, path)

# ===== 5. 龙卷风图（敏感性排序，国奖标配）=====
def tornado(param_names, low_deltas, high_deltas, path, title="参数敏感性分析"):
    """low/high: 参数 -X%/+X% 时结果相对基准的变化（绝对值或比例）"""
    y = np.arange(len(param_names))
    fig, ax = plt.subplots(figsize=(6, len(param_names)*0.55+1.2))
    ax.barh(y, low_deltas, color=C_MAIN, label="下限扰动")
    ax.barh(y, high_deltas, color=C_ALT1, label="上限扰动", left=low_deltas)
    ax.set_yticks(y); ax.set_yticklabels(param_names)
    ax.axvline(0, color="black", lw=0.8)
    ax.set_xlabel("结果变化 (%)")
    ax.set_title(title)
    ax.legend(loc="lower right")
    savefig(fig, path)

# ===== 6. 箱线图（分布对比）=====
def box_plot(data, labels, ylabel, path):
    fig, ax = plt.subplots(figsize=(6, 4))
    bp = ax.boxplot(data, tick_labels=labels, patch_artist=True, widths=0.55)
    for patch in bp["boxes"]:
        patch.set_facecolor("#DDEBF7"); patch.set_edgecolor(C_MAIN)
    for med in bp["medians"]:
        med.set_color(C_WARN); med.set_linewidth(1.6)
    ax.set_ylabel(ylabel)
    savefig(fig, path)

# ===== 7. 三维图（matplotlib 3D）=====
def plot3d_surface(X, Y, Z, path, xlabel="X", ylabel="Y", zlabel="Z", cmap="viridis"):
    from mpl_toolkits.mplot3d import Axes3D  # noqa
    fig = plt.figure(figsize=(6, 4.5))
    ax = fig.add_subplot(111, projection="3d")
    surf = ax.plot_surface(X, Y, Z, cmap=cmap, edgecolor="none", alpha=0.9)
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel); ax.set_zlabel(zlabel)
    savefig(fig, path)

# ===== 8. 直方图（分布）=====
def histogram(data, xlabel, ylabel, path, bins=30, color=C_MAIN, title=None):
    fig, ax = plt.subplots(figsize=(6, 3.8))
    ax.hist(data, bins=bins, color=color, alpha=0.75, edgecolor="white")
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    if title: ax.set_title(title)
    savefig(fig, path)

# ===== 9. 双 y 轴图（两个量纲不同的序列）=====
def twin_axis(x, y1, y2, labels, path, xlabel="x", ylabels=("左轴", "右轴")):
    fig, ax1 = plt.subplots(figsize=(6.5, 4))
    ax1.plot(x, y1, color=C_MAIN, lw=1.8, label=labels[0])
    ax1.set_xlabel(xlabel); ax1.set_ylabel(ylabels[0], color=C_MAIN)
    ax1.tick_params(axis="y", labelcolor=C_MAIN)
    ax2 = ax1.twinx()
    ax2.plot(x, y2, color=C_ALT1, lw=1.8, ls="--", label=labels[1])
    ax2.set_ylabel(ylabels[1], color=C_ALT1)
    ax2.tick_params(axis="y", labelcolor=C_ALT1)
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc="best")
    savefig(fig, path)

# ===== 10. 对数坐标图（量级跨度大）=====
def log_plot(x, y, xlabel, ylabel, path, logx=False, logy=True, label=None):
    fig, ax = plt.subplots(figsize=(6, 3.8))
    ax.plot(x, y, color=C_MAIN, lw=1.8, label=label)
    if logx: ax.set_xscale("log")
    if logy: ax.set_yscale("log")
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    if label: ax.legend()
    savefig(fig, path)

# ===== 11. 子图组合（多图对比，国奖常见）=====
def subplot_grid(nrows, ncols, path):
    """返回 (fig, axes数组)；axes 逐个画完后调 savefig"""
    fig, axes = plt.subplots(nrows, ncols, figsize=(6.5*ncols, 3.8*nrows))
    return fig, axes

# ===== 12. 柱状误差棒（带波动范围）=====
def bar_with_error(categories, means, errors, ylabel, path, color=C_MAIN):
    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    ax.bar(categories, means, color=color, width=0.55, yerr=errors,
           capsize=4, edgecolor="white")
    ax.set_ylabel(ylabel)
    savefig(fig, path)

# ===== 13. 空间色图 / 地图类（choropleth）=====
def map_scatter(x, y, c, path, xlabel="x (m)", ylabel="y (m)", title="",
                cmap="viridis", s=18, edgecolor="k", cbar_label="值",
                markers=None, marker_annot=None, marker_color="#B64342",
                equal_aspect=True):
    """空间采样点着色散点图：x,y 坐标; c 数值(或分类标签); markers 可选(如污染源★)。
    适用: 城区采样点污染分布 / 点位浓度图。"""
    fig, ax = plt.subplots(figsize=(6.8, 5.2))
    if np.issubdtype(np.asarray(c).dtype, np.number):
        sc = ax.scatter(x, y, c=c, cmap=cmap, s=s, edgecolor=edgecolor,
                        linewidths=0.3)
        cb = fig.colorbar(sc, ax=ax, label=cbar_label)
        if title: ax.set_title(title)
    else:  # 分类标签 -> 用类别着色 + 图例
        cats = list(dict.fromkeys(c))
        cmap_obj = plt.get_cmap("tab10")
        for k, cat in enumerate(cats):
            mask = [v == cat for v in c]
            ax.scatter(np.array(x)[mask], np.array(y)[mask],
                       s=s, color=cmap_obj(k % 10), edgecolor="white",
                       linewidths=0.3, label=cat)
        ax.legend(fontsize=8, frameon=True, title=title or "分类")
    if markers is not None:  # markers: [(mx, my, label), ...]
        for mx, my, lab in markers:
            ax.scatter([mx], [my], marker="*", s=260, color=marker_color,
                       edgecolor="white", linewidths=1.0, zorder=6)
            if marker_annot and lab:
                ax.annotate(lab, (mx, my), xytext=(6, 6),
                            textcoords="offset points", fontsize=9)
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    if equal_aspect: ax.set_aspect("equal")
    savefig(fig, path)

def map_contour(x, y, z, path, xlabel="x (m)", ylabel="y (m)", title="",
                cmap="viridis", n_grid=120, markers=None, cbar_label="值",
                k=20, p=2.0, contour_lines=False):
    """空间插值面（IDW）+ 等值线, 采样点可叠加★标记。适用: 污染等值面/浓度场。"""
    from math import sqrt
    x = np.asarray(x, float); y = np.asarray(y, float); z = np.asarray(z, float)
    gx = np.linspace(x.min(), x.max(), n_grid)
    gy = np.linspace(y.min(), y.max(), n_grid)
    GX, GY = np.meshgrid(gx, gy)
    ZI = np.zeros_like(GX)
    xs, ys, zs = x.ravel(), y.ravel(), z.ravel()
    for i in range(GX.shape[0]):
        for j in range(GX.shape[1]):
            d2 = (xs - GX[i, j]) ** 2 + (ys - GY[i, j]) ** 2
            nn = np.argpartition(d2, min(k, xs.size))[:min(k, xs.size)]
            dd = np.sqrt(np.maximum(d2[nn], 1e-12))
            w = 1.0 / dd ** p
            ZI[i, j] = np.sum(w * zs[nn]) / np.sum(w)
    fig, ax = plt.subplots(figsize=(7.2, 5.4))
    cf = ax.contourf(GX, GY, ZI, 18, cmap=cmap)
    if contour_lines:
        cs = ax.contour(GX, GY, ZI, 8, colors="white", linewidths=0.5, alpha=0.7)
        ax.clabel(cs, inline=True, fontsize=7, fmt="%.1f")
    cb = fig.colorbar(cf, ax=ax, label=cbar_label)
    if markers is not None:
        for mx, my, lab in markers:
            ax.scatter([mx], [my], marker="*", s=300, color="#B64342",
                       edgecolor="white", linewidths=1.1, zorder=6)
            if lab: ax.annotate(lab, (mx, my), xytext=(7, 7),
                                textcoords="offset points", fontsize=9)
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    if title: ax.set_title(title)
    ax.set_aspect("equal")
    savefig(fig, path)


# ===== 15. 雷达图（多方案·多维对比，极坐标）=====
def radar_chart(categories, values_list, labels, path,
                title="多维度对比", rmax=None):
    """categories: 维度名列表; values_list: [各方案各维取值...]; labels: 方案名
    适用: 多方案/多模型/多区域在多个指标上的综合对比（一眼看出优劣剖面）"""
    N = len(categories)
    angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()
    angles += angles[:1]
    colors = [C_MAIN, C_ALT1, C_ALT2, C_BASE, "#CCBB44", "#66CCEE"]
    fig, ax = plt.subplots(figsize=(6.4, 6.4), subplot_kw=dict(polar=True))
    for i, vals in enumerate(values_list):
        v = np.asarray(vals, float)
        v = np.concatenate([v, v[:1]])
        c = colors[i % len(colors)]
        ax.plot(angles, v, color=c, lw=2, label=labels[i])
        ax.fill(angles, v, color=c, alpha=0.15)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=9)
    if rmax: ax.set_ylim(0, rmax)
    ax.set_title(title, fontsize=11, pad=18)
    ax.legend(loc="upper right", bbox_to_anchor=(1.28, 1.12), fontsize=9)
    savefig(fig, path)


# ===== 16. 小提琴图（分布密度+箱线，比箱线信息量大）=====
def violin_plot(datasets, labels, ylabel, path, title=None):
    """datasets: [每组数据数组...]; labels: 组名
    适用: 多组输出/结果的分布对比（形状+中位数+四分位一并展示）"""
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    vp = ax.violinplot(datasets, showmeans=False, showmedians=True)
    colors = [C_MAIN, C_ALT1, C_ALT2, C_BASE, "#CCBB44"]
    for i, body in enumerate(vp["bodies"]):
        body.set_facecolor(colors[i % len(colors)])
        body.set_edgecolor(colors[i % len(colors)])
        body.set_alpha(0.55)
    for part in ("cbars", "cmins", "cmaxes", "cmedians"):
        if part in vp:
            vp[part].set_color("#333333")
            vp[part].set_linewidth(1.0)
    ax.set_xticks(range(1, len(labels)+1))
    ax.set_xticklabels(labels)
    ax.set_ylabel(ylabel)
    if title: ax.set_title(title, fontsize=11)
    savefig(fig, path)


# ===== 17. 气泡图（位置+大小+颜色，一图三信息）=====
def bubble_chart(x, y, size, color, xlabel, ylabel, path,
                 s_scale=400, cmap="viridis", cbar_label="", title=None):
    """size: 气泡大小(自动归一化缩放); color: 数值(着色)
    适用: 三维信息压缩到二维（如 x=位置, y=价格, 大小=销量, 颜色=利润）"""
    fig, ax = plt.subplots(figsize=(7, 5))
    size = np.asarray(size, float)
    s = size / (size.max() + 1e-9) * s_scale
    sc = ax.scatter(x, y, s=s, c=color, cmap=cmap, alpha=0.7,
                    edgecolors="white", linewidths=0.5)
    fig.colorbar(sc, ax=ax, label=cbar_label)
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    if title: ax.set_title(title, fontsize=11)
    savefig(fig, path)


# ===== 18. 脊线图（多组分布堆叠密度）=====
def ridgeline_plot(datasets, labels, path, xlabel="值", title=None, bins=40):
    """datasets: [每组数据数组...]; labels: 组名
    适用: 多组数据整体分布形状对比（多年份/多区域/多方法的输出分布）"""
    fig, ax = plt.subplots(figsize=(7, len(datasets)*0.75+1.6))
    colors = [C_MAIN, C_ALT1, C_ALT2, C_BASE, "#CCBB44", "#66CCEE"]
    for i, data in enumerate(datasets):
        data = np.asarray(data, float)
        counts, edges = np.histogram(data, bins=bins, density=True)
        x = (edges[:-1] + edges[1:]) / 2
        y = counts / (counts.max() + 1e-9) * 0.85 + i
        c = colors[i % len(colors)]
        ax.fill_between(x, i, y, color=c, alpha=0.55, zorder=3)
        ax.plot(x, y, color=c, lw=1.2)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels)
    ax.set_xlabel(xlabel)
    ax.spines["left"].set_visible(False)
    if title: ax.set_title(title, fontsize=11)
    savefig(fig, path)


# ===== 19. 桑基图（流量/资源去向）=====
def sankey_diagram(flows, labels, path, orientations=None, title="流量图"):
    """flows: 流量数组(正=流入, 负=流出, 总和≈0); labels: 节点名
    适用: 资源/资金/物质/能源的分配去向、成本分摊、系统能流"""
    from matplotlib.sankey import Sankey
    fig = plt.figure(figsize=(8, 4))
    ax = fig.add_subplot(1, 1, 1)
    m = max(abs(np.min(flows)), abs(np.max(flows)), 1e-9)
    sk = Sankey(ax=ax, scale=0.6/m, format="%.2f", unit="", gap=0.35,
                head_angle=120, shoulder=0.03)
    if orientations is None:
        orientations = [0] * len(flows)
    sk.add(flows=flows, labels=labels, orientations=orientations, pathlengths=0.5)
    sk.finish()
    if title: ax.set_title(title, fontsize=11)
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"[图] 已保存 {path}")


# ===== 20. 和弦图（n×n 关联/迁移矩阵的环形流向）=====
def chord_diagram(matrix, labels, path, title="和弦图"):
    """matrix: n×n 关系矩阵(行→列的流量/强度); labels: 节点名
    适用: 多对象间交互强度/迁移矩阵/贸易流/关联网络"""
    matrix = np.asarray(matrix, float)
    n = matrix.shape[0]
    total = matrix.sum()
    if total <= 0:
        raise ValueError("关系矩阵总和须 > 0")
    row_out = matrix.sum(axis=1)
    col_in = matrix.sum(axis=0)
    starts = np.zeros(n); acc = 0.0
    for i in range(n):
        starts[i] = acc
        acc += row_out[i] / total * 2 * np.pi
    col_starts = np.zeros(n); acc = 0.0
    for j in range(n):
        col_starts[j] = acc
        acc += col_in[j] / total * 2 * np.pi
    col_cursor = col_starts.copy()
    cmap = plt.get_cmap("tab20")
    fig, ax = plt.subplots(figsize=(7.6, 7.6), subplot_kw=dict(polar=True))
    R = 1.0
    ax.set_rmax(R * 1.4)
    ax.set_rmin(0)
    ax.set_frame_on(False)
    ax.set_xticks([]); ax.set_yticks([])
    for i in range(n):
        a0 = starts[i]
        a1 = starts[i] + row_out[i] / total * 2 * np.pi
        th = np.linspace(a0, a1, 80)
        ax.plot(th, np.full(80, R), color=cmap(i), lw=12,
                solid_capstyle="butt", alpha=0.9)
        ax.text((a0 + a1) / 2, R * 1.14, labels[i], ha="center", va="center",
                fontsize=10, color=cmap(i))
    for i in range(n):
        if row_out[i] <= 0:
            continue
        acc_i = starts[i]
        span_i = row_out[i] / total * 2 * np.pi
        for j in range(n):
            w = matrix[i, j]
            if w <= 0 or col_in[j] <= 0:
                continue
            a_s = acc_i
            a_e = acc_i + w / row_out[i] * span_i
            acc_i = a_e
            t1 = (a_s + a_e) / 2
            span_j = col_in[j] / total * 2 * np.pi
            b_s = col_cursor[j]
            b_e = col_cursor[j] + w / col_in[j] * span_j
            col_cursor[j] = b_e
            t2 = (b_s + b_e) / 2
            t = np.linspace(0, 1, 40)
            ang = t1 + (t2 - t1) * t
            rr = R * (1 - 0.6 * (1 - (2 * t - 1) ** 2))
            ax.plot(ang, rr, color=cmap(i), lw=1 + 3 * (w / matrix.max()),
                    alpha=0.55)
    savefig(fig, path)


# ===== 21. Pareto 前沿（多目标优化权衡曲线，A/B 类常考）=====
def pareto_front(x, y, path, xlabel="目标1", ylabel="目标2",
                 minimize=(True, True), title="Pareto 前沿",
                 highlight=None, hl_label="推荐解"):
    """x,y: 两个目标的解集; minimize: 各自是否越小越好; highlight: 推荐解索引
    适用: 多目标优化的权衡曲线（成本vs效果 / 精度vs速度 / 收益vs风险）"""
    fig, ax = plt.subplots(figsize=(6.2, 4.6))
    ax.scatter(x, y, s=30, c=C_BASE, alpha=0.7, edgecolors="white",
               linewidths=0.4, label="可行解")
    pts = np.column_stack([np.asarray(x, float), np.asarray(y, float)])
    sx = -1 if minimize[0] else 1
    sy = -1 if minimize[1] else 1
    is_front = np.ones(len(pts), bool)
    for i in range(len(pts)):
        for j in range(len(pts)):
            if i == j:
                continue
            if (sx*pts[j, 0] >= sx*pts[i, 0] and sy*pts[j, 1] >= sy*pts[i, 1]) and \
               (sx*pts[j, 0] > sx*pts[i, 0] or sy*pts[j, 1] > sy*pts[i, 1]):
                is_front[i] = False
                break
    fx, fy = pts[is_front][:, 0], pts[is_front][:, 1]
    idx = np.argsort(fx)
    ax.plot(fx[idx], fy[idx], color=C_MAIN, lw=2, marker="o", ms=5,
            label="Pareto 前沿")
    if highlight is not None:
        ax.scatter([x[highlight]], [y[highlight]], s=160, marker="*",
                   color=C_WARN, edgecolor="black", zorder=6, label=hl_label)
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    ax.set_title(title, fontsize=11)
    ax.legend()
    savefig(fig, path)


# ===== 22. 预测 vs 真实（验证图，附 45° 线与 R²）=====
def pred_vs_true(y_true, y_pred, path, xlabel="真实值", ylabel="预测值",
                 title="预测 vs 真实"):
    """y_true/y_pred: 真实与预测值; 画散点+45°理想线+R²
    适用: 检验三板斧之「误差分析」，模型精度一目了然"""
    y_true = np.asarray(y_true, float)
    y_pred = np.asarray(y_pred, float)
    fig, ax = plt.subplots(figsize=(5.8, 5.0))
    lo = min(y_true.min(), y_pred.min())
    hi = max(y_true.max(), y_pred.max())
    ax.plot([lo, hi], [lo, hi], color=C_WARN, lw=1.4, ls="--", label="y=x 理想线")
    ax.scatter(y_true, y_pred, s=28, c=C_MAIN, alpha=0.65,
               edgecolors="white", linewidths=0.4)
    ss_res = ((y_true - y_pred) ** 2).sum()
    ss_tot = ((y_true - y_true.mean()) ** 2).sum()
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    ax.text(0.05, 0.95, f"$R^2$ = {r2:.4f}", transform=ax.transAxes, va="top",
            fontsize=11, bbox=dict(boxstyle="round", fc="white", alpha=0.8))
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    ax.set_title(title, fontsize=11)
    ax.set_aspect("equal")
    ax.legend(loc="lower right")
    savefig(fig, path)


# ===== 23. 特征重要性（水平条形，数据/AI 题）=====
def feature_importance(features, importances, path, title="特征重要性", top=None):
    """features: 特征名; importances: 重要性值(自动升序排列); top: 只画前 top 个
    适用: 数据/AI 题揭示「哪个变量最关键」——风格库模板8 的直接可视化"""
    importances = np.asarray(importances, float)
    order = np.argsort(importances)
    if top:
        order = order[-top:]
    feats = [features[i] for i in order]
    vals = [importances[i] for i in order]
    fig, ax = plt.subplots(figsize=(6.5, max(2.2, len(feats)*0.45)))
    ax.barh(range(len(feats)), vals, color=C_MAIN, height=0.6)
    ax.set_yticks(range(len(feats)))
    ax.set_yticklabels(feats)
    ax.set_xlabel("重要性")
    ax.set_title(title, fontsize=11)
    savefig(fig, path)


# ===== 24. 收敛曲线（优化算法迭代过程）=====
def convergence_curve(iterations, objective, path, optimal=None,
                      xlabel="迭代次数", ylabel="目标值", title="算法收敛曲线"):
    """iterations: 迭代序号; objective: 各代最优目标值; optimal: 已知最优(画虚线)
    适用: 优化题的算法收敛性展示——风格库模板11 的标配佐证"""
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.plot(iterations, objective, color=C_MAIN, lw=1.8, label="当前最优")
    if optimal is not None:
        ax.axhline(optimal, color=C_WARN, lw=1.3, ls="--",
                   label=f"已知最优={optimal}")
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    ax.set_title(title, fontsize=11)
    ax.legend()
    savefig(fig, path)


# ===== 25. 预测区间带（预测 + 置信区间 + 真实值）=====
def prediction_band(x, y_pred, y_lower, y_upper, path, y_true=None,
                    xlabel="x", ylabel="y", title="预测及置信区间"):
    """y_pred/y_lower/y_upper: 预测值与上下界; y_true: 可选真实值散点
    适用: 预测题展示不确定性(区间而非点估计)——数据题真知"""
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.fill_between(x, y_lower, y_upper, color=C_MAIN, alpha=0.2, label="置信区间")
    ax.plot(x, y_pred, color=C_MAIN, lw=1.8, label="预测值")
    if y_true is not None:
        ax.scatter(x, y_true, s=20, c=C_ALT1, alpha=0.7, label="真实值", zorder=5)
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    ax.set_title(title, fontsize=11)
    ax.legend()
    savefig(fig, path)


if __name__ == "__main__":
    # 自测：画 3 张示例图验证
    import os
    demo = os.path.join(os.path.dirname(__file__), "_demo图")
    os.makedirs(demo, exist_ok=True)
    t = np.linspace(0, 2*np.pi, 100)
    line_chart(t, [np.sin(t), np.cos(t)], ["sin", "cos"], "x", "y",
               os.path.join(demo, "demo_line.png"))
    grouped_bar(["Q1", "Q2", "Q3"], [[30, 40, 35], [45, 32, 50]],
                os.path.join(demo, "demo_bar.png"), "销量", ["A", "B"])
    params = ["价格弹性", "成本", "需求", "折扣"]
    tornado(params, [-3.2, -1.1, -5.8, -0.8], [3.2, 1.1, 5.8, 0.8],
            os.path.join(demo, "demo_tornado.png"))
    print("图表库自测完成")
