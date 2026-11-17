"""
Online (incremental) dessin of a temporal hypergraph.

Events = first participations (user, thread), processed in time order. Each event inserts one
new dart z into the cyclic order at its user (after dart x) and at its thread (after dart y);
existing rotations are never rearranged. Faces are cycles of phi = sigma0 o sigma1.

Event types (exact, by Euler's formula):
  new     : user and thread both new             F+1, c+1
  pendant : exactly one of them is new           F, c unchanged
  bridge  : both exist, different components     F-1, c-1
  local   : both exist, same component, chosen corners on the SAME face   F+1  (genus same)
  handle  : both exist, same component, corners on DIFFERENT faces        F-1, genus+1
Invariants: beta1 = #local + #handle, genus = #handle, F - c = #local - #handle.

Corner policy
  greedy : for a cycle-creating event, use a face shared by the user and the thread if one
           exists (=> local); otherwise random corners (=> handle). Pendants: random corner.
  random : all corners uniformly at random (random-map growth, reference).

Faces are kept as labelled dart sets; after an insertion, the affected cycles are traced in
lockstep and only the smaller pieces are relabelled, so giant faces are never rescanned.
"""

import random
from collections import defaultdict


class OnlineDessin:
    def __init__(self, n_max, policy="greedy", seed=0):
        self.rng = random.Random(seed)
        self.policy = policy
        self.s0 = [0] * n_max
        self.s1 = [0] * n_max
        self.s1inv = [0] * n_max
        self.phi = [0] * n_max
        self.label = [-1] * n_max
        self.members = {}
        self.next_label = 0
        self.udarts = defaultdict(list)
        self.tdarts = defaultdict(list)
        self.parent = {}
        self.n = 0
        self.c = 0
        self.counts = dict(new=0, pendant=0, bridge=0, local=0, handle=0)

    # ------------------------------------------------------------ components
    def _find(self, a):
        p = self.parent
        while p[a] != a:
            p[a] = p[p[a]]
            a = p[a]
        return a

    # ------------------------------------------------------------ faces
    def _new_label(self, darts):
        lab = self.next_label
        self.next_label += 1
        self.members[lab] = set(darts)
        for d in darts:
            self.label[d] = lab
        return lab

    def _retrace(self, A, z):
        phi, label, members = self.phi, self.label, self.members
        starts = list(dict.fromkeys(A))
        startset = set(starts)
        old = {label[d] for d in starts if d != z and label[d] >= 0}
        cur = {s: s for s in starts}
        seen = {s: [s] for s in starts}
        rep = {s: s for s in starts}
        active = set(starts)
        finished = []

        def find(s):
            while rep[s] != s:
                s = rep[s]
            return s

        while len(active) > 1:
            for s in list(active):
                if s not in active:
                    continue
                nxt = phi[cur[s]]
                if nxt == s:
                    finished.append(seen[s])
                    active.discard(s)
                    inside = set(seen[s])
                    for t in list(active):
                        if t in inside:
                            active.discard(t)
                            rep[t] = s
                    continue
                if nxt in startset and nxt != s:
                    r = find(nxt)
                    if r != s and r in active:
                        active.discard(s)
                        rep[s] = r
                        continue
                cur[s] = nxt
                seen[s].append(nxt)

        for cyc in finished:
            for d in cyc:
                if label[d] >= 0:
                    members[label[d]].discard(d)
            self._new_label(cyc)
        left = [l for l in old if members.get(l)]
        for l in old:
            if l in members and not members[l]:
                del members[l]
        if active:
            (s,) = tuple(active)
            if not left:
                self._new_label(seen[s])
                return
            left.sort(key=lambda l: len(members[l]), reverse=True)
            keep = left[0]
            for l in left[1:]:                      # merge smaller faces into the largest
                for d in members[l]:
                    label[d] = keep
                members[keep] |= members.pop(l)
            for d in seen[s] + ([z] if label[z] < 0 else []):   # traced darts not yet labelled
                if label[d] != keep:
                    if label[d] >= 0 and label[d] in members:
                        members[label[d]].discard(d)
                    label[d] = keep
                    members[keep].add(d)
        else:
            assert not left, "untraced darts left on old faces"

    # ------------------------------------------------------------ insertion
    def add(self, u, t, x_hint=None, y_hint=None, hint_cycles=False):
        """x_hint / y_hint: preferred dart to insert after, at the user / at the thread.
        Used for pendant and bridge events (and cycle events too if hint_cycles)."""
        z = self.n
        self.n += 1
        ud, td = self.udarts[u], self.tdarts[t]
        U, T = ("u", u), ("t", t)
        rng = self.rng
        x = y = None
        if not ud and not td:
            kind = "new"
        elif not ud or not td:
            kind = "pendant"
        else:
            ru, rt = self._find(U), self._find(T)
            if ru != rt:
                kind = "bridge"
            else:
                kind = "cycle"
                if hint_cycles:
                    x, y = x_hint, y_hint
                elif self.policy == "greedy":
                    fu = defaultdict(list)
                    for e in ud:
                        fu[self.label[self.s1inv[e]]].append(e)
                    shared = defaultdict(list)
                    for d in td:
                        f = self.label[d]
                        if f in fu:
                            shared[f].append(d)
                    if shared:
                        f = rng.choice(sorted(shared))
                        x, y = rng.choice(fu[f]), rng.choice(shared[f])
        if kind in ("pendant", "bridge"):
            if ud and x_hint is not None:
                x = x_hint
            if td and y_hint is not None:
                y = y_hint
        if ud and x is None:
            x = rng.choice(ud)
        if td and y is None:
            y = rng.choice(td)

        s0, s1, s1inv = self.s0, self.s1, self.s1inv
        if x is None:
            s0[z] = z
        else:
            s0[z] = s0[x]
            s0[x] = z
        if y is None:
            s1[z] = z
            s1inv[z] = z
        else:
            w = s1[y]
            s1[z] = w
            s1[y] = z
            s1inv[z] = y
            s1inv[w] = z
        A = [z]
        if y is not None:
            A.append(y)
        if x is not None:
            A.append(s1inv[x])
        A.append(s1inv[z])
        for d in A:
            self.phi[d] = s0[s1[d]]

        F_before = len(self.members)
        if kind == "new":
            self._new_label([z])
        else:
            self._retrace(A, z)
        dF = len(self.members) - F_before

        self.parent.setdefault(U, U)
        self.parent.setdefault(T, T)
        if kind == "new":
            self.parent[U] = T
            self.c += 1
        elif kind == "bridge":
            self.parent[self._find(U)] = self._find(T)
            self.c -= 1
        elif kind == "pendant":
            if not ud:
                self.parent[U] = self._find(T)
            else:
                self.parent[T] = self._find(U)
        if kind == "cycle":
            kind = "local" if dF == 1 else "handle"
            assert dF in (1, -1), dF
        elif kind == "bridge":
            assert dF == -1, dF
        elif kind == "pendant":
            assert dF == 0, dF
        self.counts[kind] += 1
        ud.append(z)
        td.append(z)
        return kind

    # ------------------------------------------------------------ checks
    @property
    def F(self):
        return len(self.members)

    def recount_faces(self):
        n, ph = self.n, [self.s0[self.s1[i]] for i in range(self.n)]
        seen, F = [False] * n, 0
        for i in range(n):
            if not seen[i]:
                F += 1
                j = i
                while not seen[j]:
                    seen[j] = True
                    j = ph[j]
        return F

    def genus(self):
        V, E = len(self.udarts), len(self.tdarts)
        chi = V + E - self.n + self.F
        return (2 * self.c - chi) // 2


