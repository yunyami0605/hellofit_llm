from fastapi import APIRouter, Depends, Header, HTTPException, status
from typing import Optional
import asyncio
import json
from fastapi.responses import StreamingResponse

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

@router.post("/generate/stream", summary="SSE 스트리밍 텍스트 생성(데모)")
async def generate_text_stream(body: GenerateRequest, _=Depends(verify_service_api_key)):
    """
    SSE 스트리밍 텍스트 생성.
    - 가능한 경우 OpenAI 스트리밍으로 토큰(delta)을 즉시 흘려보낸다.
    - 스트리밍이 불가능/실패하면: 생성된 텍스트를 일정 청크로 나눠 흘려보낸다(폴백).
    """
    service = ChatService()

    async def event_gen():
        # 1) 진짜 스트리밍(가능하면)
        try:
            for delta in service.generate_stream(
                prompt=body.prompt,
                model=body.model,
                temperature=body.temperature,
                system=body.system,
            ):
                payload = json.dumps({"delta": delta})
                yield f"data: {payload}\n\n"
                # 이벤트 루프에 제어권 양보(동시성/flush 도움)
                await asyncio.sleep(0)
            yield "data: [DONE]\n\n"
            return
        except Exception:
            # 2) 폴백: 완성 텍스트를 청크로 분할
            pass

        try:
            text = service.generate(
                prompt=body.prompt,
                model=body.model,
                temperature=body.temperature,
                system=body.system,
            )
            if not text.strip():
                text = "죄송해요. 지금은 답변을 제공할 수 없어요."
        except Exception:
            text = "죄송해요. 지금은 답변을 제공할 수 없어요."

        chunk_size = 40
        for i in range(0, len(text), chunk_size):
            delta = text[i : i + chunk_size]
            payload = json.dumps({"delta": delta})
            yield f"data: {payload}\n\n"
            await asyncio.sleep(0.02)
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_gen(), media_type="text/event-stream")

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


