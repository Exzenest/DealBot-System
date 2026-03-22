from math import ceil
from uuid import UUID

from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter, CommandObject
from aiogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
    CallbackQuery,
)
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.config import config
from src.database.repo.userRepo import UserRepo
from src.database.repo.postRepo import PostRepo
from src.database.models.posts import PostStatus, PostType
from src.tgbot.middlewares.session import DataBaseSession
from src.tgbot.states.post_create import Post_state
from aiogram import Bot


TASKS_PER_PAGE = 5

STATUS_EMOJI = {
    PostStatus.NEW: "🔵",
    PostStatus.IN_PROGRESS: "🟡",
    PostStatus.CANCELLED: "🔴",
    PostStatus.DONE: "🟢",
}


def contact_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="Надіслати мій номер",
                    request_contact=True,
                )
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Профіль"),
                KeyboardButton(text="Завдання"),
                KeyboardButton(text="Нове Завдання"),
            ]
        ],
        resize_keyboard=True,
    )


def tasks_pagination_keyboard(posts, page: int, total_pages: int):
    buttons = []

    for post in posts:
        emoji = STATUS_EMOJI.get(post.status, "⚪")
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{emoji} {post.title}",
                    callback_data=f"task_view:{post.id}",
                )
            ]
        )

    nav_row = []
    if page > 1:
        nav_row.append(
            InlineKeyboardButton(
                text="⬅️",
                callback_data=f"tasks_page:{page - 1}",
            )
        )

    nav_row.append(
        InlineKeyboardButton(
            text=f"{page} / {total_pages}",
            callback_data="noop",
        )
    )

    if page < total_pages:
        nav_row.append(
            InlineKeyboardButton(
                text="➡️",
                callback_data=f"tasks_page:{page + 1}",
            )
        )

    buttons.append(nav_row)

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def task_actions_keyboard(post, current_user_id: int):
    buttons = []

    if post.author_id != current_user_id:
        if post.status == PostStatus.NEW:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text="Взяти в роботу",
                        callback_data=f"task_take:{post.id}",
                    )
                ]
            )
        elif post.status == PostStatus.IN_PROGRESS and post.executor_id == current_user_id:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text="Виконано",
                        callback_data=f"task_done:{post.id}",
                    )
                ]
            )

    if post.author_id == current_user_id:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Відмінити",
                    callback_data=f"task_cancel:{post.id}",
                ),
                InlineKeyboardButton(
                    text="Переписка",
                    callback_data=f"task_chat:{post.id}",
                ),
            ]
        )
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Виконано",
                    callback_data=f"task_done:{post.id}",
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                text="⬅️ Назад до списку",
                callback_data="tasks_page:1",
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def render_post_text(post) -> str:
    emoji = STATUS_EMOJI.get(post.status, "⚪")
    executor = "не призначено"

    if post.executor:
        executor = post.executor.full_name or post.executor.username or str(post.executor.telegram_id)
    elif post.executor_id:
        executor = str(post.executor_id)

    file_info = post.file_name if post.file_name else "немає"

    return (
        f"{emoji} <b>Статус:</b> {post.status.value}\n"
        f"<b>ID:</b> <code>{post.id}</code>\n"
        f"<b>Назва:</b> {post.title}\n"
        f"<b>Предмет:</b> {post.subject}\n"
        f"<b>Опис:</b> {post.description}\n"
        f"<b>Файл:</b> {file_info}\n"
        f"<b>Виконавець:</b> {executor}"
    )


botConfig = config.load_bot()
bot = Bot(token=botConfig.token_task.get_secret_value())
router = Router()
router.message.middleware(DataBaseSession())
router.callback_query.middleware(DataBaseSession())


@router.message(CommandStart(deep_link=True))
async def start_with_deeplink(
    message: Message,
    command: CommandObject,
    session: AsyncSession,
):
    args = command.args

    if not args or not args.startswith("task_"):
        user = await UserRepo(session).get_by_id(telegram_id=message.chat.id)
        if user is None:
            await bot.send_message(
                message.chat.id,
                "Ви ще не зареєстровані, для того щоб продовжити поділіться номером",
                reply_markup=contact_keyboard(),
            )
        else:
            await bot.send_message(
                message.chat.id,
                "Привіт! Це бот для перегляду і пошуку завдань!",
                reply_markup=menu_keyboard(),
            )
        return

    try:
        task_id = UUID(args.replace("task_", ""))
    except ValueError:
        await message.answer("Некоректне посилання на завдання.")
        return

    post = await PostRepo(session).get_post_by_id(task_id)
    if not post:
        await message.answer("Завдання не знайдено.")
        return

    await message.answer(
        render_post_text(post),
        parse_mode="HTML",
        reply_markup=task_actions_keyboard(post, message.from_user.id),
    )


