"""Unit-тесты валидатора загрузки CSV."""

from __future__ import annotations
import pandas as pd
from config import MAX_COLUMNS, MAX_ROWS
from services.upload_validator import (
    validate_fields,
    validate_graph_fields,
    validate_upload,
)


# ============================================================
# validate_upload
# ============================================================

def _valid_df() -> pd.DataFrame:
    return pd.DataFrame({
        "order_id": [1, 2, 3],
        "created_at": ["2024-01-01", "2024-01-02", "2024-01-03"],
        "total": [10.0, 20.0, 30.0],
        "product_id": [1, 2, 3],
        "user_id": [10, 20, 30],
    })


def test_upload_valid():
    assert validate_upload(_valid_df()) == []


def test_upload_empty():
    df = pd.DataFrame()
    errors = validate_upload(df)
    assert any("2 колонки" in e or "колонк" in e for e in errors)
    assert any("пустой" in e for e in errors)


def test_upload_too_many_columns():
    df = _valid_df()
    # добавить колонки до MAX_COLUMNS + 1
    for i in range(MAX_COLUMNS + 1):
        df[f"col_{i}"] = i
    errors = validate_upload(df)
    assert any("колонок" in e for e in errors)


def test_upload_too_many_rows():
    n = MAX_ROWS + 1
    df = pd.DataFrame({
        "a": range(n),
        "b": range(n),
    })
    errors = validate_upload(df)
    assert any("строк" in e for e in errors)


# ============================================================
# validate_fields
# ============================================================

def _valid_fields() -> dict:
    return {
        "unique_id": "order_id",
        "order": "created_at",
        "value": "total",
        "source": "product_id",
        "target": "user_id",
    }


def test_fields_valid():
    assert validate_fields(_valid_df(), _valid_fields()) == []


def test_fields_missing_field():
    fields = _valid_fields()
    fields["unique_id"] = "nonexistent"
    errors = validate_fields(_valid_df(), fields)
    assert any("nonexistent" in e for e in errors)


def test_fields_empty_field():
    fields = _valid_fields()
    fields["value"] = ""
    errors = validate_fields(_valid_df(), fields)
    assert any("не выбрано" in e for e in errors)


def test_fields_not_unique():
    df = _valid_df()
    df["order_id"] = [1, 1, 3]
    errors = validate_fields(df, _valid_fields())
    assert any("не уникальна" in e for e in errors)


def test_fields_nan_in_unique():
    df = _valid_df()
    df["order_id"] = [1, None, 3]
    errors = validate_fields(df, _valid_fields())
    assert any("пропусков" in e for e in errors)


def test_fields_not_numeric():
    df = _valid_df()
    df["total"] = [10.0, "abc", 30.0]
    errors = validate_fields(df, _valid_fields())
    assert any("нечисловых" in e for e in errors)


def test_fields_bad_date():
    df = _valid_df()
    df["created_at"] = ["2024-01-01", "not-a-date", "2024-01-03"]
    errors = validate_fields(df, _valid_fields())
    assert any("невалидных дат" in e for e in errors)


# ============================================================
# validate_graph_fields
# ============================================================

def test_graph_fields_valid():
    assert validate_graph_fields(_valid_df(), _valid_fields()) == []


def test_graph_fields_missing_source():
    fields = _valid_fields()
    fields["source"] = "nonexistent"
    errors = validate_graph_fields(_valid_df(), fields)
    assert any("nonexistent" in e for e in errors)


def test_graph_fields_empty_target():
    fields = _valid_fields()
    fields["target"] = ""
    errors = validate_graph_fields(_valid_df(), fields)
    assert any("не выбрано" in e for e in errors)