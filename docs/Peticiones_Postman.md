# Guía de Consultas API

Esta guía detalla todas las peticiones disponibles en la API del sistema de búsqueda, con ejemplos para Postman.

## 1. Búsqueda de Reseñas

### Endpoint: POST /search

Realiza búsquedas en las reseñas usando diferentes métodos.

#### 1.1 Búsqueda TF-IDF (por defecto)

```http
POST http://localhost:8000/search
Content-Type: application/json

{
    "query": "auriculares con buena batería",
    "search_type": "tf_idf"
}
```

Respuesta:
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
        },
        {
            "id": "2",
            "producto": "Auriculares Bose QuietComfort",
            "categoria": "Tecnología",
            "resena": "Buena duración de batería, aproximadamente 15 horas...",
            "puntuacion": 4.0,
            "score": 0.72
        }
    ],
    "metrics": {
        "total_results": 2,
        "matches_by_category": {
            "Tecnología": 2
        },
        "rating_distribution": {
            "4-5": 2,
            "3-4": 0,
            "2-3": 0,
            "1-2": 0
        },
        "avg_rating": 4.25
    },
    "score_statistics": {
        "min_score": 0.72,
        "max_score": 0.85,
        "mean_score": 0.785,
        "median_score": 0.785,
        "score_distribution": {
            "0.0-0.1": 0,
            "0.1-0.2": 0,
            "0.2-0.3": 0,
            "0.3-0.4": 0,
            "0.4-0.5": 0,
            "0.5+": 2
        },
        "total_matches": 2,
        "matches_by_category": {
            "Tecnología": 2
        }
    }
}
```

#### 1.2 Búsqueda Booleana

```http
POST http://localhost:8000/search
Content-Type: application/json

{
    "query": "auriculares AND (bateria OR duracion) AND NOT malo",
    "search_type": "boolean",
    "operator": "AND"
}
```

Respuesta:
```json
{
    "results": [
        {
            "id": "1",
            "producto": "Auriculares Sony WH-1000XM4",
            "categoria": "Tecnología",
            "resena": "Excelente calidad de sonido y batería dura más de 20 horas...",
            "puntuacion": 4.5
        }
    ],
    "metrics": {
        "total_results": 1,
        "matches_by_category": {
            "Tecnología": 1
        },
        "rating_distribution": {
            "4-5": 1,
            "3-4": 0,
            "2-3": 0,
            "1-2": 0
        },
        "avg_rating": 4.5
    }
}
```

## 2. Evaluación de Búsquedas

### Endpoint: POST /evaluate_search

Evalúa una búsqueda para una necesidad de información específica.

```http
POST http://localhost:8000/evaluate_search
Content-Type: application/json

{
    "necesidad_id": "N1",
    "search_type": "tf_idf"
}
```

Respuesta:
```json
{
    "status": "success",
    "necesidad": {
        "id": "N1",
        "descripcion": "Encontrar auriculares con buena duración de batería",
        "consulta_booleana": "auriculares AND (bateria OR duracion)",
        "consulta_libre": "auriculares batería duración autonomía"
    },
    "results": [...],
    "metrics": {
        "precision": 0.75,
        "recall": 0.68,
        "f1": 0.71
    },
    "score_statistics": {...}
}
```

## 3. Experimentos

### Endpoint: POST /run_experiments

Ejecuta experimentos detallados para una necesidad específica.

```http
POST http://localhost:8000/run_experiments
Content-Type: application/json

{
    "necesidad_id": "N1"
}
```

Respuesta:
```json
{
    "status": "success",
    "results": {
        "necesidad": {
            "id": "N1",
            "descripcion": "Encontrar auriculares con buena duración de batería"
        },
        "timing": {
            "boolean_search": {
                "query": "auriculares AND (bateria OR duracion)",
                "time": 0.023,
                "num_results": 5
            },
            "tfidf_search": {
                "query": "auriculares batería duración autonomía",
                "time": 0.045,
                "num_results": 8
            }
        },
        "synonyms": {...},
        "thresholds": {...}
    }
}
```

## 4. Evaluación Global

### Endpoint: GET /evaluate_all

Evalúa todas las necesidades de información usando tf-idf.

```http
GET http://localhost:8000/evaluate_all
```

Respuesta:
```json
{
    "status": "success",
    "evaluacion": {
        "per_necesidad": {
            "N1": {
                "descripcion": "Encontrar auriculares con buena duración de batería",
                "metricas": {
                    "precision": 0.75,
                    "recall": 0.68,
                    "f1": 0.71
                }
            }
        },
        "overall": {
            "map": 0.82,
            "precision": 0.75,
            "recall": 0.70
        }
    }
}
```

## 5. Estadísticas del Sistema

### Endpoint: GET /statistics

Obtiene estadísticas generales del sistema.

```http
GET http://localhost:8000/statistics
```

Respuesta:
```json
{
    "status": "success",
    "statistics": {
        "total_reviews": 50,
        "avg_rating": 4.2,
        "categories": {
            "Tecnología": 30,
            "Audio": 15,
            "Accesorios": 5
        },
        "websites": {
            "Amazon": 25,
            "MediaMarkt": 15,
            "PCComponentes": 10
        }
    }
}
```

## 6. Notas Importantes

1. **Umbrales**:
   - Score mínimo para resultados TF-IDF: 0.01
   - Los resultados se ordenan por score descendente

2. **Procesamiento de Texto**:
   - Las consultas se normalizan (minúsculas, sin acentos)
   - Se eliminan stopwords
   - Se aplica stemming
   - Se expanden sinónimos

3. **Límites**:
   - Máximo de 1000 caracteres por consulta
   - Máximo de 5000 caracteres por reseña
   - Máximo de 100 resultados por búsqueda 

## 4. Gestión de Necesidades de Información

### 4.1 Crear Nueva Necesidad

Endpoint para añadir una nueva necesidad de información al sistema.

```http
POST http://localhost:8000/needs/create
Content-Type: application/json

