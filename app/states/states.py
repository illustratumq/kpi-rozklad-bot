from app.states.base import *


class AuthSG(StatesGroup):
    Inline = State()
    Group = State()


class GroupSG(StatesGroup):
    Group = State()


class LinkSG(StatesGroup):
    Input = State()


class MessageSG(StatesGroup):
    Text = State()
    Photo = State()
    ButtonText = State()
    ButtonUrl = State()
    Confirm = State()


class InfoSG(StatesGroup):
    Input = State()
