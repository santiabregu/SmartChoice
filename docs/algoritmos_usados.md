# Algoritmos de Búsqueda - Fundamentos Matemáticos

## 1. Búsqueda TF-IDF

### 1.1 Term Frequency (TF)

Utilizamos una variante del TF inspirada en BM25:

$$ tf(t,d) = \frac{f_{t,d} \cdot (k_1 + 1)}{f_{t,d} + k_1 \cdot (1 - b + b \cdot \frac{|d|}{avgdl})} $$

Donde:
- $f_{t,d}$ = frecuencia del término t en el documento d
- $k_1 = 1.2$ (parámetro de saturación del término)
- $b = 0.75$ (parámetro de normalización de longitud)
- $|d|$ = longitud del documento en términos
- $avgdl$ = longitud promedio de los documentos

### 1.2 Inverse Document Frequency (IDF)

$$ idf(t) = \log(1 + \frac{N}{1 + df_t}) \cdot w_t \cdot p_t $$

Donde:
- $N$ = número total de documentos
- $df_t$ = número de documentos que contienen el término t
- $w_t$ = peso del término (term_importance)
- $p_t$ = factor de penalización (penalty_terms)

### 1.3 Score Final

$$ score(d,q) = \sum_{t \in q} tf(t,d) \cdot idf(t) \cdot boost(t,q) $$

Donde:
- $boost(t,q)$ = boost adicional por términos compuestos
- $t \in q$ = términos de la consulta presentes en el documento

### 1.4 Valores de Pesos (term_importance)

```python
# Términos de batería y duración (peso muy alto: 3.0)
'bateria': 3.0,
'duracion': 3.0,
'autonomia': 3.0,
'horas': 2.5,
'aguanta': 2.5,
'dura': 2.5,

# Términos de calidad y valoración (2.0-2.5)
'calidad': 2.5,
'excelente': 2.3,
'premium': 2.3,
'profesional': 2.2,
'bueno': 2.0,
'alta gama': 2.0,

# Características técnicas principales (2.0)
'cancelacion': 2.0,
'sonido': 2.0,
'audio': 2.0,

# Categorías de producto (1.8)
'auricular': 1.8,
'altavoz': 1.8,
'smartphone': 1.8,
'tablet': 1.8,
'electrodomestico': 1.8,

# Características específicas (1.5)
'bluetooth': 1.5,
'wifi': 1.5,
'inalambrico': 1.5,
'ergonomico': 1.5,
'ajustable': 1.5,
'smart': 1.5,
'inteligente': 1.5,

# Características de rendimiento (1.5)
'velocidad': 1.5,
'rendimiento': 1.5,
'potencia': 1.5,
'precision': 1.5,
'eficiencia': 1.5,

# Características de diseño (1.4)
'diseno': 1.4,
'construccion': 1.4,
'materiales': 1.4,
'pantalla': 1.4,
'amoled': 1.4,

# Características de uso y mantenimiento (1.3)
'configuracion': 1.3,
'control': 1.3,
'app': 1.3,
'aplicacion': 1.3,
'compatible': 1.3,
'garantia': 1.3,
'durabilidad': 1.3,
'mantenimiento': 1.3,
'limpieza': 1.3,
'automatico': 1.3,

# Términos económicos (1.2)
'precio': 1.2,
'economico': 1.2,
'barato': 1.2,
'ahorro': 1.2,

# Términos específicos de nicho (peso variable)
'gaming': 1.8,
'fitness': 1.5,
'deportivo': 1.5,
'salud': 1.5,
'cosmetico': 1.5,
'cocina': 1.4,
'hogar': 1.3
```

### 1.5 Términos Compuestos (compound_terms)

$$ boost_{compound}(t_1,t_2) = w_{t1,t2} $$

Valores:
```python
'duracion bateria': 3.5,
'buena bateria': 3.5,
'larga duracion': 3.5,
'autonomia bateria': 3.5,
'calidad sonido': 2.8,
'cancelacion ruido': 2.8,
'alta gama': 2.5,
'smart home': 2.3,
'carga rapida': 2.2,
'bajo consumo': 2.0
```

### 1.6 Factores de Penalización (penalty_terms)

$$ p_t = \begin{cases} 
0.5 & \text{si } t \in \{\text{malo, defectuoso, roto}\} \\
0.6 & \text{si } t = \text{problema} \\
1.0 & \text{en otro caso}
\end{cases} $$

### 1.7 Normalización Final

$$ score_{norm}(d,q) = \frac{score(d,q)}{\sqrt{\sum_{t \in d} w_t^2}} $$

## 2. Búsqueda Booleana

### 2.1 Operaciones de Conjuntos

Sean A y B conjuntos de documentos que contienen los términos a y b respectivamente:

#### AND (Intersección)
$$ A \land B = \{ d \mid d \in A \land d \in B \} $$

#### OR (Unión)
$$ A \lor B = \{ d \mid d \in A \lor d \in B \} $$

#### NOT (Complemento)
$$ \neg A = \{ d \mid d \in D \land d \notin A \} $$

Donde D es el conjunto total de documentos.

### 2.2 Expansión de Términos

Para cada término t, el conjunto de documentos se expande con:

$$ D_t = D_{exact} \cup D_{norm} \cup D_{stem} \cup D_{syn} $$

