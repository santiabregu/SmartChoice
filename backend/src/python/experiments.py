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
            # Cargar algunas reseñas de ejemplo si no hay
            example_reviews = [
                {
                    "id": "1",
                    "producto": "Auriculares Sony WH-1000XM4",
                    "categoria": "Tecnología",
                    "resena": "Excelente calidad de sonido y la batería dura más de 20 horas. La cancelación de ruido es impresionante.",
                    "puntuacion": 4.5,
                    "website": {
                        "nombre": "Amazon",
                        "url": "https://www.amazon.es/review/123"
                    }
                },
                {
                    "id": "2",
                    "producto": "Auriculares Bose QC35",
                    "categoria": "Tecnología",
                    "resena": "Buena batería y cancelación de ruido efectiva. Audio de calidad.",
                    "puntuacion": 4.0,
                    "website": {
                        "nombre": "Amazon",
                        "url": "https://www.amazon.es/review/456"
                    }
                }
            ]
            
            # Verificar si hay reseñas y cargar ejemplos si no hay
            if not self.review_handler.list_reviews():
                print("No se encontraron reseñas. Cargando ejemplos...")
                for review in example_reviews:
                    self.review_handler.save_review(review)
                print(f"Se cargaron {len(example_reviews)} reseñas de ejemplo")
                
                # Procesar las reseñas para actualizar el índice
                print("Procesando reseñas...")
                self.review_handler.process_reviews()
            
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

    def run_timing_experiments(self) -> Dict:
        """
        Ejecuta experimentos de medición de tiempos para diferentes operaciones
        """
        print("\nIniciando experimentos de tiempo...")
        
        timing_results = {
            'indexing': [],
            'boolean_search': [],
            'tfidf_search': []
        }
        
        test_queries = [
            "auriculares",
            "auriculares AND bateria",
            "auriculares AND (bateria OR duracion) AND NOT malo"
        ]
        
        for query in test_queries:
            try:
                print(f"\nProcesando query: {query}")
                
                # Búsqueda booleana
                results_bool, time_bool = self.measure_execution_time(
                    self.review_handler.search_reviews,
                    query, 'boolean'
                )
                bool_results = self.process_search_results(results_bool)
                print(f"- Resultados booleanos: {len(bool_results)}")
                
                timing_results['boolean_search'].append({
                    'query': query,
                    'time': time_bool,
                    'num_results': len(bool_results)
                })
                
                # Búsqueda TF-IDF
                results_tfidf, time_tfidf = self.measure_execution_time(
                    self.review_handler.search_reviews,
                    query, 'tf_idf'
                )
                tfidf_results = self.process_search_results(results_tfidf)
                print(f"- Resultados TF-IDF: {len(tfidf_results)}")
                
                timing_results['tfidf_search'].append({
                    'query': query,
                    'time': time_tfidf,
                    'num_results': len(tfidf_results)
                })
            except Exception as e:
                print(f"Error en query '{query}': {str(e)}")
                continue
        
        # Calcular estadísticas en una copia del diccionario
        timing_copy = copy.deepcopy(timing_results)
        stats_results = {}
        
        for operation in timing_copy:
            if timing_copy[operation]:
                times = [r['time'] for r in timing_copy[operation]]
                stats_results[f"{operation}_stats"] = self.safe_stats(times)
        
        # Crear un nuevo diccionario con los resultados combinados
        final_results = {**timing_results, **stats_results}
        
        self._save_results('timing_experiments.json', final_results)
        return final_results

    def evaluate_synonym_impact(self) -> Dict:
        """
        Evalúa el impacto de usar sinónimos en la búsqueda
        """
        test_pairs = [
            ("auriculares batería", "audifonos duración"),
            ("buenos cascos", "buenos auriculares"),
            ("calidad sonido", "calidad audio")
        ]
        
        results = {
            'with_synonyms': [],
            'without_synonyms': [],
            'comparisons': []
        }
        
        for query1, query2 in test_pairs:
            try:
                # Procesar resultados de manera segura
                results1 = self.process_search_results(
                    self.review_handler.search_reviews(query1, 'tf_idf')
                )
                results2 = self.process_search_results(
                    self.review_handler.search_reviews(query2, 'tf_idf')
                )
                
                # Usar conjuntos de IDs estables
                docs1 = {r['id'] for r in results1}
                docs2 = {r['id'] for r in results2}
                overlap = len(docs1 & docs2)
                union_size = len(docs1 | docs2)
                
                comparison = {
                    'query_pair': (query1, query2),
                    'overlap': overlap,
                    'results1_count': len(results1),
                    'results2_count': len(results2),
                    'unique_to_1': len(docs1 - docs2),
                    'unique_to_2': len(docs2 - docs1),
                    'jaccard_similarity': overlap / union_size if union_size > 0 else 0.0
                }
                
                results['comparisons'].append(comparison)
                
                # Evaluar cada consulta por separado
                for query, res in [(query1, results1), (query2, results2)]:
                    if res:
                        scores = {r['id']: r['score'] for r in res}
                        metrics = self.evaluator.evaluate_ranked_search({query: scores})
                        if query in metrics.get('per_query', {}):
                            results['with_synonyms'].append({
                                'query': query,
                                'metrics': copy.deepcopy(metrics['per_query'][query])
                            })
            except Exception as e:
                print(f"Error en par de consultas '{query1}' - '{query2}': {str(e)}")
                continue
        
        # Calcular estadísticas globales en una copia
        results_copy = copy.deepcopy(results)
        if results_copy['with_synonyms']:
            try:
                precisions = []
                recalls = []
                overlaps = []
                jaccards = []
                
                for r in results_copy['with_synonyms']:
                    if 'metrics' in r:
                        precisions.append(r['metrics'].get('precision', 0.0))
                        recalls.append(r['metrics'].get('recall', 0.0))
                
                for c in results_copy['comparisons']:
                    overlaps.append(c.get('overlap', 0))
                    jaccards.append(c.get('jaccard_similarity', 0.0))
                
                results['global_stats'] = {
                    'mean_precision': self.safe_mean(precisions),
                    'mean_recall': self.safe_mean(recalls),
                    'mean_overlap': self.safe_mean(overlaps),
                    'mean_jaccard': self.safe_mean(jaccards)
                }
            except Exception as e:
                print(f"Error calculando estadísticas globales: {str(e)}")
                results['global_stats'] = {
                    'mean_precision': 0.0,
                    'mean_recall': 0.0,
                    'mean_overlap': 0.0,
                    'mean_jaccard': 0.0
                }
        
        self._save_results('synonym_impact.json', results)
        return results

    def analyze_thresholds(self) -> Dict:
        """
        Analiza el impacto de diferentes umbrales de relevancia
        """
        thresholds = [0.05, 0.15, 0.30]
        test_queries = [
            "auriculares con buena batería",
            "productos con buena calidad de sonido",
            "productos con cancelación de ruido"
        ]
        
        results = {
            'per_threshold': {},
            'comparisons': []
        }
        
        for threshold in thresholds:
            try:
                evaluator = Evaluator(similarity_threshold=threshold)
                threshold_results = []
                
                for query in test_queries:
                    try:
                        # Procesar resultados de manera segura
                        search_results = self.process_search_results(
                            self.review_handler.search_reviews(query, 'tf_idf')
                        )
                        
                        if search_results:
                            scores = {r['id']: r['score'] for r in search_results}
                            metrics = evaluator.evaluate_ranked_search({query: scores})
                            
                            if query in metrics.get('per_query', {}):
                                all_scores = [r['score'] for r in search_results]
                                score_stats = self.safe_stats(all_scores)
                                
                                threshold_results.append({
                                    'query': query,
                                    'metrics': copy.deepcopy(metrics['per_query'][query]),
                                    'score_stats': score_stats,
                                    'num_results': len(search_results),
                                    'num_above_threshold': len([s for s in all_scores if s >= threshold])
                                })
                    except Exception as e:
                        print(f"Error en query '{query}' con umbral {threshold}: {str(e)}")
                        continue
                
                results['per_threshold'][str(threshold)] = threshold_results
                
                # Calcular estadísticas globales para este umbral
                if threshold_results:
                    try:
                        threshold_copy = copy.deepcopy(threshold_results)
                        
                        precisions = []
                        recalls = []
                        num_results = []
                        above_threshold = []
                        
                        for r in threshold_copy:
                            if 'metrics' in r:
                                precisions.append(r['metrics'].get('precision', 0.0))
                                recalls.append(r['metrics'].get('recall', 0.0))
                            num_results.append(r.get('num_results', 0))
                            above_threshold.append(r.get('num_above_threshold', 0))
                        
                        results['comparisons'].append({
                            'threshold': threshold,
                            'mean_precision': self.safe_mean(precisions),
                            'mean_recall': self.safe_mean(recalls),
                            'mean_results': self.safe_mean(num_results),
                            'mean_above_threshold': self.safe_mean(above_threshold)
                        })
                    except Exception as e:
                        print(f"Error calculando estadísticas para umbral {threshold}: {str(e)}")
                        continue
                        
            except Exception as e:
                print(f"Error general con umbral {threshold}: {str(e)}")
                continue
        
        self._save_results('threshold_analysis.json', results)
        return results

    def _save_results(self, filename: str, results: Dict):
        """Guarda resultados de experimentos en JSON"""
        try:
            # Crear una copia profunda antes de guardar
            results_copy = copy.deepcopy(results)
            with open(self.results_dir / filename, 'w', encoding='utf-8') as f:
                json.dump(results_copy, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando resultados en {filename}: {str(e)}")

def run_all_experiments():
    """
    Ejecuta todos los experimentos y genera informes
    """
    try:
        print("\nIniciando suite de experimentos...")
        runner = ExperimentRunner()
        
        print("\n1. Ejecutando experimentos de tiempo...")
        timing_results = runner.run_timing_experiments()
        
        print("\n2. Evaluando impacto de sinónimos...")
        synonym_results = runner.evaluate_synonym_impact()
        
        print("\n3. Analizando umbrales de relevancia...")
        threshold_results = runner.analyze_thresholds()
        
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