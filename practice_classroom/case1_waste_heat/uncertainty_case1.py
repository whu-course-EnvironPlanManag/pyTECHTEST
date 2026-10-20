#!/usr/bin/env python3
"""
案例一（工业余热回收）不确定性分析脚本。

选取工业电价作为不确定性参数，做两类分析：
1. 单因素（OAT）情景分析：电价在 0.5x ~ 1.5x 之间变动，观察单位成本节约的变化；
2. 蒙特卡洛模拟：电价服从三角分布，抽样 1000 次，统计 P5 / P50 / P95。

输出：终端摘要 + outputs/ 目录下的 PNG 图与 Markdown 表。
"""

import sys
from pathlib import Path

import numpy as np

# 确保项目根目录在 sys.path 中
_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from pytechtest.engines.full_engine import TechTestFullEngine
from pytechtest.io.yaml_loader import TechTestYAMLLoader

# ---------------------------------------------------------------- 分析设置
N_RUNS = 1000                      # 蒙特卡洛抽样次数（按教学要求）
SEED = 42                          # 随机种子，保证结果可复现
PRICE_BASE = 0.0718                # 基准电价 ($/kWh)
DIST = (0.0503, 0.0718, 0.0933)    # 三角分布 (下限, 众数, 上限) = 0.7x / 1.0x / 1.3x
OAT_FACTORS = (0.5, 0.7, 0.9, 1.0, 1.1, 1.3, 1.5)

CASE_DIR = Path(__file__).resolve().parent
YAML_PATH = CASE_DIR / "student_template.yaml"
OUT_DIR = CASE_DIR / "outputs"


def load_base_config():
    """读取学生配置，作为所有情景的基准。"""
    return TechTestYAMLLoader.load_full(YAML_PATH)


def saving_at(base_cfg, price: float) -> float:
    """在给定电价下重算单位功能成本节约 ($/ref)。"""
    cfg = base_cfg.model_copy(deep=True)
    for side in (cfg.new_technology, cfg.commercial_benchmark):
        for item in side.energy_items:
            if item.energy_source == "Electricity":
                item.unit_price = price
    results = TechTestFullEngine(cfg).run()
    return results.summary.cost_savings_per_ref_volume


def run_oat(base_cfg):
    """单因素情景：电价按倍数缩放。"""
    rows = []
    base_saving = saving_at(base_cfg, PRICE_BASE)
    for factor in OAT_FACTORS:
        price = PRICE_BASE * factor
        saving = saving_at(base_cfg, price)
        rows.append((factor, price, saving, saving / base_saving))
    return rows


def run_monte_carlo(base_cfg):
    """蒙特卡洛：电价服从三角分布，抽样 N_RUNS 次。"""
    rng = np.random.default_rng(SEED)
    prices = rng.triangular(*DIST, N_RUNS)
    savings = np.array([saving_at(base_cfg, p) for p in prices])
    return prices, savings


