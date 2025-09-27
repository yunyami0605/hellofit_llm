import asyncio
from dotenv import load_dotenv
load_dotenv()   # 👈 .env 읽기
from app.core.vectorstore import FoodVectorStore

async def main():
    store = FoodVectorStore()
    await store.build_index()
    print("✅ FAISS index 생성 완료")

if __name__ == "__main__":
    asyncio.run(main())
