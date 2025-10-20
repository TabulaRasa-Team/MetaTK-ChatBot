"""
소상공인 가게 정보 챗봇 API
모듈화된 FastAPI 애플리케이션
"""
from fastapi import FastAPI
import uvicorn
from api import store_router
from config import get_settings

# 설정 로드
settings = get_settings()

# FastAPI 앱 초기화
app = FastAPI(
    title="소상공인 가게 정보 챗봇 API",
    description="Gemma API와 ChromaDB를 활용한 가게 정보 관리 및 질의응답 시스템",
    version="1.0.0"
)

# 라우터 등록
app.include_router(store_router)


@app.get("/")
async def root():
    """API 상태 확인"""
    return {
        "message": "소상공인 가게 정보 챗봇 API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "POST /store/register": "가게 정보 등록",
            "POST /store/question": "가게에 대한 질문",
            "GET /health": "서버 상태 확인",
            "GET /docs": "API 문서 (Swagger UI)"
        }
    }


@app.get("/health")
async def health_check():
    """서버 상태 확인"""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port
    )

