import os
import json
from typing import Dict, List
from datetime import datetime
from text_processor import TextProcessor
import uuid
from pathlib import Path

class ReviewFileHandler:
    def __init__(self):
        self.data_dir = Path(__file__).parent / 'data'
        print(f"\nReviewFileHandler inicializado")
        print(f"Directorio de datos: {self.data_dir}")
        print(f"El directorio existe: {self.data_dir.exists()}")
        if self.data_dir.exists():
            print(f"Contenido del directorio: {[f.name for f in self.data_dir.glob('*')]}")
        self.text_processor = TextProcessor()
        self.data_dir.mkdir(exist_ok=True)
        
        # Procesar las reseñas existentes al inicializar
        self.process_reviews()
    
    def save_review(self, review_data: Dict) -> str:
        # Generar ID único si no existe
        if 'id' not in review_data:
            review_data['id'] = str(uuid.uuid4())
        
        # Procesar el texto de la reseña
        text_analysis = self.text_processor.process_text(
            review_data['resena'], 
            doc_id=review_data['id']
        )
        
        # Añadir análisis y metadatos
        review_data['analisis_texto'] = text_analysis
        review_data['metadata'] = {
            'fecha_procesamiento': datetime.now().isoformat(),
            'idioma': 'es',
            'version_sistema': '1.0'
        }
        
        # Guardar todo en un archivo .txt
        filename = f"review_{review_data['id']}.txt"
        filepath = self.data_dir / filename
        
        # Guardar el JSON en formato legible en el archivo .txt
        with filepath.open('w', encoding='utf-8') as f:
            json.dump(review_data, f, ensure_ascii=False, indent=2)
        
        return filename
    
    def load_review(self, filename: str) -> Dict:
        """Carga una reseña desde un archivo"""
        filepath = self.data_dir / filename
        try:
            with filepath.open('r', encoding='utf-8') as f:
                review = json.load(f)
                print(f"\nProcesando reseña: {filename}")
                print(f"ID: {review.get('id', 'No ID')}")
                print(f"Producto: {review.get('producto', 'No producto')}")
                return review
        except Exception as e:
            print(f"Error cargando reseña {filename}: {str(e)}")
            return None
    
    def list_reviews(self) -> List[str]:
        try:
            return [f.name for f in self.data_dir.glob('*.txt')]
        except Exception as e:
            print(f"Error listing reviews: {str(e)}")
            return []
    
    def search_reviews(self, query: str, search_type: str = 'tf_idf', operator: str = 'AND', min_score: float = 0.05) -> List[Dict]:
        """
        Busca reseñas usando el sistema especificado
        Args:
            query: Texto de búsqueda
            search_type: 'boolean' o 'tf_idf'
            operator: 'AND', 'OR', 'NOT' (solo para búsqueda booleana)
            min_score: Score mínimo para incluir un resultado (solo para tf_idf)
        Returns:
            Lista de reseñas ordenadas por relevancia
        """
        results = []
        
        if search_type == 'boolean':
            # Búsqueda booleana
            matching_ids = self.text_processor.boolean_search(query, operator)
            for filename in self.list_reviews():
                review = self.load_review(filename)
                if review and review['id'] in matching_ids:
                    results.append(review)
                    
        elif search_type == 'tf_idf':
            # Búsqueda por similitud tf-idf
            scores = self.text_processor.tf_idf_search(query)
            for filename in self.list_reviews():
                review = self.load_review(filename)
                if review and review['id'] in scores:
                    score = scores[review['id']]
                    if score >= min_score:  # Solo incluir resultados que superen el umbral
                        review['score'] = score
                        results.append(review)
            
            # Ordenar por puntuación
            results.sort(key=lambda x: (x.get('score', 0), x.get('puntuacion', 0)), reverse=True)
        
        return results
    
    def get_statistics(self) -> Dict:
        """
        Calcula estadísticas sobre las reseñas almacenadas
        """
        stats = {
            'total_reviews': 0,
            'avg_rating': 0.0,
            'categories': {},
            'websites': {},
            'vocabulary_size': len(self.text_processor.inverted_index),
            'reviews_per_category': {},
            'reviews_per_website': {}
        }
        
        total_rating = 0
        
        for filename in self.list_reviews():
            review = self.load_review(filename)
            if review:
                stats['total_reviews'] += 1
                total_rating += review['puntuacion']
                
                # Conteo por categoría
                category = review['categoria']
                stats['categories'][category] = stats['categories'].get(category, 0) + 1
                
                # Conteo por website
                website = review['website']['nombre']
                stats['websites'][website] = stats['websites'].get(website, 0) + 1
        
        # Calcular promedio de puntuación
        if stats['total_reviews'] > 0:
            stats['avg_rating'] = total_rating / stats['total_reviews']
        
        return stats

    def process_reviews(self):
        """Procesa todas las reseñas y actualiza el índice"""
        print("\n=== Iniciando carga de reseñas ===")
        print(f"Directorio de datos: {self.data_dir}")
        print(f"El directorio existe: {self.data_dir.exists()}")
        review_files = self.list_reviews()
        print(f"Contenido del directorio: {review_files}")
        
        # Reiniciar el índice
        self.text_processor.inverted_index.clear()
        self.text_processor.document_lengths.clear()
        self.text_processor.total_documents = 0
        
        processed_count = 0
        for filename in review_files:
            try:
                review = self.load_review(filename)
                if review and 'resena' in review and 'id' in review and 'producto' in review:
                    print(f"\nProcesando reseña: {filename}")
                    print(f"ID: {review['id']}")
                    print(f"Producto: {review['producto']}")
                    
                    # Procesar el título del producto y la reseña como un solo texto
                    combined_text = f"{review['producto']}. {review['resena']}"
                    result = self.text_processor.process_text(combined_text, doc_id=review['id'])
                    
                    # Verificar que el documento se indexó correctamente
                    if review['id'] in self.text_processor.document_lengths:
                        processed_count += 1
                        print(f"Reseña {review['id']} indexada correctamente")
                        print(f"Longitud del documento: {self.text_processor.document_lengths[review['id']]}")
                        print(f"Términos indexados: {len([term for term, docs in self.text_processor.inverted_index.items() if review['id'] in docs])}")
                    else:
                        print(f"Error: La reseña {review['id']} no se indexó correctamente")
                else:
                    print(f"Error: Reseña {filename} no tiene el formato esperado")
            except Exception as e:
                print(f"Error procesando {filename}: {str(e)}")
        
        print(f"\nTotal de reseñas procesadas: {processed_count}")
        print(f"Tamaño del índice invertido: {len(self.text_processor.inverted_index)} términos")
        print("Términos en el índice:", sorted(list(self.text_processor.inverted_index.keys())))
        print("Documentos indexados:", sorted(list(self.text_processor.document_lengths.keys())))
        print("=== Carga de reseñas completada ===\n") 