import sqlalchemy as sa

from database.models.base import TimedBaseModel


class User(TimedBaseModel):
    user_id = sa.Column(sa.BIGINT, primary_key=True, autoincrement=False, index=True, nullable=True)
    group_id = sa.Column(sa.VARCHAR(100), sa.ForeignKey('groups.group_id', ondelete='SET NULL'), nullable=True)
    full_name = sa.Column(sa.VARCHAR(300), nullable=False)
    mention = sa.Column(sa.VARCHAR(350), nullable=True)
    notification = sa.Column(sa.BOOLEAN, nullable=False, default=True)
    mark = sa.Column(sa.BOOLEAN, nullable=False, default=True)