from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from src.database.models.reviews import Review
from sqlalchemy import select, update, func
from typing import List, Optional


class ReviewRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_review(
        self,
        agreement_id: UUID,
        from_user_id: int,
        to_user_id: int,
        score: int,
        comment: str,
    ) -> Review:

        rev = Review(
            agreement_id=agreement_id,
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            score=score,
            comment=comment,
        )

        self.session.add(rev)
        await self.session.commit()
        await self.session.refresh(rev)
        return rev

    async def get_rev_by_id(self, rev_id: UUID) -> Optional[Review]:
        stmt = select(Review).where(Review.id == rev_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_revs(self, user_id: int) -> List[Review]:
        stmt = select(Review).where(Review.from_user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_revs_score(self, score: int) -> List[Review]:
        stmt = select(Review).where(Review.score == score)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_revs_agreements(self, agreet: int) -> List[Review]:
        stmt = select(Review).where(Review.agreement_id == agreet)
        result = await self.session.execute(stmt)
        return result.scalars().all()
