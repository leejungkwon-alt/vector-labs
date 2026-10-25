# tests/test_api.py

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Saju Engine API is running successfully!"}


def test_calculate_saju_endpoint():
    payload = {
        "birth_date": "1990-05-05",
        "birth_time": "14:30:00",
        "timezone_str": "Asia/Seoul",
        "longitude": 126.9780,
        "correction_mode": "lmt",
        "jasi_boundary": 23,
    }

    response = client.post("/api/v1/saju/calculate", json=payload)
    assert response.status_code == 200
    data = response.json()

    for field in (
        "solar_year",
        "year_pillar",
        "month_pillar",
        "day_pillar",
        "hour_pillar",
        "solar_adjusted_time",
        "birth_instant_utc",
        "ten_gods",
    ):
        assert field in data

    assert data["solar_year"] == 1990
    assert data["year_pillar"] == "庚午"
    assert data["month_pillar"] == "庚辰"
    assert data["day_pillar"] == "庚午"
    assert data["hour_pillar"] == "癸未"
    
    # 시스템 코드 적용 여부 검증
    assert data["ten_gods"]["day_pillar"]["stem"] == "ROLE_DAY_MASTER"


def test_calculate_saju_with_target_year_endpoint():
    payload = {
        "birth_date": "1990-05-05",
        "birth_time": "14:30:00",
        "timezone_str": "Asia/Seoul",
        "longitude": 126.9780,
        "correction_mode": "lmt",
        "jasi_boundary": 23,
        "gender": "M",
        "target_year": 2026,
    }

    response = client.post("/api/v1/saju/calculate", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "luck_info" in data
    luck_info = data["luck_info"]
    assert luck_info is not None
    assert luck_info["target_year"] == 2026
    assert "annual_luck" in luck_info
    assert "monthly_lucks" in luck_info
    assert len(luck_info["monthly_lucks"]) == 12


def test_calculate_saju_invalid_jasi_boundary():
    payload = {
        "birth_date": "1990-05-05",
        "birth_time": "14:30:00",
        "jasi_boundary": 12,
    }
    response = client.post("/api/v1/saju/calculate", json=payload)
    assert response.status_code == 422


def test_calculate_saju_eot_not_implemented():
    payload = {
        "birth_date": "1990-05-05",
        "birth_time": "14:30:00",
        "correction_mode": "eot",
    }
    response = client.post("/api/v1/saju/calculate", json=payload)
    assert response.status_code == 422