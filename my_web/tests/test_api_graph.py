"""API-тесты графа через TestClient."""

from __future__ import annotations


# ============================================================
# /api/graph/info
# ============================================================

def test_graph_info(client):
    r = client.get("/api/graph/info")
    assert r.status_code == 200
    data = r.json()

    assert data["vertices"] == 1000
    assert data["edges"] > 0
    assert data["components"] >= 1
    assert data["build_ms"] >= 0


# ============================================================
# /api/graph/paths
# ============================================================

def test_graph_paths_ok(client):
    r = client.get("/api/graph/paths?source=1&target=36&k=3")
    assert r.status_code == 200
    data = r.json()

    assert data["source"] == 1
    assert data["target"] == 36
    assert data["k"] == 3
    assert isinstance(data["paths"], list)
    assert len(data["paths"]) <= 3
    assert data["dijkstra_ms"] >= 0
    assert data["yen_ms"] >= 0

    # каждый путь — валидная структура
    for p in data["paths"]:
        assert isinstance(p["nodes"], list)
        assert len(p["nodes"]) >= 2
        assert p["nodes"][0] == 1
        assert p["nodes"][-1] == 36
        assert p["distance"] >= 0
        assert p["length"] == len(p["nodes"]) - 1

    # пути отсортированы по distance
    dists = [p["distance"] for p in data["paths"]]
    assert dists == sorted(dists)


def test_graph_paths_k1(client):
    """K=1 — ровно один путь."""

    r = client.get("/api/graph/paths?source=1&target=36&k=1")
    assert r.status_code == 200
    assert len(r.json()["paths"]) == 1


def test_graph_paths_missing_source(client):
    r = client.get("/api/graph/paths?source=99999&target=36&k=3")
    assert r.status_code == 400
    assert "99999" in r.json()["detail"]


def test_graph_paths_missing_target(client):
    r = client.get("/api/graph/paths?source=1&target=99999&k=3")
    assert r.status_code == 400
    assert "99999" in r.json()["detail"]


def test_graph_paths_same_source_target(client):
    r = client.get("/api/graph/paths?source=1&target=1&k=3")
    assert r.status_code == 400


def test_graph_paths_k_out_of_range(client):
    # k = 0
    r = client.get("/api/graph/paths?source=1&target=36&k=0")
    assert r.status_code == 422   # FastAPI валидация (ge=1)

    # k > MAX_K
    r = client.get("/api/graph/paths?source=1&target=36&k=100")
    assert r.status_code == 422


# ============================================================
# /api/graph/benchmark
# ============================================================

def test_graph_benchmark(client):
    r = client.get("/api/graph/benchmark?source=1&target=36&k=3")
    assert r.status_code == 200
    data = r.json()

    assert data["source"] == 1
    assert data["target"] == 36
    assert data["k"] == 3
    assert data["dijkstra_ms"] >= 0
    assert data["yen_ms"] >= 0
    # speedup = yen / dijkstra — может быть None, если dijkstra_ms == 0
    if data["speedup"] is not None:
        assert data["speedup"] >= 0


def test_graph_benchmark_k1(client):
    """При K=1 Йен ≈ Дейкстра."""

    r = client.get("/api/graph/benchmark?source=1&target=36&k=1")
    assert r.status_code == 200


# ============================================================
# /api/graph/products
# ============================================================

def test_graph_products(client):
    r = client.get("/api/graph/products?limit=10")
    assert r.status_code == 200
    data = r.json()

    assert isinstance(data, list)
    assert len(data) == 10
    for item in data:
        assert item["product_id"] >= 1
        assert item["purchases"] >= 1

    # отсортированы по purchases (убывание)
    purchases = [item["purchases"] for item in data]
    assert purchases == sorted(purchases, reverse=True)


def test_graph_products_limit_bounds(client):
    # limit = 0 → 422
    r = client.get("/api/graph/products?limit=0")
    assert r.status_code == 422

    # limit > 1000 → 422
    r = client.get("/api/graph/products?limit=10000")
    assert r.status_code == 422


# ============================================================
# HTML-страницы
# ============================================================

def test_graph_pages_return_html(client):
    for path in ["/graph", "/graph/demo", "/graph/benchmark"]:
        r = client.get(path)
        assert r.status_code == 200, f"{path} вернул {r.status_code}"
        assert "text/html" in r.headers["content-type"]


# ============================================================
# /docs — эндпоинты графа в OpenAPI
# ============================================================

def test_graph_endpoints_in_openapi(client):
    r = client.get("/openapi.json")
    assert r.status_code == 200
    spec = r.json()

    paths = spec["paths"]
    assert "/api/graph/info" in paths
    assert "/api/graph/paths" in paths
    assert "/api/graph/benchmark" in paths
    assert "/api/graph/products" in paths