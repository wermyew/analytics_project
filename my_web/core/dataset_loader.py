"""Загрузка и подготовка датасета.

Отвечает за то, чтобы DataFrame был в том виде,
в котором ожидают его сервисы: created_at — datetime, отсортирован.
"""

from __future__ import annotations
from pathlib import Path
import pandas as pd


def load_dataset(
    path: str | Path,
    order_field: str | None = None,
) -> pd.DataFrame:
    """Загрузить CSV/parquet/xlsx в DataFrame.

    order_field — по какому полю сортировать (и парсить как дату).
    Если None — не сортируем, не парсим. Для /upload и /configure.
    """

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

    if order_field is not None:
        if order_field not in df.columns:

            raise ValueError(f"Нет колонки {order_field!r}")

        df[order_field] = pd.to_datetime(df[order_field])
        df = df.sort_values(order_field).reset_index(drop=True)

    return df


def df_to_records(
    df: pd.DataFrame,
    order_field: str,
    value_field: str,
) -> list[dict]:

    return df[[order_field, value_field]].to_dict("records")