def test_requires_auth(client):
    assert client.get("/todos").status_code == 401


def test_crud_flow(client, alice):
    r = client.post("/todos", json={"title": "写测试"}, headers=alice)
    assert r.status_code == 201
    todo_id = r.json()["id"]

    assert len(client.get("/todos", headers=alice).json()) == 1
    assert client.get(f"/todos/{todo_id}", headers=alice).json()["title"] == "写测试"

    assert client.delete(f"/todos/{todo_id}", headers=alice).status_code == 204
    assert client.get(f"/todos/{todo_id}", headers=alice).status_code == 404


def test_cross_user_isolation(client, alice):
    todo_id = client.post("/todos", json={"title": "alice 的"}, headers=alice).json()["id"]
    client.post("/users/register", json={"username": "bob", "password": "secret123"})
    r = client.post("/users/login", data={"username": "bob", "password": "secret123"})
    bob = {"Authorization": f"Bearer {r.json()['access_token']}"}

    # B 拿不到 A 的数据，且返回 404 而不是 403（不暴露“这条存在”）
    assert client.get(f"/todos/{todo_id}", headers=bob).status_code == 404


def test_empty_title(client, alice):
    assert client.post("/todos", json={"title": ""}, headers=alice).status_code == 422