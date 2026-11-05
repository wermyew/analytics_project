"""Unit-тесты MinHeap и MaxHeap."""

from __future__ import annotations
import random
import pytest

from core.heap import MinHeap, MaxHeap


# ============================================================
# MinHeap
# ============================================================

def test_min_heap_empty():
    h = MinHeap()
    assert len(h) == 0
    assert not h
    assert h.is_valid()


def test_min_heap_push_peek():
    h = MinHeap()
    h.push(5)
    h.push(3)
    h.push(8)
    assert h.peek() == 3
    assert len(h) == 3


def test_min_heap_pop_order():
    h = MinHeap()
    for x in [5, 3, 8, 1, 9, 2]:
        h.push(x)

    result = [h.pop() for _ in range(6)]
    assert result == [1, 2, 3, 5, 8, 9]
    assert len(h) == 0


def test_min_heap_pop_empty():
    h = MinHeap()
    with pytest.raises(IndexError):
        h.pop()


def test_min_heap_peek_empty():
    h = MinHeap()
    with pytest.raises(IndexError):
        h.peek()


def test_min_heap_peek_does_not_remove():
    h = MinHeap()
    h.push(5)
    h.push(3)
    assert h.peek() == 3
    assert h.peek() == 3   # повторный peek
    assert len(h) == 2


def test_min_heap_many_random():
    rng = random.Random(42)
    values = [rng.randint(-1000, 1000) for _ in range(500)]

    h = MinHeap()
    for x in values:
        h.push(x)
        assert h.is_valid()

    result = [h.pop() for _ in range(len(values))]
    assert result == sorted(values)


def test_min_heap_invariant_after_operations():
    rng = random.Random(42)
    h = MinHeap()

    for _ in range(100):
        if rng.random() < 0.6 or not h:
            h.push(rng.randint(0, 100))
        else:
            h.pop()
        assert h.is_valid()


def test_min_heap_duplicates():
    h = MinHeap()
    for x in [3, 3, 1, 1, 2, 2]:
        h.push(x)

    result = [h.pop() for _ in range(6)]
    assert result == [1, 1, 2, 2, 3, 3]


def test_min_heap_tuples():
    """Кортежи сравниваются лексикографически — как в Дейкстре."""
    h = MinHeap()
    h.push((3.0, "a"))
    h.push((1.0, "b"))
    h.push((2.0, "c"))

    assert h.pop() == (1.0, "b")
    assert h.pop() == (2.0, "c")
    assert h.pop() == (3.0, "a")


def test_min_heap_tuples_same_priority():
    """При равных priority сравнивается второй элемент кортежа."""
    h = MinHeap()
    h.push((1.0, "c"))
    h.push((1.0, "a"))
    h.push((1.0, "b"))

    assert h.pop() == (1.0, "a")
    assert h.pop() == (1.0, "b")
    assert h.pop() == (1.0, "c")


def test_min_heap_bool():
    h = MinHeap()
    assert not h
    h.push(1)
    assert h


def test_min_heap_to_list_copy():
    """to_list возвращает копию, а не ссылку."""
    h = MinHeap()
    h.push(5)
    h.push(3)

    copy = h.to_list()
    copy.append(999)
    assert len(h) == 2   # внутренний массив не изменился


# ============================================================
# MaxHeap
# ============================================================

def test_max_heap_empty():
    h = MaxHeap()
    assert len(h) == 0
    assert not h
    assert h.is_valid()


def test_max_heap_push_peek():
    h = MaxHeap()
    h.push(5)
    h.push(3)
    h.push(8)
    assert h.peek() == 8


def test_max_heap_pop_order():
    h = MaxHeap()
    for x in [5, 3, 8, 1, 9, 2]:
        h.push(x)

    result = [h.pop() for _ in range(6)]
    assert result == [9, 8, 5, 3, 2, 1]


def test_max_heap_many_random():
    rng = random.Random(42)
    values = [rng.randint(-1000, 1000) for _ in range(500)]

    h = MaxHeap()
    for x in values:
        h.push(x)
        assert h.is_valid()

    result = [h.pop() for _ in range(len(values))]
    assert result == sorted(values, reverse=True)


def test_max_heap_pop_empty():
    h = MaxHeap()
    with pytest.raises(IndexError):
        h.pop()


def test_max_heap_duplicates():
    h = MaxHeap()
    for x in [3, 3, 1, 1, 2, 2]:
        h.push(x)

    result = [h.pop() for _ in range(6)]
    assert result == [3, 3, 2, 2, 1, 1]