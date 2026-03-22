from typing import List, Optional
from uuid import UUID
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func

from src.database.models.posts import Post, PostStatus, PostType


class PostRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_post(
            self,
            author_id: int,
            title: str,
            subject: str,
            description: str,
            file_id: str | None = None,
            file_name: str | None = None,
            post_type: PostType = PostType.PUBLIC,
    ) -> Post:
        post = Post(
            author_id=author_id,
            executor_id=None,
            title=title,
            subject=subject,
            description=description,
            category=subject,
            budget=Decimal("0"),
            file_id=file_id,
            file_name=file_name,
            type=post_type,
            status=PostStatus.NEW,
            channel_message_id=None,
        )

        self.session.add(post)
        await self.session.commit()
        await self.session.refresh(post)
        return post

    async def get_post_by_id(self, post_id: UUID) -> Optional[Post]:
        stmt = select(Post).where(Post.id == post_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def count_posts(self) -> int:
        stmt = select(func.count(Post.id))
        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def get_posts_page(self, offset: int, limit: int) -> List[Post]:
        stmt = (
            select(Post)
            .order_by(Post.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_user_posts(self, user_id: int) -> List[Post]:
        stmt = (
            select(Post)
            .where(Post.author_id == user_id)
            .order_by(Post.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def take_in_work(self, post_id: UUID, executor_id: int) -> Optional[Post]:
        post = await self.get_post_by_id(post_id)
        if not post:
            return None

        if post.author_id == executor_id:
            return None

        if post.status != PostStatus.NEW:
            return None

        post.executor_id = executor_id
        post.status = PostStatus.IN_PROGRESS
        await self.session.commit()
        await self.session.refresh(post)
        return post

    async def mark_done(self, post_id: UUID) -> Optional[Post]:
        post = await self.get_post_by_id(post_id)
        if not post:
            return None

        post.status = PostStatus.DONE
        await self.session.commit()
        await self.session.refresh(post)
        return post

    async def mark_cancelled(self, post_id: UUID) -> Optional[Post]:
        post = await self.get_post_by_id(post_id)
        if not post:
            return None

        post.status = PostStatus.CANCELLED
        await self.session.commit()
        await self.session.refresh(post)
        return post