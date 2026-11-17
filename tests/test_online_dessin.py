"""Randomized checks of the growing dessin: incrementally maintained faces equal a full recount,
every dart carries the label of its face, and the conservation law of Corollary 4.3 holds."""
import random

from dessins.growth import run_rule
from dessins.online_dessin import run


def test_random_event_sequences():
    rng = random.Random(3)
    for trial in range(200):
        ev = list({(f"u{rng.randrange(15)}", f"t{rng.randrange(12)}") for _ in range(60)})
        rng.shuffle(ev)
        for policy in ("greedy", "random"):
            D, trace = run(ev, policy, seed=trial)
            assert D.F == D.recount_faces()
            assert sorted(d for m in D.members.values() for d in m) == list(range(D.n))
            assert all(D.label[d] == l for l, m in D.members.items() for d in m)
            beta1 = D.n - len(D.udarts) - len(D.tdarts) + D.c
            assert beta1 == D.counts["local"] + D.counts["handle"]          # beta1 = L + H
            assert D.genus() == D.counts["handle"]                          # g = H
            assert D.F - D.c == D.counts["local"] - D.counts["handle"]      # F - c = L - H


def test_insertion_rules_with_anchors():
    rng = random.Random(7)
    for trial in range(50):
        ev, seen = [], set()
        for _ in range(80):
            u, t = f"u{rng.randrange(12)}", f"t{rng.randrange(10)}"
            if (u, t) in seen:
                continue
            members = [v for v, s in seen if s == t]
            ev.append((u, t, rng.choice(members) if members else None))
            seen.add((u, t))
        for policy in ("reply-pendant", "hub-pendant", "random-pendant"):
            D, trace, _ = run_rule(ev, policy, seed=trial)
            assert D.F == D.recount_faces()
            assert D.genus() == trace.count("handle")


def test_worked_example():
    events = [(1, "a", None), (2, "a", 1), (3, "a", 1), (1, "b", None), (2, "b", 1), (4, "b", 1),
              (3, "c", None), (4, "c", 3)]
    D, trace, _ = run_rule(events, "reply-pendant", seed=0)
    assert trace == ["new", "pendant", "pendant", "pendant", "local", "pendant", "pendant", "handle"]
    assert (D.F, D.c, D.genus()) == (1, 1, 1)
