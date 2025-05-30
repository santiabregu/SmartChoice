import os
import sys
from ir_system import IRSystem

def print_menu():
    """Print the main menu options."""
    print("\n=== Sistema de Recuperación de Información de Reseñas ===")
    print("1. Añadir nuevas reseñas")
    print("2. Búsqueda booleana")
    print("3. Búsqueda por texto libre (ranking)")
    print("4. Salir")
    print("================================================")

def add_reviews(ir_system: IRSystem):
    """Add new reviews from text files."""
    print("\n=== Añadir Nuevas Reseñas ===")
    reviews_dir = input("Ingrese la ruta del directorio con las reseñas (.txt): ").strip()
    
    if not os.path.exists(reviews_dir):
        print("Error: El directorio no existe.")
        return
    
    files_added = 0
    for filename in os.listdir(reviews_dir):
        if filename.endswith('.txt'):
            file_path = os.path.join(reviews_dir, filename)
            try:
                ir_system.add_review(file_path)
                files_added += 1
                print(f"Reseña añadida: {filename}")
            except Exception as e:
                print(f"Error al procesar {filename}: {str(e)}")
    
    print(f"\nSe añadieron {files_added} reseñas al corpus.")

def boolean_search(ir_system: IRSystem):
    """Perform boolean search."""
    print("\n=== Búsqueda Booleana ===")
    print("Formato: término1 AND/OR/NOT término2")
    print("Ejemplo: smartphone AND batería NOT lento")
    
    query = input("\nIngrese su consulta: ").strip()
    results = ir_system.boolean_search(query)
    
    if not results:
        print("\nNo se encontraron resultados.")
        return
    
    print(f"\nSe encontraron {len(results)} resultados:")
    for i, doc in enumerate(results, 1):
        print(f"\n{i}. {doc['producto']}")
        print(f"Categoría: {doc['categoría']}")
        print(f"Puntuación: {doc['puntuación'] if doc['puntuación'] else 'No disponible'}")
        print(f"Reseña: {doc['reseña'][:200]}...")

def ranked_search(ir_system: IRSystem):
    """Perform ranked free-text search."""
    print("\n=== Búsqueda por Texto Libre ===")
    query = input("Ingrese su consulta: ").strip()
    results = ir_system.ranked_search(query)
    
    if not results:
        print("\nNo se encontraron resultados.")
        return
    
    print(f"\nResultados ordenados por relevancia:")
    for i, (doc, score) in enumerate(results, 1):
        print(f"\n{i}. {doc['producto']} (Relevancia: {score:.3f})")
        print(f"Categoría: {doc['categoría']}")
        print(f"Puntuación: {doc['puntuación'] if doc['puntuación'] else 'No disponible'}")
        print(f"Reseña: {doc['reseña'][:200]}...")

def main():
    """Main program loop."""
    # Create necessary directories
    os.makedirs('data', exist_ok=True)
    corpus_file = 'data/corpus_estructurado.json'
    
    # Initialize the IR system
    ir_system = IRSystem(corpus_file)
    
    while True:
        print_menu()
        choice = input("Seleccione una opción (1-4): ").strip()
        
        if choice == '1':
            add_reviews(ir_system)
        elif choice == '2':
            boolean_search(ir_system)
        elif choice == '3':
            ranked_search(ir_system)
        elif choice == '4':
            print("\n¡Gracias por usar el sistema!")
            sys.exit(0)
        else:
            print("\nOpción no válida. Por favor, intente de nuevo.")

if __name__ == "__main__":
    main() 