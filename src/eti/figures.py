"""Publication-quality charts for the README and reports (matplotlib only)."""
import os
from collections import defaultdict
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

from . import battery, market  # noqa: E402

NAVY, TEAL, AMBER, CORAL, GREY, LIGHT = "#1F3A5F", "#1B998B", "#F4A259", "#E15554", "#8A8F98", "#EEF1F5"
AMS = ZoneInfo("Europe/Amsterdam")
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "axes.titlesize": 12, "axes.titleweight": "bold",
    "axes.titlelocation": "left", "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": "#DDE2E8", "grid.linewidth": 0.7, "axes.edgecolor": GREY,
    "figure.dpi": 110, "savefig.dpi": 160, "savefig.bbox": "tight",
})
CMAP = LinearSegmentedColormap.from_list("eti", [TEAL, "#F7F7F2", CORAL])


def _local(ts):
    return datetime.strptime(ts, "%Y-%m-%dT%H:%MZ").replace(tzinfo=timezone.utc).astimezone(AMS)


def _save(fig, out, name, note):
    fig.text(0.0, -0.02, note, fontsize=7.5, color=GREY, ha="left")
    path = os.path.join(out, name)
    fig.savefig(path)
    plt.close(fig)
    return path


def hero(res, out, note):
    s, b, m, i = res["solar"], res["battery"], res["market"], res["impact"]
    over = i["solar_avoided_t_yearly_avg"] / i["solar_avoided_t_hourly"] - 1
    cards = [("Solar capture rate", f"{m['capture_rate_solar']:.0%}", "of the average power price", TEAL),
             ("Solar IRR (P50)", f"{s['irr_p50']:.1%}", f"P10 {s['irr_p10']:.1%} · P90 {s['irr_p90']:.1%}", NAVY),
             ("Battery IRR", "n/a" if b["irr"] is None else f"{b['irr']:.1%}", "arbitrage only, perfect foresight", CORAL),
             ("CO₂ overstatement", f"+{over:.0%}", "yearly-average vs hourly factor", AMBER)]
    fig, axes = plt.subplots(1, 4, figsize=(12, 2.6))
    for ax, (title, value, sub, color) in zip(axes, cards):
        ax.set_axis_off()
        ax.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax.transAxes, color=LIGHT, zorder=0))
        ax.add_patch(plt.Rectangle((0, 0), 0.03, 1, transform=ax.transAxes, color=color, zorder=1))
        ax.text(0.09, 0.78, title, fontsize=10, color=GREY, transform=ax.transAxes)
        ax.text(0.09, 0.38, value, fontsize=26, fontweight="bold", color=color, transform=ax.transAxes)
        ax.text(0.09, 0.12, sub, fontsize=8.5, color=NAVY, transform=ax.transAxes)
    fig.suptitle("Solar + Storage Investment Lab — key results", x=0.01, ha="left", fontsize=14,
                 fontweight="bold", color=NAVY, y=1.05)
    return _save(fig, out, "hero.png", note)


