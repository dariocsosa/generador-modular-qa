# 🤖 Generador Modular de Q&A

Un sistema completo y modular para generar preguntas y respuestas (Q&A) a partir de prompts temáticos y documentos, con soporte para múltiples modelos de IA y exportación a diversos formatos.

## ✨ Características Principales

### 🎯 Generación Múltiple
- **Generación por prompts**: Crea Q&A desde temas y descripciones textuales
- **Procesamiento de documentos**: Extrae Q&A de PDF, DOCX, TXT y MD
- **Búsqueda avanzada**: Integración con Perplexity para información actualizada

### 🤖 Soporte Multi-LLM
- **OpenAI GPT**: GPT-4, GPT-3.5-turbo
- **Anthropic Claude**: Claude-3-Sonnet, Claude-3-Haiku
- **Google Gemini**: Gemini-Pro
- **Configuración flexible**: Cambio dinámico entre proveedores

### 📊 Gestión Inteligente
- **Unificación de datos**: Combina múltiples fuentes en un formato estándar
- **Detección de duplicados**: Fusión inteligente de contenido similar
- **Filtrado avanzado**: Por categoría, nivel, confianza, fecha, etc.
- **Estadísticas detalladas**: Análisis completo de los datos generados

### 💾 Exportación Versátil
- **Múltiples formatos**: CSV, JSON, Excel, YAML
- **Metadatos incluidos**: Información completa de origen y generación
- **Descarga directa**: Desde la interfaz web

### 🖥️ Interfaz Intuitiva
- **Streamlit Web App**: Interfaz moderna y responsiva
- **Configuración en tiempo real**: Cambios dinámicos de configuración
- **Visualización rica**: Gráficos y estadísticas interactivas
- **Experiencia fluida**: Diseño centrado en el usuario

## 🚀 Inicio Rápido

### Requisitos Previos
- Python 3.11+
- Docker (opcional)
- API Keys de al menos uno de los proveedores soportados

### Instalación Local

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/tu-usuario/generador-modular-qa.git
   cd generador-modular-qa
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv venv
   
   # Windows
   venv\\Scripts\\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   
   # Descargar modelo de spaCy para español
   python -m spacy download es_core_news_sm
   ```

4. **Configurar variables de entorno**
   ```bash
   # Copiar archivo de configuración
   cp .env.example .env
   
   # Editar .env con tus API keys
   nano .env
   ```

5. **Ejecutar la aplicación**
   ```bash
   streamlit run app.py
   ```

   La aplicación estará disponible en `http://localhost:8501`

### Instalación con Docker

1. **Usando docker-compose (recomendado)**
   ```bash
   # Configurar variables de entorno
   cp .env.example .env
   nano .env
   
   # Ejecutar
   docker-compose up -d
   ```

2. **Docker manual**
   ```bash
   # Construir imagen
   docker build -t qa-generator .
   
   # Ejecutar contenedor
   docker run -p 8501:8501 -v $(pwd)/.env:/app/.env qa-generator
   ```

## 📖 Guía de Uso

### 1. Configuración de API Keys

Edita el archivo `.env` con tus claves de API:

```env
# Configurar al menos una API key
OPENAI_API_KEY=tu_clave_openai
ANTHROPIC_API_KEY=tu_clave_anthropic
GOOGLE_API_KEY=tu_clave_google
PERPLEXITY_API_KEY=tu_clave_perplexity

# Configuración opcional
DEFAULT_MODEL_PROVIDER=openai
MAX_QUESTIONS_PER_BATCH=50
DEFAULT_LANGUAGE=es
```

### 2. Generación por Prompts

```python
from src.generators.prompt_generator import generate_qa_from_prompt

# Generar Q&A desde un tema
batch = await generate_qa_from_prompt(
    prompt="Inteligencia artificial en medicina",
    categoria="tecnologia",
    nivel="intermedio",
    num_preguntas=10,
    modelo="openai",
    usar_busqueda=True
)
```

### 3. Procesamiento de Documentos

```python
from src.extractors.document_processor import process_document_to_qa

# Procesar documento PDF
batch = await process_document_to_qa(
    file_path="ruta/al/documento.pdf",
    categoria="educacion",
    nivel="avanzado",
    preguntas_por_chunk=5
)
```

### 4. Unificación y Exportación

```python
from src.unifiers.data_unifier import QADataManager, ExportConfig

# Crear manager y agregar datos
manager = QADataManager()
manager.add_data([batch1, batch2, batch3])

# Exportar a CSV
config = ExportConfig(formato="csv", incluir_metadatos=True)
output_path = manager.process_and_export(config)
```

## 🏗️ Estructura del Proyecto

```
generador-modular-qa/
├── 📁 src/                          # Código fuente principal
│   ├── 📁 generators/               # Generadores de Q&A
│   │   └── prompt_generator.py      # Generación por prompts + LLMs
│   ├── 📁 extractors/               # Extractores de documentos
│   │   └── document_processor.py    # Procesamiento de PDF/DOCX/TXT
│   ├── 📁 unifiers/                 # Unificadores y exportadores
│   │   └── data_unifier.py          # Gestión y exportación de datos
│   └── 📁 utils/                    # Utilidades compartidas
│       ├── data_models.py           # Modelos Pydantic
│       └── logger.py                # Sistema de logging
├── 📁 config/                       # Configuración
│   └── settings.py                  # Configuración central
├── 📁 data/                         # Datos del proyecto
│   ├── documents/                   # Documentos de entrada
│   └── output/                      # Archivos exportados
├── 📁 examples/                     # Ejemplos de uso
├── 📁 tests/                        # Tests unitarios
├── 📄 app.py                        # Aplicación Streamlit
├── 📄 requirements.txt              # Dependencias Python
├── 📄 Dockerfile                    # Imagen Docker
├── 📄 docker-compose.yml            # Orquestación Docker
└── 📄 README.md                     # Este archivo
```

