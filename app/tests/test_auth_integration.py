def test_protected_requires_auth(client):
    r = client.get("/notes")
    assert r.status_code == 401
