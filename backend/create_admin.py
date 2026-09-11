import asyncio

from sqlalchemy import select

from app.core.database import AsyncSessionLocal, init_database
from app.core.security import hash_password
from app.models.models import User


ADMIN_EMAIL = "admin@aurixa.com"
ADMIN_PASSWORD = "Admin@123456"
ADMIN_NAME = "AURIXA Admin"

USER_EMAIL = "user@aurixa.com"
USER_PASSWORD = "User@123456"
USER_NAME = "AURIXA User"


async def create_users():
    # Ensure database tables exist
    await init_database()

    async with AsyncSessionLocal() as db:

        # ============================================================
        # CREATE ADMIN
        # ============================================================

        admin = await db.scalar(
            select(User).where(
                User.email == ADMIN_EMAIL
            )
        )

        if admin is None:
            admin = User(
                email=ADMIN_EMAIL,
                full_name=ADMIN_NAME,
                password_hash=hash_password(
                    ADMIN_PASSWORD
                ),
                status="active",
                is_admin=True,
            )

            db.add(admin)

            print(
                f"Admin created: {ADMIN_EMAIL}"
            )

        else:
            admin.full_name = ADMIN_NAME
            admin.password_hash = hash_password(
                ADMIN_PASSWORD
            )
            admin.status = "active"
            admin.is_admin = True

            print(
                f"Admin already exists. Updated: {ADMIN_EMAIL}"
            )

        # ============================================================
        # CREATE NORMAL USER
        # ============================================================

        user = await db.scalar(
            select(User).where(
                User.email == USER_EMAIL
            )
        )

        if user is None:
            user = User(
                email=USER_EMAIL,
                full_name=USER_NAME,
                password_hash=hash_password(
                    USER_PASSWORD
                ),
                status="active",
                is_admin=False,
            )

            db.add(user)

            print(
                f"User created: {USER_EMAIL}"
            )

        else:
            user.full_name = USER_NAME
            user.password_hash = hash_password(
                USER_PASSWORD
            )
            user.status = "active"
            user.is_admin = False

            print(
                f"User already exists. Updated: {USER_EMAIL}"
            )

        await db.commit()

        print("\n================================")
        print("AURIXA USERS READY")
        print("================================")
        print()
        print("ADMIN")
        print(f"Email: {ADMIN_EMAIL}")
        print(f"Password: {ADMIN_PASSWORD}")
        print()
        print("NORMAL USER")
        print(f"Email: {USER_EMAIL}")
        print(f"Password: {USER_PASSWORD}")
        print("================================")


if __name__ == "__main__":
    asyncio.run(create_users())