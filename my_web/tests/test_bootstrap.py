"""Тесты Bootstrap-сервиса и API."""

from __future__ import annotations
import numpy as np
import pandas as pd
import pytest

from services.bootstrap_service import calculate_bootstrap_interval


# ============================================================
# Unit-тесты сервиса
# ============================================================

def test_bootstrap_simple_data():
    """Проверка на маленьких данных."""
    df = pd.DataFrame({
        "user": ["a", "a", "b", "b", "c"],
        "total": [10.0, 20.0, 30.0, 40.0, 100.0],
    })
    # Суммы: a=30, b=70, c=100. Медиана = 70
    res = calculate_bootstrap_interval(df, "total", "user", repeats=100)

    assert res["units"] == 3
    assert res["observed_median"] == 70.0
    assert res["ci_low"] <= 70.0 <= res["ci_high"]


def test_bootstrap_aggregates_by_group():
    """Проверяем, что данные агрегируются (50 заказов = 1 покупатель)."""
    # Один пользователь с 50 заказами по 10, второй с 1 заказом на 100
    df = pd.DataFrame({
        "user": [1] * 50 + [2],
        "total": [10.0] * 50 + [100.0],
    })
    # Суммы: 1 -> 500, 2 -> 100
    res = calculate_bootstrap_interval(df, "total", "user", repeats=10)

    assert res["units"] == 2
    # Медиана (500+100)/2 = 300
    assert res["observed_median"] == 300.0


def test_bootstrap_not_enough_data():
    """Меньше 2 групп — ошибка."""
    df = pd.DataFrame({"user": [1, 1], "total": [10.0, 20.0]})
    with pytest.raises(ValueError, match="Недостаточно данных"):
        calculate_bootstrap_interval(df, "total", "user")


def test_bootstrap_drops_na():
    """NaN в данных должны удаляться."""
    df = pd.DataFrame({
        "user": ["a", "b", "c", "d"],
        "total": [10.0, np.nan, 30.0, 40.0],
    })
    res = calculate_bootstrap_interval(df, "total", "user", repeats=10)
    # Должно остаться 3 валидных покупателя (a, c, d)
    assert res["units"] == 3


# ============================================================
# API-тесты
# ============================================================

def test_api_bootstrap_ok(client):
    """Проверка успешного ответа API."""
    r = client.get("/api/bootstrap/interval?repeats=100")
    assert r.status_code == 200

    data = r.json()
    assert data["units"] > 0
    assert data["observed_median"] > 0
    assert data["ci_low"] <= data["observed_median"] <= data["ci_high"]
    assert data["repeats"] == 100


def test_api_bootstrap_invalid_repeats(client):
    """Проверка валидации параметра repeats."""
    # Меньше 100
    r = client.get("/api/bootstrap/interval?repeats=10")
    assert r.status_code == 422

    # Больше 10000
    r = client.get("/api/bootstrap/interval?repeats=20000")
    assert r.status_code == 422