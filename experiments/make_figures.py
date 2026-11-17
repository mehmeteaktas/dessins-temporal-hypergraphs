"""Figures 3, 5, 6 and 7 and the numbers of Tables 6-8, from results/growth_runs.json.

Usage: python -m experiments.make_figures   (after python -m experiments.run_growth)
Output: results/figures/*.pdf|png and results/numbers.json
"""
import json
import os
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from .config import RESULTS_DIR

R = json.load(open(os.path.join(RESULTS_DIR, "growth_runs.json")))
FIG = os.path.join(RESULTS_DIR, "figures")
os.makedirs(FIG, exist_ok=True)
SITES = [s for s in ["DataScience", "AI", "Biology", "Astronomy", "Academia"] if s in R]
NAME = {"DataScience": "Data Science", "AI": "Artificial Intelligence", "Biology": "Biology",
        "Astronomy": "Astronomy", "Academia": "Academia"}
COL = {"DataScience": "#534AB7", "AI": "#9E97E8", "Biology": "#D85A30", "Astronomy": "#1D9E75",
       "Academia": "#BA7517"}
LS = {"DataScience": "-", "AI": "--", "Biology": "-", "Astronomy": "-", "Academia": "-"}


def yr(s):
    d = datetime.strptime(s, "%Y-%m-%d")
    return d.year + (d.timetuple().tm_yday - 1) / 365.25


def arr(runs, key):
    return np.array([[p[key] for p in r["curve"]] for r in runs], float)


def at_beta1(runs, target):
    vals, dates = [], []
    for r in runs:
        b = np.array([p["local"] + p["handle"] for p in r["curve"]])
        i = int(np.searchsorted(b, target))
        if i >= len(b):
            return None, None
        p = r["curve"][i]
        vals.append(100 * (p["local"] - p["handle"]) / (p["local"] + p["handle"]))
        dates.append(p["date"])
    return float(np.mean(vals)), dates[0]


nums = {"profile": {}, "matched": {}, "final": {}, "composition": {}, "bracket": {}, "dates": {}}
for s in SITES:
    d = R[s]["describe"]
    nums["profile"][s] = d
    for rule in ("reply", "hub", "random", "shuffled"):
        for m in (1000, 2000, 5000, 10000, 20000):
            v, dt = at_beta1(R[s]["full"][rule], m)
            nums["matched"].setdefault(rule, {}).setdefault(s, {})[m] = v
            if rule == "reply":
                nums["dates"].setdefault(s, {})[m] = dt
        runs = R[s]["full"][rule]
        loc = np.array([r["totals"].get("local", 0) for r in runs], float)
        han = np.array([r["totals"].get("handle", 0) for r in runs], float)
        nums["final"].setdefault(rule, {})[s] = dict(
            beta1=float((loc + han).mean()), genus=float(han.mean()), local=float(loc.mean()),
            handle=float(han.mean()), handle_fraction=float((2 * han / (loc + han)).mean()),
            netlocal100=float((100 * (loc - han) / (loc + han)).mean()),
            netlocal100_min=float((100 * (loc - han) / (loc + han)).min()),
            netlocal100_max=float((100 * (loc - han) / (loc + han)).max()),
            F=float(np.mean([r["F"] for r in runs])), c=float(np.mean([r["c"] for r in runs])))
    runs = R[s]["full"]["reply"]
    nums["composition"][s] = {k: float(np.mean([r["totals"].get(k, 0) for r in runs]) / d["participations"])
                              for k in ("new", "pendant", "bridge", "local", "handle")}
    smp = R[s]["samples"]
    nums["bracket"][s] = {k: [float(np.mean([100 * r[k]["net_local"] / r[k]["beta1"] for r in smp])),
                              float(np.std([100 * r[k]["net_local"] / r[k]["beta1"] for r in smp]))]
                          for k in ("random", "reply", "ceiling")}
    nums["bracket"][s]["beta1"] = float(np.mean([r["reply"]["beta1"] for r in smp]))
    nums["bracket"][s]["darts"] = float(np.mean([r["darts"] for r in smp]))
