"""
Gemma API 서비스
"""
import requests
from typing import List
from config import get_settings


class GemmaService:
    """Gemma API 호출 서비스"""
    
    def __init__(self):
        settings = get_settings()
        self.api_url = f"{settings.gemma_api}/api/generate"
        self.model = settings.gemma_model
    
    def parse_text_to_sentences(self, description: str) -> List[str]:
        """
        텍스트를 의미 단위로 파싱
        
        Args:
            description: 가게 소개 텍스트
            
        Returns:
            파싱된 문장 리스트
        """
        
        prompt = f"""다음 가게 소개글을 의미 단위별로 분리해서 문장으로 나눠주세요. 
          각 문장은 하나의 완전한 의미를 담고 있어야 합니다.
          각 문장은 새로운 줄로 구분하고, 번호나 기호 없이 문장만 출력해주세요.

          가게 소개:
          {description}

          출력 형식 예시:
          이 가게는 한식 전문점입니다
          30년 전통의 비법 소스를 사용합니다
          매일 아침 신선한 재료를 직접 준비합니다
        """
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        response = requests.post(self.api_url, json=payload)
        response.raise_for_status()
        
        # 응답에서 텍스트 추출
        result = response.json()
        parsed_text = result.get('response', '')
        
        # 문장들을 분리
        sentences = [s.strip() for s in parsed_text.strip().split('\n') if s.strip()]
        
        return sentences
    
    def generate_answer(self, context: str, question: str) -> str:
        """
        컨텍스트를 기반으로 질문에 답변 생성
        
        Args:
            context: 가게 정보 컨텍스트
            question: 사용자 질문
            
        Returns:
            생성된 답변
        """

        prompt = f"""
        다음은 가게에 대한 정보입니다: {context}

        위 정보를 바탕으로 다음 질문에 자연스럽고 친절하게 답변해주세요:
        질문: {question}

        답변은 한국어로, 자연스러운 문장으로 작성해주세요.
        """

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        response = requests.post(self.api_url, json=payload)
        response.raise_for_status()
        
        result = response.json()
        answer = result.get('response', '')
        
        return answer.strip()
