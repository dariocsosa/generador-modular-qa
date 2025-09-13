"""
Script de inicio rápido para el Generador Modular de Q&A - Version Compatible
Configura el entorno y ejecuta una demo básica sin emojis para compatibilidad
"""

import os
import sys
from pathlib import Path

def verificar_entorno():
    """Verificar que el entorno esté correctamente configurado"""
    print("[INFO] Verificando configuracion del entorno...")
    
    # Verificar Python version
    if sys.version_info < (3, 9):
        print(f"[ERROR] Python 3.9+ requerido. Version actual: {sys.version}")
        return False
    else:
        print(f"[OK] Python {sys.version.split()[0]}")
    
    # Verificar dependencias críticas
    dependencias_criticas = [
        "streamlit", "pydantic", "pandas"
    ]
    
    dependencias_faltantes = []
    for dep in dependencias_criticas:
        try:
            __import__(dep.replace(".", "_") if "." in dep else dep)
            print(f"[OK] {dep}")
        except ImportError:
            dependencias_faltantes.append(dep)
            print(f"[ERROR] {dep} (faltante)")
    
    if dependencias_faltantes:
        print(f"\n[INFO] Para instalar dependencias faltantes:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def configurar_env():
    """Ayudar a configurar variables de entorno"""
    print("\n[INFO] Configuracion de Variables de Entorno...")
    
    env_file = Path(".env")
    
    if not env_file.exists():
        print("[INFO] Archivo .env no encontrado. Copiando desde .env.example...")
        example_file = Path(".env.example")
        if example_file.exists():
            import shutil
            shutil.copy(example_file, env_file)
            print("[OK] Archivo .env creado")
        else:
            print("[ERROR] .env.example no encontrado")
            return False
    
    return True

async def demo_rapida():
    """Ejecutar una demostración rápida del sistema"""
    print("\n[INFO] Demo Rapida del Sistema...")
    
    # Agregar ruta del proyecto
    sys.path.insert(0, str(Path(__file__).parent))
    
    try:
        from src.utils.data_models import QAItem, QABatch
        print("[OK] Modulos importados correctamente")
        
        # Crear algunos Q&A de ejemplo
        qa_items = [
            QAItem(
                pregunta="¿Qué es Python?",
                respuesta="Python es un lenguaje de programación de alto nivel, interpretado e interactivo.",
                categoria="programacion",
                nivel="básico",
                tema="fundamentos",
                confianza=0.95
            )
        ]
        
        # Crear batch
        batch = QABatch(
            items=qa_items,
            origen="manual",
            parametros_generacion={"demo": True}
        )
        
        print(f"[OK] Batch de demo creado con {len(batch.items)} elementos")
        print("\n[SUCCESS] Demo rapida completada exitosamente!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error en demo: {e}")
        return False

def mostrar_siguiente_pasos():
    """Mostrar los próximos pasos al usuario"""
    print("\n[INFO] Proximos Pasos:")
    print("1. Ejecutar la aplicacion web:")
    print("   streamlit run app.py")
    print("\n2. Probar ejemplos basicos:")
    print("   python examples/basic_usage.py")
    print("\n3. Usar Docker (opcional):")
    print("   docker-compose up -d")
    print("\n4. Leer la documentacion completa:")
    print("   README.md")

def main():
    """Función principal del script de inicio rápido"""
    print("=== Generador Modular de Q&A - Inicio Rapido ===\n")
    
    # Verificar entorno
    if not verificar_entorno():
        print("\n[ERROR] Entorno no configurado correctamente.")
        return False
    
    # Configurar variables de entorno
    if not configurar_env():
        print("\n[WARNING] Variables de entorno no configuradas completamente.")
    
    # Ejecutar demo rápida
    import asyncio
    demo_exitosa = asyncio.run(demo_rapida())
    
    if demo_exitosa:
        print("\n[SUCCESS] Sistema configurado y funcionando correctamente!")
        mostrar_siguiente_pasos()
    else:
        print("\n[ERROR] Hay problemas en la configuracion.")
    
    return demo_exitosa

if __name__ == "__main__":
    main()