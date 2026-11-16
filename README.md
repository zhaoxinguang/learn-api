# learn-api

一个带用户隔离的 Todo REST API：注册/登录、JWT 鉴权、Todo 增删改查、分页/过滤/排序、统一错误格式、请求日志、Alembic 迁移，以及 17 个自动化测试。

## 技术栈

| 技术 | 作用 |
|---|---|
| FastAPI | 原生支持异步，处理数据库查询等耗时操作时会让出控制权 |
| Uvicorn | ASGI 服务器，轻量，适合开发；生产环境要配多个 worker |
| SQLAlchemy | ORM，用 Python 类操作数据库表，换 MySQL 只需改连接 URL |
| SQLite | 轻量数据库，单文件、零配置，适合学习；并发写需要排队 |
| Pydantic | 参数/数据格式校验，省去手动判断 |
| PyJWT | 服务端无状态鉴权，客户端每次请求携带 Bearer token |
| pwdlib | 密码哈希（Argon2），不存明文 |
| Alembic | 数据库表版本管理，负责表结构变更与回退 |
| Docker | 镜像化运行，启动时自动执行迁移 |
| GitHub Actions | CI：ruff + pytest + 迁移 upgrade/downgrade 校验 |

## 环境要求

- Python 3.13+
- Docker（可选，用于容器运行；macOS 可用 OrbStack）

## 本地启动（macOS / Linux）

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(48))"   # 填入 .env 的 SECRET_KEY
alembic upgrade head
python -m uvicorn main:app --reload
# 打开 http://127.0.0.1:8000/docs
```

Windows 激活虚拟环境：

```bash
.venv\Scripts\activate
```

## Docker 启动

前置：安装 Docker（macOS 推荐 OrbStack）。

```bash
docker compose up -d --build
docker compose ps
```

等 `STATUS` 变成 `Up (healthy)` 后，打开 <http://127.0.0.1:8000/docs>。

容器启动时会先执行 `alembic upgrade head`，再启动 uvicorn，所以不需要手动迁移。

### 数据

- 容器内数据库：`/app/data/todo.db`
- 数据存在命名卷 `todo_data` 中
- `docker compose down` 保留数据；`docker compose down -v` 会删除
- 与本地 `todo.db` 是**两套独立数据**，互不影响

### 常用命令

```bash
docker compose logs -f api      # 看日志
docker compose exec api sh      # 进容器
docker compose exec api alembic current
docker compose up -d --build    # 改代码后重建
docker compose down             # 停止，保留数据
docker compose down -v          # 停止并删除数据
```

### 健康检查

- 每 30 秒请求一次 `/health`
- `start_period` 15 秒，给迁移和启动留时间
- 连续失败 3 次标记为 `unhealthy`
- Docker 只标记状态，**不会因为 unhealthy 自动重启**；`restart: unless-stopped` 只在进程退出时生效

### 注意

- `.env` 不会打进镜像，通过 compose 的 `env_file` 注入；
- 构建默认使用清华 PyPI 源（`PIP_INDEX_URL` 构建参数），可覆盖；
- 容器里没有 `--reload`，改代码需要 `docker compose up -d --build`；
- SQLite 适合单实例演示，生产环境应换 MySQL/PostgreSQL；
- `/health` 目前只检查进程存活，还不检查数据库。

## API

### 列表（分页 / 过滤 / 排序）

```http
GET /todos?limit=20&offset=0&done=true&sort=-created_at
```

- `limit`：1–100，默认 20
- `offset`：≥ 0，默认 0
- `done`：可选，`true` / `false`
- `sort`：`created_at`、`id`、`title`，前缀 `-` 表示倒序

响应：

```json
{
  "items": [
    {
      "id": 1,
      "title": "写文档",
      "done": false,
      "created_at": "2026-11-16T09:00:00",
      "updated_at": "2026-11-16T09:00:00"
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

其余接口可在 `/docs` 里查看。

## 数据库迁移

模型变更后，生成并应用迁移：

```bash
alembic revision --autogenerate -m "描述"
alembic upgrade head
```

回滚一个版本：

```bash
alembic downgrade -1
```

## 测试

```bash
python -m pytest -q
```

## CI

每次 push 到 `main` 或提交 PR，GitHub Actions 会执行：

1. `ruff check --select F,E9 .`
2. `python -m pytest -q`
3. 在临时库上 `alembic upgrade head` + `alembic downgrade base`
