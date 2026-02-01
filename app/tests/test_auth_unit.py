def test_register_validation(client):
    r = client.post("/auth/register", json={
        "email": "bad",
        "username": "",
        "password": "123"
    })
    assert r.status_code == 400

def test_register_and_login(client):
    r = client.post("/auth/register", json={
        "email": "a@test.com",
        "username": "a",
        "password": "StrongPass!1"
    })
    assert r.status_code == 201

    r = client.post("/auth/login", json={
        "email": "a@test.com",
        "password": "StrongPass!1"
    })
    assert r.status_code == 200
