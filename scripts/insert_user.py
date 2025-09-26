# import sys
# from datetime import datetime
# from pathlib import Path

# # Add the project root to sys.path
# ROOT_DIR = Path(__file__).resolve().parent.parent
# sys.path.append(str(ROOT_DIR))

# import asyncio
# from uuid import UUID

# from sqlalchemy import select
# from app.db.base import Base 
# from app.db.models.user import Users
# from app.core.security import get_password_hash
# from app.db.session import (
#     AsyncSessionLocal, engine)


# async def prepare_database():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)

# async def insert_user():
#     await prepare_database()

#     async with AsyncSessionLocal() as session:
#         async with session.begin():
#             # Get a real user ID to link with department
#             # result = await session.execute(
#             #     select(Users).where(Users.email == "arun_n_a@abacies.in")
#             # )
#             # existing_admin = result.scalar_one_or_none()
#             # if existing_admin:
#             #     print(f"existing_admin {existing_admin}")
#             #     # If the user exists, mark it for deletion
#             #     session.delete(existing_admin)
#             #     # Commit the transaction to apply the deletion to the database
#             #     await session.commit()
#             # return True
#             user_obj = Users(
#                 first_name="Arun",
#                 last_name="N A",
#                 email="arun_n_a@abacies.in",
#                 role_id=1,
#                 department_id=1,
#                 is_deleted=False,
#                 invited_at=datetime.utcnow(),
#                 registered_at=datetime.utcnow(),
#                 hashed_password=get_password_hash('Abacies@123'), # default password
#             )
#             session.add(user_obj)
#         await session.commit()
#         print("✅ Inserted default user")

# if __name__ == "__main__":
#     asyncio.run(insert_user())