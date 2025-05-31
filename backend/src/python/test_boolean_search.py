from text_processor import TextProcessor
from evaluation import load_information_needs, evaluate_boolean_search
import json

def load_reviews():
    """Carga las reseñas de ejemplo"""
    reviews = [
        {
            "id": "1",
            "producto": "Auriculares Sony WH-1000XM4",
            "categoria": "Tecnología",
            "resena": "Excelente calidad de sonido y la batería dura más de 20 horas. La cancelación de ruido es impresionante, especialmente en aviones y trenes. El único inconveniente es que son un poco caros, pero vale la pena la inversión. La app es muy útil para personalizar el sonido.",
            "puntuacion": 4.5,
            "website": {
                "nombre": "Amazon",
                "url": "https://www.amazon.es/review/123"
            }
        },
        {
            "id": "2",
            "producto": "Nike Air Zoom Pegasus 38",
            "categoria": "Ropa",
            "resena": "Zapatillas muy cómodas y ligeras, perfectas para running. El diseño es moderno y vienen en color blanco que combina con todo. La amortiguación es excelente para carreras largas. La talla es exacta, no hace falta pedir un número más. La transpirabilidad es muy buena.",
            "puntuacion": 5.0,
            "website": {
                "nombre": "AliExpress",
                "url": "https://www.aliexpress.com/review/456"
            }
        },
        {
            "id": "3",
            "producto": "Samsung Galaxy S23",
            "categoria": "Tecnología",
            "resena": "La cámara es espectacular, especialmente en condiciones de poca luz. La batería aguanta todo el día con uso intensivo y la carga rápida es muy útil. La pantalla tiene colores vibrantes y el brillo automático funciona perfectamente. El rendimiento es excelente para juegos y multitarea. El único punto negativo es que se calienta un poco al jugar.",
            "puntuacion": 4.8,
            "website": {
                "nombre": "MediaMarkt",
                "url": "https://www.mediamarkt.es/review/789"
            }
        },
        {
            "id": "4",
            "producto": "Crema Hidratante La Roche-Posay Effaclar",
            "categoria": "Cosméticos",
            "resena": "Excelente para pieles mixtas y con tendencia al acné. No deja la piel grasa y se absorbe rápidamente. He notado una mejora significativa en mi piel después de dos semanas de uso. No tiene perfume, lo cual es perfecto para pieles sensibles. La textura es ligera y un poco va muy lejos.",
            "puntuacion": 4.7,
            "website": {
                "nombre": "Amazon",
                "url": "https://www.amazon.es/review/321"
            }
        },
        {
            "id": "5",
            "producto": "Auriculares Bluetooth JBL Tune 510BT",
            "categoria": "Tecnología",
            "resena": "La calidad de sonido es mediocre y la batería dura menos de lo anunciado, apenas 3-4 horas. La conexión Bluetooth es inestable y se desconecta frecuentemente. Los materiales parecen de baja calidad y son incómodos después de una hora de uso. Lo único positivo es que son ligeros y el precio es económico.",
            "puntuacion": 2.0,
            "website": {
                "nombre": "AliExpress",
                "url": "https://www.aliexpress.com/review/987"
            }
        }
    ]
    return reviews

def main():
    # Inicializar el procesador de texto
    processor = TextProcessor()
    
    # Cargar reseñas y procesarlas
    reviews = load_reviews()
    for review in reviews:
        processor.process_text(review['resena'], review['id'])
    
    # Cargar necesidades de información
    needs = load_information_needs('necesidades_informacion.json')
    
    # Realizar búsquedas booleanas y evaluar resultados
    results = []
    print("\nResultados de búsquedas booleanas:")
    print("-" * 50)
    
    for need in needs:
        print(f"\nNecesidad {need['id']}: {need['descripcion']}")
        print(f"Consulta booleana: {need['consulta_booleana']}")
        
        # Realizar búsqueda
        result = processor.boolean_search(need['consulta_booleana'])
        results.append(result)
        
        # Mostrar resultados
        print("\nDocumentos recuperados:")
        for doc_id in result:
            review = next(r for r in reviews if r['id'] == doc_id)
            print(f"- [{doc_id}] {review['producto']}")
        
        # Calcular métricas individuales
        relevant = set(need['documentos_relevantes'])
        p = len(relevant & result) / len(result) if result else 0
        r = len(relevant & result) / len(relevant) if relevant else 0
        f1 = 2 * (p * r) / (p + r) if (p + r) > 0 else 0
        
        print(f"\nMétricas para esta consulta:")
        print(f"Precisión: {p:.2f}")
        print(f"Recall: {r:.2f}")
        print(f"F1: {f1:.2f}")
    
    # Evaluar resultados globales
    metrics = evaluate_boolean_search(results, needs)
    
    print("\nMétricas globales:")
    print("-" * 50)
    print(f"Precisión media: {metrics['precision']:.2f}")
    print(f"Recall medio: {metrics['recall']:.2f}")
    print(f"F1 medio: {metrics['f1']:.2f}")

if __name__ == "__main__":
    main() 