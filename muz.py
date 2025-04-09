import logging
import os
import asyncio
import yandex_music
import re
from telegram.ext import CommandHandler, Application, filters, MessageHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

client = yandex_music.Client('').init()


def file_n(name: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', '', name)[:250]


async def download_track(track, file_path: str) -> None:
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, track.download, file_path)


async def search_tracks(query: str):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, client.search, query)


async def start(update, context):
    user = update.effective_user
    await update.message.reply_markdown(
        f"Привет {user.name}\nЯ музыкальный бот. Напиши название песни, и я найду ее для тебя!")


async def handle_search(update, context):
    query = update.message.text.strip()
    search_results = await search_tracks(query)
    track = search_results.best.result
    if not isinstance(track, yandex_music.Track):
        await update.message.reply_text("Трек не найден")
        return

    try:
        artists = ", ".join(a.name for a in track.artists)
        title = track.title
        filename = file_n(f"{artists} - {title}.mp3")
        file_path = os.path.join("music", filename)

        if not os.path.exists(file_path):
            await download_track(track, file_path)
            logger.info(f"Downloaded: {filename}")
        await update.message.reply_text(artists)
        await update.message.reply_text(title)
        await update.message.reply_audio(
            audio=open(file_path, 'rb'),
            title=title,
            performer=artists,
            duration=track.duration_ms // 1000
        )
    except Exception as e:
        logger.error(f"Error: {e}")


def main():
    os.makedirs("music", exist_ok=True)
    application = Application.builder().token('').build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_search))
    application.run_polling()


if __name__ == "__main__":
    main()
