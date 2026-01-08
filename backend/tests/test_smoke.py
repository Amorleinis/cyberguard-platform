import os
import sys
from datetime import datetime
from types import SimpleNamespace
from fastapi.testclient import TestClient

# Ensure backend package is importable when tests run from repo root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app  # noqa: E402
from app.api.auth import get_current_user  # noqa: E402


def _fake_user():
    """Lightweight user stub for auth-protected demo routes."""
    return SimpleNamespace(
        id=1,
        email="test@example.com",
        username="tester",
        full_name="Test User",
        is_superuser=True,
        subscription_plan="free",
        created_at=datetime.utcnow(),
    )


app.dependency_overrides[get_current_user] = _fake_user
client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("status") == "healthy"


def test_dashboard():
    resp = client.get("/api/v1/dashboard")
    assert resp.status_code == 200
    body = resp.json()
    assert "active_threats" in body
    assert "blocked_threats" in body


def test_threats():
    resp = client.get("/api/v1/threats")
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body.get("threats"), list)


def test_websocket_connects():
    with client.websocket_connect("/ws/threats") as websocket:
        msg = websocket.receive_json()
        assert msg.get("type") in {"connection", "threat"}
