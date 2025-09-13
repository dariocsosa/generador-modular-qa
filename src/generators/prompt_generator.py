"""
Generador de Q&A basado en prompts temáticos
Soporta múltiples proveedores de LLM y búsqueda avanzada
"""

import asyncio
import re
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

import openai
import anthropic
import google.generativeai as genai
import requests

from config.settings import settings
from src.utils.logger import get_logger
from src.utils.data_models import QAItem, QABatch, GenerationRequest

logger = get_logger(__name__)

class LLMProvider(ABC):
    """Clase base para proveedores de LLM"""
    
    @abstractmethod
    async def generate_qa(self, prompt: str, **kwargs) -> str:
        """Generar Q&A usando el proveedor específico"""
        pass

class OpenAIProvider(LLMProvider):
    """Proveedor OpenAI/GPT"""
    
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY no configurada")
        openai.api_key = settings.OPENAI_API_KEY
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def generate_qa(self, prompt: str, **kwargs) -> str:
        """Generar Q&A usando OpenAI"""
        try:
            model = kwargs.get('model', settings.OPENAI_MODEL)
            max_tokens = kwargs.get('max_tokens', 3000)
            temperature = kwargs.get('temperature', 0.7)
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Eres un experto generador de preguntas y respuestas educativas."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generando Q&A con OpenAI: {e}")
            raise

class AnthropicProvider(LLMProvider):
    """Proveedor Anthropic/Claude"""
    
    def __init__(self):
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY no configurada")
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    async def generate_qa(self, prompt: str, **kwargs) -> str:
        """Generar Q&A usando Anthropic"""
        try:
            model = kwargs.get('model', settings.ANTHROPIC_MODEL)
            max_tokens = kwargs.get('max_tokens', 3000)
            temperature = kwargs.get('temperature', 0.7)
            
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text
        except Exception as e:
            logger.error(f"Error generando Q&A con Anthropic: {e}")
            raise

class GoogleProvider(LLMProvider):
    """Proveedor Google/Gemini"""
    
    def __init__(self):
        if not settings.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY no configurada")
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(settings.GOOGLE_MODEL)
    
    async def generate_qa(self, prompt: str, **kwargs) -> str:
        """Generar Q&A usando Google Gemini"""
        try:
            temperature = kwargs.get('temperature', 0.7)
            
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=3000,
            )
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            return response.text
        except Exception as e:
            logger.error(f"Error generando Q&A con Google: {e}")
            raise

