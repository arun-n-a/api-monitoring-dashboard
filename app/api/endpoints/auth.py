from fastapi import (
    APIRouter, Depends, Query, status
)

import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis_config import get_redis_client
from app.core.security import (
    create_forgot_password_token,
    create_login_token,
    get_current_user_from_header_token,
    logout_user_from_all_devices,
    jwt_decoder_get_payload
)
from app.db.session import get_db
from app.schemas.user import (
    UserLogin,
    UserLoginResponse,
    UserPasswordReset,
    UserPasswordResetConfirm,
    SingleUserWrapResponse,
)

from app.services.user_service import UserService
from app.services.email_send import BrevoEmailSending #SendgridEmailSending
from app.schemas.success_schema import SuccessMessage
from app.core.templates import templates 
from app.core.config import settings
from app.utils.datetime_utils import response_data_date_conversion

router = APIRouter()


@router.post(
    "/login",
    response_model=UserLoginResponse,
    summary="User Login",
    description="Authenticate user with email and password",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Login successful"},
        400: {"description": "Incorrect username or password"},
        422: {"description": "Validation error"}
    }
)
async def login(
    payload: UserLogin,
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client)
):
    """Login endpoint for user authentication."""
    user_service = UserService(db)
    user = await user_service.authenticate_user(
        payload.email, 
        payload.password
    )
    department_name = await user_service.get_department_name_by_id(user.department_id)
    user_data = {
        "id": str(user.id),
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "department_id": user.department_id,
        "role_id": user.role_id,
        "permissions": user.permissions,
        "department_name": department_name
    }
    access_token = await create_login_token(user_data, redis_client)
    return UserLoginResponse(
        access_token=access_token,
        data=user_data
        )


@router.post(
    "/logout",
    summary="User Logout",
    description="Logout user and invalidate token",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Logout successful"},
        401: {"description": "Invalid token"}
    }
)
async def logout(
    current_user: dict = Depends(get_current_user_from_header_token),
    redis_client: redis.Redis = Depends(get_redis_client)
):
    """Logout endpoint to invalidate user token."""
    await redis_client.delete(f"{current_user['id']}_login")       
    # The token will be invalidated by removing it from Redis
    # This is handled automatically by the token validation middleware
    return {"message": "Successfully logged out"}


@router.get(
    "/me",
    response_model=SingleUserWrapResponse,
    summary="Get Current User",
    description="Get current authenticated user information",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "User information retrieved successfully"},
        401: {"description": "Invalid token"}
    }
)
async def get_current_user(
    timezone:  str = Query(..., description="User's local time zone", example="Asia/Kolkata"),
    current_user: dict = Depends(get_current_user_from_header_token),
    db: AsyncSession = Depends(get_db)):
    """Get current user information."""
    user = await UserService(db).get_user_by_id(current_user["id"])
    print(f'****Arun {user}')
    result = response_data_date_conversion(user._asdict(), ['updated_at', 'registered_at', 'created_at'], timezone)
    return {"data": result}


@router.post(
    "/forgot-password",
    summary="Forgot Password",
    description="Request password reset token",
    status_code=status.HTTP_200_OK,
    response_model=SuccessMessage,
    responses={
        404: {"description": "User not found"},
        422: {"description": "Validation error"}
    }
)
async def forgot_password(
    payload: UserPasswordReset,
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client)
):
    """Request password reset token."""
    user = await UserService(db).get_user_by_email(payload.email)
    if not user or not user.is_active:
        return {"message": "If the email exists, a password reset link has been sent"}
    if not user.registered_at:
        return {"message": "Please complete your registration process first"}
    await logout_user_from_all_devices(user.id, redis_client)
    # Create forgot password token
    user_data = {
        "id": str(user.id),
        "email": user.email
    }
    token = await create_forgot_password_token(user_data, redis_client)
    html_content = templates.get_template("reset_password.html").render({
        "first_name": user.first_name,
        "reset_url": f"{settings.FRONT_END_PASSWORD_RESET_URL}/{token}"
        })
    
    # await SendgridEmailSending(
    #     to_emails=[user.email], 
    #     subject="Reset Password: DocuHuB Application",
    #     html_content= html_content).send_email()

    await BrevoEmailSending(
        to_emails=[user.email], 
        subject="Reset Password: DocuHuB Application",
        html_content= html_content).send_email()
    
    return {"message": "If the email exists, a password reset link has been sent"}


@router.post(
    "/reset-password",
    summary="Reset Password",
    description="Reset password using token",
    status_code=status.HTTP_200_OK,
    response_model=SuccessMessage,
    responses={
        400: {"description": "Invalid token"},
        422: {"description": "Validation error"}
    }
)
async def reset_password(
    payload: UserPasswordResetConfirm,
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client)
):
    """Reset password using token."""
    current_user = await jwt_decoder_get_payload(payload.token, "forgot_pwd", redis_client)
    await UserService(db).reset_password(
        current_user['email'], payload.new_password)
    await redis_client.delete(f"{current_user['id']}_forgot_pwd")      
    return {"message": "Password reset successful"}
