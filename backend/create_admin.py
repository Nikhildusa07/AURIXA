import asyncio

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.models import User


ADMIN_EMAIL = "admin@aurixa.com"
ADMIN_PASSWORD = "Admin@12345"
ADMIN_NAME = "AURIXA Administrator"


async def create_admin() -> None:
    async with AsyncSessionLocal() as db:

        existing_user = await db.scalar(
            select(User).where(
                User.email == ADMIN_EMAIL
            )
        )

        if existing_user:
            # Reset existing user's password and admin permissions
            existing_user.password_hash = hash_password(
                ADMIN_PASSWORD
            )
            existing_user.full_name = ADMIN_NAME
            existing_user.is_admin = True
            existing_user.status = "active"

            await db.commit()

            print(
                f"Admin updated successfully: "
                f"{ADMIN_EMAIL}"
            )
            print(
                f"Password reset successfully."
            )

            return

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
        await db.commit()

        print(
            f"Admin created successfully: "
            f"{ADMIN_EMAIL}"
        )


if __name__ == "__main__":
    asyncio.run(create_admin())