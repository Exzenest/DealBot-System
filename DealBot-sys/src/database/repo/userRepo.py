from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from src.database.models.users import User

class UserRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create_user(self, telegram_id: int, phone: str, username: str,fullname:str, role: str = "user"):


        stmt = insert(User).values(
            telegram_id=telegram_id,
            username=username,
            phone=phone,
            role=role,
            full_name=fullname,
            balance=0.0,
            rating=0.0
        ).on_conflict_do_update(
            index_elements=[User.telegram_id],
            set_=dict(username=username)
        ).returning(User)

        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()

    async def get_by_id(self, telegram_id: int):
        stmt = select(User).where(User.telegram_id == telegram_id)
        user = await self.session.execute(stmt)
        return  user.scalar_one_or_none()

