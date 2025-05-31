import json
from typing import List, Set, Dict
import math

class Evaluator:
    def __init__(self, necesidades_file: str = "data/necesidades_informacion.json"):
        """Inicializa el evaluador cargando las necesidades de información"""
        with open(necesidades_file, 'r', encoding='utf-8') as f:
            self.necesidades = json.load(f)['necesidades']
            
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
    
    def evaluate_boolean_search(self, search_results: Dict[str, List[str]]) -> Dict:
        """
        Evalúa los resultados de búsquedas booleanas
        Args:
            search_results: Dict[necesidad_id -> List[doc_id]]
        Returns:
            Dict con métricas agregadas
        """
        metrics = {
            'per_query': {},
            'overall': {
                'precision': 0.0,
                'recall': 0.0,
                'f1': 0.0
            }
        }
        
        total_queries = 0
        
        for necesidad in self.necesidades:
            nid = necesidad['id']
            if nid not in search_results:
                continue
                
            retrieved = set(search_results[nid])
            relevant = set(necesidad['documentos_relevantes'])
            
            precision = self.calculate_precision(retrieved, relevant)
            recall = self.calculate_recall(retrieved, relevant)
            f1 = self.calculate_f1(precision, recall)
            
            metrics['per_query'][nid] = {
                'precision': precision,
                'recall': recall,
                'f1': f1,
                'retrieved_count': len(retrieved),
                'relevant_count': len(relevant),
                'retrieved_and_relevant': len(retrieved & relevant)
            }
            
            metrics['overall']['precision'] += precision
            metrics['overall']['recall'] += recall
            metrics['overall']['f1'] += f1
            total_queries += 1
        
        # Calcular promedios
        if total_queries > 0:
            metrics['overall']['precision'] /= total_queries
            metrics['overall']['recall'] /= total_queries
            metrics['overall']['f1'] /= total_queries
            
        return metrics
    
    def evaluate_ranked_search(self, search_results: Dict[str, List[str]]) -> Dict:
        """
        Evalúa los resultados de búsquedas con ranking
        Args:
            search_results: Dict[necesidad_id -> List[doc_id]] (documentos ordenados por relevancia)
        Returns:
            Dict con métricas incluyendo MAP
        """
        metrics = {
            'per_query': {},
            'overall': {
                'map': 0.0,
                'precision': 0.0,
                'recall': 0.0
            }
        }
        
        total_queries = 0
        
        for necesidad in self.necesidades:
            nid = necesidad['id']
            if nid not in search_results:
                continue
                
            ranked_docs = search_results[nid]
            relevant = set(necesidad['documentos_relevantes'])
            retrieved = set(ranked_docs)
            
            ap = self.calculate_average_precision(ranked_docs, relevant)
            precision = self.calculate_precision(retrieved, relevant)
            recall = self.calculate_recall(retrieved, relevant)
            
            metrics['per_query'][nid] = {
                'average_precision': ap,
                'precision': precision,
                'recall': recall,
                'retrieved_count': len(retrieved),
                'relevant_count': len(relevant),
                'retrieved_and_relevant': len(retrieved & relevant)
            }
            
            metrics['overall']['map'] += ap
            metrics['overall']['precision'] += precision
            metrics['overall']['recall'] += recall
            total_queries += 1
        
        # Calcular promedios
        if total_queries > 0:
            metrics['overall']['map'] /= total_queries
            metrics['overall']['precision'] /= total_queries
            metrics['overall']['recall'] /= total_queries
            
        return metrics 