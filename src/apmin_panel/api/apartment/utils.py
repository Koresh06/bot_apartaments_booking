import requests
import aiohttp
from io import BytesIO
from PIL import Image

from src.core.config import config

TELEGRAM_BOT_TOKEN = config.tg_bot.token


async def fetch_and_determine_extension(photo_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(photo_url) as response:
            if response.status == 200:
                img_data = await response.read()
                img = Image.open(BytesIO(img_data))
                img_format = img.format.lower()  # Получаем формат изображения
                # Генерируем новый URL с добавленным расширением
                new_url = f"{photo_url}.{img_format}"
                return new_url  # Возвращаем полный путь к фото с форматом
            else:
                return None  # Если не удалось получить изображение


async def get_photo_url(file_id: str) -> str:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getFile?file_id={file_id}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise ValueError(f"Ошибка запроса к Telegram API для file_id: {file_id}")
            
            file_info = await response.json()

            if "result" not in file_info:
                raise ValueError(f"'result' отсутствует в ответе Telegram API для file_id: {file_id}")

            # Получаем путь к файлу с расширением
            file_path = file_info["result"]["file_path"]
            # Возвращаем полный URL для скачивания файла
            photo_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"

            extension = await fetch_and_determine_extension(photo_url)

            return extension
        

async def get_photos_urls(file_ids: list) -> list:
    print(file_ids)
    return [await get_photo_url(file_id[0]) for file_id in file_ids]
