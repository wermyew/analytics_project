"""Pydantic-схемы для API-ответов.

FastAPI использует их для:
- валидации ответа
- автодокументации на /docs
- сериализации (datetime, numpy → JSON)
"""

from __future__ import annotations
from typing import Optional
from pydantic import BaseModel


# ---------- dataset ----------

class DatasetInfo(BaseModel):
    rows: int
    columns: list[str]
    date_from: str
    date_to: str
    total_sum: float
    unique_field: str
    order_field: str
    value_field: str


class DatasetHeadRow(BaseModel):
    order_id: int
    user_id: int
    product_id: int
    category: str
    quantity: int
    price: float
    total: float
    created_at: str


class DatasetHeadResponse(BaseModel):
    rows: list[DatasetHeadRow]


# ---------- hash ----------

class OrderRow(BaseModel):
    order_id: int
    user_id: int
    product_id: int
    category: str
    quantity: int
    price: float
    total: float
    created_at: str


class HashSearchResponse(BaseModel):
    order_id: int
    found: bool
    row: Optional[OrderRow] = None
    hash_row_id: Optional[int] = None
    linear_row_id: Optional[int] = None
    hash_ms: float
    linear_ms: float
    speedup: Optional[float] = None


class HashBenchmarkResponse(BaseModel):
    n_queries: int
    linear_ms: float
    hash_ms: float
    speedup: Optional[float] = None


# ---------- segment ----------

class SegmentQueryResponse(BaseModel):
    l: int
    r: int
    tree_sum: float
    naive_sum: float
    tree_ms: float
    naive_ms: float
    date_from: str
    date_to: str
    matches: bool


class SegmentUpdateRequest(BaseModel):
    pos: int
    value: float


class SegmentUpdateResponse(BaseModel):
    pos: int
    old_value: float
    new_value: float
    update_ms: float
    new_sum: float


class SegmentBenchmarkResponse(BaseModel):
    n_ops: int
    n_updates: int
    n_queries: int
    naive_ms: float
    tree_ms: float
    speedup: Optional[float] = None


class SegmentResetRequest(BaseModel):
    pos: int


class SegmentResetResponse(BaseModel):
    pos: int
    old_value: float
    new_value: float
    update_ms: float


class GraphInfo(BaseModel):
    vertices: int
    edges: int
    components: int
    build_ms: float


class PathItem(BaseModel):
    nodes: list[int]
    distance: float
    length: int


class PathsResponse(BaseModel):
    source: int
    target: int
    k: int
    paths: list[PathItem]
    dijkstra_ms: float
    yen_ms: float


class GraphBenchmarkResponse(BaseModel):
    source: int
    target: int
    k: int
    dijkstra_ms: float
    yen_ms: float
    speedup: Optional[float] = None


class ProductItem(BaseModel):
    product_id: int
    purchases: int