"""Алгоритм Йена: K кратчайших простых путей.

Простой путь — без повторения вершин.
Работает поверх Дейкстры: много раз вызывает её с разными запретами.
"""

from __future__ import annotations
import heapq
from core.dijkstra import dijkstra


def yen_k_shortest_paths(
    graph,
    source,
    target,
    K: int,
) -> list[tuple[list, float]]:
    """K кратчайших простых путей source → target.

    Возвращает список [(path, distance), ...], отсортированный по distance.
    Если путей меньше K — вернёт сколько есть.
    Если путей нет — вернёт [].

    K >= 1.
    """

    if K <= 0:

        return []

    if source == target:

        return [([source], 0.0)]

    # A — найденные пути (в порядке возрастания distance)
    A: list[tuple[list, float]] = []
    # B — куча кандидатов: (distance, counter, path)
    # counter нужен, чтобы heapq не сравнивал списки при равных distance
    B: list[tuple[float, int, list]] = []
    counter = 0

    # 1. первый путь — обычная Дейкстра
    first_path, first_dist = dijkstra(graph, source, target)
    if first_path is None:

        return []

    A.append((first_path, first_dist))

    # 2. ещё K-1 путей
    for k in range(1, K):
        prev_path = A[k - 1][0]

        # для каждой вершины предыдущего пути (кроме последней)
        for i in range(len(prev_path) - 1):
            spur_node = prev_path[i]
            root_path = prev_path[:i + 1]

            # запрещаем рёбра, которые уже использованы другими путями
            # из этого же корня (root_path)
            banned_edges = set()
            for path, _ in A:
                if path[:i + 1] == root_path and len(path) > i + 1:
                    banned_edges.add(frozenset({path[i], path[i + 1]}))

            # запрещаем вершины root_path[:-1], чтобы spur не вернулся назад
            banned_nodes = set(root_path[:-1])

            # ищем spur-путь
            spur_path, spur_dist = dijkstra(
                graph,
                spur_node,
                target,
                banned_edges=banned_edges,
                banned_nodes=banned_nodes,
            )

            if spur_path is None:
                continue

            # склеиваем root + spur (без дублирования spur_node)
            total_path = root_path[:-1] + spur_path

            # проверяем, что путь простой (без повторений)
            if len(total_path) != len(set(total_path)):
                continue

            # считаем distance как сумму весов по рёбрам
            # (не доверяем spur_dist + root_dist из-за float-погрешностей)
            total_dist = _path_distance(graph, total_path)
            if total_dist is None:
                continue

            # не дублируем уже найденные пути и кандидатов
            if any(p == total_path for p, _ in A):
                continue
            if any(p == total_path for _, _, p in B):
                continue

            heapq.heappush(B, (total_dist, counter, total_path))
            counter += 1

        if not B:
            break

        # берём лучший кандидат
        dist, _, path = heapq.heappop(B)
        A.append((path, dist))

    return A


def _path_distance(graph, path: list) -> float | None:
    """Сумма весов рёбер пути. None, если какого-то ребра нет."""

    total = 0.0
    for u, v in zip(path, path[1:]):
        w = graph.edge_weight(u, v)
        if w is None:

            return None

        total += w

    return total