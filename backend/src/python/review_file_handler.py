import os
import json
from typing import Dict, List
from datetime import datetime
from text_processor import TextProcessor

class ReviewFileHandler:
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        self.text_processor = TextProcessor()
        os.makedirs(self.data_dir, exist_ok=True)
    
    def save_review(self, review_data: Dict) -> str:
        # Process the review text
        text_analysis = self.text_processor.process_text(review_data['resena'])
        review_data['analisis_texto'] = text_analysis
        
        # Add metadata
        review_data['metadata'] = {
            'processingDate': datetime.now().isoformat(),
            'language': 'es'
        }
        
        # Generate filename
        filename = f"review_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.data_dir, filename)
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(review_data, f, ensure_ascii=False, indent=2)
        
        return filename
    
    def load_review(self, filename: str) -> Dict:
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def list_reviews(self) -> List[str]:
        return [f for f in os.listdir(self.data_dir) if f.endswith('.json')]
    
    def search_reviews(self, query: str, search_type: str = 'boolean') -> List[Dict]:
        results = []
        query_terms = set(self.text_processor.process_text(query)['lemmatized'])
        
        for filename in self.list_reviews():
            review = self.load_review(filename)
            review_terms = set(review['analisis_texto']['lemmatized'])
            
            if search_type == 'boolean':
                if query_terms.intersection(review_terms):
                    results.append(review)
            elif search_type == 'tf_idf':
                # Simple TF-IDF similarity
                review_vector = review['analisis_texto']['tf_idf_vector']
                score = sum(review_vector.get(term, 0) for term in query_terms)
                if score > 0:
                    review['score'] = score
                    results.append(review)
        
        if search_type == 'tf_idf':
            results.sort(key=lambda x: x['score'], reverse=True)
        
        return results 