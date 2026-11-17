"""Сервис Bootstrap-анализа: медиана чека на покупателя."""

from __future__ import annotations
import numpy as np
import pandas as pd
from time import perf_counter


def calculate_bootstrap_interval(
    df: pd.DataFrame,
    value_field: str,
    group_field: str,
    repeats: int = 1000,
    seed: int = 42,
) -> dict:
    # 1. Считаем сумму трат для каждого покупателя
    clean_df = df[[group_field, value_field]].dropna()
    user_totals = clean_df.groupby(group_field)[value_field].sum()

    x = user_totals.to_numpy(dtype=float)
    x = x[np.isfinite(x)]

    if len(x) < 2:
        raise ValueError("Недостаточно данных")

    # 2. Простой Bootstrap (цикл)
    rng = np.random.default_rng(seed)
    n = len(x)
    results = []

    start = perf_counter()
    for _ in range(repeats):
        # Выбираем случайные элементы с возвращением
        sample = rng.choice(x, size=n, replace=True)
        # Считаем медиану этого ресемпла
        results.append(np.median(sample))
    elapsed_ms = (perf_counter() - start) * 1000

    boot_medians = np.array(results)

    # 3. Результаты
    observed = float(np.median(x))
    mean_val = float(np.mean(x))
    low, high = np.percentile(boot_medians, [2.5, 97.5])

    return {
        "units": int(n),                # сколько покупателей
        "observed_median": observed,    # медиана по исходным данным
        "mean": mean_val,               # среднее (для сравнения)
        "ci_low": float(low),           # нижняя граница (2.5%)
        "ci_high": float(high),         # верхняя граница (97.5%)
        "repeats": repeats,
        "elapsed_ms": elapsed_ms,       # время в миллисекундах
    }