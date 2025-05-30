import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from .text_processor import TextProcessor

class ReviewFileHandler:
    def __init__(self, reviews_dir: str = "data/reviews"):
        self.reviews_dir = reviews_dir
        self.text_processor = TextProcessor()
        
    def save_review(self, review_data: Dict, filename: Optional[str] = None) -> str:
        """
        Save a review to a JSON file
        """
        if filename is None:
            filename = f"review_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
        filepath = os.path.join(self.reviews_dir, filename)
        
        # Process text before saving
        tokens, stems, lemmas = self.text_processor.preprocess_text(review_data['resena'])
        
        # Update document frequencies for TF-IDF
        self.text_processor.update_document_frequencies(tokens)
        
        # Calculate TF-IDF vector
        tf_idf_vector = self.text_processor.calculate_tf_idf(review_data['resena'])
        
        # Add text analysis to review data
        review_data['analisis_texto'] = {
            'tokens': tokens,
            'stems': stems,
            'lemmatized': lemmas,
            'tf_idf_vector': tf_idf_vector
        }
        
        # Add metadata
        review_data['metadata'] = {
            'filename': filename,
            'processingDate': datetime.now().isoformat(),
            'language': 'es'
        }
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(review_data, f, ensure_ascii=False, indent=2)
            
        return filename
    
    def load_review(self, filename: str) -> Dict:
        """
        Load a review from a JSON file
        """
        filepath = os.path.join(self.reviews_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def list_reviews(self) -> List[str]:
        """
        List all review files in the directory
        """
        return [f for f in os.listdir(self.reviews_dir) if f.endswith('.txt')]
    
    def search_reviews(self, query: str, search_type: str = 'boolean') -> List[Dict]:
        """
        Search reviews using either boolean or TF-IDF similarity
        """
        results = []
        reviews = []
        
        # Load all reviews
        for filename in self.list_reviews():
            review = self.load_review(filename)
            reviews.append(review)
            
        if search_type == 'boolean':
            # Boolean search
            matching_indices = self.text_processor.boolean_search(
                query,
                [review['resena'] for review in reviews]
            )
            results = [reviews[i] for i in matching_indices]
            
        else:
            # TF-IDF similarity search
            query_vector = self.text_processor.calculate_tf_idf(query)
            
            # Calculate similarities
            similarities = []
            for review in reviews:
                if 'analisis_texto' in review and 'tf_idf_vector' in review['analisis_texto']:
                    similarity = self.text_processor.calculate_cosine_similarity(
                        query_vector,
                        review['analisis_texto']['tf_idf_vector']
                    )
                    similarities.append((similarity, review))
            
            # Sort by similarity
            similarities.sort(reverse=True)
            results = [review for _, review in similarities]
        
        return results 