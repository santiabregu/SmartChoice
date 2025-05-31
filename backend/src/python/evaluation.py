"""
Módulo para evaluar el rendimiento del sistema de recuperación de información.
"""

from typing import List, Set, Dict
import json
import math

def load_information_needs(file_path: str) -> List[dict]:
    """Carga las necesidades de información desde un archivo JSON"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['necesidades']

def precision(retrieved: Set[str], relevant: Set[str]) -> float:
    """
    Calcula la precisión: fracción de documentos recuperados que son relevantes
    precision = |relevant ∩ retrieved| / |retrieved|
    """
    if not retrieved:
        return 0.0
    return len(relevant & retrieved) / len(retrieved)

def recall(retrieved: Set[str], relevant: Set[str]) -> float:
    """
    Calcula la exhaustividad: fracción de documentos relevantes que fueron recuperados
    recall = |relevant ∩ retrieved| / |relevant|
    """
    if not relevant:
        return 0.0
    return len(relevant & retrieved) / len(relevant)

def f1_score(precision_val: float, recall_val: float) -> float:
    """
    Calcula la medida F1: media armónica de precisión y exhaustividad
    F1 = 2 * (precision * recall) / (precision + recall)
    """
    if precision_val == 0 and recall_val == 0:
        return 0.0
    return 2 * (precision_val * recall_val) / (precision_val + recall_val)

def average_precision(retrieved_ranked: List[str], relevant: Set[str]) -> float:
    """
    Calcula la precisión media para una lista ordenada de resultados
    AP = Σ(P(k) * rel(k)) / |relevant|
    donde P(k) es la precisión en el corte k y rel(k) es 1 si el documento k es relevante
    """
    if not relevant:
        return 0.0
        
    score = 0.0
    num_hits = 0
    
    for i, doc_id in enumerate(retrieved_ranked, 1):
        if doc_id in relevant:
            num_hits += 1
            score += num_hits / i
            
    return score / len(relevant)

def mean_average_precision(results: List[Dict[str, List[str]]], needs: List[dict]) -> float:
    """
    Calcula el MAP sobre todas las necesidades de información
    MAP = Σ(AP) / N
    donde N es el número de necesidades de información
    """
    if not results or not needs:
        return 0.0
        
    total_ap = 0.0
    
    for result, need in zip(results, needs):
        retrieved_ranked = list(result.keys())  # Para búsquedas con ranking
        relevant = set(need['documentos_relevantes'])
        total_ap += average_precision(retrieved_ranked, relevant)
        
    return total_ap / len(needs)

def evaluate_boolean_search(results: List[Set[str]], needs: List[dict]) -> Dict[str, float]:
    """
    Evalúa los resultados de búsquedas booleanas usando precisión y exhaustividad
    """
    total_precision = 0.0
    total_recall = 0.0
    total_f1 = 0.0
    
    for result, need in zip(results, needs):
        relevant = set(need['documentos_relevantes'])
        p = precision(result, relevant)
        r = recall(result, relevant)
        f1 = f1_score(p, r)
        
        total_precision += p
        total_recall += r
        total_f1 += f1
        
    n = len(needs)
    return {
        'precision': total_precision / n,
        'recall': total_recall / n,
        'f1': total_f1 / n
    }

def evaluate_ranked_search(results: List[Dict[str, float]], needs: List[dict]) -> Dict[str, float]:
    """
    Evalúa los resultados de búsquedas con ranking usando MAP
    """
    map_score = mean_average_precision(results, needs)
    
    # También calculamos precisión y recall usando un umbral
    threshold = 0.1  # Documentos con score > 0.1 se consideran recuperados
    
    results_sets = []
    for result in results:
        retrieved = {doc_id for doc_id, score in result.items() if score > threshold}
        results_sets.append(retrieved)
    
    bool_metrics = evaluate_boolean_search(results_sets, needs)
    
    return {
        'map': map_score,
        'precision': bool_metrics['precision'],
        'recall': bool_metrics['recall'],
        'f1': bool_metrics['f1']
    } 