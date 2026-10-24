"""Глобальное состояние приложения.

Здесь живут df, hash_index, segment_index. Заполняется один раз
в lifespan (main.py), читается в роутах и сервисах.

Почему модуль-синглтон, а не app.state:
- проще импортировать: from services.state import state
- не надо таскать Request в каждый сервис
- для учебного проекта этого достаточно

Для продакшена так делать не стоит (thread-safety, тесты),
но у нас read-only после старта + один update-эндпоинт.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import pandas as pd
from core.hash_map import HashMap
from core.segment_tree import SegmentTreeIndex


@dataclass
class AppState:
    df: Optional[pd.DataFrame] = None
    hash_index: Optional[HashMap] = None
    segment_index: Optional[SegmentTreeIndex] = None

    # кэш значений для naive-бенчмарков и для отката update
    values: list[float] = field(default_factory=list)
    original_values: list[float] = field(default_factory=list)  # ← новое
    keys: list[int] = field(default_factory=list)

    # время построения индексов (для отображения на сайте)
    hash_build_ms: float = 0.0
    segment_build_ms: float = 0.0

    @property
    def is_ready(self) -> bool:

        return (
            self.df is not None
            and self.hash_index is not None
            and self.segment_index is not None
        )


state = AppState()