Donde:
- $D_{exact}$ = documentos con término exacto
- $D_{norm}$ = documentos con término normalizado
- $D_{stem}$ = documentos con stem del término
- $D_{syn}$ = documentos con sinónimos

### 2.3 Evaluación de Expresiones Compuestas

Para una expresión booleana E:

$$ E = (A \land B) \lor (\neg C) $$

Se evalúa recursivamente:
1. Resolver paréntesis internos
2. Aplicar operadores NOT
3. Aplicar operadores AND
4. Aplicar operadores OR

## 3. Métricas de Evaluación

### 3.1 Precisión

$$ P = \frac{|R \cap Ret|}{|Ret|} $$

La precisión mide la proporción de documentos relevantes entre todos los documentos recuperados por el sistema. En otras palabras:
- ¿Qué porcentaje de los resultados que devolvemos son realmente útiles?
- Si devolvemos 10 reseñas y 7 son relevantes, la precisión es 0.7 (70%)
- Una precisión alta significa que la mayoría de los resultados son útiles
- Una precisión baja significa que estamos devolviendo muchos resultados irrelevantes

### 3.2 Recall (Exhaustividad)

$$ R = \frac{|R \cap Ret|}{|R|} $$

El recall mide la proporción de documentos relevantes que hemos encontrado del total de documentos relevantes que existen. En otras palabras:
- ¿Qué porcentaje de todos los documentos relevantes hemos logrado encontrar?
- Si hay 20 reseñas relevantes en total y encontramos 15, el recall es 0.75 (75%)
- Un recall alto significa que encontramos la mayoría de los documentos útiles
- Un recall bajo significa que nos estamos perdiendo muchos documentos relevantes

### 3.3 F1-Score

$$ F1 = 2 \cdot \frac{P \cdot R}{P + R} $$

El F1-Score es la media armónica entre precisión y recall. En otras palabras:
- Es una medida que combina precisión y recall en un solo número
- Da igual importancia a ambas métricas
- Un F1 alto (cercano a 1) significa que el sistema es bueno tanto en precisión como en recall
- Un F1 bajo (cercano a 0) significa que el sistema falla en al menos una de las métricas
- Es útil cuando necesitamos un balance entre encontrar muchos resultados relevantes y evitar resultados irrelevantes

### 3.4 Average Precision (AP)

$$ AP = \frac{\sum_{k=1}^n P(k) \cdot rel(k)}{|R|} $$

El Average Precision mide la calidad del ranking de resultados. En otras palabras:
- Evalúa no solo si encontramos documentos relevantes, sino si los colocamos en las primeras posiciones
- Da más importancia a los documentos relevantes que aparecen al principio de la lista
- Un AP alto significa que los documentos más relevantes aparecen primero
- Un AP bajo puede significar que:
  * Los documentos relevantes aparecen muy abajo en la lista
  * Hay muchos documentos irrelevantes mezclados con los relevantes
  * No encontramos suficientes documentos relevantes

#### Ejemplo de AP:
Si tenemos 5 resultados (R = relevante, I = irrelevante) en este orden:
```
1. R (P@1 = 1/1)
2. I (P@2 = 1/2)
3. R (P@3 = 2/3)
4. R (P@4 = 3/4)
5. I (P@5 = 3/5)
```
AP = (1/1 + 2/3 + 3/4) / 4 = 0.76

## 4. Parámetros del Sistema

### 4.1 Umbrales
- Umbral mínimo de score: 0.05 (optimizado para mejor balance entre precisión y recall)
- Umbral de similitud para evaluación: 0.15
- Umbral alto para documentos muy relevantes: 0.20
- Umbral para pseudo-relevance feedback: 0.07

Los umbrales han sido optimizados basándose en experimentos que muestran:
- Umbrales muy bajos (<0.05) producen demasiado ruido
- Umbrales muy altos (>0.20) pierden documentos relevantes
- El rango 0.05-0.15 ofrece el mejor balance entre precisión y recall
- Para algunas consultas específicas, umbrales más altos (0.20) pueden mejorar la precisión

### 4.2 Normalización de Texto
- Conversión a minúsculas
- Eliminación de acentos y caracteres especiales
- Eliminación de stopwords
- Stemming para español

### 4.3 Expansión de Sinónimos
```python
sinonimos = {
    'auriculares': ['cascos', 'audífonos', 'headphones', 'earbuds'],
    'batería': ['autonomía', 'duración', 'pila'],
    'sonido': ['audio', 'acústica', 'reproducción'],
    'calidad': ['excelente', 'superior', 'premium', 'buena']
}
```

## 5. Ejemplo de Cálculo

Para la consulta "auriculares con buena batería":

1. Normalización:
   - Eliminación de stopwords: "auriculares buena bateria"
   - Expansión con sinónimos: ["auriculares", "cascos", "buena", "bateria", "duracion"]

2. Cálculo TF-IDF:
   ```python
   # Para cada término t
   tf = freq * (1.2 + 1) / (freq + 1.2 * (1 - 0.75 + 0.75 * (doc_len/avg_len)))
   idf = log(1 + (N/(1 + df))) * term_importance[t]
   
   # Para términos compuestos
   if "buena bateria" in doc:
       score *= 2.5  # boost por término compuesto
   ```

3. Score final:
   ```python
   final_score = sum(tf * idf for term in query) / sqrt(doc_length)
   ``` 