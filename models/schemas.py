from pydantic import BaseModel
from typing import List, Optional


class StoreRegistrationRequest(BaseModel):
    """가게 정보 등록 요청"""
    store_id: str
    description: str


class QuestionRequest(BaseModel):
    """질문 요청"""
    store_id: str
    question: str


class StoreRegistrationResponse(BaseModel):
    """가게 정보 등록 응답"""
    store_id: str
    parsed_sentences: List[str]
    message: str


class QuestionResponse(BaseModel):
    """질문 응답"""
    store_id: str
    question: str
    answer: str


# OCR 관련 스키마
class OCRTextResult(BaseModel):
    """OCR 텍스트 결과 (개별 텍스트)"""
    text: str
    confidence: float
    bbox: List


class OCRResponse(BaseModel):
    """OCR 응답 (이미지용) - text만 반환"""
    text: str


class BusinessInfoResponse(BaseModel):
    """사업자등록증 정보 응답"""
    company_name: str
    business_number: str
    representative_name: str
    opening_date: str
    parsed: bool


class PDFPageResult(BaseModel):
    """PDF 페이지별 OCR 결과"""
    page_number: int
    text: str
    results: List[OCRTextResult] = []


class PDFOCRResponse(BaseModel):
    """PDF OCR 응답"""
    success: bool
    text: str
    pages: List[PDFPageResult] = []
    error: Optional[str] = None
