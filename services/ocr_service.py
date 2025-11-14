"""
EasyOCR 기반 OCR 서비스
이미지와 PDF에서 텍스트를 추출합니다.
"""
import easyocr
from typing import List, Dict
from PIL import Image
import numpy as np
import io
import logging
import re

logger = logging.getLogger(__name__)


class OCRService:
    """OCR 서비스"""
    
    def __init__(self, languages: List[str] = None, gpu: bool = False):
        """
        OCR 서비스 초기화
        
        Args:
            languages: OCR을 수행할 언어 목록 (기본값: ['ko', 'en'])
            gpu: GPU 사용 여부 (기본값: False)
        """
        if languages is None:
            languages = ['ko', 'en']
        
        self.languages = languages
        self.gpu = gpu
        logger.info(f"EasyOCR 초기화 - 언어: {languages}, GPU: {gpu}")
        self.reader = easyocr.Reader(languages, gpu=gpu)
    
    def extract_text_from_image(self, image_bytes: bytes) -> Dict:
        """
        이미지 바이너리에서 텍스트 추출
        
        Args:
            image_bytes: 이미지 파일의 바이너리 데이터
            
        Returns:
            {
                "success": bool,
                "text": str (전체 텍스트),
                "results": [
                    {
                        "text": str (추출된 텍스트),
                        "confidence": float (신뢰도),
                        "bbox": [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                    }
                ],
                "error": str (에러 메시지, 있을 경우)
            }
        """
        try:
            # 이미지 로드
            image = Image.open(io.BytesIO(image_bytes))
            
            # 이미지를 RGB로 변환 (RGBA 등의 형식 대응)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            logger.info(f"이미지 크기: {image.size}, 모드: {image.mode}")
            
            # 이미지를 반으로 잘라서 위쪽 부분만 추출
            width, height = image.size
            upper_half = image.crop((0, 0, width, height // 2))
            logger.info(f"위쪽 절반 이미지 크기: {upper_half.size}")
            
            # PIL Image를 numpy array로 변환 (easyocr이 numpy array를 지원)
            image_array = np.array(upper_half)
            
            # OCR 수행
            results = self.reader.readtext(image_array, detail=1)
            
            # 결과 처리
            extracted_texts = []
            full_text = ""
            
            for (bbox, text, confidence) in results:
                # numpy 타입을 Python 네이티브 타입으로 변환 (Pydantic 직렬화 호환)
                bbox_list = [[float(point[0]), float(point[1])] for point in bbox]
                extracted_texts.append({
                    "text": text,
                    "confidence": float(confidence),
                    "bbox": bbox_list
                })
                full_text += text + "\n"
            
            return {
                "success": True,
                "text": full_text.strip(),
                "results": extracted_texts
            }
        
        except Exception as e:
            logger.error(f"OCR 처리 중 에러: {str(e)}")
            return {
                "success": False,
                "text": "",
                "results": [],
                "error": str(e)
            }
    
    def parse_business_registration_info(self, ocr_text: str) -> Dict:
        """
        사업자등록증 OCR 텍스트에서 주요 정보 파싱
        
        Args:
            ocr_text: OCR로 추출한 전체 텍스트
            
        Returns:
            {
                "company_name": str (상호/법인명),
                "business_number": str (사업자등록번호),
                "representative_name": str (대표자 성명),
                "opening_date": str (개업일자, YYYY년 MM월 DD일 형식),
                "parsed": bool (파싱 성공 여부)
            }
        """
        try:
            # 원본 텍스트 보존하고 정리된 텍스트도 생성
            cleaned_text = ocr_text.replace('\n', ' ').replace('\r', ' ')
            # 연속된 공백을 단일 공백으로 정리
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
            
            company_name = ""
            business_number = ""
            representative_name = ""
            opening_date = ""
            
            # 1. 상호(법인명) 추출
            # "상 호 ( 법 인 명 )" 또는 "상호(법인명)" 다음의 텍스트 추출
            company_pattern = r'상\s*호\s*\(\s*법\s*인\s*명\s*\)\s*[|\s]*([가-힣a-zA-Z0-9]+)'
            company_match = re.search(company_pattern, cleaned_text)
            if company_match:
                company_name = company_match.group(1).strip()
            
            # 2. 사업자등록번호 추출 - XXX-XX-XXXXX 형식
            business_pattern = r'(\d{3}-\d{2}-\d{5})'
            business_match = re.search(business_pattern, cleaned_text)
            if business_match:
                business_number = business_match.group(1).strip()
            
            # 3. 대표자 성명 추출
            # "성 명 ( 대 표 자 )" 또는 "성명(대표자)" 다음의 한글 이름 추출
            representative_pattern = r'성\s*명\s*\(\s*대\s*표\s*자\s*\)\s*([가-힣]+)'
            representative_match = re.search(representative_pattern, cleaned_text)
            if representative_match:
                representative_name = representative_match.group(1).strip()
            
            # 4. 개업일자 추출
            # "개 업 일" 또는 "개업일" 다음의 날짜 추출 (공백 포함 가능)
            opening_date_pattern = r'개\s*업\s*일\s*(\d{4})\s*년\s*(\d{1,2})\s*월\s*(\d{1,2})\s*일'
            opening_date_match = re.search(opening_date_pattern, cleaned_text)
            if opening_date_match:
                year = opening_date_match.group(1)
                month = opening_date_match.group(2).zfill(2)
                day = opening_date_match.group(3).zfill(2)
                opening_date = f"{year}년{month}월{day}일"
            
            # 파싱 성공 여부 판단
            parsed_success = bool(company_name or business_number or representative_name or opening_date)
            
            logger.info(f"파싱 결과 - 상호: {company_name}, 사업자번호: {business_number}, 대표자: {representative_name}, 개업일: {opening_date}")
            
            return {
                "company_name": company_name,
                "business_number": business_number.replace('-', ''),
                "representative_name": representative_name,
                "opening_date": opening_date.replace('년', '').replace('월', '').replace('일', ''),
                "parsed": parsed_success
            }
        
        except Exception as e:
            logger.error(f"정보 파싱 중 에러: {str(e)}")
            return {
                "company_name": "",
                "business_number": "",
                "representative_name": "",
                "opening_date": "",
                "parsed": False
            }

# 싱글톤 인스턴스 (한번만 초기화)
_ocr_service = None

def get_ocr_service(languages: List[str] = None, gpu: bool = False) -> OCRService:
    """
    OCR 서비스 싱글톤 인스턴스 반환
    
    Args:
        languages: OCR 언어 목록
        gpu: GPU 사용 여부
        
    Returns:
        OCRService 인스턴스
    """
    global _ocr_service
    if _ocr_service is None:
        _ocr_service = OCRService(languages=languages, gpu=gpu)
    return _ocr_service
