from pydantic import BaseModel, Field, field_validator

class TodoCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    done: bool = False

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("title 不能为空白")
        return v


class TodoUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    done: bool | None = None

    @field_validator("title")
    @classmethod
    def title_not_null_or_blank(cls, v: str | None) -> str:
        if v is None:
            raise ValueError("title 不能为 null")
        v = v.strip()
        if not v:
            raise ValueError("title 不能为空白")
        return v

    @field_validator("done")
    @classmethod
    def done_not_null(cls, v: bool | None) -> bool:
        if v is None:
            raise ValueError("done 不能为 null")
        return v

class TodoOut(BaseModel):
    id: int
    title: str
    done: bool

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=72)   # bcrypt 上限 72 字节


class UserOut(BaseModel):
    id: int
    username: str

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

model_config = {"from_attributes": True}  