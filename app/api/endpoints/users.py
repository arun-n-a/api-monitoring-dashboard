import redis.asyncio as redis

from fastapi import (
    APIRouter, Body, Depends, Path, Query, status,
    )
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    AlreadyExistsException,
    UnauthorizedException,
)
from app.core.security import (
    jwt_decoder_get_payload
    )
from app.db.session import get_db
from app.schemas import (
    SuccessMessage,
    UserCreate,
    UserUpdate,
    SingleUserWrapResponse,
    PaginatedUserResponse,
    UserUpdate,
    UserRegistration,
    UserDashboardWrapResponse
)
from app.core.redis_config import get_redis_client
from app.core.permissions import (
    admin_required,
    is_self_user_or_admin
)
from app.services.user_service import UserService
from app.utils.datetime_utils import response_data_date_conversion
router = APIRouter()


@router.post(
    "/invite",
    summary="Create User",
    description="Create a new user",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessMessage,  # Changed from response_class to response_model
    responses={
        400: {"description": "Bad request"},
        409: {"description": "User already exists"},
        422: {"description": "Validation error"}
    }
)
async def create_user(
    payload: UserCreate,
    current_user: dict = Depends(admin_required),
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client)
):
    """Create a new user."""
    user_service = UserService(db)
    # Check if user already exists
    payload.email = payload.email.lower()
    existing_user = await user_service.user_email_exist_or_not(payload.email)
    if existing_user:
        raise AlreadyExistsException("User with this email already exists")
    await user_service.create_user(payload, redis_client)
    return {"message": "Successfully invited new user"}


@router.post("/register/",
    summary="User Registration",
    description="From the invitation email Registration has to be completed",
    status_code=status.HTTP_200_OK,
    response_model=SuccessMessage,
    responses={
        400: {"description": "Bad request"},
        401: {"description": "Invalid token"},
        404: {"description": "User not found"},
        422: {"description": "Validation error"}
    }
)
async def user_register(
    payload: UserRegistration = Body(...),
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client)
    ):
    """Update user information via registration."""
    current_user = await jwt_decoder_get_payload(payload.token, "invitation", redis_client)    
    payload = payload.dict(exclude={"token"})
    await UserService(db).register_user(current_user['id'], payload.pop('password'), payload)
    # await redis_client.delete(f"{current_user['id']}_invitation")
    return {"message": "Successfully completed registration process"} 

@router.get(
    "/",
    response_model=PaginatedUserResponse,
    summary="Get Users",
    description="Get list of users with optional filtering",
    status_code=status.HTTP_200_OK,
    responses={
        401: {"description": "Please login and try again"},
        404: {"description": "No data found"}
        }
    )
async def get_users(
    timezone:  str = Query(..., description="User's local time zone", example="Asia/Kolkata"),
    page: int = Query(1, ge=1, description="Paginated page number"),
    per_page: int = Query(10, ge=1, le=1000, description="Number of records to return per request"),
    is_active: bool = Query(None, description="Filter by active status"),
    name_email_search: str = Query(None, description="Filter by name match or email address"),
    current_user: dict = Depends(admin_required),
    db: AsyncSession = Depends(get_db)
    ):
    """Get list of users with optional filtering."""
    user_service = UserService(db)
    result = await user_service.get_users(
        timezone,
        page=page,
        per_page=per_page,
        is_active=is_active,
        name_email_search=name_email_search
    )
    return result

@router.get(
    "/{user_id}",
    response_model=SingleUserWrapResponse,
    summary="Get User",
    description="Get user by ID",
    status_code=status.HTTP_200_OK,
    responses={
        401: {"description": "Invalid token"},
        404: {"description": "User not found"}
    }
)
async def get_single_user(
    user_id: str,
    timezone:  str = Query(..., description="User's local time zone", example="Asia/Kolkata"),
    current_user: dict = Depends(is_self_user_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get user by ID."""
    user = await UserService(db).get_user_by_id(user_id)
    data = response_data_date_conversion(user._asdict(), ['created_at', 'updated_at', 'registered_at'], timezone)
    return {"data": data}


@router.put("/{user_id}",
    summary="Update User",
    description="Admin can edit any user's information and normal user can edit their own details",
    status_code=status.HTTP_200_OK,
    response_model=SuccessMessage,
    responses={
        400: {"description": "Bad request"},
        401: {"description": "Invalid token"},
        404: {"description": "User not found"},
        422: {"description": "Validation error"}
    }
)
async def update_user(
    user_id: str = Path(...),
    payload: UserUpdate = Body(...),
    current_user: dict = Depends(is_self_user_or_admin),
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client)
    ):
    """Update user information."""
    if current_user['role_id'] != 1 and set(payload.dict().keys()) - {'first_name', 'last_name', 'department_id'}:
        raise UnauthorizedException()
    if payload.role_id or payload.permissions:
        await redis_client.delete(f"{user_id}_login")
    await UserService(db).update_user(user_id, payload)
    return {"message": "Successfully updated the details"} 


@router.get("/dashboard/",
    summary="Get user counts in user page",
    description="In user page get the count of active admins, total users, active user, unregistred users",
    status_code=status.HTTP_200_OK,
    response_model=UserDashboardWrapResponse
    )
async def user_dashboard_data(
    current_user: dict = Depends(admin_required),
    db: AsyncSession = Depends(get_db),
    ):
    result = await UserService(db).get_user_counts()
    return {"data": result} 



