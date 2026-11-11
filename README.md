# learn-api

学习用 Todo API，FastAPI + SQLAlchemy + SQLite。

## 快速开始
1. python -m venv .venv && .venv\Scripts\activate
2. pip install -r requirements-dev.txt
3. cp .env.example .env，填入 SECRET_KEY（python -c "import secrets; print(secrets.token_urlsafe(48))"）
4. python -m uvicorn main:app --reload
5. 打开 http://127.0.0.1:8000/docs

## 测试
python -m pytest -q

## 目录结构
（app/core 配置与安全、app/routers 路由、app/models ORM、app/schemas 进出参、tests 测试、scripts 一次性脚本）

## 已知问题 / 下一步
- 无分页、todos.owner_id 无索引
- register 竞态、PUT 传 null 会 500
- 无 Alembic 迁移