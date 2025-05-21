import asyncio
from telegram import Bot
from dotenv import load_dotenv
import os
from logger import setup_logger

# Configurar el logger
logger = setup_logger()

# Cargar variables de entorno desde .env
load_dotenv()

# Obtener el token del archivo .env
telegram_bot_token = os.getenv("telegram_bot_token")

# Verificar si el token fue cargado correctamente
if not telegram_bot_token:
    raise ValueError("El token de Telegram no se cargó. Verificar archivo .env y la clave telegram_bot_token.")

async def get_user_id():
    """
    Función asincrónica para obtener el ID de usuario/chat.
    """
    try:
        bot = Bot(token=telegram_bot_token)
        updates = await bot.get_updates()  # Esperar actualizaciones
        if not updates:
            print("No hay actualizaciones disponibles. Asegurarse de haber enviado un mensaje al bot.")
            return

        # Recorrer las actualizaciones y extraer el ID de chat
        for update in updates:
            print(f"ID de usuario/chat: {update.message.chat.id}")
    except Exception as e:
        print(f"Error al obtener el ID: {e}")

# Ejecutar la función asincrónica
asyncio.run(get_user_id())

