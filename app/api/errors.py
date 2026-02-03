from fastapi import HTTPException


def bad_request(msg: str) -> HTTPException:
    return HTTPException(status_code=400, detail=msg)

def forbidden(msg: str = "Forbidden") -> HTTPException:
    return HTTPException(status_code=403, detail=msg)
