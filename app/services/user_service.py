from datetime import datetime
from typing import (Optional)

import redis
from sqlalchemy import (
    or_, select, update, func, exists, and_, case)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    BadRequestException,
    NotFoundException
    )
from app.core.security import (
    get_password_hash, verify_password, 
    create_access_token)
from app.db.models import Users
from app.schemas.user import (UserCreate)
from app.core.config import settings
from app.core.templates import templates
from app.services.email_send import BrevoEmailSending 
from app.utils.datetime_utils import response_data_date_conversion
class UserService:
    """Service class for user-related database operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_user(self, data: UserCreate, redis_client: redis.Redis) -> bool:
        """Create a new user."""
        # hashed_password = get_password_hash(data.password)
        user = Users(
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            # hashed_password=hashed_password,
            role_id=data.role_id,
            # invited_by=invited_by,
            invited_at=datetime.utcnow()
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        access_token = create_access_token("invitation", {"id": str(user.id), "email": data.email}, settings.INVITATION_TOKEN_EXPIRY)
        await redis_client.setex(f"{user.id}_invitation", settings.INVITATION_TOKEN_EXPIRY, access_token)    
        html_content = templates.get_template("user_invitation.html").render({
            "first_name": data.first_name,
            "registration_url": f"{settings.FRONT_END_REGISTRATION_URL}/{access_token}?first_name={data.first_name}&last_name={data.last_name}"
            })
        
        await BrevoEmailSending(
            to_emails=[user.email], 
            subject="API Monitoring Application Invitation",
            html_content= html_content).send_email()
        return True
    
    async def get_user_by_id(self, user_id: str) -> Users:
        """Get user by ID."""
        result = await self.db.execute(
            select(
                Users.id, Users.first_name, Users.last_name, 
                Users.role_id, 
                Users.registered_at, Users.updated_at, Users.created_at,
                Users.email, Users.is_active
                ).where(Users.id == user_id)
            )
        return result.first()
    
    async def user_email_exist_or_not(self, email: str) -> bool:
        """Get user by email."""
        stmt = select(exists().where(Users.email == email))
        result = await self.db.execute(stmt)
        return result.scalar()

    async def get_user_by_email(self, email: str) -> Optional[Users]:
        """Get user by email."""
        result = await self.db.execute(
            select(Users).where(Users.email == email)
            )
        return result.scalar_one_or_none()

    async def get_users(
        self, 
        timezone: str,
        page: int, 
        per_page: int,
        is_active: bool | None,
        name_email_search: str | None
    ) -> dict:
        """Get list of users with optional filters."""
        offset = (page - 1) * per_page
        query = select(
            Users.id, Users.first_name, Users.last_name, Users.role_id,
            Users.is_active, Users.registered_at, Users.email,
            Users.created_at, Users.invited_at, Users.updated_at
            )
        if is_active is not None:
            query = query.where(Users.is_active == is_active)
        if name_email_search:
            if "@" not in name_email_search:
                query = query.where(
                    or_(
                        Users.first_name.ilike(f"%{name_email_search.strip()}%"),
                        Users.last_name.ilike(f"%{name_email_search.strip()}%")
                    )
                )
            else:
                query = query.where(Users.email == name_email_search.lower().strip())
        if page == 1:
            total_count_query = select(func.count()).select_from(Users)
            if is_active is not None:
                total_count_query = total_count_query.where(Users.is_active == is_active)
            if name_email_search:
                if "@" not in name_email_search:
                    total_count_query = total_count_query.where(
                        or_(
                        Users.first_name.ilike(f"%{name_email_search.strip()}%"),
                        Users.last_name.ilike(f"%{name_email_search.strip()}%")
                        )
                    )
                else:
                    total_count_query = total_count_query.where(Users.email == name_email_search.lower().strip())
                    total_count_query = await self.db.execute(total_count_query)
            total_count_result = await self.db.execute(total_count_query)
            total_count_result = total_count_result.scalar_one()
        else:
            total_count_result = 0
        query = query.order_by(Users.updated_at.desc()).offset(offset).limit(per_page)
        result = (await self.db.execute(query)).all()
        if not result:
            raise NotFoundException()
        users = [response_data_date_conversion(user._asdict(), ['created_at', 'invited_at', 'registered_at', 'updated_at'], timezone) for user in result]
        return {
            "data": users,
            "pagination": {
                "current_page": page,
                "per_page": per_page,
                "length": len(users),
                "total": total_count_result
            }
        }
        
    async def register_user(self, user_id: str, password: str, user_data: dict) -> bool:
        """User registration information."""
        if user_data:
            await self.db.execute(
                update(Users)
                .where(Users.id == user_id)
                .values(**user_data, updated_at=datetime.utcnow(), registered_at=datetime.utcnow(), hashed_password=get_password_hash(password))
            )
            await self.db.commit()        
        return True
    
    async def update_user(self, user_id: str, user_data: dict) -> bool:
        """Update user information."""
        # update_data = user_data.dict(exclude_unset=True)
        user_data = user_data.dict(exclude_unset=True)
        if user_data:
            await self.db.execute(
                update(Users)
                .where(Users.id == user_id)
                .values(**user_data, updated_at=datetime.utcnow())
            )
            await self.db.commit()        
        return True

    async def authenticate_user(self, email: str, password: str) -> Users:
        """Authenticate user with email and password."""
        user = await self.get_user_by_email(email)
        if not user or not user.is_active or user.is_deleted or not user.registered_at:
            raise BadRequestException("Incorrect username or password")
        if not verify_password(password, user.hashed_password):
            raise BadRequestException("Incorrect username or password")
        return user
    
    async def reset_password(self, email_address: str, new_password: str) -> bool:
        """Reset user password (for forgot password flow)."""
        user = await self.get_user_by_email(email_address)
        print(user)
        if not user:
            return False
        if user.is_active:
            user.hashed_password = get_password_hash(new_password)
            await self.db.commit()
        return True
    
    async def get_user_counts(self) -> dict:
        query = await self.db.execute(
            select(
                func.count(Users.id).label('total_users'),
                func.sum(
                    case((Users.is_active.is_(True), 1), else_=0)
                ).label('active_users'),
                func.sum(
                    case((and_(Users.is_active.is_(True), Users.role_id == 1), 1), else_=0)
                ).label('active_admin_users'),
                func.sum(
                    case((Users.registered_at.is_(None), 1), else_=0)
                ).label('unregistered_users')
            ).where(
                Users.is_deleted.is_(False)
            )
        )
        result = query.one()
        return result._asdict()
