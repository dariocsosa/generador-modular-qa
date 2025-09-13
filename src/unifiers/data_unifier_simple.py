"""
Sistema unificador y exportador de datos Q&A - Versión Simple
Maneja múltiples fuentes, formatos y exportación sin dependencias complejas
"""

import csv
import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import pandas as pd

from config.settings import settings
from src.utils.simple_logger import get_logger
from src.utils.data_models import QAItem, QABatch, ExportConfig

logger = get_logger(__name__)

class QADataUnifier:
    """Unificador de datos Q&A de múltiples fuentes"""
    
    def __init__(self):
        self.batches: List[QABatch] = []
        self.unified_items: List[QAItem] = []
    
    def add_batch(self, batch: QABatch):
        """Agregar un batch al unificador"""
        self.batches.append(batch)
        self.unified_items.extend(batch.items)
        logger.info(f"Batch agregado: {len(batch.items)} items. Total: {len(self.unified_items)}")
    
    def add_batches(self, batches: List[QABatch]):
        """Agregar múltiples batches"""
        for batch in batches:
            self.add_batch(batch)
    
    def merge_similar_items(self, similarity_threshold: float = 0.8) -> int:
        """Fusionar elementos similares para eliminar duplicados"""
        # Implementación básica basada en similitud de texto
        from difflib import SequenceMatcher
        
        merged_items = []
        merged_count = 0
        
        for item in self.unified_items:
            is_duplicate = False
            
            # Comparar con items ya procesados
            for existing_item in merged_items:
                question_sim = SequenceMatcher(
                    None, 
                    item.pregunta.lower().strip(), 
                    existing_item.pregunta.lower().strip()
                ).ratio()
                
                answer_sim = SequenceMatcher(
                    None, 
                    item.respuesta.lower().strip(), 
                    existing_item.respuesta.lower().strip()
                ).ratio()
                
                # Si son muy similares, fusionar
                if question_sim > similarity_threshold or answer_sim > similarity_threshold:
                    # Fusionar metadatos y fuentes
                    existing_item.fuentes.extend(item.fuentes)
                    existing_item.fuentes = list(set(existing_item.fuentes))  # Eliminar duplicados
                    
                    # Fusionar palabras clave
                    existing_item.palabras_clave.extend(item.palabras_clave)
                    existing_item.palabras_clave = list(set(existing_item.palabras_clave))
                    
                    # Usar la respuesta más larga si es significativamente diferente
                    if len(item.respuesta) > len(existing_item.respuesta) * 1.2:
                        existing_item.respuesta = item.respuesta
                    
                    # Promediar confianza
                    existing_item.confianza = (existing_item.confianza + item.confianza) / 2
                    
                    merged_count += 1
                    is_duplicate = True
                    break
            
            # Si no es duplicado, agregar como nuevo
            if not is_duplicate:
                merged_items.append(item)
        
        self.unified_items = merged_items
        logger.info(f"Fusionados {merged_count} elementos duplicados. Quedan: {len(self.unified_items)}")
        
        return merged_count
    
    def filter_items(self, filters: Dict[str, Any]) -> List[QAItem]:
        """Filtrar elementos según criterios"""
        filtered_items = self.unified_items.copy()
        
        # Filtrar por categoría
        if 'categoria' in filters and filters['categoria']:
            categoria = filters['categoria'].lower()
            filtered_items = [item for item in filtered_items if item.categoria.lower() == categoria]
        
        # Filtrar por nivel
        if 'nivel' in filters and filters['nivel']:
            nivel = filters['nivel'].lower()
            filtered_items = [item for item in filtered_items if item.nivel.lower() == nivel]
        
        # Filtrar por tema
        if 'tema' in filters and filters['tema']:
            tema = filters['tema'].lower()
            filtered_items = [item for item in filtered_items if tema in item.tema.lower()]
        
        # Filtrar por confianza mínima
        if 'confianza_minima' in filters and filters['confianza_minima']:
            min_conf = float(filters['confianza_minima'])
            filtered_items = [item for item in filtered_items if item.confianza >= min_conf]
        
        logger.info(f"Filtrado aplicado: {len(filtered_items)}/{len(self.unified_items)} elementos")
        return filtered_items
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas del conjunto unificado"""
        if not self.unified_items:
            return {"total": 0}
        
        # Estadísticas básicas
        stats = {
            "total_items": len(self.unified_items),
            "total_batches": len(self.batches),
        }
        
        # Distribución por categoría
        categorias = {}
        niveles = {}
        temas = {}
        idiomas = {}
        origenes = {}
        
        for item in self.unified_items:
            # Categorías
            categorias[item.categoria] = categorias.get(item.categoria, 0) + 1
            
            # Niveles
            niveles[item.nivel] = niveles.get(item.nivel, 0) + 1
            
            # Temas
            if item.tema:
                temas[item.tema] = temas.get(item.tema, 0) + 1
            
            # Idiomas
            idiomas[item.idioma] = idiomas.get(item.idioma, 0) + 1
        
        # Orígenes de los batches
        for batch in self.batches:
            origenes[batch.origen] = origenes.get(batch.origen, 0) + len(batch.items)
        
        stats.update({
            "distribucion_categorias": categorias,
            "distribucion_niveles": niveles,
            "distribucion_temas": dict(sorted(temas.items(), key=lambda x: x[1], reverse=True)[:10]),
            "distribucion_idiomas": idiomas,
            "distribucion_origenes": origenes,
            "confianza_promedio": sum(item.confianza for item in self.unified_items) / len(self.unified_items),
        })
        
        return stats

class QAExporter:
    """Exportador de datos Q&A a diferentes formatos"""
    
    def __init__(self):
        self.supported_formats = ['csv', 'json', 'xlsx', 'yaml']
    
    def prepare_export_data(self, items: List[QAItem], include_metadata: bool = True) -> List[Dict[str, Any]]:
        """Preparar datos para exportación"""
        export_data = []
        
        for item in items:
            row = {
                "id": item.id,
                "pregunta": item.pregunta,
                "respuesta": item.respuesta,
                "categoria": item.categoria,
                "nivel": item.nivel,
                "tema": item.tema,
                "idioma": item.idioma,
                "confianza": item.confianza,
                "fecha_creacion": item.fecha_creacion.isoformat(),
                "fuentes": "|".join(item.fuentes) if item.fuentes else "",
                "palabras_clave": "|".join(item.palabras_clave) if item.palabras_clave else ""
            }
            
            if include_metadata and item.metadatos:
                # Agregar metadatos como columnas adicionales
                for key, value in item.metadatos.items():
                    row[f"meta_{key}"] = str(value)
            
            export_data.append(row)
        
        return export_data
    
    def export_to_csv(self, items: List[QAItem], file_path: str, include_metadata: bool = True):
        """Exportar a formato CSV"""
        data = self.prepare_export_data(items, include_metadata)
        
        if not data:
            logger.warning("No hay datos para exportar")
            return
        
        # Obtener todas las columnas posibles
        all_columns = set()
        for row in data:
            all_columns.update(row.keys())
        
        columns = sorted(all_columns)
        
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=columns)
            writer.writeheader()
            writer.writerows(data)
        
        logger.info(f"Exportado a CSV: {file_path} ({len(data)} elementos)")
    
    def export_to_json(self, items: List[QAItem], file_path: str, include_metadata: bool = True):
        """Exportar a formato JSON"""
        data = self.prepare_export_data(items, include_metadata)
        
        export_structure = {
            "metadata": {
                "total_items": len(data),
                "export_date": datetime.now().isoformat(),
                "format_version": "1.0"
            },
            "qa_items": data
        }
        
        with open(file_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(export_structure, jsonfile, ensure_ascii=False, indent=2)
        
        logger.info(f"Exportado a JSON: {file_path} ({len(data)} elementos)")
    
    def export(self, items: List[QAItem], config: ExportConfig):
        """Exportar usando configuración específica"""
        # Determinar ruta de archivo
        if config.ruta_salida:
            output_path = Path(config.ruta_salida)
        else:
            output_path = settings.OUTPUT_DIR
        
        # Crear nombre de archivo si no se especifica
        if config.nombre_archivo:
            filename = config.nombre_archivo
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"qa_export_{timestamp}.{config.formato}"
        
        # Asegurar que la ruta tenga la extensión correcta
        if not filename.endswith(f".{config.formato}"):
            filename += f".{config.formato}"
        
        full_path = output_path / filename
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Exportar según formato
        if config.formato == "csv":
            self.export_to_csv(items, str(full_path), config.incluir_metadatos)
        elif config.formato == "json":
            self.export_to_json(items, str(full_path), config.incluir_metadatos)
        else:
            raise ValueError(f"Formato no soportado: {config.formato}")
        
        return str(full_path)

class QADataManager:
    """Manager principal para unificación y exportación de datos Q&A"""
    
    def __init__(self):
        self.unifier = QADataUnifier()
        self.exporter = QAExporter()
    
    def add_data(self, data: Union[QABatch, List[QABatch], List[QAItem]]):
        """Agregar datos al manager"""
        if isinstance(data, QABatch):
            self.unifier.add_batch(data)
        elif isinstance(data, list):
            if all(isinstance(item, QABatch) for item in data):
                self.unifier.add_batches(data)
            elif all(isinstance(item, QAItem) for item in data):
                # Crear batch temporal para los items individuales
                temp_batch = QABatch(
                    items=data,
                    origen="manual",
                    parametros_generacion={"added_manually": True}
                )
                self.unifier.add_batch(temp_batch)
        else:
            raise ValueError("Tipo de datos no soportado")
    
    def process_and_export(
        self,
        export_config: ExportConfig,
        remove_duplicates: bool = True,
        similarity_threshold: float = 0.8
    ) -> str:
        """Procesar datos y exportar"""
        
        # Eliminar duplicados si se solicita
        if remove_duplicates:
            self.unifier.merge_similar_items(similarity_threshold)
        
        # Aplicar filtros
        items_to_export = self.unifier.filter_items(export_config.filtros)
        
        # Exportar
        output_path = self.exporter.export(items_to_export, export_config)
        
        logger.info(f"Procesamiento y exportación completados: {output_path}")
        return output_path
    
    def get_summary(self) -> Dict[str, Any]:
        """Obtener resumen de los datos"""
        return self.unifier.get_statistics()