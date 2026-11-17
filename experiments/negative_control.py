"""Negative control (Section 6.3): rotations read directly from the data.

For random samples of N threads (>= 2 participants) the hypergraph is kept fixed and only the
rotations change:
  time     : threads around a user by time; users inside a thread by time of first post
  tree     : threads around a user by time; users inside a thread in reply-tree (preorder) order
  shuffled : threads around a user by time; users inside a thread in random order (mean of 10)
  random   : both rotations random (mean of 10)
  facemax  : rotations chosen to maximize faces (annealing + hill climbing)
Reported: net local faces per 100 cycles, 100 (F - c) / beta1.

Output: results/negative_control.json and results/negative_control.png
Usage:  python -m experiments.negative_control [--sites DataScience Biology] [--samples 5]
"""

import argparse
import json
import os
import random
import statistics as st
from collections import defaultdict

from dessins.facemax import build, components, maximize_faces
from dessins.stackexchange import all_incidences, dessin_stats, load, preorder_positions

from .config import RESULTS_DIR, folder

KINDS = ["random", "shuffled", "time", "tree", "facemax"]
LABELS = {"random": "random (both)", "shuffled": "shuffled in thread", "time": "timestamp",
          "tree": "reply tree", "facemax": "face-maximizing"}
COLORS = {"random": "#B4B2A9", "shuffled": "#888780", "time": "#1D9E75", "tree": "#534AB7",
          "facemax": "#D85A30"}


def tree_differs_share(t_first, rank):
    """Share of threads (>= 3 participants) whose reply-tree order differs from the time order
    as a cyclic order."""
    by_t = defaultdict(list)
    for d in t_first:
        by_t[d[1]].append(d)
    big = [ds for ds in by_t.values() if len(ds) >= 3]
    diff = 0
    for ds in big:
        a = sorted(ds, key=lambda d: (t_first[d], d[0]))
        b = sorted(ds, key=lambda d: (rank[d], d[0]))
        k = a.index(b[0])
        diff += a[k:] + a[:k] != b
    return diff / len(big), len(big)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sites", nargs="*", default=["DataScience", "Biology"])
    ap.add_argument("--sizes", default="250,500,1000,2000")
    ap.add_argument("--samples", type=int, default=5)
    a = ap.parse_args()
    os.makedirs(RESULTS_DIR, exist_ok=True)
    sizes = [int(s) for s in a.sizes.split(",")]
    rng = random.Random(1)
    rows, info = [], {}
    for name in a.sites:
        nodes = load(f"{folder(name)}/Posts.xml", f"{folder(name)}/Comments.xml")
        t_first, rank = all_incidences(nodes, preorder_positions(nodes))
        share, n_big = tree_differs_share(t_first, rank)
        info[name] = dict(threads_ge3=n_big, share_tree_order_differs_from_time=share)
        print(f"{name}: reply-tree order differs from time order in {share:.1%} of {n_big} threads")
        darts_of = defaultdict(list)
        for d in t_first:
            darts_of[d[1]].append(d)
        pool = [t for t, ds in darts_of.items() if len(ds) >= 2]
        for N in sizes:
            for s in range(a.samples):
                darts = [d for t in rng.sample(pool, N) for d in darts_of[t]]
                c = components(darts)
                time_ = dessin_stats(darts, t_first, t_first)
                tree = dessin_stats(darts, t_first, rank)
                beta1 = tree["beta1"]
                F = dict(time=time_["F"], tree=tree["F"],
                         shuffled=st.mean(dessin_stats(darts, t_first, rng=rng)["F"] for _ in range(10)),
                         random=st.mean(build(darts, rng=rng)[0].F for _ in range(10)),
                         facemax=maximize_faces(darts, restarts=2, anneal_factor=20, seed=s + N)["F"])
                rec = dict(site=name, N=N, sample=s, beta1=beta1, c=c,
                           **{f"local100_{k}": 100 * (v - c) / beta1 if beta1 else 0.0 for k, v in F.items()})
                rows.append(rec)
                print(f"  N={N:<5} sample {s}: beta1 {beta1:>5} | "
                      + "  ".join(f"{k} {rec['local100_' + k]:.1f}" for k in KINDS), flush=True)
    json.dump(dict(info=info, samples=rows), open(os.path.join(RESULTS_DIR, "negative_control.json"), "w"),
              indent=1)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    fig, axes = plt.subplots(1, len(a.sites), figsize=(7 * len(a.sites), 4.6), sharey=False, squeeze=False)
    for ax, name in zip(axes[0], a.sites):
        x = np.arange(len(sizes))
        for i, k in enumerate(KINDS):
            vals = [[r[f"local100_{k}"] for r in rows if r["site"] == name and r["N"] == N] for N in sizes]
            ax.bar(x + (i - 2) * 0.16, [st.mean(v) for v in vals], 0.16,
                   yerr=[st.pstdev(v) for v in vals], color=COLORS[k], label=LABELS[k])
        ax.set_xticks(x)
        ax.set_xticklabels([f"{N} threads" for N in sizes])
        ax.set_title(name)
        ax.set_ylabel("net local faces per 100 cycles")
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
    axes[0][0].legend(frameon=False, fontsize=8)
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, "negative_control.png"), dpi=160)
    print("saved", os.path.join(RESULTS_DIR, "negative_control.json"))


if __name__ == "__main__":
    main()
