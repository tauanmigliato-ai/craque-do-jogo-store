import sys, hmac, hashlib, json
sys.path.insert(0, 'backend')

import os
from unittest.mock import patch, MagicMock

os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("PAGARME_API_KEY", "test-pagarme-key")
os.environ.setdefault("DATABASE_URL", "/tmp/test_craque.db")

# Cria diretórios necessários para evitar PermissionError no import
os.makedirs("/tmp/craque-do-jogo/uploads", exist_ok=True)

# Patch makedirs para redirecionar /opt para /tmp durante import do main
_orig_makedirs = os.makedirs

def _patched_makedirs(path, *args, **kwargs):
    path = str(path).replace("/opt/craque-do-jogo", "/tmp/craque-do-jogo")
    return _orig_makedirs(path, *args, **kwargs)

os.makedirs = _patched_makedirs

# Patch StaticFiles para evitar erro de diretório inexistente
with patch("starlette.staticfiles.StaticFiles.__init__", return_value=None):
    from main import app

os.makedirs = _orig_makedirs  # restaura após import

from fastapi.testclient import TestClient
client = TestClient(app)

API_KEY = "test-pagarme-key"


def make_signature(body: bytes, key: str = API_KEY) -> str:
    sig = hmac.new(key.encode(), body, hashlib.sha1).hexdigest()
    return f"sha1={sig}"


def test_webhook_rejects_missing_signature():
    body = json.dumps({"current_status": "paid", "order_id": "1"}).encode()
    resp = client.post(
        "/api/webhooks/pagarme",
        content=body,
        headers={"Content-Type": "application/json"},
    )
    assert resp.status_code == 400


def test_webhook_rejects_invalid_signature():
    body = json.dumps({"current_status": "paid", "order_id": "1"}).encode()
    resp = client.post(
        "/api/webhooks/pagarme",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature": "sha1=invalido",
        },
    )
    assert resp.status_code == 400


def test_webhook_accepts_valid_signature():
    body = json.dumps({"current_status": "pending", "order_id": "1"}).encode()
    sig = make_signature(body)
    resp = client.post(
        "/api/webhooks/pagarme",
        content=body,
        headers={"Content-Type": "application/json", "X-Hub-Signature": sig},
    )
    assert resp.status_code == 200
