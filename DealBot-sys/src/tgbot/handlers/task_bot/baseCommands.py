from aiogram import Dispatcher, Bot, Router
from src.database.config import config
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from src.database.config import config
from src.database.repo.userRepo import UserRepo
from src.tgbot.middlewares.session import DataBaseSession
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import F
from src.database.repo.postRepo import PostRepo, PostStatus
from aiogram.fsm.context import FSMContext
from src.tgbot.states.post_create import Post_state
from src.database.models.posts import PostType
from aiogram.filters import StateFilter



def contact_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="📞 Надіслати мій номер",
                    request_contact=True
                )
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="🔁Профіль",

                ),
                KeyboardButton(
                    text="📝Завдання"
                ),
                KeyboardButton(
                    text="📄Нове Завдання"
                )
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )



botConfig = config.load_bot()
bot = Bot(token=botConfig.token_task.get_secret_value())

router = Router()
router.message.middleware(DataBaseSession())

@router.message(CommandStart())
async def start(message:Message, session: AsyncSession):
    if await UserRepo(session).get_by_id(telegram_id=message.chat.id) == None:
        await bot.send_message(message.chat.id, "Ви ще не зареєстровані, для того щоб продовжити подилиться номером",reply_markup=contact_keyboard())
    else:
        await bot.send_message(message.chat.id,"Привіт! Це бот для перегляду і пошуку завдань!",reply_markup=menu_keyboard())


@router.message(lambda m: m.contact is not None)
async def handle_contact(message: Message,session: AsyncSession):
    phone = message.contact.phone_number

    await UserRepo(session).get_or_create_user(phone=phone,telegram_id=message.chat.id,username=message.from_user.username,fullname=message.from_user.username)

    await message.answer(
        f"✅ успішно зареєстровано!",
        reply_markup=None
    )

@router.message(F.text =="🔁Профіль")
async def handle_profile(message: Message, session: AsyncSession):
     user = await UserRepo(session).get_by_id(message.chat.id)
     await message.answer(f"ID - {user.telegram_id}\n"
                          f"username - {user.username}\n"
                          f"fullname - {user.full_name}\n"
                          f"phone - <tg-spoiler>{user.phone}</tg-spoiler>\n"
                          f"role - {user.role}\n"
                          f"balance - {user.balance}\n"
                          f"rating - {user.rating}",parse_mode="HTML")

@router.message(F.text == "📝Завдання")
async def task_handle(message: Message,session: AsyncSession):
    posts = []
    posts = await PostRepo(session).get_user_posts(message.chat.id)

    if posts == []:
        await message.answer("🛑  Немає завдань")
        return

    for post in posts:
        await message.answer(f"📢 {post.title}\n"
                             f"ℹ️{post.description}\n"
                             f"${post.budget}")
@router.message(F.text == "📄Нове Завдання")
async def task_create(message:Message,session: AsyncSession, state:FSMContext):
    await message.answer("ℹ️ Введіть назву")
    await state.set_state(Post_state.title)

@router.message(StateFilter(Post_state.title))
async def task_description(message:Message,session: AsyncSession,state:FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(Post_state.description)
    await message.answer("ℹ️ Опишіть ваше завдання")

@router.message(StateFilter(Post_state.description))
async def task_budget(message:Message,session: AsyncSession,state:FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(Post_state.budget)
    await message.answer("ℹ️ Уведить ваш бюджет")

@router.message(StateFilter(Post_state.budget))
async def task_category(message:Message,session: AsyncSession,state:FSMContext):
    await state.update_data(budget=message.text)
    await state.set_state(Post_state.category)
    await message.answer("ℹ️ Уведить категорію")

@router.message(StateFilter(Post_state.category))
async def task_confirm(message:Message,session: AsyncSession,state:FSMContext):
    await state.update_data(category=message.text)
    data = await state.get_data()
    await PostRepo(session).create_post(message.chat.id,data.get("title"),data.get("description"),data.get("budget"),data.get("category"),PostType.PUBLIC)
    await state.clear()
    await message.answer("✅ Успішно Додано!")




