import asyncio
import threading
import os
from telegram import Bot
from telegram.request import HTTPXRequest
from dotenv import load_dotenv, find_dotenv

path = find_dotenv()
load_dotenv(path)
TOKEN = os.getenv("TelegramAPI")


def send_message_sync(chat_id: int, message: str):
    """Send message from synchronous code - non-blocking"""
    async def _send():
        try:
            request = HTTPXRequest(
                connection_pool_size=8,
                read_timeout=20,
                write_timeout=20,
                connect_timeout=20
            )
            bot = Bot(token=TOKEN, request=request)
            await bot.send_message(chat_id=chat_id, text=message)
        except Exception as e:
            print(f"Error in _send: {e}")
            import traceback
            traceback.print_exc()

    def run_async():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_send())
        loop.close()

    thread = threading.Thread(target=run_async, daemon=True)
    thread.start()


def send_image_sync(chat_id: int, image_url: str, caption: str = None):
    """Send image from synchronous code - non-blocking"""
    async def _send():
        try:
            request = HTTPXRequest(
                connection_pool_size=8,
                read_timeout=20,
                write_timeout=20,
                connect_timeout=20
            )
            bot = Bot(token=TOKEN, request=request)
            await bot.send_photo(
                chat_id=chat_id,
                photo=image_url,
                caption=caption
            )
        except Exception as e:
            print(f"Error in _send_image: {e}")
            import traceback
            traceback.print_exc()

    def run_async():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_send())
        loop.close()

    thread = threading.Thread(target=run_async, daemon=True)
    thread.start()