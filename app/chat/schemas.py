from pydantic import BaseModel, Field
from typing import Optional, Literal, List


class GenerateRequest(BaseModel):
    prompt: str = Field(..., description="사용자 프롬프트")
    model: Optional[str] = Field(default=None, description="선택적 모델명 (미설정 시 기본 모델 사용)")
    temperature: Optional[float] = Field(default=None, ge=0, le=2, description="샘플링 온도")
    system: Optional[str] = Field(default=None, description="선택적 시스템 프롬프트")


class GenerateResponse(BaseModel):
    text: str = Field(..., description="모델 응답 텍스트")


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"] = Field(..., description="메시지 역할")
    content: str = Field(..., description="메시지 내용")


class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., description="대화 히스토리 (최신순 또는 시간순 무관)")
    model: Optional[str] = Field(default=None, description="선택적 모델명 (미설정 시 기본 모델 사용)")
    temperature: Optional[float] = Field(default=None, ge=0, le=2, description="샘플링 온도")


class ChatResponse(BaseModel):
    text: str = Field(..., description="모델 응답 텍스트")


