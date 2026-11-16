from datetime import datetime

import pytest


def test_requires_auth(client):
    assert client.get("/todos").status_code == 401


def test_crud_flow(client, alice):
    r = client.post("/todos", json={"title": "写测试"}, headers=alice)
    assert r.status_code == 201
    todo_id = r.json()["id"]

    body = client.get("/todos", headers=alice).json()
    assert body["total"] == 1
    assert len(body["items"]) == 1
    assert body["items"][0]["created_at"]
    assert body["items"][0]["updated_at"]

    assert client.get(f"/todos/{todo_id}", headers=alice).json()["title"] == "写测试"

    assert client.delete(f"/todos/{todo_id}", headers=alice).status_code == 204
    assert client.get(f"/todos/{todo_id}", headers=alice).status_code == 404
    assert client.get("/todos", headers=alice).json()["total"] == 0


def test_cross_user_isolation(client, alice):
    todo_id = client.post("/todos", json={"title": "alice 的"}, headers=alice).json()["id"]
    client.post("/users/register", json={"username": "bob", "password": "secret123"})
    r = client.post("/users/login", data={"username": "bob", "password": "secret123"})
    bob = {"Authorization": f"Bearer {r.json()['access_token']}"}

    # B 拿不到 A 的数据，且返回 404 而不是 403（不暴露“这条存在”）
    assert client.get(f"/todos/{todo_id}", headers=bob).status_code == 404
    assert client.get("/todos", headers=bob).json()["total"] == 0


def test_empty_title(client, alice):
    assert client.post("/todos", json={"title": ""}, headers=alice).status_code == 422


def test_pagination(client, alice):
    for i in range(3):
        r = client.post("/todos", json={"title": f"t{i}"}, headers=alice)
        assert r.status_code == 201

    page1 = client.get("/todos?limit=2&offset=0", headers=alice).json()
    assert page1["total"] == 3
    assert page1["limit"] == 2
    assert page1["offset"] == 0
    assert len(page1["items"]) == 2

    page2 = client.get("/todos?limit=2&offset=2", headers=alice).json()
    assert len(page2["items"]) == 1

    ids = [x["id"] for x in page1["items"]] + [x["id"] for x in page2["items"]]
    assert len(ids) == len(set(ids)) == 3


@pytest.mark.parametrize(
    "query",
    ["limit=0", "limit=101", "offset=-1", "sort=bad", "done=notabool"],
)
def test_list_rejects_invalid_query(client, alice, query):
    assert client.get(f"/todos?{query}", headers=alice).status_code == 422


def test_filter_and_sort(client, alice):
    client.post("/todos", json={"title": "bravo", "done": True}, headers=alice)
    client.post("/todos", json={"title": "alpha", "done": False}, headers=alice)
    client.post("/todos", json={"title": "charlie", "done": True}, headers=alice)

    done = client.get("/todos?done=true", headers=alice).json()
    assert done["total"] == 2
    assert {x["title"] for x in done["items"]} == {"bravo", "charlie"}

    asc = client.get("/todos?sort=title", headers=alice).json()
    assert [x["title"] for x in asc["items"]] == ["alpha", "bravo", "charlie"]

    desc = client.get("/todos?sort=-title", headers=alice).json()
    assert [x["title"] for x in desc["items"]] == ["charlie", "bravo", "alpha"]


def test_timestamps(client, alice):
    created = client.post("/todos", json={"title": "time"}, headers=alice).json()
    assert datetime.fromisoformat(created["created_at"])
    assert datetime.fromisoformat(created["updated_at"])

    updated = client.put(
        f"/todos/{created['id']}", json={"title": "time2"}, headers=alice
    ).json()
    assert updated["created_at"] == created["created_at"]
    assert datetime.fromisoformat(updated["updated_at"]) >= datetime.fromisoformat(
        created["updated_at"]
    )
