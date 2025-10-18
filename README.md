
# MoSPI Scraper + RAG (HuggingFace embeddings + Groq LLM)

This repository contains an end-to-end solution for the assignment:
- Scraper: discover listings & detail pages, download PDFs, extract text & tables
- Pipeline: normalize, chunk, embed (HuggingFace), build FAISS index
- RAG: FastAPI endpoints (/ask, /ingest, /health) using Groq for generation
- Web UI: FastAPI + Jinja server-side UI showing answers & citations
- SQLite used for metadata storage (data/processed/mospi.db)
- Dockerfiles and docker-compose for reproducible runs

# for run this code must have docker.
 - command: docker-compose up--build


# Overview of this project:

Scrap the data using beautifulsoup and store them locally and build rag application on top of these data.using containerization.app contain chunking, vector embeddings, faiss vector store, prompting,llm and sqllit for metadate storage.

# Tool and technology
Huggingface
Beautifulsoup
faiss
huggingface_vector_embedding_mode.
groq_llm
html for frotend
fastapi for backend
docker
etc.
