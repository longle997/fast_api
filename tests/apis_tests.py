import string
import random

from blog_api.schemas import User


def test_get_all_users(user_db, client):

    response = client.get("/users/")

    assert response.status_code == 200

    response_orm = [User.parse_obj(x) for x in response.json()]
    user_db_orm = [User.from_orm(x) for x in user_db]

    assert response_orm == user_db_orm


# Note: don't specify id in data json file, because when we create new instance from User class, it's primary key will count from 1
# if we specify id in data json file, primary key will be duplicate => error from database
def test_create_user(user_db, client):
    sample_user = {
        "email" : _random_string() + "@mailinator.com",
        "password": _random_string()
    }
    response = client.post("/users/", json=sample_user)

    assert response.status_code == 201
    assert response.json()["email"] == sample_user["email"]


def test_get_single_user(user_db, client):
    user_sample = random.choice(user_db)

    response = client.get(f"/users/{user_sample.email}")

    for k,v in response.json().items():
        assert getattr(user_sample, k) == v


def _random_string():
    letters = string.ascii_letters
    result = ''.join(random.choice(letters) for _ in range(10))

    return result