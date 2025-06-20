import re
import unicodedata

class Preprocesador:
    def limpiar_texto(self, texto: str) -> str:
        texto = texto.lower() 
        texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
        texto = re.sub(r'[^\w\s]', '', texto) 
        texto = re.sub(r'\s+', ' ', texto).strip()
        return texto