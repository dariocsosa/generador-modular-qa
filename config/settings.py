"""
Configuración central del generador Q&A
Carga variables de entorno y define configuraciones por defecto
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict, Any

# Cargar variables de entorno
load_dotenv()

class Settings:
    """Configuración centralizada de la aplicación"""
    
    # Rutas base
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    DOCUMENTS_DIR = DATA_DIR / "documents"
    OUTPUT_DIR = DATA_DIR / "output"
    LOGS_DIR = BASE_DIR / "logs"
    
    # APIs Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
    
    # Configuración de modelos
    DEFAULT_MODEL_PROVIDER = os.getenv("DEFAULT_MODEL_PROVIDER", "openai")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
    ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")
    GOOGLE_MODEL = os.getenv("GOOGLE_MODEL", "gemini-pro")
    
    # Configuraciones de aplicación
    MAX_QUESTIONS_PER_BATCH = int(os.getenv("MAX_QUESTIONS_PER_BATCH", "50"))
    MAX_DOCUMENT_SIZE_MB = int(os.getenv("MAX_DOCUMENT_SIZE_MB", "10"))
    SUPPORTED_LANGUAGES = os.getenv("SUPPORTED_LANGUAGES", "es,en").split(",")
    DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "es")
    
    # Configuración de salida
    OUTPUT_FORMAT = os.getenv("OUTPUT_FORMAT", "both")  # csv, json, both
    DEFAULT_CATEGORY = os.getenv("DEFAULT_CATEGORY", "general")
    DEFAULT_DIFFICULTY_LEVEL = os.getenv("DEFAULT_DIFFICULTY_LEVEL", "intermediate")
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/qa_generator.log")
    
    # Prompts por defecto
    DEFAULT_QA_PROMPT_TEMPLATE = """
    Eres un experto generador de preguntas y respuestas para bases de conocimiento.
    
    Tema: {topic}
    Categoría: {category}
    Nivel de dificultad: {difficulty}
    Idioma: {language}
    
    Genera {num_questions} pares de pregunta-respuesta sobre el tema especificado.
    
    Requisitos:
    - Las preguntas deben ser claras, específicas y relevantes
    - Las respuestas deben ser precisas, completas pero concisas
    - Variar el tipo de preguntas (factual, conceptual, aplicación, análisis)
    - Usar un lenguaje apropiado para el nivel de dificultad especificado
    
    Formato de respuesta:
    Para cada par Q&A, usar exactamente este formato:
    
    PREGUNTA: [pregunta aquí]
    RESPUESTA: [respuesta aquí]
    CATEGORIA: {category}
    NIVEL: {difficulty}
    TEMA: {topic}
    ---
    """
    
    # Configuraciones de procesamiento de documentos
    CHUNK_SIZE = 1000  # Tamaño de chunks para procesamiento de documentos
    CHUNK_OVERLAP = 200  # Overlap entre chunks
    
    @classmethod
    def create_directories(cls):
        """Crear directorios necesarios si no existen"""
        for directory in [cls.DATA_DIR, cls.DOCUMENTS_DIR, cls.OUTPUT_DIR, cls.LOGS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def validate_api_keys(cls) -> Dict[str, bool]:
        """Validar que las API keys estén configuradas"""
        return {
            "openai": bool(cls.OPENAI_API_KEY),
            "anthropic": bool(cls.ANTHROPIC_API_KEY),
            "google": bool(cls.GOOGLE_API_KEY),
            "perplexity": bool(cls.PERPLEXITY_API_KEY)
        }

# Instancia global de configuración
settings = Settings()
settings.create_directories()