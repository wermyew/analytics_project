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
from core.graph import Graph
from config import DEFAULT_FIELDS


@dataclass
class AppState:
    df: Optional[pd.DataFrame] = None
    fields: dict = field(default_factory=lambda: DEFAULT_FIELDS.copy())
    hash_index: Optional[HashMap] = None
    segment_index: Optional[SegmentTreeIndex] = None
    graph: Optional[Graph] = None
    graph_build_ms: float = 0.0
    graph_vertices: int = 0
    graph_edges: int = 0

    # кэш значений для naive-бенчмарков и для отката update
    values: list[float] = field(default_factory=list)
    original_values: list[float] = field(default_factory=list)  # ← новое
    keys: list[int] = field(default_factory=list)

    build_status: str = "idle"  # "idle" | "building" | "ready" | "error"
    build_progress: float = 0.0  # 0.0 .. 1.0
    build_error: str = ""
    build_structures: list = field(default_factory=list)

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

    @property
    def is_graph_ready(self) -> bool:

        return self.graph is not None

    @property
    def is_df_ready(self) -> bool:

        return self.df is not None

    @property
    def is_hash_ready(self) -> bool:

        return self.hash_index is not None

    @property
    def is_segment_ready(self) -> bool:

        return self.segment_index is not None

    @property
    def is_building(self) -> bool:

        return self.build_status == "building"

    def reset_build_status(self) -> None:
        self.build_status = "idle"
        self.build_progress = 0.0
        self.build_error = ""
        self.build_structures = []

    def clear_structures(self) -> None:
        """Удалить построенные индексы (при загрузке нового датасета)."""

        self.hash_index = None
        self.segment_index = None
        self.graph = None

        self.hash_build_ms = 0.0
        self.segment_build_ms = 0.0
        self.graph_build_ms = 0.0
        self.graph_vertices = 0
        self.graph_edges = 0

        self.keys = []
        self.values = []
        self.original_values = []


state = AppState()