"""
Aplicación Streamlit simplificada para el Generador Modular de Q&A
Versión compatible sin dependencias complejas de logging
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, List, Any
import streamlit as st
import pandas as pd

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import settings
from src.utils.data_models import QAItem, QABatch, GenerationRequest, ExportConfig
from src.unifiers.data_unifier_simple import QADataManager

# Configurar página
st.set_page_config(
    page_title="Generador Modular Q&A",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

class SimpleQAGeneratorApp:
    """Clase principal de la aplicación Streamlit simplificada"""
    
    def __init__(self):
        self.data_manager = QADataManager()
        
        # Inicializar session state
        if "qa_data" not in st.session_state:
            st.session_state.qa_data = []
        if "current_batch" not in st.session_state:
            st.session_state.current_batch = None
        if "export_history" not in st.session_state:
            st.session_state.export_history = []
    
    def render_header(self):
        """Renderizar header principal"""
        st.title("🤖 Generador Modular de Q&A")
        st.markdown("**Genera preguntas y respuestas a partir de prompts temáticos o documentos**")
        
        # Validar APIs
        api_status = settings.validate_api_keys()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            status_icon = "✅" if api_status["openai"] else "❌"
            st.metric("OpenAI", status_icon)
        with col2:
            status_icon = "✅" if api_status["anthropic"] else "❌"
            st.metric("Anthropic", status_icon)
        with col3:
            status_icon = "✅" if api_status["google"] else "❌"
            st.metric("Google", status_icon)
        with col4:
            status_icon = "✅" if api_status["perplexity"] else "❌"
            st.metric("Perplexity", status_icon)
        
        st.divider()
    
    def render_sidebar(self):
        """Renderizar sidebar con configuración"""
        with st.sidebar:
            st.header("⚙️ Configuración")
            
            # Configuración de modelo
            st.subheader("Modelo de IA")
            available_providers = []
            api_status = settings.validate_api_keys()
            
            if api_status["openai"]:
                available_providers.append("openai")
            if api_status["anthropic"]:
                available_providers.append("anthropic")
            if api_status["google"]:
                available_providers.append("google")
            
            if not available_providers:
                st.error("⚠️ No hay APIs configuradas. Configura al menos una API key.")
                available_providers = ["demo"]  # Modo demo
            
            modelo = st.selectbox(
                "Proveedor de IA",
                available_providers,
                index=0
            )
            
            # Configuración de generación
            st.subheader("Configuración de Generación")
            
            categoria = st.text_input("Categoría", value="general")
            nivel = st.selectbox(
                "Nivel de dificultad",
                ["básico", "intermedio", "avanzado"],
                index=1
            )
            idioma = st.selectbox(
                "Idioma",
                ["es", "en"],
                index=0
            )
            
            # Estadísticas actuales
            if st.session_state.qa_data:
                st.subheader("📊 Datos Actuales")
                total_items = sum(len(batch.items) for batch in st.session_state.qa_data)
                st.metric("Total Q&A", total_items)
                st.metric("Batches", len(st.session_state.qa_data))
            
            return {
                "modelo": modelo,
                "categoria": categoria,
                "nivel": nivel,
                "idioma": idioma
            }
    
    def create_demo_qa(self, config: Dict[str, Any], num_preguntas: int = 5):
        """Crear Q&A de demostración cuando no hay APIs configuradas"""
        demo_questions = [
            {
                "pregunta": "¿Qué es la inteligencia artificial?",
                "respuesta": "La inteligencia artificial es una rama de la informática que busca crear sistemas capaces de realizar tareas que normalmente requieren inteligencia humana.",
                "tema": "fundamentos_ia"
            },
            {
                "pregunta": "¿Cuáles son los tipos de machine learning?",
                "respuesta": "Los principales tipos son: aprendizaje supervisado, no supervisado, semi-supervisado y por refuerzo.",
                "tema": "machine_learning"
            },
            {
                "pregunta": "¿Qué es el procesamiento de lenguaje natural?",
                "respuesta": "Es una rama de la IA que se enfoca en la interacción entre computadoras y el lenguaje humano natural.",
                "tema": "nlp"
            },
            {
                "pregunta": "¿Cómo funciona una red neuronal?",
                "respuesta": "Las redes neuronales procesan información a través de capas de nodos interconectados que imitan el funcionamiento básico de las neuronas.",
                "tema": "redes_neuronales"
            },
            {
                "pregunta": "¿Qué aplicaciones tiene la IA en la vida cotidiana?",
                "respuesta": "La IA se usa en asistentes virtuales, recomendaciones en streaming, navegación GPS, reconocimiento de voz y detección de fraude.",
                "tema": "aplicaciones_ia"
            }
        ]
        
        qa_items = []
        for i, item in enumerate(demo_questions[:num_preguntas]):
            qa_item = QAItem(
                pregunta=item["pregunta"],
                respuesta=item["respuesta"],
                categoria=config["categoria"],
                nivel=config["nivel"],
                tema=item["tema"],
                idioma=config["idioma"],
                confianza=0.85,
                metadatos={
                    "modo": "demo",
                    "generado": "sistema_demo"
                }
            )
            qa_items.append(qa_item)
        
        batch = QABatch(
            items=qa_items,
            origen="manual",
            parametros_generacion={
                "modo": "demo",
                "num_preguntas": num_preguntas,
                **config
            }
        )
        
        return batch
    
    def render_prompt_generator(self, config: Dict[str, Any]):
        """Renderizar sección de generación por prompts"""
        st.header("💭 Generación por Prompts Temáticos")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            prompt_text = st.text_area(
                "Describe el tema para generar Q&A:",
                height=100,
                placeholder="Ej: Inteligencia artificial en medicina, Historia de Colombia, Programación en Python..."
            )
        
        with col2:
            st.write("**Configuración:**")
            num_preguntas = st.slider("Número de preguntas", 1, 10, 5)
            if config["modelo"] != "demo":
                usar_busqueda = st.checkbox(
                    "Usar búsqueda avanzada",
                    help="Usa Perplexity para información actualizada"
                )
            else:
                usar_busqueda = False
                st.info("Modo demo activado")
        
        if st.button("🚀 Generar Q&A desde Prompt", type="primary", disabled=not prompt_text):
            with st.spinner("Generando Q&A..."):
                try:
                    if config["modelo"] == "demo":
                        # Modo demo
                        batch = self.create_demo_qa(config, num_preguntas)
                        st.session_state.qa_data.append(batch)
                        st.session_state.current_batch = batch
                        st.success(f"✅ Generadas {len(batch.items)} preguntas y respuestas! (Modo Demo)")
                    else:
                        st.error("Funcionalidad con API requiere configurar las API keys en el archivo .env")
                        st.info("Para probar sin APIs, usa el modo demo automático.")
                    
                except Exception as e:
                    st.error(f"Error generando Q&A: {str(e)}")
    
    def render_manual_input(self, config: Dict[str, Any]):
        """Renderizar entrada manual de Q&A"""
        st.header("✍️ Entrada Manual de Q&A")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            with st.form("manual_qa_form"):
                pregunta = st.text_area("Pregunta:", height=100)
                respuesta = st.text_area("Respuesta:", height=150)
                tema_custom = st.text_input("Tema específico (opcional):")
                
                submitted = st.form_submit_button("Agregar Q&A")
                
                if submitted and pregunta and respuesta:
                    try:
                        qa_item = QAItem(
                            pregunta=pregunta,
                            respuesta=respuesta,
                            categoria=config["categoria"],
                            nivel=config["nivel"],
                            tema=tema_custom or "manual",
                            idioma=config["idioma"],
                            confianza=1.0,  # Máxima confianza para entrada manual
                            metadatos={"entrada": "manual", "usuario": "local"}
                        )
                        
                        # Crear batch o agregar a existente
                        batch = QABatch(
                            items=[qa_item],
                            origen="manual",
                            parametros_generacion={"entrada": "manual"}
                        )
                        
                        st.session_state.qa_data.append(batch)
                        st.success("✅ Q&A agregado exitosamente!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error agregando Q&A: {str(e)}")
        
        with col2:
            st.write("**Instrucciones:**")
            st.write("• Pregunta debe tener al menos 10 caracteres")
            st.write("• Respuesta debe tener al menos 20 caracteres")
            st.write("• El tema es opcional pero recomendado")
            st.write("• Se asignará máxima confianza (1.0)")
    
    def render_qa_viewer(self):
        """Renderizar visualizador de Q&A"""
        if not st.session_state.qa_data:
            st.info("👆 Genera algunos Q&A usando las opciones de arriba para visualizarlos aquí.")
            return
        
        st.header("📋 Visualización de Q&A Generados")
        
        # Tabs para diferentes vistas
        tab1, tab2, tab3 = st.tabs(["🔍 Explorar", "📊 Estadísticas", "⚙️ Gestión"])
        
        with tab1:
            self.render_qa_explorer()
        
        with tab2:
            self.render_statistics()
        
        with tab3:
            self.render_data_management()
    
    def render_qa_explorer(self):
        """Renderizar explorador de Q&A"""
        # Combinar todos los items
        all_items = []
        for batch in st.session_state.qa_data:
            all_items.extend(batch.items)
        
        if not all_items:
            return
        
        # Filtros simples
        col1, col2 = st.columns(2)
        
        with col1:
            categorias = list(set(item.categoria for item in all_items))
            categoria_filter = st.selectbox("Filtrar por categoría", ["Todas"] + categorias)
        
        with col2:
            busqueda = st.text_input("Buscar en preguntas/respuestas")
        
        # Aplicar filtros
        filtered_items = all_items.copy()
        
        if categoria_filter != "Todas":
            filtered_items = [item for item in filtered_items if item.categoria == categoria_filter]
        
        if busqueda:
            busqueda_lower = busqueda.lower()
            filtered_items = [
                item for item in filtered_items 
                if busqueda_lower in item.pregunta.lower() or busqueda_lower in item.respuesta.lower()
            ]
        
        st.write(f"**Mostrando {len(filtered_items)} de {len(all_items)} elementos**")
        
        # Mostrar items
        for i, item in enumerate(filtered_items):
            with st.expander(f"Q{i+1}: {item.pregunta[:80]}{'...' if len(item.pregunta) > 80 else ''}"):
                st.markdown(f"**🤔 Pregunta:** {item.pregunta}")
                st.markdown(f"**💡 Respuesta:** {item.respuesta}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**📂 Categoría:** {item.categoria}")
                    st.markdown(f"**📈 Nivel:** {item.nivel}")
                with col2:
                    st.markdown(f"**🎯 Confianza:** {item.confianza:.2f}")
                    st.markdown(f"**🏷️ Tema:** {item.tema}")
    
    def render_statistics(self):
        """Renderizar estadísticas simples"""
        all_items = []
        for batch in st.session_state.qa_data:
            all_items.extend(batch.items)
        
        if not all_items:
            return
        
        # Métricas generales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Q&A", len(all_items))
        with col2:
            st.metric("Batches", len(st.session_state.qa_data))
        with col3:
            avg_confidence = sum(item.confianza for item in all_items) / len(all_items)
            st.metric("Confianza Promedio", f"{avg_confidence:.2f}")
        with col4:
            categorias_unicas = len(set(item.categoria for item in all_items))
            st.metric("Categorías Únicas", categorias_unicas)
        
        # Distribuciones simples
        st.subheader("Distribución por Categoría")
        categoria_counts = {}
        for item in all_items:
            categoria_counts[item.categoria] = categoria_counts.get(item.categoria, 0) + 1
        
        df_cat = pd.DataFrame(list(categoria_counts.items()), columns=['Categoría', 'Cantidad'])
        st.bar_chart(df_cat.set_index('Categoría'))
    
    def render_data_management(self):
        """Renderizar gestión de datos"""
        st.subheader("🗂️ Gestión de Datos")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Acciones:**")
            
            if st.button("🗑️ Limpiar Todo", type="secondary"):
                st.session_state.qa_data = []
                st.session_state.current_batch = None
                st.success("Datos limpiados")
                st.rerun()
        
        with col2:
            st.write("**Información de Batches:**")
            
            for i, batch in enumerate(st.session_state.qa_data):
                st.write(f"**Batch {i+1}:** {batch.origen} ({len(batch.items)} items)")
    
    def render_export_section(self):
        """Renderizar sección de exportación"""
        if not st.session_state.qa_data:
            st.info("No hay datos para exportar. Genera algunos Q&A primero.")
            return
        
        st.header("💾 Exportación de Datos")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            formato = st.selectbox(
                "Formato de exportación",
                ["csv", "json"]
            )
            
            nombre_archivo = st.text_input(
                "Nombre del archivo (opcional)",
                placeholder="mi_qa_export"
            )
        
        with col2:
            st.write("**Vista previa:**")
            total_items = sum(len(batch.items) for batch in st.session_state.qa_data)
            st.metric("Items a exportar", total_items)
            st.write(f"**Formato:** {formato.upper()}")
        
        if st.button("📤 Exportar Datos", type="primary"):
            with st.spinner("Exportando datos..."):
                try:
                    # Preparar data manager
                    temp_manager = QADataManager()
                    for batch in st.session_state.qa_data:
                        temp_manager.add_data(batch)
                    
                    # Configurar exportación
                    export_config = ExportConfig(
                        formato=formato,
                        incluir_metadatos=True,
                        nombre_archivo=nombre_archivo if nombre_archivo else None
                    )
                    
                    # Exportar
                    output_path = temp_manager.process_and_export(export_config)
                    
                    st.success(f"✅ Datos exportados exitosamente: `{output_path}`")
                    
                    # Mostrar contenido del archivo exportado
                    if os.path.exists(output_path):
                        with open(output_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        
                        st.download_button(
                            label="⬇️ Descargar archivo",
                            data=content,
                            file_name=os.path.basename(output_path),
                            mime="text/plain" if formato == "csv" else "application/json"
                        )
                    
                except Exception as e:
                    st.error(f"Error exportando datos: {str(e)}")
    
    def run(self):
        """Ejecutar la aplicación principal"""
        self.render_header()
        config = self.render_sidebar()
        
        # Pestañas principales
        tab1, tab2, tab3, tab4 = st.tabs([
            "💭 Generar por Prompt",
            "✍️ Entrada Manual", 
            "📋 Ver Q&A",
            "💾 Exportar"
        ])
        
        with tab1:
            self.render_prompt_generator(config)
        
        with tab2:
            self.render_manual_input(config)
        
        with tab3:
            self.render_qa_viewer()
        
        with tab4:
            self.render_export_section()

# Ejecutar aplicación
if __name__ == "__main__":
    app = SimpleQAGeneratorApp()
    app.run()