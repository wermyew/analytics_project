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

# Граф товаров
GRAPH_MIN_PURCHASES = 1        # минимальное число покупок товара, чтобы попасть в граф
GRAPH_WEIGHT_MODE = "inverse"  # "inverse" = 1/общие_покупатели, "direct" = общие_покупатели
DEFAULT_K = 3                  # K по умолчанию
MAX_K = 10                     # максимум K

# Кэш графа
GRAPH_CACHE_PATH = BASE_DIR / "data" / "graph_cache.pkl"
GRAPH_CACHE_VERSION = 1   # менять при изменении формата графа