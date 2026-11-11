"""Валидация загруженного CSV и выбранных полей.
Чистая логика, без FastAPI. Возвращает список ошибок (пусто = ок).
"""

from __future__ import annotations
import pandas as pd
from config import MAX_COLUMNS, MAX_ROWS


def validate_upload(df: pd.DataFrame) -> list[str]:
    """Проверить загруженный df: колонки, строки, лимиты.

    Возвращает список ошибок. Пусто — всё ок.
    """

    errors = []

    if len(df.columns) < 2:
        errors.append(f"Нужно хотя бы 2 колонки, найдено {len(df.columns)}")

    if len(df.columns) > MAX_COLUMNS:
        errors.append(
            f"Слишком много колонок: {len(df.columns)}, максимум {MAX_COLUMNS}"
        )

    if len(df) == 0:
        errors.append("Датасет пустой (0 строк)")

    if len(df) > MAX_ROWS:
        errors.append(
            f"Слишком много строк: {len(df)}, максимум {MAX_ROWS}"
        )

    return errors


def validate_fields(
    df: pd.DataFrame,
    fields: dict,
) -> list[str]:
    """Проверить выбранные поля.

    fields = {"unique_id", "order", "value", "source", "target"}
    Возвращает список ошибок.
    """

    errors = []
    cols = set(df.columns)

    # 1. все поля есть в df
    for role in ["unique_id", "order", "value"]:
        field = fields.get(role)
        if not field:
            errors.append(f"Поле '{role}' не выбрано")
        elif field not in cols:
            errors.append(f"Поле '{role}' = {field!r} нет в датасете")

    # если базовые поля не выбраны — дальше проверять нечего
    if errors:

        return errors

    unique_field = fields["unique_id"]
    order_field = fields["order"]
    value_field = fields["value"]

    # 2. unique_id уникален и без NaN
    if not df[unique_field].is_unique:
        dup_count = df[unique_field].duplicated().sum()
        errors.append(
            f"Колонка {unique_field!r} не уникальна: {dup_count} дубликатов"
        )

    if df[unique_field].isna().any():
        nan_count = int(df[unique_field].isna().sum())
        errors.append(
            f"Колонка {unique_field!r} содержит {nan_count} пропусков"
        )

    # 3. value числовой
    value_numeric = pd.to_numeric(df[value_field], errors="coerce")
    if value_numeric.isna().any():
        bad = int(value_numeric.isna().sum())
        errors.append(
            f"Колонка {value_field!r} содержит {bad} нечисловых значений"
        )

    # 4. order парсится как дата
    order_dates = pd.to_datetime(df[order_field], errors="coerce")
    if order_dates.isna().any():
        bad = int(order_dates.isna().sum())
        errors.append(
            f"Колонка {order_field!r} содержит {bad} невалидных дат"
        )

    return errors


def validate_graph_fields(
    df: pd.DataFrame,
    fields: dict,
) -> list[str]:
    """Проверить поля для графа (source, target)."""

    errors = []
    cols = set(df.columns)

    for role in ["source", "target"]:
        field = fields.get(role)
        if not field:
            errors.append(f"Поле '{role}' не выбрано (нужно для графа)")
        elif field not in cols:
            errors.append(f"Поле '{role}' = {field!r} нет в датасете")

    return errors