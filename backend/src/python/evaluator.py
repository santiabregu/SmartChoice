import json
from typing import List, Set, Dict
import math
from pathlib import Path
import re

class Evaluator:
    def __init__(self, similarity_threshold: float = 0.05):
        """
        Inicializa el evaluador con pseudo-relevance feedback y soporte de sinónimos
        Args:
            similarity_threshold: Score mínimo para considerar un documento como relevante
        """
        self.similarity_threshold = similarity_threshold
        self.top_k = 2  # Reducido a 2 para ser más selectivo
        self.sinonimos = self._load_sinonimos()
        
        # Palabras positivas generales
        self.positive_words = {
            'buena', 'bueno', 'excelente', 'gran', 'larga', 'perfecta', 'increíble',
            'impresionante', 'superior', 'magnífica', 'sobresaliente', 'útil',
            'eficiente', 'eficaz', 'dura', 'aguanta', 'funciona', 'recomendable',
            'satisfecho', 'satisfactoria', 'vale la pena', 'potente', 'estable'
        }
        
        # Palabras negativas generales
        self.negative_words = {
            'mala', 'malo', 'poca', 'poco', 'corta', 'corto', 'deficiente', 'pobre',
            'débil', 'insuficiente', 'mediocre', 'regular', 'limitada', 'limitado',
            'decepcionante', 'falla', 'problema', 'error', 'defecto', 'no recomendable',
            'insatisfecho', 'inestable'
        }
            
    def _load_sinonimos(self) -> Dict:
        """Carga el diccionario de sinónimos"""
        sinonimos_path = Path(__file__).parent / "data" / "sinonimos.json"
        try:
            with open(sinonimos_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("sinonimos", {})
        except FileNotFoundError:
            print("Archivo de sinónimos no encontrado")
            return {}
            
    def _generate_positive_patterns(self) -> List[str]:
        """Genera patrones positivos usando sinónimos"""
        base_patterns = [
            'buena', 'excelente', 'gran', 'larga', 'perfecta', 'increíble',
            'impresionante', 'superior', 'magnífica', 'sobresaliente'
        ]
        
        # Patrones específicos para duración
        duration_patterns = [
            'dura más de', 'dura hasta', 'autonomía de',
            'duración de', 'aguanta', 'larga duración'
        ]
        
        features = [
            'batería', 'duración', 'calidad', 'sonido', 'pantalla', 'rendimiento',
            'comodidad', 'diseño', 'construcción'
        ]
        
        patterns = []
        # Añadir patrones base
        for pattern in base_patterns:
            for feature in features:
                patterns.append(f"{pattern} {feature}")
                if feature in self.sinonimos:
                    for sinonimo in self.sinonimos[feature]:
                        patterns.append(f"{pattern} {sinonimo}")
        
        # Añadir patrones específicos de duración
        for pattern in duration_patterns:
            patterns.append(pattern)
            # Añadir variantes con números
            patterns.append(f"{pattern} [0-9]+ horas")
            patterns.append(f"{pattern} un día")
            patterns.append(f"{pattern} varios días")
        
        return patterns
    
    def _generate_negative_patterns(self) -> List[str]:
        """Genera patrones negativos usando sinónimos"""
        base_patterns = [
            'mala', 'poca', 'corta', 'deficiente', 'pobre', 'débil',
            'insuficiente', 'mediocre', 'regular', 'limitada'
        ]
        
        features = [
            'batería', 'duración', 'calidad', 'sonido', 'pantalla', 'rendimiento',
            'comodidad', 'diseño', 'construcción' 
        ]
        
        patterns = []
        for pattern in base_patterns:
            for feature in features:
                # Añadir patrón base
                patterns.append(f"{pattern} {feature}")
                
                # Añadir variantes con sinónimos
                if feature in self.sinonimos:
                    for sinonimo in self.sinonimos[feature]:
                        patterns.append(f"{pattern} {sinonimo}")
        
        return patterns

    def expand_query_terms(self, query_terms: List[str]) -> Set[str]:
        """
        Expande los términos de búsqueda con sus sinónimos
        Args:
            query_terms: Lista de términos de búsqueda
        Returns:
            Conjunto de términos expandidos con sinónimos
        """
        expanded_terms = set(query_terms)
        
        for term in query_terms:
            if term in self.sinonimos:
                expanded_terms.update(self.sinonimos[term])
        
        return expanded_terms

    def get_relevant_docs(self, ranked_results: Dict[str, float]) -> Set[str]:
        """
        Determina documentos relevantes usando pseudo-relevance feedback
        Args:
            ranked_results: Diccionario de doc_id -> score
        Returns:
            Conjunto de IDs de documentos considerados relevantes
        """
        # Ordenar documentos por score
        sorted_docs = sorted(ranked_results.items(), key=lambda x: x[1], reverse=True)
        
        relevant_docs = set()
        
        # Considerar documentos relevantes si:
        # 1. Están en el top K y superan el threshold
        # 2. O tienen un score muy alto (1.5x threshold)
        high_score_threshold = self.similarity_threshold * 1.5
        
        for doc_id, score in sorted_docs:
            if len(relevant_docs) < self.top_k and score >= self.similarity_threshold:
                relevant_docs.add(doc_id)
            elif score >= high_score_threshold:
                relevant_docs.add(doc_id)
                
        return relevant_docs

    def get_relevant_docs_boolean(self, results: List[Dict], query_terms: List[str] = None) -> Set[str]:
        """
        Para búsquedas booleanas, consideramos relevantes los documentos que:
        1. Tienen una puntuación decente (≥ 3)
        2. O contienen términos buscados con menciones positivas
        3. Y no tienen menciones negativas de los términos
        """
        relevant_docs = set()
        expanded_terms = self.expand_query_terms(query_terms) if query_terms else set()
        
        for doc in results:
            review_text = doc.get('resena', '').lower()
            rating = float(doc.get('puntuacion', 0))
            
            # Contar términos que coinciden
            matching_terms = sum(1 for term in expanded_terms if term.lower() in review_text)
            
            # Buscar palabras positivas cerca de los términos buscados
            has_positive = False
            has_negative = False
            
            # Dividir el texto en palabras
            words = review_text.split()
            
            # Buscar términos de búsqueda y palabras positivas/negativas cercanas
            for i, word in enumerate(words):
                if word in expanded_terms:
                    # Mirar 5 palabras antes y después
                    context = words[max(0, i-5):min(len(words), i+6)]
                    has_positive = has_positive or any(pos in context for pos in self.positive_words)
                    has_negative = has_negative or any(neg in context for neg in self.negative_words)
            
            # Un documento es relevante si:
            # - Has good rating (≥ 3) OR has positive mentions OR has multiple query terms
            # - AND doesn't have negative mentions
            if (rating >= 3 or has_positive or matching_terms >= 2) and not has_negative:
                relevant_docs.add(doc['review_id'])
                
        return relevant_docs

    def get_nonrelevant_docs(self, ranked_results: Dict[str, float], 
                            low_threshold: float = 0.05) -> Set[str]:
        """
        Determina documentos no relevantes basado en scores bajos
        """
        return {doc_id for doc_id, score in ranked_results.items() 
                if score < low_threshold}
    
    def get_nonrelevant_docs_boolean(self, results: List[Dict], relevant_docs: Set[str]) -> Set[str]:
        """
        Para búsquedas booleanas, los documentos no relevantes son aquellos que:
        1. No están en el conjunto de relevantes
        2. Mencionan negativamente los términos buscados
        """
        nonrelevant_docs = set()
        
        for doc in results:
            if doc['id'] not in relevant_docs:
                if 'resena' in doc:
                    text = doc['resena'].lower()
                    negative_patterns = [
                        'mala batería', 'poca duración', 'dura poco',
                        'batería corta', 'apenas dura'
                    ]
                    if any(pattern in text for pattern in negative_patterns):
                        nonrelevant_docs.add(doc['id'])
        
        return nonrelevant_docs
    
    def calculate_precision(self, retrieved_docs: Set[str], relevant_docs: Set[str]) -> float:
        """Calcula la precisión: fracción de documentos recuperados que son relevantes"""
        if not retrieved_docs:
            return 0.0
        return len(retrieved_docs & relevant_docs) / len(retrieved_docs)
    
    def calculate_recall(self, retrieved_docs: Set[str], relevant_docs: Set[str]) -> float:
        """Calcula el recall: fracción de documentos relevantes que fueron recuperados"""
        if not relevant_docs:
            return 0.0
        return len(retrieved_docs & relevant_docs) / len(relevant_docs)
    
    def calculate_f1(self, precision: float, recall: float) -> float:
        """Calcula el F1-score: media armónica de precisión y recall"""
        if precision + recall == 0:
            return 0.0
        return 2 * (precision * recall) / (precision + recall)
    
    def calculate_average_precision(self, ranked_docs: List[str], relevant_docs: Set[str]) -> float:
        """Calcula la precisión media para una lista ordenada de documentos"""
        if not relevant_docs:
            return 0.0
            
        running_precision = 0.0
        relevant_found = 0
        
        for i, doc_id in enumerate(ranked_docs, 1):
            if doc_id in relevant_docs:
                relevant_found += 1
                precision_at_k = relevant_found / i
                running_precision += precision_at_k
        
        return running_precision / len(relevant_docs) if relevant_found > 0 else 0.0
    
    def evaluate_boolean_search(self, results: List[Dict], query_terms: List[str] = None) -> Dict:
        """
        Evalúa los resultados de búsquedas booleanas
        Args:
            results: Lista de documentos recuperados
            query_terms: Términos de búsqueda originales
        Returns:
            Dict con métricas
        """
        # Obtener IDs de documentos recuperados
        retrieved = {doc['id'] for doc in results}
        
        # Determinar documentos relevantes basado en contenido y puntuación
        relevant_docs = self.get_relevant_docs_boolean(results, query_terms)
        nonrelevant_docs = self.get_nonrelevant_docs_boolean(results, relevant_docs)
        
        # Calcular métricas
        precision = self.calculate_precision(retrieved, relevant_docs)
        recall = self.calculate_recall(retrieved, relevant_docs)
        f1 = self.calculate_f1(precision, recall)
        
        # Para average precision, usamos el orden en que vienen los resultados
        ranked_docs = [doc['id'] for doc in results]
        ap = self.calculate_average_precision(ranked_docs, relevant_docs)
        
        return {
            'average_precision': ap,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'retrieved_count': len(retrieved),
            'relevant_count': len(relevant_docs),
            'nonrelevant_count': len(nonrelevant_docs),
            'retrieved_and_relevant': len(retrieved & relevant_docs),
            'expanded_terms': list(self.expand_query_terms(query_terms)) if query_terms else []
        }
    
    def evaluate_ranked_search(self, search_results: Dict[str, Dict[str, float]], 
                             query_terms: Dict[str, List[str]] = None) -> Dict:
        """
        Evalúa los resultados de búsquedas con ranking usando pseudo-relevance feedback
        Args:
            search_results: Dict[query_id -> Dict[doc_id -> score]]
            query_terms: Dict[query_id -> List[términos]]
        Returns:
            Dict con métricas incluyendo MAP
        """
        metrics = {
            'per_query': {},
            'overall': {
                'map': 0.0,
                'precision': 0.0,
                'recall': 0.0,
                'f1': 0.0
            }
        }
        
        total_queries = 0
        
        for query_id, doc_scores in search_results.items():
            # Usar pseudo-relevance feedback para determinar documentos relevantes
            relevant_docs = self.get_relevant_docs(doc_scores)
            nonrelevant_docs = self.get_nonrelevant_docs(doc_scores)
            
            # Convertir scores a lista ordenada de documentos
            ranked_docs = [doc_id for doc_id, _ in 
                         sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)]
            
            retrieved = set(ranked_docs)
            
            # Expandir términos si están disponibles
            expanded_terms = []
            if query_terms and query_id in query_terms:
                expanded_terms = list(self.expand_query_terms(query_terms[query_id]))
            
            ap = self.calculate_average_precision(ranked_docs, relevant_docs)
            precision = self.calculate_precision(retrieved, relevant_docs)
            recall = self.calculate_recall(retrieved, relevant_docs)
            f1 = self.calculate_f1(precision, recall)
            
            metrics['per_query'][query_id] = {
                'average_precision': ap,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'retrieved_count': len(retrieved),
                'relevant_count': len(relevant_docs),
                'nonrelevant_count': len(nonrelevant_docs),
                'retrieved_and_relevant': len(retrieved & relevant_docs),
                'expanded_terms': expanded_terms
            }
            
            # Actualizar métricas globales
            metrics['overall']['map'] += ap
            metrics['overall']['precision'] += precision
            metrics['overall']['recall'] += recall
            metrics['overall']['f1'] += f1
            total_queries += 1
        
        # Calcular promedios
        if total_queries > 0:
            metrics['overall']['map'] /= total_queries
            metrics['overall']['precision'] /= total_queries
            metrics['overall']['recall'] /= total_queries
            metrics['overall']['f1'] /= total_queries
            
        return metrics 