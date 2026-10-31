"""Эндпоинты графа товаров: info, paths, benchmark, products."""

from __future__ import annotations
from time import perf_counter
from fastapi import APIRouter, HTTPException, Query
from api.schemas import (
    GraphBenchmarkResponse,
    GraphInfo,
    PathItem,
    PathsResponse,
    ProductItem,
)
from config import DEFAULT_K, MAX_K
from services import graph_service
from services.state import state
from core.dijkstra import dijkstra


router = APIRouter(prefix="/api/graph", tags=["graph"])


def _ensure_graph_ready() -> None:
    if not state.is_graph_ready:

        raise HTTPException(status_code=503, detail="Граф ещё не построен")


def _validate_source_target(source: int, target: int) -> None:
    if not state.graph.has_vertex(source):

        raise HTTPException(status_code=400, detail=f"Вершины {source} нет в графе")

    if not state.graph.has_vertex(target):

        raise HTTPException(status_code=400, detail=f"Вершины {target} нет в графе")

    if source == target:

        raise HTTPException(status_code=400, detail="source и target должны различаться")


@router.get("/info", response_model=GraphInfo)
def graph_info() -> GraphInfo:

    _ensure_graph_ready()
    info = graph_service.graph_info(state.graph)

    return GraphInfo(
        vertices=info["vertices"],
        edges=info["edges"],
        components=info["components"],
        build_ms=state.graph_build_ms,
    )


@router.get("/paths", response_model=PathsResponse)
def graph_paths(
    source: int,
    target: int,
    k: int = Query(DEFAULT_K, ge=1, le=MAX_K),
) -> PathsResponse:

    _ensure_graph_ready()
    _validate_source_target(source, target)

    # Дейкстра — один путь, для сравнения
    start = perf_counter()
    dijkstra(state.graph, source, target)
    dijkstra_ms = (perf_counter() - start) * 1000.0

    # Йен — K путей
    start = perf_counter()
    raw_paths = graph_service.find_k_paths(state.graph, source, target, k=k)
    yen_ms = (perf_counter() - start) * 1000.0

    paths = [
        PathItem(nodes=p["nodes"], distance=p["distance"], length=p["length"])
        for p in raw_paths
    ]

    return PathsResponse(
        source=source,
        target=target,
        k=k,
        paths=paths,
        dijkstra_ms=dijkstra_ms,
        yen_ms=yen_ms,
    )


@router.get("/benchmark", response_model=GraphBenchmarkResponse)
def graph_benchmark(
    source: int,
    target: int,
    k: int = Query(DEFAULT_K, ge=1, le=MAX_K),
) -> GraphBenchmarkResponse:

    _ensure_graph_ready()
    _validate_source_target(source, target)

    # Дейкстра
    start = perf_counter()
    dijkstra(state.graph, source, target)
    dijkstra_ms = (perf_counter() - start) * 1000.0

    # Йен
    start = perf_counter()
    graph_service.find_k_paths(state.graph, source, target, k=k)
    yen_ms = (perf_counter() - start) * 1000.0

    speedup = dijkstra_ms / yen_ms if yen_ms > 0 else None

    return GraphBenchmarkResponse(
        source=source,
        target=target,
        k=k,
        dijkstra_ms=dijkstra_ms,
        yen_ms=yen_ms,
        speedup=speedup,
    )


@router.get("/products", response_model=list[ProductItem])
def graph_products(
    limit: int = Query(100, ge=1, le=1000),
) -> list[ProductItem]:

    _ensure_graph_ready()

    counts = state.df["product_id"].value_counts()
    result = []

    for pid, cnt in counts.head(limit).items():
        result.append(ProductItem(product_id=int(pid), purchases=int(cnt)))

    return result