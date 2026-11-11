def test_register_ok(client):
    r = client.post("/users/register", json={"username": "alice", "password": "secret123"})
    assert r.status_code == 201
    assert r.json()["username"] == "alice"
    assert "password" not in r.json()          # 不能泄露密码字段（含哈希）


def test_register_duplicate(client):
    client.post("/users/register", json={"username": "alice", "password": "secret123"})
    r = client.post("/users/register", json={"username": "alice", "password": "secret123"})
    assert r.status_code == 400                # 下周会改成 409，这个用例到时候先红后绿


def test_login_wrong_password(client):
    client.post("/users/register", json={"username": "alice", "password": "secret123"})
    r = client.post("/users/login", data={"username": "alice", "password": "wrong"})
    assert r.status_code == 401


def test_register_short_password(client):
    r = client.post("/users/register", json={"username": "alice", "password": "1"})
    assert r.status_code == 422