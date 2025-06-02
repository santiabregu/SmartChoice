# Métricas de Evaluación del Sistema de Recuperación

## Métricas Básicas

### Conteos
- `retrieved_count`: Número total de documentos recuperados en la búsqueda
- `relevant_count`: Número de documentos considerados relevantes (score ≥ 0.15)
- `nonrelevant_count`: Número de documentos considerados no relevantes (score < 0.05)
- `retrieved_and_relevant`: Número de documentos que son tanto recuperados como relevantes

### Precisión y Exhaustividad

#### Precision (Precisión)
```
precision = retrieved_and_relevant / retrieved_count
```
- **Qué mide**: La fracción de documentos recuperados que son relevantes
- **Rango**: 0.0 a 1.0
- **Ejemplo**: Si precision = 0.4, significa que el 40% de los documentos recuperados son relevantes
- **Interpretación**: Una precisión alta indica que la mayoría de los resultados son relevantes

#### Recall (Exhaustividad)
```
recall = retrieved_and_relevant / relevant_count
```
- **Qué mide**: La fracción de documentos relevantes que fueron recuperados
- **Rango**: 0.0 a 1.0
- **Ejemplo**: Si recall = 1.0, significa que se encontraron todos los documentos relevantes
- **Interpretación**: Un recall alto indica que se encontraron la mayoría de los documentos relevantes

### Métricas Avanzadas

#### Average Precision (Precisión Media)
- **Qué mide**: La precisión promedio en cada posición donde se encuentra un documento relevante
- **Rango**: 0.0 a 1.0
- **Cálculo**: Se calcula como:
  1. Para cada documento relevante encontrado:
     - Calcular la precisión hasta esa posición
  2. Promediar todas estas precisiones
- **Ejemplo**: 
  ```
  Resultados: R N R N N (R=relevante, N=no relevante)
  Posición 1 (R): precisión = 1/1 = 1.0
  Posición 3 (R): precisión = 2/3 = 0.67
  Average Precision = (1.0 + 0.67) / 2 = 0.835
  ```
- **Interpretación**: 
  - Considera tanto la precisión como el orden de los resultados
  - Un valor alto indica que los documentos relevantes aparecen al principio de los resultados
  - Penaliza cuando los documentos relevantes aparecen más tarde en la lista

## Ejemplo de Interpretación

Para las métricas:
```json
{
    "average_precision": 1.0,
    "precision": 0.4,
    "recall": 1.0,
    "retrieved_count": 5,
    "relevant_count": 2,
    "nonrelevant_count": 2,
    "retrieved_and_relevant": 2
}
```

Esto significa que:
1. Se recuperaron 5 documentos en total (`retrieved_count`)
2. 2 documentos fueron considerados relevantes (`relevant_count`)
3. 2 documentos fueron considerados no relevantes (`nonrelevant_count`)
4. Se encontraron todos los documentos relevantes (recall = 1.0)
5. El 40% de los resultados son relevantes (precision = 0.4)
6. Los documentos relevantes aparecieron en las mejores posiciones (average_precision = 1.0)

## Interpretación de Score Statistics

### Distribución de Scores
```json
"score_distribution": {
    "0.0-0.1": 2,
    "0.1-0.2": 1,
    "0.2-0.3": 1,
    "0.3-0.4": 1,
    "0.4-0.5": 0,
    "0.5+": 0
}
```
- Muestra cuántos documentos caen en cada rango de puntuación
- Ayuda a entender la distribución de la relevancia
- Útil para ajustar los umbrales de relevancia

### Estadísticas por Categoría
```json
"matches_by_category": {
    "Tecnología": 3,
    "Ropa": 1,
    "Cosméticos": 1
}
```
- Muestra la distribución de resultados por categoría
- Ayuda a identificar sesgos en los resultados
- Útil para evaluar la diversidad de los resultados 