"""
Ejemplos avanzados del Generador Modular de Q&A
Demuestra características avanzadas como filtrado, personalización y batch processing
"""

import asyncio
import sys
from pathlib import Path
from typing import List

# Agregar ruta del proyecto
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.data_models import QAItem, QABatch, GenerationRequest, ExportConfig
from src.generators.prompt_generator import PromptQAGenerator
from src.unifiers.data_unifier import QADataManager

async def ejemplo_generacion_multiple_temas():
    """Ejemplo de generación de Q&A para múltiples temas"""
    print("🎯 Ejemplo Avanzado: Generación Multi-Tema")
    
    generator = PromptQAGenerator()
    temas = [
        {"prompt": "Inteligencia Artificial en educación", "categoria": "educacion"},
        {"prompt": "Blockchain en finanzas", "categoria": "fintech"},
        {"prompt": "Medicina personalizada", "categoria": "medicina"},
        {"prompt": "Energías renovables", "categoria": "energia"}
    ]
    
    batches = []
    
    for tema in temas:
        print(f"  🔄 Generando Q&A para: {tema['prompt']}")
        
        request = GenerationRequest(
            tipo="prompt",
            prompt=tema["prompt"],
            categoria=tema["categoria"],
            nivel="intermedio",
            num_preguntas=3,
            modelo="openai",
            idioma="es",
            usar_busqueda_avanzada=False
        )
        
        try:
            batch = await generator.generate_qa_batch(request)
            batches.append(batch)
            print(f"    ✅ {len(batch.items)} Q&A generados")
        except Exception as e:
            print(f"    ❌ Error: {e}")
    
    return batches

def ejemplo_filtrado_avanzado(batches: List[QABatch]):
    """Ejemplo de filtrado avanzado de datos"""
    print("\n🔍 Ejemplo Avanzado: Filtrado Inteligente")
    
    # Crear data manager y agregar todos los batches
    manager = QADataManager()
    for batch in batches:
        manager.add_data(batch)
    
    total_items = len(manager.unifier.unified_items)
    print(f"📊 Total items antes del filtrado: {total_items}")
    
    # Filtro 1: Solo categoría "educacion"
    filtros_educacion = {"categoria": "educacion"}
    items_educacion = manager.unifier.filter_items(filtros_educacion)
    print(f"  🎓 Items de educación: {len(items_educacion)}")
    
    # Filtro 2: Confianza alta (>= 0.8)
    filtros_confianza = {"confianza_minima": 0.8}
    items_alta_confianza = manager.unifier.filter_items(filtros_confianza)
    print(f"  ⭐ Items con alta confianza: {len(items_alta_confianza)}")
    
    # Filtro 3: Búsqueda por palabras clave
    filtros_palabras = {"palabras_clave": ["artificial", "tecnología", "innovación"]}
    items_tech = manager.unifier.filter_items(filtros_palabras)
    print(f"  💻 Items relacionados con tecnología: {len(items_tech)}")
    
    # Filtro combinado
    filtros_combinados = {
        "categoria": "medicina",
        "confianza_minima": 0.7
    }
    items_medicina_confiable = manager.unifier.filter_items(filtros_combinados)
    print(f"  🏥 Items de medicina con buena confianza: {len(items_medicina_confiable)}")
    
    return manager

def ejemplo_estadisticas_detalladas(manager: QADataManager):
    """Ejemplo de análisis estadístico detallado"""
    print("\n📈 Ejemplo Avanzado: Análisis Estadístico")
    
    stats = manager.get_summary()
    
    print(f"📊 Resumen General:")
    print(f"  - Total elementos: {stats['total_items']}")
    print(f"  - Total batches: {stats['total_batches']}")
    print(f"  - Confianza promedio: {stats['confianza_promedio']:.3f}")
    print(f"  - Longitud promedio pregunta: {stats['longitud_pregunta_promedio']:.1f} caracteres")
    print(f"  - Longitud promedio respuesta: {stats['longitud_respuesta_promedio']:.1f} caracteres")
    
    print(f"\n🏷️ Distribución por Categorías:")
    for categoria, count in stats['distribucion_categorias'].items():
        porcentaje = (count / stats['total_items']) * 100
        print(f"  - {categoria}: {count} ({porcentaje:.1f}%)")
    
    print(f"\n📊 Distribución por Niveles:")
    for nivel, count in stats['distribucion_niveles'].items():
        porcentaje = (count / stats['total_items']) * 100
        print(f"  - {nivel}: {count} ({porcentaje:.1f}%)")
    
    print(f"\n🌍 Distribución por Idiomas:")
    for idioma, count in stats['distribucion_idiomas'].items():
        print(f"  - {idioma}: {count}")

