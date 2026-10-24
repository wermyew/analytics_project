"""API-тесты через TestClient."""

from __future__ import annotations


def test_dataset_info(client):
    r = client.get("/api/dataset/info")
    assert r.status_code == 200
    data = r.json()
    assert data["rows"] == 120_000
    assert data["unique_field"] == "order_id"
    assert data["order_field"] == "created_at"
    assert data["value_field"] == "total"
    assert data["total_sum"] > 0


def test_dataset_head(client):
    r = client.get("/api/dataset/head?n=5")
    assert r.status_code == 200
    rows = r.json()["rows"]
    assert len(rows) == 5
    assert "order_id" in rows[0]
    assert "created_at" in rows[0]


def test_hash_search_found(client):
    # order_id=60001 точно есть в датасете (1..120000)
    r = client.get("/api/hash/search/60001")
    assert r.status_code == 200
    data = r.json()
    assert data["found"] is True
    assert data["order_id"] == 60001
    assert data["row"]["order_id"] == 60001
    # hash и linear должны найти одну и ту же строку
    assert data["hash_row_id"] == data["linear_row_id"]
    assert data["hash_ms"] >= 0
    assert data["linear_ms"] >= 0


def test_hash_search_not_found(client):
    r = client.get("/api/hash/search/999999")
    assert r.status_code == 200
    data = r.json()
    assert data["found"] is False
    assert data["row"] is None
    assert data["hash_row_id"] is None


def test_hash_benchmark(client):
    r = client.get("/api/hash/benchmark?n_queries=10")
    assert r.status_code == 200
    data = r.json()
    assert data["n_queries"] == 10
    assert data["linear_ms"] >= 0
    assert data["hash_ms"] >= 0


def test_segment_query(client):
    r = client.get("/api/segment/query?l=0&r=999")
    assert r.status_code == 200
    data = r.json()
    assert data["l"] == 0
    assert data["r"] == 999
    assert data["matches"] is True
    assert abs(data["tree_sum"] - data["naive_sum"]) < 1e-6
    assert data["date_from"] <= data["date_to"]


def test_segment_query_invalid(client):
    # l > r
    r = client.get("/api/segment/query?l=100&r=50")
    assert r.status_code == 400

    # r за границей
    r = client.get("/api/segment/query?l=0&r=999999")
    assert r.status_code == 400

    # отрицательный l
    r = client.get("/api/segment/query?l=-1&r=10")
    assert r.status_code == 400


def test_segment_update_and_reset(client):
    # снимок исходного значения и суммы
    r = client.get("/api/segment/query?l=0&r=0")
    original_value = r.json()["tree_sum"]

    # update
    r = client.post("/api/segment/update", json={"pos": 0, "value": 9999.99})
    assert r.status_code == 200
    upd = r.json()
    assert upd["pos"] == 0
    assert abs(upd["new_value"] - 9999.99) < 1e-6
    assert abs(upd["old_value"] - original_value) < 1e-6

    # query видит новое значение
    r = client.get("/api/segment/query?l=0&r=0")
    assert abs(r.json()["tree_sum"] - 9999.99) < 1e-6

    # reset возвращает исходное
    r = client.post("/api/segment/reset", json={"pos": 0})
    assert r.status_code == 200
    rst = r.json()
    assert abs(rst["new_value"] - original_value) < 1e-6

    # query снова видит исходное
    r = client.get("/api/segment/query?l=0&r=0")
    assert abs(r.json()["tree_sum"] - original_value) < 1e-6


def test_segment_update_invalid_position(client):
    r = client.post("/api/segment/update", json={"pos": -1, "value": 100})
    assert r.status_code == 400

    r = client.post("/api/segment/update", json={"pos": 999999, "value": 100})
    assert r.status_code == 400


def test_segment_benchmark(client):
    r = client.get("/api/segment/benchmark?n_ops=200")
    assert r.status_code == 200
    data = r.json()
    assert data["n_ops"] == 200
    assert data["n_updates"] + data["n_queries"] == 200
    assert data["naive_ms"] >= 0
    assert data["tree_ms"] >= 0


def test_pages_return_html(client):
    for path in ["/", "/about", "/compare", "/hash", "/segment"]:
        r = client.get(path)
        assert r.status_code == 200, f"{path} вернул {r.status_code}"
        assert "text/html" in r.headers["content-type"]


def test_docs_available(client):
    r = client.get("/docs")
    assert r.status_code == 200
    r = client.get("/openapi.json")
    assert r.status_code == 200
    spec = r.json()
    assert "/api/hash/search/{order_id}" in spec["paths"]
    assert "/api/segment/query" in spec["paths"]
    assert "/api/segment/update" in spec["paths"]
    assert "/api/segment/reset" in spec["paths"]