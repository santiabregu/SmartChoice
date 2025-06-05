# Explicación del Código

## Estructura del Proyecto

```
backend/
└── src/
    └── python/
        ├── data/               # Datos y recursos
        │   ├── sinonimos.json  # Diccionario de sinónimos
        │   └── *.txt          # Archivos de reseñas
        ├── text_service.py     # Servicio principal (FastAPI)
        ├── text_processor.py   # Procesamiento de texto y búsqueda
        ├── review_file_handler.py  # Manejo de archivos
        ├── evaluator.py        # Evaluación de resultados
        ├── experiments.py      # Sistema de experimentación
        └── run_service.py      # Script de inicio
```

## Componentes Principales

### 1. TextService (text_service.py)

Clase principal que implementa el servicio REST API usando FastAPI.

#### Endpoints:
```python
@app.post("/search")         # Búsqueda de reseñas
@app.post("/process_review") # Procesar nueva reseña
@app.get("/statistics")      # Estadísticas del sistema
```

#### Modelos de Datos:
```python
class Website(BaseModel):
    nombre: str
    url: Optional[HttpUrl]

class SearchRequest(BaseModel):
    query: str
    search_type: str = 'tf_idf'
    operator: Optional[str] = 'AND'

class ScoreStats(BaseModel):
    min_score: float
    max_score: float
    mean_score: float
    median_score: float
    score_distribution: Dict[str, int]
    total_matches: int
    matches_by_category: Dict[str, int]

class SearchResponse(BaseModel):
    results: List[Dict]
    metrics: Optional[Dict]
    score_statistics: Optional[ScoreStats]
```

#### Características:
- Manejo de errores HTTP
- Validación de datos con Pydantic
- Integración con TextProcessor y ReviewFileHandler
- Respuestas JSON estructuradas

### 2. TextProcessor (text_processor.py)

Núcleo del sistema de procesamiento de texto y búsqueda.

#### Funcionalidades Principales:
```python
def process_text(text: str, doc_id: str = None) -> Dict:
    """
    Procesa texto y actualiza el índice invertido.
    - Normalización
    - Tokenización
    - Stemming
    - Expansión con sinónimos
    """

def boolean_search(query: str, operator: str = 'AND') -> Set[str]:
    """
    Búsqueda booleana con operadores AND, OR, NOT.
    Soporta paréntesis y expresiones complejas.
    """

def tf_idf_search(query: str) -> Dict[str, float]:
    """
    Búsqueda por similitud con ranking.
    Incorpora pesos por importancia y términos compuestos.
    """
```

#### Sistema de Pesos:
```python
# Sistema de pesos actualizado
term_importance = {
    # Términos de batería y duración (peso muy alto)
    'bateria': 3.0,
    'duracion': 3.0,
    'autonomia': 3.0,
    'horas': 2.5,
    'aguanta': 2.5,
    'dura': 2.5,
    
    # Términos de calidad y valoración
    'calidad': 2.5,
    'excelente': 2.3,
    'premium': 2.3,
    'profesional': 2.2,
    'bueno': 2.0,
    'alta gama': 2.0,
    
    # Características técnicas y de producto
    'cancelacion': 2.0,
    'sonido': 2.0,
    'audio': 2.0,
    'auricular': 1.8,
    'altavoz': 1.8,
    'smartphone': 1.8
}

# Términos compuestos con boost mejorado
compound_terms = {
    'duracion bateria': 3.5,
    'buena bateria': 3.5,
    'larga duracion': 3.5,
    'autonomia bateria': 3.5,
    'calidad sonido': 2.8,
    'cancelacion ruido': 2.8,
    'alta gama': 2.5,
    'smart home': 2.3,
    'carga rapida': 2.2
}

# Penalizaciones actualizadas
penalty_terms = {
    'malo': 0.5,
    'defectuoso': 0.5,
    'roto': 0.5,
    'fallo': 0.5,
    'problema': 0.6,
    'negativo': 0.6
}
```

#### Parámetros de Evaluación:
```python
# Umbrales optimizados
similarity_threshold = 0.05  # Umbral mínimo de score
high_threshold = 0.20       # Umbral para documentos muy relevantes
feedback_threshold = 0.07   # Umbral para pseudo-relevance feedback

# Parámetros de evaluación
top_k = 2                  # Número de documentos top para relevancia
expansion_enabled = True    # Control de expansión de sinónimos
```

#### Nuevas Características:
- **Sistema de pesos mejorado**:
  - Categorización detallada de términos
  - Pesos optimizados por tipo de característica
  - Mayor énfasis en términos de batería y duración
  
- **Mejoras en búsqueda**:
  - Umbrales optimizados basados en experimentos
  - Control granular de expansión de sinónimos
  - Detección mejorada de términos compuestos
  
- **Evaluación refinada**:
  - Nuevo sistema de pseudo-relevance feedback
  - Umbrales adaptativos según tipo de consulta
  - Métricas expandidas de evaluación

