import json
from typing import List, Set, Dict
import math
from pathlib import Path

class Evaluator:
    def __init__(self, similarity_threshold: float = 0.15):
        """
        Inicializa el evaluador con pseudo-relevance feedback y soporte de sinónimos
        Args:
            similarity_threshold: Score mínimo para considerar un documento como relevante
        """
        self.similarity_threshold = similarity_threshold
        self.top_k = 2  # Reducido a 2 para ser más selectivo
        self.sinonimos = self._load_sinonimos()
        self.positive_patterns = self._generate_positive_patterns()
        self.negative_patterns = self._generate_negative_patterns()
            
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

    def get_relevant_docs_boolean(self, results: List[Dict], query_terms: List[str] = None) -> Set[str]:
        """
        Para búsquedas booleanas, consideramos relevantes los documentos que:
        1. Contienen los términos buscados o sus sinónimos
        2. Tienen una puntuación alta o mencionan positivamente los términos
        Args:
            results: Lista de documentos
            query_terms: Términos de búsqueda originales
        """
        relevant_docs = set()
        expanded_terms = self.expand_query_terms(query_terms) if query_terms else set()
        
        for doc in results:
            # Consideramos relevante si:
            # - Tiene puntuación alta (≥ 4.0)
            # - O menciona positivamente los términos buscados
            if doc.get('puntuacion', 0) >= 4.0:
                relevant_docs.add(doc['id'])
            elif 'resena' in doc:
                text = doc['resena'].lower()
                
                # Verificar términos expandidos
                terms_found = any(term.lower() in text for term in expanded_terms)
                
                # Buscar menciones positivas
                has_positive = any(pattern in text for pattern in self.positive_patterns)
                # Buscar menciones negativas
                has_negative = any(pattern in text for pattern in self.negative_patterns)
                
                if (terms_found or has_positive) and not has_negative:
                    relevant_docs.add(doc['id'])
        
        return relevant_docs
            
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
        
        # Considerar los top K documentos con score sobre el threshold como relevantes
        for doc_id, score in sorted_docs[:self.top_k]:
            if score >= self.similarity_threshold:
                relevant_docs.add(doc_id)
                
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