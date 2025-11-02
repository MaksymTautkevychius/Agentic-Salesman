import os, sys
from pathlib import Path

from telegram import Update 
from dotenv import load_dotenv, find_dotenv
from typing import Final
from io import BytesIO

from src.models.Input import InputLevel, Type
from src.pre_processing.InputProcessing import add_new_data

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
input = False    

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages"""
    user_text = update.message.text
    chat_id = update.effective_chat.id

    input_data = InputLevel(
        chat_id=chat_id,
        user_id=update.effective_user.id,
        user=update.effective_user.username,
        type=Type.TEXT, 
        message=update.message.text,
        image=None  
    )
    add_new_data(input_data)


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo messages with optional caption"""
    try:
        photo = update.message.photo[-1]
        caption_text = update.message.caption or "No caption"
        chat_id = update.effective_chat.id
        file = await context.bot.get_file(photo.file_id)
        filename = f"{photo.file_id}.jpg"
        filepath = PHOTOS_DIR / filename
        await file.download_to_drive(filepath)
        photo_bytes = BytesIO()
        await file.download_to_memory(photo_bytes)
        photo_bytes.seek(0)  
        
        messages.append({
            'type': 'photo',
            'user': update.effective_user.username,
            'user_id': update.effective_user.id,
            'chat_id': chat_id,
            'file_path': str(filepath),
            'file_id': photo.file_id,
            'caption': caption_text,
            'bytes': photo_bytes  
        })
        
        print(f"Photo received from {update.effective_user.username} (chat_id: {chat_id})")
        print(f"Caption: {caption_text}")
        print(f"Saved to: {filepath}")
        
        await update.message.reply_text(
            f"Caption: {caption_text}\n"
            f"Saved as: {filename}"
        )
        
    except Exception as e:
        print(f"Error handling photo: {e}")


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        
        await update.message.reply_text(
            f"Saved as: {filename}"
        )
        
    except Exception as e:
        print(f"Error handling voice: {e}")

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return

def start_telegram_bot():
    """Initialize and start the bot"""
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", hello))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    
    print(f"Telegram Bot '{TelegramBotName}' started")
    print(f"Photos directory: {PHOTOS_DIR.absolute()}")
    print(f"Audio directory: {AUDIO_DIR.absolute()}")
    
    app.run_polling()