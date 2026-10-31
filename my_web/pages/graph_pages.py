"""Страницы графа: теория, демо, бенчмарк."""

from __future__ import annotations
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from config import DEFAULT_K, MAX_K
from pages.templates import templates
from services.state import state


router = APIRouter(prefix="/graph", tags=["pages"])


@router.get("", response_class=HTMLResponse)
def graph_theory(request: Request):
    context = {
        "page": "graph_theory",
        "graph_vertices": state.graph_vertices,
        "graph_edges": state.graph_edges,
        "graph_build_ms": state.graph_build_ms,
        "default_k": DEFAULT_K,
        "max_k": MAX_K,
    }

    return templates.TemplateResponse(
        request=request,
        name="graph/theory.html",
        context=context,
    )


@router.get("/demo", response_class=HTMLResponse)
def graph_demo(request: Request):
    context = {
        "page": "graph_demo",
        "graph_vertices": state.graph_vertices,
        "graph_edges": state.graph_edges,
        "default_k": DEFAULT_K,
        "max_k": MAX_K,
    }

    return templates.TemplateResponse(
        request=request,
        name="graph/demo.html",
        context=context,
    )


@router.get("/benchmark", response_class=HTMLResponse)
def graph_benchmark(request: Request):
    context = {
        "page": "graph_benchmark",
        "graph_vertices": state.graph_vertices,
        "graph_edges": state.graph_edges,
        "default_k": DEFAULT_K,
        "max_k": MAX_K,
    }

    return templates.TemplateResponse(
        request=request,
        name="graph/benchmark.html",
        context=context,
    )