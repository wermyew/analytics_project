"""Страница загрузки датасета."""

from __future__ import annotations
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from pages.templates import templates


router = APIRouter(tags=["pages"])


@router.get("/upload", response_class=HTMLResponse)
def upload_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="upload.html",
        context={"page": "upload"},
    )