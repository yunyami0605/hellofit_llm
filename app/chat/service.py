from typing import Optional, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from app.chat.schemas import ChatMessage
from app.core.logger import logger
from app.core.vectorstore import FoodVectorStore


class ChatService:
    def __init__(self, default_model: str = "gpt-4o-mini"):
        self.default_model = default_model
        # RAG용 벡터스토어 로드(음식/영양 맥락을 컨텍스트로 활용)
        self.food_store = FoodVectorStore()
        try:
            self.food_store.load_index()
            self.retriever = self.food_store.get_retriever(k=10)
        except Exception as e:
            logger.warning(f"[chat] vector index load failed, fallback to no-RAG: {e}")
            self.retriever = None

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        system: Optional[str] = None,
    ) -> str:
        llm = ChatOpenAI(
            model=model or self.default_model,
            temperature=temperature if temperature is not None else 0.7,
        )
        messages = []

        # RAG 컨텍스트 구성(가능한 경우)
        context_text = ""
        if self.retriever is not None and prompt:
            try:
                docs = self.retriever.invoke(prompt)
                if docs:
                    context_text = "\n".join([d.page_content for d in docs])
            except Exception as e:
                logger.warning(f"[generate] retriever error ignored: {e}")

        if system:
            messages.append(SystemMessage(content=system))
        if context_text:
            messages.append(SystemMessage(content=f"다음 음식/영양 컨텍스트를 참고해서 답변하세요:\n{context_text}"))
        messages.append(HumanMessage(content=prompt))

        # 입력 프롬프트 로깅
        logger.info(f"[generate] user: {prompt}")

        ai_msg = llm.invoke(messages)
        response_text = ai_msg.content or ""

        # 모델 응답 로깅
        logger.info(f"[generate] assistant: {response_text}")
        return response_text

    def generate_stream(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        system: Optional[str] = None,
    ):
        """
        OpenAI 스트리밍을 사용해 delta를 순차적으로 yield.
        - 프론트에서 청크 단위로 표시하기 위한 용도
        - RAG 컨텍스트(가능 시) + system 프롬프트를 동일하게 적용
        """
        llm = ChatOpenAI(
            model=model or self.default_model,
            temperature=temperature if temperature is not None else 0.7,
            streaming=True,
        )
        messages = []

        # RAG 컨텍스트 구성(가능한 경우)
        context_text = ""
        if self.retriever is not None and prompt:
            try:
                docs = self.retriever.invoke(prompt)
                if docs:
                    context_text = "\n".join([d.page_content for d in docs])
            except Exception as e:
                logger.warning(f"[generate_stream] retriever error ignored: {e}")

        if system:
            messages.append(SystemMessage(content=system))
        if context_text:
            messages.append(SystemMessage(content=f"다음 음식/영양 컨텍스트를 참고해서 답변하세요:\n{context_text}"))
        messages.append(HumanMessage(content=prompt))

        logger.info(f"[generate_stream] user: {prompt}")

        def _extract_text(content) -> str:
            # langchain chunk content는 str 또는 list(파트)일 수 있음
            if content is None:
                return ""
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                parts = []
                for p in content:
                    # 보수적으로 text만 수집
                    if isinstance(p, str):
                        parts.append(p)
                    elif isinstance(p, dict):
                        t = p.get("text")
                        if isinstance(t, str):
                            parts.append(t)
                return "".join(parts)
            return ""

        for chunk in llm.stream(messages):
            delta = _extract_text(getattr(chunk, "content", ""))
            if delta:
                yield delta

    def chat(
        self,
        messages: List[ChatMessage],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """
        주어진 대화 히스토리를 기반으로 RAG 컨텍스트(가능 시)를 주입하여 응답을 생성한다.
        ChatMessage.role은 system/user/assistant 중 하나여야 한다.
        """
        llm = ChatOpenAI(
            model=model or self.default_model,
            temperature=temperature if temperature is not None else 0.7,
        )
        lc_messages = []
        for m in messages:
            if m.role == "system":
                lc_messages.append(SystemMessage(content=m.content))
            elif m.role == "user":
                lc_messages.append(HumanMessage(content=m.content))
            else:  # assistant
                lc_messages.append(AIMessage(content=m.content))

        # 마지막 사용자 메시지 로깅
        last_user_message = next(
            (m.content for m in reversed(messages) if m.role == "user"),
            None,
        )
        if last_user_message is not None:
            logger.info(f"[chat] user: {last_user_message}")

        # RAG 컨텍스트 주입(가능한 경우)
        if self.retriever is not None:
            try:
                query = last_user_message or "영양/식단 관련 일반 질문"
                docs = self.retriever.invoke(query)
                if docs:
                    context_text = "\n".join([d.page_content for d in docs])
                    lc_messages.insert(0, SystemMessage(content=f"다음 음식/영양 컨텍스트를 참고해서 답변하세요:\n{context_text}"))
            except Exception as e:
                logger.warning(f"[chat] retriever error ignored: {e}")

        ai_msg = llm.invoke(lc_messages)
        response_text = ai_msg.content or ""

        # 모델 응답 로깅
        logger.info(f"[chat] assistant: {response_text}")
        return response_text


