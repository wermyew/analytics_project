"""Граф: неориентированный, взвешенный, список смежности.

Вершины — произвольные хешируемые объекты (у нас product_id: int).
Рёбра хранятся в обе стороны: если есть (u, v, w), то есть и (v, u, w).

Почему список смежности, а не матрица:
- граф товаров разреженный (E << V²), матрица V×V = 1000×1000 = 1M ячеек,
  а реальных рёбер ~10⁴–10⁵
- обход соседей O(degree(v)), а не O(V)
"""

from __future__ import annotations


class Graph:
    def __init__(self) -> None:
        # vertex -> list[(neighbor, weight)]
        self._adj: dict = {}

    def add_vertex(self, v) -> None:
        """Добавить вершину без рёбер."""
        if v not in self._adj:
            self._adj[v] = []

    def add_edge(self, u, v, weight: float) -> None:
        """Добавить неориентированное ребро u — v с весом weight.

        Если ребро уже есть — вес перезаписывается.
        Петли (u == v) игнорируются.
        """

        if u == v:

            return

        self.add_vertex(u)
        self.add_vertex(v)

        # обновляем существующее ребро, если есть
        for i, (nbr, _) in enumerate(self._adj[u]):
            if nbr == v:
                self._adj[u][i] = (v, weight)
                break
        else:
            self._adj[u].append((v, weight))

        for i, (nbr, _) in enumerate(self._adj[v]):
            if nbr == u:
                self._adj[v][i] = (u, weight)
                break
        else:
            self._adj[v].append((u, weight))

    def neighbors(self, v) -> list[tuple]:
        """Список (сосед, вес). Пустой, если вершины нет."""

        return self._adj.get(v, [])

    def vertices(self) -> list:
        """Список всех вершин."""

        return list(self._adj.keys())

    def has_vertex(self, v) -> bool:

        return v in self._adj

    def has_edge(self, u, v) -> bool:

        return any(nbr == v for nbr, _ in self._adj.get(u, []))

    def edge_weight(self, u, v):
        """Вес ребра u — v или None, если ребра нет."""
        for nbr, w in self._adj.get(u, []):
            if nbr == v:

                return w

        return None

    def num_vertices(self) -> int:

        return len(self._adj)

    def num_edges(self) -> int:
        """Уникальные рёбра (каждое считается один раз, не дважды)."""

        return sum(len(nbrs) for nbrs in self._adj.values()) // 2

    def components(self) -> int:
        """Число компонент связности (обходом в глубину)."""

        seen = set()
        count = 0

        for start in self._adj:
            if start in seen:

                continue

            count += 1
            stack = [start]
            seen.add(start)

            while stack:
                v = stack.pop()
                for nbr, _ in self._adj[v]:
                    if nbr not in seen:
                        seen.add(nbr)
                        stack.append(nbr)

        return count

    def __repr__(self) -> str:

        return f"Graph(V={self.num_vertices()}, E={self.num_edges()})"