{
    "id": "N001",
    "descripcion": "Buscar reseñas de auriculares con buena calidad de sonido y batería duradera",
    "consulta": "auriculares calidad sonido bateria",
    "documentos_relevantes": [
        "rev_123",
        "rev_456",
        "rev_789"
    ],
    "tipo_busqueda": "tf_idf",
    "metricas_esperadas": {
        "precision": 0.8,
        "recall": 0.7,
        "f1": 0.75
    }
}
```

Respuesta:
```json
{
    "status": "success",
    "message": "Necesidad de información creada correctamente",
    "need_id": "N001"
}
```

### 4.2 Obtener Necesidades

Endpoint para listar todas las necesidades de información.

```http
GET http://localhost:8000/needs
```

Respuesta:
```json
{
    "needs": [
        {
            "id": "N001",
            "descripcion": "Buscar reseñas de auriculares con buena calidad de sonido y batería duradera",
            "consulta": "auriculares calidad sonido bateria",
            "documentos_relevantes": ["rev_123", "rev_456", "rev_789"],
            "tipo_busqueda": "tf_idf",
            "metricas_esperadas": {
                "precision": 0.8,
                "recall": 0.7,
                "f1": 0.75
            }
        }
    ]
}
```

### 4.3 Obtener Necesidad Específica

Endpoint para obtener una necesidad de información específica.

```http
GET http://localhost:8000/needs/N001
```

Respuesta:
```json
{
    "id": "N001",
    "descripcion": "Buscar reseñas de auriculares con buena calidad de sonido y batería duradera",
    "consulta": "auriculares calidad sonido bateria",
    "documentos_relevantes": ["rev_123", "rev_456", "rev_789"],
    "tipo_busqueda": "tf_idf",
    "metricas_esperadas": {
        "precision": 0.8,
        "recall": 0.7,
        "f1": 0.75
    },
    "ultima_evaluacion": {
        "fecha": "2024-01-15T10:30:00Z",
        "metricas_obtenidas": {
            "precision": 0.75,
            "recall": 0.68,
            "f1": 0.71
        }
    }
}
```

### 4.4 Actualizar Necesidad

Endpoint para actualizar una necesidad existente.

```http
PUT http://localhost:8000/needs/N001
Content-Type: application/json

{
    "descripcion": "Buscar reseñas de auriculares con buena calidad de sonido y batería duradera",
    "consulta": "auriculares calidad sonido bateria duracion",
    "documentos_relevantes": [
        "rev_123",
        "rev_456",
        "rev_789",
        "rev_101"
    ],
    "tipo_busqueda": "tf_idf",
    "metricas_esperadas": {
        "precision": 0.85,
        "recall": 0.75,
        "f1": 0.80
    }
}
```

Respuesta:
```json
{
    "status": "success",
    "message": "Necesidad de información actualizada correctamente",
    "need_id": "N001"
}
```

### 4.5 Eliminar Necesidad

Endpoint para eliminar una necesidad de información.

```http
DELETE http://localhost:8000/needs/N001
```

Respuesta:
```json
{
    "status": "success",
    "message": "Necesidad de información eliminada correctamente",
    "need_id": "N001"
}
```

### 4.6 Evaluar Necesidad

Endpoint para evaluar una necesidad de información específica.

```http
POST http://localhost:8000/needs/N001/evaluate
```

Respuesta:
```json
{
    "need_id": "N001",
    "fecha_evaluacion": "2024-01-15T10:30:00Z",
    "metricas": {
        "precision": 0.75,
        "recall": 0.68,
        "f1": 0.71,
        "average_precision": 0.82
    },
    "analisis": {
        "documentos_relevantes_encontrados": 15,
        "documentos_relevantes_total": 22,
        "documentos_recuperados": 20,
        "distribucion_scores": {
            "0.8-1.0": 5,
            "0.6-0.8": 8,
            "0.4-0.6": 4,
            "0.2-0.4": 2,
            "0.0-0.2": 1
        }
    }
}
```

## 6. Notas sobre Necesidades de Información

1. **Formato de IDs**:
   - Los IDs de necesidades deben comenzar con 'N' seguido de números
   - Ejemplo: N001, N002, etc.

2. **Documentos Relevantes**:
   - Se deben especificar usando los IDs de las reseñas
   - Los IDs deben existir en el sistema

3. **Métricas**:
   - Precision: [0-1]
   - Recall: [0-1]
   - F1: [0-1]
   - Se pueden especificar métricas esperadas para evaluación

4. **Tipos de Búsqueda**:
   - "tf_idf": búsqueda por relevancia
   - "boolean": búsqueda booleana
   - El tipo afecta cómo se evalúan los resultados 