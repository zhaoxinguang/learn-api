from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.schemas import TodoCreate, TodoUpdate, TodoOut,TodoPage
from app.dependencies import get_current_user

router = APIRouter(prefix="/todos", tags=["todos"])

SORT_COLUMNS = {
    "created_at": models.Todo.created_at,
    "id": models.Todo.id,
    "title": models.Todo.title,
}

SortKey = Literal["created_at", "-created_at", "id", "-id", "title", "-title"]

@router.post("", response_model=TodoOut, status_code=201)
def create_todo(
    todo: TodoCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    item = models.Todo(title=todo.title, done=todo.done, owner_id=current_user.id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.get("", response_model=TodoPage)
def list_todos(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    done: bool | None = Query(None),
    sort: SortKey = Query("-created_at"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    query = db.query(models.Todo).filter(models.Todo.owner_id == current_user.id)

    if done is not None:
        query = query.filter(models.Todo.done == done)

    total = query.count()

    desc = sort.startswith("-")
    field = sort.removeprefix("-")
    column = SORT_COLUMNS[field]
    order_clause = column.desc() if desc else column.asc()

    items = (
        query.order_by(order_clause, models.Todo.id.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return TodoPage(items=items, total=total, limit=limit, offset=offset)



@router.get("/{todo_id}", response_model=TodoOut)
def get_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    item = db.get(models.Todo, todo_id)
    if not item or item.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Todo not found")
    return item


@router.put("/{todo_id}", response_model=TodoOut)
def update_todo(
    todo_id: int,
    todo: TodoUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    item = db.get(models.Todo, todo_id)
    if not item or item.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Todo not found")

    for key, value in todo.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{todo_id}", status_code=204)
def delete_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    item = db.get(models.Todo, todo_id)
    if not item or item.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(item)
    db.commit()
    return