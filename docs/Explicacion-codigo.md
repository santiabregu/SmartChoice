# Explicación del Código

## Estructura del Proyecto

```
backend/
└── src/
    └── python/
        ├── data/               # Datos y recursos
        │   ├── necesidades_informacion.json
        │   └── reviews/       # Reseñas en formato JSON
        ├── nltk_data/         # Datos de NLTK (stopwords, etc.)
        ├── text_service.py    # Servicio principal (FastAPI)
        ├── text_processor.py  # Procesamiento de texto y búsqueda
        ├── review_file_handler.py  # Manejo de archivos
        ├── evaluator.py       # Evaluación de búsquedas
        └── run_service.py     # Script de inicio
```

## Componentes Principales

### 1. TextService (`text_service.py`)
- **Propósito**: Servicio REST API con FastAPI
- **Endpoints**:
  ```python
  @app.post("/search")              # Búsqueda de reseñas
  @app.post("/process_review")      # Procesar nueva reseña
  @app.post("/evaluate_search")     # Evaluar una búsqueda
  @app.get("/evaluate_all")         # Evaluar todas las necesidades
  ```
- **Características**:
  - Manejo de errores HTTP
  - Validación de datos con Pydantic
  - Integración con otros componentes

### 2. TextProcessor (`text_processor.py`)
- **Propósito**: Núcleo del sistema de procesamiento y búsqueda
- **Funcionalidades principales**:
  ```python
  def process_text(text: str, doc_id: str = None) -> Dict:
      # Procesa texto y actualiza índice invertido
  
  def boolean_search(query: str, operator: str = 'AND') -> Set[str]:
      # Búsqueda booleana con operadores AND, OR, NOT
  
  def tf_idf_search(query: str) -> Dict[str, float]:
      # Búsqueda por similitud con ranking
  ```
- **Características**:
  - Índice invertido
  - Stemming español
  - Sistema de sinónimos
  - Normalización de texto
  - Cálculo TF-IDF mejorado

### 3. ReviewFileHandler (`review_file_handler.py`)
- **Propósito**: Gestión de archivos de reseñas
- **Métodos principales**:
  ```python
  def save_review(review_data: Dict) -> str:
      # Guarda una reseña en formato JSON
  
  def load_review(filename: str) -> Dict:
      # Carga una reseña desde archivo
  
  def search_reviews(query: str, search_type: str) -> List[Dict]:
      # Busca reseñas usando el sistema especificado
  ```
- **Características**:
  - Almacenamiento en JSON
  - Manejo de metadatos
  - Integración con TextProcessor

### 4. Evaluator (`evaluator.py`)
- **Propósito**: Evaluación del sistema de búsqueda
- **Métodos principales**:
  ```python
  def evaluate_boolean_search(search_results: Dict) -> Dict:
      # Evalúa búsquedas booleanas
  
  def evaluate_ranked_search(search_results: Dict) -> Dict:
      # Evalúa búsquedas con ranking
  ```
- **Métricas implementadas**:
  - Precisión
  - Recall
  - F1-score
  - MAP (Mean Average Precision)
  - Métricas por consulta y globales

## Flujo de Trabajo

### 1. Procesamiento de Reseñas
1. Se recibe una reseña vía API
2. Se procesa el texto (normalización, stemming)
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
     - Calcula similitud
     - Ordena por relevancia
3. Retorna resultados

### 3. Evaluación
1. Se carga una necesidad de información
2. Se ejecuta la búsqueda
3. Se comparan resultados con documentos relevantes
4. Se calculan métricas
5. Se retornan estadísticas

## Características Avanzadas

### 1. Normalización de Texto
```python
def normalize_text(self, text: str) -> str:
    # Minúsculas
    text = text.lower()
    # Normalizar caracteres españoles
    replacements = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'ü': 'u', 'ñ': 'n'
    }
    # ...
```

### 2. Sistema de Sinónimos
```python
sinonimos = {
    'auricular': ['auriculares', 'cascos', 'headphones'],
    'bateria': ['batería', 'pila', 'duración'],
    # ...
}
```

### 3. Mejoras TF-IDF
```python
# Boost por importancia de términos
term_importance = {
    'auricular': 2.0,
    'bateria': 1.5,
    'bueno': 1.2
}

# IDF mejorado
boost = 1.2  # Para términos raros
idf = boost * math.log(1 + (total_docs / (1 + doc_freq)))
```

## Uso del Sistema

### 1. Iniciar el Servicio
```bash
python run_service.py
```

### 2. Realizar Búsquedas
```http
POST http://localhost:8000/search
Content-Type: application/json

{
    "query": "auriculares AND (bateria OR duracion)",
    "search_type": "boolean"
}
```

### 3. Evaluar Resultados
```http
POST http://localhost:8000/evaluate_search
Content-Type: application/json

{
    "necesidad_id": "N1",
    "search_type": "boolean"
}
``` 