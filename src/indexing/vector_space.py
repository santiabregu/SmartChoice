"""
Implementación del modelo de espacio vectorial para recuperación por ranking.

Este módulo implementa el modelo de espacio vectorial utilizando TF-IDF
y similitud coseno para la recuperación de documentos por ranking.
"""

from typing import Dict, List, Tuple
import numpy as np
from collections import Counter
from ..preprocessing.tokenizer import tokenize
import math

class VectorSpaceModel:
    def __init__(self):
        """
        Inicializa el modelo de espacio vectorial.
        """
        self.documents: Dict[int, str] = {}
        self.term_doc_freq: Dict[str, Dict[int, int]] = {}  # tf
        self.doc_freq: Dict[str, int] = {}  # df
        self.idf: Dict[str, float] = {}
        self.doc_vectors: Dict[int, np.ndarray] = {}
        self.vocabulary: List[str] = []
        self.num_docs = 0
    
    def add_document(self, doc_id: int, text: str):
        """
        Añade un documento al modelo.
        
        Args:
            doc_id (int): Identificador único del documento
            text (str): Texto del documento
        """
        self.documents[doc_id] = text
        tokens = tokenize(text)
        term_freq = Counter(tokens)
        
        # Actualizar frecuencias
        for term, freq in term_freq.items():
            if term not in self.term_doc_freq:
                self.term_doc_freq[term] = {}
            self.term_doc_freq[term][doc_id] = freq
            self.doc_freq[term] = self.doc_freq.get(term, 0) + 1
        
        self.num_docs += 1
    
    def build_model(self):
        """
        Construye el modelo vectorial calculando IDF y vectores TF-IDF.
        """
        # Construir vocabulario
        self.vocabulary = sorted(self.term_doc_freq.keys())
        
        # Calcular IDF
        for term in self.vocabulary:
            self.idf[term] = math.log(self.num_docs / self.doc_freq[term])
        
        # Construir vectores TF-IDF para cada documento
        for doc_id in self.documents:
            vector = np.zeros(len(self.vocabulary))
            for i, term in enumerate(self.vocabulary):
                if doc_id in self.term_doc_freq[term]:
                    tf = 1 + math.log(self.term_doc_freq[term][doc_id])
                    vector[i] = tf * self.idf[term]
            
            # Normalizar vector
            norm = np.linalg.norm(vector)
            if norm > 0:
                vector = vector / norm
            
            self.doc_vectors[doc_id] = vector
    
    def search(self, query: str, top_k: int = 10) -> List[Tuple[int, float]]:
        """
        Realiza una búsqueda por ranking usando similitud coseno.
        
        Args:
            query (str): Consulta de texto libre
            top_k (int): Número máximo de resultados a retornar
            
        Returns:
            List[Tuple[int, float]]: Lista de tuplas (doc_id, score)
        """
        # Construir vector de consulta
        query_tokens = tokenize(query)
        query_tf = Counter(query_tokens)
        query_vector = np.zeros(len(self.vocabulary))
        
        for term, freq in query_tf.items():
            if term in self.vocabulary:
                idx = self.vocabulary.index(term)
                tf = 1 + math.log(freq)
                query_vector[idx] = tf * self.idf.get(term, 0)
        
        # Normalizar vector de consulta
        query_norm = np.linalg.norm(query_vector)
        if query_norm > 0:
            query_vector = query_vector / query_norm
        
        # Calcular similitudes
        scores = []
        for doc_id, doc_vector in self.doc_vectors.items():
            similarity = np.dot(query_vector, doc_vector)
            scores.append((doc_id, similarity))
        
        # Ordenar por similitud y retornar top-k
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]
    
    def get_document_terms(self, doc_id: int) -> List[Tuple[str, float]]:
        """
        Obtiene los términos más importantes de un documento según su peso TF-IDF.
        
        Args:
            doc_id (int): ID del documento
            
        Returns:
            List[Tuple[str, float]]: Lista de tuplas (término, peso)
        """
        if doc_id not in self.doc_vectors:
            return []
        
        vector = self.doc_vectors[doc_id]
        terms_weights = [(term, vector[i]) 
                        for i, term in enumerate(self.vocabulary)]
        
        return sorted(terms_weights, key=lambda x: x[1], reverse=True) 