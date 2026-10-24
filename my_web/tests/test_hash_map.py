"""Unit-тесты HashMap: put, search, delete, resize, коллизии."""

from __future__ import annotations
from core.hash_map import HashMap


def test_put_and_search():
    m = HashMap(capacity=4)
    m.put("a", 10)
    assert m.search("a") == 10
    assert m.search("missing") is None
    assert m.search("missing", default=-1) == -1


def test_update_does_not_increase_size():
    m = HashMap(capacity=4)
    m.put("a", 10)
    m.put("a", 20)
    assert m.search("a") == 20
    assert m.size() == 1


def test_update_does_not_trigger_resize():
    m = HashMap(capacity=4)
    m.put("a", 1)
    m.put("b", 2)
    m.put("c", 3)  # load_factor = 0.75
    cap_before = m.capacity
    m.put("a", 100)  # update, не новый ключ
    assert m.capacity == cap_before
    assert m.search("a") == 100


def test_contains_and_delete():
    m = HashMap(capacity=4)
    m.put("a", 1)
    assert m.contains("a")
    assert not m.contains("b")
    assert m.delete("a") is True
    assert not m.contains("a")
    assert m.delete("a") is False  # повторный delete
    assert m.size() == 0


def test_collisions():
    # при capacity=8 ключи 1, 9, 17, 25 дают один bucket
    m = HashMap(capacity=8)
    for key in [1, 9, 17, 25]:
        m.put(key, key * 10)

    assert m.search(1) == 10
    assert m.search(9) == 90
    assert m.search(17) == 170
    assert m.search(25) == 250

    m.delete(9)
    assert m.search(9) is None
    assert m.search(1) == 10
    assert m.search(17) == 170
    assert m.search(25) == 250


def test_resize_and_rehash():
    m = HashMap(capacity=4)
    m.put(1, "A")
    m.put(2, "B")
    m.put(3, "C")
    assert m.capacity == 4
    assert abs(m.load_factor() - 0.75) < 1e-9

    m.put(4, "D")  # превышает MAX_LOAD_FACTOR → resize
    assert m.capacity == 8
    assert m.search(1) == "A"
    assert m.search(2) == "B"
    assert m.search(3) == "C"
    assert m.search(4) == "D"
    assert m.load_factor() <= HashMap.MAX_LOAD_FACTOR


def test_len():
    m = HashMap(capacity=4)
    m.put("a", 1)
    m.put("b", 2)
    assert len(m) == 2
    m.delete("a")
    assert len(m) == 1


def test_many_items():
    m = HashMap(capacity=4)
    n = 1000
    for i in range(n):
        m.put(i, i * 2)

    assert m.size() == n
    for i in range(n):
        assert m.search(i) == i * 2

    assert m.capacity > 4  # resize сработал
    assert m.load_factor() <= HashMap.MAX_LOAD_FACTOR