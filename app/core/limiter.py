from fastapi import Request
from slowapi import Limiter


def get_client_identifier(request: Request) -> str:
    authorization = request.headers.get("Authorization")
    if authorization:
        return authorization
    return request.client.host if request.client else "anonymous"


limiter = Limiter(key_func=get_client_identifier)
