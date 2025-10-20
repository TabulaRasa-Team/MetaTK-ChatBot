from fastapi import APIRouter, HTTPException
from models import (
    StoreRegistrationRequest,
    StoreRegistrationResponse,
    QuestionRequest,
    QuestionResponse
)
from services import GemmaService, EmbeddingService, VectorDBService
from config import get_settings

router = APIRouter(prefix="/store", tags=["store"])

# 서비스 인스턴스
gemma_service = GemmaService()
embedding_service = EmbeddingService()
vectordb_service = VectorDBService()
settings = get_settings()


@router.post("/register", response_model=StoreRegistrationResponse)
async def register_store(request: StoreRegistrationRequest):
    """
    소상공인 가게 정보를 등록하는 API
    
    1. Gemma API를 사용하여 가게 소개를 의미 단위로 파싱
    2. 각 문장을 임베딩하여 ChromaDB에 저장
    """
    try:
        # 1. 텍스트를 의미 단위로 파싱
        sentences = gemma_service.parse_text_to_sentences(request.description)
        
        if not sentences:
            raise HTTPException(
                status_code=400,
                detail="텍스트 파싱 결과가 비어있습니다."
            )
        
        # 2. 각 문장을 임베딩
        embeddings = embedding_service.encode(sentences)
        
        # 3. ChromaDB에 저장
        vectordb_service.add_documents(
            store_id=request.store_id,
            documents=sentences,
            embeddings=embeddings.tolist()
        )
        
        return StoreRegistrationResponse(
            store_id=request.store_id,
            parsed_sentences=sentences,
            message=f"가게 정보가 성공적으로 등록되었습니다. (총 {len(sentences)}개 문장)"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"가게 등록 중 오류 발생: {str(e)}"
        )


@router.post("/question", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    특정 가게에 대한 질문에 답변하는 API
    
    1. 질문을 임베딩
    2. ChromaDB에서 해당 가게의 관련 정보 검색
    3. Gemma API를 사용하여 답변 생성
    """
    try:
        # 1. 질문 임베딩
        question_embedding = embedding_service.encode_single(request.question)
        
        # 2. ChromaDB에서 관련 정보 검색
        results = vectordb_service.search_similar(
            store_id=request.store_id,
            query_embedding=question_embedding.tolist(),
            n_results=settings.search_n_results
        )
        
        # 3. 검색 결과 확인
        if not results['documents'] or not results['documents'][0]:
            raise HTTPException(
                status_code=404,
                detail=f"가게 ID '{request.store_id}'에 대한 정보를 찾을 수 없습니다."
            )
        
        # 4. 컨텍스트 구성
        relevant_info = results['documents'][0]
        context = "\n".join(relevant_info)
        
        # 5. Gemma API로 답변 생성
        answer = gemma_service.generate_answer(context, request.question)
        
        return QuestionResponse(
            store_id=request.store_id,
            question=request.question,
            answer=answer
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"질문 처리 중 오류 발생: {str(e)}"
        )
