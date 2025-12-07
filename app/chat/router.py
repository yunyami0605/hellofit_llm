from fastapi import APIRouter, Depends, Header, HTTPException, status
from typing import Optional

from app.chat.schemas import GenerateRequest, GenerateResponse, ChatRequest, ChatResponse
from app.chat.service import ChatService
from app.core.config import settings

router = APIRouter()


def verify_service_api_key(authorization: Optional[str] = Header(default=None)):
    """
    스프링 서버가 Authorization: Bearer <apiKey> 헤더를 보낼 수 있음.
    환경변수 SERVICE_API_KEY 설정 시 해당 값과 불일치하면 401.
    설정되지 않은 경우 인증을 건너뜀(로컬 개발 편의).
    """
    expected = getattr(settings, "service_api_key", None)
    if not expected:
        return
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    token = authorization.split(" ", 1)[1].strip()
    if token != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")


"""
채팅 대화 생성 API (히스토리 기반이 아닌 질문에 대한 답변 생성, 추후 삭제 예정)
"""
@router.post("/generate", response_model=GenerateResponse)
def generate_text(body: GenerateRequest, _=Depends(verify_service_api_key)):
    service = ChatService()
    try:
        text = service.generate(
            prompt=body.prompt,
            model=body.model,
            temperature=body.temperature,
            system=body.system,
        )
        if not text.strip():
            text = "죄송해요. 지금은 답변을 제공할 수 없어요."
        return GenerateResponse(text=text)
    except Exception:
        # 상세 내부 오류는 숨기고 고정 메시지 반환
        return GenerateResponse(text="죄송해요. 지금은 답변을 제공할 수 없어요.")

"""
대화 히스토리 기반 채팅 API
"""
@router.post("/chat", response_model=ChatResponse, summary="대화 히스토리 기반 채팅 API")
def chat(body: ChatRequest, _=Depends(verify_service_api_key)):
    service = ChatService()
    try:
        text = service.chat(
            messages=body.messages,
            model=body.model,
            temperature=body.temperature,
        )
        if not text.strip():
            text = "죄송해요. 지금은 답변을 제공할 수 없어요."
        return ChatResponse(text=text)
    except Exception:
        return ChatResponse(text="죄송해요. 지금은 답변을 제공할 수 없어요.")


