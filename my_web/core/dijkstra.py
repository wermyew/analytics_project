"""Алгоритм Дейкстры: кратчайший путь в взвешенном графе.

Работает с неотрицательными весами — у нас веса = 1/общие_покупатели > 0,
так что ограничение соблюдается.

Поддерживает запреты (banned_edges, banned_nodes) — это нужно для Йена:
когда Йен «отклоняет» путь, он запрещает часть рёбер и вершин,
чтобы Дейкстра нашёл альтернативу.
"""

from __future__ import annotations
import heapq
import math


def dijkstra(
    graph,
    source,
    target,
    banned_edges: set | None = None,
    banned_nodes: set | None = None,
) -> tuple[list | None, float]:
    """Кратчайший путь source → target.

    Параметры:
        graph        — Graph из core.graph
        source       — стартовая вершина
        target       — конечная вершина
        banned_edges — множество frozenset({u, v}), которые нельзя проходить
        banned_nodes — множество вершин, которые нельзя проходить

    Возвращает:
        (path, distance) — path = [source, ..., target], distance = сумма весов
        (None, inf)      — если пути нет

    Если source == target — возвращает ([source], 0.0).
    """

    banned_edges = banned_edges or set()
    banned_nodes = banned_nodes or set()

    if source == target:

        return ([source], 0.0)

    if source in banned_nodes or target in banned_nodes:

        return (None, math.inf)

    if not graph.has_vertex(source) or not graph.has_vertex(target):

        return (None, math.inf)

    # dist[v] = кратчайшее известное расстояние от source до v
    dist = {source: 0.0}
    # prev[v] = предыдущая вершина на кратчайшем пути
    prev = {}
    # heap: (distance, vertex)
    heap = [(0.0, source)]
    visited = set()

    while heap:
        d, v = heapq.heappop(heap)

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
                heapq.heappush(heap, (nd, nbr))

    if target not in dist:

        return (None, math.inf)

    # восстанавливаем путь по prev
    path = []
    v = target

    while v is not None:
        path.append(v)
        v = prev.get(v)
    path.reverse()

    return (path, dist[target])