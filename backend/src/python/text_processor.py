import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from typing import List, Dict, Set
import math
from collections import defaultdict
import re
import json
from pathlib import Path

class TextProcessor:
    def __init__(self):
        self.stemmer = SnowballStemmer('spanish')
        self.stop_words = set(stopwords.words('spanish'))
        self.inverted_index = defaultdict(dict)  # term -> {doc_id -> positions}
        self.document_lengths = {}  # doc_id -> length
        self.total_documents = 0
        self.sinonimos = self._load_sinonimos()
        self.use_synonyms = True  # Flag to control synonym expansion
        
        # Configuración de pesos para términos
        self.term_importance = {
            # Términos de batería y duración (peso muy alto)
            'bateria': 3.0,
            'duracion': 3.0,
            'autonomia': 3.0,
            'horas': 2.5,
            'aguanta': 2.5,
            'dura': 2.5,

            # Términos de calidad y valoración (peso alto)
            'calidad': 2.5,
            'excelente': 2.3,
            'premium': 2.3,
            'profesional': 2.2,
            'bueno': 2.0,
            'alta gama': 2.0,

            # Características técnicas principales (peso alto)
            'cancelacion': 2.0,
            'sonido': 2.0,
            'audio': 2.0,

            # Categorías de producto (peso medio-alto)
            'auricular': 1.8,
            'altavoz': 1.8,
            'smartphone': 1.8,
            'tablet': 1.8,
            'electrodomestico': 1.8,

            # Características específicas (peso medio)
            'bluetooth': 1.5,
            'wifi': 1.5,
            'inalambrico': 1.5,
            'ergonomico': 1.5,
            'ajustable': 1.5,
            'smart': 1.5,
            'inteligente': 1.5,

            # Características de rendimiento (peso medio)
            'velocidad': 1.5,
            'rendimiento': 1.5,
            'potencia': 1.5,
            'precision': 1.5,
            'eficiencia': 1.5,

            # Características de diseño (peso medio)
            'diseno': 1.4,
            'construccion': 1.4,
            'materiales': 1.4,
            'pantalla': 1.4,
            'amoled': 1.4,

            # Características de uso (peso medio-bajo)
            'configuracion': 1.3,
            'control': 1.3,
            'app': 1.3,
            'aplicacion': 1.3,
            'compatible': 1.3,

            # Términos de mantenimiento (peso medio-bajo)
            'garantia': 1.3,
            'durabilidad': 1.3,
            'mantenimiento': 1.3,
            'limpieza': 1.3,
            'automatico': 1.3,

            # Términos económicos (peso medio-bajo)
            'precio': 1.2,
            'economico': 1.2,
            'barato': 1.2,
            'ahorro': 1.2,

            # Términos específicos de nicho (peso variable según contexto)
            'gaming': 1.8,
            'fitness': 1.5,
            'deportivo': 1.5,
            'salud': 1.5,
            'cosmetico': 1.5,
            'cocina': 1.4,
            'hogar': 1.3
        }
        
        # Boost adicional para combinaciones específicas
        self.compound_terms = {
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
        }
        
        # Factores de penalización
        self.penalty_terms = {
            'malo': 0.5,
            'defectuoso': 0.5,
            'roto': 0.5,
            'fallo': 0.5,
            'problema': 0.6,
            'negativo': 0.6
        }
        
    def _load_sinonimos(self) -> Dict[str, List[str]]:
        """Carga el diccionario de sinónimos desde el archivo JSON"""
        try:
            sinonimos_path = Path(__file__).parent / "data" / "sinonimos.json"
            with open(sinonimos_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Combinar sinónimos y categorías en un solo diccionario
                sinonimos_dict = data.get("sinonimos", {})
                categorias_dict = data.get("categorias", {})
                # Añadir categorías al diccionario de sinónimos
                sinonimos_dict.update(categorias_dict)
                return sinonimos_dict
        except FileNotFoundError:
            print("Archivo sinonimos.json no encontrado, usando diccionario vacío")
            return {}

    def normalize_text(self, text: str) -> str:
        """Normaliza el texto aplicando reglas específicas para español"""
        # Convertir a minúsculas
        text = text.lower()
        
        # Normalizar caracteres especiales españoles
        replacements = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'ü': 'u', 'ñ': 'n', 'à': 'a', 'è': 'e', 'ì': 'i',
            'ò': 'o', 'ù': 'u'
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
            
        return text

    def tokenize(self, text: str) -> List[str]:
        """Tokeniza el texto usando una aproximación robusta para español"""
        # Normalizar texto
        text = self.normalize_text(text)
        
        # Reemplazar números por token especial
        text = re.sub(r'\d+', 'NUM', text)
        
        # Reemplazar caracteres no alfanuméricos por espacios
        text = re.sub(r'[^a-z\s]', ' ', text)
        
        # Tokenizar y filtrar tokens vacíos y muy cortos
        tokens = []
        for token in text.split():
            token = token.strip()
            if token and len(token) > 1:  # Ignorar tokens de un solo carácter
                tokens.append(token)
        
        print(f"Tokens generados: {tokens[:10]}...")
        return tokens
        
    def process_text(self, text: str, doc_id: str = None) -> Dict:
        """Procesa el texto y actualiza el índice invertido si se proporciona doc_id"""
        print(f"\nProcesando texto para doc_id: {doc_id}")
        print(f"Texto original: {text}")
        
        # Tokenización y normalización inicial
        tokens = self.tokenize(text)
        print(f"Tokens totales ({len(tokens)}): {tokens}")
        
        # Filtrado de stopwords y normalización
        tokens = [self.normalize_text(token) for token in tokens if token not in self.stop_words and token != 'NUM']
        print(f"Tokens después de eliminar stopwords ({len(tokens)}): {tokens}")
        
        # Expandir con sinónimos y aplicar stemming
        expanded_tokens = []
        stemmed_tokens = []
        stem_map = {}
        
        # Procesar cada token
        for token in tokens:
            # Añadir el token original
            expanded_tokens.append(token)
            
            # Buscar sinónimos solo si use_synonyms es True
            if self.use_synonyms:
                # Buscar sinónimos (usando token normalizado)
                normalized_token = self.normalize_text(token)
                for concepto, sinonimos_list in self.sinonimos.items():
                    # Normalizar concepto y sinónimos para comparación
                    normalized_concepto = self.normalize_text(concepto)
                    normalized_sinonimos = [self.normalize_text(s) for s in sinonimos_list]
                    
                    if normalized_token in normalized_sinonimos or normalized_token == normalized_concepto:
                        # Añadir sinónimos y concepto principal
                        expanded_tokens.extend([s for s in sinonimos_list if self.normalize_text(s) != normalized_token])
                        if normalized_concepto != normalized_token:
                            expanded_tokens.append(concepto)
        
        # Aplicar stemming a tokens expandidos
        for token in expanded_tokens:
            stem = self.stemmer.stem(token)
            stemmed_tokens.append(stem)
            if stem not in stem_map:
                stem_map[stem] = set()
            stem_map[stem].add(token)
        
        print(f"Términos después de stemming y expansión ({len(stemmed_tokens)}): {stemmed_tokens}")
        print("Mapeo de stems a palabras originales:")
        for stem, originals in stem_map.items():
            print(f"  {stem}: {originals}")
        
        # Si tenemos un doc_id, actualizamos el índice invertido
        if doc_id:
            # Actualizar longitud del documento
            self.document_lengths[doc_id] = len(tokens)  # Longitud original sin expansión
            self.total_documents = len(self.document_lengths)
            
            # Indexar tanto los tokens originales como los stems
            all_terms = list(set(expanded_tokens + stemmed_tokens))
            self._update_inverted_index(all_terms, doc_id)
            print(f"Índice invertido actualizado para doc_id: {doc_id}")
            print(f"Tamaño actual del índice: {len(self.inverted_index)} términos")
            print(f"Longitud del documento: {self.document_lengths[doc_id]}")
            print(f"Total documentos indexados: {self.total_documents}")
        
        return {
            "tokens": tokens,
            "expanded": expanded_tokens,
            "stemmed": stemmed_tokens,
            "stem_map": stem_map,
            "tf_vector": self._calculate_tf(stemmed_tokens)
        }
    
    def _update_inverted_index(self, tokens: List[str], doc_id: str):
        """Actualiza el índice invertido con las posiciones de los términos"""
        # Actualizar longitud del documento (acumular si ya existe)
        if doc_id in self.document_lengths:
            self.document_lengths[doc_id] += len(tokens)
        else:
            self.document_lengths[doc_id] = len(tokens)
        
        # Conjunto para almacenar todos los términos a indexar
        terms_to_index = set()
        
        # Procesar cada token
        for pos, token in enumerate(tokens):
            # Añadir el token original
            terms_to_index.add(token.lower())
            
            # Añadir el stem
            stem = self.stemmer.stem(token.lower())
            terms_to_index.add(stem)
            
            # Añadir sinónimos y sus stems
            for concepto, sinonimos in self.sinonimos.items():
                if token.lower() in [s.lower() for s in sinonimos] or token.lower() == concepto.lower():
                    # Añadir el concepto y su stem
                    terms_to_index.add(concepto.lower())
                    terms_to_index.add(self.stemmer.stem(concepto))
                    # Añadir todos los sinónimos y sus stems
                    for sinonimo in sinonimos:
                        terms_to_index.add(sinonimo.lower())
                        terms_to_index.add(self.stemmer.stem(sinonimo))
        
        # Indexar todos los términos
        for term in terms_to_index:
            if term not in self.inverted_index:
                self.inverted_index[term] = {}
            if doc_id not in self.inverted_index[term]:
                self.inverted_index[term][doc_id] = []
            if 0 not in self.inverted_index[term][doc_id]:  # Solo añadir la posición si no existe
                self.inverted_index[term][doc_id].append(0)
        
        # Actualizar total de documentos
        self.total_documents = len(self.document_lengths)
        
        # Imprimir estado actual del índice para este documento
        doc_terms = sorted([term for term, docs in self.inverted_index.items() if doc_id in docs])
        print(f"\nEstado del índice para doc_id {doc_id}:")
        print(f"- Términos indexados: {doc_terms}")
        print(f"- Total términos en índice: {len(self.inverted_index)}")
        print(f"- Total documentos indexados: {self.total_documents}")
        
        # Imprimir términos específicos para debug
        debug_terms = ['auriculares', 'auricular', 'bateria', 'batería', 'duracion', 'duración']
        print("\nEstado de términos específicos en el índice:")
        for term in debug_terms:
            if term in self.inverted_index:
                print(f"- {term}: {self.inverted_index[term]}")
            else:
                print(f"- {term}: No indexado")
    
    def _calculate_tf(self, tokens: List[str]) -> Dict[str, float]:
        """Calcula la frecuencia de términos normalizada usando BM25-inspired weighting"""
        tf_dict = defaultdict(float)
        if not tokens:
            return tf_dict
        
        # Contar frecuencias brutas
        for token in tokens:
            tf_dict[token] += 1
        
        # Parámetros de BM25
        k1 = 1.2  # Parámetro de saturación de término
        b = 0.75  # Parámetro de normalización de longitud
        
        # Calcular longitud promedio del documento de forma segura
        total_length = sum(self.document_lengths.values())
        num_docs = len(self.document_lengths)
        avg_len = total_length / num_docs if num_docs > 0 else 1.0
        
        # Longitud del documento actual (o 1 si no hay tokens)
        doc_len = len(tokens) if tokens else 1.0
        
        # Aplicar fórmula inspirada en BM25 para el peso del término
        # Añadir 1 al denominador para evitar división por cero
        return {term: (freq * (k1 + 1)) / (freq + k1 * (1 - b + b * (doc_len / avg_len)) + 1)
                for term, freq in tf_dict.items()}
    
    def calculate_idf(self, term: str) -> float:
        """Calcula el IDF de un término con boost por importancia"""
        if term not in self.inverted_index:
            return 0.0
        
        # Obtener el número de documentos que contienen el término
        doc_freq = len(self.inverted_index[term])
        
        # Calcular IDF base
        idf = math.log(1 + (self.total_documents / (1 + doc_freq)))
        
        # Aplicar boost por importancia del término
        term_boost = self.term_importance.get(term.lower(), 1.0)
        
        # Aplicar penalización si es un término negativo
        term_penalty = self.penalty_terms.get(term.lower(), 1.0)
        
        # El IDF final es el producto del IDF base, el boost y la penalización
        return idf * term_boost * term_penalty

    def boolean_search(self, query: str, operator: str = 'AND') -> Set[str]:
        """Realiza una búsqueda booleana con operadores AND, OR, NOT"""
        print(f"\nRealizando búsqueda booleana: {query}")
        
        # Normalizar espacios alrededor de operadores y paréntesis
        query = query.replace('(', ' ( ').replace(')', ' ) ')
        query = query.replace(' AND ', ' AND ').replace(' OR ', ' OR ').replace(' NOT ', ' NOT ')
        query = ' '.join(query.split())  # Normalizar espacios múltiples
        print(f"Query normalizada: {query}")
        
        # Primero procesamos los paréntesis
        if '(' in query and ')' in query:
            parts = query.split()
            result_parts = []
            i = 0
            while i < len(parts):
                if parts[i] == '(':
                    # Encontrar el paréntesis de cierre correspondiente
                    j = i + 1
                    count = 1
                    while j < len(parts) and count > 0:
                        if parts[j] == '(':
                            count += 1
                        elif parts[j] == ')':
                            count -= 1
                        j += 1
                    
                    # Procesar la subexpresión
                    subquery = ' '.join(parts[i+1:j-1])
                    print(f"Procesando subexpresión: {subquery}")
                    
                    # Procesar términos separados por OR
                    subterms = subquery.split(' OR ')
                    subresult = set()
                    for term in subterms:
                        term = term.strip()
                        if term:
                            term_result = self._search_single_term(term)
                            print(f"Resultado OR para '{term}': {term_result}")
                            subresult |= term_result
                    
                    print(f"Resultado de subexpresión: {subresult}")
                    result_parts.append(subresult)
                    i = j
                elif parts[i].upper() in ['AND', 'OR', 'NOT']:
                    result_parts.append(parts[i].upper())
                    i += 1
                else:
                    result = self._search_single_term(parts[i])
                    print(f"Resultado para término '{parts[i]}': {result}")
                    result_parts.append(result)
                    i += 1
            
            # Procesar los resultados con los operadores
            if not result_parts:
                return set()
            
            final_result = result_parts[0] if isinstance(result_parts[0], set) else set()
            for i in range(1, len(result_parts), 2):
                if i + 1 < len(result_parts):
                    op = result_parts[i]
                    next_set = result_parts[i + 1]
                    if op == 'AND':
                        final_result &= next_set
                    elif op == 'OR':
                        final_result |= next_set
                    elif op == 'NOT':
                        final_result -= next_set
            
            return final_result
        
        # Si no hay paréntesis, procesamos normalmente
        parts = query.split()
        if not parts:
            return set()
        
        # Procesar el primer término
        final_result = self._search_single_term(parts[0])
        
        # Procesar el resto de términos con sus operadores
        i = 1
        while i < len(parts):
            if parts[i].upper() in ['AND', 'OR', 'NOT'] and i + 1 < len(parts):
                op = parts[i].upper()
                next_result = self._search_single_term(parts[i + 1])
                if op == 'AND':
                    final_result &= next_result
                elif op == 'OR':
                    final_result |= next_result
                elif op == 'NOT':
                    final_result -= next_result
                i += 2
            else:
                i += 1
        
        print(f"Resultado final: {final_result}")
        return final_result

    def _search_single_term(self, term: str) -> Set[str]:
        """Busca un término individual en el índice"""
        print(f"\nBuscando término individual: {term}")
        
        # Normalizar el término
        normalized_term = self.normalize_text(term.lower())
        print(f"Término normalizado: {normalized_term}")
        
        # Buscar coincidencias directas y variantes
        results = set()
        
        # 1. Buscar el término exacto y su forma normalizada
        if term in self.inverted_index:
            docs = set(self.inverted_index[term].keys())
            print(f"Documentos encontrados para término exacto '{term}': {docs}")
            results |= docs
        
        if normalized_term in self.inverted_index:
            docs = set(self.inverted_index[normalized_term].keys())
            print(f"Documentos encontrados para término normalizado '{normalized_term}': {docs}")
            results |= docs
        
        # 2. Buscar el stem del término
        stem = self.stemmer.stem(normalized_term)
        if stem in self.inverted_index:
            docs = set(self.inverted_index[stem].keys())
            print(f"Documentos encontrados para stem '{stem}': {docs}")
            results |= docs
        
        # 3. Buscar en sinónimos
        for concepto, sinonimos in self.sinonimos.items():
            # Normalizar concepto y sinónimos para comparación
            normalized_concepto = self.normalize_text(concepto)
            normalized_sinonimos = [self.normalize_text(s) for s in sinonimos]
            
            if normalized_term in normalized_sinonimos or normalized_term == normalized_concepto:
                # Buscar por el concepto y su forma normalizada
                if concepto in self.inverted_index:
                    docs = set(self.inverted_index[concepto].keys())
                    print(f"Documentos encontrados para concepto '{concepto}': {docs}")
                    results |= docs
                
                if normalized_concepto in self.inverted_index:
                    docs = set(self.inverted_index[normalized_concepto].keys())
                    print(f"Documentos encontrados para concepto normalizado '{normalized_concepto}': {docs}")
                    results |= docs
                
                # Buscar por cada sinónimo y su forma normalizada
                for sinonimo in sinonimos:
                    if sinonimo in self.inverted_index:
                        docs = set(self.inverted_index[sinonimo].keys())
                        print(f"Documentos encontrados para sinónimo '{sinonimo}': {docs}")
                        results |= docs
                    
                    normalized_sinonimo = self.normalize_text(sinonimo)
                    if normalized_sinonimo in self.inverted_index:
                        docs = set(self.inverted_index[normalized_sinonimo].keys())
                        print(f"Documentos encontrados para sinónimo normalizado '{normalized_sinonimo}': {docs}")
                        results |= docs
                    
                    # Buscar también el stem de cada sinónimo
                    stem_sinonimo = self.stemmer.stem(normalized_sinonimo)
                    if stem_sinonimo in self.inverted_index:
                        docs = set(self.inverted_index[stem_sinonimo].keys())
                        print(f"Documentos encontrados para stem de sinónimo '{stem_sinonimo}': {docs}")
                        results |= docs
        
        print(f"Resultado final para '{term}': {results}")
        return results
    
    def tf_idf_search(self, query: str) -> Dict[str, float]:
        """Realiza una búsqueda por similitud usando TF-IDF con pesos mejorados"""
        print(f"\nRealizando búsqueda TF-IDF para: {query}")
        
        # Procesar la consulta
        query_terms = self.process_text(query)
        query_vector = query_terms['tf_vector']
        
        # Buscar términos compuestos en la consulta normalizada
        query_normalized = ' '.join(query_terms['tokens']).lower()
        compound_boost = 1.0
        for compound, boost in self.compound_terms.items():
            if compound.lower() in query_normalized:
                compound_boost *= boost
                print(f"Aplicando boost de término compuesto '{compound}': {boost}")
        
        # Calcular similitud para cada documento
        scores = {}
        for doc_id in self.document_lengths:
            score = 0.0
            doc_length = self.document_lengths[doc_id]
            
            # Calcular similitud coseno con boost por términos importantes
            for term, query_tf in query_vector.items():
                if doc_id in self.inverted_index.get(term, {}):
                    # Calcular TF-IDF para el documento con boost por importancia
                    doc_tf = len(self.inverted_index[term][doc_id]) / doc_length
                    idf = self.calculate_idf(term)
                    term_boost = self.term_importance.get(term.lower(), 1.0)
                    term_score = query_tf * doc_tf * idf * term_boost
                    score += term_score
                    
                    print(f"Término '{term}': TF={doc_tf:.4f}, IDF={idf:.4f}, Boost={term_boost:.1f}, Score={term_score:.4f}")
            
            # Normalizar por longitud del documento y aplicar boost de términos compuestos
            if score > 0:
                score = (score / math.sqrt(doc_length)) * compound_boost
                scores[doc_id] = score
                print(f"Doc {doc_id}: Score final={score:.4f}")
        
        # Ordenar por score descendente
        return dict(sorted(scores.items(), key=lambda x: x[1], reverse=True)) 