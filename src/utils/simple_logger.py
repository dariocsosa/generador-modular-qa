"""
Sistema de logging simple sin dependencias externas
"""

import logging
import sys
from pathlib import Path

class SimpleLogger:
    """Logger simple usando solo la librería estándar"""
    
    def __init__(self, name: str = "qa_generator"):
        self.logger = logging.getLogger(name)
        if not self.logger.handlers:
            self._setup_logger()
    
    def _setup_logger(self):
        """Configurar el logger"""
        self.logger.setLevel(logging.INFO)
        
        # Handler para consola
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Formato simple
        formatter = logging.Formatter(
            '[%(levelname)s] %(name)s: %(message)s'
        )
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(console_handler)
    
    def info(self, message):
        """Log info message"""
        self.logger.info(message)
    
    def error(self, message):
        """Log error message"""
        self.logger.error(message)
    
    def warning(self, message):
        """Log warning message"""
        self.logger.warning(message)

# Instancia global
simple_logger = SimpleLogger()

def get_logger(name: str = None):
    """Obtener logger simple"""
    return simple_logger