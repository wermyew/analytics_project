"""Страница Bootstrap-анализа."""

from __future__ import annotations
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from pages.templates import templates


router = APIRouter(tags=["pages"])


@router.get("/bootstrap", response_class=HTMLResponse)
def bootstrap_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="bootstrap.html",
        context={"page": "bootstrap"},
    )