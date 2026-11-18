import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "version" in data


def test_presets_endpoint():
    response = client.get("/api/criteria/presets")
    assert response.status_code == 200
    presets = response.json()
    assert isinstance(presets, list)
    assert len(presets) >= 4


def test_ahp_calculation():
    matrix = [
        [1.0, 1.0, 1.0, 1.0],
        [1.0, 1.0, 1.0, 1.0],
        [1.0, 1.0, 1.0, 1.0],
        [1.0, 1.0, 1.0, 1.0]
    ]
    response = client.post("/api/criteria/ahp", json={"matrix": matrix})
    assert response.status_code == 200
    data = response.json()
    assert "weights" in data
    assert data["consistency_ratio"] == 0.0