@router.message(CommandStart())
async def start(message: Message, session: AsyncSession):
    if await UserRepo(session).get_by_id(telegram_id=message.chat.id) is None:
        await bot.send_message(
            message.chat.id,
            "Ви ще не зареєстровані, для того щоб продовжити поділіться номером",
            reply_markup=contact_keyboard(),
        )
    else:
        await bot.send_message(
            message.chat.id,
            "Привіт! Це бот для перегляду і пошуку завдань!",
            reply_markup=menu_keyboard(),
        )


@router.message(lambda m: m.contact is not None)
async def handle_contact(message: Message, session: AsyncSession):
    phone = message.contact.phone_number
    await UserRepo(session).get_or_create_user(
        phone=phone,
        telegram_id=message.chat.id,
        username=message.from_user.username,
        fullname=message.from_user.username,
    )
    await message.answer("✅ Успішно зареєстровано!", reply_markup=menu_keyboard())


@router.message(F.text == "Профіль")
async def handle_profile(message: Message, session: AsyncSession):
    user = await UserRepo(session).get_by_id(message.chat.id)
    await message.answer(
        f"ID - {user.telegram_id}\n"
        f"username - {user.username}\n"
        f"fullname - {user.full_name}\n"
        f"phone - {user.phone}\n"
        f"role - {user.role}\n"
        f"balance - {user.balance}\n"
        f"rating - {user.rating}",
        parse_mode="HTML",
    )


@router.message(F.text == "Завдання")
async def task_handle(message: Message, session: AsyncSession):
    page = 1
    offset = (page - 1) * TASKS_PER_PAGE

    total = await PostRepo(session).count_posts()
    posts = await PostRepo(session).get_posts_page(offset=offset, limit=TASKS_PER_PAGE)

    if not posts:
        await message.answer("Немає завдань.")
        return

    total_pages = max(1, ceil(total / TASKS_PER_PAGE))

    await message.answer(
        "📋 Список завдань:",
        reply_markup=tasks_pagination_keyboard(posts, page, total_pages),
    )


@router.callback_query(F.data.startswith("tasks_page:"))
async def tasks_page_callback(callback: CallbackQuery, session: AsyncSession):
    page = int(callback.data.split(":")[1])
    offset = (page - 1) * TASKS_PER_PAGE

    total = await PostRepo(session).count_posts()
    posts = await PostRepo(session).get_posts_page(offset=offset, limit=TASKS_PER_PAGE)

    total_pages = max(1, ceil(total / TASKS_PER_PAGE))

    if not posts:
        await callback.answer("Немає завдань.")
        return

    await callback.message.edit_text(
        "📋 Список завдань:",
        reply_markup=tasks_pagination_keyboard(posts, page, total_pages),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("task_view:"))
