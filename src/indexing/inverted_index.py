"""
Implementación del índice invertido para recuperación booleana.

Este módulo implementa un índice invertido completo con soporte para
operaciones booleanas (AND, OR, NOT) y búsqueda de frases exactas.
"""

from typing import Dict, Set, List, Union
from collections import defaultdict
import pickle
from ..preprocessing.tokenizer import tokenize, get_ngrams

class InvertedIndex:
    def __init__(self):
        """
        Inicializa el índice invertido.
        """
        self.index: Dict[str, Set[int]] = defaultdict(set)
        self.documents: Dict[int, str] = {}
        self.doc_lengths: Dict[int, int] = {}
        self.positional_index: Dict[str, Dict[int, List[int]]] = defaultdict(lambda: defaultdict(list))
        
    def add_document(self, doc_id: int, text: str):
        """
        Añade un documento al índice.
        
        Args:
            doc_id (int): Identificador único del documento
            text (str): Texto del documento
        """
        self.documents[doc_id] = text
        tokens = tokenize(text)
        self.doc_lengths[doc_id] = len(tokens)
        
        # Construir índice invertido básico
        for position, token in enumerate(tokens):
            self.index[token].add(doc_id)
            self.positional_index[token][doc_id].append(position)
    
    def boolean_query(self, query: str) -> Set[int]:
        """
        Ejecuta una consulta booleana.
        
        Args:
            query (str): Consulta booleana (e.g., "term1 AND term2 NOT term3")
            
        Returns:
            Set[int]: Conjunto de IDs de documentos que coinciden
        """
        tokens = query.upper().split()
        result = None
        current_op = "AND"
        
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            if token in ("AND", "OR", "NOT"):
                current_op = token
                i += 1
                continue
            
            # Obtener conjunto de documentos para el término actual
            term_docs = self.index.get(token.lower(), set())
            
            if result is None:
                result = term_docs
            else:
                if current_op == "AND":
                    result &= term_docs
                elif current_op == "OR":
                    result |= term_docs
                elif current_op == "NOT":
                    result -= term_docs
            
            i += 1
        
        return result if result is not None else set()
    
    def phrase_query(self, phrase: str) -> Set[int]:
        """
        Busca una frase exacta.
        
        Args:
            phrase (str): Frase a buscar
            
        Returns:
            Set[int]: Conjunto de IDs de documentos que contienen la frase
        """
        tokens = tokenize(phrase)
        if not tokens:
            return set()
        
        # Obtener documentos que contienen todos los términos
        result = set.intersection(*[self.index.get(token, set()) for token in tokens])
        
        # Verificar posiciones consecutivas
        matches = set()
        for doc_id in result:
            positions = self.positional_index[tokens[0]][doc_id]
            
            for pos in positions:
                match = True
                for i, token in enumerate(tokens[1:], 1):
                    if pos + i not in self.positional_index[token][doc_id]:
                        match = False
                        break
                
                if match:
                    matches.add(doc_id)
                    break
        
        return matches
    
    def save(self, filepath: str):
        """
        Guarda el índice en disco.
        
        Args:
            filepath (str): Ruta donde guardar el índice
        """
        with open(filepath, 'wb') as f:
            pickle.dump({
                'index': dict(self.index),
                'documents': self.documents,
                'doc_lengths': self.doc_lengths,
                'positional_index': dict(self.positional_index)
            }, f)
    
    @classmethod
    def load(cls, filepath: str) -> 'InvertedIndex':
        """
        Carga un índice desde disco.
        
        Args:
            filepath (str): Ruta del archivo del índice
            
        Returns:
            InvertedIndex: Índice cargado
        """
        index = cls()
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
            index.index = defaultdict(set, data['index'])
            index.documents = data['documents']
            index.doc_lengths = data['doc_lengths']
            index.positional_index = defaultdict(lambda: defaultdict(list), 
                                              data['positional_index'])
        return index 