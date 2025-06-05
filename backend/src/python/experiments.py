import time
from typing import Dict, List, Tuple
from text_processor import TextProcessor
from review_file_handler import ReviewFileHandler
from evaluator import Evaluator
import statistics
import json
from pathlib import Path
import copy

class ExperimentRunner:
    def __init__(self):
        self.review_handler = ReviewFileHandler()
        self.evaluator = Evaluator()
        self.results_dir = Path("experiment_results")
        self.results_dir.mkdir(exist_ok=True)
        
        # Verificar que hay reseñas cargadas
        self.verify_data()
        
    def verify_data(self):
        """Verifica que hay datos cargados en el sistema"""
        try:
            # Verificar que el procesador de texto está funcionando
            test_query = "auriculares"
            results = self.review_handler.search_reviews(test_query, 'tf_idf')
            print(f"\nVerificación del sistema:")
            print(f"- Reseñas disponibles: {len(self.review_handler.list_reviews())}")
            print(f"- Prueba de búsqueda '{test_query}': {len(results)} resultados")
            print(f"- Términos en índice: {len(self.review_handler.text_processor.inverted_index)}")
            print(f"- Documentos indexados: {len(self.review_handler.text_processor.document_lengths)}")
            
        except Exception as e:
            print(f"Error en la verificación de datos: {str(e)}")

    def measure_execution_time(self, func, *args, **kwargs) -> Tuple[any, float]:
        """
        Mide el tiempo de ejecución de una función
        Returns:
            Tuple(resultado, tiempo_en_segundos)
        """
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        return result, end_time - start_time

    def safe_mean(self, numbers: List[float]) -> float:
        """Calcula la media de forma segura"""
        try:
            return statistics.mean(numbers) if numbers else 0.0
        except Exception:
            return 0.0

    def safe_stats(self, numbers: List[float]) -> Dict:
        """Calcula estadísticas de forma segura"""
        try:
            if not numbers:
                return {
                    'min': 0.0,
                    'max': 0.0,
                    'mean': 0.0,
                    'median': 0.0
                }
            return {
                'min': min(numbers),
                'max': max(numbers),
                'mean': statistics.mean(numbers),
                'median': statistics.median(numbers)
            }
        except Exception:
            return {
                'min': 0.0,
                'max': 0.0,
                'mean': 0.0,
                'median': 0.0
            }

    def process_search_results(self, results) -> List[Dict]:
        """
        Procesa y estabiliza los resultados de búsqueda
        """
        if not results:
            return []
        try:
            # Crear una copia profunda y estable de los resultados
            processed = []
            for r in results:
                if isinstance(r, dict):
                    item = {
                        'id': str(r.get('id', '')),
                        'score': float(r.get('score', 0.0)),
                        'producto': str(r.get('producto', '')),
                        'categoria': str(r.get('categoria', '')),
                        'puntuacion': float(r.get('puntuacion', 0.0))
                    }
                    processed.append(item)
            
            print(f"\nResultados procesados: {len(processed)}")
            if processed:
                print(f"Ejemplo de resultado: {processed[0]}")
            return processed
            
        except Exception as e:
            print(f"Error procesando resultados: {str(e)}")
            return []

    def run_timing_experiments(self, queries: List[str], search_type: str = 'tf_idf') -> Dict:
        """
        Ejecuta experimentos de medición de tiempos para diferentes operaciones
        Args:
            queries: Lista de consultas a probar
            search_type: Tipo de búsqueda ('boolean' o 'tf_idf')
        """
        print(f"\nIniciando experimentos de tiempo para {search_type}...")
        
        timing_results = {
            'boolean_search': [],
            'tfidf_search': []
        }
        
        for query in queries:
            try:
                print(f"\nProcesando query: {query}")
                
                # Ejecutar búsqueda
                results, time_taken = self.measure_execution_time(
                    self.review_handler.search_reviews,
                    query, search_type
                )
                processed_results = self.process_search_results(results)
                print(f"- Resultados {search_type}: {len(processed_results)}")
                
                timing_results[f'{search_type}_search'].append({
                    'query': query,
                    'time': time_taken,
                    'num_results': len(processed_results)
                })
                
            except Exception as e:
                print(f"Error en query '{query}': {str(e)}")
                continue
        
        return timing_results

    def evaluate_synonym_impact(self, necesidades: List[Dict]) -> Dict:
        """
        Evalúa el impacto de los sinónimos en las búsquedas
        Args:
            necesidades: Lista de necesidades de información
        """
        results = {
            'per_need': {},
            'overall': {
                'with_synonyms': {'precision': 0.0, 'recall': 0.0, 'f1': 0.0},
                'without_synonyms': {'precision': 0.0, 'recall': 0.0, 'f1': 0.0}
            }
        }
        
        for need in necesidades:
            need_id = need['id']
            print(f"\nEvaluando necesidad {need_id}: {need['descripcion']}")
            
            # Búsqueda con sinónimos (por defecto)
            results_with_syn = self.review_handler.search_reviews(
                need['consulta_libre'], 
                'tf_idf'
            )
            processed_with_syn = self.process_search_results(results_with_syn)
            
            # Búsqueda sin sinónimos
            self.review_handler.text_processor.use_synonyms = False
            results_without_syn = self.review_handler.search_reviews(
                need['consulta_libre'], 
                'tf_idf'
            )
            processed_without_syn = self.process_search_results(results_without_syn)
            self.review_handler.text_processor.use_synonyms = True
            
            # Evaluar resultados
            scores_with_syn = {str(r['id']): r['score'] for r in processed_with_syn}
            scores_without_syn = {str(r['id']): r['score'] for r in processed_without_syn}
            
            metrics_with_syn = self.evaluator.evaluate_ranked_search({need_id: scores_with_syn})['per_query'].get(need_id, {})
            metrics_without_syn = self.evaluator.evaluate_ranked_search({need_id: scores_without_syn})['per_query'].get(need_id, {})
            
            results['per_need'][need_id] = {
                'descripcion': need['descripcion'],
                'with_synonyms': {
                    'num_results': len(processed_with_syn),
                    'metrics': metrics_with_syn
                },
                'without_synonyms': {
                    'num_results': len(processed_without_syn),
                    'metrics': metrics_without_syn
                }
            }
            
            # Actualizar métricas globales
            for metric in ['precision', 'recall', 'f1']:
                results['overall']['with_synonyms'][metric] += metrics_with_syn.get(metric, 0.0)
                results['overall']['without_synonyms'][metric] += metrics_without_syn.get(metric, 0.0)
        
        # Calcular promedios globales
        num_needs = len(necesidades)
        if num_needs > 0:
            for metric_type in results['overall']:
                for metric in results['overall'][metric_type]:
                    results['overall'][metric_type][metric] /= num_needs
        
        return results

    def analyze_thresholds(self, necesidades: List[Dict]) -> Dict:
        """
        Analiza el impacto de diferentes umbrales de similitud
        Args:
            necesidades: Lista de necesidades de información
        """
        thresholds = [0.05, 0.07, 0.09, 0.11, 0.15, 0.30, 0.50]
        results = {
            'per_threshold': {},
            'per_need': {},
            'overall': {}
        }
        
        for threshold in thresholds:
            print(f"\nEvaluando umbral {threshold}")
            self.evaluator.similarity_threshold = threshold
            
            threshold_metrics = {
                'precision': 0.0,
                'recall': 0.0,
                'f1': 0.0,
                'num_results': 0
            }
            
            for need in necesidades:
                need_id = need['id']
                print(f"- Procesando necesidad {need_id}")
                
                # Realizar búsqueda
                search_results = self.review_handler.search_reviews(
                    need['consulta_libre'],
                    'tf_idf'
                )
                processed_results = self.process_search_results(search_results)
                
                # Evaluar resultados
                scores = {str(r['id']): r['score'] for r in processed_results}
                metrics = self.evaluator.evaluate_ranked_search({need_id: scores})['per_query'].get(need_id, {})
                
                # Guardar resultados por necesidad
                if need_id not in results['per_need']:
                    results['per_need'][need_id] = {}
                
                results['per_need'][need_id][str(threshold)] = {
                    'metrics': metrics,
                    'num_results': len(processed_results)
                }
                
                # Actualizar métricas del umbral
                threshold_metrics['precision'] += metrics.get('precision', 0.0)
                threshold_metrics['recall'] += metrics.get('recall', 0.0)
                threshold_metrics['f1'] += metrics.get('f1', 0.0)
                threshold_metrics['num_results'] += len(processed_results)
            
            # Calcular promedios para el umbral
            num_needs = len(necesidades)
            if num_needs > 0:
                for metric in threshold_metrics:
                    if metric != 'num_results':
                        threshold_metrics[metric] /= num_needs
            
            results['per_threshold'][str(threshold)] = threshold_metrics
        
        # Restaurar umbral original
        self.evaluator.similarity_threshold = 0.15
        
        return results

    def _save_results(self, filename: str, results: Dict):
        """Guarda resultados en un archivo JSON"""
        try:
            filepath = self.results_dir / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"\nResultados guardados en {filepath}")
        except Exception as e:
            print(f"Error guardando resultados: {str(e)}")

