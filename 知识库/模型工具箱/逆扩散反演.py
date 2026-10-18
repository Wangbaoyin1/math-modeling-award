# -*- coding: utf-8 -*-
"""
多源逆扩散反演（污染源定位）—— 可运行代码模板
- 对应知识卡 07 §3.2b / 风格库模板 18
- 把污染源位置 s_k、源强 Q_k、扩散宽度 σ_k 当未知量，用高斯扩散核全空间联合反演
- 区别于"拟合单条衰减曲线看 R²"：允许多源叠加，源坐标自动最优
用法：
    from 逆扩散反演 import inverse_diffusion_locate
    src = inverse_diffusion_locate(x, y, c)   # x,y 采样点坐标; c 浓度(或富集系数)
"""
import numpy as np
from scipy.optimize import least_squares
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


def _gauss_kernel(X, Y, sx, sy, sigma):
    """点源高斯核：C = exp(-r^2/(2*sigma^2))，r 为到源(sx,sy)距离。"""
    r2 = (X - sx) ** 2 + (Y - sy) ** 2
    return np.exp(-r2 / (2.0 * sigma ** 2))


def _model(params, X, Y, n_src):
    """合成场：n_src 个源叠加。params = [sx_1,sy_1,sigma_1,Q_1, sx_2,...]。"""
    field = np.zeros_like(X, dtype=float)
    for k in range(n_src):
        sx, sy, sig, Q = params[4 * k: 4 * k + 4]
        field += Q * _gauss_kernel(X, Y, sx, sy, sig)
    return field


def _residual(params, X, Y, C, n_src):
    return (_model(params, X, Y, n_src) - C).ravel()


def inverse_diffusion_locate(x, y, c, n_src=3, n_restarts=8, seed=42,
                             bounds_pct=0.25, sigma_guess=None, out_dir=None):
    """
    多源逆扩散反演。
    x, y: 采样点坐标（同量纲，建议先中心化到 0 附近以利优化）
    c:    采样点浓度/富集系数（标量场）
    n_src: 源数量（先验/肘部/AIC 定）
    返回: dict{coords: [(sx,sy),...], sigma: [...], Q: [...], r2: float, field: 网格合成场}
    """
    x = np.asarray(x, float); y = np.asarray(y, float); c = np.asarray(c, float)
    # 中心化坐标（避免大数导致优化病态）
    x0, y0 = x.mean(), y.mean()
    xs, ys = x - x0, y - y0
    rng = np.random.RandomState(seed)
    # 尺度估计
    xr = xs.max() - xs.min(); yr = ys.max() - ys.min()
    span = max(xr, yr)
    sig0 = sigma_guess or (span / 6.0)          # 扩散宽度初值 ~ 1/6 跨度
    cmax = c.max()
    lb_p = bounds_pct
    # 每个源 4 参数：[sx, sy, sigma, Q]，边界
    lo, hi = [], []
    for _ in range(n_src):
        lo += [xs.min(), ys.min(), span * 0.02, 0.0]      # Q >= 0
        hi += [xs.max(), ys.max(), span * 1.2, cmax * 2.0]
    best = None
    for _ in range(n_restarts):
        p0 = []
        for _ in range(n_src):
            p0 += [rng.uniform(xs.min(), xs.max()),
                   rng.uniform(ys.min(), ys.max()),
                   sig0 * rng.uniform(0.5, 1.5),
                   cmax * rng.uniform(0.3, 1.0)]
        try:
            res = least_squares(_residual, p0, args=(xs, ys, c, n_src),
                                bounds=(lo, hi), method="trf", max_nfev=4000)
            cost = np.sum(res.fun ** 2)
            if best is None or cost < best[0]:
                best = (cost, res.x)
        except Exception:
            continue
    if best is None:
        raise RuntimeError("逆扩散反演失败：所有重启未收敛")
    p = best[1]
    coords, sigmas, Qs = [], [], []
    for k in range(n_src):
        coords.append((p[4 * k] + x0, p[4 * k + 1] + y0))
        sigmas.append(p[4 * k + 2])
        Qs.append(p[4 * k + 3])
    # R^2（合成场 vs 实测）
    pred = _model(p, xs, ys, n_src)
    ss_res = np.sum((pred - c) ** 2)
    ss_tot = np.sum((c - c.mean()) ** 2)
    r2 = 1.0 - ss_res / ss_tot
    out = {"coords": coords, "sigma": sigmas, "Q": Qs, "r2": r2, "x0": x0, "y0": y0}
    if out_dir:
        _plot_result(x, y, c, p, n_src, out, out_dir)
    return out


def _plot_result(x, y, c, params, n_src, out, out_dir):
    """绘制：左=实测散点+反演源标记；右=合成场等值线+残差。"""
    xs, ys = x - out["x0"], y - out["y0"]
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.2))
    ax = axes[0]
    sc = ax.scatter(x, y, c=c, cmap="viridis", s=18, edgecolor="k", linewidths=0.3)
    for k in range(n_src):
        sx, sy = out["coords"][k]
        ax.scatter([sx], [sy], marker="*", s=280, color="#B64342",
                   edgecolor="white", linewidths=1.2, zorder=5)
    ax.set_title("实测场与反演源位置（★=源）")
    ax.set_xlabel("x"); ax.set_ylabel("y"); ax.set_aspect("equal")
    fig.colorbar(sc, ax=ax, label="浓度/富集")
    # 合成场 + 残差
    ax2 = axes[1]
    n = 100
    gx = np.linspace(xs.min(), xs.max(), n)
    gy = np.linspace(ys.min(), ys.max(), n)
    GX, GY = np.meshgrid(gx, gy)
    Z = _model(params, GX, GY, n_src)
    cs = ax2.contourf(GX + out["x0"], GY + out["y0"], Z, 15, cmap="viridis")
    ax2.set_title("反演合成场（$R^2$=%.2f）" % out["r2"])
    ax2.set_xlabel("x"); ax2.set_ylabel("y"); ax2.set_aspect("equal")
    fig.colorbar(cs, ax=ax2, label="合成浓度")
    fig.tight_layout()
    path = os.path.join(out_dir, "逆扩散反演结果.png")
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"[图] 已保存 {path}")


if __name__ == "__main__":
    # 演示：两个高斯源叠加的合成数据
    rng = np.random.RandomState(0)
    n = 200
    x = rng.uniform(0, 100, n)
    y = rng.uniform(0, 100, n)
    true = 5.0 * _gauss_kernel(x, y, 30, 30, 12) + 3.0 * _gauss_kernel(x, y, 70, 75, 10)
    c = true + rng.normal(0, 0.2, n)
    res = inverse_diffusion_locate(x, y, c, n_src=2, out_dir=".")
    print("反演源坐标:", np.round(res["coords"], 1))
    print("反演源强:", np.round(res["Q"], 2))
    print("R² =", round(res["r2"], 3))
    print("（真源: (30,30,Q=5) 与 (70,75,Q=3)）")
