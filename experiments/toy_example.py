"""The toy hypergraph of the paper: a = {1,2,3}, b = {1,2,4}, c = {3,4}.

1. Table 1: its four rotation systems (sigma0 fixed), with faces, F and genus.
2. Table 3: the worked example (Section 4.8), grown with the reply rule, step by step.
3. The alternative history in which user 4 is placed after 2b in step 6.

Usage: python -m experiments.toy_example
"""

from dessins.growth import run_rule
from dessins.online_dessin import OnlineDessin

# darts 1..8 = 1a 2a 3a 1b 2b 4b 3c 4c ; sigma0 = (1 4)(2 5)(3 7)(6 8)
SIGMA0 = {1: 4, 4: 1, 2: 5, 5: 2, 3: 7, 7: 3, 6: 8, 8: 6}
ROWS = {1: [(1, 2, 3), (4, 6, 5)], 2: [(1, 3, 2), (4, 5, 6)],
        3: [(1, 2, 3), (4, 5, 6)], 4: [(1, 3, 2), (4, 6, 5)]}


def cycles(p):
    seen, out = set(), []
    for i in sorted(p):
        if i not in seen:
            c, j = [], i
            while j not in seen:
                seen.add(j)
                c.append(j)
                j = p[j]
            out.append(tuple(c))
    return out


def table1():
    print("Table 1: rotation systems (faces as cycles of phi = sigma0 sigma1 and of sigma_inf = phi^-1)")
    for row, cyc in ROWS.items():
        s1 = {7: 8, 8: 7}
        for c in cyc:
            for k, d in enumerate(c):
                s1[d] = c[(k + 1) % len(c)]
        phi = {d: SIGMA0[s1[d]] for d in s1}
        inv = {v: k for k, v in phi.items()}
        F = len(cycles(phi))
        g = (2 * 1 - (4 + 3 - 8 + F)) // 2
        print(f"  row {row}: sigma1 {cyc} | phi {cycles(phi)} | sigma_inf {cycles(inv)} | F={F} g={g}")


EVENTS = [(1, "a", None), (2, "a", 1), (3, "a", 1), (1, "b", None), (2, "b", 1), (4, "b", 1),
          (3, "c", None), (4, "c", 3)]
TEXT = ["1 asks a", "2 answers a", "3 answers a", "1 asks b", "2 answers b", "4 answers b",
        "3 asks c", "4 answers c"]


def table3():
    print("\nTable 3: worked example with the reply rule")
    print(f"  {'step':<5}{'event':<13}{'type':<9}{'V':>3}{'E':>3}{'D':>3}{'F':>3}{'c':>3}{'b1':>4}{'g':>3}")
    for k in range(1, len(EVENTS) + 1):
        D, trace, _ = run_rule(EVENTS[:k], "reply-pendant", seed=0)
        V, E = len(D.udarts), len(D.tdarts)
        beta1 = D.n - V - E + D.c
        print(f"  {k:<5}{TEXT[k - 1]:<13}{trace[-1]:<9}{V:>3}{E:>3}{D.n:>3}{D.F:>3}{D.c:>3}{beta1:>4}{D.genus():>3}")


def alternative():
    """Same history, but in step 6 user 4's dart is inserted after 2b instead of after 1b."""
    D = OnlineDessin(len(EVENTS), "greedy", 0)
    dart = {}
    kinds = []
    for k, (u, t, parent) in enumerate(EVENTS, start=1):
        x = D.udarts[u][-1] if D.udarts[u] else None
        y = None
        if D.tdarts[t]:
            y = dart[(2, "b")] if k == 6 else dart[(parent, t)]
        kinds.append(D.add(u, t, x, y))
        dart[(u, t)] = D.n - 1
    print(f"\nAlternative history (step 6 after 2b): {kinds} -> F={D.F}, c={D.c}, genus={D.genus()}")


if __name__ == "__main__":
    table1()
    table3()
    alternative()
