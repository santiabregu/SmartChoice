# Sistema de Búsqueda - Documentación

Este documento explica en detalle cómo funciona nuestro sistema de búsqueda de reseñas de productos.

## Tipos de Búsqueda

El sistema implementa dos tipos principales de búsqueda:

### 1. Búsqueda Booleana

```json
{
  "query": "auriculares AND (bateria OR duracion)",
  "search_type": "boolean"
}
```

#### Proceso de búsqueda booleana:
1. **Normalización de la consulta**
   - Espaciado correcto alrededor de operadores
   - Manejo de paréntesis
   - Normalización de caracteres españoles

2. **Procesamiento de términos**
   - Búsqueda de término exacto
   - Búsqueda de forma normalizada (sin acentos)
   - Búsqueda de stem (raíz de la palabra)
   - Búsqueda de sinónimos

3. **Aplicación de operadores**
   - AND: intersección de conjuntos
   - OR: unión de conjuntos
   - NOT: diferencia de conjuntos

### 2. Búsqueda por Similitud (TF-IDF)

```json
{
  "query": "auriculares batería duración autonomía",
  "search_type": "tf_idf"
}
```

#### Proceso de búsqueda TF-IDF:
1. **Procesamiento de la consulta**
   - Tokenización
   - Stemming
   - Eliminación de stopwords

2. **Cálculo de pesos TF-IDF mejorado**
   - Factor de boost por frecuencia en la consulta
   - Boost adicional para términos importantes:
     ```python
     term_importance = {
         'auricular': 2.0,  # Término principal del producto
         'bateria': 1.5,    # Característica importante
         'bueno': 1.2,      # Calificador de calidad
         'tecnologia': 1.1  # Categoría relevante
     }
     ```
   - IDF mejorado para términos discriminativos

3. **Ranking de resultados**
   - Cálculo de similitud con cada documento
   - Ordenamiento por score de similitud

## Características Especiales

### 1. Normalización de Texto
- Conversión a minúsculas
- Eliminación de acentos
- Manejo de caracteres especiales españoles
- Eliminación de stopwords

### 2. Sistema de Sinónimos
```python
sinonimos = {
    'auricular': ['auriculares', 'cascos', 'headphones', 'audifonos'],
    'bateria': ['batería', 'pila', 'duración', 'autonomía', 'dura'],
    'bueno': ['buena', 'excelente', 'genial', 'impresionante', 'útil'],
    'sonido': ['audio', 'acústica', 'calidad'],
    'precio': ['costo', 'valor', 'económico'],
    'comodidad': ['cómodo', 'ergonómico', 'confortable'],
    'tecnologia': ['tecnología', 'tech', 'dispositivo', 'electrónico']
}
```

### 3. Métricas de Evaluación

#### Para búsqueda booleana:
- Precisión: fracción de documentos recuperados que son relevantes
- Recall: fracción de documentos relevantes que fueron recuperados
- F1-score: media armónica entre precisión y recall

#### Para búsqueda por ranking:
- MAP (Mean Average Precision)
- Precisión@k
- Recall
- Métricas por consulta y globales

## Ejemplos de Uso

### Búsqueda Booleana
```http
POST http://localhost:8000/search
Content-Type: application/json

{
    "query": "auriculares AND (bateria OR duracion)",
    "search_type": "boolean"
}
```

### Búsqueda por Similitud
```http
POST http://localhost:8000/search
Content-Type: application/json

{
    "query": "auriculares con buena batería",
    "search_type": "tf_idf"
}
```

## Evaluación de Búsquedas
El sistema permite evaluar las búsquedas usando necesidades de información predefinidas:

```http
POST http://localhost:8000/evaluate_search
Content-Type: application/json

{
    "necesidad_id": "N1",
    "search_type": "boolean"  // o "tf_idf"
}
```

Esto retorna métricas detalladas sobre la efectividad de la búsqueda para esa necesidad específica. 