def ejemplo_exportacion_personalizada(manager: QADataManager):
    """Ejemplo de exportación con configuraciones personalizadas"""
    print("\n💾 Ejemplo Avanzado: Exportación Personalizada")
    
    # Exportación 1: Solo datos de alta confianza en CSV
    config_premium = ExportConfig(
        formato="csv",
        incluir_metadatos=True,
        filtros={"confianza_minima": 0.85},
        nombre_archivo="qa_premium_quality"
    )
    
    try:
        output_premium = manager.process_and_export(config_premium)
        print(f"  ⭐ Exportado CSV premium: {output_premium}")
    except Exception as e:
        print(f"  ❌ Error en exportación premium: {e}")
    
    # Exportación 2: Datos de educación en JSON
    config_educacion = ExportConfig(
        formato="json",
        incluir_metadatos=True,
        filtros={"categoria": "educacion"},
        nombre_archivo="qa_educacion_especializado"
    )
    
    try:
        output_educacion = manager.process_and_export(config_educacion)
        print(f"  🎓 Exportado JSON educación: {output_educacion}")
    except Exception as e:
        print(f"  ❌ Error en exportación educación: {e}")
    
    # Exportación 3: Resumen en Excel con múltiples hojas
    config_excel = ExportConfig(
        formato="xlsx",
        incluir_metadatos=True,
        nombre_archivo="qa_reporte_completo"
    )
    
    try:
        output_excel = manager.process_and_export(config_excel)
        print(f"  📊 Exportado Excel completo: {output_excel}")
    except Exception as e:
        print(f"  ❌ Error en exportación Excel: {e}")

def ejemplo_qa_personalizado():
    """Ejemplo de creación manual de Q&A"""
    print("\n✍️ Ejemplo Avanzado: Q&A Manual")
    
    # Crear Q&A personalizados
    qa_items = [
        QAItem(
            pregunta="¿Cuáles son las principales ventajas de usar Docker en desarrollo?",
            respuesta="Docker ofrece portabilidad, consistencia entre entornos, aislamiento de aplicaciones y facilita el despliegue y escalamiento.",
            categoria="devops",
            nivel="intermedio",
            tema="containerización",
            palabras_clave=["docker", "containers", "devops"],
            confianza=0.95,
            metadatos={"creado_manual": True, "experto": "DevOps Engineer"}
        ),
        QAItem(
            pregunta="¿Qué es GraphQL y cómo se diferencia de REST?",
            respuesta="GraphQL es un lenguaje de consulta que permite a los clientes solicitar exactamente los datos que necesitan. A diferencia de REST, usa un único endpoint y permite consultas más flexibles.",
            categoria="desarrollo",
            nivel="avanzado",
            tema="APIs",
            palabras_clave=["graphql", "api", "rest"],
            confianza=0.90,
            metadatos={"creado_manual": True, "experto": "Backend Developer"}
        )
    ]
    
    # Crear batch manual
    batch_manual = QABatch(
        items=qa_items,
        origen="manual",
        parametros_generacion={"metodo": "creacion_experta", "revisor": "equipo_tecnico"}
    )
    
    print(f"✅ Creado batch manual con {len(batch_manual.items)} Q&A especializados")
    
    # Mostrar detalles
    for i, item in enumerate(batch_manual.items, 1):
        print(f"\n--- Q&A Manual {i} ---")
        print(f"P: {item.pregunta}")
        print(f"R: {item.respuesta[:100]}...")
        print(f"Categoría: {item.categoria} | Nivel: {item.nivel} | Confianza: {item.confianza}")
    
    return batch_manual

async def main():
    """Función principal que ejecuta todos los ejemplos avanzados"""
    print("🚀 Ejemplos Avanzados del Generador Modular de Q&A\n")
    
    # Ejemplo 1: Generación multi-tema
    batches_generados = await ejemplo_generacion_multiple_temas()
    
    # Ejemplo 2: Q&A manual
    batch_manual = ejemplo_qa_personalizado()
    batches_generados.append(batch_manual)
    
    # Ejemplo 3: Filtrado avanzado
    manager = ejemplo_filtrado_avanzado(batches_generados)
    
    # Ejemplo 4: Estadísticas detalladas
    ejemplo_estadisticas_detalladas(manager)
    
    # Ejemplo 5: Exportación personalizada
    ejemplo_exportacion_personalizada(manager)
    
    print("\n🎉 Todos los ejemplos avanzados completados!")
    print("\n📝 Revisa los archivos exportados en la carpeta 'data/output/'")

if __name__ == "__main__":
    # Verificar configuración
    from config.settings import settings
    
    api_status = settings.validate_api_keys()
    if not any(api_status.values()):
        print("⚠️ ADVERTENCIA: No hay API keys configuradas.")
        print("Los ejemplos de generación automática fallarán.")
        print("Solo se ejecutarán ejemplos que no requieren APIs externas.")
    
    # Ejecutar ejemplos
    asyncio.run(main())