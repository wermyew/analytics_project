"""Эндпоинты про сам датасет: инфо и первые строки."""

from __future__ import annotations
from fastapi import APIRouter, HTTPException
from config import ORDER_FIELD, UNIQUE_FIELD, VALUE_FIELD
from services.state import state
from api.schemas import DatasetInfo, DatasetHeadResponse, DatasetHeadRow


router = APIRouter(prefix="/api/dataset", tags=["dataset"])


def _ensure_ready() -> None:
    if not state.is_ready:

        raise HTTPException(status_code=503, detail="Индексы ещё не построены")


@router.get("/info", response_model=DatasetInfo)
def dataset_info() -> DatasetInfo:
    _ensure_ready()
    df = state.df

    return DatasetInfo(
        rows=len(df),
        columns=list(df.columns),
        date_from=df[ORDER_FIELD].min().date().isoformat(),
        date_to=df[ORDER_FIELD].max().date().isoformat(),
        total_sum=float(df[VALUE_FIELD].sum()),
        unique_field=UNIQUE_FIELD,
        order_field=ORDER_FIELD,
        value_field=VALUE_FIELD,
    )


@router.get("/head", response_model=DatasetHeadResponse)
def dataset_head(n: int = 10) -> DatasetHeadResponse:
    _ensure_ready()
    n = max(1, min(n, 100))
    df = state.df.head(n)
    rows = []

    for _, row in df.iterrows():
        rows.append(DatasetHeadRow(
            order_id=int(row["order_id"]),
            user_id=int(row["user_id"]),
            product_id=int(row["product_id"]),
            category=str(row["category"]),
            quantity=int(row["quantity"]),
            price=float(row["price"]),
            total=float(row["total"]),
            created_at=row[ORDER_FIELD].isoformat(),
        ))

    return DatasetHeadResponse(rows=rows)