from typing import List, Optional
from uuid import UUID
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func

from src.database.models.posts import Post, PostStatus


class PostRepo:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def create_post(
        self,
        author_id: int,
        title: str,
        description: str,
        budget: Decimal,
        category: str,
        post_type: str = "public"
    ) -> Post:

        post = Post(
            author_id=author_id,
            title=title,
            description=description,
            budget=budget,
            category=category,
            type=post_type,
            status=PostStatus.MODERATION,
        )

        self.session.add(post)
        await self.session.commit()
        await self.session.refresh(post)
        return post


    async def get_post_by_id(self, post_id: UUID) -> Optional[Post]:
        stmt = select(Post).where(Post.id == post_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


    async def get_public_feed(self) -> List[Post]:
        stmt = select(Post).where(Post.status == PostStatus.PUBLISHED)
        result = await self.session.execute(stmt)
        return result.scalars().all()


    async def get_user_posts(self, user_id: int) -> List[Post]:
        stmt = select(Post).where(Post.author_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    #
    async def set_channel_message_id(self, post_id: UUID, message_id: int) -> bool:
        stmt = (
            update(Post)
            .where(Post.id == post_id)
            .values(channel_message_id=message_id)
        )

        await self.session.execute(stmt)
        await self.session.commit()
        return True


    async def assign_executor(self, post_id: UUID, executor_id: int) -> Optional[Post]:
        stmt = (
            update(Post)
            .where(
                Post.id == post_id,
                Post.status == PostStatus.PUBLISHED,
                Post.executor_id.is_(None)
            )
            .values(
                executor_id=executor_id,
                status=PostStatus.WORKING,
                updated_at=func.now()
            )
            .returning(Post)
        )

        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()


    async def update_status(self, post_id: UUID, new_status: PostStatus) -> Optional[Post]:
        stmt = (
            update(Post)
            .where(Post.id == post_id)
            .values(
                status=new_status,
                updated_at=func.now()
            )
            .returning(Post)
        )

        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()


    async def delete_post(self, post_id: UUID) -> bool:
        stmt = (
            update(Post)
            .where(
                Post.id == post_id,
                Post.status != PostStatus.ARCHIVED
            )
            .values(
                status=PostStatus.ARCHIVED,
                updated_at=func.now()
            )
        )

        await self.session.execute(stmt)
        await self.session.commit()
        return True