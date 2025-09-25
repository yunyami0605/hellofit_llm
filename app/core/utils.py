import uuid
from datetime import datetime

def generate_uuid() -> str:
    return str(uuid.uuid4())

def now_str() -> str:
    return datetime.utcnow().isoformat()
