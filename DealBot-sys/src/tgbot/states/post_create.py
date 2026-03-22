from aiogram.fsm.state import State, StatesGroup


class Post_state(StatesGroup):
    title = State()
    subject = State()
    description = State()
    file = State()