## 🔧 API Reference

### Modelos de Datos Principales

#### QAItem
```python
class QAItem(BaseModel):
    pregunta: str              # La pregunta formulada
    respuesta: str             # La respuesta correspondiente
    categoria: str             # Categoría temática
    nivel: str                 # Nivel: básico, intermedio, avanzado
    tema: str                  # Tema específico
    fuentes: List[str]         # Fuentes de información
    confianza: float           # Nivel de confianza (0.0-1.0)
    idioma: str                # Idioma del contenido
    metadatos: Dict[str, Any]  # Metadatos adicionales
```

#### QABatch
```python
class QABatch(BaseModel):
    items: List[QAItem]              # Lista de elementos Q&A
    origen: str                      # prompt, documento, manual, api
    prompt_original: str             # Prompt usado (si aplica)
    documento_fuente: str            # Documento fuente (si aplica)
    parametros_generacion: Dict      # Parámetros de generación
    estadisticas: Dict               # Estadísticas del lote
```

### Funciones Principales

#### Generación por Prompt
```python
async def generate_qa_from_prompt(
    prompt: str,
    categoria: str = "general",
    nivel: str = "intermedio", 
    num_preguntas: int = 10,
    modelo: str = "openai",
    usar_busqueda: bool = False
) -> QABatch
```

#### Procesamiento de Documentos
```python
async def process_document_to_qa(
    file_path: str,
    categoria: str = "general",
    nivel: str = "intermedio",
    preguntas_por_chunk: int = 3,
    modelo: str = "openai"
) -> QABatch
```

## 🎨 Personalización

### Agregar Nuevo Proveedor de LLM

1. **Implementar interfaz base**
   ```python
   class NuevoProvider(LLMProvider):
       async def generate_qa(self, prompt: str, **kwargs) -> str:
           # Implementar lógica específica
           pass
   ```

2. **Registrar en el generador**
   ```python
   # En prompt_generator.py
   self.providers["nuevo"] = NuevoProvider
   ```

3. **Configurar API key**
   ```env
   # En .env
   NUEVO_API_KEY=tu_clave_api
   ```

### Personalizar Prompts

Modifica los templates en `config/settings.py`:

```python
CUSTOM_PROMPT_TEMPLATE = """
Tu prompt personalizado aquí...
Tema: {topic}
Nivel: {difficulty}
...
"""
```

### Agregar Nuevo Formato de Exportación

1. **Implementar método en QAExporter**
   ```python
   def export_to_nuevo_formato(self, items: List[QAItem], file_path: str):
       # Lógica de exportación
       pass
   ```

2. **Registrar formato**
   ```python
   self.supported_formats.append('nuevo_formato')
   ```

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Tests con coverage
pytest --cov=src tests/

# Tests específicos
pytest tests/test_generators.py -v
```

## 📊 Métricas y Monitoreo

El sistema incluye logging detallado y métricas:

- **Logs estructurados**: Con rotación automática
- **Métricas de rendimiento**: Tiempo de generación, tokens usados
- **Estadísticas de calidad**: Confianza, distribución por categorías
- **Análisis de datos**: Visualizaciones en Streamlit

## 🐳 Despliegue

### Producción Local
```bash
# Usando gunicorn para mejor rendimiento
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app
```

### Cloud Deployment

**Heroku**
```bash
git push heroku main
```

**Railway**
```bash
railway up
```

**Google Cloud Run**
```bash
gcloud run deploy --source .
```

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama feature (`git checkout -b feature/nueva-caracteristica`)
3. Commit tus cambios (`git commit -am 'Añadir nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Abre un Pull Request

### Directrices de Contribución

- **Código**: Seguir PEP 8, usar type hints
- **Documentación**: Documentar funciones públicas
- **Tests**: Incluir tests para nuevas funcionalidades
- **Commits**: Mensajes descriptivos en español

## 📈 Roadmap

### V1.1 - Mejoras de IA
- [ ] Soporte para LLaMA y modelos locales
- [ ] Fine-tuning automático basado en feedback
- [ ] Evaluación automática de calidad de Q&A

### V1.2 - Escalabilidad
- [ ] Procesamiento distribuido con Celery
- [ ] Base de datos PostgreSQL/MongoDB
- [ ] API REST completa

### V1.3 - Integraciones
- [ ] Plugin para WordPress/Drupal
- [ ] Integración con LMS (Moodle, Canvas)
- [ ] API para integración empresarial

## 🐛 Troubleshooting

### Problemas Comunes

**Error: "No module named 'src'"**
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

**Error: "API key not found"**
- Verificar que `.env` esté en la raíz del proyecto
- Confirmar que las variables tengan el formato correcto

**Streamlit no carga**
- Verificar puerto 8501 disponible
- Revisar logs en `logs/qa_generator.log`

**Docker no construye**
- Verificar Docker daemon activo
- Limpiar caché: `docker system prune -a`

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 👨‍💻 Autor

**Tu Nombre**
- GitHub: [@tu-usuario](https://github.com/tu-usuario)
- Email: tu.email@ejemplo.com
- LinkedIn: [Tu Perfil](https://linkedin.com/in/tu-perfil)

## 🙏 Agradecimientos

- OpenAI por GPT API
- Anthropic por Claude API
- Google por Gemini API
- Streamlit por el framework web
- Comunidad open source por las librerías utilizadas

---

⭐ **Si este proyecto te resulta útil, considera darle una estrella en GitHub**