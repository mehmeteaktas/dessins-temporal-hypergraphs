"""
Face-maximizing rotations for hypergraph dessins (= heuristic minimum-genus embedding).

Darts d = (user, thread). sigma0 = cyclic order at users, sigma1 = cyclic order at threads,
faces = cycles of phi = sigma0 o sigma1  (phi[d] = sigma0[sigma1[d]]).
Users, threads, darts and components are fixed, so maximizing faces F <=> minimizing genus.

Move: take a dart x at a vertex with >= 3 darts and re-insert it right after another dart y
of the same vertex (p = predecessor of x).
  thread move: sigma1' = sigma1 o pi with pi = (p x y)            => phi' = phi o (p x y)
  user move  : sigma0' = sigma0 o pi                              => phi' = phi o (p' x' y')
               with p' = sigma1^-1(p), x' = sigma1^-1(x), y' = sigma1^-1(y)
and (p x y) = (p y) o (p x), so Delta F in {-2, 0, +2} is read off from face labels in O(1):
  p, x, y on one face C : +2 if x lies on the arc (y, p] of C, else 0
  p, y on one face, x elsewhere : 0
  p, y on different faces       : 0 if x is on one of them, else -2
Accepted moves relabel only the faces through p, x, y.

Search: first-improvement hill climbing over random vertex/dart/target orders, optional
sideways (Delta F = 0) moves, several restarts; keeps the best rotation found.
"""

import random
from collections import defaultdict


class Hypermap:
    def __init__(self, darts, s0, s1):
        self.n = len(darts)
        self.darts = darts
        self.s0, self.s1 = list(s0), list(s1)
        self.s0inv = [0] * self.n
        self.s1inv = [0] * self.n
        for i in range(self.n):
            self.s0inv[self.s0[i]] = i
            self.s1inv[self.s1[i]] = i
        self.phi = [self.s0[self.s1[i]] for i in range(self.n)]
        self.face = [-1] * self.n
        self.pos = [0] * self.n
        self.flen = {}
        self.next_id = 0
        for i in range(self.n):
            if self.face[i] == -1:
                self._trace(i)
        self.F = len(self.flen)

    def _trace(self, start):
        fid = self.next_id
        self.next_id += 1
        k, j = 0, start
        while True:
            self.face[j] = fid
            self.pos[j] = k
            k += 1
            j = self.phi[j]
            if j == start:
                break
        self.flen[fid] = k
        return fid

    def _delta(self, p, x, y):
        fp, fx, fy = self.face[p], self.face[x], self.face[y]
        if fp == fy:
            if fx != fp:
                return 0
            L = self.flen[fp]
            dyx = (self.pos[x] - self.pos[y]) % L
            dyp = (self.pos[p] - self.pos[y]) % L
            return 2 if 0 < dyx <= dyp else 0
        return 0 if fx in (fp, fy) else -2

    def _apply_phi(self, p, x, y):
        old = {self.face[p], self.face[x], self.face[y]}
        ph = self.phi
        ph[p], ph[x], ph[y] = ph[x], ph[y], ph[p]
        for f in old:
            del self.flen[f]
        # every dart of the old faces lies on a new face through p, x or y
        fresh = self.next_id
        for s in (p, x, y):
            if self.face[s] < fresh:          # not yet relabeled in this update
                self._trace(s)
        self.F = len(self.flen)

    # ---------------------------------------------------------------- moves
    def try_thread_move(self, x, y):
        """Move dart x to right after y in its thread (sigma1). Returns Delta F (not applied)."""
        p = self.s1inv[x]
        if y == x or y == p:
            return None
        return self._delta(p, x, y)

    def apply_thread_move(self, x, y):
        p = self.s1inv[x]
        s, q = self.s1[x], self.s1[y]
        self.s1[p], self.s1[y], self.s1[x] = s, x, q
        self.s1inv[s], self.s1inv[x], self.s1inv[q] = p, y, x
        self._apply_phi(p, x, y)

    def try_user_move(self, x, y):
        p = self.s0inv[x]
        if y == x or y == p:
            return None
        return self._delta(self.s1inv[p], self.s1inv[x], self.s1inv[y])

    def apply_user_move(self, x, y):
        p = self.s0inv[x]
        pp, xx, yy = self.s1inv[p], self.s1inv[x], self.s1inv[y]
        s, q = self.s0[x], self.s0[y]
        self.s0[p], self.s0[y], self.s0[x] = s, x, q
        self.s0inv[s], self.s0inv[x], self.s0inv[q] = p, y, x
        self._apply_phi(pp, xx, yy)

    def recount(self):
        """Face count from scratch (for checking)."""
        ph = [self.s0[self.s1[i]] for i in range(self.n)]
        seen, F = [False] * self.n, 0
        for i in range(self.n):
            if not seen[i]:
                F += 1
                j = i
                while not seen[j]:
                    seen[j] = True
                    j = ph[j]
        return F


