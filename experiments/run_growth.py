"""Main experiment of the paper (Sections 6.1, 6.2 and 6.4-6.6).

(A) Full history of every community, real time order, three insertion rules (reply = main,
    hub, random), two seeds each, plus the shuffled ablation (random event order + random rule).
(B) Bracketing on identical samples: 5 samples of 1,000 threads (>= 2 participants) per community;
    online random rule (floor), online reply rule (main), offline face maximization (ceiling).

Output: results/growth_runs.json (resumable: communities already present are skipped).
Usage:  python -m experiments.run_growth [--sites DataScience AI ...] [--samples 5] [--seeds 2]
"""

import argparse
import json
import os
import random
from collections import Counter, defaultdict

from dessins.facemax import maximize_faces
from dessins.growth import RULES, describe, run_rule, trace_curve
from dessins.stackexchange import first_participations

from .config import RESULTS_DIR, SITES, folder


def summary(D, trace):
    return dict(totals=dict(Counter(trace)), genus=D.genus(), F=D.F, c=D.c)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sites", nargs="*", default=list(SITES))
    ap.add_argument("--seeds", type=int, default=2, help="runs per rule (paper: 2)")
    ap.add_argument("--samples", type=int, default=5, help="bracketing samples (paper: 5)")
    ap.add_argument("--sample-threads", type=int, default=1000)
    a = ap.parse_args()

    os.makedirs(RESULTS_DIR, exist_ok=True)
    path = os.path.join(RESULTS_DIR, "growth_runs.json")
    out = json.load(open(path)) if os.path.exists(path) else {}
    for site in a.sites:
        if site in out:
            print(f"{site}: already in {path}, skipped")
            continue
        events, times = first_participations(folder(site))
        res = dict(describe=describe(events, times), full={}, samples=[])
        print(site, len(events), "events", flush=True)

        # (A) full history
        for name, policy in RULES.items():
            for seed in range(a.seeds):
                D, tr, _ = run_rule(events, policy, seed)
                res["full"].setdefault(name, []).append(dict(summary(D, tr), curve=trace_curve(tr, times)))
                print(f"  {name:<8} seed {seed}: F-c = {D.F - D.c}, genus = {D.genus()}", flush=True)
        for seed in range(a.seeds):
            sh = events[:]
            random.Random(900 + seed).shuffle(sh)
            sh = [(u, t, None) for u, t, _ in sh]
            D, tr, _ = run_rule(sh, RULES["random"], seed)
            res["full"].setdefault("shuffled", []).append(dict(summary(D, tr), curve=trace_curve(tr, times)))
            print(f"  shuffled seed {seed}: F-c = {D.F - D.c}, genus = {D.genus()}", flush=True)

        # (B) floor / main / ceiling on the same sub-hypergraphs
        size = defaultdict(int)
        for _, t, _ in events:
            size[t] += 1
        pool = sorted(t for t, k in size.items() if k >= 2)
        rng = random.Random(2024)
        for s in range(a.samples):
            keep = set(rng.sample(pool, a.sample_threads))
            ev = [e for e in events if e[1] in keep]
            rec = {}
            for name in ("random", "reply"):
                D, tr, _ = run_rule(ev, RULES[name], s)
                c = Counter(tr)
                rec[name] = dict(beta1=c["local"] + c["handle"], net_local=c["local"] - c["handle"],
                                 genus=D.genus(), cycle_rate=(c["local"] + c["handle"]) / len(ev))
            fm = maximize_faces([(u, t) for u, t, _ in ev], restarts=2, anneal_factor=20, seed=s)
            rec["ceiling"] = dict(beta1=fm["beta1"], net_local=fm["F"] - fm["c"], genus=fm["genus"])
            rec["darts"] = len(ev)
            res["samples"].append(rec)
            print(f"  sample {s}: beta1 {fm['beta1']}, F-c random {rec['random']['net_local']}, "
                  f"reply {rec['reply']['net_local']}, ceiling {rec['ceiling']['net_local']}", flush=True)
        out[site] = res
        json.dump(out, open(path, "w"))
    print("saved", path)


if __name__ == "__main__":
    main()