class PerplexitySearch:
    """Cliente para búsqueda avanzada usando Perplexity API"""
    
    def __init__(self):
        self.api_key = settings.PERPLEXITY_API_KEY
        self.base_url = "https://api.perplexity.ai"
    
    async def search_topic(self, topic: str, language: str = "es") -> str:
        """Buscar información actualizada sobre un tema"""
        if not self.api_key:
            logger.warning("PERPLEXITY_API_KEY no configurada, saltando búsqueda avanzada")
            return ""
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            search_prompt = f"Proporciona información actualizada y detallada sobre: {topic}"
            if language == "es":
                search_prompt += " (responde en español)"
            
            payload = {
                "model": "llama-3.1-sonar-small-128k-online",
                "messages": [
                    {
                        "role": "user",
                        "content": search_prompt
                    }
                ]
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                logger.warning(f"Error en búsqueda Perplexity: {response.status_code}")
                return ""
                
        except Exception as e:
            logger.error(f"Error en búsqueda avanzada: {e}")
            return ""

class PromptQAGenerator:
    """Generador principal de Q&A basado en prompts"""
    
    def __init__(self):
        self.providers = {
            "openai": OpenAIProvider,
            "anthropic": AnthropicProvider,
            "google": GoogleProvider
        }
        self.perplexity_search = PerplexitySearch()
        
    def get_provider(self, provider_name: str) -> LLMProvider:
        """Obtener instancia del proveedor especificado"""
        if provider_name not in self.providers:
            raise ValueError(f"Proveedor no soportado: {provider_name}")
        
        try:
            return self.providers[provider_name]()
        except ValueError as e:
            logger.error(f"Error configurando proveedor {provider_name}: {e}")
            raise
    
    def create_prompt(self, request: GenerationRequest, additional_context: str = "") -> str:
        """Crear prompt optimizado para generación de Q&A"""
        
        # Construir el prompt base
        topic = request.tema or request.prompt
        category = request.categoria or "general"
        difficulty = request.nivel or "intermedio"
        language = request.idioma or "es"
        num_questions = request.num_preguntas or 10
        
        # Contexto adicional si hay búsqueda avanzada
        context_section = ""
        if additional_context:
            context_section = f"\n\nContexto adicional actualizado:\n{additional_context}\n"
        
        prompt = settings.DEFAULT_QA_PROMPT_TEMPLATE.format(
            topic=topic,
            category=category,
            difficulty=difficulty,
            language=language,
            num_questions=num_questions
        )
        
        return prompt + context_section
    
    def parse_qa_response(self, response: str, request: GenerationRequest) -> List[QAItem]:
        """Parsear respuesta del LLM y convertir a QAItems"""
        qa_items = []
        
        # Patrón para extraer Q&A usando el formato esperado
        pattern = r'PREGUNTA:\s*(.+?)\s*RESPUESTA:\s*(.+?)(?=PREGUNTA:|CATEGORIA:|$)'
        matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)
        
        # Si no funciona el patrón principal, intentar patrones alternativos
        if not matches:
            # Patrón alternativo más flexible
            alt_patterns = [
                r'(?:Q|P):\s*(.+?)\s*(?:A|R):\s*(.+?)(?=(?:Q|P):|$)',
                r'(\d+\.\s*.+?\?)\s*(.+?)(?=\d+\.|$)'
            ]
            
            for pattern in alt_patterns:
                matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)
                if matches:
                    break
        
        for i, (question, answer) in enumerate(matches):
            try:
                # Limpiar pregunta y respuesta
                question = question.strip().replace('\n', ' ')
                answer = answer.strip().replace('\n', ' ')
                
                # Remover marcadores de categoría/nivel/tema si están incluidos
                for marker in ['CATEGORIA:', 'NIVEL:', 'TEMA:', '---']:
                    answer = answer.split(marker)[0].strip()
                
                # Crear QAItem
                qa_item = QAItem(
                    pregunta=question,
                    respuesta=answer,
                    categoria=request.categoria or "general",
                    nivel=request.nivel or "intermedio",
                    tema=request.tema or request.prompt or "",
                    idioma=request.idioma or "es",
                    metadatos={
                        "modelo_usado": request.modelo,
                        "prompt_original": request.prompt,
                        "posicion_en_batch": i + 1
                    }
                )
                
                qa_items.append(qa_item)
                
            except Exception as e:
                logger.warning(f"Error procesando Q&A {i+1}: {e}")
                continue
        
        return qa_items
    
    async def generate_qa_batch(self, request: GenerationRequest) -> QABatch:
        """Generar un lote completo de Q&A"""
        logger.info(f"Generando Q&A batch: {request.dict()}")
        
        # Búsqueda avanzada si está habilitada
        additional_context = ""
        if request.usar_busqueda_avanzada and (request.tema or request.prompt):
            search_topic = request.tema or request.prompt
            logger.info(f"Realizando búsqueda avanzada para: {search_topic}")
            additional_context = await self.perplexity_search.search_topic(
                search_topic, request.idioma or "es"
            )
        
        # Crear prompt
        prompt = self.create_prompt(request, additional_context)
        
        # Obtener proveedor y generar
        provider = self.get_provider(request.modelo or "openai")
        response = await provider.generate_qa(prompt)
        
        # Parsear respuesta
        qa_items = self.parse_qa_response(response, request)
        
        # Crear batch
        batch = QABatch(
            items=qa_items,
            origen="prompt",
            prompt_original=request.prompt,
            parametros_generacion=request.dict(),
            estadisticas={}
        )
        
        # Calcular estadísticas
        batch.estadisticas = batch.get_stats()
        
        logger.info(f"Generado batch con {len(qa_items)} elementos")
        return batch

# Función de conveniencia para uso directo
async def generate_qa_from_prompt(
    prompt: str,
    categoria: str = "general",
    nivel: str = "intermedio",
    num_preguntas: int = 10,
    modelo: str = "openai",
    usar_busqueda: bool = False
) -> QABatch:
    """Función de conveniencia para generar Q&A desde prompt"""
    
    request = GenerationRequest(
        tipo="prompt",
        prompt=prompt,
        categoria=categoria,
        nivel=nivel,
        num_preguntas=num_preguntas,
        modelo=modelo,
        usar_busqueda_avanzada=usar_busqueda
    )
    
    generator = PromptQAGenerator()
    return await generator.generate_qa_batch(request)