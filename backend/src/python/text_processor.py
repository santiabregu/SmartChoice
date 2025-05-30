import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from typing import List, Dict
import math

class TextProcessor:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('spanish'))
        
    def process_text(self, text: str) -> Dict:
        tokens = word_tokenize(text.lower())
        tokens = [token for token in tokens if token.isalnum()]
        tokens = [token for token in tokens if token not in self.stop_words]
        
        lemmatized = [self.lemmatizer.lemmatize(token) for token in tokens]
        
        return {
            "tokens": tokens,
            "lemmatized": lemmatized,
            "tf_idf_vector": self._calculate_tf(lemmatized)
        }
    
    def _calculate_tf(self, tokens: List[str]) -> Dict[str, float]:
        tf_dict = {}
        for token in tokens:
            tf_dict[token] = tf_dict.get(token, 0) + 1
        
        # Normalize TF by document length
        length = len(tokens)
        return {term: freq/length for term, freq in tf_dict.items()} 