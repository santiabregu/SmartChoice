"""
Módulo de tokenización para textos en español.

Este módulo implementa funciones especializadas para la tokenización de texto
en español, incluyendo manejo de contracciones y casos especiales del idioma.
"""

from typing import List
import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk

# Asegurar que tenemos los recursos necesarios de NLTK
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

# Cargar stopwords en español
STOP_WORDS = set(stopwords.words('spanish'))

# Patrones específicos del español
CONTRACTIONS = {
    'del': 'de el',
    'al': 'a el',
    'conmigo': 'con mi',
    'contigo': 'con ti'
}

def expand_contractions(text: str) -> str:
    """
    Expande las contracciones comunes en español.
    
    Args:
        text (str): Texto con posibles contracciones
        
    Returns:
        str: Texto con contracciones expandidas
    """
    for contraction, expansion in CONTRACTIONS.items():
        text = re.sub(r'\b' + contraction + r'\b', expansion, text, flags=re.IGNORECASE)
    return text

def tokenize(text: str, remove_stopwords: bool = True) -> List[str]:
    """
    Tokeniza el texto en español, con opción de eliminar stopwords.
    
    Args:
        text (str): Texto a tokenizar
        remove_stopwords (bool): Si se deben eliminar las stopwords
        
    Returns:
        List[str]: Lista de tokens
    """
    # Expandir contracciones
    text = expand_contractions(text)
    
    # Tokenizar
    tokens = word_tokenize(text, language='spanish')
    
    # Filtrar tokens
    tokens = [token.lower() for token in tokens if token.isalnum()]
    
    # Eliminar stopwords si se solicita
    if remove_stopwords:
        tokens = [token for token in tokens if token not in STOP_WORDS]
    
    return tokens

def get_ngrams(tokens: List[str], n: int) -> List[str]:
    """
    Genera n-gramas a partir de una lista de tokens.
    
    Args:
        tokens (List[str]): Lista de tokens
        n (int): Tamaño del n-grama
        
    Returns:
        List[str]: Lista de n-gramas
    """
    return [' '.join(tokens[i:i+n]) for i in range(len(tokens)-n+1)]

def analyze_tokens(text: str) -> dict:
    """
    Realiza un análisis básico de los tokens en el texto.
    
    Args:
        text (str): Texto a analizar
        
    Returns:
        dict: Diccionario con estadísticas de los tokens
    """
    tokens = tokenize(text, remove_stopwords=False)
    tokens_no_stop = tokenize(text, remove_stopwords=True)
    
    return {
        'total_tokens': len(tokens),
        'unique_tokens': len(set(tokens)),
        'tokens_no_stopwords': len(tokens_no_stop),
        'unique_tokens_no_stopwords': len(set(tokens_no_stop))
    } 