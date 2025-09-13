"""
Modelos de datos usando Pydantic para validación y estructura
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, validator
import uuid

class QAItem(BaseModel):
    """Modelo para un elemento individual de pregunta-respuesta"""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    pregunta: str = Field(..., min_length=10, description="La pregunta formulada")
    respuesta: str = Field(..., min_length=20, description="La respuesta correspondiente")
    categoria: str = Field(default="general", description="Categoría temática")
    nivel: Literal["básico", "intermedio", "avanzado"] = Field(
        default="intermedio", 
        description="Nivel de dificultad"
    )
    tema: str = Field(default="", description="Tema específico")
    fuentes: List[str] = Field(default_factory=list, description="Fuentes de información")
    palabras_clave: List[str] = Field(default_factory=list, description="Palabras clave relevantes")
    idioma: str = Field(default="es", description="Idioma del contenido")
    confianza: float = Field(default=0.8, ge=0.0, le=1.0, description="Nivel de confianza")
    metadatos: Dict[str, Any] = Field(default_factory=dict, description="Metadatos adicionales")
    fecha_creacion: datetime = Field(default_factory=datetime.now)
    
    @validator('pregunta', 'respuesta')
    def clean_text(cls, v):
        """Limpiar y validar texto"""
        if isinstance(v, str):
            return v.strip()
        return v
    
    @validator('categoria', 'tema')
    def lowercase_category_theme(cls, v):
        """Convertir categoría y tema a minúsculas"""
        if isinstance(v, str):
            return v.lower().strip()
        return v

class QABatch(BaseModel):
    """Modelo para un lote de elementos Q&A"""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    items: List[QAItem] = Field(default_factory=list)
    origen: Literal["prompt", "documento", "manual", "api"] = Field(
        ..., description="Origen de la generación"
    )
    prompt_original: Optional[str] = Field(None, description="Prompt usado si aplica")
    documento_fuente: Optional[str] = Field(None, description="Documento fuente si aplica")
    parametros_generacion: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Parámetros usados en la generación"
    )
    estadisticas: Dict[str, Any] = Field(
        default_factory=dict,
        description="Estadísticas del lote"
    )
    fecha_creacion: datetime = Field(default_factory=datetime.now)
    
    def add_item(self, item: QAItem):
        """Agregar un item al lote"""
        self.items.append(item)
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del lote"""
        if not self.items:
            return {"total": 0}
        
        categorias = {}
        niveles = {}
        temas = {}
        
        for item in self.items:
            # Contar categorías
            categorias[item.categoria] = categorias.get(item.categoria, 0) + 1
            # Contar niveles
            niveles[item.nivel] = niveles.get(item.nivel, 0) + 1
            # Contar temas
            if item.tema:
                temas[item.tema] = temas.get(item.tema, 0) + 1
        
        return {
            "total": len(self.items),
            "categorias": categorias,
            "niveles": niveles,
            "temas": temas,
            "confianza_promedio": sum(item.confianza for item in self.items) / len(self.items)
        }

class GenerationRequest(BaseModel):
    """Modelo para requests de generación"""
    
    tipo: Literal["prompt", "documento"] = Field(..., description="Tipo de generación")
    
    # Para generación por prompt
    prompt: Optional[str] = Field(None, description="Prompt temático")
    tema: Optional[str] = Field(None, description="Tema específico")
    categoria: Optional[str] = Field("general", description="Categoría")
    nivel: Optional[Literal["básico", "intermedio", "avanzado"]] = Field("intermedio")
    num_preguntas: Optional[int] = Field(10, ge=1, le=100, description="Número de preguntas")
    
    # Para generación por documento
    documento_path: Optional[str] = Field(None, description="Ruta al documento")
    
    # Configuración general
    modelo: Optional[str] = Field("openai", description="Proveedor de modelo")
    idioma: Optional[str] = Field("es", description="Idioma")
    usar_busqueda_avanzada: Optional[bool] = Field(False, description="Usar APIs como Perplexity")
    
    @validator('tipo')
    def validate_request_type(cls, v, values):
        """Validar que se proporcionen los campos necesarios según el tipo"""
        if v == "prompt" and not values.get('prompt') and not values.get('tema'):
            raise ValueError("Para tipo 'prompt' se requiere 'prompt' o 'tema'")
        elif v == "documento" and not values.get('documento_path'):
            raise ValueError("Para tipo 'documento' se requiere 'documento_path'")
        return v

class ExportConfig(BaseModel):
    """Configuración para exportación de datos"""
    
    formato: Literal["csv", "json", "xlsx", "yaml"] = Field("csv", description="Formato de exportación")
    incluir_metadatos: bool = Field(True, description="Incluir metadatos en la exportación")
    filtros: Dict[str, Any] = Field(default_factory=dict, description="Filtros a aplicar")
    ruta_salida: Optional[str] = Field(None, description="Ruta específica de salida")
    nombre_archivo: Optional[str] = Field(None, description="Nombre específico del archivo")