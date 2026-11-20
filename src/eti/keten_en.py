"""Engelse ketenafbeelding voor dashboard 7 (docs/img/chain_en.png), 2400 x 440 px."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

BLOKKEN = [
    ("1  Sources", ["Energy-Charts: prices and", "generation, 37 zones, hourly", "Ember, OWID: annual figures",
                    "ENTSO-E, EIA, NASA POWER", "LevelTen, Pexapark: PPAs"]),
    ("2  Pipeline", ["Python: fetch, align clocks,", "types (eti.pipeline, eti.uurdata)", "SQL: raw > staging > mart",
                     "SQLite and SQL Server", "run: bash run_analyse.sh"]),
    ("3  Analysis", ["Profiles and segments", "Statistics and forecasts", "Hirth regression, battery",
                     "arbitrage, investment cases", "Sensitivity and shock tests"]),
    ("4  Dashboards", ["Tableau Public: Solar and", "storage in Europe (tabs)", "Data in tableau/data_en",
                       "Power BI / Fabric with DAX", "Same figures checked (C02, C03)"]),
    ("5  Checks", ["21 controls, 6 still open", "244 automated tests", "12 external comparisons",
                   "Risk register, 15 risks", "Code on GitHub"]),
]
DONKER, LICHT, RAND, GRIJS, TEKST = "#44403C", "#F5F5F4", "#1F9E89", "#78716C", "#292524"


def main(pad="docs/img/chain_en.png"):
    fig = plt.figure(figsize=(12, 2.2), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 12); ax.set_ylim(0, 2.2); ax.axis("off")
    b, gap, x0 = 2.12, 0.29, 0.07
    for i, (kop, regels) in enumerate(BLOKKEN):
        x = x0 + i * (b + gap)
        ax.add_patch(FancyBboxPatch((x, 0.06), b, 1.62, boxstyle="round,pad=0,rounding_size=0.06",
                                    fc=LICHT, ec=RAND, lw=1.2))
        ax.add_patch(FancyBboxPatch((x, 1.74), b, 0.38, boxstyle="round,pad=0,rounding_size=0.06", fc=DONKER, ec=DONKER))
        ax.text(x + b / 2, 1.93, kop, ha="center", va="center", color="white", fontsize=11, fontweight="bold")
        for j, r in enumerate(regels):
            ax.text(x + 0.1, 1.5 - j * 0.29, r, ha="left", va="center", color=TEKST, fontsize=8.6)
        if i < len(BLOKKEN) - 1:
            ax.add_patch(FancyArrowPatch((x + b + 0.03, 0.87), (x + b + gap - 0.03, 0.87),
                                         arrowstyle="-|>", mutation_scale=12, color=GRIJS, lw=1.5))
    fig.savefig(pad, facecolor="white")
    print(pad)


if __name__ == "__main__":
    main()
