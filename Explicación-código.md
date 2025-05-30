# Explicación del Código - SmartChoice

## Estructura del Proyecto

```
SmartChoice/
├── src/
│   ├── preprocessing/       # Procesamiento de texto
│   ├── indexing/           # Sistemas de búsqueda
│   └── utils/              # Utilidades
├── backend/                # API REST
├── data/                   # Datos y corpus
└── docs/                   # Documentación
```

## Módulos Principales

### 1. Preprocesamiento (`src/preprocessing/`)

#### `text_cleaner.py`
- **Propósito**: Limpieza y normalización de texto en español
- **Funciones principales**:
  - `normalize_text()`: Elimina acentos y caracteres especiales
    ```python
    "México" -> "mexico"
    "café" -> "cafe"
    ```
  - `remove_special_chars()`: Elimina símbolos manteniendo letras y números
    ```python
    "¡Hola! ¿Qué tal?" -> "hola que tal"
    "precio: $299.99" -> "precio 299 99"
    ```
  - `clean_text()`: Aplica todas las limpiezas en secuencia

#### `tokenizer.py`
- **Propósito**: Tokenización específica para español
- **Funciones principales**:
  - `expand_contractions()`: Expande contracciones españolas
    ```python
    "del" -> "de el"
    "al" -> "a el"
    ```
  - `tokenize()`: Divide texto en tokens y elimina stopwords
  - `get_ngrams()`: Genera secuencias de n palabras
  - `analyze_tokens()`: Proporciona estadísticas de tokens

### 2. Sistemas de Búsqueda (`src/indexing/`)

#### `inverted_index.py`
- **Propósito**: Implementa búsqueda booleana
- **Características**:
  - Soporta operadores AND, OR, NOT
  - Búsqueda de frases exactas
  - Índice posicional para orden de palabras
- **Métodos principales**:
  ```python
  boolean_query("smartphone AND batería NOT lento")
  phrase_query("batería excelente")
  ```

#### `vector_space.py`
- **Propósito**: Implementa búsqueda por ranking
- **Características**:
  - Modelo TF-IDF
  - Similitud coseno
  - Ranking de resultados
- **Métodos principales**:
  - `build_model()`: Construye vectores TF-IDF
  - `search()`: Búsqueda por similitud

### 3. Procesamiento de Reseñas (`src/review_processor.py`)
- **Propósito**: Extracción de información estructurada
- **Funcionalidades**:
  ```python
  {
    "producto": "Smartphone XYZ",
    "categoría": "Tecnología",
    "reseña": "Este smartphone tiene...",
    "puntuación": 4.0
  }
  ```
- **Métodos principales**:
  - `extract_review_info()`: Extrae información de reseñas
  - `_infer_category()`: Detecta categoría por palabras clave
  - `save_review()`: Guarda en el corpus JSON

### 4. Interfaz CLI (`src/main.py`)
- **Propósito**: Interfaz de línea de comandos
- **Opciones**:
  1. Añadir nuevas reseñas
  2. Búsqueda booleana
  3. Búsqueda por texto libre
  4. Salir
- **Funciones principales**:
  - `add_reviews()`: Procesa nuevas reseñas
  - `boolean_search()`: Búsqueda con operadores
  - `ranked_search()`: Búsqueda por similitud

## Backend (API REST)

### Estructura
```
backend/
├── src/
│   ├── models/          # Esquemas de datos
│   ├── controllers/     # Lógica de negocio
│   ├── services/        # Servicios externos
│   └── routes/          # Rutas API
```

### Componentes Principales

#### 1. Modelos (`models/Review.ts`)
```typescript
interface IReview {
  producto: string;
  categoria: string;
  resena: string;
  puntuacion: number;
  sentimiento: ISentimentAnalysis;
  aspectos_clave: string[];
}
```

#### 2. Servicios (`services/deepseek.service.ts`)
- Integración con Deepseek para:
  - Procesamiento de reseñas
  - Análisis de sentimientos
  - Extracción de aspectos clave
  - Generación de sugerencias

#### 3. Controladores (`controllers/review.controller.ts`)
- **Endpoints**:
  - `POST /api/reviews/upload`: Sube y procesa reseñas
  - `GET /api/reviews/search`: Búsqueda de reseñas
  - `GET /api/reviews/stats`: Estadísticas del corpus

### Tecnologías Backend
- Node.js con TypeScript
- Express para API REST
- MongoDB para almacenamiento
- Deepseek API para procesamiento
- Multer para manejo de archivos

### Configuración
```bash
# Instalación
npm install

# Variables de entorno (.env)
MONGODB_URI=mongodb://localhost:27017/smartchoice
PORT=3000

# Desarrollo
npm run dev
```

## Diferencias entre Sistemas de Búsqueda

### Índice Invertido (Búsqueda Booleana)
- Búsquedas exactas con operadores
- Resultados binarios (coincide/no coincide)
- Ideal para búsquedas precisas

### Modelo Vectorial (Búsqueda por Ranking)
- Búsquedas por similitud
- Resultados ordenados por relevancia
- Ideal para consultas en lenguaje natural

## Ejemplo de Uso

```python
# Búsqueda booleana
results = index.boolean_query("smartphone AND batería NOT lento")

# Búsqueda por ranking
results = vector_model.search("busco un smartphone con buena batería")
```