import os
import re
import joblib
import unicodedata
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, MessengeHandler, ContextTypes, filters
from logger import setup_logger


class Preprocesador:#VA A LIMPIAR EL TEXTO DE ENTRADA DEL USUARIO PARA DEVOLVERLO LIMPIO ELIMINANDO PUNTUACIONES, CARACTERES, MAYUSCULAS Y ESPACIOS EN BLANCO
    def limpiar_texto(self, texto: str) -> str:
        texto = texto.lower() #de un Hola Mundo devuelve un hola mundo
        texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')#de un niño devuelve nino
        texto = re.sub(r'[^\w\s]', '', texto) #de un ¡Hola, Mundo! devuelve un Hola Mundo
        texto = re.sub(r'\s+', ' ', texto).strip()# de un " Hola Mundo " devuelve un "Hola Mundo"
        return texto


class Clasificador_Bot:#METODO QUE RECIBE LA PREGUNTA DEL USUARIO, LE APLICA LOS METODOS DE LIMPIEZA DEL PREPROCESADOR Y CONVIERET LA PREGUNTA EN UNA REPRESENTACION NUMERICA PARA EL MODELO
    def __init__(self, modelo_path, vectorizer_path):#metodo constructor que recibe las rutas donse se encuentra el modelo entrenado y el vectorizador
        self.modelo = joblib.load(modelo_path)#carga del modelo y se almacena en la instancia del clasificador_bot
        self.vectorizer = joblib.load(vectorizer_path)#igual que la liena anterior pero con el vectorizer
        self.preprocesador = Preprocesador()#creacion o llamado de la instancia de la clase preprocesador y almacenado en la instancia del clasificador_bot para utilizarlo mas tarde
        self.logger = setup_logger()#configuracion y almacenamiento del loger como instancia de la clase

    def obtener_respuesta(self, pregunta_usuario: str) -> str: #metodo dentro de la clase clasificador_bot para obtener_respuesta a partir de un str y devolver un str
        pregunta_limpia = self.preprocesador.limpiar_texto(pregunta_usuario)# la pregunta limpia es pasada al metodo limpiar_texto
        pregunta_vectorizada = self.vectorized.transform([pregunta_limpia])#transforma el texto limpio del constructor en una representacion numerica que pueda entender el modelo
        respuesta = self.modelo.predict(pregunta_vectorizada)#se carga el modelo del constructor  que toma una pregunta vectorizada y predice cual es la respuesta o la calse asociada
        return respuesta[0]#el modelo retorna la primera respuesta (0) de la prediccion obtenida y es lo que se respondera al usuario

async def responder(self, update: Update, context: ContextTypes.DEFAULT_TYPE):# METODO ASINCRONICO PARA INTERACTUAR CON EL USUARIO, RECIBIR LOS MENSAJES, PROCESARLOS Y DEVOLVER UNA RESPUESTA
    try: #el codigo se envuelve en un try para manejar los posibles errores sin afectar la ejecucion del metodo, ya que si ocurre un error, este se captura sin interrumpir el flujo
        pregunta = update.message.text #obtencion del mensaje
        mensaje_limpio = self.preprocesador.limpiar_texto(pregunta)#limpieza del mensaje
        #definicion de variables a analizar
        es_muy_corto = len(mensaje_limpio) < 2 #mide la longitud del mensaje (no puede ser menor a 2)
        solo_una_letra_o_numero = mensaje_limpio.isalnum() and len(mensaje_limpio) == 1 #verifica qwue el mensaje no sea solo un caracter alfanumerico (a o 5)
        contiene_palabras = any(c.isalpha() for c in mensaje_limpio) and len(mensaje_limpio.split()) >= 1 #corrobora que al menos uno de los caracteres sea una letra y que el texto tenga al menos una palabra
        
        if es_muy_corto or solo_una_letra_o_numero or not contiene_palabras: #evalua las tres condiciones y si se cumple alguna devuelve un mensaje
            await update.mesage.replay_text("Por ahí quisiste decir otra cosa o no entendí🧐, ¿lo escribís de nuevo?")
            return
        
        respuesta = self.obtener_respuesta(pregunta)#si el mensaje es valido se obitne una respuesta
        await update.message.replay_text(f" {respuesta}")#una vez obtenida la respuesta el bot la envia al usuario con await para que el mensaje se envie de manera asincronica para evitar bloquear otras interacciones
        
    except Exception as e:#si ocurre algun error en el codigo, se captura con el except y se guarda en el logger
        self.logger.error(f"Error al responder: {e}")
        await update.mesage.reply_text("Si te digo que se cayó el sistema, ¿me creés? jaja😂.")#respuesta al usuario cuando hay un error
        
async def main():#metodo principal que se ejecuta cuando se inicia el bot. esta en asyncro para no frenar y bloquear ejecuciones mientras se espera la pregunta 
    load_dotenv()#carga las variables (token) que estan fuera del codigo
    telegram_bot_token = os.getenv("telegram_bot_token")
    
    if not telegram_bot_token:#si no se encuentra el token devuelve un mensaje de error una excepcion(valuerror)
        raise ValueError("No se encontro el token en el archivo .env")
    
    bot = Clasificador_Bot("modelo/modelo_entrenado.pkl", "modelo/vectorizer.pkl")#se crea una instancia del bot (clasificador_bot) con las rutas de los archivos del moedelo y el vectorizador
    
    app = ApplicationBuilder().token(telegram_bot_token).build()# se construye la aplicacion del bot utilizando la libreria de python telegram bot y pasandole el token
    app.add_error_handler(MessengeHandler(filters.TEXT & ~filters.COMMAND, bot.responder))#se agrega un manejador de mensajes especificando que el bot solo debe responder a texto y no a comandos
    print("🤖 Bot en funcionamiento...") #inicializa el bot
    await app.initialize() #inicializa la aplicacion de telegram de forma asincronica
    await app.start()#inicia la escucha del bot
    await app.updater.start_polling()#hace el polling de la api de telegam significa que el bot estara verificando continuamente si hay mensajes para procesar


if __name__ == "__main__":#verifica que el script es ejecutado directamente y no como modulo
    import asyncio

    async def safe_main():#se define nuevamente la funcion asyncronica
        await main()#llama a main para inicializar el bot y esperar indefinidamente
        await asyncio.Event().wait()#permite que el bot siga funcionando mientras espera mensajes

    try:
        asyncio.get_event_loop().run_until_complete(safe_main())#permite que el bo no se bloquee con un bucle de eventos
    except KeyboardInterrupt:#el bucle continua hasta que se produce una excepcion por teclado (keyboardinterrump) con ctrl + c
        print("🔴 Bot detenido manualmente.")