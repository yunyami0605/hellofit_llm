import os
import asyncmy
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document

class FoodVectorStore:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.vectorstore = None

    async def build_index(self):
        conn = await asyncmy.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
        )

        async with conn.cursor() as cursor:
            await cursor.execute("""
                SELECT rep_food_name,
                       category,
                       ROUND(AVG(kcal), 1) AS avg_kcal,
                       ROUND(AVG(protein), 1) AS avg_protein,
                       ROUND(AVG(carbs), 1) AS avg_carbs,
                       ROUND(AVG(fat), 1) AS avg_fat,
                       ROUND(AVG(weight), 1) AS avg_weight,
                       COUNT(*) AS variant_count
                FROM foods
                GROUP BY rep_food_name, category
            """)
            rows = await cursor.fetchall()

        await conn.ensure_closed()

        docs = []
        for row in rows:
            rep_food_name, category, kcal, protein, carbs, fat, weight, variant_count = row

            content = f"""{rep_food_name} ({category})
            kcal: {kcal}, protein: {protein}, carbs: {carbs}, fat: {fat}
            (variants: {variant_count})"""

            docs.append(Document(
                page_content=content,
                metadata={
                    "rep_food_name": rep_food_name,
                    "category": category,
                    "kcal": kcal,
                    "protein": protein,
                    "carbs": carbs,
                    "fat": fat,
                    "weight": weight,
                    "variants": variant_count
                }
            ))

        self.vectorstore = FAISS.from_documents(docs, self.embeddings)
        self.vectorstore.save_local("faiss_index")

    def load_index(self):
        self.vectorstore = FAISS.load_local(
            "faiss_index",
            self.embeddings,
            allow_dangerous_deserialization=True
        )

    def get_retriever(self, k=10):
        return self.vectorstore.as_retriever(search_kwargs={"k": k})
