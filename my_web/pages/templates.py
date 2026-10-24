"""Общий объект Jinja2Templates для всех pages-роутов."""

from __future__ import annotations
from fastapi.templating import Jinja2Templates
from config import BASE_DIR


templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))