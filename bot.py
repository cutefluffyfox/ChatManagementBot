import logging
from os import getenv

import dotenv
from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message, CallbackQuery, ContentType


from helpers import generators


# Configure logging
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
    # filename="logs.log"
)


# Initialize environment variables from .env file (if it exists)
dotenv.load_dotenv(dotenv.find_dotenv())
BOT_TOKEN = getenv('BOT_TOKEN')


# Check that critical variables are defined
if BOT_TOKEN is None:
    logging.critical('No BOT_TOKEN variable found in project environment')


# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['switch'])
async def switch(message: Message):
    await message.answer(
        text="To switch from anonymous mode to basic please click button:",
        reply_markup=generators.generate_inline_markup({'text': 'Change mode', 'callback_data': 'switchMode'})
    )


@dp.callback_query_handler(lambda c: c.data == 'switchMode')
async def switch_mode(callback_query: CallbackQuery):
    chat_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id
    permissions = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)

    if permissions.status == 'member':
        await bot.promote_chat_member(chat_id=chat_id, user_id=user_id, is_anonymous=True)
        await callback_query.answer('Status changed successfully')
        return

    if permissions.is_chat_admin():
        only_rights = dict(permissions)
        for info in ['user', 'status', 'can_be_edited', 'is_anonymous']:
            if only_rights.get(info) is not None:
                only_rights.pop(info)
        is_anonymous = permissions['is_anonymous']
        if (not permissions.is_chat_owner) and permissions['can_be_edited']:
            await bot.promote_chat_member(chat_id=chat_id, user_id=user_id, is_anonymous=not is_anonymous, **only_rights)
            await callback_query.answer('Status changed successfully')
        else:
            await callback_query.answer('Please contact chat owner to change your status.', show_alert=True)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
