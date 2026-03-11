from aiogram.fsm.state import State, StatesGroup


class Post_state(StatesGroup):
    author_id=State()
    title = State
    description = State()
    budget = State()
    category = State()
    post_type: State()

