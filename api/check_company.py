from fastapi import APIRouter, HTTPException, UploadFile, File
from config import get_settings
from services.ocr_service import get_ocr_service
from models.schemas import OCRResponse, PDFOCRResponse, BusinessInfoResponse

router = APIRouter(prefix="/company", tags=["company"])

settings = get_settings()

@router.post("/ocr", response_model=BusinessInfoResponse)
async def extract_text_from_image(file: UploadFile = File(...)):
  """
  사진 파일에서 OCR로 텍스트 추출 후 사업자등록증 정보 파싱
  
  - 지원 형식: jpg, jpeg, png, gif, bmp
  - 응답: 상호(법인명), 사업자등록번호, 대표자 성명
  
  Args:
      file: 업로드된 이미지 파일
      
  Returns:
      BusinessInfoResponse: 파싱된 사업자등록증 정보
  """
  try:
    # 파일 크기 확인 (최대 10MB)
    max_file_size = 10 * 1024 * 1024
    file_content = await file.read()
    
    if len(file_content) > max_file_size:
      raise HTTPException(
        status_code=400,
        detail="파일 크기가 너무 큽니다. (최대 10MB)"
      )
    
    # 지원 형식 확인
    supported_formats = ['image/jpeg', 'image/png', 'image/gif', 'image/bmp']
    if file.content_type not in supported_formats:
      raise HTTPException(
        status_code=400,
        detail=f"지원하지 않는 형식입니다. 지원 형식: {supported_formats}"
      )
    
    # OCR 서비스 인스턴스 획득
    ocr_service = get_ocr_service()
    
    # OCR 수행
    ocr_result = ocr_service.extract_text_from_image(file_content)
    
    # OCR 텍스트에서 사업자등록증 정보 파싱
    parsed_info = ocr_service.parse_business_registration_info(ocr_result['text'])
    
    return BusinessInfoResponse(**parsed_info)
  
  except HTTPException:
    raise
  except Exception as e:
    raise HTTPException(
      status_code=500,
      detail=f"OCR 처리 중 오류가 발생했습니다: {str(e)}"
    )

@router.post("/check")
async def check_company():
  """
  소상공인 확인 API
  
  1. 중소기업 확인서를 사진으로 받음
  2. OCR을 통해 텍스트 추출
  """
