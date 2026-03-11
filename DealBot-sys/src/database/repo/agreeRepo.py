from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from src.database.models.agreements import Agreement
from sqlalchemy import select, update, func
from typing import List, Optional


class AgreeRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_agree(
        self,
        post_id: UUID,
        customer_id: int,
        performer_id: int,


    ) -> Agreement:

        rev = Agreement(
            post_id=post_id,
            customer_id=customer_id,
            performer_id=performer_id,

        )

        self.session.add(rev)
        await self.session.commit()
        await self.session.refresh(rev)
        return rev

    async def get_agree_by_id(self, rev_id: UUID) -> Optional[Agreement]:
        stmt = select(Agreement).where(Agreement.id == rev_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_customer_agree(self, user_id: int) -> List[Agreement]:
        stmt = select(Agreement).where(Agreement.customer_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_performer_agree(self, user_id: int) -> List[Agreement]:
        stmt = select(Agreement).where(Agreement.performer_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    
