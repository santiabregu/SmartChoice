from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import nltk
import os
from text_processor import TextProcessor
from review_file_handler import ReviewFileHandler

# Set NLTK data path to a local directory
nltk.data.path.append(os.path.join(os.path.dirname(__file__), 'nltk_data'))

# Initialize FastAPI app
app = FastAPI()

# Initialize services
text_processor = TextProcessor()
review_handler = ReviewFileHandler()

class SearchQuery(BaseModel):
    query: str
    search_type: str = 'boolean'
    operator: Optional[str] = 'AND'

class ReviewData(BaseModel):
    producto: str
    categoria: str
    resena: str
    puntuacion: float
    website: Dict[str, str]

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
        results = review_handler.search_reviews(
            search_query.query,
            search_query.search_type
        )
        return {"status": "success", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/statistics")
async def get_statistics():
    try:
        reviews = [review_handler.load_review(f) for f in review_handler.list_reviews()]
        
        # Calculate basic statistics
        total_reviews = len(reviews)
        avg_rating = sum(r['puntuacion'] for r in reviews) / total_reviews if total_reviews > 0 else 0
        websites = {}
        categories = {}
        
        for review in reviews:
            website = review['website']['nombre']
            category = review['categoria']
            websites[website] = websites.get(website, 0) + 1
            categories[category] = categories.get(category, 0) + 1
            
        return {
            "status": "success",
            "statistics": {
                "total_reviews": total_reviews,
                "average_rating": avg_rating,
                "website_distribution": websites,
                "category_distribution": categories
            }
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