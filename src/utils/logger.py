"""
Sistema de logging centralizado para el generador Q&A
"""

import logging
import sys
from pathlib import Path
from loguru import logger
from config.settings import settings

class LoggerSetup:
    """Configuración del sistema de logging"""
    
    @staticmethod
    def setup_logger():
        """Configurar el logger principal"""
        # Eliminar el handler por defecto de loguru
        logger.remove()
        
        # Configurar formato de logs
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )
        
        # Handler para consola
        logger.add(
            sys.stdout,
            format=log_format,
            level=settings.LOG_LEVEL,
            colorize=True
        )
        
        # Handler para archivo
        log_file = Path(settings.LOG_FILE)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            log_file,
            format=log_format,
            level=settings.LOG_LEVEL,
            rotation="10 MB",
            retention="1 week",
            compression="zip"
        )
        
        return logger

# Configurar y exportar logger
app_logger = LoggerSetup.setup_logger()

# Función de conveniencia para otros módulos
def get_logger(name: str = None):
    """Obtener una instancia del logger"""
    if name:
        return app_logger.bind(name=name)
    return app_logger