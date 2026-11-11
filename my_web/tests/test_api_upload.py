"""API-тесты загрузки датасета: upload / configure / build / status / reset."""

from __future__ import annotations
import io
import time
import pandas as pd


# ============================================================
# helpers
# ============================================================

def _make_csv_bytes(n_rows: int = 100) -> bytes:
    """Сгенерировать простой CSV в памяти."""
    df = pd.DataFrame({
        "id": range(1, n_rows + 1),
        "date": pd.date_range("2024-01-01", periods=n_rows, freq="h").astype(str),
        "amount": [float(i * 10) for i in range(n_rows)],
        "prod": [(i % 10) + 1 for i in range(n_rows)],
        "user": [(i % 5) + 1 for i in range(n_rows)],
    })
    buf = io.BytesIO()
    df.to_csv(buf, index=False)
    return buf.getvalue()


def _upload(client, csv_bytes: bytes):
    return client.post(
        "/api/dataset/upload",
        files={"file": ("test.csv", csv_bytes, "text/csv")},
    )


def _configure(client, upload_id: str, fields: dict):
    return client.post(
        "/api/dataset/configure",
        json={"upload_id": upload_id, "fields": fields},
    )


# ============================================================
# upload
# ============================================================

def test_upload_ok(client):
    r = _upload(client, _make_csv_bytes())
    assert r.status_code == 200
    data = r.json()
    assert data["rows"] == 100
    assert "columns" in data
    assert set(data["columns"]) == {"id", "date", "amount", "prod", "user"}
    assert len(data["preview"]) <= 5
    assert "upload_id" in data


def test_upload_empty_file(client):
    r = _upload(client, b"")
    assert r.status_code == 400


def test_upload_not_csv(client):
    r = _upload(client, b"not a csv at all")
    assert r.status_code == 400


# ============================================================
# configure
# ============================================================

def test_configure_ok(client):
    r = _upload(client, _make_csv_bytes())
    upload_id = r.json()["upload_id"]

    fields = {
        "unique_id": "id",
        "order": "date",
        "value": "amount",
        "source": "prod",
        "target": "user",
    }
    r = _configure(client, upload_id, fields)
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["rows"] == 100
    assert data["fields"] == fields


def test_configure_missing_upload(client):
    fields = {
        "unique_id": "id",
        "order": "date",
        "value": "amount",
        "source": "prod",
        "target": "user",
    }
    r = _configure(client, "nonexistent_id", fields)
    assert r.status_code == 404


def test_configure_bad_unique(client):
    r = _upload(client, _make_csv_bytes())
    upload_id = r.json()["upload_id"]

    fields = {
        "unique_id": "user",   # не уникален
        "order": "date",
        "value": "amount",
        "source": "prod",
        "target": "user",
    }
    r = _configure(client, upload_id, fields)
    assert r.status_code == 400


# ============================================================
# build + status
# ============================================================

def _wait_build(client, timeout: float = 30.0):
    start = time.time()
    while time.time() - start < timeout:
        r = client.get("/api/dataset/build/status")
        assert r.status_code == 200
        data = r.json()
        if data["status"] in {"ready", "error"}:
            return data
        time.sleep(0.2)
    raise AssertionError(f"build не завершился за {timeout}s")


def test_build_hash_and_segment(client):
    r = _upload(client, _make_csv_bytes())
    upload_id = r.json()["upload_id"]

    fields = {
        "unique_id": "id",
        "order": "date",
        "value": "amount",
        "source": "prod",
        "target": "user",
    }
    r = _configure(client, upload_id, fields)
    assert r.status_code == 200

    r = client.post(
        "/api/dataset/build",
        json={"structures": ["hash", "segment"]},
    )
    assert r.status_code == 200
    assert r.json()["status"] == "started"

    data = _wait_build(client)
    assert data["status"] == "ready"
    assert data["progress"] == 1.0


def test_build_invalid_structure(client):
    r = _upload(client, _make_csv_bytes())
    upload_id = r.json()["upload_id"]

    fields = {
        "unique_id": "id",
        "order": "date",
        "value": "amount",
        "source": "prod",
        "target": "user",
    }
    _configure(client, upload_id, fields)

    r = client.post(
        "/api/dataset/build",
        json={"structures": ["invalid_structure"]},
    )
    assert r.status_code == 400


def test_build_without_configure(client):
    """Без configure — state.df остаётся от предыдущего теста или дефолта.
    Тест проверяет только, что /build не падает 500."""
    r = client.post("/api/dataset/build", json={"structures": []})
    # либо 200 (started), либо 400 (нет df) — оба валидны
    assert r.status_code in {200, 400}


# ============================================================
# reset
# ============================================================

def test_reset(client):
    r = client.post("/api/dataset/reset")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["rows"] == 120_000


def test_reset_restores_default_fields(client):
    client.post("/api/dataset/reset")
    r = client.get("/api/dataset/info")
    assert r.status_code == 200
    data = r.json()
    assert data["unique_field"] == "order_id"
    assert data["order_field"] == "created_at"
    assert data["value_field"] == "total"