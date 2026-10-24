"""Точка входа: FastAPI-приложение, lifespan, роутеры, статика."""

from __future__ import annotations
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from api import dataset_api, hash_api, segment_api
from config import BASE_DIR, DATA_PATH, UNIQUE_FIELD, VALUE_FIELD
from core.dataset_loader import df_to_records, load_dataset
from pages import hash_pages, main_pages, segment_pages
from services import hash_service, segment_service
from services.state import state


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. датасет
    df = load_dataset(DATA_PATH)
    state.df = df
    state.keys = df[UNIQUE_FIELD].tolist()
    state.values = df[VALUE_FIELD].tolist()
    state.original_values = state.values.copy()
    records = df_to_records(df)

    # 2. индексы
    state.hash_index, state.hash_build_ms = hash_service.build_hash_index(state.keys)
    state.segment_index, state.segment_build_ms = segment_service.build_segment_index(records)

    print(f"[startup] hash build:  {state.hash_build_ms:.1f} ms "
          f"(cap={state.hash_index.capacity})")
    print(f"[startup] seg  build:  {state.segment_build_ms:.1f} ms "
          f"(n={len(state.segment_index)})")

    yield

    print("[shutdown] bye")


app = FastAPI(
    title="ds_learning_site",
    description="Учебный сайт: hash map и segment tree на датасете заказов.",
    version="0.1.0",
    lifespan=lifespan,
)

# статика
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# API
app.include_router(dataset_api.router)
app.include_router(hash_api.router)
app.include_router(segment_api.router)

# HTML
app.include_router(main_pages.router)
app.include_router(hash_pages.router)
app.include_router(segment_pages.router)