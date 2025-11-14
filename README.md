# 소상공인 가게 정보 챗봇 API

FastAPI, Sentence Transformers, ChromaDB, Gemma API를 활용한 소상공인 가게 정보 관리 및 질의응답 시스템입니다.

## 📁 프로젝트 구조

```
MetaTK-ChatBot/
├── main.py                 # FastAPI 애플리케이션 진입점
├── .env                    # 환경 변수 설정
├── requirements.txt        # 패키지 의존성
├── test_client.py          # API 테스트 클라이언트
│
├── config/                 # 설정 모듈
│   ├── __init__.py
│   └── settings.py         # 환경 변수 및 설정 관리
│
├── models/                 # 데이터 모델
│   ├── __init__.py
│   └── schemas.py          # Pydantic 스키마 정의
│
├── services/               # 비즈니스 로직
│   ├── __init__.py
│   ├── gemma_service.py    # Gemma API 호출 서비스
│   ├── embedding_service.py # 임베딩 생성 서비스
│   └── vectordb_service.py  # ChromaDB 벡터 DB 서비스
│
└── api/                    # API 라우터
    ├── __init__.py
    └── store_routes.py     # 가게 정보 관련 API 엔드포인트
```

## 🎯 기능

### 1️⃣ 가게 정보 등록 API (`POST /store/register`)

- Gemma API가 가게 소개를 의미 단위로 파싱
- KR-SBERT로 각 문장을 임베딩
- ChromaDB에 store_id를 메타데이터로 저장

### 2️⃣ 질문 답변 API (`POST /store/question`)

- 질문을 임베딩하여 관련 가게 정보 검색
- 검색된 정보를 바탕으로 Gemma API가 자연스러운 답변 생성

## 🔧 설정 파일 (.env)

`.env` 파일에서 다음 환경 변수를 설정합니다:

```bash
# Gemma API 설정 (필수)
GEMMA_API=https://gemma3.kwon5700.kr

# 모델 설정
EMBEDDING_MODEL_NAME=snunlp/KR-SBERT-V40K-klueNLI-augSTS
GEMMA_MODEL=gemma2

# ChromaDB 설정
CHROMA_PERSIST_DIRECTORY=./chroma_db
CHROMA_COLLECTION_NAME=store_information

# API 서버 설정
API_HOST=0.0.0.0
API_PORT=8000

# 검색 설정
SEARCH_N_RESULTS=5
```

## 📦 패키지 설치

```bash
pip install -r requirements.txt
```

## 🚀 서버 실행

### 방법 1: Python으로 직접 실행

```bash
python main.py
```

### 방법 2: Uvicorn 사용 (개발 모드)

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

서버가 실행되면 다음 주소에서 API 문서를 확인할 수 있습니다:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **루트**: http://localhost:8000/

## 📡 API 엔드포인트

### 1. 가게 정보 등록

**Endpoint**: `POST /store/register`

**Request Body**:

```json
{
  "store_id": "store_001",
  "description": "우리 가게는 30년 전통의 한식 전문점입니다. 매일 아침 신선한 재료를 직접 시장에서 구매하여 준비합니다."
}
```

**cURL 예시**:

```bash
curl -X POST "http://localhost:8000/store/register" \
  -H "Content-Type: application/json" \
  -d '{
    "store_id": "store_001",
    "description": "우리 가게는 30년 전통의 한식 전문점입니다. 매일 아침 신선한 재료를 직접 시장에서 구매하여 준비합니다. 할머니의 비법 된장으로 만든 된장찌개가 시그니처 메뉴이며, 모든 반찬은 매일 직접 만듭니다. 가족 단위 손님들이 많이 찾아주시며, 넓은 좌석과 주차 공간을 제공합니다."
  }'
```

**응답 예시**:

```json
{
  "store_id": "store_001",
  "parsed_sentences": [
    "우리 가게는 30년 전통의 한식 전문점입니다",
    "매일 아침 신선한 재료를 직접 시장에서 구매하여 준비합니다",
    "할머니의 비법 된장으로 만든 된장찌개가 시그니처 메뉴입니다",
    "모든 반찬은 매일 직접 만듭니다",
    "가족 단위 손님들이 많이 찾아주십니다",
    "넓은 좌석과 주차 공간을 제공합니다"
  ],
  "message": "가게 정보가 성공적으로 등록되었습니다. (총 6개 문장)"
}
```

### 2. 가게에 대한 질문

**Endpoint**: `POST /ask-question`

```bash
curl -X POST "http://localhost:8000/store/question" \
  -H "Content-Type: application/json" \
  -d '{
    "store_id": "store_001",
    "question": "이 가게의 시그니처 메뉴가 뭔가요?"
  }'
```

**응답 예시**:

```json
{
  "store_id": "store_001",
  "question": "이 가게의 시그니처 메뉴가 뭔가요?",
  "answer": "이 가게의 시그니처 메뉴는 할머니의 비법 된장으로 만든 된장찌개입니다. 30년 전통의 한식 전문점으로, 매일 신선한 재료로 정성껏 준비하고 있습니다."
}
```

### 3. Python으로 API 호출 예시

```python
import requests

# 가게 정보 등록
register_data = {
    "store_id": "store_002",
    "description": "이탈리안 레스토랑으로 정통 나폴리 피자를 제공합니다. 이탈리아에서 직수입한 화덕에서 구워내며, 매주 신선한 모짜렐라 치즈를 직접 만듭니다."
}

response = requests.post("http://localhost:8000/store/register", json=register_data)
print(response.json())

# 질문하기
question_data = {
    "store_id": "store_002",
    "question": "어떤 종류의 피자를 파나요?"
}

response = requests.post("http://localhost:8000/store/question", json=question_data)
print(response.json())
```

## 시스템 아키텍처

1. **텍스트 파싱**: Ollama Gemma3 모델이 긴 가게 소개를 의미 단위로 분리
2. **임베딩**: KR-SBERT-V40K 모델로 한국어 문장을 벡터로 변환
3. **저장**: ChromaDB에 벡터와 메타데이터(store_id) 저장
4. **검색**: 질문 임베딩과 유사한 가게 정보를 검색
5. **답변 생성**: 검색된 컨텍스트를 바탕으로 Gemma3가 자연스러운 답변 생성

## 주의사항

- Ollama 서비스가 실행 중이어야 합니다 (`ollama serve`)
- Gemma2 모델이 다운로드되어 있어야 합니다 (`ollama pull gemma2`)
- 첫 실행 시 SentenceTransformer 모델 다운로드에 시간이 걸릴 수 있습니다
- ChromaDB 데이터는 `./chroma_db` 디렉토리에 저장됩니다

## 트러블슈팅

### Ollama 연결 오류

```bash
# Ollama 서비스 시작
ollama serve
```

### 모델을 찾을 수 없는 경우

```bash
# 모델 다운로드
ollama pull gemma2
```

### 포트 충돌

```bash
# 다른 포트로 실행
uvicorn main:app --port 8080
```
