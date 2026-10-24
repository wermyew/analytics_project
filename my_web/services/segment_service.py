"""Сервис дерева отрезков: построение, query, update, бенчмарк."""

from __future__ import annotations
import random
from time import perf_counter
import pandas as pd
from config import ORDER_FIELD, VALUE_FIELD
from core.naive import naive_range_sum
from core.segment_tree import SegmentTreeIndex


def build_segment_index(
    records: list[dict],
) -> tuple[SegmentTreeIndex, float]:
    """Строит SegmentTreeIndex. Возвращает (index, время_построения_мс)."""

    start = perf_counter()
    index = SegmentTreeIndex(
        records,
        value_field=VALUE_FIELD,
        order_field=ORDER_FIELD,
    )
    elapsed_ms = (perf_counter() - start) * 1000.0

    return index, elapsed_ms


def query_range(
    df: pd.DataFrame,
    index: SegmentTreeIndex,
    values: list[float],
    l: int,
    r: int,
) -> dict:
    """Сумма total за [l, r] через дерево и через naive.

    Возвращает обе суммы, обе длительности и даты диапазона.
    """

    if l < 0 or r >= len(values) or l > r:

        raise ValueError(f"Некорректный диапазон [{l}, {r}]")

    start = perf_counter()
    tree_sum = index.query(l, r)
    tree_ms = (perf_counter() - start) * 1000.0

    start = perf_counter()
    naive_sum = naive_range_sum(values, l, r)
    naive_ms = (perf_counter() - start) * 1000.0

    return {
        "l": l,
        "r": r,
        "tree_sum": float(tree_sum),
        "naive_sum": float(naive_sum),
        "tree_ms": tree_ms,
        "naive_ms": naive_ms,
        "date_from": df[ORDER_FIELD].iloc[l].date().isoformat(),
        "date_to": df[ORDER_FIELD].iloc[r].date().isoformat(),
        "matches": abs(tree_sum - naive_sum) < 1e-6,
    }


def update_value(
    df: pd.DataFrame,
    index: SegmentTreeIndex,
    values: list[float],
    pos: int,
    value: float,
) -> dict:
    """Меняет total у записи pos. Обновляет и records, и values, и дерево."""

    if pos < 0 or pos >= len(values):

        raise ValueError(f"Некорректная позиция {pos}")

    old_value = values[pos]

    start = perf_counter()
    index.update(pos, value)
    update_ms = (perf_counter() - start) * 1000.0

    values[pos] = value
    df.at[pos, VALUE_FIELD] = value

    return {
        "pos": pos,
        "old_value": float(old_value),
        "new_value": float(value),
        "update_ms": update_ms,
    }


def reset_value(
    df: pd.DataFrame,
    index: SegmentTreeIndex,
    values: list[float],
    pos: int,
    original: float,
) -> dict:
    """Возвращает total записи pos к исходному значению.

    original — исходное значение, которое надо помнить снаружи
    (state.original_values). Мы не храним его в сервисе,
    потому что сервис не должен знать про историю.
    """

    if pos < 0 or pos >= len(values):

        raise ValueError(f"Некорректная позиция {pos}")

    current = values[pos]
    index.update(pos, original)
    values[pos] = original
    df.at[pos, VALUE_FIELD] = original

    return {
        "pos": pos,
        "old_value": float(current),
        "new_value": float(original),
    }