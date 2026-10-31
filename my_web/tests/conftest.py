"""Общие фикстуры для API-тестов."""

from __future__ import annotations
import pytest
from fastapi.testclient import TestClient
from config import DATA_PATH, UNIQUE_FIELD, VALUE_FIELD
from core.dataset_loader import df_to_records, load_dataset
from services import hash_service, segment_service, graph_service
from services.state import state
from main import app


@pytest.fixture(scope="session", autouse=True)
def _prepare_state():
    """Заполняет state так же, как lifespan, но один раз на всю сессию.

    TestClient по умолчанию НЕ выполняет lifespan, поэтому делаем вручную.
    """
    df = load_dataset(DATA_PATH)
    state.df = df
    state.keys = df[UNIQUE_FIELD].tolist()
    state.values = df[VALUE_FIELD].tolist()
    state.original_values = state.values.copy()
    records = df_to_records(df)

    state.hash_index, state.hash_build_ms = hash_service.build_hash_index(state.keys)
    state.segment_index, state.segment_build_ms = segment_service.build_segment_index(records)
    state.graph, state.graph_build_ms, _ = graph_service.build_or_load_product_graph(df)
    state.graph_vertices = state.graph.num_vertices()
    state.graph_edges = state.graph.num_edges()
    yield


@pytest.fixture()
def client():
    """TestClient без запуска lifespan (state уже готов фикстурой выше)."""

    return TestClient(app)