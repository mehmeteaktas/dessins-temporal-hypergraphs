"""Growing a dessin from a temporal hypergraph with an insertion rule.

Events are (vertex, hyperedge, anchor_vertex) in time order. For every event a new dart is
inserted; cycle-closing events always use a face shared by the vertex and the hyperedge when one
exists (shared-face search). The rule decides the corners for all other events:

  reply  ("reply-pendant") : at the hyperedge, right after the anchor's dart (fallback: the
                             hyperedge's first dart); at the vertex, after its most recent hyperedge
  hub    ("hub-pendant")   : at the hyperedge, after the dart of its most active vertex so far
  random ("random-pendant"): uniformly random corners (the floor)
"""

from collections import Counter, defaultdict
from itertools import combinations

import numpy as np

from .online_dessin import OnlineDessin

KINDS = ("new", "pendant", "bridge", "local", "handle")
RULES = {"reply": "reply-pendant", "hub": "hub-pendant", "random": "random-pendant"}


def run_rule(events, policy, seed):
    """Grow the dessin. policy is one of RULES.values() (or "reply-all": reply placement for
    every event, without the shared-face search). Returns (dessin, trace of event kinds, stats)."""
    D = OnlineDessin(len(events), "greedy", seed)
    D.darts_user = []
    dart_of = {}
    trace = []
    stats = Counter()
    for u, t, parent in events:
        x_hint = y_hint = None
        if policy == "hub-pendant":
            if D.udarts[u]:
                x_hint = D.udarts[u][-1]
            if D.tdarts[t]:
                y_hint = max(D.tdarts[t], key=lambda d: (len(D.udarts[D.darts_user[d]]), -d))
        elif policy != "random-pendant":
            if D.udarts[u]:
                x_hint = D.udarts[u][-1]
            if D.tdarts[t]:
                if parent and parent != u and (parent, t) in dart_of:
                    y_hint = dart_of[(parent, t)]
                    stats["anchor_used"] += 1
                else:
                    y_hint = D.tdarts[t][0]
                    stats["fallback_first_dart"] += 1
        hint_cycles = policy == "reply-all" and x_hint is not None and y_hint is not None
        kind = D.add(u, t, x_hint, y_hint, hint_cycles=hint_cycles)
        dart_of[(u, t)] = D.n - 1
        D.darts_user.append(u)
        trace.append(kind)
    assert D.F == D.recount_faces()
    return D, trace, stats


def trace_curve(trace, times, n_points=100):
    """Cumulative event counts at n_points equally spaced positions of the history."""
    cum = Counter()
    marks = {int(len(trace) * k / n_points) - 1 for k in range(1, n_points + 1)}
    out = []
    for i, k in enumerate(trace):
        cum[k] += 1
        if i in marks:
            out.append(dict(i=i + 1, date=times[i][:10], **{k_: cum[k_] for k_ in KINDS}))
    return out


def describe(events, times):
    """Order-free profile of a temporal hypergraph (Table 5 of the paper)."""
    members, deg = defaultdict(set), Counter()
    for u, t, _ in events:
        members[t].add(u)
        deg[u] += 1
    sizes = np.array([len(v) for v in members.values()])
    d = np.sort(np.array(list(deg.values())))[::-1]
    pairs = Counter()
    for us in members.values():
        if len(us) <= 60:                      # very large threads are skipped for pair counting
            for a, b in combinations(sorted(us), 2):
                pairs[(a, b)] += 1
    replies_to_other = sum(1 for u, _, p in events if p and p != u)
    return dict(first_year=times[0][:4], last_year=times[-1][:4], threads=len(members),
                users=len(deg), participations=len(events),
                participants_per_thread=float(sizes.mean()),
                share_threads_3plus=float((sizes >= 3).mean()),
                share_users_single_thread=float((d == 1).mean()),
                top1pct_share_of_participations=float(d[:max(1, len(d) // 100)].sum() / d.sum()),
                repeat_pair_rate=sum(1 for v in pairs.values() if v >= 2) / len(pairs),
                share_participations_replying_to_someone=replies_to_other / len(events))