def plot(prices, savings, base_saving, png_path):
    """绘制直方图 + 累积分布图。

    使用 Pillow 作图：当前沙箱环境下 matplotlib 的渲染后端会直接崩溃。
    """
    from PIL import Image, ImageDraw, ImageFont

    BLUE = (91, 143, 249)
    YELLOW = (246, 189, 22)
    RED = (232, 104, 74)
    GREEN = (90, 216, 166)
    DARK = (51, 51, 51)
    GRID = (229, 231, 235)

    def load_font(size, bold=False):
        candidates = [
            "C:/Windows/Fonts/msyhbd.ttc" if bold else "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/simhei.ttf",
            "C:/Windows/Fonts/arial.ttf",
        ]
        for path in candidates:
            if Path(path).exists():
                try:
                    return ImageFont.truetype(path, size)
                except OSError:
                    continue
        return ImageFont.load_default()

    width, height = 1600, 820
    m_left, m_right, m_top, m_bottom, gap = 100, 50, 170, 100, 110
    panel_w = (width - m_left - m_right - gap) // 2
    x0_left, x0_right = m_left, m_left + panel_w + gap
    y_top, y_bottom = m_top, height - m_bottom
    panel_h = y_bottom - y_top

    canvas = Image.new("RGBA", (width, height), "white")
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    f_title = load_font(36, bold=True)
    f_sub = load_font(20)
    f_axis = load_font(22)
    f_tick = load_font(18)
    f_legend = load_font(19)

    p5, p50, p95 = np.percentile(savings, [5, 50, 95])

    # 横轴范围：按 10 的整数倍取整，两端留白
    lo = int(np.floor(savings.min() / 10) * 10)
    hi = int(np.ceil(savings.max() / 10) * 10)
    span = hi - lo

    def make_x(x0):
        return lambda v: x0 + (v - lo) / span * panel_w

    def make_y(count_max):
        return lambda c: y_bottom - c / count_max * panel_h

    def dashed(draw, p1, p2, fill, width_=2, dash=9):
        length = max(abs(p2[0] - p1[0]), abs(p2[1] - p1[1]))
        steps = max(int(length // dash), 1)
        for i in range(0, steps, 2):
            t0, t1 = i / steps, min((i + 1) / steps, 1.0)
            draw.line(
                [
                    (p1[0] + (p2[0] - p1[0]) * t0, p1[1] + (p2[1] - p1[1]) * t0),
                    (p1[0] + (p2[0] - p1[0]) * t1, p1[1] + (p2[1] - p1[1]) * t1),
                ],
                fill=fill,
                width=width_,
            )

    def vertical_text(text, center, fnt, fill):
        bbox = fnt.getbbox(text)
        tmp = Image.new("RGBA", (bbox[2] - bbox[0] + 8, bbox[3] - bbox[1] + 8), (0, 0, 0, 0))
        ImageDraw.Draw(tmp).text((4 - bbox[0], 4 - bbox[1]), text, font=fnt, fill=fill)
        tmp = tmp.rotate(90, expand=True)
        canvas.alpha_composite(tmp, (int(center[0] - tmp.width / 2), int(center[1] - tmp.height / 2)))

    # 标题
    draw.text((width / 2, 44), "案例一 余热回收 —— 工业电价不确定性分析",
              font=f_title, fill=DARK, anchor="mm")
    draw.text(
        (width / 2, 88),
        f"三角分布 triangular({DIST[0]:.4f}, {DIST[1]:.4f}, {DIST[2]:.4f})，"
        f"N = {N_RUNS}，点估计 = {base_saving:.2f} $/MGal",
        font=f_sub, fill=(102, 102, 102), anchor="mm",
    )

    # ---------------------------------------------------------- 左图：直方图
    mx = make_x(x0_left)
    counts, edges = np.histogram(savings, bins=30, range=(lo, hi))
    # 纵轴取整齐刻度：4 等分，步长为 5 的整数倍
    step = max(5, int(np.ceil(counts.max() / 4 / 5)) * 5)
    count_max = step * 4
    my = make_y(count_max)

    for i in range(5):
        value = step * i
        py = my(value)
        draw.line([(x0_left, py), (x0_left + panel_w, py)], fill=GRID, width=1)
        draw.text((x0_left - 12, py), str(value), font=f_tick,
                  fill=(120, 120, 120), anchor="rm")

    for i, count in enumerate(counts):
        if count == 0:
            continue
        bx0 = mx(edges[i])
        bx1 = mx(edges[i + 1])
        draw.rectangle(
            [(bx0 + 1, my(count)), (bx1 - 1, y_bottom)],
            fill=BLUE + (215,), outline="white", width=2,
        )

    for value, color in ((p5, YELLOW), (p50, RED), (p95, GREEN)):
        dashed(draw, (mx(value), y_top), (mx(value), y_bottom), color, width_=3)

    draw.line([(x0_left, y_top), (x0_left, y_bottom)], fill=(153, 153, 153), width=2)
    draw.line([(x0_left, y_bottom), (x0_left + panel_w, y_bottom)], fill=(153, 153, 153), width=2)

    for tick in range(lo, hi + 1, 20):
        px = mx(tick)
        draw.line([(px, y_bottom), (px, y_bottom + 7)], fill=(153, 153, 153), width=2)
        draw.text((px, y_bottom + 14), str(tick), font=f_tick,
                  fill=(102, 102, 102), anchor="ma")

    draw.text((x0_left + panel_w / 2, y_bottom + 52), "单位功能成本节约 ($/MGal)",
              font=f_axis, fill=DARK, anchor="mm")
    vertical_text("频数", (x0_left - 58, y_top + panel_h / 2), f_axis, DARK)
    draw.text((x0_left + panel_w / 2, y_top - 26), f"抽样分布 (N = {N_RUNS})",
              font=f_axis, fill=DARK, anchor="mm")

    # 图例
    lx, ly = x0_left + 18, y_top + 16
    draw.rounded_rectangle([(lx, ly), (lx + 226, ly + 96)], radius=8,
                           fill=(255, 255, 255, 235), outline=(221, 221, 221), width=1)
    for i, (label, color) in enumerate(
        ((f"P5 = {p5:.2f}", YELLOW), (f"P50 = {p50:.2f}", RED), (f"P95 = {p95:.2f}", GREEN))
    ):
        ty = ly + 26 + i * 26
        draw.line([(lx + 14, ty), (lx + 48, ty)], fill=color, width=3)
        draw.text((lx + 60, ty), label, font=f_legend, fill=DARK, anchor="lm")

    # ---------------------------------------------------------- 右图：CDF
    mx2 = make_x(x0_right)

    def cdf_y(p):
        return y_bottom - p * panel_h

    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rectangle(
        [(mx2(p5), y_top), (mx2(p95), y_bottom)], fill=BLUE + (26,)
    )
    canvas = Image.alpha_composite(canvas, overlay)
    draw = ImageDraw.Draw(canvas)

    for i in range(5):
        p = i / 4
        py = cdf_y(p)
        draw.line([(x0_right, py), (x0_right + panel_w, py)], fill=GRID, width=1)
        draw.text((x0_right - 12, py), f"{int(p * 100)}%", font=f_tick,
                  fill=(120, 120, 120), anchor="rm")

    ordered = np.sort(savings)
    cdf = np.arange(1, len(ordered) + 1) / len(ordered)
    points = [(mx2(v), cdf_y(p)) for v, p in zip(ordered, cdf)]
    draw.line(points, fill=BLUE, width=3, joint="curve")

    dashed(draw, (x0_right, cdf_y(0.5)), (x0_right + panel_w, cdf_y(0.5)),
           (170, 170, 170), width_=2, dash=6)
    for value, color in ((p5, YELLOW), (p50, RED), (p95, GREEN)):
        dashed(draw, (mx2(value), y_top), (mx2(value), y_bottom), color, width_=2)
        py = cdf_y(np.searchsorted(ordered, value) / len(ordered))
        draw.ellipse([(mx2(value) - 6, py - 6), (mx2(value) + 6, py + 6)],
                     fill=color, outline="white", width=2)

    draw.line([(x0_right, y_top), (x0_right, y_bottom)], fill=(153, 153, 153), width=2)
    draw.line([(x0_right, y_bottom), (x0_right + panel_w, y_bottom)], fill=(153, 153, 153), width=2)

    for tick in range(lo, hi + 1, 20):
        px = mx2(tick)
        draw.line([(px, y_bottom), (px, y_bottom + 7)], fill=(153, 153, 153), width=2)
        draw.text((px, y_bottom + 14), str(tick), font=f_tick,
                  fill=(102, 102, 102), anchor="ma")

    draw.text((x0_right + panel_w / 2, y_bottom + 52), "单位功能成本节约 ($/MGal)",
              font=f_axis, fill=DARK, anchor="mm")
    vertical_text("累积概率", (x0_right - 58, y_top + panel_h / 2), f_axis, DARK)
    draw.text((x0_right + panel_w / 2, y_top - 26), "累积分布曲线",
              font=f_axis, fill=DARK, anchor="mm")

    canvas.convert("RGB").save(png_path, optimize=True)


def write_markdown(oat_rows, savings, base_saving, md_path):
    """导出 Markdown 结果表。"""
    p5, p50, p95 = np.percentile(savings, [5, 50, 95])
    mean = savings.mean()
    std = savings.std(ddof=1)
    positive = (savings > 0).mean()
    by_factor = {factor: saving for factor, _, saving, _ in oat_rows}

    lines = [
        "# 案例一 余热回收 —— 不确定性分析结果",
        "",
        "## 1. 抽样设置",
        "",
        "| 项目 | 设置 |",
        "| --- | --- |",
        "| 不确定性参数 | 工业电价 ($/kWh) |",
        "| 基准值 | 0.0718 |",
        f"| 概率分布 | 三角分布 triangular({DIST[0]:.4f}, {DIST[1]:.4f}, {DIST[2]:.4f}) |",
        "| 区间依据 | 0.7x / 1.0x / 1.3x 基准电价 |",
        f"| 抽样次数 | {N_RUNS} |",
        f"| 随机种子 | {SEED} |",
        "",
        "## 2. 单因素（OAT）情景分析",
        "",
        "| 电价倍数 | 电价 ($/kWh) | 成本节约 ($/MGal) | 相对基准 |",
        "| --- | --- | --- | --- |",
    ]
    for factor, price, saving, ratio in oat_rows:
        lines.append(
            f"| {factor:.1f}x | {price:.4f} | {saving:.2f} | {ratio * 100:.2f}% |"
        )

    lines += [
        "",
        "## 3. 蒙特卡洛统计结果",
        "",
        "| 统计量 | 数值 ($/MGal) |",
        "| --- | --- |",
        f"| P5 | {p5:.2f} |",
        f"| P50（中位数） | {p50:.2f} |",
        f"| P95 | {p95:.2f} |",
        f"| 均值 | {mean:.2f} |",
        f"| 标准差 | {std:.2f} |",
        f"| 最小值 | {savings.min():.2f} |",
        f"| 最大值 | {savings.max():.2f} |",
        f"| 点估计（电价 0.0718） | {base_saving:.2f} |",
        f"| 节约为正的概率 | {positive * 100:.1f}% |",
        "",
        "## 4. 结论",
        "",
        f"- 点估计 {base_saving:.2f} $/MGal 与 P50 {p50:.2f} $/MGal 基本重合，中位数偏差 "
        f"{abs(p50 - base_saving) / base_saving * 100:.2f}%。",
        f"- 90% 置信区间为 {p5:.2f} ~ {p95:.2f} $/MGal，宽度约 {p95 - p5:.2f} $/MGal，"
        f"相对点估计约 ±{(p95 - p5) / 2 / base_saving * 100:.1f}%。",
        f"- {N_RUNS} 次抽样中节约为正的比例为 {positive * 100:.1f}%，说明结论对电价波动稳健。",
        "- 电价上浮 30% 时节约仍有约 "
        f"{by_factor[1.3]:.2f} $/MGal，电价下跌 30% 时约 "
        f"{by_factor[0.7]:.2f} $/MGal，均显著为正。",
        "",
        f"> 图件：`{Path('uncertainty_case1.png').as_posix()}`",
        "",
    ]

    md_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    if not YAML_PATH.exists():
        print(f"错误：未找到配置文件 {YAML_PATH}", file=sys.stderr)
        sys.exit(1)

    OUT_DIR.mkdir(exist_ok=True)
    base_cfg = load_base_config()
    base_saving = saving_at(base_cfg, PRICE_BASE)

    print(f"\n{'=' * 60}")
    print("案例一 余热回收 —— 电价不确定性分析")
    print(f"{'=' * 60}")
    print(f"点估计（电价 {PRICE_BASE} $/kWh）：{base_saving:.2f} $/MGal")

    print("\n--- 单因素情景 ---")
    oat_rows = run_oat(base_cfg)
    for factor, price, saving, _ in oat_rows:
        print(f"  {factor:.1f}x  {price:.4f} $/kWh -> {saving:.2f} $/MGal")

    print(f"\n--- 蒙特卡洛 ({N_RUNS} 次) ---")
    prices, savings = run_monte_carlo(base_cfg)
    p5, p50, p95 = np.percentile(savings, [5, 50, 95])
    print(f"  P5 / P50 / P95 = {p5:.2f} / {p50:.2f} / {p95:.2f}")
    print(f"  均值 = {savings.mean():.2f}, 标准差 = {savings.std(ddof=1):.2f}")
    print(f"  最小值 / 最大值 = {savings.min():.2f} / {savings.max():.2f}")
    print(f"  节约为正的概率 = {(savings > 0).mean() * 100:.1f}%")

    png_path = OUT_DIR / "uncertainty_case1.png"
    md_path = OUT_DIR / "uncertainty_case1.md"
    plot(prices, savings, base_saving, png_path)
    write_markdown(oat_rows, savings, base_saving, md_path)

    print(f"\n已导出：{png_path}")
    print(f"已导出：{md_path}\n")


if __name__ == "__main__":
    main()
