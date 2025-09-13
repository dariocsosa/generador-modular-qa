"""
Tests para los modelos de datos
"""

import pytest
from datetime import datetime
from src.utils.data_models import QAItem, QABatch, GenerationRequest, ExportConfig

class TestQAItem:
    """Tests para el modelo QAItem"""
    
    def test_qa_item_creation_basic(self):
        """Test creación básica de QAItem"""
        item = QAItem(
            pregunta="¿Qué es Python?",
            respuesta="Python es un lenguaje de programación de alto nivel."
        )
        
        assert item.pregunta == "¿Qué es Python?"
        assert item.respuesta == "Python es un lenguaje de programación de alto nivel."
        assert item.categoria == "general"  # valor por defecto
        assert item.nivel == "intermedio"  # valor por defecto
        assert item.idioma == "es"  # valor por defecto
        assert item.confianza == 0.8  # valor por defecto
        assert isinstance(item.fecha_creacion, datetime)
        assert isinstance(item.id, str)
    
    def test_qa_item_creation_complete(self):
        """Test creación completa de QAItem"""
        item = QAItem(
            pregunta="¿Cuáles son los tipos de datos en Python?",
            respuesta="Los tipos básicos son: int, float, str, bool, list, dict, tuple, set.",
            categoria="programacion",
            nivel="básico",
            tema="tipos_datos",
            fuentes=["python.org", "docs.python.org"],
            palabras_clave=["python", "tipos", "datos"],
            idioma="es",
            confianza=0.95,
            metadatos={"autor": "test", "revisado": True}
        )
        
        assert item.categoria == "programacion"
        assert item.nivel == "básico"
        assert item.tema == "tipos_datos"
        assert len(item.fuentes) == 2
        assert len(item.palabras_clave) == 3
        assert item.confianza == 0.95
        assert item.metadatos["autor"] == "test"
    
    def test_qa_item_validation(self):
        """Test validación de QAItem"""
        # Test pregunta muy corta
        with pytest.raises(ValueError):
            QAItem(pregunta="Qué?", respuesta="Una respuesta válida de más de 20 caracteres.")
        
        # Test respuesta muy corta
        with pytest.raises(ValueError):
            QAItem(pregunta="¿Una pregunta válida?", respuesta="Corta.")
        
        # Test confianza fuera de rango
        with pytest.raises(ValueError):
            QAItem(
                pregunta="¿Pregunta válida?",
                respuesta="Respuesta válida de más de 20 caracteres.",
                confianza=1.5
            )
    
    def test_qa_item_text_cleaning(self):
        """Test limpieza de texto"""
        item = QAItem(
            pregunta="  ¿Pregunta con espacios?  ",
            respuesta="  Respuesta con espacios adicionales.  "
        )
        
        assert item.pregunta == "¿Pregunta con espacios?"
        assert item.respuesta == "Respuesta con espacios adicionales."

class TestQABatch:
    """Tests para el modelo QABatch"""
    
    def test_qa_batch_creation(self):
        """Test creación de QABatch"""
        items = [
            QAItem(pregunta="¿Pregunta 1?", respuesta="Respuesta 1 con suficientes caracteres."),
            QAItem(pregunta="¿Pregunta 2?", respuesta="Respuesta 2 con suficientes caracteres.")
        ]
        
        batch = QABatch(
            items=items,
            origen="prompt",
            prompt_original="Test prompt",
            parametros_generacion={"modelo": "test", "temperatura": 0.7}
        )
        
        assert len(batch.items) == 2
        assert batch.origen == "prompt"
        assert batch.prompt_original == "Test prompt"
        assert batch.parametros_generacion["modelo"] == "test"
        assert isinstance(batch.fecha_creacion, datetime)
        assert isinstance(batch.id, str)
    
    def test_qa_batch_add_item(self):
        """Test agregar item a batch"""
        batch = QABatch(items=[], origen="manual")
        
        item = QAItem(
            pregunta="¿Nueva pregunta?", 
            respuesta="Nueva respuesta con suficientes caracteres."
        )
        
        batch.add_item(item)
        assert len(batch.items) == 1
        assert batch.items[0] == item
    
    def test_qa_batch_get_stats(self):
        """Test obtener estadísticas de batch"""
        items = [
            QAItem(
                pregunta="¿P1?", 
                respuesta="R1 con suficientes caracteres.",
                categoria="cat1",
                nivel="básico"
            ),
            QAItem(
                pregunta="¿P2?", 
                respuesta="R2 con suficientes caracteres.",
                categoria="cat1",
                nivel="intermedio"
            ),
            QAItem(
                pregunta="¿P3?", 
                respuesta="R3 con suficientes caracteres.",
                categoria="cat2",
                nivel="básico"
            )
        ]
        
        batch = QABatch(items=items, origen="test")
        stats = batch.get_stats()
        
        assert stats["total"] == 3
        assert stats["categorias"]["cat1"] == 2
        assert stats["categorias"]["cat2"] == 1
        assert stats["niveles"]["básico"] == 2
        assert stats["niveles"]["intermedio"] == 1
        assert "confianza_promedio" in stats

class TestGenerationRequest:
    """Tests para el modelo GenerationRequest"""
    
    def test_generation_request_prompt(self):
        """Test request para generación por prompt"""
        request = GenerationRequest(
            tipo="prompt",
            prompt="Test prompt",
            categoria="test",
            nivel="básico",
            num_preguntas=5
        )
        
        assert request.tipo == "prompt"
        assert request.prompt == "Test prompt"
        assert request.categoria == "test"
        assert request.nivel == "básico"
        assert request.num_preguntas == 5
    
    def test_generation_request_documento(self):
        """Test request para generación por documento"""
        request = GenerationRequest(
            tipo="documento",
            documento_path="/path/to/doc.pdf"
        )
        
        assert request.tipo == "documento"
        assert request.documento_path == "/path/to/doc.pdf"
    
    def test_generation_request_validation(self):
        """Test validación de GenerationRequest"""
        # Test prompt sin prompt ni tema
        with pytest.raises(ValueError, match="Para tipo 'prompt' se requiere 'prompt' o 'tema'"):
            GenerationRequest(tipo="prompt")
        
        # Test documento sin ruta
        with pytest.raises(ValueError, match="Para tipo 'documento' se requiere 'documento_path'"):
            GenerationRequest(tipo="documento")

class TestExportConfig:
    """Tests para el modelo ExportConfig"""
    
    def test_export_config_basic(self):
        """Test configuración básica de exportación"""
        config = ExportConfig(formato="csv")
        
        assert config.formato == "csv"
        assert config.incluir_metadatos == True  # valor por defecto
        assert config.filtros == {}  # valor por defecto
    
    def test_export_config_complete(self):
        """Test configuración completa de exportación"""
        config = ExportConfig(
            formato="json",
            incluir_metadatos=False,
            filtros={"categoria": "test"},
            ruta_salida="/custom/path",
            nombre_archivo="custom_name"
        )
        
        assert config.formato == "json"
        assert config.incluir_metadatos == False
        assert config.filtros["categoria"] == "test"
        assert config.ruta_salida == "/custom/path"
        assert config.nombre_archivo == "custom_name"

if __name__ == "__main__":
    pytest.main([__file__])