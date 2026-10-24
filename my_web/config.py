"""Константы проекта: пути, имена полей, лимиты."""

from __future__ import annotations
from pathlib import Path


# Корень проекта = папка, где лежит config.py
BASE_DIR = Path(__file__).resolve().parent

# Данные
DATA_PATH = BASE_DIR / "data" / "marketplace_orders_2024_2026.csv"

# Имена полей датасета
ORDER_FIELD = "created_at"   # ось, по которой сортируем
VALUE_FIELD = "total"        # числовое поле для суммы
UNIQUE_FIELD = "order_id"    # ключ для хеш-индекса

# Начальная capacity хеш-таблицы
HASH_INITIAL_CAPACITY = 10

# Лимиты для демо-эндпоинтов (чтобы не положить сервер тяжёлым запросом)
MAX_BENCHMARK_QUERIES = 100
MAX_SEGMENT_RANGE = 10_000