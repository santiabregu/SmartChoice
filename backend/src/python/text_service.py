from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Dict, Optional
import nltk
import os
from text_processor import TextProcessor
from review_file_handler import ReviewFileHandler

# Set NLTK data path to a local directory
nltk.data.path.append(os.path.join(os.path.dirname(__file__), 'nltk_data'))

# Initialize FastAPI app
app = FastAPI(title="Sistema de Recuperación de Información - Reseñas de Productos",
             description="API para búsqueda y gestión de reseñas de productos")

# Initialize services
text_processor = TextProcessor()
review_handler = ReviewFileHandler()

@app.on_event("startup")
async def load_reviews():
    """Carga y procesa todas las reseñas al iniciar el servidor"""
    review_handler.process_reviews()

class Website(BaseModel):
    nombre: str = Field(..., description="Nombre del sitio web (Amazon, AliExpress, MediaMarkt)")
    url: Optional[HttpUrl] = Field(None, description="URL de la reseña")

class ReviewData(BaseModel):
    id: Optional[str] = Field(None, description="Identificador único interno")
    producto: str = Field(..., description="Nombre real del producto en la tienda")
    categoria: str = Field(..., description="Categoría del producto (Ropa, Tecnología, Cosméticos, etc)")
    resena: str = Field(..., description="Texto real de la opinión del usuario")
    puntuacion: float = Field(..., ge=1, le=5, description="Puntuación de 1 a 5 estrellas")
    website: Website

    class Config:
        schema_extra = {
            "example": {
                "producto": "Auriculares Sony WH-1000XM4",
                "categoria": "Tecnología",
                "resena": "Excelente calidad de sonido y batería dura más de 20 horas...",
                "puntuacion": 4.5,
                "website": {
                    "nombre": "Amazon",
                    "url": "https://www.amazon.es/review/123"
                }
            }
        }

class SearchQuery(BaseModel):
    query: str = Field(..., description="Texto de búsqueda (ej: 'auriculares con buena batería')")
    search_type: str = Field('boolean', description="Tipo de búsqueda: 'boolean' o 'tf_idf'")
    operator: Optional[str] = Field('AND', description="Operador para búsqueda booleana: 'AND', 'OR', 'NOT'")

@app.post("/process_review")
async def process_review(review: ReviewData):
    try:
        filename = review_handler.save_review(review.dict())
        return {"status": "success", "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search")
async def search_reviews(search_query: SearchQuery):
    try:
        print(f"\n=== Nueva búsqueda ===")
        print(f"Query: {search_query.query}")
        print(f"Tipo: {search_query.search_type}")
        print(f"Operador: {search_query.operator}")
        
        results = review_handler.search_reviews(
            search_query.query,
            search_query.search_type,
            search_query.operator
        )
        
        print(f"Resultados encontrados: {len(results)}")
        if results:
            print("IDs encontrados:", [r.get('id') for r in results])
        print("=== Búsqueda completada ===\n")
        
        return {"status": "success", "results": results}
    except Exception as e:
        print(f"Error en búsqueda: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/statistics")
async def get_statistics():
    try:
        return {
            "status": "success",
            "statistics": review_handler.get_statistics()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Ensure NLTK data is downloaded
    try:
        nltk.download('punkt', download_dir='nltk_data')
        nltk.download('stopwords', download_dir='nltk_data')
        nltk.download('wordnet', download_dir='nltk_data')
    except Exception as e:
        print(f"Warning: Failed to download NLTK data: {e}")
    
    uvicorn.run(app, host="0.0.0.0", port=8000) 