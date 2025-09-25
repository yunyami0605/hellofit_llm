import logging

logger = logging.getLogger("hellofit-llm")
logger.setLevel(logging.INFO)

# 콘솔 핸들러
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# 포맷
formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] %(name)s - %(message)s"
)
ch.setFormatter(formatter)

# 핸들러 등록 (중복 방지)
if not logger.handlers:
    logger.addHandler(ch)
