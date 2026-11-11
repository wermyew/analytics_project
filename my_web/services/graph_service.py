"""Сервис графа товаров: построение из df, поиск K путей, метрики.

Граф:
- вершины — df[source_field] (например, product_id)
- рёбра — есть, если хотя бы один df[target_field] (например, user_id)
           связан с обоими source
- вес — 1 / количество общих target
             (чем больше общих, тем ближе вершины → меньше расстояние)

Йен ищет K кратчайших путей между source и target.
"""

from __future__ import annotations
from itertools import combinations
from time import perf_counter
import pandas as pd
from config import GRAPH_MIN_PURCHASES, GRAPH_WEIGHT_MODE, GRAPH_CACHE_PATH, GRAPH_CACHE_VERSION
from core.graph import Graph
from core.yen import yen_k_shortest_paths
import pickle


def build_product_graph(
    df: pd.DataFrame,
    source_field: str,
    target_field: str,
    min_purchases: int = GRAPH_MIN_PURCHASES,
) -> tuple[Graph, float]:
    """Строит граф: вершины = df[source_field], рёбра = общие df[target_field].

    Параметры:
        df            — DataFrame
        source_field  — колонка-вершина (например, product_id)
        target_field  — колонка-группа (например, user_id)
        min_purchases — минимум записей source, чтобы попасть в граф

    Возвращает:
        (graph, build_ms)
    """

    start = perf_counter()

    # 1. отфильтровать source с >= min_purchases
    if min_purchases > 1:
        counts = df[source_field].value_counts()
        keep = set(counts[counts >= min_purchases].index)
        df = df[df[source_field].isin(keep)]

    # 2. target -> set(source)
    target_sources = df.groupby(target_field)[source_field].apply(set)

    # 3. для каждой пары source одного target — +1 к паре
    pair_counts: dict[tuple, int] = {}
    for sources in target_sources:
        if len(sources) < 2:
            continue
        for s1, s2 in combinations(sorted(sources), 2):
            pair_counts[(s1, s2)] = pair_counts.get((s1, s2), 0) + 1

    # 4. строим граф
    graph = Graph()
    for (s1, s2), count in pair_counts.items():
        if GRAPH_WEIGHT_MODE == "inverse":
            # расстояние: чем больше общих target, тем ближе
            weight = 1.0 / count
        else:
            # «вес = общие target» (Дейкстра будет искать далёкие — не рекомендуется)
            weight = float(count)
        graph.add_edge(s1, s2, weight)

    elapsed_ms = (perf_counter() - start) * 1000.0

    return graph, elapsed_ms


def find_k_paths(
    graph: Graph,
    source: int,
    target: int,
    k: int,
) -> list[dict]:
    """K кратчайших путей между source и target.

    Возвращает список dict:
        {"nodes": [...], "distance": float, "length": int}
    """

    raw = yen_k_shortest_paths(graph, source, target, K=k)

    return [
        {
            "nodes": path,
            "distance": float(dist),
            "length": len(path) - 1,   # число рёбер
        }
        for path, dist in raw
    ]


def graph_info(graph: Graph) -> dict:
    """Метрики графа для API и главной страницы."""

    return {
        "vertices": graph.num_vertices(),
        "edges": graph.num_edges(),
        "components": graph.components(),
    }


def save_graph_cache(graph: Graph, path=GRAPH_CACHE_PATH) -> None:
    """Сохранить граф в pickle-файл."""

    with open(path, "wb") as f:
        pickle.dump({"version": GRAPH_CACHE_VERSION, "graph": graph}, f)


def load_graph_cache(path=GRAPH_CACHE_PATH) -> Graph | None:
    """Загрузить граф из pickle. None, если файла нет или версия не совпадает."""

    if not path.exists():

        return None

    try:
        with open(path, "rb") as f:
            data = pickle.load(f)
        if data.get("version") != GRAPH_CACHE_VERSION:

            return None

        return data["graph"]

    except Exception:

        return None


def build_or_load_product_graph(
    df,
    source_field: str,
    target_field: str,
    min_purchases=GRAPH_MIN_PURCHASES,
):
    """Загрузить граф из кэша или построить и сохранить.

    Возвращает (graph, build_ms, from_cache).
    """

    cached = load_graph_cache()
    if cached is not None:

        return cached, 0.0, True

    graph, ms = build_product_graph(
        df, source_field, target_field, min_purchases=min_purchases,
    )
    save_graph_cache(graph)

    return graph, ms, False