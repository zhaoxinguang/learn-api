from locust import HttpUser, task, between
import random

class MultiUser(HttpUser):
    wait_time = between(0.1, 0.5)

    def on_start(self):
        # 随机挑一个已注册的账号
        user_id = random.randint(0, 499)
        username = f"user_{user_id}"
        password = "123456"
        
        r = self.client.post("/users/login", data={"username": username, "password": password})
        if r.status_code == 200:
            self.token = r.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            print(f"登录失败: {username}")

    @task(3)
    def list_todos(self):
        # 真实场景应该是分页查，这里为了简化直接查
        self.client.get("/todos", headers=self.headers)

    @task(2)
    def create_todo(self):
        title = f"Task {random.randint(1, 10000)}"
        self.client.post("/todos", json={"title": title, "done": False}, headers=self.headers)