import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from config import Config
from gemini_client import GeminiClient
from database import Database


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=Config.BOT_TOKEN)
dp = Dispatcher()

# DB и клиент
db = Database()
client = GeminiClient()


# Клавиатура
def get_main_keyboard():
    keyboard = [
        [types.KeyboardButton(text="🆕 Новый запрос")],
    ]
    return types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    db.save_user(user_id)
    db.delete_messages(user_id)

    await message.answer(
        "Привет! Я умный ассистент ⚡\n"
        "Задавай вопрос — я отвечу.\n\n"
        "Контекст диалога будет сохраняться автоматически.",
        reply_markup=get_main_keyboard(),
    )


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "Просто напиши мне сообщение — я отвечу.\n"
        "Нажми «🆕 Новый запрос», чтобы начать новый диалог."
    )


@dp.message(lambda msg: msg.text == "🆕 Новый запрос")
async def new_dialog(message: types.Message):
    user_id = message.from_user.id
    db.delete_messages(user_id)
    await message.answer(
        "Диалог начат заново! 🆕\n" 
        "Можешь задавать новый вопрос.",
        reply_markup=get_main_keyboard(),
    )


@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    user_text = message.text.strip()

    db.save_user(user_id)

    # Восстанавливаем контекст из БД
    past = db.get_messages(user_id, limit=50)  # [(role, content), ...]

    contents = []
    for role, content in past:
        # Только две роли: user и model
        if role == 'user':
            contents.append({"role": "user", "parts": [{"text": content}]})
        else:
            # любые прочие сохраняемые роли (например 'assistant') считаем как 'model'
            contents.append({"role": "model", "parts": [{"text": content}]})

    # Добавляем текущее сообщение пользователя
    contents.append({"role": "user", "parts": [{"text": user_text}]})

    sent_msg = await message.answer("⌛ Думаю...")

    try:
        response_text = client.ask(contents)

        # Сохраняем в БД: роль user и роль model
        db.save_message(user_id, "user", user_text)
        db.save_message(user_id, "model", response_text)

        # Редактируем сообщение с ответом (без reply_markup)
        await sent_msg.edit_text(response_text)

    except Exception as e:
        logger.exception(f"Ошибка обработки сообщения: {e}")
        await sent_msg.edit_text(
            "❌ Ошибка при обращении к ChatGPT.\n"
            "Попробуйте снова через несколько секунд."
        )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
