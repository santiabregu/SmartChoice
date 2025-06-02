# Algoritmos Utilizados en el Sistema de Recuperación

## 1. TF-IDF (Term Frequency-Inverse Document Frequency)

### Term Frequency (TF)
Usamos una variante del TF inspirada en BM25:

$$ tf(t,d) = \frac{f_{t,d} \cdot (k_1 + 1)}{f_{t,d} + k_1 \cdot (1 - b + b \cdot \frac{|d|}{avgdl})} $$

Donde:
- $f_{t,d}$ = frecuencia del término t en el documento d
- $k_1 = 1.2$ (parámetro de saturación)
- $b = 0.75$ (parámetro de normalización de longitud)
- $|d|$ = longitud del documento
- $avgdl$ = longitud promedio de los documentos

### Inverse Document Frequency (IDF)
Usamos un IDF mejorado con factor de boost:

$$ idf(t) = boost \cdot \log(1 + \frac{N}{1 + df_t}) $$

Donde:
- $N$ = número total de documentos
- $df_t$ = número de documentos que contienen el término t
- $boost = 1.2$ (factor de boost para términos discriminativos)

### Score Final TF-IDF
Para un término t en un documento d:

$$ score(t,d) = tf(t,d) \cdot idf(t) $$

## 2. Similitud de Coseno
Para calcular la similitud entre la consulta q y un documento d:

$$ sim(q,d) = \frac{\sum_{t \in q \cap d} w_{t,q} \cdot w_{t,d}}{\sqrt{\sum_{t \in q} w_{t,q}^2} \cdot \sqrt{\sum_{t \in d} w_{t,d}^2}} $$

Donde:
- $w_{t,q}$ = peso del término t en la consulta
- $w_{t,d}$ = peso del término t en el documento
- $q \cap d$ = términos comunes entre consulta y documento

## 3. Pseudo-Relevance Feedback
Utilizamos un sistema de umbral para determinar relevancia:

$$ R = \{ d_i \in D_{top-k} \mid score(d_i) \geq \theta \} $$

Donde:
- $D_{top-k}$ = top k documentos (k = 2)
- $\theta = 0.15$ (umbral de relevancia)
- $R$ = conjunto de documentos considerados relevantes

## 4. Búsqueda Booleana
Implementamos operadores AND, OR, NOT usando teoría de conjuntos:

### AND
$$ A \land B = \{ d \mid d \in A \land d \in B \} $$

### OR
$$ A \lor B = \{ d \mid d \in A \lor d \in B \} $$

### NOT
$$ \neg A = \{ d \mid d \in D \land d \notin A \} $$

Donde:
- $A, B$ = conjuntos de documentos que contienen los términos a, b
- $D$ = conjunto total de documentos

## 5. Normalización de Scores
Para normalizar los scores finales:

$$ score_{norm}(d) = \frac{score(d)}{\sqrt{\sum_{t \in d} w_t^2}} $$

## 6. Evaluación de Resultados

### Precision
$$ P = \frac{|R \cap Ret|}{|Ret|} $$

### Recall
$$ R = \frac{|R \cap Ret|}{|R|} $$

### Average Precision
$$ AP = \frac{\sum_{k=1}^n P(k) \cdot rel(k)}{|R|} $$

Donde:
- $R$ = conjunto de documentos relevantes
- $Ret$ = conjunto de documentos recuperados
- $P(k)$ = precisión en el corte k
- $rel(k)$ = 1 si el documento en posición k es relevante, 0 si no
- $n$ = número total de documentos recuperados

## Notas de Implementación

1. **Procesamiento de Texto**:
   - Normalización de caracteres españoles: á → a, é → e, etc.
   - Eliminación de stopwords en español
   - Stemming usando Snowball Stemmer para español

2. **Optimizaciones**:
   - Índice invertido para búsqueda eficiente
   - Vectores normalizados precalculados
   - Cache de stems para términos frecuentes

3. **Umbrales Utilizados**:
   - Relevancia alta: score ≥ 0.15
   - No relevante: score < 0.05
   - Top-k: k = 2 documentos
   - Boost términos raros: 1.2 