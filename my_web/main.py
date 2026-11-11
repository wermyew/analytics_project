"""Точка входа: FastAPI-приложение, lifespan, роутеры, статика."""

from __future__ import annotations
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from api import dataset_api, hash_api, segment_api, graph_api
from config import (
    BASE_DIR,
    DATA_PATH,
    DEFAULT_FIELDS,
    UPLOADS_DIR,
)
from core.dataset_loader import load_dataset
from pages import hash_pages, main_pages, segment_pages, upload_pages, graph_pages
from services import graph_service, hash_service, segment_service
from services.state import state


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 0. папка для загрузок
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. датасет
    state.fields = DEFAULT_FIELDS.copy()
    df = load_dataset(DATA_PATH, order_field=state.fields["order"])
    state.df = df
    state.keys = df[state.fields["unique_id"]].tolist()
    state.values = df[state.fields["value"]].tolist()
    state.original_values = state.values.copy()

    # 2. индексы
    state.hash_index, state.hash_build_ms = hash_service.build_hash_index(
        df, state.fields["unique_id"],
    )
    state.segment_index, state.segment_build_ms = segment_service.build_segment_index(
        df, state.fields["order"], state.fields["value"],
    )
    state.graph, state.graph_build_ms, _ = graph_service.build_or_load_product_graph(
        df, state.fields["source"], state.fields["target"],
    )
    state.graph_vertices = state.graph.num_vertices()
    state.graph_edges = state.graph.num_edges()

    print(f"[startup] df: {len(df)} rows")
    print(f"[startup] hash:     {state.hash_build_ms:.1f} ms "
          f"(cap={state.hash_index.capacity})")
    print(f"[startup] segment:  {state.segment_build_ms:.1f} ms "
          f"(n={len(state.segment_index)})")
    print(f"[startup] graph:    {state.graph_build_ms:.1f} ms "
          f"(V={state.graph_vertices}, E={state.graph_edges})")

    yield

    print("[shutdown] bye")


app = FastAPI(
    title="ds_learning_site",
    description="Учебный сайт: hash map, segment tree и Yen's K paths на датасете заказов.",
    version="0.2.0",
    lifespan=lifespan,
)

# статика
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# API
app.include_router(dataset_api.router)
app.include_router(hash_api.router)
app.include_router(segment_api.router)
app.include_router(graph_api.router)

# HTML
app.include_router(main_pages.router)
app.include_router(hash_pages.router)
app.include_router(segment_pages.router)
app.include_router(upload_pages.router)
app.include_router(graph_pages.router)