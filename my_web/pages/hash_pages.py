"""Страницы Hash Map: теория, демо, бенчмарк."""

from __future__ import annotations
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from pages.templates import templates


router = APIRouter(prefix="/hash", tags=["pages"])


@router.get("", response_class=HTMLResponse)
def hash_theory(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="hash/theory.html",
        context={"page": "hash_theory"},
    )


@router.get("/demo", response_class=HTMLResponse)
def hash_demo(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="hash/demo.html",
        context={"page": "hash_demo"},
    )


@router.get("/benchmark", response_class=HTMLResponse)
def hash_benchmark(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="hash/benchmark.html",
        context={"page": "hash_benchmark"},
    )