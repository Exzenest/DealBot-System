from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models.logs import Logs
from sqlalchemy.dialects.postgresql import insert


class LogRepo:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def get_by_id(self, id: int):
        stmt = select(Logs).where(Logs.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


    async def get_all_by_action(self, action: str):
        stmt = select(Logs).where(Logs.action == action)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create_log(
            self,
            actor_id: int,
            action: str,
            details: str,
            log_type: str = "public",
    ) -> Logs:
        log = Logs(
            actor_id=actor_id,
            action=action,
            details=details,
            type=log_type,

        )
        self.session.add(log)
        await self.session.commit()
        await self.session.refresh(log)
        return log



