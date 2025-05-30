import uvicorn
from text_service import app
from setup_nltk import setup_nltk

if __name__ == "__main__":
    # Set up NLTK data
    setup_nltk()
    
    # Run the FastAPI service
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    ) 