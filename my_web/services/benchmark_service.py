"""Бенчмарки: замеры времени на реальном датасете."""

from __future__ import annotations
import random
from time import perf_counter
import numpy as np
from core.hash_map import HashMap
from core.naive import linear_search, naive_range_sum
from core.segment_tree import SegmentTreeIndex
from core.segment_tree import SegmentTree


def benchmark_hash(
    keys: list[int],
    index: HashMap,
    n_queries: int = 30,
) -> dict:
    """n_queries равномерно распределённых запросов: linear vs hash."""

    n_queries = min(n_queries, len(keys))
    positions = np.linspace(0, len(keys) - 1, num=n_queries, dtype=int)
    test_keys = [keys[i] for i in positions]

    start = perf_counter()

    for key in test_keys:
        linear_search(keys, key)
    linear_ms = (perf_counter() - start) * 1000.0

    start = perf_counter()

    for key in test_keys:
        index.search(key)
    hash_ms = (perf_counter() - start) * 1000.0

    speedup = linear_ms / hash_ms if hash_ms > 0 else None

    return {
        "n_queries": n_queries,
        "linear_ms": linear_ms,
        "hash_ms": hash_ms,
        "speedup": speedup,
    }


def benchmark_segment(
    values: list[float],
    index: SegmentTreeIndex,
    n_ops: int = 2000,
    seed: int = 42,
) -> dict:
    """n_ops смешанных операций (≈50% update, ≈50% query): naive vs tree."""

    rng = random.Random(seed)
    n = len(values)

    ops: list[tuple] = []
    for _ in range(n_ops):
        if rng.random() < 0.5:
            ops.append(("update", rng.randrange(n), rng.uniform(1, 1000)))
        else:
            l = rng.randrange(n)
            r = rng.randrange(l, n)
            ops.append(("query", l, r))

    # naive
    naive_arr = values[:]
    start = perf_counter()

    for op in ops:
        if op[0] == "update":
            naive_arr[op[1]] = op[2]
        else:
            _ = naive_range_sum(naive_arr, op[1], op[2])
    naive_ms = (perf_counter() - start) * 1000.0

    # segment tree
    # работаем на копии values, чтобы не портить state.values
    st = SegmentTreeIndex.__new__(SegmentTreeIndex)
    st.records = [{"value": v} for v in values]
    st.value_field = "value"
    st.order_field = "value"
    st.st = SegmentTree(values[:])

    start = perf_counter()

    for op in ops:
        if op[0] == "update":
            st.st.update(op[1], op[2])
        else:
            st.st.query(op[1], op[2])
    st_ms = (perf_counter() - start) * 1000.0

    n_updates = sum(1 for op in ops if op[0] == "update")
    n_queries = len(ops) - n_updates
    speedup = naive_ms / st_ms if st_ms > 0 else None

    return {
        "n_ops": n_ops,
        "n_updates": n_updates,
        "n_queries": n_queries,
        "naive_ms": naive_ms,
        "tree_ms": st_ms,
        "speedup": speedup,
    }