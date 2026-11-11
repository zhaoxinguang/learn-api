import requests

for i in range(500):
    username = f"user_{i}"
    password = "123456"
    # 注册
    requests.post("http://127.0.0.1:8000/users/register", json={"username": username, "password": password})