"""Unit-тесты Graph, dijkstra, yen."""

from __future__ import annotations
import math
import pytest
from core.graph import Graph
from core.dijkstra import dijkstra
from core.yen import yen_k_shortest_paths


# ============================================================
# Graph
# ============================================================

def test_graph_empty():
    g = Graph()
    assert g.num_vertices() == 0
    assert g.num_edges() == 0
    assert g.vertices() == []
    assert g.neighbors(1) == []


def test_graph_add_edge_both_directions():
    g = Graph()
    g.add_edge(1, 2, 0.5)
    assert g.has_edge(1, 2)
    assert g.has_edge(2, 1)          # неориентированный
    assert g.edge_weight(1, 2) == 0.5
    assert g.edge_weight(2, 1) == 0.5


def test_graph_update_weight():
    g = Graph()
    g.add_edge(1, 2, 1.0)
    g.add_edge(1, 2, 0.1)
    assert g.edge_weight(1, 2) == 0.1
    assert g.num_edges() == 1        # не задвоилось


def test_graph_ignore_self_loop():
    g = Graph()
    g.add_edge(1, 1, 1.0)
    assert g.num_vertices() == 0
    assert g.num_edges() == 0


def test_graph_num_edges():
    g = Graph()
    g.add_edge(1, 2, 1.0)
    g.add_edge(2, 3, 1.0)
    g.add_edge(1, 3, 1.0)
    assert g.num_vertices() == 3
    assert g.num_edges() == 3


def test_graph_components_one():
    g = Graph()
    g.add_edge(1, 2, 1.0)
    g.add_edge(2, 3, 1.0)
    assert g.components() == 1


def test_graph_components_many():
    g = Graph()
    g.add_edge(1, 2, 1.0)
    g.add_edge(3, 4, 1.0)
    g.add_edge(5, 6, 1.0)
    assert g.components() == 3


def test_graph_has_vertex():
    g = Graph()
    g.add_edge(1, 2, 1.0)
    assert g.has_vertex(1)
    assert g.has_vertex(2)
    assert not g.has_vertex(99)


# ============================================================
# Dijkstra
# ============================================================

def _make_simple_graph():
    """1 — 2 — 3, плюс 1 — 3 напрямую (дороже)."""

    g = Graph()
    g.add_edge(1, 2, 1.0)
    g.add_edge(2, 3, 1.0)
    g.add_edge(1, 3, 3.0)

    return g


def test_dijkstra_basic():
    g = _make_simple_graph()
    path, dist = dijkstra(g, 1, 3)
    assert path == [1, 2, 3]
    assert dist == 2.0


def test_dijkstra_same_source_target():
    g = _make_simple_graph()
    path, dist = dijkstra(g, 1, 1)
    assert path == [1]
    assert dist == 0.0


def test_dijkstra_no_path():
    g = Graph()
    g.add_edge(1, 2, 1.0)
    g.add_edge(3, 4, 1.0)
    path, dist = dijkstra(g, 1, 4)
    assert path is None
    assert math.isinf(dist)


def test_dijkstra_banned_edge():
    g = _make_simple_graph()
    path, dist = dijkstra(g, 1, 3, banned_edges={frozenset({1, 2})})
    assert path == [1, 3]
    assert dist == 3.0


def test_dijkstra_banned_node():
    g = _make_simple_graph()
    path, dist = dijkstra(g, 1, 3, banned_nodes={2})
    assert path == [1, 3]
    assert dist == 3.0


def test_dijkstra_missing_vertex():
    g = _make_simple_graph()
    path, dist = dijkstra(g, 99, 3)
    assert path is None
    assert math.isinf(dist)


# ============================================================
# Yen
# ============================================================

def test_yen_k_zero():
    g = _make_simple_graph()
    assert yen_k_shortest_paths(g, 1, 3, K=0) == []


def test_yen_same_source_target():
    g = _make_simple_graph()
    result = yen_k_shortest_paths(g, 1, 1, K=3)
    assert result == [([1], 0.0)]


def test_yen_no_path():
    g = Graph()
    g.add_edge(1, 2, 1.0)
    g.add_edge(3, 4, 1.0)
    assert yen_k_shortest_paths(g, 1, 4, K=3) == []


def test_yen_two_paths():
    """Классический пример: 1 — 2 — 4 — 5 и 1 — 3 — 4 — 5, оба по 3.0."""

    g = Graph()
    g.add_edge(1, 2, 1.0)
    g.add_edge(1, 3, 1.0)
    g.add_edge(2, 4, 1.0)
    g.add_edge(3, 4, 1.0)
    g.add_edge(4, 5, 1.0)

    result = yen_k_shortest_paths(g, 1, 5, K=3)
    assert len(result) == 2
    paths = [p for p, _ in result]
    assert [1, 2, 4, 5] in paths
    assert [1, 3, 4, 5] in paths
    assert all(abs(d - 3.0) < 1e-9 for _, d in result)


def test_yen_three_paths():
    """1 → 3: три пути с разными расстояниями."""

    g = Graph()
    g.add_edge(1, 2, 1.0)
    g.add_edge(2, 3, 1.0)
    g.add_edge(1, 3, 3.0)
    g.add_edge(1, 4, 0.5)
    g.add_edge(4, 3, 0.5)

    result = yen_k_shortest_paths(g, 1, 3, K=3)
    assert len(result) == 3
    paths = [p for p, _ in result]
    dists = [d for _, d in result]

    assert paths[0] == [1, 4, 3]
    assert abs(dists[0] - 1.0) < 1e-9
    assert paths[1] == [1, 2, 3]
    assert abs(dists[1] - 2.0) < 1e-9
    assert paths[2] == [1, 3]
    assert abs(dists[2] - 3.0) < 1e-9

    # отсортированы по возрастанию
    assert dists == sorted(dists)


def test_yen_paths_are_simple():
    """Все пути без повторения вершин."""

    g = Graph()
    g.add_edge(1, 2, 1.0)
    g.add_edge(2, 3, 1.0)
    g.add_edge(3, 4, 1.0)
    g.add_edge(1, 4, 5.0)
    g.add_edge(1, 3, 3.0)
    g.add_edge(2, 4, 3.0)

    result = yen_k_shortest_paths(g, 1, 4, K=5)
    for path, _ in result:
        assert len(path) == len(set(path)), f"путь с повтором: {path}"
        assert path[0] == 1
        assert path[-1] == 4


def test_yen_k_greater_than_available():
    """K больше, чем есть путей — вернуть сколько есть."""

    g = _make_simple_graph()   # 2 простых пути: [1,2,3] и [1,3]
    result = yen_k_shortest_paths(g, 1, 3, K=10)
    assert len(result) == 2


def test_yen_all_paths_distinct():
    g = _make_simple_graph()
    result = yen_k_shortest_paths(g, 1, 3, K=5)
    paths = [p for p, _ in result]
    assert len(paths) == len(set(map(tuple, paths)))