import sqlalchemy as sa

from database.models.base import TimedBaseModel


class Lecture(TimedBaseModel):
    lecture_id = sa.Column(sa.BIGINT, primary_key=True, autoincrement=True)
    group_id = sa.Column(sa.VARCHAR(100), sa.ForeignKey('groups.group_id', ondelete='SET NULL'), nullable=False)
    name = sa.Column(sa.VARCHAR(500), nullable=False)
    tag = sa.Column(sa.VARCHAR(10), nullable=False)
    url = sa.Column(sa.VARCHAR(1000), nullable=True)
