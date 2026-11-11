"""Эндпоинты про сам датасет: инфо и первые строки."""

import asyncio
import uuid
from pathlib import Path
import pandas as pd
from fastapi import File, UploadFile, APIRouter, HTTPException
from services.state import state
from config import (
    DATA_PATH,
    DEFAULT_FIELDS,
    MAX_UPLOAD_SIZE_MB,
    UPLOADS_DIR,
)
from core.dataset_loader import load_dataset
from services import graph_service, hash_service, segment_service
from services.upload_validator import (
    validate_fields,
    validate_graph_fields,
    validate_upload,
)
from api.schemas import (
    BuildRequest,
    BuildResponse,
    BuildStatusResponse,
    ConfigureRequest,
    ConfigureResponse,
    DatasetInfo,
    DatasetHeadResponse,
    DatasetHeadRow,
    ResetResponse,
    UploadResponse,
)


router = APIRouter(prefix="/api/dataset", tags=["dataset"])


def _ensure_df_ready() -> None:
    if not state.is_df_ready:
        raise HTTPException(status_code=503, detail="Датасет не загружен")


@router.get("/info", response_model=DatasetInfo)
def dataset_info() -> DatasetInfo:
    _ensure_df_ready()
    df = state.df

    order_field = state.fields["order"]
    value_field = state.fields["value"]
    unique_field = state.fields["unique_id"]

    return DatasetInfo(
        rows=len(df),
        columns=list(df.columns),
        date_from=df[order_field].min().date().isoformat(),
        date_to=df[order_field].max().date().isoformat(),
        total_sum=float(df[value_field].sum()),
        unique_field=unique_field,
        order_field=order_field,
        value_field=value_field,
    )


@router.get("/head", response_model=DatasetHeadResponse)
def dataset_head(n: int = 10) -> DatasetHeadResponse:
    _ensure_df_ready()
    n = max(1, min(n, 100))
    df = state.df.head(n).copy()

    # datetime → str, чтобы JSON-сериализовалось
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].astype(str)

    rows = df.to_dict("records")

    return DatasetHeadResponse(rows=rows)


# ============================================================
# upload / configure / build / status / reset
# ============================================================

def _upload_path(upload_id: str) -> Path:
    return UPLOADS_DIR / f"{upload_id}.csv"


@router.post("/upload", response_model=UploadResponse)
async def dataset_upload(file: UploadFile = File(...)) -> UploadResponse:
    """Загрузить CSV, вернуть колонки и preview. Индексы не строятся."""
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. размер
    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > MAX_UPLOAD_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"Файл слишком большой: {size_mb:.1f} МБ, максимум {MAX_UPLOAD_SIZE_MB} МБ",
        )

    # 2. сохранить во временный файл
    upload_id = uuid.uuid4().hex
    path = _upload_path(upload_id)
    path.write_bytes(content)

    # 3. загрузить в df
    try:
        df = load_dataset(path, order_field=None)
    except Exception as e:
        path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=f"Не удалось прочитать CSV: {e}")

    # 4. валидация
    errors = validate_upload(df)
    if errors:
        path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail="; ".join(errors))

    # 5. preview (первые 5 строк, datetime → str)
    preview_df = df.head(5).copy()
    for col in preview_df.columns:
        if hasattr(preview_df[col].iloc[0], "isoformat"):
            preview_df[col] = preview_df[col].astype(str)

    return UploadResponse(
        upload_id=upload_id,
        columns=list(df.columns),
        preview=preview_df.to_dict("records"),
        rows=len(df),
    )


@router.post("/configure", response_model=ConfigureResponse)
async def dataset_configure(req: ConfigureRequest) -> ConfigureResponse:
    """Применить поля к загруженному CSV. Индексы не строятся."""
    # 1. найти файл
    path = _upload_path(req.upload_id)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Загрузка не найдена")

    # 2. загрузить df
    df = load_dataset(path, order_field=None)

    # 3. валидация полей
    errors = validate_fields(df, req.fields)

    # если выбрана структура graph — проверить source/target
    # (проверим в /build, здесь только базовые)

    if errors:
        raise HTTPException(status_code=400, detail="; ".join(errors))

    # 4. преобразовать df: order → datetime, value → numeric, сортировка
    order_field = req.fields["order"]
    value_field = req.fields["value"]

    df[order_field] = pd.to_datetime(df[order_field])
    df[value_field] = pd.to_numeric(df[value_field], errors="raise")
    df = df.sort_values(order_field).reset_index(drop=True)

    # 5. обновить state
    state.df = df
    state.fields = req.fields.copy()
    state.keys = df[req.fields["unique_id"]].tolist()
    state.values = df[value_field].tolist()
    state.original_values = state.values.copy()

    # 6. сбросить старые структуры и статус
    state.clear_structures()
    state.reset_build_status()

    # 7. удалить кэш графа (новый датасет — новый граф)
    from config import GRAPH_CACHE_PATH
    if GRAPH_CACHE_PATH.exists():
        GRAPH_CACHE_PATH.unlink()

    return ConfigureResponse(
        status="ok",
        rows=len(df),
        fields=req.fields,
    )


