"""Unit-тесты SegmentTree и SegmentTreeIndex."""

from __future__ import annotations
import pytest
from core.segment_tree import SegmentTree, SegmentTreeIndex


A = [2, 5, 1, 4, 3, 7, 6, 8]


def test_build():
    st = SegmentTree(A)
    assert st.tree[1] == sum(A) == 36


@pytest.mark.parametrize("l,r,expected", [
    (0, 0, 2),
    (0, 3, 12),
    (2, 6, 21),
    (4, 7, 24),
    (0, 7, 36),
    (7, 7, 8),
    (3, 3, 4),
])
def test_query(l, r, expected):
    st = SegmentTree(A)
    assert st.query(l, r) == expected


def test_query_against_naive():
    st = SegmentTree(A)
    for l in range(len(A)):
        for r in range(l, len(A)):
            assert st.query(l, r) == sum(A[l:r + 1])


def test_update():
    st = SegmentTree(A)
    st.update(3, 10)  # было 4
    assert st.query(0, 7) == 42
    assert st.query(2, 6) == 27
    assert st.query(0, 1) == 7
    assert st.query(3, 3) == 10


def test_multiple_updates():
    st = SegmentTree(A)
    st.update(3, 10)
    st.update(5, 1)   # было 7
    st.update(0, 100)  # было 2
    assert st.query(0, 7) == sum([100, 5, 1, 10, 3, 1, 6, 8])
    assert st.query(0, 1) == 105


def test_invalid_range():
    st = SegmentTree(A)
    with pytest.raises(ValueError):
        st.query(-1, 3)
    with pytest.raises(ValueError):
        st.query(2, 100)
    with pytest.raises(ValueError):
        st.query(3, 2)


def test_invalid_update_position():
    st = SegmentTree(A)
    with pytest.raises(ValueError):
        st.update(-1, 5)
    with pytest.raises(ValueError):
        st.update(8, 5)


def test_empty_tree():
    st = SegmentTree([])
    assert st.query(0, 0) == 0
    with pytest.raises(ValueError):
        st.update(0, 1)


def test_segment_tree_index_sorts_records():
    records = [
        {"created_at": "2024-01-03", "total": 300.0},
        {"created_at": "2024-01-01", "total": 100.0},
        {"created_at": "2024-01-02", "total": 200.0},
    ]
    idx = SegmentTreeIndex(records, value_field="total", order_field="created_at")
    # после сортировки порядок: 100, 200, 300
    assert idx.query(0, 2) == 600.0
    assert idx.query(0, 0) == 100.0
    assert idx.query(2, 2) == 300.0


def test_segment_tree_index_update_keeps_records_in_sync():
    records = [
        {"created_at": "2024-01-01", "total": 100.0},
        {"created_at": "2024-01-02", "total": 200.0},
    ]
    idx = SegmentTreeIndex(records, value_field="total", order_field="created_at")
    idx.update(0, 500.0)
    assert idx.records[0]["total"] == 500.0
    assert idx.query(0, 1) == 700.0