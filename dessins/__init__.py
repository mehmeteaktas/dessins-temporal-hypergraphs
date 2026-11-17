"""Dessins d'enfants of temporal hypergraphs.

Modules
-------
online_dessin  : the growing dessin (incremental rotation system, exact event classification)
facemax        : offline face maximization (heuristic minimum-genus embedding), the "ceiling"
growth         : insertion rules (reply, hub, random), event traces and order-free statistics
stackexchange  : loading Stack Exchange dumps into temporal hypergraphs; static rotations
"""

from .online_dessin import OnlineDessin
from .facemax import maximize_faces
from .growth import RULES, KINDS, run_rule, describe, trace_curve

__all__ = ["OnlineDessin", "maximize_faces", "RULES", "KINDS", "run_rule", "describe", "trace_curve"]
