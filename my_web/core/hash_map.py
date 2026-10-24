"""Хеш-таблица с разрешением коллизий методом цепочек.

Реализация из учебного ноутбука hash_map_and_index.ipynb.
Ключи — хешируемые объекты (в нашем случае int: order_id).
Значения — произвольные (в нашем случае row_id: int).
"""

from __future__ import annotations


class HashMap:
    MAX_LOAD_FACTOR = 0.75

    def __init__(self, capacity: int = 10) -> None:
        self.hash_map: list[list[tuple]] = [[] for _ in range(capacity)]
        self.capacity = capacity
        self._size = 0

    def _hash(self, key) -> int:

        return hash(key) % self.capacity

    def load_factor(self, extra: int = 0) -> float:

        return (self._size + extra) / self.capacity

    def put(self, key, value) -> None:
        index = self._hash(key)
        bucket = self.hash_map[index]

        for i, (k, _) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)

                return

        if self.load_factor(extra=1) > self.MAX_LOAD_FACTOR:
            self.resize()
            index = self._hash(key)
            bucket = self.hash_map[index]

        bucket.append((key, value))
        self._size += 1

    def delete(self, key) -> bool:
        index = self._hash(key)
        bucket = self.hash_map[index]

        for i, (k, _) in enumerate(bucket):
            if k == key:
                bucket.pop(i)
                self._size -= 1

                return True

        return False

    def search(self, key, default=None):
        index = self._hash(key)

        for k, v in self.hash_map[index]:
            if k == key:

                return v

        return default

    def contains(self, key) -> bool:
        index = self._hash(key)

        for k, _ in self.hash_map[index]:
            if k == key:

                return True

        return False

    def resize(self) -> None:
        self.capacity *= 2
        old_map = self.hash_map
        self.hash_map = [[] for _ in range(self.capacity)]
        self._size = 0
        self.rehash(old_map)

    def rehash(self, old_map: list[list[tuple]]) -> None:
        for bucket in old_map:
            for key, value in bucket:
                self.put(key, value)

    def size(self) -> int:

        return self._size

    def __len__(self) -> int:

        return self._size