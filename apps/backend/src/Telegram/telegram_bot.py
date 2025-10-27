from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackContext
from dotenv import load_dotenv, find_dotenv
from typing import Final
from io import BytesIO
import os


path = find_dotenv()
load_dotenv(path)

TOKEN: Final = os.getenv("TelegramAPI")
TelegramBotName = 'DiplomaProject_S26871_bot'

messages: list = []

async def hello(update: Update):
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    messages.append(user_text)
    print(messages)
    await update.message.reply_text(f"You said: {user_text}")

def photo(update: Update, context: CallbackContext):
    file: object = context.bot.get_file(update.message.photo[-1].file_id)
    print(file)
    #f =  BytesIO(file.download_as_bytearray())
    #print(f)


def start_telegram_bot():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", hello))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    app.add_handler(MessageHandler(filters.PHOTO,photo))
    print(f" Telegram Bot '{TelegramBotName}' started")
    app.run_polling() 

start_telegram_bot()