"""Checks: incremental face count = recount; toy example reaches genus 0;
heuristic vs exhaustive minimum genus on small random hypergraphs."""
import itertools
import random
import time
from collections import defaultdict

from dessins.facemax import build, maximize_faces, components

rng = random.Random(1)

# 1. random moves: incremental F must equal full recount
for trial in range(30):
    darts = sorted({(f"u{rng.randrange(12)}", f"t{rng.randrange(8)}") for _ in range(40)})
    H, vertices, V, E = build(darts, rng=rng)
    for _ in range(300):
        if not vertices:
            break
        kind, ds = rng.choice(vertices)
        x, y = rng.sample(ds, 2)
        if kind == "t":
            d = H.try_thread_move(x, y)
            if d is not None:
                F_before = H.F
                H.apply_thread_move(x, y)
                assert H.F == F_before + d, (H.F, F_before, d)
        else:
            d = H.try_user_move(x, y)
            if d is not None:
                F_before = H.F
                H.apply_user_move(x, y)
                assert H.F == F_before + d, (H.F, F_before, d)
        assert H.F == H.recount()
print("[PASS] incremental face count matches recount (30 hypergraphs x 300 random moves)")

# 2. toy hypergraph a={1,2,3}, b={1,2,4}, c={3,4}: minimum genus 0
toy = [(1, "a"), (2, "a"), (3, "a"), (1, "b"), (2, "b"), (4, "b"), (3, "c"), (4, "c")]
r = maximize_faces(toy, restarts=5, seed=0)
print(f"[{'PASS' if r['genus'] == 0 else 'FAIL'}] toy: F={r['F']} genus={r['genus']}")


# 3. heuristic vs exhaustive on 40 small hypergraphs (the validation reported in Section 4.6)
def exhaustive_max_faces(darts):
    by_v = defaultdict(list)
    for i, d in enumerate(darts):
        by_v[("u", d[0])].append(i)
        by_v[("t", d[1])].append(i)
    choices = [(k[0], [[ds[0]] + list(p) for p in itertools.permutations(ds[1:])]) for k, ds in by_v.items()]
    n, best = len(darts), 0
    for combo in itertools.product(*[c for _, c in choices]):
        s0, s1 = [0] * n, [0] * n
        for (kind, _), cyc in zip(choices, combo):
            s = s0 if kind == "u" else s1
            for k, d in enumerate(cyc):
                s[d] = cyc[(k + 1) % len(cyc)]
        ph = [s0[s1[i]] for i in range(n)]
        seen, F = [False] * n, 0
        for i in range(n):
            if not seen[i]:
                F += 1
                j = i
                while not seen[j]:
                    seen[j] = True
                    j = ph[j]
        best = max(best, F)
    return best


rng7, cases = random.Random(7), []
while len(cases) < 40:
    darts = sorted({(f"u{rng7.randrange(6)}", f"t{rng7.randrange(5)}") for _ in range(17)})
    deg = defaultdict(int)
    for u, t in darts:
        deg[u] += 1
        deg[t] += 1
    n_rot = 1
    for k in deg.values():
        for i in range(2, k):
            n_rot *= i
    if 200 <= n_rot <= 60000:
        cases.append((darts, exhaustive_max_faces(darts)))
t0 = time.time()
gaps_hill = [(Fm - maximize_faces(d, restarts=3, anneal_factor=0, seed=i)["F"]) // 2 for i, (d, Fm) in enumerate(cases)]
gaps = [(Fm - maximize_faces(d, restarts=3, anneal_factor=20, seed=i)["F"]) // 2 for i, (d, Fm) in enumerate(cases)]
print(f"[INFO] hill climbing only: optimal in {sum(g == 0 for g in gaps_hill)}/40, "
      f"off by one genus in {sum(g == 1 for g in gaps_hill)}")
print(f"[{'PASS' if all(g == 0 for g in gaps) else 'FAIL'}] annealing + hill climbing: optimal in "
      f"{sum(g == 0 for g in gaps)}/40  ({time.time() - t0:.1f}s)")

# assertions (also picked up by pytest)
assert r["genus"] == 0
assert all(g == 0 for g in gaps), gaps
