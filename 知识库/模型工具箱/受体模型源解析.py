# -*- coding: utf-8 -*-
"""
受体模型源解析（APCS-MLR / PMF-NMF）—— 可运行代码模板
- 对应知识卡 07 §3.2 / 风格库模板 19
- 定量各污染源的贡献率（%），输出贡献率堆叠图
- APCS-MLR：主成分分析(PCA) → 绝对主成分得分(APCS) → 多元线性回归(MLR) → 各源贡献
- PMF-NMF：非负矩阵分解同时反演源谱 F 与源贡献 G
用法：
    from 受体模型源解析 import apcs_mlr, pmf_nmf
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os

for _fp in [r"C:\Windows\Fonts\simhei.ttf", r"C:\Windows\Fonts\msyh.ttc"]:
    if os.path.exists(_fp):
        try:
            fm.fontManager.addfont(_fp)
        except Exception:
            pass
plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "Arial"]
plt.rcParams["axes.unicode_minus"] = False


def _zscore(X):
    return (X - X.mean(axis=0)) / X.std(axis=0, ddof=1)


def apcs_mlr(conc, elements=None, n_components=None, alpha=0.0, out_dir=None):
    """
    APCS-MLR 绝对主成分得分-多元线性回归。
    conc: DataFrame/ndarray，行=样本，列=元素浓度（原始值，非标准化）
    n_components: 保留主成分数（默认累计方差>=85% 或特征值>1）
    alpha: 岭回归正则（病态时增大）
    返回: dict{contrib_pct: 各源对总浓度的贡献%, loadings: 载荷, source_names: 自动命名}
    """
    if isinstance(conc, pd.DataFrame):
        elements = list(conc.columns)
        X = conc.to_numpy(float)
    else:
        X = np.asarray(conc, float)
        elements = elements or [f"E{i+1}" for i in range(X.shape[1])]
    n = X.shape[0]
    Z = _zscore(X)                          # 标准化
    # PCA（用 SVD，等同主成分）
    U, S, Vt = np.linalg.svd(Z, full_matrices=False)
    ev = (S ** 2) / (n - 1)                 # 特征值
    explained = ev / ev.sum()
    if n_components is None:
        kaiser = np.sum(ev > 1.0)
        k85 = int(np.searchsorted(np.cumsum(explained), 0.85) + 1)
        n_components = min(max(kaiser, k85), X.shape[1])
    scores = U[:, :n_components] * S[:n_components]     # 主成分得分
    loadings = Vt[:n_components, :].T                    # 载荷 (元素 x 成分)
    # APCS：绝对主成分得分 = 得分 − 虚拟零样本得分
    Z0 = np.zeros((1, X.shape[1]))
    Z0_scores = (Z0 @ loadings) / S[:n_components]
    apcs = scores - Z0_scores                       # (n, k)
    # 对每个元素做 MLR：X_j = b_j0 + Σ_k b_jk · APCS_k
    contrib = np.zeros((n_components, X.shape[1]))  # (源, 元素)
    ones = np.ones((n, 1))
    A = np.hstack([ones, apcs])
    for j in range(X.shape[1]):
        y = X[:, j]
        # 岭回归
        reg = np.linalg.solve(A.T @ A + alpha * np.eye(A.shape[1]), A.T @ y)
        b0, b = reg[0], reg[1:]
        # 各源贡献 = |b_k| * mean(APCS_k)（取绝对值近似贡献量）
        for k in range(n_components):
            contrib[k, j] = abs(b[k]) * np.abs(apcs[:, k]).mean()
    # 归一化为百分比
    total = contrib.sum(axis=0) + 1e-12
    contrib_pct = contrib / total * 100.0          # (源, 元素)
    overall = contrib.sum(axis=1) / total.sum() * 100.0   # 各源总贡献
    # 自动命名：按每源最高载荷元素
    names = []
    for k in range(n_components):
        jtop = int(np.argmax(np.abs(loadings[:, k])))
        names.append(f"源{k+1}({elements[jtop]})")
    out = {"contrib_pct": contrib_pct, "overall_pct": overall,
           "loadings": loadings, "explained": explained,
           "n_components": n_components, "source_names": names,
           "elements": elements}
    if out_dir:
        _plot_contrib(out, out_dir)
    return out


def pmf_nmf(conc, n_components, elements=None, out_dir=None, seed=42):
    """
    PMF 风格的非负矩阵分解（NMF）。conc: 样本 x 元素。
    同时反演源谱 F（n_components x 元素）与源贡献 G（样本 x n_components），全非负。
    """
    from sklearn.decomposition import NMF
    if isinstance(conc, pd.DataFrame):
        elements = list(conc.columns)
        X = conc.to_numpy(float)
    else:
        X = np.asarray(conc, float)
        elements = elements or [f"E{i+1}" for i in range(X.shape[1])]
    X = np.maximum(X, 0)
    model = NMF(n_components=n_components, init="nndsvda", random_state=seed,
                max_iter=2000)
    G = model.fit_transform(X)      # 样本 x 源 贡献
    F = model.components_           # 源 x 元素 源谱
    # 各源对每元素的总贡献
    recon = G @ F
    contrib = np.zeros((n_components, X.shape[1]))
    for k in range(n_components):
        contrib[k, :] = (G[:, k][:, None] * F[k, :]).sum(axis=0)
    total = contrib.sum(axis=0) + 1e-12
    contrib_pct = contrib / total * 100
    overall = contrib.sum(axis=1) / total.sum() * 100
    names = []
    for k in range(n_components):
        jtop = int(np.argmax(F[k, :]))
        names.append(f"因子{k+1}({elements[jtop]})")
    out = {"contrib_pct": contrib_pct, "overall_pct": overall,
           "F": F, "G": G, "source_names": names, "elements": elements,
           "recon_err": np.mean((recon - X) ** 2)}
    if out_dir:
        _plot_contrib(out, out_dir)
    return out


def _plot_contrib(res, out_dir):
    names = res["source_names"]
    elems = res["elements"]
    overall = res["overall_pct"]
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.8))
    # 左：总贡献柱状
    ax = axes[0]
    ax.bar(range(len(names)), overall, color="#4477AA", alpha=0.85)
    ax.set_xticks(range(len(names))); ax.set_xticklabels(names, rotation=25)
    ax.set_ylabel("总贡献率 (%)")
    ax.set_title("各污染源总贡献率")
    for i, v in enumerate(overall):
        ax.text(i, v + 1, f"{v:.1f}%", ha="center", fontsize=9)
    # 右：堆叠贡献
    ax2 = axes[1]
    bottom = np.zeros(len(elems))
    colors = ["#4477AA", "#EE6677", "#228833", "#CCBB44", "#66CCEE"]
    for k in range(len(names)):
        vals = res["contrib_pct"][k, :]
        ax2.bar(range(len(elems)), vals, bottom=bottom,
                color=colors[k % len(colors)], label=names[k], alpha=0.85)
        bottom += vals
    ax2.set_xticks(range(len(elems))); ax2.set_xticklabels(elems)
    ax2.set_ylabel("贡献率 (%)"); ax2.set_title("各元素来源贡献堆叠")
    ax2.legend(fontsize=8, loc="upper right")
    fig.tight_layout()
    path = os.path.join(out_dir, "源贡献率.png")
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"[图] 已保存 {path}")


if __name__ == "__main__":
    # 演示：3 个源混合的合成数据（2 元素 x 3 源）
    rng = np.random.RandomState(1)
    n = 300
    # 源谱：源1 富 Pb/Zn, 源2 富 Cd/Cu, 源3 自然源 As/Cr
    F_true = np.array([
        [1.0, 0.1, 0.1, 0.1, 0.05, 0.05, 5.0, 5.0],   # 源1 工业 Pb/Zn
        [0.1, 5.0, 0.1, 5.0, 0.05, 0.05, 0.5, 0.5],   # 源2 工业 Cd/Cu
        [5.0, 0.1, 5.0, 0.1, 0.1, 5.0, 0.2, 0.2],     # 源3 自然 As/Cr/Ni
    ])
    G_true = rng.dirichlet([3, 2, 5], n) * 100.0       # 样本贡献
    X = G_true @ F_true + rng.normal(0, 0.3, (n, 8))
    X = np.maximum(X, 0)
    elems = ["As", "Cd", "Cr", "Cu", "Hg", "Ni", "Pb", "Zn"]
    print("=== APCS-MLR ===")
    r1 = apcs_mlr(X, elements=elems, n_components=3, out_dir=".")
    print("各源总贡献率:", np.round(r1["overall_pct"], 1), r1["source_names"])
    print("=== PMF-NMF ===")
    r2 = pmf_nmf(X, n_components=3, elements=elems, out_dir=".")
    print("各源总贡献率:", np.round(r2["overall_pct"], 1), r2["source_names"])
    print("重构误差:", round(r2["recon_err"], 3))
