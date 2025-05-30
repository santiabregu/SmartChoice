"""
Módulo para la limpieza y normalización de texto.

Este módulo implementa funciones para la limpieza y normalización de texto
en español, incluyendo eliminación de caracteres especiales, normalización
de espacios y otros procesos básicos de limpieza.
"""

import re
import unicodedata

def normalize_text(text: str) -> str:
    """
    Normaliza el texto eliminando acentos y caracteres especiales.
    
    Args:
        text (str): Texto a normalizar
        
    Returns:
        str: Texto normalizado
    """
    # Convertir a minúsculas
    text = text.lower()
    
    # Normalizar caracteres Unicode
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ASCII', 'ignore').decode('utf-8')
    
    return text

def remove_special_chars(text: str) -> str:
    """
    Elimina caracteres especiales y símbolos, manteniendo letras, números y espacios.
    
    Args:
        text (str): Texto del que eliminar caracteres especiales
        
    Returns:
        str: Texto limpio
    """
    # Mantener solo letras, números y espacios
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    
    # Normalizar espacios
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def clean_text(text: str) -> str:
    """
    Aplica todas las funciones de limpieza en secuencia.
    
    Args:
        text (str): Texto a limpiar
        
    Returns:
        str: Texto limpio y normalizado
    """
    text = normalize_text(text)
    text = remove_special_chars(text)
    return text 