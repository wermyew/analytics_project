"""Эндпоинты хеш-индекса: поиск и бенчмарк."""

from __future__ import annotations
from fastapi import APIRouter, HTTPException
from api.schemas import (
    HashBenchmarkResponse,
    HashSearchResponse,
    OrderRow,
)
from services import benchmark_service, hash_service
from services.state import state


router = APIRouter(prefix="/api/hash", tags=["hash"])


def _ensure_ready() -> None:
    if not state.is_ready:

        raise HTTPException(status_code=503, detail="Индексы ещё не построены")


@router.get("/search/{order_id}", response_model=HashSearchResponse)
def hash_search(order_id: int) -> HashSearchResponse:
    _ensure_ready()

    result = hash_service.search_order(
        df=state.df,
        index=state.hash_index,
        keys=state.keys,
        order_id=order_id,
    )

    row = None
    if result["row"] is not None:
        row = OrderRow(**result["row"])

    speedup = None
    if result["hash_ms"] > 0 and result["linear_ms"] > 0:
        speedup = result["linear_ms"] / result["hash_ms"]

    return HashSearchResponse(
        order_id=order_id,
        found=row is not None,
        row=row,
        hash_row_id=result["hash_row_id"],
        linear_row_id=result["linear_row_id"],
        hash_ms=result["hash_ms"],
        linear_ms=result["linear_ms"],
        speedup=speedup,
    )


@router.get("/benchmark", response_model=HashBenchmarkResponse)
def hash_benchmark(n_queries: int = 30) -> HashBenchmarkResponse:
    _ensure_ready()

    result = benchmark_service.benchmark_hash(
        keys=state.keys,
        index=state.hash_index,
        n_queries=n_queries,
    )

    return HashBenchmarkResponse(**result)