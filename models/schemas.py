from pydantic import BaseModel
from typing import List


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
