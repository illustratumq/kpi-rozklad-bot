from database.models import *
from database.services.db_ctx import BaseRepo


class UserRepo(BaseRepo[User]):
    model = User

    async def get_user(self, user_id: int) -> User:
        return await self.get_one(self.model.user_id == user_id)

    async def get_users_by_group(self, group_id: str) -> list[User]:
        return await self.get_all(self.model.group_id == group_id)

    async def get_using_groups(self) -> list[str]:
        return list(set(user.group_id for user in await self.get_all()))

    async def update_user(self, user_id: int, **kwargs) -> None:
        return await self.update(self.model.user_id == user_id, **kwargs)

    async def delete_user(self, user_id: int):
        await self.delete(self.model.user_id == user_id)


class GroupRepo(BaseRepo[Group]):
    model = Group

    async def get_group(self, group_id: str) -> Group:
        return await self.get_one(self.model.group_id == group_id)

    async def get_group_by_name(self, group_name: str) -> Group:
        return await self.get_one(self.model.name == group_name)

    async def get_group_by_chat(self, chat_id: int) -> Group:
        return await self.get_one(self.model.chat_id == chat_id)

    async def update_group(self, group_id: str, **kwargs) -> None:
        return await self.update(self.model.group_id == group_id, **kwargs)

    async def delete_group(self, group_id: str):
        await self.delete(self.model.group_id == group_id)


class LectureRepo(BaseRepo[Lecture]):
    model = Lecture

    async def get_lecture_by_id(self, lecture_id: int) -> Lecture:
        return await self.get_one(self.model.lecture_id == lecture_id)

    async def get_lectures_by_group(self, group_id: str) -> list[Lecture]:
        return await self.get_all(self.model.group_id == group_id)

    async def get_lecture(self, group_id: str, name: str, tag: str) -> Lecture:
        return await self.get_one(self.model.group_id == group_id, self.model.name == name, self.model.tag == tag)

    async def update_lecture(self, lecture_id: int, **kwargs) -> None:
        return await self.update(self.model.lecture_id == lecture_id, **kwargs)

    async def delete_lecture(self, lecture_id: str) -> None:
        await self.delete(self.model.group_id == lecture_id)


class NotifyRepo(BaseRepo[Notification]):
    model = Notification

    async def get_notify(self, notify_id: int) -> Notification:
        return await self.get_one(self.model.notify_id == notify_id)

    async def get_user_notify(self, lecture_id: int, user_id: int) -> Notification:
        return await self.get_one(self.model.user_id == user_id, self.model.lecture_id == lecture_id)

    async def get_notifies_by_lecture(self, lecture_id: int) -> list[Notification]:
        return await self.get_all(self.model.lecture_id == lecture_id)

    async def get_notify_by_user(self, user_id: int) -> list[Notification]:
        return await self.get_all(self.model.user_id == user_id)

    async def update_notify(self, notify_id: int, **kwargs) -> None:
        return await self.update(self.model.notify_id == notify_id, **kwargs)

    async def delete_notify(self, notify_id: int):
        await self.delete(self.model.notify_id == notify_id)