"""Константы проекта: пути, имена полей, лимиты."""

from __future__ import annotations
from pathlib import Path


# Корень проекта = папка, где лежит config.py
BASE_DIR = Path(__file__).resolve().parent

# Данные
DATA_PATH = BASE_DIR / "data" / "marketplace_orders_2024_2026.csv"

DEFAULT_UNIQUE_FIELD = "order_id"
DEFAULT_ORDER_FIELD = "created_at"
DEFAULT_VALUE_FIELD = "total"
DEFAULT_SOURCE_FIELD = "product_id"
DEFAULT_TARGET_FIELD = "user_id"

DEFAULT_FIELDS = {
    "unique_id": DEFAULT_UNIQUE_FIELD,
    "order": DEFAULT_ORDER_FIELD,
    "value": DEFAULT_VALUE_FIELD,
    "source": DEFAULT_SOURCE_FIELD,
    "target": DEFAULT_TARGET_FIELD,
}

UPLOADS_DIR = BASE_DIR / "data" / "uploads"

# лимиты загрузки
MAX_UPLOAD_SIZE_MB = 100
MAX_ROWS = 500_000
MAX_COLUMNS = 50

# Начальная capacity хеш-таблицы
HASH_INITIAL_CAPACITY = 10
MAX_LOAD_FACTOR = 0.75

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

# Бенчмарк Дейкстры: heapq vs своя MinHeap
DIJKSTRA_BENCH_RUNS = 5