
# Submission Note

## What Worked
- End-to-end scraping, PDF extraction, ETL, embeddings, FAISS index, and RAG API.
- HuggingFace sentence-transformers for embeddings (CPU-friendly).
- Groq LLM used for generation via API; system prompt enforces sourcing from context.
- Web UI (FastAPI + Jinja) displays answers and clickable citations.

## What Didn't Work
- Some PDFs are scanned images; extraction without OCR was incomplete.
- Camelot table extraction may miss complex tables.

## Future Improvements
- Add OCR (Tesseract) for scanned PDFs.
- More robust selectors and retries for changes in site structure.
- Add Great Expectations checks for data quality and more integration tests.
