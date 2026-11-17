"""Stack Exchange data as a temporal hypergraph.

Vertices are users, hyperedges are threads (a question, its answers and all comments on them).
An incidence (user, thread) is created by the user's first post in the thread; its anchor is the
author of the parent post (the question for an answer, the commented post for a comment).

Input: the Posts.xml and Comments.xml files of one site from the public Stack Exchange data dump.
"""

import xml.etree.ElementTree as ET
from collections import defaultdict


def load(posts_path, comments_path):
    """Return the posts and comments of a site as a list of nodes
    dict(id, thread, parent, time, user), where parent is the id of the post being replied to."""
    nodes, thread_of = [], {}
    for _, el in ET.iterparse(posts_path, events=("end",)):
        if el.tag != "row":
            continue
        a = el.attrib
        pt, user = a.get("PostTypeId"), a.get("OwnerUserId")
        if pt == "1":                                            # question
            thread_of[a["Id"]] = a["Id"]
            nodes.append(dict(id="p" + a["Id"], thread=a["Id"], parent=None,
                              time=a["CreationDate"], user=user))
        elif pt == "2" and a.get("ParentId"):                    # answer
            thread_of[a["Id"]] = a["ParentId"]
            nodes.append(dict(id="p" + a["Id"], thread=a["ParentId"], parent="p" + a["ParentId"],
                              time=a["CreationDate"], user=user))
        el.clear()
    for _, el in ET.iterparse(comments_path, events=("end",)):
        if el.tag != "row":
            continue
        a = el.attrib
        pid = a.get("PostId")
        if pid in thread_of:                                     # comment on a question or answer
            nodes.append(dict(id="c" + a["Id"], thread=thread_of[pid], parent="p" + pid,
                              time=a["CreationDate"], user=a.get("UserId")))
        el.clear()
    return nodes


def first_participations(folder):
    """Time-ordered events (user, thread, parent_author), one per user's first post in a thread,
    and the list of their timestamps. Posts of deleted accounts (no user id) are dropped."""
    nodes = load(f"{folder}/Posts.xml", f"{folder}/Comments.xml")
    author = {n["id"]: n["user"] for n in nodes}
    first = {}
    for n in sorted(nodes, key=lambda n: (n["time"], n["id"])):
        if not n["user"]:
            continue
        key = (n["user"], n["thread"])
        if key not in first:
            first[key] = (n["time"], author.get(n["parent"]) if n["parent"] else None)
    events = sorted(first, key=lambda d: (first[d][0], d[0], d[1]))
    return [(u, t, first[(u, t)][1]) for u, t in events], [first[d][0] for d in events]


# ------------------------------------------------------------------ static rotations (negative control)
def preorder_positions(nodes):
    """Position of every post in the depth-first walk of its thread's reply tree
    (question -> answers and comments, children ordered by time)."""
    children, roots = defaultdict(list), {}
    for n in nodes:
        if n["parent"] is None:
            roots[n["thread"]] = n
        else:
            children[n["parent"]].append(n)
    for ch in children.values():
        ch.sort(key=lambda n: (n["time"], n["id"]))
    pos = {}
    for root in roots.values():
        k, stack = 0, [root]
        while stack:
            n = stack.pop()
            pos[n["id"]] = k
            k += 1
            stack.extend(reversed(children.get(n["id"], [])))
    return pos


def all_incidences(nodes, pos):
    """For every incidence (user, thread): time of the first post and reply-tree rank."""
    t_first, rank = {}, {}
    for n in nodes:
        if not n["user"] or n["id"] not in pos:
            continue
        d = (n["user"], n["thread"])
        if d not in t_first or n["time"] < t_first[d]:
            t_first[d] = n["time"]
        rank[d] = min(rank.get(d, 1 << 60), pos[n["id"]])
    return t_first, rank


def dessin_stats(darts, t_first, thread_key=None, rng=None):
    """Static dessin: threads around each user ordered by time; users inside each thread ordered
    by thread_key (a dict on darts) or shuffled with rng. Returns D, V, E, F, genus, beta1."""
    idx = {d: i for i, d in enumerate(darts)}
    n = len(darts)
    by_user, by_thread = defaultdict(list), defaultdict(list)
    for d in darts:
        by_user[d[0]].append(d)
        by_thread[d[1]].append(d)
    s0, s1 = [0] * n, [0] * n
    for ds in by_user.values():
        ds.sort(key=lambda d: (t_first[d], d[1]))
        for k, d in enumerate(ds):
            s0[idx[d]] = idx[ds[(k + 1) % len(ds)]]
    for ds in by_thread.values():
        if rng is not None:
            rng.shuffle(ds)
        else:
            ds.sort(key=lambda d: (thread_key[d], d[0]))
        for k, d in enumerate(ds):
            s1[idx[d]] = idx[ds[(k + 1) % len(ds)]]
    phi = [s0[s1[i]] for i in range(n)]
    seen, F = [False] * n, 0
    for i in range(n):
        if not seen[i]:
            F += 1
            j = i
            while not seen[j]:
                seen[j] = True
                j = phi[j]
    comp, c = [-1] * n, 0
    for i in range(n):
        if comp[i] == -1:
            stack = [i]
            while stack:
                x = stack.pop()
                if comp[x] == -1:
                    comp[x] = c
                    stack += [s0[x], s1[x]]
            c += 1
    V, E = len(by_user), len(by_thread)
    g = (2 * c - (V + E - n + F)) // 2
    return dict(D=n, V=V, E=E, F=F, c=c, genus=g, beta1=n - V - E + c)
