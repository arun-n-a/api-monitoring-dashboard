from typing import (
    List, Optional, Dict)
from uuid import UUID

from pydantic import (
    BaseModel, EmailStr, Field)

from .pagination import Pagination

class UserBase(BaseModel):
    """Base user schema with common fields."""
    first_name: str = Field(..., min_length=1, max_length=255, description="User's first name")
    last_name: str = Field(..., min_length=1, max_length=255, description="User's last name")
    role_id: int = Field(default=2, ge=1, description="User's role ID")
    department_id: int = Field(..., description="User's department ID")
    

class UserCreate(BaseModel):
    """Schema for creating a new user."""
    first_name: str = Field(..., min_length=1, max_length=255, description="User's first name")
    last_name: str = Field(..., min_length=1, max_length=255, description="User's last name")
    role_id: int = Field(default=2, ge=1, description="User's role ID")
    department_id: int = Field(..., description="User's department ID")
    email: EmailStr = Field(..., description="User's email address")
    permissions: List[int] = Field(default_factory=lambda: [], description="User's permissions")


class UserRegistration(BaseModel):
    """Schema for registration user information."""
    first_name: str = Field(..., min_length=1, max_length=255, description="User's first name")
    last_name: str = Field(..., min_length=1, max_length=255, description="User's last name")
    department_id: int = Field(..., ge=1, description="User's department ID")
    token: str = Field(..., description="User Registration token")
    password: str = Field(..., description="User's password")


class UserUpdate(UserBase):
    """Schema for updating user information."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=255, description="User's first name")
    last_name: Optional[str] = Field(None, min_length=1, max_length=255, description="User's last name")
    department_id: Optional[int] = Field(None, ge=1, description="User's department ID")
    # email: Optional[EmailStr] = Field(None, description="User's email address")
    role_id: Optional[int] = Field(None, ge=1, description="User's role ID")
    permissions: Optional[List[str]] = Field(None, description="User's permissions")
    is_active: Optional[bool] = Field(None, description="Whether the user is active")


class UserRetrieval(UserCreate):
    """Schema for user response."""
    id: UUID = Field(..., description="User's unique identifier")
    department_name: str = Field(..., description="The department name")


class SingleUserResponse(UserRetrieval):
    """Schema for user response."""
    registered_at: Optional[str] = Field(None, description="When the user registered")
    invited_at: Optional[str] = Field(None, description="When the user was invited")
    # invited_by: Optional[str] = Field(None, description="ID of user who invited this user")
    created_at: str = Field(..., description="When the user was created")
    updated_at: str = Field(..., description="When the user was last modified")
    is_active: bool = Field(..., description="User active status")

class SingleUserWrapResponse(BaseModel):
    data: SingleUserResponse = Field(..., description="User details are accessable here")
    
    class Config:
        from_attributes = True


class PaginatedUserResponse(BaseModel):
    data: List[SingleUserResponse] = Field(..., description="User's details are accessable here")
    pagination: Pagination = Field(..., description="Pagination details")
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")

    # class Config:
    #     from_attributes = True


class UserLoginResponse(BaseModel):
    """Schema for user login response."""
    access_token: str = Field(..., description="JWT access token")
    data: UserRetrieval = Field(..., description="User information")


class UserPasswordReset(BaseModel):
    """Schema for password reset request."""
    email: EmailStr = Field(..., description="User's email address")


class UserPasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation."""
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New password")


class UserDashboard(BaseModel):
    unregistered_users: int = Field(..., description="Total unregistered users")
    active_admin_users: int = Field(..., description="Total active admin users")
    total_users: int = Field(..., description="Total active and inactive users")
    active_users: int = Field(..., description="Total active users")


class UserDashboardWrapResponse(BaseModel):
    data: UserDashboard = Field(..., description="User count information")