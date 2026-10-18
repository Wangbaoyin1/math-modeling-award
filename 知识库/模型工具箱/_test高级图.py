# -*- coding: utf-8 -*-
"""自测 6 款新增高级可视化图：验证语法与渲染"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 图表库 import *
import numpy as np

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_demo高级图")
os.makedirs(out, exist_ok=True)
rng = np.random.default_rng(42)

# 15 雷达图
radar_chart(
    ["精度", "速度", "鲁棒性", "可解释性", "成本"],
    [[0.9, 0.7, 0.85, 0.6, 0.5], [0.8, 0.9, 0.7, 0.75, 0.4], [0.6, 0.8, 0.9, 0.5, 0.7]],
    ["方法A", "方法B", "方法C"],
    os.path.join(out, "radar.png"), title="三种方法多维度对比")

# 16 小提琴图
violin_plot(
    [rng.normal(0, 1, 500), rng.normal(1, 1.5, 500), rng.normal(-0.5, 0.8, 500)],
    ["组1", "组2", "组3"], "输出值", os.path.join(out, "violin.png"), title="三组输出分布")

# 17 气泡图
n = 60
bubble_chart(
    rng.uniform(0, 10, n), rng.uniform(0, 10, n),
    rng.uniform(1, 100, n), rng.uniform(0, 1, n),
    "X", "Y", os.path.join(out, "bubble.png"), cbar_label="强度", title="气泡图示例")

# 18 脊线图
ridgeline_plot(
    [rng.normal(i*0.5, 1, 800) for i in range(4)],
    ["2020", "2021", "2022", "2023"], os.path.join(out, "ridge.png"),
    xlabel="值", title="多年份分布演化")

# 19 桑基图
sankey_diagram(
    [100, -60, -40], ["总资源", "去向A", "去向B"],
    os.path.join(out, "sankey.png"), title="资源分配桑基图")

# 20 和弦图
M = np.array([[0, 5, 3, 2],
              [4, 0, 2, 1],
              [1, 2, 0, 6],
              [3, 1, 4, 0]], float)
chord_diagram(M, ["A", "B", "C", "D"], os.path.join(out, "chord.png"), title="关联矩阵和弦图")

# 21 Pareto 前沿
pareto_front(
    np.concatenate([rng.uniform(0, 1, 120), [0.3, 0.5, 0.8]]),
    np.concatenate([rng.uniform(0, 1, 120), [0.4, 0.2, 0.15]]),
    os.path.join(out, "pareto.png"), highlight=122, title="Pareto 前沿示例")

# 22 预测 vs 真实
yt = rng.normal(10, 2, 200)
pred_vs_true(yt, yt + rng.normal(0, 1, 200),
             os.path.join(out, "pred_true.png"), title="预测vs真实示例")

# 23 特征重要性
feature_importance(["价格", "折扣", "销量", "库存", "季节"],
                   [0.35, 0.28, 0.15, 0.12, 0.10],
                   os.path.join(out, "importance.png"))

# 24 收敛曲线
convergence_curve(range(1, 101), 100*np.exp(-np.arange(100)/30) + 5 + rng.normal(0, 0.5, 100),
                  os.path.join(out, "conv.png"), optimal=5)

# 25 预测区间
xx = np.linspace(0, 10, 50)
prediction_band(xx, np.sin(xx), np.sin(xx)-0.3, np.sin(xx)+0.3,
                os.path.join(out, "band.png"), y_true=np.sin(xx)+rng.normal(0, 0.1, 50))

print("=== 11 款新图自测完成（6 高级可视化 + 5 分析图）===")
for f in os.listdir(out):
    p = os.path.join(out, f)
    print(f"{f}: {os.path.getsize(p)} bytes")
