import os
import re
import joblib
import unicodedata
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from logger import setup_logger


class Preprocesador:
    def limpiar_texto(self, texto: str) -> str:
        texto = texto.lower() 
        texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
        texto = re.sub(r'[^\w\s]', '', texto) 
        texto = re.sub(r'\s+', ' ', texto).strip()
        return texto


class Clasificador_Bot:
    def __init__(self, modelo_path, vectorizer_path):
        self.modelo = joblib.load(modelo_path)
        self.vectorizer = joblib.load(vectorizer_path)
        self.logger = setup_logger()
        self.preprocesador = Preprocesador()

    def obtener_respuesta(self, pregunta_usuario: str) -> str: 
        pregunta_limpia = self.preprocesador.limpiar_texto(pregunta_usuario)
        pregunta_vectorizada = self.vectorizer.transform([pregunta_limpia])
        respuesta = self.modelo.predict(pregunta_vectorizada)
        return respuesta[0]

    async def responder(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try: 
            pregunta = update.message.text 
            mensaje_limpio = self.preprocesador.limpiar_texto(pregunta)
            es_muy_corto = len(mensaje_limpio) < 2 
            solo_una_letra_o_numero = mensaje_limpio.isalnum() and len(mensaje_limpio) == 1 
            contiene_palabras = any(c.isalpha() for c in mensaje_limpio) and len(mensaje_limpio.split()) >= 1 
        
            if es_muy_corto or solo_una_letra_o_numero or not contiene_palabras: 
                await update.message.reply_text("Por ahí quisiste decir otra cosa o no entendí🧐, ¿lo escribís de nuevo?")
                return
        
            respuesta = self.obtener_respuesta(pregunta)
        
        except Exception as e:
            self.logger.error(f"Error al responder: {e}")
            await update.message.reply_text("Si te digo que se cayó el sistema, ¿me creés? jaja😂.")
        
async def main():
    load_dotenv()
    telegram_bot_token = os.getenv("telegram_bot_token")
    
    if not telegram_bot_token:
        raise ValueError("No se encontro el token en el archivo .env")
    
    modelo_path = "../modelo/modelo_entrenado.pkl"
    vectorizer_path = "../modelo/vectorizer.pkl"
    
    bot = Clasificador_Bot("../modelo/modelo_entrenado.pkl", "../modelo/vectorizer.pkl")
    
    app = ApplicationBuilder().token(telegram_bot_token).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.responder))
    print("🤖 Bot en funcionamiento...") 
    await app.initialize() 
    await app.start()
    await app.updater.start_polling()


if __name__ == "__main__":#verifica que el script es ejecutado directamente y no como modulo
    import asyncio

    async def safe_main():#se define nuevamente la funcion asyncronica
        await main()#llama a main para inicializar el bot y esperar indefinidamente
        await asyncio.Event().wait()#permite que el bot siga funcionando mientras espera mensajes

    try:
        asyncio.get_event_loop().run_until_complete(safe_main())#permite que el bo no se bloquee con un bucle de eventos
    except KeyboardInterrupt:#el bucle continua hasta que se produce una excepcion por teclado (keyboardinterrump) con ctrl + c
        print("🔴 Bot detenido manualmente.")