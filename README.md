# HelloFit LLM Server

# script

rm -rf faiss_index
poetry run python scripts/build_index.py

#

poetry run uvicorn app.main:app --reload --port 8001
