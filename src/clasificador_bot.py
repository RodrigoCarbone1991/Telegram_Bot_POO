import os
import joblib
from telegram import Update
from telegram.ext import ContextTypes
from src.preprocesador import Preprocesador
from src.logger import setup_logger

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