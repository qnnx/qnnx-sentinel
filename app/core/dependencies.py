from fastapi import Header, HTTPException

async def get_db():
    # Placeholder - baad mein real database connection aayega
    db = None
    try:
        yield db
    finally:
        pass

async def get_current_user(authorization: str = Header(None)):
    # Placeholder - baad mein real authentication aayega
    if authorization is None:
        return {"id": "mock-user", "name": "Mock User", "role": "admin"}
    return {"id": "mock-user", "name": "Mock User", "role": "admin"}

async def validate_api_key(x_api_key: str = Header(None)):
    # Placeholder - baad mein real API key validation aayega
    if x_api_key is None:
        raise HTTPException(
            status_code=401,
            detail="API Key required"
        )
    return x_api_key