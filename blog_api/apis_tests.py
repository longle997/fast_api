import string
import random

from fastapi.testclient import TestClient

from .main import app

client = TestClient(app)

def test_get_all_users():
    response = client.get("users/")
    assert response.status_code == 200


def test_create_user():
    sample_user = {
        "email" : _random_string(),
        "password": _random_string()
    }
    response = client.post("users/", json=sample_user)

    assert response.status_code == 200
    assert response.json()["email"] == sample_user["email"]


def _random_string():
    letters = string.ascii_letters
    result = ''.join(random.choice(letters) for _ in range(10))

    return result