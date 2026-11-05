"""Бинарная куча (min-heap) на массиве.

Реализация «как у heapq», но своя — чтобы сравнить с C-версией из stdlib.

Элементы — любые сравнимые объекты (числа, кортежи).
Кортежи сравниваются лексикографически: (priority, value) — по priority,
а value только при равных priority.

Индексация:
- heap[0] — корень (минимум)
- heap[i] — узел
- дети: 2*i + 1 (левый), 2*i + 2 (правый)
- родитель: (i - 1) // 2
"""

from __future__ import annotations


class MinHeap:
    def __init__(self) -> None:
        self._heap: list = []

    def push(self, item) -> None:
        """Добавить элемент. O(log n)."""

        self._heap.append(item)
        self._sift_up(len(self._heap) - 1)

    def pop(self):
        """Извлечь минимум. O(log n). Если пусто — IndexError."""

        if not self._heap:

            raise IndexError("pop from empty heap")

        root = self._heap[0]
        last = self._heap.pop()

        if self._heap:
            self._heap[0] = last
            self._sift_down(0)

        return root

    def peek(self):
        """Минимум без извлечения. O(1). Если пусто — IndexError."""

        if not self._heap:

            raise IndexError("peek from empty heap")

        return self._heap[0]

    def __len__(self) -> int:

        return len(self._heap)

    def __bool__(self) -> bool:

        return bool(self._heap)

    def _sift_up(self, i: int) -> None:
        """Поднять элемент вверх, пока он меньше родителя."""

        while i > 0:
            parent = (i - 1) // 2
            if self._heap[i] < self._heap[parent]:
                self._heap[i], self._heap[parent] = self._heap[parent], self._heap[i]
                i = parent
            else:

                break

    def _sift_down(self, i: int) -> None:
        """Опустить элемент вниз, пока он больше кого-то из детей."""

        n = len(self._heap)

        while True:
            left = 2 * i + 1
            right = 2 * i + 2
            smallest = i

            if left < n and self._heap[left] < self._heap[smallest]:
                smallest = left
            if right < n and self._heap[right] < self._heap[smallest]:
                smallest = right

            if smallest == i:

                break

            self._heap[i], self._heap[smallest] = self._heap[smallest], self._heap[i]
            i = smallest

    def to_list(self) -> list:
        """Копия внутреннего массива (для отладки/визуализации)."""

        return self._heap[:]

    def is_valid(self) -> bool:
        """Проверить инвариант кучи: parent <= children. O(n)."""

        n = len(self._heap)

        for i in range(n):
            left = 2 * i + 1
            right = 2 * i + 2
            if left < n and self._heap[i] > self._heap[left]:

                return False

            if right < n and self._heap[i] > self._heap[right]:

                return False

        return True


class MaxHeap(MinHeap):
    """Max-heap через инверсию сравнения.

    Наследуем MinHeap и переопределяем _sift_up/_sift_down:
    вместо `<` используем `>`.
    """

    def _sift_up(self, i: int) -> None:
        while i > 0:
            parent = (i - 1) // 2
            if self._heap[i] > self._heap[parent]:
                self._heap[i], self._heap[parent] = self._heap[parent], self._heap[i]
                i = parent
            else:

                break

    def _sift_down(self, i: int) -> None:
        n = len(self._heap)

        while True:
            left = 2 * i + 1
            right = 2 * i + 2
            largest = i

            if left < n and self._heap[left] > self._heap[largest]:
                largest = left
            if right < n and self._heap[right] > self._heap[largest]:
                largest = right

            if largest == i:

                break

            self._heap[i], self._heap[largest] = self._heap[largest], self._heap[i]
            i = largest

    def is_valid(self) -> bool:
        """Проверить инвариант max-heap: parent >= children."""

        n = len(self._heap)

        for i in range(n):
            left = 2 * i + 1
            right = 2 * i + 2
            if left < n and self._heap[i] < self._heap[left]:

                return False
            if right < n and self._heap[i] < self._heap[right]:

                return False

        return True