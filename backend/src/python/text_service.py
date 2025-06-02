from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Dict, Optional
import nltk
import os
import json
from text_processor import TextProcessor
from review_file_handler import ReviewFileHandler
from evaluator import Evaluator
from experiments import ExperimentRunner
import statistics

# Set NLTK data path to a local directory
nltk.data.path.append(os.path.join(os.path.dirname(__file__), 'nltk_data'))

# Initialize FastAPI app
app = FastAPI(title="Sistema de Recuperación de Información - Reseñas de Productos",
             description="API para búsqueda y gestión de reseñas de productos")

# Initialize services
text_processor = TextProcessor()
review_handler = ReviewFileHandler()
evaluator = Evaluator(similarity_threshold=0.15)

# Load information needs
with open(os.path.join(os.path.dirname(__file__), 'data/necesidades_informacion.json'), 'r', encoding='utf-8') as f:
    NECESIDADES = json.load(f)['necesidades']

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

class SearchRequest(BaseModel):
    query: str
    search_type: str = 'tf_idf'  # 'boolean' o 'tf_idf'
    operator: Optional[str] = 'AND'

class ScoreStats(BaseModel):
    min_score: float
    max_score: float
    mean_score: float
    median_score: float
    score_distribution: Dict[str, int]  # rangos de scores -> cantidad
    total_matches: int
    matches_by_category: Dict[str, int]

class SearchResponse(BaseModel):
    results: List[Dict]
    metrics: Optional[Dict] = None
    score_statistics: Optional[ScoreStats] = None

class EvaluationRequest(BaseModel):
    necesidad_id: str
    search_type: str = "tf_idf"

@app.post("/search")
async def search(request: SearchRequest) -> SearchResponse:
    """
    Busca reseñas que coincidan con la consulta y proporciona estadísticas detalladas
    Args:
        request: SearchRequest con query y tipo de búsqueda
    Returns:
        SearchResponse con resultados, métricas y estadísticas de scores
    """
    try:
        # Realizar búsqueda
        results = review_handler.search_reviews(
            request.query, 
            request.search_type, 
            request.operator
        )
        
        # Calcular estadísticas de scores para tf-idf
        score_statistics = None
        if request.search_type == 'tf_idf' and results:
            scores = [r.get('score', 0.0) for r in results]
            
            # Crear rangos de scores para distribución
            score_ranges = {
                '0.0-0.1': 0,
                '0.1-0.2': 0,
                '0.2-0.3': 0,
                '0.3-0.4': 0,
                '0.4-0.5': 0,
                '0.5+': 0
            }
            
            for score in scores:
                if score >= 0.5:
                    score_ranges['0.5+'] += 1
                elif score >= 0.4:
                    score_ranges['0.4-0.5'] += 1
                elif score >= 0.3:
                    score_ranges['0.3-0.4'] += 1
                elif score >= 0.2:
                    score_ranges['0.2-0.3'] += 1
                elif score >= 0.1:
                    score_ranges['0.1-0.2'] += 1
                else:
                    score_ranges['0.0-0.1'] += 1
            
            # Contar matches por categoría
            category_matches = {}
            for result in results:
                category = result.get('categoria', 'Unknown')
                category_matches[category] = category_matches.get(category, 0) + 1
            
            score_statistics = ScoreStats(
                min_score=min(scores),
                max_score=max(scores),
                mean_score=statistics.mean(scores),
                median_score=statistics.median(scores),
                score_distribution=score_ranges,
                total_matches=len(results),
                matches_by_category=category_matches
            )
        
        # Para búsquedas tf-idf, evaluar usando pseudo-relevance feedback
        metrics = None
        if request.search_type == 'tf_idf' and results:
            # Extraer scores de los resultados
            scores = {str(r['id']): r.get('score', 0.0) for r in results}
            
            # Evaluar usando pseudo-relevance feedback
            search_results = {request.query: scores}
            metrics = evaluator.evaluate_ranked_search(search_results)
        
        return SearchResponse(
            results=results,
            metrics=metrics,
            score_statistics=score_statistics
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process_review")
async def process_review(review: ReviewData):
    """Procesa y almacena una nueva reseña"""
    try:
        filename = review_handler.save_review(review.dict())
        return {"status": "success", "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/evaluate_search")
async def evaluate_search(eval_request: EvaluationRequest):
    """Evalúa una búsqueda para una necesidad de información específica"""
    try:
        # Buscar la necesidad
        necesidad = next((n for n in NECESIDADES if n['id'] == eval_request.necesidad_id), None)
        if not necesidad:
            raise HTTPException(status_code=404, detail="Necesidad no encontrada")
        
        # Realizar la búsqueda
        query = necesidad['consulta_libre'] if eval_request.search_type == 'tf_idf' else necesidad['consulta_booleana']
        results = review_handler.search_reviews(query, eval_request.search_type)
        
        # Evaluar resultados según el tipo de búsqueda
        if eval_request.search_type == 'boolean':
            metrics = evaluator.evaluate_boolean_search(results)
        else:  # tf_idf
            if results:
                scores = {str(r['id']): r.get('score', 0.0) for r in results}
                search_results = {necesidad['id']: scores}
                metrics = evaluator.evaluate_ranked_search(search_results)['per_query'][necesidad['id']]
            else:
                metrics = None
        
        return {
            "status": "success",
            "necesidad": necesidad,
            "resultados": results,
            "metricas": metrics
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/evaluate_all")
async def evaluate_all():
    """Evalúa todas las necesidades de información usando tf-idf y pseudo-relevance feedback"""
    try:
        all_metrics = {
            'per_necesidad': {},
            'overall': {
                'map': 0.0,
                'precision': 0.0,
                'recall': 0.0
            }
        }
        
        # Evaluar cada necesidad
        for necesidad in NECESIDADES:
            # Realizar búsqueda tf-idf
            results = review_handler.search_reviews(
                necesidad['consulta_libre'],
                'tf_idf'
            )
            
            # Calcular métricas si hay resultados
            if results:
                scores = {str(r['id']): r.get('score', 0.0) for r in results}
                search_results = {necesidad['id']: scores}
                metrics = evaluator.evaluate_ranked_search(search_results)
                
                all_metrics['per_necesidad'][necesidad['id']] = {
                    'descripcion': necesidad['descripcion'],
                    'metricas': metrics['per_query'][necesidad['id']]
                }
                
                # Actualizar métricas globales
                all_metrics['overall']['map'] += metrics['overall']['map']
                all_metrics['overall']['precision'] += metrics['overall']['precision']
                all_metrics['overall']['recall'] += metrics['overall']['recall']
        
        # Calcular promedios globales
        num_necesidades = len(NECESIDADES)
        if num_necesidades > 0:
            all_metrics['overall']['map'] /= num_necesidades
            all_metrics['overall']['precision'] /= num_necesidades
            all_metrics['overall']['recall'] /= num_necesidades
        
        return {
            "status": "success",
            "evaluacion": all_metrics
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/statistics")
async def get_statistics():
    """Obtiene estadísticas del sistema"""
    try:
        return {
            "status": "success",
            "statistics": review_handler.get_statistics()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/run_experiments")
async def run_experiments():
    """Ejecuta experimentos de evaluación del sistema"""
    try:
        runner = ExperimentRunner()
        
        results = {
            'timing': runner.run_timing_experiments(),
            'synonyms': runner.evaluate_synonym_impact(),
            'thresholds': runner.analyze_thresholds()
        }
        
        return {
            "status": "success",
            "results": results
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