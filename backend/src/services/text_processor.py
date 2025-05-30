import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from nltk.stem import WordNetLemmatizer
from typing import Dict, List, Tuple, Set
import math
from collections import Counter

# Download required NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

class TextProcessor:
    def __init__(self):
        self.stemmer = SnowballStemmer('spanish')
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('spanish'))
        self.document_frequencies: Dict[str, int] = {}
        self.total_documents = 0
        
    def preprocess_text(self, text: str) -> Tuple[List[str], List[str], List[str]]:
        """
        Preprocess text by tokenizing, removing stopwords, and generating stems and lemmas
        """
        # Tokenization
        tokens = word_tokenize(text.lower())
        
        # Remove stopwords and non-alphabetic tokens
        tokens = [token for token in tokens if token.isalpha() and token not in self.stop_words]
        
        # Stemming and Lemmatization
        stems = [self.stemmer.stem(token) for token in tokens]
        lemmas = [self.lemmatizer.lemmatize(token) for token in tokens]
        
        return tokens, stems, lemmas
    
    def update_document_frequencies(self, tokens: List[str]):
        """
        Update document frequencies for TF-IDF calculation
        """
        self.total_documents += 1
        unique_terms = set(tokens)
        for term in unique_terms:
            self.document_frequencies[term] = self.document_frequencies.get(term, 0) + 1
    
    def calculate_tf_idf(self, text: str) -> Dict[str, float]:
        """
        Calculate TF-IDF vector for a document
        """
        tokens, _, _ = self.preprocess_text(text)
        term_freq = Counter(tokens)
        
        tf_idf_vector = {}
        for term, freq in term_freq.items():
            tf = freq / len(tokens)
            idf = math.log(self.total_documents / (self.document_frequencies.get(term, 1)))
            tf_idf_vector[term] = tf * idf
            
        return tf_idf_vector
    
    def calculate_cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """
        Calculate cosine similarity between two TF-IDF vectors
        """
        # Get common terms
        common_terms = set(vec1.keys()) & set(vec2.keys())
        
        # Calculate dot product
        dot_product = sum(vec1[term] * vec2[term] for term in common_terms)
        
        # Calculate magnitudes
        mag1 = math.sqrt(sum(v * v for v in vec1.values()))
        mag2 = math.sqrt(sum(v * v for v in vec2.values()))
        
        if mag1 == 0 or mag2 == 0:
            return 0
            
        return dot_product / (mag1 * mag2)
    
    def _tokenize_query(self, query: str) -> List[str]:
        """
        Tokenize a query into terms and operators
        """
        # Replace operators with spaces around them
        for op in ['AND', 'OR', 'NOT']:
            query = query.replace(op, f' {op} ')
        return [token.strip() for token in query.split() if token.strip()]

    def _evaluate_boolean_expression(self, query_tokens: List[str], doc_tokens: Set[str]) -> bool:
        """
        Evaluate a boolean expression with AND, OR, NOT operators
        """
        stack = []
        i = 0
        while i < len(query_tokens):
            token = query_tokens[i]
            
            if token == 'NOT':
                i += 1
                if i >= len(query_tokens):
                    raise ValueError("Invalid boolean expression: NOT must be followed by a term")
                next_token = query_tokens[i]
                processed_token = self.preprocess_text(next_token)[0]
                result = not any(term in doc_tokens for term in processed_token)
                stack.append(result)
            
            elif token == 'AND':
                if len(stack) < 1:
                    raise ValueError("Invalid boolean expression: AND requires two operands")
                i += 1
                if i >= len(query_tokens):
                    raise ValueError("Invalid boolean expression: AND must be followed by a term")
                next_token = query_tokens[i]
                processed_token = self.preprocess_text(next_token)[0]
                op1 = stack.pop()
                op2 = any(term in doc_tokens for term in processed_token)
                stack.append(op1 and op2)
            
            elif token == 'OR':
                if len(stack) < 1:
                    raise ValueError("Invalid boolean expression: OR requires two operands")
                i += 1
                if i >= len(query_tokens):
                    raise ValueError("Invalid boolean expression: OR must be followed by a term")
                next_token = query_tokens[i]
                processed_token = self.preprocess_text(next_token)[0]
                op1 = stack.pop()
                op2 = any(term in doc_tokens for term in processed_token)
                stack.append(op1 or op2)
            
            else:
                processed_token = self.preprocess_text(token)[0]
                result = any(term in doc_tokens for term in processed_token)
                stack.append(result)
            
            i += 1
        
        if not stack:
            return False
        return stack[0]

    def boolean_search(self, query: str, documents: List[str]) -> List[int]:
        """
        Perform boolean search using AND, OR, NOT operators
        """
        results = []
        query_tokens = self._tokenize_query(query)
        
        for i, doc in enumerate(documents):
            doc_tokens = set(self.preprocess_text(doc)[0])
            try:
                if self._evaluate_boolean_expression(query_tokens, doc_tokens):
                    results.append(i)
            except ValueError as e:
                print(f"Warning: {str(e)}")
                continue
                
        return results 