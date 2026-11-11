"""Главные страницы: /, /about, /compare."""

from __future__ import annotations
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from pages.templates import templates
from services.state import state


router = APIRouter(tags=["pages"])


@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    df = state.df
    order_field = state.fields["order"]
    value_field = state.fields["value"]
    unique_field = state.fields["unique_id"]

    context = {
        "page": "index",
        "rows": len(df) if df is not None else 0,
        "date_from": df[order_field].min().date().isoformat() if df is not None else "—",
        "date_to": df[order_field].max().date().isoformat() if df is not None else "—",
        "total_sum": float(df[value_field].sum()) if df is not None else 0.0,
        "unique_field": unique_field,
        "order_field": order_field,
        "value_field": value_field,
        "hash_build_ms": state.hash_build_ms,
        "segment_build_ms": state.segment_build_ms,
        "hash_capacity": state.hash_index.capacity if state.hash_index else 0,
        "segment_n": len(state.segment_index) if state.segment_index else 0,
        "graph_vertices": state.graph_vertices,
        "graph_edges": state.graph_edges,
        "graph_build_ms": state.graph_build_ms,
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
        "graph_vertices": state.graph_vertices,
        "graph_edges": state.graph_edges,
        "graph_build_ms": state.graph_build_ms,
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