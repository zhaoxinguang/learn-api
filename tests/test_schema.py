import pytest
from sqlalchemy.exc import IntegrityError
from app import models


def test_foreign_key_enforced(db):
    db.add(models.Todo(title="孤儿", done=False, owner_id=9999))
    with pytest.raises(IntegrityError):
        db.commit()