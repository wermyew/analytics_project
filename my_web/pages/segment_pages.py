"""Страницы Segment Tree: теория, демо, бенчмарк."""

from __future__ import annotations
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from pages.templates import templates


router = APIRouter(prefix="/segment", tags=["pages"])


@router.get("", response_class=HTMLResponse)
def segment_theory(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="segment/theory.html",
        context={"page": "segment_theory"},
    )


@router.get("/demo", response_class=HTMLResponse)
def segment_demo(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="segment/demo.html",
        context={"page": "segment_demo"},
    )


@router.get("/benchmark", response_class=HTMLResponse)
def segment_benchmark(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="segment/benchmark.html",
        context={"page": "segment_benchmark"},
    )