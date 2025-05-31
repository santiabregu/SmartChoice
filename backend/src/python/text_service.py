from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Dict, Optional
import nltk
import os
from text_processor import TextProcessor
from review_file_handler import ReviewFileHandler
from evaluator import Evaluator

# Set NLTK data path to a local directory
nltk.data.path.append(os.path.join(os.path.dirname(__file__), 'nltk_data'))

# Initialize FastAPI app
app = FastAPI(title="Sistema de Recuperación de Información - Reseñas de Productos",
             description="API para búsqueda y gestión de reseñas de productos")

# Initialize services
text_processor = TextProcessor()
review_handler = ReviewFileHandler()
evaluator = Evaluator()

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
    query: str
    search_type: str = "boolean"
    operator: str = "AND"

class EvaluationRequest(BaseModel):
    necesidad_id: str
    search_type: str = "boolean"

@app.post("/process_review")
async def process_review(review: ReviewData):
    try:
        filename = review_handler.save_review(review.dict())
        return {"status": "success", "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search")
async def search(search_query: SearchQuery):
    try:
        results = review_handler.search_reviews(
            search_query.query,
            search_query.search_type,
            search_query.operator
        )
        return {"status": "success", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/evaluate_search")
async def evaluate_search(eval_request: EvaluationRequest):
    """Evalúa una búsqueda para una necesidad de información específica"""
    try:
        # Buscar la necesidad
        necesidad = None
        for n in evaluator.necesidades:
            if n['id'] == eval_request.necesidad_id:
                necesidad = n
                break
        
        if not necesidad:
            raise HTTPException(status_code=404, detail="Necesidad no encontrada")
        
        # Realizar la búsqueda según el tipo
        if eval_request.search_type == "boolean":
            query = necesidad['consulta_booleana']
            results = review_handler.search_reviews(query, "boolean", "AND")
            search_results = {necesidad['id']: [r['id'] for r in results]}
            metrics = evaluator.evaluate_boolean_search(search_results)
        else:
            query = necesidad['consulta_libre']
            results = review_handler.search_reviews(query, "tf_idf")
            search_results = {necesidad['id']: [r['id'] for r in results]}
            metrics = evaluator.evaluate_ranked_search(search_results)
        
        return {
            "status": "success",
            "necesidad": necesidad,
            "resultados": results,
            "metricas": metrics['per_query'][necesidad['id']]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/evaluate_all")
async def evaluate_all():
    """Evalúa todas las necesidades de información con ambos sistemas"""
    try:
        boolean_results = {}
        ranked_results = {}
        
        # Realizar todas las búsquedas
        for necesidad in evaluator.necesidades:
            # Búsqueda booleana
            bool_results = review_handler.search_reviews(
                necesidad['consulta_booleana'],
                "boolean",
                "AND"
            )
            boolean_results[necesidad['id']] = [r['id'] for r in bool_results]
            
            # Búsqueda tf-idf
            tfidf_results = review_handler.search_reviews(
                necesidad['consulta_libre'],
                "tf_idf"
            )
            ranked_results[necesidad['id']] = [r['id'] for r in tfidf_results]
        
        # Evaluar resultados
        boolean_metrics = evaluator.evaluate_boolean_search(boolean_results)
        ranked_metrics = evaluator.evaluate_ranked_search(ranked_results)
        
        return {
            "status": "success",
            "evaluacion_booleana": boolean_metrics,
            "evaluacion_tfidf": ranked_metrics
        }
        
    except Exception as e:
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