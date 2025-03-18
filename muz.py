import logging

import yandex_music
from telegram.ext import CommandHandler, Application, filters, MessageHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)


async def start(update, context):
    user_name = update.message.from_user.first_name
    await update.message.reply_text(f"Привет {user_name}")
    await update.message.reply_text('Я музыкальный бот. Напиши название песни, и я найду ее для тебя!')


async def search_music(update, context):
    client = yandex_music.Client('').init()

    search_results = client.search(update.message.adres)
    if search_results.best:
        track = search_results.best.result

        if isinstance(track, yandex_music.Track):
            await update.message.reply_text(f"Исполнитель: {', '.join(artist.name for artist in track.artists)}")
            await update.message.reply_text(f"Название: {track.title}")
            track.download('track.mp3')
            await update.message.reply_audio('track.mp3')
        else:
            await update.message.reply_text("Лучший результат не является треком.")
    else:
        await update.message.reply_text("Трек не найден.")


async def help(update, context):
    await update.message.reply_text(f"/start - перезапуск\n"
                                    f"/baza - история запросов")


async def baza(update, context):
    pass


def main():
    TOKEN = ''
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_music))
    application.run_polling()


if __name__ == '__main__':
    main()
