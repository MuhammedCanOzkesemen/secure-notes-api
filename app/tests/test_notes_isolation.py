def test_user_isolation(client):
    client.post("/auth/register", json={
        "email": "a@test.com",
        "username": "a",
        "password": "StrongPass!1"
    })
    client.post("/auth/login", json={
        "email": "a@test.com",
        "password": "StrongPass!1"
    })

    r = client.post("/notes", json={
        "title": "A",
        "content": "secret"
    })
    note_id = r.get_json()["id"]

    client.post("/auth/logout")

    client.post("/auth/register", json={
        "email": "b@test.com",
        "username": "b",
        "password": "StrongPass!1"
    })
    client.post("/auth/login", json={
        "email": "b@test.com",
        "password": "StrongPass!1"
    })

    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 404