def capture_rate(res, out, note):
    mcr = res["market"]["monthly_capture_rate"]
    months = [int(k) for k in mcr]
    vals = list(mcr.values())
    fig, ax = plt.subplots(figsize=(8, 3.4))
    ax.fill_between(months, vals, 1.0, where=[v < 1 for v in vals], color=CORAL, alpha=0.18, label="value lost to cannibalisation")
    ax.plot(months, vals, color=NAVY, marker="o", lw=2.2)
    ax.axhline(1.0, color=GREY, ls="--", lw=1)
    ax.set_xticks(range(1, 13), ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"])
    ax.set_ylabel("capture rate")
    ax.set_title("Solar earns least when the sun shines most")
    ax.legend(frameon=False, loc="lower left")
    return _save(fig, out, "capture_rate.png", note)


def price_heatmap(rows, out, note):
    acc = defaultdict(list)
    for ts, p, _s, _f in rows:
        if p is not None:
            t = _local(ts)
            acc[(t.hour, t.month)].append(p)
    grid = [[(sum(acc[(h, m)]) / len(acc[(h, m)])) if acc[(h, m)] else float("nan") for m in range(1, 13)] for h in range(24)]
    fig, ax = plt.subplots(figsize=(8, 4.2))
    im = ax.imshow(grid, aspect="auto", cmap=CMAP, origin="upper")
    ax.set_xticks(range(12), ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"])
    ax.set_yticks(range(0, 24, 3)); ax.set_ylabel("hour (Amsterdam time)"); ax.grid(False)
    ax.set_title("Average day-ahead price by hour and month")
    fig.colorbar(im, ax=ax, label="€/MWh", shrink=0.85)
    return _save(fig, out, "price_heatmap.png", note)


def duck_curve(rows, out, note):
    seasons = {"Winter (DJF)": (12, 1, 2), "Spring (MAM)": (3, 4, 5), "Summer (JJA)": (6, 7, 8), "Autumn (SON)": (9, 10, 11)}
    colors = [NAVY, TEAL, AMBER, CORAL]
    fig, ax = plt.subplots(figsize=(8, 3.6))
    for (name, months), c in zip(seasons.items(), colors):
        acc = defaultdict(list)
        for ts, p, _s, _f in rows:
            t = _local(ts)
            if p is not None and t.month in months:
                acc[t.hour].append(p)
        ax.plot(range(24), [sum(acc[h]) / len(acc[h]) for h in range(24)], color=c, lw=2.2, label=name)
    ax.set_xticks(range(0, 24, 3)); ax.set_xlabel("hour (Amsterdam time)"); ax.set_ylabel("€/MWh")
    ax.set_title("The 'duck curve': midday prices sag as solar grows")
    ax.legend(frameon=False, ncol=4, fontsize=8.5, loc="upper center", bbox_to_anchor=(0.5, -0.18))
    return _save(fig, out, "duck_curve.png", note)


def cannibalisation(rows, res, out, note):
    x = [s for _t, p, s, _f in rows if p is not None]
    y = [p for _t, p, _s, _f in rows if p is not None]
    slope, intercept, r2 = market.ols(x, y)
    fig, ax = plt.subplots(figsize=(8, 3.6))
    hb = ax.hexbin(x, y, gridsize=40, cmap=LinearSegmentedColormap.from_list("b", ["#FFFFFF", TEAL, NAVY]), mincnt=1)
    xs = [min(x), max(x)]
    ax.plot(xs, [intercept + slope * v for v in xs], color=CORAL, lw=2.4,
            label=f"€ {slope * 1000:.1f}/MWh per extra GWh solar · R² {r2:.2f}")
    ax.set_xlabel("national solar output (MWh in the hour)"); ax.set_ylabel("€/MWh"); ax.grid(False)
    ax.set_title("More solar, lower prices (cannibalisation)")
    ax.legend(frameon=False, loc="upper right")
    fig.colorbar(hb, ax=ax, label="hours", shrink=0.85)
    return _save(fig, out, "cannibalisation.png", note)


def irr_distribution(res, out, note):
    sims, s, hurdle = res["irr_simulations_solar"], res["solar"], res["assumptions"]["hurdle_irr"]
    fig, ax = plt.subplots(figsize=(8, 3.4))
    ax.hist([v * 100 for v in sims], bins=40, color=TEAL, alpha=0.85, edgecolor="white")
    ax.axvline(hurdle * 100, color=CORAL, lw=2.2, label=f"hurdle {hurdle:.0%} · P(below) = {s['p_below_hurdle']:.0%}")
    for q, ls in (("irr_p10", ":"), ("irr_p50", "-"), ("irr_p90", ":")):
        ax.axvline(s[q] * 100, color=NAVY, ls=ls, lw=1.4)
    ax.set_xlabel("solar project IRR (%)"); ax.set_ylabel("simulations")
    ax.set_title(f"Return is a distribution, not a number (P10 {s['irr_p10']:.1%} · P50 {s['irr_p50']:.1%} · P90 {s['irr_p90']:.1%})")
    ax.legend(frameon=False, loc="upper left")
    return _save(fig, out, "irr_distribution.png", note)


def tornado(res, out, note):
    base = res["solar"]["irr"] * 100
    items = sorted(res["sensitivity_solar_irr"].items(), key=lambda kv: abs(kv[1][1] - kv[1][0]))
    fig, ax = plt.subplots(figsize=(8, 3.4))
    for i, (name, (low, high)) in enumerate(items):
        ax.barh(i, low * 100 - base, left=base, color=CORAL, height=0.55)
        ax.barh(i, high * 100 - base, left=base, color=TEAL, height=0.55)
    ax.axvline(base, color=NAVY, lw=1.5)
    ax.set_yticks(range(len(items)), [k for k, _ in items])
    ax.set_xlabel("solar IRR (%)"); ax.grid(axis="y", visible=False)
    ax.set_title(f"What moves the return? (base case {base:.1f}%)")
    return _save(fig, out, "tornado.png", note)


def battery_day(rows, out, note, hours=2, eff=0.88):
    days = defaultdict(list)
    for ts, p, _s, _f in rows:
        days[ts[:10]].append(p)
    best = max((d for d, v in days.items() if len(v) == 24 and None not in v),
               key=lambda d: battery.best_daily_spread(days[d], hours, eff)[0])
    prices = days[best]
    gain, (i, j) = battery.best_daily_spread(prices, hours, eff)
    fig, ax = plt.subplots(figsize=(8, 3.4))
    colors = [TEAL if i <= h < i + hours else CORAL if j <= h < j + hours else "#C9D1DB" for h in range(24)]
    ax.bar(range(24), prices, color=colors)
    ax.axhline(0, color=GREY, lw=0.8)
    ax.set_xlabel("hour (UTC)"); ax.set_ylabel("€/MWh")
    ax.set_title(f"Best battery day {best}: charge (teal), discharge (coral) → € {gain:,.0f} per MW")
    return _save(fig, out, "battery_day.png", note)


def co2_methods(res, out, note):
    i = res["impact"]
    labels = ["Solar, yearly-average factor", "Solar, hourly factor", "Battery shifting (per year)"]
    vals = [i["solar_avoided_t_yearly_avg"], i["solar_avoided_t_hourly"], i["battery_shift_t"]]
    fig, ax = plt.subplots(figsize=(8, 3.0))
    bars = ax.barh(labels, vals, color=[AMBER, TEAL, NAVY], height=0.55)
    for b, v in zip(bars, vals):
        ax.text(v, b.get_y() + b.get_height() / 2, f"  {v:,.0f} t", va="center", fontsize=9)
    ax.invert_yaxis(); ax.grid(axis="y", visible=False); ax.set_xlabel("avoided CO₂ (tonnes per year)")
    ax.set_title("Same park, different impact claim: the method matters")
    return _save(fig, out, "co2_methods.png", note)


def make_all(rows, res, out):
    os.makedirs(out, exist_ok=True)
    note = res.get("meta", {}).get("attribution", "")
    return [hero(res, out, note), capture_rate(res, out, note), price_heatmap(rows, out, note),
            duck_curve(rows, out, note), cannibalisation(rows, res, out, note), irr_distribution(res, out, note),
            tornado(res, out, note), battery_day(rows, out, note), co2_methods(res, out, note)]
