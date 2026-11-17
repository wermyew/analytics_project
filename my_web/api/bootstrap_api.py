"""Эндпоинт Bootstrap-анализа: медиана чека на покупателя."""

from __future__ import annotations
from fastapi import APIRouter, HTTPException, Query
from api.schemas import BootstrapResponse
from services.state import state
from services.bootstrap_service import calculate_bootstrap_interval


router = APIRouter(prefix="/api/bootstrap", tags=["bootstrap"])


@router.get("/interval", response_model=BootstrapResponse)
def bootstrap_interval(
    repeats: int = Query(1000, ge=100, le=10_000),
) -> BootstrapResponse:
    """Считает 95% bootstrap-интервал для медианного расхода на покупателя."""

    if not state.is_df_ready:

        raise HTTPException(status_code=503, detail="Датасет не загружен")

    try:
        result = calculate_bootstrap_interval(
            df=state.df,
            value_field=state.fields["value"],
            group_field=state.fields["target"],
            repeats=repeats,
        )
    except ValueError as e:

        raise HTTPException(status_code=400, detail=str(e))

    return BootstrapResponse(**result)