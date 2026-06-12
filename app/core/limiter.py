from fastapi import Request
from slowapi import Limiter

def get_api_key_identifier(request: Request):
    # Extract the API key from the header. If missing, we label it "anonymous".
    return request.headers.get("X-API-Key", "anonymous")

limiter = Limiter(key_func=get_api_key_identifier)