json.dump(nums, open(os.path.join(RESULTS_DIR, "numbers.json"), "w"), indent=1, default=str)

# ---------------------------------------------------------------- Figure: main comparison
fig, axes = plt.subplots(2, 2, figsize=(13, 9))
for s in SITES:
    runs = R[s]["full"]["reply"]
    dates = np.array([yr(p["date"]) for p in runs[0]["curve"]])
    loc, han = arr(runs, "local"), arr(runs, "handle")
    b = loc + han
    ok = b[0] > 200
    axes[0, 0].plot(dates[ok], (2 * han / np.maximum(b, 1)).mean(0)[ok], color=COL[s], ls=LS[s], lw=2,
                    label=NAME[s])
    nl = 100 * (loc - han) / np.maximum(b, 1)
    axes[0, 1].plot(b.mean(0)[ok], nl.mean(0)[ok], color=COL[s], ls=LS[s], lw=2, label=NAME[s])
    axes[0, 1].fill_between(b.mean(0)[ok], nl.min(0)[ok], nl.max(0)[ok], color=COL[s], alpha=0.18)
    dl, dh = np.diff(loc, axis=1), np.diff(han, axis=1)
    with np.errstate(invalid="ignore", divide="ignore"):
        ls = np.nanmean(dl / (dl + dh), 0)
    k = 7
    sm = np.convolve(ls, np.ones(k) / k, mode="valid")
    axes[1, 0].plot(dates[1:][k // 2:k // 2 + len(sm)], sm, color=COL[s], ls=LS[s], lw=2, label=NAME[s])
axes[0, 0].set_title("(a) Handle fraction $2g/\\beta_1$ over calendar time", fontsize=11)
axes[0, 0].set_xlabel("year")
axes[0, 0].set_ylabel("$2g/\\beta_1$")
axes[0, 1].set_xscale("log")
axes[0, 1].set_title("(b) Net local faces per 100 cycles at equal $\\beta_1$", fontsize=11)
axes[0, 1].set_xlabel("number of independent cycles $\\beta_1$ (log scale)")
axes[0, 1].set_ylabel("$100\\,(F-c)/\\beta_1$")
axes[1, 0].axhline(0.5, color="#444441", lw=0.8, ls=":")
axes[1, 0].set_title("(c) Local share of newly created cycles (moving average)", fontsize=11)
axes[1, 0].set_xlabel("year")
axes[1, 0].set_ylabel("local / (local + handle)")
kinds = ["new", "pendant", "bridge", "local", "handle"]
kcol = {"new": "#D3D1C7", "pendant": "#B4B2A9", "bridge": "#888780", "local": "#1D9E75", "handle": "#D85A30"}
ax = axes[1, 1]
bottom = np.zeros(len(SITES))
for kd in kinds:
    v = np.array([nums["composition"][s][kd] for s in SITES])
    ax.bar([NAME[s].replace("Artificial Intelligence", "AI") for s in SITES], v, bottom=bottom,
           color=kcol[kd], label=kd)
    for i, (bb, vv) in enumerate(zip(bottom, v)):
        if vv > 0.05:
            ax.text(i, bb + vv / 2, f"{100 * vv:.0f}%", ha="center", va="center", fontsize=8.5)
    bottom += v
ax.set_ylim(0, 1)
ax.set_title("(d) What each participation did", fontsize=11)
ax.legend(frameon=False, fontsize=8.5, ncol=5, loc="upper center", bbox_to_anchor=(0.5, -0.07))
for a in axes.flat[:3]:
    a.legend(frameon=False, fontsize=8.5)
for a in axes.flat:
    for sp in ("top", "right"):
        a.spines[sp].set_visible(False)
plt.tight_layout()
plt.savefig(os.path.join(FIG, "main_comparison.pdf"))
plt.savefig(os.path.join(FIG, "main_comparison.png"), dpi=150)

# ---------------------------------------------------------------- Figure: rules (matched beta1)
RULES = [("reply", "(a) reply rule (main)"), ("hub", "(b) hub rule"), ("random", "(c) random rule"),
         ("shuffled", "(d) shuffled order + random rule")]
fig, axes = plt.subplots(1, 4, figsize=(19, 4.6), sharey=True)
for ax, (rule, title) in zip(axes, RULES):
    for s in SITES:
        runs = R[s]["full"][rule]
        loc, han = arr(runs, "local"), arr(runs, "handle")
        b = (loc + han).mean(0)
        nl = 100 * (loc - han) / np.maximum(loc + han, 1)
        ok = b > 300
        ax.plot(b[ok], nl.mean(0)[ok], color=COL[s], ls=LS[s], lw=2, label=NAME[s])
        ax.fill_between(b[ok], nl.min(0)[ok], nl.max(0)[ok], color=COL[s], alpha=0.18)
    ax.set_xscale("log")
    ax.set_xlabel("$\\beta_1$ (log scale)")
    ax.set_title(title, fontsize=11)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
axes[0].set_ylabel("net local faces per 100 cycles")
axes[0].legend(frameon=False, fontsize=8.5)
plt.tight_layout()
plt.savefig(os.path.join(FIG, "rules.pdf"))
plt.savefig(os.path.join(FIG, "rules.png"), dpi=150)

# ---------------------------------------------------------------- Figure: ablation bars at beta1=10k
fig, ax = plt.subplots(figsize=(10, 4.4))
setups = [("shuffled", "shuffled order, random rule", "#D3D1C7"), ("random", "real order, random rule", "#888780"),
          ("hub", "real order, hub rule", "#7F77DD"), ("reply", "real order, reply rule (main)", "#3C3489")]
x = np.arange(len(SITES))
w = 0.2
for i, (rule, lab, col) in enumerate(setups):
    v = [nums["matched"][rule][s][10000] for s in SITES]
    bars = ax.bar(x + (i - 1.5) * w, v, w, color=col, label=lab)
    for bb, vv in zip(bars, v):
        ax.text(bb.get_x() + bb.get_width() / 2, vv + 0.12, f"{vv:.1f}", ha="center", fontsize=7.5)
ax.set_xticks(x)
ax.set_xticklabels([NAME[s] for s in SITES])
ax.set_ylabel("net local faces per 100 cycles\nat $\\beta_1 = 10{,}000$")
ax.set_ylim(0, 12)
ax.legend(frameon=False, fontsize=8.5, ncol=4, loc="upper center")
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)
plt.tight_layout()
plt.savefig(os.path.join(FIG, "ablation.pdf"))
plt.savefig(os.path.join(FIG, "ablation.png"), dpi=150)

# ---------------------------------------------------------------- Figure: bracket on samples
fig, ax = plt.subplots(figsize=(10, 4.4))
w = 0.26
for i, (k, lab, col) in enumerate((("random", "online, random rule (floor)", "#B4B2A9"),
                                   ("reply", "online, reply rule (main)", "#534AB7"),
                                   ("ceiling", "offline face maximization (ceiling)", "#D85A30"))):
    m = [nums["bracket"][s][k][0] for s in SITES]
    sd = [nums["bracket"][s][k][1] for s in SITES]
    ax.bar(x + (i - 1) * w, m, w, yerr=sd, capsize=3, color=col, label=lab)
ax.set_xticks(x)
ax.set_xticklabels([f"{NAME[s]}\n$\\beta_1\\approx${nums['bracket'][s]['beta1']:.0f}" for s in SITES],
                   fontsize=9)
ax.set_ylabel("net local faces per 100 cycles")
ax.legend(frameon=False, fontsize=8.5)
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)
plt.tight_layout()
plt.savefig(os.path.join(FIG, "bracket.pdf"))
plt.savefig(os.path.join(FIG, "bracket.png"), dpi=150)

print(json.dumps({k: nums[k] for k in ("matched", "bracket", "dates")}, indent=1, default=str))
print(json.dumps(nums["final"], indent=1))
print(json.dumps(nums["composition"], indent=1))
