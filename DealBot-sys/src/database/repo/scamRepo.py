from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from src.database.models.scam_list import Scammer
from sqlalchemy.dialects.postgresql import insert


class ScamRepo:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def get_by_id(self, id: int):
        stmt = select(Scammer).where(Scammer.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


    async def get_all_by_admin(self, telegram_id: int):
        stmt = select(Scammer).where(Scammer.added_by_admin_id == telegram_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()


    async def upsert_scammer(self, user_id: str, admin_id: int, reason: str):
        stmt = (
            insert(Scammer)
            .values(
                user_id=user_id,
                added_by_admin_id=admin_id,
                reason=reason,
                created_at=func.now()
            )
            .on_conflict_do_update(
                index_elements=[Scammer.user_id],
                set_={
                    "reason": reason,
                    "updated_at": func.now()
                }
            )
            .returning(Scammer)
        )

        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()


    async def delete(self, id: int):
        stmt = delete(Scammer).where(Scammer.id == id)
        await self.session.execute(stmt)
        await self.session.commit()
        return True
