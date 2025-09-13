"""
Script de inicio rápido para el Generador Modular de Q&A
Configura el entorno y ejecuta una demo básica
"""

import os
import sys
from pathlib import Path

def verificar_entorno():
    """Verificar que el entorno esté correctamente configurado"""
    print("🔍 Verificando configuración del entorno...")
    
    # Verificar Python version
    if sys.version_info < (3, 11):
        print(f"❌ Python 3.11+ requerido. Versión actual: {sys.version}")
        return False
    else:
        print(f"✅ Python {sys.version.split()[0]}")
    
    # Verificar dependencias críticas
    dependencias_criticas = [
        "streamlit", "openai", "anthropic", "google.generativeai", 
        "pydantic", "pandas", "plotly"
    ]
    
    dependencias_faltantes = []
    for dep in dependencias_criticas:
        try:
            __import__(dep.replace(".", "_") if "." in dep else dep)
            print(f"✅ {dep}")
        except ImportError:
            dependencias_faltantes.append(dep)
            print(f"❌ {dep} (faltante)")
    
    if dependencias_faltantes:
        print(f"\n📦 Para instalar dependencias faltantes:")
        print("pip install -r requirements.txt")
        return False
    
    # Verificar estructura de directorios
    directorios_requeridos = ["src", "config", "data", "data/documents", "data/output"]
    for directorio in directorios_requeridos:
        path = Path(directorio)
        if path.exists():
            print(f"✅ {directorio}/")
        else:
            print(f"❌ {directorio}/ (faltante)")
            path.mkdir(parents=True, exist_ok=True)
            print(f"  📁 Creado: {directorio}/")
    
    return True

def configurar_env():
    """Ayudar a configurar variables de entorno"""
    print("\n🔧 Configuración de Variables de Entorno...")
    
    env_file = Path(".env")
    
    if not env_file.exists():
        print("📝 Archivo .env no encontrado. Copiando desde .env.example...")
        example_file = Path(".env.example")
        if example_file.exists():
            import shutil
            shutil.copy(example_file, env_file)
            print("✅ Archivo .env creado")
        else:
            print("❌ .env.example no encontrado")
            return False
    
    # Verificar API keys
    from config.settings import settings
    api_status = settings.validate_api_keys()
    
    print("\n🔑 Estado de API Keys:")
    providers = {
        "OpenAI": api_status["openai"],
        "Anthropic (Claude)": api_status["anthropic"], 
        "Google (Gemini)": api_status["google"],
        "Perplexity": api_status["perplexity"]
    }
    
    configurado = False
    for provider, status in providers.items():
        if status:
            print(f"✅ {provider}")
            configurado = True
        else:
            print(f"❌ {provider} (no configurado)")
    
    if not configurado:
        print("\n⚠️ No hay API keys configuradas.")
        print("Edita el archivo .env y agrega al menos una API key:")
        print("  OPENAI_API_KEY=tu_clave_openai")
        print("  ANTHROPIC_API_KEY=tu_clave_anthropic")
        print("  GOOGLE_API_KEY=tu_clave_google")
        return False
    
    return True

async def demo_rapida():
    """Ejecutar una demostración rápida del sistema"""
    print("\n🚀 Demo Rápida del Sistema...")
    
    # Agregar ruta del proyecto
    sys.path.insert(0, str(Path(__file__).parent))
    
    try:
        from src.utils.data_models import QAItem, QABatch
        from src.unifiers.data_unifier import QADataManager, ExportConfig
        
        print("✅ Módulos importados correctamente")
        
        # Crear algunos Q&A de ejemplo
        qa_items = [
            QAItem(
                pregunta="¿Qué es Python?",
                respuesta="Python es un lenguaje de programación de alto nivel, interpretado e interactivo.",
                categoria="programacion",
                nivel="básico",
                tema="fundamentos",
                confianza=0.95
            ),
            QAItem(
                pregunta="¿Cuáles son las ventajas de Python?",
                respuesta="Python es fácil de aprender, tiene sintaxis clara, amplia biblioteca estándar y gran comunidad.",
                categoria="programacion", 
                nivel="básico",
                tema="ventajas",
                confianza=0.90
            )
        ]
        
        # Crear batch
        batch = QABatch(
            items=qa_items,
            origen="demo",
            parametros_generacion={"demo": True}
        )
        
        print(f"✅ Batch de demo creado con {len(batch.items)} elementos")
        
        # Probar data manager
        manager = QADataManager()
        manager.add_data(batch)
        
        # Obtener estadísticas
        stats = manager.get_summary()
        print(f"✅ Estadísticas generadas: {stats['total_items']} items")
        
        # Probar exportación
        config = ExportConfig(
            formato="csv",
            nombre_archivo="demo_quick_start"
        )
        
        output_path = manager.process_and_export(config)
        print(f"✅ Demo exportada a: {output_path}")
        
        print("\n🎉 Demo rápida completada exitosamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error en demo: {e}")
        return False

def mostrar_siguiente_pasos():
    """Mostrar los próximos pasos al usuario"""
    print("\n🎯 Próximos Pasos:")
    print("1. 🖥️  Ejecutar la aplicación web:")
    print("   streamlit run app.py")
    print("\n2. 🧪 Probar ejemplos básicos:")
    print("   python examples/basic_usage.py")
    print("\n3. 🚀 Probar ejemplos avanzados:")
    print("   python examples/advanced_usage.py")
    print("\n4. 🐳 Usar Docker (opcional):")
    print("   docker-compose up -d")
    print("\n5. 📚 Leer la documentación completa:")
    print("   README.md")
    
    print("\n💡 Consejos:")
    print("• Configura al menos una API key en .env para funcionalidad completa")
    print("• Sube documentos a data/documents/ para procesamiento")
    print("• Los archivos exportados se guardan en data/output/")
    print("• Revisa los logs en logs/ si tienes problemas")

def main():
    """Función principal del script de inicio rápido"""
    print("🤖 Generador Modular de Q&A - Inicio Rápido\n")
    
    # Verificar entorno
    if not verificar_entorno():
        print("\n❌ Entorno no configurado correctamente. Por favor corrige los errores.")
        return False
    
    # Configurar variables de entorno
    if not configurar_env():
        print("\n⚠️ Variables de entorno no configuradas completamente.")
        print("El sistema funcionará con funcionalidad limitada.")
    
    # Ejecutar demo rápida
    import asyncio
    demo_exitosa = asyncio.run(demo_rapida())
    
    if demo_exitosa:
        print("\n✅ Sistema configurado y funcionando correctamente!")
        mostrar_siguiente_pasos()
        
        # Preguntar si quiere iniciar la aplicación web
        try:
            respuesta = input("\n¿Quieres iniciar la aplicación web ahora? (s/n): ").lower().strip()
            if respuesta in ['s', 'si', 'y', 'yes']:
                print("🚀 Iniciando aplicación web...")
                os.system("streamlit run app.py")
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
    else:
        print("\n❌ Hay problemas en la configuración. Revisa los errores anteriores.")
    
    return demo_exitosa

if __name__ == "__main__":
    main()