"""Эндпоинты дерева отрезков: query, update, бенчмарк."""

from __future__ import annotations
from time import perf_counter
from fastapi import APIRouter, HTTPException
from api.schemas import (
    SegmentBenchmarkResponse,
    SegmentQueryResponse,
    SegmentUpdateRequest,
    SegmentUpdateResponse,
    SegmentResetResponse,
    SegmentResetRequest,
)
from config import MAX_BENCHMARK_QUERIES, MAX_SEGMENT_RANGE
from services import benchmark_service, segment_service
from services.state import state

router = APIRouter(prefix="/api/segment", tags=["segment"])


def _ensure_ready() -> None:
    if not state.is_ready:
        raise HTTPException(status_code=503, detail="Индексы ещё не построены")


@router.get("/query", response_model=SegmentQueryResponse)
def segment_query(l: int, r: int) -> SegmentQueryResponse:
    _ensure_ready()

    if l < 0 or r < 0:
        raise HTTPException(status_code=400, detail="l и r должны быть >= 0")
    if l > r:
        raise HTTPException(status_code=400, detail="l должен быть <= r")
    if r >= len(state.values):
        raise HTTPException(
            status_code=400,
            detail=f"r должен быть < {len(state.values)}",
        )
    if r - l > MAX_SEGMENT_RANGE:
        raise HTTPException(
            status_code=400,
            detail=f"Слишком большой диапазон: максимум {MAX_SEGMENT_RANGE}",
        )

    try:
        result = segment_service.query_range(
            df=state.df,
            index=state.segment_index,
            values=state.values,
            l=l,
            r=r,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return SegmentQueryResponse(**result)


@router.post("/update", response_model=SegmentUpdateResponse)
def segment_update(payload: SegmentUpdateRequest) -> SegmentUpdateResponse:
    _ensure_ready()

    try:
        result = segment_service.update_value(
            df=state.df,
            index=state.segment_index,
            values=state.values,
            pos=payload.pos,
            value=payload.value,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    new_sum = state.segment_index.query(payload.pos, payload.pos)

    return SegmentUpdateResponse(
        pos=result["pos"],
        old_value=result["old_value"],
        new_value=result["new_value"],
        update_ms=result["update_ms"],
        new_sum=float(new_sum),
    )


@router.get("/benchmark", response_model=SegmentBenchmarkResponse)
def segment_benchmark(n_ops: int = 2000) -> SegmentBenchmarkResponse:
    _ensure_ready()
    n_ops = max(1, min(n_ops, MAX_BENCHMARK_QUERIES * 20))
    result = benchmark_service.benchmark_segment(
        values=state.values,
        index=state.segment_index,
        n_ops=n_ops,
    )
    return SegmentBenchmarkResponse(**result)


@router.post("/reset", response_model=SegmentResetResponse)
def segment_reset(payload: SegmentResetRequest) -> SegmentResetResponse:
    _ensure_ready()

    pos = payload.pos
    if pos < 0 or pos >= len(state.values):
        raise HTTPException(status_code=400, detail=f"pos должен быть < {len(state.values)}")

    original = state.original_values[pos]

    start = perf_counter()
    result = segment_service.reset_value(
        df=state.df,
        index=state.segment_index,
        values=state.values,
        pos=pos,
        original=original,
    )
    update_ms = (perf_counter() - start) * 1000.0

    return SegmentResetResponse(
        pos=result["pos"],
        old_value=result["old_value"],
        new_value=result["new_value"],
        update_ms=update_ms,
    )