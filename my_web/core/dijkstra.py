"""Алгоритм Дейкстры: кратчайший путь во взвешенном графе.

Работает с неотрицательными весами — у нас веса = 1/общие_покупатели > 0,
так что ограничение соблюдается.

Поддерживает запреты (banned_edges, banned_nodes) — это нужно для алгоритма Йена:
когда Йен «отклоняет» путь, он запрещает часть рёбер и вершин,
чтобы Дейкстра нашёл альтернативу.
"""

from __future__ import annotations
import heapq
import math
from core.heap import MinHeap


def dijkstra(
    graph,
    source,
    target,
    banned_edges: set | None = None,
    banned_nodes: set | None = None,
    use_own_heap: bool = False,
) -> tuple[list | None, float]:
    """Кратчайший путь source → target.

    use_own_heap:
        False — heapq (C, быстро, по умолчанию)
        True  — своя MinHeap (Python, медленнее, но показывает «как устроено»)
    """

    banned_edges = banned_edges or set()
    banned_nodes = banned_nodes or set()

    if source == target:
        return ([source], 0.0)

    if source in banned_nodes or target in banned_nodes:
        return (None, math.inf)

    if not graph.has_vertex(source) or not graph.has_vertex(target):
        return (None, math.inf)

    dist = {source: 0.0}
    prev = {}
    visited = set()

    # ---------- выбор кучи ----------
    if use_own_heap:
        heap = MinHeap()
        heap.push((0.0, source))
        pop = heap.pop
        push = heap.push
    else:
        heap_list = [(0.0, source)]
        pop = lambda: heapq.heappop(heap_list)
        push = lambda item: heapq.heappush(heap_list, item)
        heap = heap_list

    while heap:
        d, v = pop()

        if v in visited:

            continue

        visited.add(v)


        if v == target:

            break

        for nbr, weight in graph.neighbors(v):
            if nbr in banned_nodes:

                continue

            if frozenset({v, nbr}) in banned_edges:

                continue

            nd = d + weight
            if nd < dist.get(nbr, math.inf):
                dist[nbr] = nd
                prev[nbr] = v
                push((nd, nbr))

    if target not in dist:

        return (None, math.inf)

    path = []
    v = target

    while v is not None:
        path.append(v)
        v = prev.get(v)
    path.reverse()

    return (path, dist[target])