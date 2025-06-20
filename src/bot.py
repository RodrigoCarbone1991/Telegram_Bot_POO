import os
from dotenv import load_dotenv
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters,
)
from src.clasificador_bot import Clasificador_Bot

async def main():
    # Cargar variables de entorno
    load_dotenv()
    telegram_bot_token = os.getenv("telegram_bot_token")
    if not telegram_bot_token:
        raise ValueError("No se encontró el token en el archivo .env")

    # Crear instancia de nuestro bot
    bot = Clasificador_Bot(
        modelo_path="modelo/modelo_entrenado.pkl",
        vectorizer_path="modelo/vectorizer.pkl"
    )

    # Configurar la aplicación de Telegram
    app = ApplicationBuilder().token(telegram_bot_token).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.responder))

    print("🤖 Bot en funcionamiento...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()

# Para ejecutar directamente con "python src/bot.py"
if __name__ == "__main__":
    import asyncio
    async def safe_main():
        await main()
        await asyncio.Event().wait()
    try:
        asyncio.get_event_loop().run_until_complete(safe_main())
    except KeyboardInterrupt:
        print("🔴 Bot detenido manualmente.")