- **Categorías expandidas**:
  - Nuevas categorías de productos
  - Características específicas por nicho
  - Términos técnicos especializados

### 3. ReviewFileHandler (review_file_handler.py)

Gestiona el almacenamiento y recuperación de reseñas.

#### Métodos Principales:
```python
def save_review(review_data: Dict) -> str:
    """
    Guarda una reseña en formato JSON.
    Retorna el ID asignado.
    """

def load_review(filename: str) -> Dict:
    """
    Carga una reseña desde archivo.
    Retorna los datos de la reseña.
    """

def search_reviews(query: str, search_type: str) -> List[Dict]:
    """
    Busca reseñas usando el sistema especificado.
    Integra con TextProcessor para la búsqueda.
    """

def get_statistics(self) -> Dict:
    """
    Calcula estadísticas sobre las reseñas almacenadas.
    """
```

### 4. Evaluator (evaluator.py)

Sistema de evaluación de resultados de búsqueda.

#### Métodos Principales:
```python
def evaluate_boolean_search(self, search_results: Dict) -> Dict:
    """
    Evalúa resultados de búsqueda booleana.
    Calcula precisión, recall y F1.
    """

def evaluate_ranked_search(self, search_results: Dict, query_terms: Dict = None) -> Dict:
    """
    Evalúa resultados de búsqueda con ranking.
    Calcula MAP y otras métricas.
    """

def calculate_average_precision(self, ranked_docs: List[str], relevant_docs: Set[str]) -> float:
    """
    Calcula la precisión media para resultados ordenados.
    """
```

#### Características:
- Evaluación de precisión y recall
- Cálculo de F1-score
- Evaluación de ranking (MAP)
- Umbral de similitud configurable

### 5. ExperimentRunner (experiments.py)

Sistema de experimentación y evaluación del sistema.

#### Métodos Principales:
```python
def run_timing_experiments(self, queries: List[str], search_type: str) -> Dict:
    """
    Mide tiempos de ejecución para diferentes consultas.
    """

def measure_execution_time(self, func, *args, **kwargs) -> Tuple[any, float]:
    """
    Mide el tiempo de ejecución de una función.
    """

def process_search_results(self, results) -> List[Dict]:
    """
    Procesa y estabiliza resultados de búsqueda.
    """
```

#### Características:
- Medición de tiempos de ejecución
- Procesamiento de resultados
- Generación de estadísticas
- Almacenamiento de resultados en JSON

## Flujo de Trabajo

### 1. Procesamiento de Reseñas
1. Se recibe una reseña vía API
2. Se procesa el texto:
   - Normalización (minúsculas, acentos)
   - Tokenización
   - Eliminación de stopwords
   - Stemming
   - Expansión con sinónimos
3. Se actualiza el índice invertido
4. Se guarda en archivo JSON

### 2. Búsqueda
1. Se recibe una consulta vía API
2. Según el tipo:
   - **Booleana**: 
     - Procesa operadores
     - Busca en índice invertido
     - Aplica operaciones de conjuntos
   - **TF-IDF**:
     - Procesa y expande la consulta
     - Aplica pesos por importancia
     - Detecta términos compuestos
     - Calcula similitud
     - Aplica boosts y penalizaciones
     - Ordena por relevancia
3. Retorna resultados filtrados por umbral

### 3. Evaluación y Experimentación
1. Medición de tiempos de ejecución
2. Evaluación de precisión y recall
3. Cálculo de métricas de ranking
4. Generación de estadísticas
5. Almacenamiento de resultados

## Ejemplo de Uso

### 1. Búsqueda TF-IDF
```http
POST http://localhost:8000/search
Content-Type: application/json

{
    "query": "auriculares con buena batería",
    "search_type": "tf_idf"
}
```

### 2. Respuesta del Sistema
```json
{
    "results": [
        {
            "id": "1",
            "producto": "Auriculares Sony WH-1000XM4",
            "categoria": "Tecnología",
            "resena": "Excelente calidad de sonido y batería dura más de 20 horas...",
            "puntuacion": 4.5,
            "score": 0.85
        }
    ]
}
```

## Características Avanzadas

### 1. Normalización de Texto
```python
def normalize_text(self, text: str) -> str:
    # Minúsculas
    text = text.lower()
    
    # Normalizar caracteres españoles
    replacements = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'ü': 'u', 'ñ': 'n', 'à': 'a', 'è': 'e', 'ì': 'i',
        'ò': 'o', 'ù': 'u'
    }
    return text
```

### 2. Sistema de Sinónimos
```python
sinonimos = {
    'auriculares': ['cascos', 'audífonos', 'headphones', 'earbuds'],
    'batería': ['autonomía', 'duración', 'pila'],
    'sonido': ['audio', 'acústica', 'reproducción'],
    'calidad': ['excelente', 'superior', 'premium', 'buena']
}
``` 