# -------------------------------------------------------------------- building
def build(darts, order_key=None, rng=None):
    """Rotations: by order_key (dict dart -> sortable) or random if rng given."""
    idx = {d: i for i, d in enumerate(darts)}
    n = len(darts)
    by_user, by_thread = defaultdict(list), defaultdict(list)
    for d in darts:
        by_user[d[0]].append(d)
        by_thread[d[1]].append(d)
    s0, s1 = [0] * n, [0] * n
    for groups, s in ((by_user, s0), (by_thread, s1)):
        for ds in groups.values():
            if rng is not None:
                rng.shuffle(ds)
            elif order_key is not None:
                ds.sort(key=lambda d: order_key[d])
            for k, d in enumerate(ds):
                s[idx[d]] = idx[ds[(k + 1) % len(ds)]]
    vertices = [("t", [idx[d] for d in ds]) for ds in by_thread.values() if len(ds) >= 3] + \
               [("u", [idx[d] for d in ds]) for ds in by_user.values() if len(ds) >= 3]
    return Hypermap(darts, s0, s1), vertices, len(by_user), len(by_thread)


def components(darts):
    parent = {}

    def find(a):
        while parent.setdefault(a, a) != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for u, t in darts:
        parent[find(("u", u))] = find(("t", t))
    return len({find(("u", u)) for u, _ in darts})


# -------------------------------------------------------------------- search
def anneal(H, vertices, rng, steps, T0=1.5, T1=0.05):
    """Simulated annealing with random relocation moves; ends at the best rotation seen."""
    import math
    if not vertices or steps <= 0:
        return
    weights = [len(ds) for _, ds in vertices]
    picks = rng.choices(range(len(vertices)), weights=weights, k=steps)
    bestF, best_s = H.F, (H.s0[:], H.s1[:])
    for k, vi in enumerate(picks):
        T = T0 * (T1 / T0) ** (k / steps)
        kind, ds = vertices[vi]
        x, y = rng.sample(ds, 2)
        d = H.try_thread_move(x, y) if kind == "t" else H.try_user_move(x, y)
        if d is None:
            continue
        if d >= 0 or rng.random() < math.exp(d / T):
            (H.apply_thread_move if kind == "t" else H.apply_user_move)(x, y)
            if H.F > bestF:
                bestF, best_s = H.F, (H.s0[:], H.s1[:])
    if H.F < bestF:
        H.__init__(H.darts, *best_s)


def maximize_faces(darts, order_key=None, restarts=3, max_passes=30, sideways=0.05,
                   max_targets=40, anneal_factor=20, seed=0):
    """Annealing + hill climbing on rotations. Returns dict with best F, genus, and stats."""
    rng = random.Random(seed)
    c = components(darts)
    best = None
    for r in range(restarts):
        start_rng = rng if (r > 0 or order_key is None) else None
        H, vertices, V, E = build(darts, order_key, start_rng)
        F0 = H.F
        anneal(H, vertices, rng, anneal_factor * len(darts))
        for _ in range(max_passes):
            improved = False
            rng.shuffle(vertices)
            for kind, ds in vertices:
                try_m = H.try_thread_move if kind == "t" else H.try_user_move
                app_m = H.apply_thread_move if kind == "t" else H.apply_user_move
                for x in rng.sample(ds, len(ds)):
                    targets = ds if len(ds) <= max_targets else rng.sample(ds, max_targets)
                    for y in targets:
                        d = try_m(x, y)
                        if d is None:
                            continue
                        if d > 0 or (d == 0 and rng.random() < sideways):
                            app_m(x, y)
                            if d > 0:
                                improved = True
                            break
            if not improved:
                break
        if best is None or H.F > best["F"]:
            D = len(darts)
            g2 = 2 * c - (V + E - D + H.F)
            beta1 = D - V - E + c
            best = dict(F=H.F, F_start=F0, D=D, V=V, E=E, c=c, beta1=beta1, two_g=g2,
                        genus=g2 // 2, handle_frac=g2 / beta1 if beta1 else 0.0,
                        local_frac=(H.F - c) / beta1 if beta1 else 0.0, hypermap=H)
    return best
