"""Сервис графа товаров: построение из df, поиск K путей, метрики.

Граф:
- вершины  — product_id (int)
- рёбра    — есть, если хотя бы один user_id купил оба товара
- вес      — 1 / количество общих покупателей
             (чем больше общих, тем ближе товары → меньше расстояние)

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
    min_purchases: int = GRAPH_MIN_PURCHASES,
) -> tuple[Graph, float]:
    """Строит граф товаров из датасета.

    Параметры:
        df            — DataFrame с колонками user_id, product_id
        min_purchases — минимальное число покупок товара, чтобы попасть в граф

    Возвращает:
        (graph, build_ms)
    """

    start = perf_counter()

    # 1. отфильтровать товары с >= min_purchases покупок
    if min_purchases > 1:
        counts = df["product_id"].value_counts()
        keep = set(counts[counts >= min_purchases].index)
        df = df[df["product_id"].isin(keep)]

    # 2. user_id -> set(product_id)
    user_products = df.groupby("user_id")["product_id"].apply(set)

    # 3. для каждой пары товаров одного пользователя — +1 к паре
    pair_counts: dict[tuple[int, int], int] = {}
    for products in user_products:
        if len(products) < 2:
            continue
        for p1, p2 in combinations(sorted(products), 2):
            pair_counts[(p1, p2)] = pair_counts.get((p1, p2), 0) + 1

    # 4. строим граф
    graph = Graph()
    for (p1, p2), count in pair_counts.items():
        if GRAPH_WEIGHT_MODE == "inverse":
            # расстояние: чем больше общих покупателей, тем ближе
            weight = 1.0 / count
        else:
            # «вес = общие покупатели» (Дейкстра будет искать далёкие — не рекомендуется)
            weight = float(count)
        graph.add_edge(p1, p2, weight)

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


def build_or_load_product_graph(df, min_purchases=GRAPH_MIN_PURCHASES):
    """Загрузить граф из кэша или построить и сохранить.

    Возвращает (graph, build_ms, from_cache).
    """

    cached = load_graph_cache()
    if cached is not None:

        return cached, 0.0, True

    graph, ms = build_product_graph(df, min_purchases=min_purchases)
    save_graph_cache(graph)

    return graph, ms, False