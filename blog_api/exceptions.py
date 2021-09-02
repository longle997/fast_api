from fastapi import HTTPException

def ItemDoesNotExsit(detail: str):
    raise HTTPException(
        status_code=400,
        detail=detail
    )