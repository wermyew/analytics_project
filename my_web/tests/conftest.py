"""Общие фикстуры для API-тестов."""

from __future__ import annotations
import pytest
from fastapi.testclient import TestClient
from config import DATA_PATH, DEFAULT_FIELDS
from core.dataset_loader import load_dataset
from services import graph_service, hash_service, segment_service
from services.state import state
from main import app


@pytest.fixture(scope="session", autouse=True)
def _prepare_state():
    """Заполняет state так же, как lifespan, но один раз на всю сессию.

    TestClient по умолчанию НЕ выполняет lifespan, поэтому делаем вручную.
    """

    state.fields = DEFAULT_FIELDS.copy()
    df = load_dataset(DATA_PATH, order_field=state.fields["order"])
    state.df = df
    state.keys = df[state.fields["unique_id"]].tolist()
    state.values = df[state.fields["value"]].tolist()
    state.original_values = state.values.copy()

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

    yield


@pytest.fixture(autouse=True)
def _reset_build_status():
    """Сбрасывать build_status после каждого теста, чтобы не тащить 'ready'."""

    yield

    state.reset_build_status()


@pytest.fixture()
def client():
    """TestClient без запуска lifespan (state уже готов фикстурой выше)."""

    return TestClient(app)