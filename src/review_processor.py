import json
import os
import re
from typing import Dict, List, Optional
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import SnowballStemmer
import spacy

class ReviewProcessor:
    def __init__(self):
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('punkt')
            nltk.download('stopwords')
        
        self.stemmer = SnowballStemmer('spanish')
        self.stop_words = set(stopwords.words('spanish'))
        # Load Spanish language model for spaCy
        try:
            self.nlp = spacy.load('es_core_news_sm')
        except OSError:
            os.system('python -m spacy download es_core_news_sm')
            self.nlp = spacy.load('es_core_news_sm')

    def extract_review_info(self, file_path: str) -> Dict:
        """Extract review information from a text file."""
        filename = os.path.basename(file_path)
        product_name = os.path.splitext(filename)[0]
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract or infer rating (assuming ratings are written as X/5 or X estrellas)
        rating_match = re.search(r'(\d+(?:\.\d+)?)/5|(\d+(?:\.\d+)?) estrellas', content, re.IGNORECASE)
        rating = float(rating_match.group(1) or rating_match.group(2)) if rating_match else None
        
        # Infer category based on keywords in content
        category = self._infer_category(content)
        
        return {
            "producto": product_name,
            "categoría": category,
            "reseña": content,
            "puntuación": rating
        }
    
    def _infer_category(self, text: str) -> str:
        """Infer product category based on text content."""
        # Simple rule-based category inference
        categories = {
            "Tecnología": ["smartphone", "tablet", "laptop", "ordenador", "pc", "televisor", "tv"],
            "Ropa": ["camisa", "pantalón", "vestido", "zapatos", "ropa", "talla"],
            "Hogar": ["mueble", "sofá", "mesa", "silla", "cocina", "dormitorio"],
            "Electrodomésticos": ["nevera", "lavadora", "microondas", "horno", "lavavajillas"],
            "Otros": []
        }
        
        text_lower = text.lower()
        for category, keywords in categories.items():
            if any(keyword in text_lower for keyword in keywords):
                return category
        return "Otros"
    
    def preprocess_text(self, text: str) -> List[str]:
        """Preprocess text: lowercase, tokenize, remove stopwords and stem."""
        # Lowercase and tokenize
        tokens = word_tokenize(text.lower(), language='spanish')
        
        # Remove stopwords and stem
        tokens = [self.stemmer.stem(token) for token in tokens 
                 if token.isalnum() and token not in self.stop_words]
        
        return tokens
    
    def save_review(self, review: Dict, corpus_file: str):
        """Save a review to the corpus file."""
        try:
            with open(corpus_file, 'r', encoding='utf-8') as f:
                corpus = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            corpus = []
        
        corpus.append(review)
        
        with open(corpus_file, 'w', encoding='utf-8') as f:
            json.dump(corpus, f, ensure_ascii=False, indent=2) 