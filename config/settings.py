"""
환경 변수 및 설정 관리
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # Gemma API 설정
    gemma_api: str = os.getenv("GEMMA_API")
    
    # 모델 설정
    embedding_model_name: str = os.getenv("EMBEDDING_MODEL_NAME")
    gemma_model: str = os.getenv("GEMMA_MODEL")
    
    # ChromaDB 설정
    chroma_persist_directory: str = os.getenv("CHROMA_PERSIST_DIRECTORY")
    chroma_collection_name: str = os.getenv("CHROMA_COLLECTION_NAME")
    
    # API 설정
    api_host: str = os.getenv("API_HOST")
    api_port: int = os.getenv("API_PORT")
    
    # 검색 설정
    search_n_results: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
