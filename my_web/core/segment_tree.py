"""Дерево отрезков для range-sum запросов с обновлениями.

Реализация из учебного ноутбука segment_tree_project.ipynb.
"""

from __future__ import annotations


class SegmentTree:
    def __init__(self, a: list[float]) -> None:
        self.n = len(a)
        self.a = a[:]

        if self.n == 0:
            self.tree: list[float] = []

            return

        self.tree = [0.0] * (4 * self.n)
        self._build(1, 0, self.n - 1)

    def _build(self, v: int, tl: int, tr: int) -> None:
        if tl == tr:
            self.tree[v] = self.a[tl]

            return

        tm = (tl + tr) // 2
        self._build(2 * v, tl, tm)
        self._build(2 * v + 1, tm + 1, tr)
        self.tree[v] = self.tree[2 * v] + self.tree[2 * v + 1]

    def query(self, l: int, r: int) -> float:
        if self.n == 0:

            return 0.0

        if l < 0 or r >= self.n or l > r:

            raise ValueError(f"Некорректный диапазон [{l}, {r}]")

        return self._query(1, 0, self.n - 1, l, r)

    def _query(self, v: int, tl: int, tr: int, l: int, r: int) -> float:
        if l > tr or r < tl:

            return 0.0

        if l <= tl and tr <= r:

            return self.tree[v]

        tm = (tl + tr) // 2
        left = self._query(2 * v, tl, tm, l, r)
        right = self._query(2 * v + 1, tm + 1, tr, l, r)

        return left + right

    def update(self, pos: int, value: float) -> None:
        if self.n == 0:

            raise ValueError("Дерево пустое")

        if pos < 0 or pos >= self.n:

            raise ValueError(f"Некорректная позиция {pos}")

        self.a[pos] = value
        self._update(1, 0, self.n - 1, pos, value)

    def _update(self, v: int, tl: int, tr: int, pos: int, value: float) -> None:
        if tl == tr:
            self.tree[v] = value

            return

        tm = (tl + tr) // 2
        if pos <= tm:
            self._update(2 * v, tl, tm, pos, value)
        else:
            self._update(2 * v + 1, tm + 1, tr, pos, value)

        self.tree[v] = self.tree[2 * v] + self.tree[2 * v + 1]


class SegmentTreeIndex:
    """Обёртка над SegmentTree, которая держит records и дерево в синхроне.

    В ноутбуке было предупреждение: если лезть напрямую в `.st`,
    records и дерево рассинхронизируются. Здесь update() —
    единственный способ менять значение, он обновляет оба.
    """

    def __init__(
        self,
        records: list[dict],
        value_field: str = "total",
        order_field: str = "created_at",
    ) -> None:
        self.records = sorted(records, key=lambda r: r[order_field])
        self.value_field = value_field
        self.order_field = order_field

        values = [r[value_field] for r in self.records]
        self.st = SegmentTree(values)

    def update(self, pos: int, value: float) -> None:
        self.records[pos][self.value_field] = value
        self.st.update(pos, value)

    def query(self, l: int, r: int) -> float:

        return self.st.query(l, r)

    def __len__(self) -> int:

        return len(self.records)