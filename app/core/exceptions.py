from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail,
            "path": request.url.path,
        },
        headers=getattr(exc, "headers", None),
    )

def _jsonable_errors(errors):
    cleaned = []
    for err in errors:
        item = dict(err)
        if "ctx" in item:
            item["ctx"] = {k: str(v) for k, v in item["ctx"].items()}
        inp = item.get("input")
        if inp is not None and not isinstance(inp, (str, int, float, bool, list, dict)):
            item["input"] = repr(inp)
        cleaned.append(item)
    return cleaned

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": 422,
            "message": "Validation error",
            "errors": _jsonable_errors(exc.errors()),
            "path": request.url.path,
        },
    )