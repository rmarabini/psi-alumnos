
# tests/test_persona_remote.py
import requests
import uuid
import pytest  # install with pip install pytest

BASE_URL = "https://persona-asq4.onrender.com/api/v1/personas/"  # Adjust if needed

def unique_email():
    return f"{uuid.uuid4().hex[:8]}@example.com"

@pytest.mark.parametrize("timeout", [10])
def test_persona_crud_remote(timeout):
    # --- CREATE ---
    payload = {
        "nombre": "Ada",
        "apellido": "Lovelace",
        "email": unique_email()
    }
    r = requests.post(BASE_URL, json=payload, timeout=timeout)
    assert r.status_code in (201, 200), f"Create failed: {r.status_code} {r.text}"
    created = r.json()
    persona_id = created.get("id") or created.get("pk")
    assert persona_id, f"No ID in response: {created}"
    print("persona_id", persona_id)
    # --- LIST ---
    r = requests.get(BASE_URL, timeout=timeout)
    assert r.status_code == 200
    assert isinstance(r.json(), list), "Expected list of personas"

    detail_url = f"{BASE_URL}{persona_id}/"

    # --- RETRIEVE ---
    r = requests.get(detail_url, timeout=timeout)
    assert r.status_code == 200
    data = r.json()
    assert data["nombre"] == "Ada"
    assert data["apellido"] == "Lovelace"

    # --- UPDATE (PUT) ---
    put_payload = {
        "nombre": "Ada",
        "apellido": "Byron",
        "email": payload["email"]
    }
    r = requests.put(detail_url, json=put_payload, timeout=timeout)
    assert r.status_code in (200, 202), f"PUT failed: {r.status_code} {r.text}"
    r = requests.get(detail_url, timeout=timeout)
    assert r.json()["apellido"] == "Byron"

    # --- DELETE ---
    r = requests.delete(detail_url, timeout=timeout)
    assert r.status_code in (204, 200), f"Delete failed: {r.status_code} {r.text}"
    r = requests.get(detail_url, timeout=timeout)
    assert r.status_code in (404, 410), f"Expected not found after delete, got {r.status_code}"

