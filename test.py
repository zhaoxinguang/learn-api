import requests

try:
    r = requests.get(
    "https://httpbin.org/delay/10",
    params={"name": "alice", "age": 20},
    headers={"X-My-Token": "abc123"},
    timeout=2,
    )
    # print(r.json()["args"])      # 看查询参数
    # print(r.json()["headers"])
    print(r.status_code)
except requests.Timeout:
    print("请求超时")