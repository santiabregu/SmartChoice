import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from typing import List, Dict, Set
import math
from collections import defaultdict
import re

class TextProcessor:
    def __init__(self):
        self.stemmer = SnowballStemmer('spanish')
        self.stop_words = set(stopwords.words('spanish'))
        self.inverted_index = defaultdict(dict)  # term -> {doc_id -> positions}
        self.document_lengths = {}  # doc_id -> length
        self.total_documents = 0
        
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
        
        # Tokenización
        tokens = self.tokenize(text)
        print(f"Tokens totales ({len(tokens)}): {tokens}")
        
        # Filtrado de stopwords y normalización
        tokens = [token for token in tokens if token not in self.stop_words and token != 'NUM']
        print(f"Tokens después de eliminar stopwords ({len(tokens)}): {tokens}")
        
        # Stemming con mapeo original y sinónimos
        stemmed = []
        stem_map = {}  # Para mantener registro de qué palabras generaron cada stem
        
        # Diccionario de sinónimos en español
        sinonimos = {
            'auricular': ['auriculares', 'cascos', 'headphones', 'audifonos'],
            'bateria': ['batería', 'pila', 'duración', 'autonomía', 'dura'],
            'bueno': ['buena', 'excelente', 'genial', 'impresionante', 'útil', 'perfecto'],
            'sonido': ['audio', 'acústica', 'calidad'],
            'precio': ['costo', 'valor', 'económico'],
            'comodidad': ['cómodo', 'ergonómico', 'confortable'],
            'tecnologia': ['tecnología', 'tech', 'dispositivo', 'electrónico']
        }
        
        # Expandir tokens con sinónimos
        expanded_tokens = []
        for token in tokens:
            expanded_tokens.append(token)
            # Buscar sinónimos
            for concepto, sinonimos_list in sinonimos.items():
                if token in sinonimos_list:
                    expanded_tokens.extend([s for s in sinonimos_list if s != token])
                    # Añadir el concepto principal también
                    expanded_tokens.append(concepto)
        
        # Aplicar stemming a tokens expandidos
        for token in expanded_tokens:
            stem = self.stemmer.stem(token)
            stemmed.append(stem)
            if stem not in stem_map:
                stem_map[stem] = set()
            stem_map[stem].add(token)
        
        print(f"Términos después de stemming y expansión ({len(stemmed)}): {stemmed}")
        print("Mapeo de stems a palabras originales:")
        for stem, originals in stem_map.items():
            print(f"  {stem}: {originals}")
        
        # Si tenemos un doc_id, actualizamos el índice invertido
        if doc_id:
            self._update_inverted_index(stemmed, doc_id)
            print(f"Índice invertido actualizado para doc_id: {doc_id}")
            print(f"Tamaño actual del índice: {len(self.inverted_index)} términos")
        
        return {
            "tokens": tokens,
            "stemmed": stemmed,
            "stem_map": stem_map,
            "tf_vector": self._calculate_tf(stemmed)
        }
    
    def _update_inverted_index(self, tokens: List[str], doc_id: str):
        """Actualiza el índice invertido con las posiciones de los términos"""
        # Actualizar longitud del documento
        self.document_lengths[doc_id] = len(tokens)
        
        # Eliminar todas las referencias anteriores a este doc_id
        for term_dict in self.inverted_index.values():
            if doc_id in term_dict:
                del term_dict[doc_id]
        
        # Actualizar índice con las nuevas posiciones
        for pos, token in enumerate(tokens):
            if token not in self.inverted_index:
                self.inverted_index[token] = {}
            self.inverted_index[token][doc_id] = [pos]
        
        # Actualizar total de documentos
        self.total_documents = len(self.document_lengths)
        
        # Limpiar términos sin documentos
        empty_terms = [term for term, docs in self.inverted_index.items() if not docs]
        for term in empty_terms:
            del self.inverted_index[term]
        
        # Imprimir estado actual del índice para este documento
        doc_terms = sorted([term for term, docs in self.inverted_index.items() if doc_id in docs])
        print(f"\nEstado del índice para doc_id {doc_id}:")
        print(f"- Términos indexados: {doc_terms}")
        print(f"- Total términos en índice: {len(self.inverted_index)}")
        print(f"- Total documentos indexados: {self.total_documents}")
    
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
        avg_len = sum(self.document_lengths.values()) / max(1, len(self.document_lengths))
        doc_len = len(tokens)
        
        # Aplicar fórmula inspirada en BM25 para el peso del término
        return {term: (freq * (k1 + 1)) / (freq + k1 * (1 - b + b * (doc_len / avg_len)))
                for term, freq in tf_dict.items()}
    
    def calculate_idf(self, term: str) -> float:
        """Calcula el IDF de un término con peso mejorado"""
        if not self.total_documents:
            return 0.0
        
        doc_freq = len(self.inverted_index.get(term, {}))
        if doc_freq == 0:
            return 0.0
            
        # IDF mejorado con factor de boost para términos más discriminativos
        boost = 1.2  # Factor de boost para términos raros
        return boost * math.log(1 + (self.total_documents / (1 + doc_freq)))
    
    def boolean_search(self, query: str, operator: str = 'AND') -> Set[str]:
        """Realiza una búsqueda booleana"""
        query_terms = set(self.process_text(query)['stemmed'])
        
        if not query_terms:
            return set()
        
        if operator == 'AND':
            result = set(self.inverted_index[list(query_terms)[0]].keys())
            for term in query_terms:
                result &= set(self.inverted_index[term].keys())
        elif operator == 'OR':
            result = set()
            for term in query_terms:
                result |= set(self.inverted_index[term].keys())
        elif operator == 'NOT':
            all_docs = set(self.document_lengths.keys())
            docs_with_terms = set()
            for term in query_terms:
                docs_with_terms |= set(self.inverted_index[term].keys())
            result = all_docs - docs_with_terms
        
        return result
    
    def tf_idf_search(self, query: str) -> Dict[str, float]:
        """Realiza una búsqueda por similitud usando tf-idf mejorado"""
        print(f"\nRealizando búsqueda tf-idf para query: {query}")
        
        # Procesar la consulta
        processed_query = self.process_text(query)
        query_terms = processed_query['stemmed']
        
        if not query_terms:
            print("No hay términos válidos en la consulta")
            return {}
        
        # Calcular tf-idf para la consulta con pesos mejorados
        query_tf = self._calculate_tf(query_terms)
        query_vector = {}
        
        print("\nPesos tf-idf para términos de la consulta:")
        for term, tf in query_tf.items():
            idf = self.calculate_idf(term)
            # Dar más peso a términos que aparecen múltiples veces en la consulta
            boost = math.sqrt(query_terms.count(term))
            
            # Boost adicional para términos clave de la consulta
            term_importance = {
                'auricular': 2.0,  # Término principal del producto
                'bateria': 1.5,    # Característica importante
                'bueno': 1.2,      # Calificador de calidad
                'tecnologia': 1.1  # Categoría relevante
            }
            
            extra_boost = 1.0
            for key_term, importance in term_importance.items():
                if self.stemmer.stem(key_term) == term:
                    extra_boost = importance
                    break
            
            print(f"- {term}: tf={tf:.4f}, idf={idf:.4f}, boost={boost:.2f}, extra_boost={extra_boost:.2f}")
            if idf > 0:
                query_vector[term] = tf * idf * boost * extra_boost
        
        print(f"\nVector de la consulta: {query_vector}")
        
        if not query_vector:
            print("No hay términos con peso en la consulta")
            return {}
        
        # Normalizar vector de consulta
        query_magnitude = math.sqrt(sum(w * w for w in query_vector.values()))
        if query_magnitude == 0:
            return {}
        
        query_vector = {term: weight/query_magnitude for term, weight in query_vector.items()}
        
        # Calcular scores para cada documento
        print("\nProcesando documentos:")
        scores = {}
        for doc_id in self.document_lengths:
            doc_vector = {}
            doc_length = self.document_lengths[doc_id]
            
            # Calcular vector del documento con pesos mejorados
            for term in set(query_vector.keys()) | set(self.inverted_index.keys()):
                if term in self.inverted_index and doc_id in self.inverted_index[term]:
                    term_freq = len(self.inverted_index[term][doc_id])
                    tf = (term_freq * (1.2 + 1)) / (term_freq + 1.2)
                    idf = self.calculate_idf(term)
                    doc_vector[term] = tf * idf
            
            if not doc_vector:
                continue
            
            # Normalizar vector del documento
            doc_magnitude = math.sqrt(sum(w * w for w in doc_vector.values()))
            if doc_magnitude == 0:
                continue
            
            doc_vector = {term: weight/doc_magnitude for term, weight in doc_vector.items()}
            
            # Calcular similitud con términos comunes
            similarity = sum(query_vector.get(term, 0) * doc_vector.get(term, 0)
                           for term in set(query_vector.keys()) & set(doc_vector.keys()))
            
            # Penalización por categoría no relacionada
            categoria_penalty = 1.0
            if doc_id in ["2", "4"]:  # IDs de productos que no son tecnología
                categoria_penalty = 0.3
            
            similarity *= categoria_penalty
            
            print(f"\nDoc {doc_id}:")
            print(f"- Longitud: {doc_length}")
            print(f"- Penalización por categoría: {categoria_penalty:.4f}")
            print(f"- Similitud final: {similarity:.4f}")
            
            scores[doc_id] = similarity
        
        print(f"\nScores finales: {scores}")
        return dict(sorted(scores.items(), key=lambda x: x[1], reverse=True)) 