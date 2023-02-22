import sqlalchemy as sa

from database.models.base import TimedBaseModel


class Notification(TimedBaseModel):
    notify_id = sa.Column(sa.BIGINT, primary_key=True, autoincrement=True)
    group_id = sa.Column(sa.VARCHAR(100), sa.ForeignKey('groups.group_id', ondelete='SET NULL'), nullable=False)
    lecture_id = sa.Column(sa.BIGINT, sa.ForeignKey('lectures.lecture_id', ondelete='SET NULL'), nullable=False)
    user_id = sa.Column(sa.BIGINT, sa.ForeignKey('users.user_id', ondelete='SET NULL'), nullable=False)
    notification = sa.Column(sa.BOOLEAN, nullable=False, default=False)
