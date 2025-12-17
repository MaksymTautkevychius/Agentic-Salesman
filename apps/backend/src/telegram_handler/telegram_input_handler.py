import os
import time
import threading
from pathlib import Path
from telegram import Update
from dotenv import load_dotenv, find_dotenv
from typing import Final
from io import BytesIO
from telegram import Bot
from telegram.request import HTTPXRequest
from src.models.DM.input import InputLevel, Type
from src.services.wait_and_reply import add_new_data_to_dm
from src.models.audio_input import AudioInput
from src.models.image_input import ImageInput
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)

path = find_dotenv()
load_dotenv(path)

TOKEN: Final = os.getenv("TelegramAPI")
TelegramBotName = 'DiplomaProject_S26871_bot'
messages: list = []

PHOTOS_DIR = Path("received_photos")
AUDIO_DIR = Path("received_audio")
PHOTOS_DIR.mkdir(exist_ok=True)
AUDIO_DIR.mkdir(exist_ok=True)

_bot_app = None


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages"""
    print('clicked')
    user_text = update.message.text
    chat_id = update.effective_chat.id
    if chat_id==981594163 :
        return
        
    input_data = InputLevel(
        chat_id=chat_id,
        user_id=update.effective_user.id,
        user=update.effective_user.username,
        type=Type.TEXT,
        message=update.message.text,
        image=None,
        audio=None
    )
    add_new_data_to_dm(input_data)


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if chat_id==981594163 :
        return
    """Handle photo messages with optional caption"""
    try:
        photo = update.message.photo[-1]
        caption_text = update.message.caption or "No caption"
        chat_id = update.effective_chat.id
        
        file = await context.bot.get_file(photo.file_id)
        filename = f"{photo.file_id}.jpg"
        filepath = PHOTOS_DIR / filename
        
        print(filepath)
        print(filename)
        
        await file.download_to_drive(filepath)
        
        photo_bytes = BytesIO()
        await file.download_to_memory(photo_bytes)
        photo_bytes.seek(0)
        
        input_data = InputLevel(
            chat_id=chat_id,
            user_id=update.effective_user.id,
            user=update.effective_user.username,
            type=Type.IMAGE,
            message=update.message.caption or " ",
            image=ImageInput(
                file_path=str(filepath),
                file_id=photo.file_id,
                file_name=filename
            ),
            audio=None
        )
        add_new_data_to_dm(input_data)
        
        print(f"Photo received from {update.effective_user.username} (chat_id: {chat_id})")
        print(f"Caption: {caption_text}")
        print(f"Saved to: {filepath}")
        
    except Exception as e:
        print(f"Error handling photo using telegram bot: {e}")
        import traceback
        traceback.print_exc()


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if chat_id==981594163 :
        return
    """Handle voice messages (audio notes from Telegram)"""
    try:
        voice = update.message.voice
        caption_text = update.message.caption or "No caption"
        chat_id = update.effective_chat.id
        
        file = await context.bot.get_file(voice.file_id)
        filename = f"voice_{voice.file_id}.ogg"
        filepath = AUDIO_DIR / filename
        
        await file.download_to_drive(filepath)
        
        voice_bytes = BytesIO()
        await file.download_to_memory(voice_bytes)
        voice_bytes.seek(0)
        
        messages.append({
            'type': 'voice',
            'user': update.effective_user.username,
            'user_id': update.effective_user.id,
            'chat_id': chat_id,
            'file_path': str(filepath),
            'file_id': voice.file_id,
            'duration': voice.duration,
            'caption': caption_text,
            'bytes': voice_bytes
        })
        
        print(f"Voice message received from chat_id {chat_id}: {filename} ({voice.duration}s)")
        await update.message.reply_text(f"Saved as: {filename}")
        
    except Exception as e:
        print(f"Error handling voice: {e}")


def start_telegram_bot():
    """Initialize and start the bot (BLOCKING)"""
    global _bot_app
    _bot_app = ApplicationBuilder().token(TOKEN).build()
    
    _bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    _bot_app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    _bot_app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    
    print(f"Telegram Bot '{TelegramBotName}' started")
    print(f"Photos directory: {PHOTOS_DIR.absolute()}")
    print(f"Audio directory: {AUDIO_DIR.absolute()}")
    
    _bot_app.run_polling()


def start_telegram_bot_background():
    """Start bot in a background thread (NON-BLOCKING)"""
    bot_thread = threading.Thread(target=start_telegram_bot, daemon=True)
    bot_thread.start()
    print("Telegram bot running in background thread")
    time.sleep(2)
    return bot_thread