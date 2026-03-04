"""API integration tests"""
import pytest
from datetime import datetime, timezone

TEST_EMAIL = "test@example.com"
TEST_PASS = "testpass"


@pytest.mark.asyncio
async def test_health(client):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_auth_login(client, seed_data):
    r = await client.post("/auth/login", json={"email": TEST_EMAIL, "password": TEST_PASS})
    assert r.status_code == 200
    assert "access_token" in r.json()


@pytest.mark.asyncio
async def test_auth_me(client, seed_data):
    login = await client.post("/auth/login", json={"email": TEST_EMAIL, "password": TEST_PASS})
    token = login.json()["access_token"]
    r = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["email"] == TEST_EMAIL


@pytest.mark.asyncio
async def test_auth_wrong_password(client, seed_data):
    r = await client.post("/auth/login", json={"email": TEST_EMAIL, "password": "wrong"})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_qr_token(client, seed_data):
    cage = seed_data["cage"]
    r = await client.get(f"/qr/{cage.qr_token}")
    assert r.status_code == 200
    assert r.json()["cage_id"] == cage.id


@pytest.mark.asyncio
async def test_qr_token_invalid(client, db_session):
    r = await client.get("/qr/invalid-token-xyz")
    assert r.status_code == 404


async def _login(client) -> str:
    login = await client.post("/auth/login", json={"email": TEST_EMAIL, "password": TEST_PASS})
    return login.json()["access_token"]


@pytest.mark.asyncio
async def test_event_feeding(client, seed_data):
    token = await _login(client)
    headers = {"Authorization": f"Bearer {token}"}
    cage = seed_data["cage"]
    r = await client.post("/events", json={
        "event_type": "FEEDING",
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "cage_id": cage.id,
        "payload_json": {"feed_kg": 25.5, "feed_type": "生餌", "memo": "通常給餌"},
    }, headers=headers)
    assert r.status_code == 201
    data = r.json()
    assert data["event_type"] == "FEEDING"
    assert data["payload_json"]["feed_kg"] == 25.5


@pytest.mark.asyncio
async def test_event_mortality(client, seed_data):
    token = await _login(client)
    headers = {"Authorization": f"Bearer {token}"}
    cage = seed_data["cage"]
    r = await client.post("/events", json={
        "event_type": "MORTALITY",
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "cage_id": cage.id,
        "payload_json": {"dead_count": 5, "cause_guess": "不明"},
    }, headers=headers)
    assert r.status_code == 201
    assert r.json()["payload_json"]["dead_count"] == 5


@pytest.mark.asyncio
async def test_event_sampling(client, seed_data):
    token = await _login(client)
    headers = {"Authorization": f"Bearer {token}"}
    cage = seed_data["cage"]
    r = await client.post("/events", json={
        "event_type": "SAMPLING",
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "cage_id": cage.id,
        "payload_json": {"sample_count": 20, "avg_weight_g": 620.5, "avg_length_cm": 35.2},
    }, headers=headers)
    assert r.status_code == 201
    assert r.json()["payload_json"]["avg_weight_g"] == 620.5
