"""
ChromaDB 서비스
"""
import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any
from config import get_settings


class VectorDBService:
    """ChromaDB 벡터 데이터베이스 서비스"""
    
    def __init__(self):
        settings = get_settings()
        
        # ChromaDB 클라이언트 초기화
        self.client = chromadb.Client(ChromaSettings(
            persist_directory=settings.chroma_persist_directory,
            anonymized_telemetry=False
        ))
        
        # 컬렉션 생성 또는 가져오기
        self.collection = self.client.get_or_create_collection(
            name=settings.chroma_collection_name
        )
    
    def add_documents(
        self,
        store_id: str,
        documents: List[str],
        embeddings: List[List[float]]
    ) -> None:
        """
        문서를 벡터 DB에 추가
        
        Args:
            store_id: 가게 ID
            documents: 문서 리스트
            embeddings: 임베딩 벡터 리스트
        """
        # 기존 데이터 삭제
        self.delete_store_documents(store_id)
        
        # 새로운 데이터 추가
        ids = [f"{store_id}_sent_{i}" for i in range(len(documents))]
        metadatas = [{"store_id": store_id} for _ in documents]
        
        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    
    def delete_store_documents(self, store_id: str) -> None:
        """
        특정 가게의 모든 문서 삭제
        
        Args:
            store_id: 가게 ID
        """
        try:
            existing = self.collection.get(where={"store_id": store_id})
            if existing['ids']:
                self.collection.delete(ids=existing['ids'])
        except Exception:
            pass
    
    def search_similar(
        self,
        store_id: str,
        query_embedding: List[List[float]],
        n_results: int = 5
    ) -> Dict[str, Any]:
        """
        유사한 문서 검색
        
        Args:
            store_id: 가게 ID
            query_embedding: 질문 임베딩
            n_results: 반환할 결과 개수
            
        Returns:
            검색 결과
        """
        results = self.collection.query(
            query_embeddings=query_embedding,
            where={"store_id": store_id},
            n_results=n_results
        )
        
        return results