async def _build_structures(structures: list[str]) -> None:
    """Фоновая задача: строит индексы по state.df / state.fields."""
    state.build_status = "building"
    state.build_progress = 0.0
    state.build_error = ""
    state.build_structures = list(structures)

    try:
        total = len(structures)
        if total == 0:
            state.build_status = "ready"
            return

        for i, s in enumerate(structures):
            if s == "hash":
                state.hash_index, state.hash_build_ms = await asyncio.to_thread(
                    hash_service.build_hash_index,
                    state.df, state.fields["unique_id"],
                )
            elif s == "segment":
                state.segment_index, state.segment_build_ms = await asyncio.to_thread(
                    segment_service.build_segment_index,
                    state.df, state.fields["order"], state.fields["value"],
                )
            elif s == "graph":
                state.graph, state.graph_build_ms, _ = await asyncio.to_thread(
                    graph_service.build_or_load_product_graph,
                    state.df, state.fields["source"], state.fields["target"],
                )
                state.graph_vertices = state.graph.num_vertices()
                state.graph_edges = state.graph.num_edges()

            state.build_progress = (i + 1) / total
            await asyncio.sleep(0)

        state.build_status = "ready"
    except Exception as e:
        state.build_status = "error"
        state.build_error = str(e)


@router.post("/build", response_model=BuildResponse)
async def dataset_build(req: BuildRequest) -> BuildResponse:
    """Запустить построение индексов в фоне. Сразу отвечает."""
    if not state.is_df_ready:
        raise HTTPException(status_code=400, detail="Сначала загрузите и настройте датасет")

    if state.is_building:
        raise HTTPException(status_code=409, detail="Построение уже идёт")

    # валидация структур
    allowed = {"hash", "segment", "graph"}
    bad = set(req.structures) - allowed
    if bad:
        raise HTTPException(status_code=400, detail=f"Неизвестные структуры: {bad}")

    # для графа — проверить source/target
    if "graph" in req.structures:
        errors = validate_graph_fields(state.df, state.fields)
        if errors:
            raise HTTPException(status_code=400, detail="; ".join(errors))

    # запустить в фоне
    asyncio.create_task(_build_structures(req.structures))

    return BuildResponse(status="started")


@router.get("/build/status", response_model=BuildStatusResponse)
async def dataset_build_status() -> BuildStatusResponse:
    """Прогресс фонового построения."""
    return BuildStatusResponse(
        status=state.build_status,
        progress=state.build_progress,
        error=state.build_error,
        structures=state.build_structures,
    )


@router.post("/reset", response_model=ResetResponse)
async def dataset_reset() -> ResetResponse:
    """Вернуть дефолтный датасет (синхронно, без фона)."""
    state.fields = DEFAULT_FIELDS.copy()
    df = load_dataset(DATA_PATH, order_field=state.fields["order"])
    state.df = df
    state.keys = df[state.fields["unique_id"]].tolist()
    state.values = df[state.fields["value"]].tolist()
    state.original_values = state.values.copy()

    state.clear_structures()
    state.reset_build_status()

    # перестроить hash и segment (быстро), граф — через кэш или пропустить
    state.hash_index, state.hash_build_ms = hash_service.build_hash_index(
        df, state.fields["unique_id"],
    )
    state.segment_index, state.segment_build_ms = segment_service.build_segment_index(
        df, state.fields["order"], state.fields["value"],
    )
    state.graph, state.graph_build_ms, _ = graph_service.build_or_load_product_graph(
        df, state.fields["source"], state.fields["target"],
    )
    state.graph_vertices = state.graph.num_vertices()
    state.graph_edges = state.graph.num_edges()

    return ResetResponse(status="ok", rows=len(df))