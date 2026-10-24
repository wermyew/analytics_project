"""Загрузка и подготовка датасета.

Отвечает за то, чтобы DataFrame был в том виде,
в котором ожидают его сервисы: created_at — datetime, отсортирован.
"""

from __future__ import annotations
from pathlib import Path
import pandas as pd


ORDER_FIELD = "created_at"
VALUE_FIELD = "total"


def load_dataset(path: str | Path) -> pd.DataFrame:
    path = str(path)
    suffix = Path(path).suffix.lower()

    if suffix == ".csv":
        df = pd.read_csv(path)
    elif suffix in {".parquet", ".pq"}:
        df = pd.read_parquet(path)
    elif suffix in {".xlsx", ".xls"}:
        df = pd.read_excel(path)
    else:

        raise ValueError(f"Неизвестный формат: {suffix}")

    if ORDER_FIELD not in df.columns:

        raise ValueError(f"Нет колонки {ORDER_FIELD!r}")

    if VALUE_FIELD not in df.columns:

        raise ValueError(f"Нет колонки {VALUE_FIELD!r}")

    df[ORDER_FIELD] = pd.to_datetime(df[ORDER_FIELD])
    df = df.sort_values(ORDER_FIELD).reset_index(drop=True)

    return df


def df_to_records(df: pd.DataFrame) -> list[dict]:
    """DataFrame → list[dict], как ожидает SegmentTreeIndex."""

    return df[[ORDER_FIELD, VALUE_FIELD]].to_dict("records")