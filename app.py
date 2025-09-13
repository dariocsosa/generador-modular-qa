"""
Aplicación Streamlit para el Generador Modular de Q&A
Interfaz principal para la generación, visualización y exportación de Q&A
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, List, Any
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import settings
from src.utils.logger import get_logger
from src.utils.data_models import QAItem, QABatch, GenerationRequest, ExportConfig
from src.generators.prompt_generator import PromptQAGenerator, generate_qa_from_prompt
from src.extractors.document_processor import DocumentQAProcessor, process_document_to_qa
from src.unifiers.data_unifier import QADataManager

# Configurar página
st.set_page_config(
    page_title="Generador Modular Q&A",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

logger = get_logger(__name__)

class QAGeneratorApp:
    """Clase principal de la aplicación Streamlit"""
    
    def __init__(self):
        self.data_manager = QADataManager()
        self.prompt_generator = PromptQAGenerator()
        self.document_processor = DocumentQAProcessor()
        
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
                st.stop()
            
            modelo = st.selectbox(
                "Proveedor de IA",
                available_providers,
                index=0 if available_providers else None
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
            num_preguntas = st.slider("Número de preguntas", 1, 50, 10)
            usar_busqueda = st.checkbox(
                "Usar búsqueda avanzada",
                help="Usa Perplexity para información actualizada"
            )
        
        if st.button("🚀 Generar Q&A desde Prompt", type="primary", disabled=not prompt_text):
            with st.spinner("Generando Q&A..."):
                try:
                    # Crear request
                    request = GenerationRequest(
                        tipo="prompt",
                        prompt=prompt_text,
                        categoria=config["categoria"],
                        nivel=config["nivel"],
                        num_preguntas=num_preguntas,
                        modelo=config["modelo"],
                        idioma=config["idioma"],
                        usar_busqueda_avanzada=usar_busqueda
                    )
                    
                    # Generar Q&A (ejecutar función async)
                    batch = asyncio.run(self.prompt_generator.generate_qa_batch(request))
                    
                    # Guardar en session state
                    st.session_state.qa_data.append(batch)
                    st.session_state.current_batch = batch
                    
                    st.success(f"✅ Generadas {len(batch.items)} preguntas y respuestas!")
                    
                except Exception as e:
                    st.error(f"Error generando Q&A: {str(e)}")
                    logger.error(f"Error en generación por prompt: {e}")
    
    def render_document_processor(self, config: Dict[str, Any]):
        """Renderizar sección de procesamiento de documentos"""
        st.header("📄 Procesamiento de Documentos")
        
        # Upload de archivo
        uploaded_file = st.file_uploader(
            "Sube tu documento",
            type=["pdf", "docx", "txt", "md"],
            help="Formatos soportados: PDF, DOCX, TXT, MD"
        )
        
        if uploaded_file:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Archivo:** {uploaded_file.name}")
                st.write(f"**Tamaño:** {uploaded_file.size / 1024:.1f} KB")
            
            with col2:
                st.write("**Configuración:**")
                preguntas_por_chunk = st.slider("Preguntas por sección", 1, 10, 3)
                extraer_existente = st.checkbox(
                    "Extraer Q&A existentes",
                    value=True,
                    help="Buscar Q&A que ya estén en el documento"
                )
            
            if st.button("📝 Procesar Documento", type="primary"):
                with st.spinner("Procesando documento..."):
                    try:
                        # Guardar archivo temporalmente
                        temp_path = settings.DOCUMENTS_DIR / uploaded_file.name
                        with open(temp_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        
                        # Procesar documento
                        batch = asyncio.run(
                            self.document_processor.process_document(
                                str(temp_path),
                                categoria=config["categoria"],
                                nivel=config["nivel"],
                                preguntas_por_chunk=preguntas_por_chunk,
                                modelo=config["modelo"],
                                extraer_existente=extraer_existente
                            )
                        )
                        
                        # Limpiar archivo temporal
                        temp_path.unlink(missing_ok=True)
                        
                        # Guardar en session state
                        st.session_state.qa_data.append(batch)
                        st.session_state.current_batch = batch
                        
                        st.success(f"✅ Procesado documento: {len(batch.items)} Q&A extraídos!")
                        
                    except Exception as e:
                        st.error(f"Error procesando documento: {str(e)}")
                        logger.error(f"Error en procesamiento de documento: {e}")
    
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
        
        # Filtros
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            categorias = list(set(item.categoria for item in all_items))
            categoria_filter = st.selectbox("Filtrar por categoría", ["Todas"] + categorias)
        
        with col2:
            niveles = list(set(item.nivel for item in all_items))
            nivel_filter = st.selectbox("Filtrar por nivel", ["Todos"] + niveles)
        
        with col3:
            confianza_min = st.slider("Confianza mínima", 0.0, 1.0, 0.0)
        
        with col4:
            busqueda = st.text_input("Buscar en preguntas/respuestas")
        
        # Aplicar filtros
        filtered_items = all_items.copy()
        
        if categoria_filter != "Todas":
            filtered_items = [item for item in filtered_items if item.categoria == categoria_filter]
        
        if nivel_filter != "Todos":
            filtered_items = [item for item in filtered_items if item.nivel == nivel_filter]
        
        filtered_items = [item for item in filtered_items if item.confianza >= confianza_min]
        
        if busqueda:
            busqueda_lower = busqueda.lower()
            filtered_items = [
                item for item in filtered_items 
                if busqueda_lower in item.pregunta.lower() or busqueda_lower in item.respuesta.lower()
            ]
        
        st.write(f"**Mostrando {len(filtered_items)} de {len(all_items)} elementos**")
        
        # Mostrar items
        for i, item in enumerate(filtered_items):
            with st.expander(f"Q{i+1}: {item.pregunta[:100]}{'...' if len(item.pregunta) > 100 else ''}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**🤔 Pregunta:** {item.pregunta}")
                    st.markdown(f"**💡 Respuesta:** {item.respuesta}")
                
                with col2:
                    st.markdown(f"**📂 Categoría:** {item.categoria}")
                    st.markdown(f"**📈 Nivel:** {item.nivel}")
                    st.markdown(f"**🎯 Confianza:** {item.confianza:.2f}")
                    st.markdown(f"**🗓️ Creado:** {item.fecha_creacion.strftime('%Y-%m-%d %H:%M')}")
                    
                    if item.fuentes:
                        st.markdown(f"**📚 Fuentes:** {', '.join(item.fuentes[:2])}{'...' if len(item.fuentes) > 2 else ''}")
    
    def render_statistics(self):
        """Renderizar estadísticas"""
        # Combinar todos los items
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
        
        # Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribución por categoría
            categoria_counts = {}
            for item in all_items:
                categoria_counts[item.categoria] = categoria_counts.get(item.categoria, 0) + 1
            
            if categoria_counts:
                fig_cat = px.pie(
                    values=list(categoria_counts.values()),
                    names=list(categoria_counts.keys()),
                    title="Distribución por Categoría"
                )
                st.plotly_chart(fig_cat, use_container_width=True)
        
        with col2:
            # Distribución por nivel
            nivel_counts = {}
            for item in all_items:
                nivel_counts[item.nivel] = nivel_counts.get(item.nivel, 0) + 1
            
            if nivel_counts:
                fig_nivel = px.bar(
                    x=list(nivel_counts.keys()),
                    y=list(nivel_counts.values()),
                    title="Distribución por Nivel"
                )
                st.plotly_chart(fig_nivel, use_container_width=True)
        
        # Histograma de confianza
        confianzas = [item.confianza for item in all_items]
        fig_conf = px.histogram(
            x=confianzas,
            nbins=20,
            title="Distribución de Niveles de Confianza"
        )
        st.plotly_chart(fig_conf, use_container_width=True)
    
    def render_data_management(self):
        """Renderizar gestión de datos"""
        st.subheader("🗂️ Gestión de Datos")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Acciones de Datos:**")
            
            if st.button("🔄 Fusionar Duplicados", help="Elimina elementos muy similares"):
                if st.session_state.qa_data:
                    # Agregar todos los batches al data manager
                    self.data_manager.unifier.batches = []
                    self.data_manager.unifier.unified_items = []
                    
                    for batch in st.session_state.qa_data:
                        self.data_manager.add_data(batch)
                    
                    # Fusionar duplicados
                    merged_count = self.data_manager.unifier.merge_similar_items()
                    st.success(f"Fusionados {merged_count} elementos duplicados")
            
            if st.button("🗑️ Limpiar Todo", type="secondary"):
                st.session_state.qa_data = []
                st.session_state.current_batch = None
                st.success("Datos limpiados")
                st.rerun()
        
        with col2:
            st.write("**Información de Batches:**")
            
            for i, batch in enumerate(st.session_state.qa_data):
                with st.expander(f"Batch {i+1} - {batch.origen} ({len(batch.items)} items)"):
                    st.json({
                        "ID": batch.id,
                        "Origen": batch.origen,
                        "Items": len(batch.items),
                        "Fecha": batch.fecha_creacion.strftime("%Y-%m-%d %H:%M:%S"),
                        "Estadísticas": batch.get_stats()
                    })
    
    def render_export_section(self):
        """Renderizar sección de exportación"""
        if not st.session_state.qa_data:
            st.info("No hay datos para exportar. Genera algunos Q&A primero.")
            return
        
        st.header("💾 Exportación de Datos")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Configuración de exportación
            formato = st.selectbox(
                "Formato de exportación",
                ["csv", "json", "xlsx", "yaml"]
            )
            
            incluir_metadatos = st.checkbox("Incluir metadatos", value=True)
            
            nombre_archivo = st.text_input(
                "Nombre del archivo (opcional)",
                placeholder="qa_export_personalizado"
            )
        
        with col2:
            st.write("**Vista previa:**")
            total_items = sum(len(batch.items) for batch in st.session_state.qa_data)
            st.metric("Items a exportar", total_items)
            st.write(f"**Formato:** {formato.upper()}")
            st.write(f"**Incluir metadatos:** {'Sí' if incluir_metadatos else 'No'}")
        
        if st.button("📤 Exportar Datos", type="primary"):
            with st.spinner("Exportando datos..."):
                try:
                    # Preparar data manager
                    self.data_manager.unifier.batches = []
                    self.data_manager.unifier.unified_items = []
                    
                    for batch in st.session_state.qa_data:
                        self.data_manager.add_data(batch)
                    
                    # Configurar exportación
                    export_config = ExportConfig(
                        formato=formato,
                        incluir_metadatos=incluir_metadatos,
                        nombre_archivo=nombre_archivo if nombre_archivo else None
                    )
                    
                    # Exportar
                    output_path = self.data_manager.process_and_export(export_config)
                    
                    # Guardar en historial
                    st.session_state.export_history.append({
                        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "archivo": output_path,
                        "formato": formato,
                        "items": total_items
                    })
                    
                    st.success(f"✅ Datos exportados exitosamente: `{output_path}`")
                    
                    # Mostrar botón de descarga si es posible
                    if os.path.exists(output_path):
                        with open(output_path, "rb") as file:
                            btn = st.download_button(
                                label="⬇️ Descargar archivo",
                                data=file.read(),
                                file_name=os.path.basename(output_path),
                                mime="application/octet-stream"
                            )
                    
                except Exception as e:
                    st.error(f"Error exportando datos: {str(e)}")
                    logger.error(f"Error en exportación: {e}")
        
        # Historial de exportaciones
        if st.session_state.export_history:
            st.subheader("📋 Historial de Exportaciones")
            df_history = pd.DataFrame(st.session_state.export_history)
            st.dataframe(df_history, use_container_width=True)
    
    def run(self):
        """Ejecutar la aplicación principal"""
        self.render_header()
        config = self.render_sidebar()
        
        # Pestañas principales
        tab1, tab2, tab3, tab4 = st.tabs([
            "💭 Generar por Prompt",
            "📄 Procesar Documentos", 
            "📋 Ver Q&A",
            "💾 Exportar"
        ])
        
        with tab1:
            self.render_prompt_generator(config)
        
        with tab2:
            self.render_document_processor(config)
        
        with tab3:
            self.render_qa_viewer()
        
        with tab4:
            self.render_export_section()

# Ejecutar aplicación
if __name__ == "__main__":
    app = QAGeneratorApp()
    app.run()