def run(events, policy="greedy", seed=0, record_every=1):
    """events: list of (user, thread). Returns the dessin and a per-event trace."""
    D = OnlineDessin(len(events), policy, seed)
    trace = []
    for k, (u, t) in enumerate(events):
        kind = D.add(u, t)
        trace.append(kind)
    return D, trace


if __name__ == "__main__":
    # self-test on random event sequences: incremental faces == recount, invariants hold
    rng = random.Random(3)
    for trial in range(40):
        ev = list({(f"u{rng.randrange(15)}", f"t{rng.randrange(12)}") for _ in range(60)})
        rng.shuffle(ev)
        for pol in ("greedy", "random"):
            D, tr = run(ev, pol, seed=trial)
            assert D.F == D.recount_faces()
            assert sorted(d for m in D.members.values() for d in m) == list(range(D.n))
            assert all(D.label[d] == l for l, m in D.members.items() for d in m)
            beta1 = D.n - len(D.udarts) - len(D.tdarts) + D.c
            assert beta1 == D.counts["local"] + D.counts["handle"]
            assert D.genus() == D.counts["handle"]
    # toy: a={1,2,3}, b={1,2,4}, c={3,4} in the order of the worked example
    toy = [(1, "a"), (2, "a"), (3, "a"), (1, "b"), (2, "b"), (4, "b"), (3, "c"), (4, "c")]
    outcomes = {}
    for s in range(200):
        D, tr = run(toy, "random", seed=s)
        outcomes[D.genus()] = outcomes.get(D.genus(), 0) + 1
    print("self-tests passed; toy example, random corners over 200 seeds -> genus counts", outcomes)
    D, tr = run(toy, "greedy", seed=0)
    print("toy with greedy corners:", tr, "genus", D.genus())
