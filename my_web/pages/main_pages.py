"""Главные страницы: /, /about, /compare."""

from __future__ import annotations
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from config import ORDER_FIELD, UNIQUE_FIELD, VALUE_FIELD
from pages.templates import templates
from services.state import state


router = APIRouter(tags=["pages"])


@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    df = state.df
    context = {
        "page": "index",
        "rows": len(df) if df is not None else 0,
        "date_from": df[ORDER_FIELD].min().date().isoformat() if df is not None else "—",
        "date_to": df[ORDER_FIELD].max().date().isoformat() if df is not None else "—",
        "total_sum": float(df[VALUE_FIELD].sum()) if df is not None else 0.0,
        "unique_field": UNIQUE_FIELD,
        "order_field": ORDER_FIELD,
        "value_field": VALUE_FIELD,
        "hash_build_ms": state.hash_build_ms,
        "segment_build_ms": state.segment_build_ms,
        "hash_capacity": state.hash_index.capacity if state.hash_index else 0,
        "segment_n": len(state.segment_index) if state.segment_index else 0,
    }

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=context,
    )


@router.get("/compare", response_class=HTMLResponse)
def compare(request: Request):
    context = {
        "page": "compare",
        "rows": len(state.df) if state.df is not None else 0,
        "hash_capacity": state.hash_index.capacity if state.hash_index else 0,
        "hash_build_ms": state.hash_build_ms,
        "segment_n": len(state.segment_index) if state.segment_index else 0,
        "segment_build_ms": state.segment_build_ms,
        "segment_tree_size": 4 * len(state.segment_index) if state.segment_index else 0,
    }

    return templates.TemplateResponse(
        request=request,
        name="compare.html",
        context=context,
    )


@router.get("/about", response_class=HTMLResponse)
def about(request: Request):
    context = {"page": "about"}

    return templates.TemplateResponse(
        request=request,
        name="about.html",
        context=context,
    )