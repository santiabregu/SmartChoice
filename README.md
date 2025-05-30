# SmartChoice

Sistema de Recuperación de Información para reseñas de productos.

## Descripción
Este proyecto implementa un sistema completo de recuperación de información para procesar y buscar reseñas de productos. El sistema permite cargar reseñas desde archivos de texto, procesarlas automáticamente, y realizar búsquedas tanto booleanas como por texto libre con ranking.

## Características
- Procesamiento automático de reseñas en español
- Extracción de información estructurada (producto, categoría, puntuación)
- Búsqueda booleana con operadores AND, OR, NOT
- Búsqueda por texto libre con ranking basado en TF-IDF y similitud coseno
- Interfaz de línea de comandos intuitiva

## Requisitos
- Python 3.8 o superior
- Dependencias listadas en `requirements.txt`

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/santiabregu/SmartChoice.git
cd SmartChoice
```

2. Crear un entorno virtual (opcional pero recomendado):
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

4. Descargar los modelos de lenguaje necesarios:
```bash
python -m spacy download es_core_news_sm
```

## Uso

1. Ejecutar el programa:
```bash
python src/main.py
```

2. El sistema mostrará un menú con las siguientes opciones:
   - Añadir nuevas reseñas
   - Búsqueda booleana
   - Búsqueda por texto libre (ranking)
   - Salir

### Formato de las Reseñas
Las reseñas deben estar en archivos .txt con el siguiente formato recomendado:

```
[Nombre del Producto]
Puntuación: X/5 estrellas

[Contenido de la reseña...]
```

El sistema intentará inferir:
- Producto: del nombre del archivo o contenido
- Categoría: basada en palabras clave en el contenido
- Puntuación: buscando patrones como "X/5" o "X estrellas"
- Reseña: todo el contenido del archivo

### Ejemplos de Búsqueda

Búsqueda booleana:
```
smartphone AND batería NOT lento
```

Búsqueda por texto libre:
```
buena cámara con batería duradera
```

## Estructura del Proyecto
```
SmartChoice/
├── data/
│   ├── corpus_estructurado.json
│   └── reviews/
├── src/
│   ├── main.py
│   ├── ir_system.py
│   └── review_processor.py
├── requirements.txt
└── README.md
```

## Licencia
Este proyecto está bajo la Licencia MIT - ver el archivo LICENSE para más detalles. 