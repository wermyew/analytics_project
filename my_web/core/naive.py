"""Наивные (без индекса) реализации — для сравнения на бенчмарках."""

from __future__ import annotations


def linear_search(values: list, target):
    """O(n) поиск индекса значения в списке. Возвращает row_id или None."""

    for i, row in enumerate(values):
        if row == target:

            return i

    return None


def naive_range_sum(values: list[float], l: int, r: int) -> float:
    """O(r-l+1) сумма по срезу. Возвращает sum(values[l:r+1])."""

    return sum(values[l:r + 1])