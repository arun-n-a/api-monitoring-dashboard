from datetime import (
    datetime, timedelta, timezone)
from typing import Optional

import jwt # Changed from jose import jwt
from jwt import PyJWTError # Changed from jose import JWTError
import redis.asyncio as redis
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext

from app.core.config import settings
from app.core.exceptions import InvalidCredentialsException
from app.core.redis_config import get_redis_client


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against a hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hashes a plain password.
    """
    return pwd_context.hash(password)


def create_access_token(purpose: str, data: dict, expiry_in_minutes: timedelta) -> str:
    """
    Creates a JWT access token using PyJWT.
    """
    expire = datetime.now(timezone.utc) + timedelta(seconds=expiry_in_minutes)
    to_encode = {"exp": expire, "sub": purpose, **data}
    access_token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return access_token


async def create_login_token(user_data: dict, redis_client: redis.Redis) -> str:
    """
    Creates a JWT login token and stores it in Redis.
    """
    purpose = 'login'
    data = {
        "id": user_data["id"],
        "email": user_data["email"],
        "first_name": user_data["first_name"],
        "last_name": user_data["last_name"],
        "department_id": user_data.get("department_id"),
        "role_id": user_data["role_id"],
        "permissions": user_data.get("permissions", [])
    }
    access_token = create_access_token(purpose, data, settings.LOGIN_ACCESS_TOKEN_EXPIRY)
    # Store token in Redis with 24-hour TTL
    await redis_client.setex(f"{user_data['id']}_{purpose}", settings.LOGIN_ACCESS_TOKEN_EXPIRY, access_token)
    return access_token


async def logout_user_from_all_devices(user_id: str, redis_client: redis.Redis) -> bool:
    """
    Remove user all tokens from redis
    """
    keys = await redis_client.keys(f"{user_id}_*")
    for key in keys:
        await redis_client.delete(key)
    return True


async def create_forgot_password_token(user_data: dict, redis_client: redis.Redis) -> str:
    """
    Creates a JWT forgot password token and stores it in Redis.
    """
    purpose = "forgot_pwd"
    access_token = create_access_token(purpose, user_data, settings.FORGOT_PASSWORD_EXPIRY)
    await redis_client.setex(f"{user_data['id']}_{purpose}", settings.FORGOT_PASSWORD_EXPIRY, access_token)
    return access_token

async def jwt_decoder_get_payload(token: str, type_: str, redis_client: redis.Redis):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        stored_token = await redis_client.get(f"{payload['id']}_{type_}")
        if stored_token == token:
            return payload
    except PyJWTError as e:
        print(f"PyJWTError {e}")
    except Exception as e:
        print(f"Exception toke {e} {token}")
    raise InvalidCredentialsException("Could not validate credentials")


async def get_current_user_from_header_token(
    # token: str = Depends(oauth2_scheme),
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    redis_client: redis.Redis = Depends(get_redis_client),
    type_: str = Depends(lambda: 'login') 
    ) -> dict:
    """
    Dependency to get the current user from a JWT token.
    Validates the token using PyJWT and checks if it exists in Redis.
    """
    token = credentials.credentials
    return await jwt_decoder_get_payload(token, type_, redis_client)

async def invalidate_token(token: str, redis_client: redis.Redis) -> bool:
    """
    Invalidates a JWT token by removing it from Redis.
    """
    try:
        # Decode to get user ID
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        # Remove the token from Redis
        stored_token = await redis_client.get(f"{payload['id']}_{payload['sub']}")
        if stored_token == token:
            await redis_client.delete(f"{payload['id']}_{payload['sub']}")
        return True
    except PyJWTError as e:
        print(f"PyJWTError--> as {e}")
    except Exception as e:
        print(f"Exception toke {e} {token}")
    return False  # Token is already invalid or malformed

