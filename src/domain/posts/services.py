import uuid
from typing import List, Optional, Sequence

from sqlmodel import Session, select, desc, col, and_, or_
from sqlalchemy.orm import joinedload

from src.domain.models import Post, Likes, User
from src.interface.posts.schemas import PostSchema
from lib.fastapi.utils import db_session_value_create, get_after_date_from_enum
from lib.fastapi.custom_enums import FilterDates


class PostService:
    """post service for handling post database operations"""

    def __init__(self, session: Session):
        self.db_session = session

    def get_post_by_id(self, id: uuid.UUID) -> Optional[Post]:
        """get post by post id"""
        return self.db_session.get(Post, id)

    def get_all_posts_by_user_id(
        self,
        user_id: uuid.UUID,
        search: Optional[str] = None,
        filter_by: Optional[FilterDates] = None,
    ) -> Sequence[Post]:
        """get all posts posted by the user using user id all or filtered by created at or search query in caption from database"""
        base = select(Post).where(Post.posted_by == user_id)
        if search and filter_by:
            after_date = get_after_date_from_enum(value=filter_by)
            statement = base.filter(Post.caption.contains(search)).filter(
                Post.created_at >= after_date
            )
        elif search:
            statement = base.filter(Post.caption.contains(search))
        elif filter_by:
            after_date = get_after_date_from_enum(value=filter_by)
            # print(after_date)
            statement = base.filter(Post.created_at >= (after_date))
        else:
            statement = base
        posts = self.db_session.exec(statement.order_by(desc(Post.created_at))).all()
        return posts

    # def get_post_by_post_id_for_user(self, post_id:uuid.UUID, user_id:uuid.UUID) -> Optional[Post]:
    #     """get post by post id that is posted by the user from the database"""
    #     return self.db_session.scalars(select(Post).where(Post.posted_by == user_id).where(Post.id == post_id))

    def get_all_posts_not_liked_by_user(
        self, user: User, public_users: List[User]
    ) -> List[Post]:
        """get all posts from public users and from user following that aren't liked by user from the database"""
        following_ids = [f.following.id for f in user.following]
        # print(following_ids)
        public_user_ids = [public_user.id for public_user in public_users]
        recommend_from = following_ids + public_user_ids
        posts = (
            self.db_session.exec(
                select(Post)
                .join(Post.likes, isouter=True)
                .where(or_(Likes.liked_by != user.id, ~Post.likes.any()))
                # .filter(Likes.liked_by != user.id)
                .where(
                    and_(
                        Post.posted_by != user.id,
                        col(Post.posted_by).in_(recommend_from),
                    )
                )
            )
            .unique()
            .all()
        )
        return posts

    def create(self, post: PostSchema) -> Post:
        """create post in the database"""
        db_post = Post.model_validate(post)
        db_session_value_create(session=self.db_session, value=db_post)
        return db_post

    def update(self, post: PostSchema, db_post: Post) -> Post:
        """update post in the database"""
        db_post.sqlmodel_update(post)
        db_session_value_create(session=self.db_session, value=db_post)
        return db_post

    def delete(self, db_post: Post) -> None:
        """delete post from the database"""
        self.db_session.delete(db_post)
        self.db_session.commit()
