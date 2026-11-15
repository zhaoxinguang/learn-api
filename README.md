## 项目介绍
这是一个带用户隔离的 Todo REST API：注册/登录、JWT 鉴权、Todo 增删改查、统一错误格式、请求日志、9 个自动化测试
### 技术栈
FastApi : 原生支持异步，在处理数据库查询等耗时操作时会让出控制权，避免干等
Uvicorn : ASGI服务器，特点是轻量适合开发，生产环境要配多个worker
SQLAlchemy : 负责数据持久化，用python的类操作数据库表，换成SQL只用改URL
SQLite : 轻量数据库，作为应用程序的库，本身是个文件，不需要配置，适合学习环境，并发写需要排队，代价大
Pydantic : 参数/数据格式校验，省去手动判断
PyJWT : 服务端进行用户校验，服务器无状态，客户端每次登录携带，服务端用同样的密钥验证用户身份
pwdlib : 将明文密码哈希存储，防爆破
## 环境要求
Python 3.13+，macOS / Linux / Windows

## 快速开始（macOS / Linux）
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(48))"   # 填入 SECRET_KEY
python -m uvicorn main:app --reload
# 打开 http://127.0.0.1:8000/docs

## 数据库迁移
almebic upgrade head

## Windows
.venv\Scripts\activate

## 测试
python -m pytest -q