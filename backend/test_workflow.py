import asyncio

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.models import Workflow


async def main():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Workflow))
        workflows = result.scalars().all()

        print([
            (str(workflow.id), workflow.name)
            for workflow in workflows
        ])


if __name__ == "__main__":
    asyncio.run(main())