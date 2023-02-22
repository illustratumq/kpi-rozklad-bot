import sqlalchemy as sa

from database.models.base import TimedBaseModel


class Group(TimedBaseModel):
    group_id = sa.Column(sa.VARCHAR(100), primary_key=True)
    chat_id = sa.Column(sa.BIGINT, nullable=True)
    faculty = sa.Column(sa.VARCHAR(20), nullable=False)
    name = sa.Column(sa.VARCHAR(20), nullable=False)
    schedule = sa.Column(sa.JSON, nullable=False)
