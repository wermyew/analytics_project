"""Сервис хеш-индекса: построение, поиск, бенчмарк."""

from __future__ import annotations
from time import perf_counter
import pandas as pd
from config import HASH_INITIAL_CAPACITY, UNIQUE_FIELD
from core.hash_map import HashMap
from core.naive import linear_search


def build_hash_index(keys: list[int]) -> tuple[HashMap, float]:
    """Строит HashMap: key=order_id → value=row_id.

    Возвращает (index, время_построения_мс).
    """

    index = HashMap(capacity=HASH_INITIAL_CAPACITY)
    start = perf_counter()
    for row_id, key in enumerate(keys):
        index.put(key, row_id)
    elapsed_ms = (perf_counter() - start) * 1000.0

    return index, elapsed_ms


def search_order(
    df: pd.DataFrame,
    index: HashMap,
    keys: list[int],
    order_id: int,
) -> dict:
    """Ищет заказ по order_id через hash и через linear.

    Возвращает dict с найденной строкой и временами обоих способов.
    Если заказа нет — row=None.
    """

    start = perf_counter()
    row_id = index.search(order_id)
    hash_ms = (perf_counter() - start) * 1000.0

    start = perf_counter()
    linear_row_id = linear_search(keys, order_id)
    linear_ms = (perf_counter() - start) * 1000.0

    row = None
    if row_id is not None:
        row = df.iloc[row_id].to_dict()
        # datetime → str, иначе JSON не сериализует
        for k, v in row.items():
            if hasattr(v, "isoformat"):
                row[k] = v.isoformat()

    return {
        "order_id": order_id,
        "row": row,
        "hash_ms": hash_ms,
        "linear_ms": linear_ms,
        "hash_row_id": row_id,
        "linear_row_id": linear_row_id,
    }