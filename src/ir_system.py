import json
from typing import Dict, List, Set, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from review_processor import ReviewProcessor

class IRSystem:
    def __init__(self, corpus_file: str):
        self.corpus_file = corpus_file
        self.processor = ReviewProcessor()
        self.inverted_index: Dict[str, Set[int]] = {}
        self.tfidf_matrix = None
        self.tfidf_vectorizer = None
        self.documents = []
        self.load_corpus()
        self.build_indices()

    def load_corpus(self):
        """Load the corpus from the JSON file."""
        try:
            with open(self.corpus_file, 'r', encoding='utf-8') as f:
                self.documents = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.documents = []

    def build_indices(self):
        """Build both inverted index and TF-IDF matrix."""
        self._build_inverted_index()
        self._build_tfidf_matrix()

    def _build_inverted_index(self):
        """Build inverted index for boolean retrieval."""
        self.inverted_index.clear()
        
        for doc_id, doc in enumerate(self.documents):
            tokens = self.processor.preprocess_text(doc['reseña'])
            
            for token in tokens:
                if token not in self.inverted_index:
                    self.inverted_index[token] = set()
                self.inverted_index[token].add(doc_id)

    def _build_tfidf_matrix(self):
        """Build TF-IDF matrix for ranked retrieval."""
        # Extract and preprocess all reviews
        processed_docs = [' '.join(self.processor.preprocess_text(doc['reseña'])) 
                        for doc in self.documents]
        
        # Create TF-IDF matrix
        self.tfidf_vectorizer = TfidfVectorizer()
        if processed_docs:
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(processed_docs)
        else:
            self.tfidf_matrix = None

    def boolean_search(self, query: str) -> List[Dict]:
        """
        Perform boolean search with AND, OR, NOT operators.
        Example query: "smartphone AND batería NOT lento"
        """
        if not query.strip():
            return []

        # Split query into terms and operators
        terms = query.upper().split()
        result_set = None
        current_op = "AND"
        
        i = 0
        while i < len(terms):
            term = terms[i]
            
            if term in ("AND", "OR", "NOT"):
                current_op = term
                i += 1
                continue
            
            # Get document set for current term
            term_lower = term.lower()
            term_processed = self.processor.preprocess_text(term_lower)[0]
            current_set = self.inverted_index.get(term_processed, set())
            
            if result_set is None:
                result_set = current_set
            else:
                if current_op == "AND":
                    result_set &= current_set
                elif current_op == "OR":
                    result_set |= current_set
                elif current_op == "NOT":
                    result_set -= current_set
            
            i += 1
        
        # Convert document IDs to actual documents
        if result_set:
            return [self.documents[doc_id] for doc_id in result_set]
        return []

    def ranked_search(self, query: str, top_k: int = 5) -> List[Tuple[Dict, float]]:
        """Perform ranked search using cosine similarity."""
        if not self.tfidf_matrix or not query.strip():
            return []

        # Preprocess query
        processed_query = ' '.join(self.processor.preprocess_text(query))
        
        # Transform query to TF-IDF space
        query_vector = self.tfidf_vectorizer.transform([processed_query])
        
        # Calculate cosine similarities
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        
        # Get top-k results
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        # Return documents with their similarity scores
        results = []
        for idx in top_indices:
            if similarities[idx] > 0:  # Only include relevant documents
                results.append((self.documents[idx], float(similarities[idx])))
        
        return results

    def add_review(self, file_path: str):
        """Process and add a new review to the corpus."""
        review = self.processor.extract_review_info(file_path)
        self.processor.save_review(review, self.corpus_file)
        self.load_corpus()
        self.build_indices() 