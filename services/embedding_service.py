"""
임베딩 서비스
"""
from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
from config import get_settings


class EmbeddingService:
    """임베딩 생성 서비스"""
    
    def __init__(self):
        settings = get_settings()
        self.model = SentenceTransformer(settings.embedding_model_name)
    
    def encode(self, texts: List[str]) -> np.ndarray:
        """
        텍스트 리스트를 임베딩 벡터로 변환
        
        Args:
            texts: 임베딩할 텍스트 리스트
            
        Returns:
            임베딩 벡터 배열
        """
        return self.model.encode(texts)
    
    def encode_single(self, text: str) -> np.ndarray:
        """
        단일 텍스트를 임베딩 벡터로 변환
        
        Args:
            text: 임베딩할 텍스트
            
        Returns:
            임베딩 벡터
        """
        return self.model.encode([text])