def run_all_experiments():
    """
    Ejecuta todos los experimentos y genera informes
    """
    try:
        print("\nIniciando suite de experimentos...")
        runner = ExperimentRunner()
        
        print("\n1. Ejecutando experimentos de tiempo...")
        timing_results = runner.run_timing_experiments(["auriculares", "auriculares AND bateria", "auriculares AND (bateria OR duracion) AND NOT malo"])
        
        print("\n2. Evaluando impacto de sinónimos...")
        synonym_results = runner.evaluate_synonym_impact([
            {"id": "1", "descripcion": "auriculares batería", "consulta_libre": "auriculares batería"},
            {"id": "2", "descripcion": "buenos cascos", "consulta_libre": "buenos cascos"},
            {"id": "3", "descripcion": "calidad sonido", "consulta_libre": "calidad sonido"}
        ])
        
        print("\n3. Analizando umbrales de relevancia...")
        threshold_results = runner.analyze_thresholds([
            {"id": "1", "descripcion": "auriculares con buena batería", "consulta_libre": "auriculares con buena batería"},
            {"id": "2", "descripcion": "productos con buena calidad de sonido", "consulta_libre": "productos con buena calidad de sonido"},
            {"id": "3", "descripcion": "productos con cancelación de ruido", "consulta_libre": "productos con cancelación de ruido"}
        ])
        
        print("\nTodos los experimentos completados. Resultados guardados en /experiment_results/")
        
        return {
            'timing': timing_results,
            'synonyms': synonym_results,
            'thresholds': threshold_results
        }
    except Exception as e:
        print(f"Error ejecutando experimentos: {str(e)}")
        return {
            'error': str(e),
            'timing': {},
            'synonyms': {},
            'thresholds': {}
        }

if __name__ == "__main__":
    run_all_experiments() 