async def task_view_callback(callback: CallbackQuery, session: AsyncSession):
    task_id = callback.data.split(":")[1]

    try:
        post_id = UUID(task_id)
    except ValueError:
        await callback.answer("Некоректний ID", show_alert=True)
        return

    post = await PostRepo(session).get_post_by_id(post_id)
    if not post:
        await callback.answer("Завдання не знайдено", show_alert=True)
        return

    await callback.message.edit_text(
        render_post_text(post),
        parse_mode="HTML",
        reply_markup=task_actions_keyboard(post, callback.from_user.id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("task_take:"))
async def task_take_callback(callback: CallbackQuery, session: AsyncSession):
    task_id = callback.data.split(":")[1]

    try:
        post_id = UUID(task_id)
    except ValueError:
        await callback.answer("Некоректний ID", show_alert=True)
        return

    post = await PostRepo(session).take_in_work(post_id, callback.from_user.id)
    if not post:
        await callback.answer("Не вдалося взяти завдання в роботу", show_alert=True)
        return

    await callback.message.edit_text(
        render_post_text(post),
        parse_mode="HTML",
        reply_markup=task_actions_keyboard(post, callback.from_user.id),
    )
    await callback.answer("Завдання взято в роботу")


@router.callback_query(F.data.startswith("task_done:"))
async def task_done_callback(callback: CallbackQuery, session: AsyncSession):
    task_id = callback.data.split(":")[1]

    try:
        post_id = UUID(task_id)
    except ValueError:
        await callback.answer("Некоректний ID", show_alert=True)
        return

    post = await PostRepo(session).get_post_by_id(post_id)
    if not post:
        await callback.answer("Завдання не знайдено", show_alert=True)
        return

    # виконати може автор або призначений виконавець
    if callback.from_user.id not in [post.author_id, post.executor_id]:
        await callback.answer("У вас немає прав для цієї дії", show_alert=True)
        return

    post = await PostRepo(session).mark_done(post_id)

    await callback.message.edit_text(
        render_post_text(post),
        parse_mode="HTML",
        reply_markup=task_actions_keyboard(post, callback.from_user.id),
    )
    await callback.answer("Завдання виконано")


@router.callback_query(F.data.startswith("task_cancel:"))
async def task_cancel_callback(callback: CallbackQuery, session: AsyncSession):
    task_id = callback.data.split(":")[1]

    try:
        post_id = UUID(task_id)
    except ValueError:
        await callback.answer("Некоректний ID", show_alert=True)
        return

    post = await PostRepo(session).get_post_by_id(post_id)
    if not post:
        await callback.answer("Завдання не знайдено", show_alert=True)
        return

    if callback.from_user.id != post.author_id:
        await callback.answer("Скасувати може тільки автор", show_alert=True)
        return

    post = await PostRepo(session).mark_cancelled(post_id)

    await callback.message.edit_text(
        render_post_text(post),
        parse_mode="HTML",
        reply_markup=task_actions_keyboard(post, callback.from_user.id),
    )
    await callback.answer("Завдання відмінено")


@router.callback_query(F.data.startswith("task_chat:"))
async def task_chat_callback(callback: CallbackQuery):
    await callback.answer("Переписка поки що заглушка", show_alert=True)


@router.callback_query(F.data == "noop")
async def noop_callback(callback: CallbackQuery):
    await callback.answer()


@router.message(F.text == "Нове Завдання")
async def task_create(message: Message, state: FSMContext):
    await message.answer("ℹ️ Введіть назву")
    await state.set_state(Post_state.title)


@router.message(StateFilter(Post_state.title))
async def task_subject(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(Post_state.subject)
    await message.answer("ℹ️ Введіть предмет")


@router.message(StateFilter(Post_state.subject))
async def task_description(message: Message, state: FSMContext):
    await state.update_data(subject=message.text)
    await state.set_state(Post_state.description)
    await message.answer("ℹ️ Опишіть суть завдання")


@router.message(StateFilter(Post_state.description))
async def task_file_step(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(Post_state.file)
    await message.answer("ℹ️ Надішліть файл або введіть '-' якщо файл не потрібен")


@router.message(StateFilter(Post_state.file), F.document)
async def task_save_with_file(message: Message, session: AsyncSession, state: FSMContext):
    data = await state.get_data()

    post = await PostRepo(session).create_post(
        author_id=message.chat.id,
        title=data["title"],
        subject=data["subject"],
        description=data["description"],
        file_id=message.document.file_id,
        file_name=message.document.file_name,
        post_type=PostType.PUBLIC,
    )

    await state.clear()

    await message.answer(
        "✅ Нове завдання створено\n\n"
        f"{render_post_text(post)}",
        parse_mode="HTML",
        reply_markup=menu_keyboard(),
    )


@router.message(StateFilter(Post_state.file), F.text == "-")
async def task_save_without_file(message: Message, session: AsyncSession, state: FSMContext):
    data = await state.get_data()

    post = await PostRepo(session).create_post(
        author_id=message.chat.id,
        title=data["title"],
        subject=data["subject"],
        description=data["description"],
        file_id=None,
        file_name=None,
        post_type=PostType.PUBLIC,
    )

    await state.clear()

    await message.answer(
        "✅ Нове завдання створено\n\n"
        f"{render_post_text(post)}",
        parse_mode="HTML",
        reply_markup=menu_keyboard(),
    )