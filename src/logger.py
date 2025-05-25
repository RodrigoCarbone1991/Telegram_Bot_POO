import logging

def setup_logger():
    """
    Configura el sistema de logging para el proyecto.
    """
    logging.basicConfig(
        level = logging.INFO,  # Nivel de registro: DEBUG, INFO, WARNING, ERROR, CRITICAL
        format = "%(asctime)s - %(levelname)s - %(message)s",  # Formato del log
        filename = "bot.log",  # Archivo donde se guardarán los logs (opcional)
        filemode ="a"  # Modo: 'a' para anexar, 'w' para sobrescribir
    )
    return logging.getLogger(__name__)  # Devuelve un logger para usar en otros scripts
