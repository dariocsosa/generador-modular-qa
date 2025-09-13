"""
Ejemplos básicos de uso del Generador Modular de Q&A
"""

import asyncio
import sys
from pathlib import Path

# Agregar ruta del proyecto
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.generators.prompt_generator import generate_qa_from_prompt
from src.extractors.document_processor import process_document_to_qa
from src.unifiers.data_unifier import QADataManager, ExportConfig

async def ejemplo_generacion_prompt():
    """Ejemplo de generación de Q&A por prompts"""
    print("🚀 Ejemplo: Generación por Prompts")
    
    # Generar Q&A sobre un tema específico
    batch = await generate_qa_from_prompt(
        prompt="Machine Learning en el sector salud",
        categoria="tecnologia",
        nivel="intermedio",
        num_preguntas=5,
        modelo="openai",  # Asegurar que tengas OPENAI_API_KEY configurada
        usar_busqueda=False
    )
    
    print(f"✅ Generadas {len(batch.items)} preguntas y respuestas")
    
    # Mostrar las primeras 2 preguntas
    for i, item in enumerate(batch.items[:2], 1):
        print(f"\n--- Q&A {i} ---")
        print(f"P: {item.pregunta}")
        print(f"R: {item.respuesta}")
        print(f"Categoría: {item.categoria} | Nivel: {item.nivel} | Confianza: {item.confianza:.2f}")
    
    return batch

async def ejemplo_procesamiento_documento():
    """Ejemplo de procesamiento de documentos (requiere documento de prueba)"""
    print("\n📄 Ejemplo: Procesamiento de Documentos")
    
    # Para este ejemplo, necesitarías un documento real
    documento_path = "data/documents/ejemplo.txt"
    
    # Crear documento de ejemplo si no existe
    if not Path(documento_path).exists():
        Path(documento_path).parent.mkdir(parents=True, exist_ok=True)
        with open(documento_path, "w", encoding="utf-8") as f:
            f.write("""
            Inteligencia Artificial en Medicina
            
            La inteligencia artificial (IA) está transformando el sector de la salud de múltiples maneras.
            Los algoritmos de machine learning pueden analizar imágenes médicas con una precisión comparable
            o superior a la de los especialistas humanos.
            
            Los sistemas de IA también pueden ayudar en el diagnóstico predictivo, analizando grandes
            cantidades de datos de pacientes para identificar patrones que pueden indicar el riesgo
            de ciertas enfermedades.
            
            Sin embargo, la implementación de IA en medicina también presenta desafíos éticos y
            regulatorios que deben ser cuidadosamente considerados.
            """)
        print(f"📝 Documento de ejemplo creado en: {documento_path}")
    
    # Procesar documento
    try:
        batch = await process_document_to_qa(
            file_path=documento_path,
            categoria="medicina",
            nivel="intermedio",
            preguntas_por_chunk=3,
            modelo="openai"
        )
        
        print(f"✅ Procesado documento: {len(batch.items)} Q&A extraídos")
        
        # Mostrar algunos resultados
        for i, item in enumerate(batch.items[:2], 1):
            print(f"\n--- Q&A Documento {i} ---")
            print(f"P: {item.pregunta}")
            print(f"R: {item.respuesta}")
        
        return batch
        
    except Exception as e:
        print(f"❌ Error procesando documento: {e}")
        return None

def ejemplo_unificacion_exportacion(batches):
    """Ejemplo de unificación y exportación de datos"""
    print("\n💾 Ejemplo: Unificación y Exportación")
    
    # Crear data manager
    manager = QADataManager()
    
    # Agregar batches (filtrar None)
    batches_validos = [batch for batch in batches if batch is not None]
    if batches_validos:
        for batch in batches_validos:
            manager.add_data(batch)
        
        # Obtener estadísticas
        stats = manager.get_summary()
        print(f"📊 Estadísticas totales:")
        print(f"  - Total items: {stats['total_items']}")
        print(f"  - Categorías: {list(stats['distribucion_categorias'].keys())}")
        print(f"  - Confianza promedio: {stats['confianza_promedio']:.2f}")
        
        # Exportar a CSV
        config_csv = ExportConfig(
            formato="csv",
            incluir_metadatos=True,
            nombre_archivo="ejemplo_qa_export"
        )
        
        try:
            output_path = manager.process_and_export(config_csv)
            print(f"✅ Datos exportados a: {output_path}")
        except Exception as e:
            print(f"❌ Error exportando: {e}")
        
        # Exportar a JSON
        config_json = ExportConfig(
            formato="json",
            incluir_metadatos=True,
            nombre_archivo="ejemplo_qa_export"
        )
        
        try:
            output_path_json = manager.process_and_export(config_json)
            print(f"✅ Datos exportados a JSON: {output_path_json}")
        except Exception as e:
            print(f"❌ Error exportando JSON: {e}")
    
    else:
        print("⚠️ No hay batches válidos para procesar")

async def main():
    """Función principal que ejecuta todos los ejemplos"""
    print("🤖 Ejemplos de uso del Generador Modular de Q&A\n")
    
    batches = []
    
    # Ejemplo 1: Generación por prompt
    try:
        batch_prompt = await ejemplo_generacion_prompt()
        batches.append(batch_prompt)
    except Exception as e:
        print(f"❌ Error en ejemplo de prompt: {e}")
        batches.append(None)
    
    # Ejemplo 2: Procesamiento de documento
    try:
        batch_doc = await ejemplo_procesamiento_documento()
        batches.append(batch_doc)
    except Exception as e:
        print(f"❌ Error en ejemplo de documento: {e}")
        batches.append(None)
    
    # Ejemplo 3: Unificación y exportación
    ejemplo_unificacion_exportacion(batches)
    
    print("\n🎉 Ejemplos completados!")

if __name__ == "__main__":
    # Verificar configuración básica
    from config.settings import settings
    
    api_status = settings.validate_api_keys()
    if not any(api_status.values()):
        print("⚠️ ADVERTENCIA: No hay API keys configuradas.")
        print("Configura al menos una API key en el archivo .env para ejecutar los ejemplos.")
        print("\nEjemplo de configuración .env:")
        print("OPENAI_API_KEY=tu_clave_aqui")
        exit(1)
    
    # Ejecutar ejemplos
    asyncio.run(main())